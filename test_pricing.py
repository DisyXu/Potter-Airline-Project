from datetime import date, timedelta
from flight import Flight
from pricing import *

# test maximum fare
flight1 = Flight(flight_id="AC123",origin="YYZ",destination="YVR",departure_date="2028-09-25",
                departure_time="08:30",base_fare_cad=100,capacity=100,seats_remaining=100,
                demand_score=3.1,demand_level="high",season="regular",is_weekend=False)

assert calculate_price(flight1) == 300

# test minimum fare
flight2 = Flight(flight_id="AC123",origin="YYZ",destination="YVR",departure_date="2028-09-25",
                departure_time="08:30",base_fare_cad=100,capacity=100,seats_remaining=100,
                demand_score=0.6,demand_level="high",season="regular",is_weekend=False)

assert calculate_price(flight2) == 70

