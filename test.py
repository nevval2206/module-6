from fontTools.misc.cython import returns


class BasePlan:
    """Base class for all subscription plans."""

    def __init__(self, name, price, included_visits, extra_visit_price, services):
        self.name = name
        self.price = price
        self.included_visits = included_visits  # int or float("inf")
        self.extra_visit_price = extra_visit_price
        self.services = services  # list of strings

    def calculate_revenue(self, visits, hospital_cost_per_visit=10):
        """Calculate revenue and profit for the hospital."""
        # Unlimited:
        if self.included_visits == float("inf"):
            extra_visits = 0
        else:
            extra_visits = max(visits - self.included_visits, 0)

        revenue = self.price + extra_visits * self.extra_visit_price
        cost = visits * hospital_cost_per_visit
        profit = revenue - cost

        return {
            "plan": self.name,
            "visits": visits,
            "revenue": revenue,
            "profit": profit
        }


class LitePlan(BasePlan):
    """Cheap plan, few visits, minimal diagnostics."""

    def __init__(self):
        super().__init__(
            name="Lite Care Pack",
            price=25,
            included_visits=2,
            extra_visit_price=15,
            services=["Basic check-ups"]
        )


class StandardPlan(BasePlan):
    """Balanced plan for average adults."""

    def __init__(self):
        super().__init__(
            name="Standard Health Pack",
            price=45,
            included_visits=4,
            extra_visit_price=20,
            services=["Basic check-ups", "Blood analysis"]
        )


class ChronicPlan(BasePlan):
    """For chronic patients requiring frequent care."""

    def __init__(self):
        super().__init__(
            name="Chronic Care Pack",
            price=80,
            included_visits=8,
            extra_visit_price=18,
            services=["Blood tests", "X-ray", "ECG"]
        )


class UnlimitedPlan(BasePlan):
    """Unlimited monthly plan."""

    def __init__(self):
        super().__init__(
            name="Unlimited Premium Pack",
            price=120,
            included_visits=float("inf"),
            extra_visit_price=0,
            services=["All diagnostics", "X-ray", "Ultrasound", "Full blood panel"]
        )
        return
