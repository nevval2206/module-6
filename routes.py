# src/routes/plans.py

import os
import datetime
import json
from functools import wraps
from io import BytesIO

from flask import Blueprint, request, jsonify, make_response, g
from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app

import bcrypt
import jwt
import numpy as np
import matplotlib.pyplot as plt
from fontTools.misc.cython import returns

# SQLAlchemy instance (app factory ile uyumlu)
db = SQLAlchemy()

plans_bp = Blueprint("plans", __name__)


# ---------- Models ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    included_visits = db.Column(db.Float, nullable=False)
    extra_visit_price = db.Column(db.Float, nullable=False)
    services_json = db.Column(db.Text, nullable=False)

    def services(self):
        return json.loads(self.services_json)


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)


# ---------- JWT Helpers ----------
def encode_jwt(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    }
    return jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")


def decode_jwt(token):
    try:
        return jwt.decode(token, app.config["JWT_SECRET"], algorithms=["HS256"])
    except Exception:
        return None


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("jwt") or request.headers.get("Authorization")

        if token and token.startswith("Bearer "):
            token = token.split(" ", 1)[1]

        payload = decode_jwt(token) if token else None
        if not payload or not payload.get("user_id"):
            return jsonify({"message": "Token invalid or missing"}), 401

        g.user_id = payload["user_id"]
        return f(*args, **kwargs)
    return wrapper


# ---------- AUTH ROUTES ----------
@plans_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = User(username=username, password=hashed)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered"}), 201


@plans_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password):
        return jsonify({"message": "Invalid username or password"}), 401

    token = encode_jwt(user.id)

    resp = make_response({"message": "Login successful"})
    resp.set_cookie("jwt", token, httponly=True, samesite="Strict")

    return resp


@plans_bp.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"message": "Logged out"}))
    resp.set_cookie("jwt", "", expires=0, httponly=True, samesite="Strict")
    return resp


# ---------- PLANS ROUTE ----------
@plans_bp.route("/plans", methods=["GET"])
@auth_required
def get_plans():
    plans = Plan.query.all()
    out = []

    for p in plans:
        out.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "included_visits": "Unlimited" if p.included_visits == float("inf") else p.included_visits,
            "extra_visit_price": p.extra_visit_price,
            "services": p.services()
        })

    return jsonify(out)


# ---------- DB INITIALIZER ----------
def init_db(app):
    """App factory içinde çağrılacak DB initializer."""
    with app.app_context():
        db.create_all()

        if Plan.query.count() == 0:  # Add default plans once
            plans = [
                {
                    "name": "Lite Care Pack",
                    "price": 25,
                    "included_visits": 2,
                    "extra_visit_price": 15,
                    "services": ["Basic check-up"]
                },
                {
                    "name": "Standard Health Pack",
                    "price": 45,
                    "included_visits": 4,
                    "extra_visit_price": 20,
                    "services": ["Check-up", "Blood analysis"]
                },
                {
                    "name": "Chronic Care Pack",
                    "price": 80,
                    "included_visits": 8,
                    "extra_visit_price": 18,
                    "services": ["Blood tests", "X-ray", "ECG"]
                },
                {
                    "name": "Unlimited Premium Pack",
                    "price": 120,
                    "included_visits": float("inf"),
                    "extra_visit_price": 0,
                    "services": ["All diagnostics", "X-ray", "Ultrasound"]
                }
            ]

            for p in plans:
                plan = Plan(
                    name=p["name"],
                    price=p["price"],
                    included_visits=p["included_visits"],
                    extra_visit_price=p["extra_visit_price"],
                    services_json=json.dumps(p["services"])
                )
                db.session.add(plan)

            db.session.commit()
            return
