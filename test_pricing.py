from datetime import date, timedelta
from flight import Flight

flight1 = Flight(
        flight_id="AC123",
        origin="YYZ",
        destination="YVR",
        departure_date="2026-09-25",
        departure_time="08:30",
        base_fare_cad=250,
        capacity=100,
        seats_remaining=12,
        demand_score=1.32,
        demand_level="high",
        season="peak",
        is_weekend=False
    )

print(calculate_price(flight1))

test = 1 + 0.45 * (1 - (flight1.seats_remaining / flight1.capacity))