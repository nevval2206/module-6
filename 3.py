# src/routes/plans.py
import os

import datetime

import json

from functools import wraps

from io import BytesIO

from flask import Flask, request, jsonify, make_response, g, send_file
from flask_sqlalchemy import SQLAlchemy

import bcrypt

import jwt

import numpy as np

import matplotlib.pyplot as plt
import sqlite3

from flask import Blueprint, jsonify
from fontTools.misc.cython import returns

from src.routes.auth import auth_required

from src.models.plans import LitePlan, StandardPlan, ChronicPlan, UnlimitedPlan

from sqlite3 import db

plans_bp = Blueprint('plans', __name__)


@plans_bp.route('/plans', methods=['GET'])
@auth_required
def get_plans():
    """Return all available subscription plans."""

    plans = [

        LitePlan(),

        StandardPlan(),

        ChronicPlan(),

        UnlimitedPlan()

    ]

    response = []

    for p in plans:
        response.append({

            "name": p.name,

            "price": p.price,

            "included_visits": (

                "Unlimited" if p.included_visits == float("inf") else p.included_visits

            ),

            "extra_visit_price": p.extra_visit_price,

            "services": p.services

        })

    return jsonify(response)


"""

Simple Flask app for: auth, subscription plans, buy/renew/cancel, simulation and profitability graphs.

Single-file for clarity. Use SQLite. Keep it small and easy to read.



Run:

1) pip install flask sqlalchemy flask-sqlalchemy bcrypt pyjwt numpy matplotlib

2) export FLASK_APP=healthcare_subscription_app.py

  export JWT_SECRET='your-secret'

3) flask run



DB file: subscriptions.db (in working dir)

Graphs saved to ./static/plots.png

"""



