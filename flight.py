from datetime import date, datetime


class Flight:
    def __init__(
        self,
        flight_id,
        origin,
        destination,
        departure_date,
        departure_time,
        base_fare_cad,
        capacity,
        seats_remaining,
        demand_score,
        demand_level,
        season,
        is_weekend
    ):
        self.flight_id = flight_id
        self.origin = origin
        self.destination = destination

        # Convert departure_date into a Python date object
        if isinstance(departure_date, str):
            self.departure_date = datetime.strptime(
                departure_date, "%Y-%m-%d"
            ).date()
        elif isinstance(departure_date, datetime):
            self.departure_date = departure_date.date()
        else:
            self.departure_date = departure_date

        self.departure_time = departure_time
        self.base_fare_cad = float(base_fare_cad)
        self.capacity = int(capacity)
        self.seats_remaining = int(seats_remaining)
        self.demand_score = float(demand_score)
        self.demand_level = demand_level
        self.season = season
        self.is_weekend = bool(is_weekend)

    def occupancy_rate(self):
        seats_booked = self.capacity - self.seats_remaining
        return float (seats_booked / self.capacity*100)

    def days_to_departure(self, reference_date=None):
        if reference_date is None:
            reference_date = date.today()

        return (self.departure_date - reference_date).days

    def to_dict(self):
        return {
            "flight_id": self.flight_id,
            "origin": self.origin,
            "destination": self.destination,
            "departure_date": self.departure_date.isoformat(),
            "departure_time": self.departure_time,
            "base_fare_cad": self.base_fare_cad,
            "capacity": self.capacity,
            "seats_remaining": self.seats_remaining,
            "demand_score": self.demand_score,
            "demand_level": self.demand_level,
            "season": self.season,
            "is_weekend": self.is_weekend
        }

