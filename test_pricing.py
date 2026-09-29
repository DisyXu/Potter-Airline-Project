from datetime import date, timedelta
from flight import Flight
from pricing import *

def test_maximum_fare():
    flight1 = Flight(flight_id="AC123",origin="YYZ",destination="YVR",departure_date="2028-09-25",
                departure_time="08:30",base_fare_cad=100,capacity=100,seats_remaining=1,
                demand_score=10,demand_level="high",season="peak",is_weekend=True)

    assert calculate_price(flight1) == 300


def test_minimum_fare():
    flight2 = Flight(flight_id="AC123",origin="YYZ",destination="YVR",departure_date="2028-09-25",
                    departure_time="08:30",base_fare_cad=100,capacity=100,seats_remaining=100,
                    demand_score=0.01,demand_level="low",season="regular",is_weekend=False)

    assert calculate_price(flight2) == 70

