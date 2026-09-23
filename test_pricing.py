from datetime import date, timedelta
from flight import Flight
from pricing import *

# test minimum fare
flight1 = Flight(flight_id="AC123",origin="YYZ",destination="YVR",departure_date="2028-09-25",
                departure_time="08:30",base_fare_cad=1,capacity=100,seats_remaining=12,
                demand_score=1.32,demand_level="high",season="peak",is_weekend=False)

assert calculate_price(flight1) == 45

# test maximum fare
flight2 = Flight(flight_id="AC123",origin="YYZ",destination="YVR",departure_date="2028-09-25",
                departure_time="08:30",base_fare_cad=2000,capacity=100,seats_remaining=12,
                demand_score=1.32,demand_level="high",season="peak",is_weekend=False)

assert calculate_price(flight2) == 1500

# test flights where departure time has passed
flight3 = Flight(flight_id="AC123",origin="YYZ",destination="YVR",departure_date="2026-09-20",
                departure_time="08:30",base_fare_cad=250,capacity=100,seats_remaining=12,
                demand_score=1.32,demand_level="high",season="peak",is_weekend=False)

calculate_price(flight3)

# test seats remaining > capacity 
flight4 = Flight(flight_id="AC123",origin="YYZ",destination="YVR",departure_date="2028-09-25",
                departure_time="08:30",base_fare_cad=250,capacity=10,seats_remaining=120,
                demand_score=1.32,demand_level="high",season="peak",is_weekend=False)

calculate_price(flight4)

# test seats remaining <= 0 
flight5 = Flight(flight_id="AC123",origin="YYZ",destination="YVR",departure_date="2028-09-25",
                departure_time="08:30",base_fare_cad=250,capacity=10,seats_remaining=0,
                demand_score=1.32,demand_level="high",season="peak",is_weekend=False)

calculate_price(flight5)

# test capacity <= 0 
flight6 = Flight(flight_id="AC123",origin="YYZ",destination="YVR",departure_date="2028-09-25",
                departure_time="08:30",base_fare_cad=250,capacity=0,seats_remaining=10,
                demand_score=1.32,demand_level="high",season="peak",is_weekend=False)

calculate_price(flight6)