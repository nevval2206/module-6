# ---------- Plans API ----------

@app.route('/plans', methods=['GET'])
@auth_required
def get_plans():
    plans = Plan.query.all()

    out = []

    for p in plans:
        out.append({

            'id': p.id, 'name': p.name, 'price': p.price,

            'included_visits': 'Unlimited' if p.included_visits == float('inf') else p.included_visits,

            'extra_visit_price': p.extra_visit_price, 'services': p.services()

        })

    return jsonify(out)
