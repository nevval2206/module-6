import json
from sqlite3 import db

def init_db():
    db.create_all()

    if Plan.query.count() == 0:

        plans = [

            {

                'name': 'Lite Care Pack', 'price': 25, 'included_visits': 2,

                'extra_visit_price': 15, 'services': ['Basic check-up']

            },

            {

                'name': 'Standard Health Pack', 'price': 45, 'included_visits': 4,

                'extra_visit_price': 20, 'services': ['Check-up', 'Blood analysis']

            },

            {

                'name': 'Chronic Care Pack', 'price': 80, 'included_visits': 8,

                'extra_visit_price': 18, 'services': ['Blood tests', 'X-ray', 'ECG']

            },

            {

                'name': 'Unlimited Premium Pack', 'price': 120, 'included_visits': float('inf'),

                'extra_visit_price': 0, 'services': ['All diagnostics', 'X-ray', 'Ultrasound']

            }

        ]

        for p in plans:
            plan = Plan(

                name=p['name'], price=p['price'], included_visits=p['included_visits'],

                extra_visit_price=p['extra_visit_price'], services_json=json.dumps(p['services'])

            )

            db.session.add(plan)

        db.session.commit()

        return
