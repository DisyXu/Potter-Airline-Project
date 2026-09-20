from datetime import date
from flight import Flight


def create_test_flight():
    return Flight(
        flight_id="PA9999",
        origin="YYZ",
        destination="YVR",
        departure_date="2026-10-10",
        departure_time="10:30",
        base_fare_cad=300.0,
        capacity=200,
        seats_remaining=50,
        demand_score=1.2,
        demand_level="high",
        season="regular",
        is_weekend=False
    )


# Tests for occupancy_rate()

def test_occupancy_rate():
    flight = create_test_flight()

    assert flight.occupancy_rate() == 75.0


def test_full_occupancy():
    flight = create_test_flight()
    flight.seats_remaining = 0

    assert flight.occupancy_rate() == 100.0


# Tests for days_to_departure()

def test_days_to_departure():
    flight = create_test_flight()

    reference_date = date(2026, 10, 1)

    assert flight.days_to_departure(reference_date) == 9


def test_departure_today():
    flight = create_test_flight()

    reference_date = date(2026, 10, 10)

    assert flight.days_to_departure(reference_date) == 0


# Tests for to_dict()

def test_to_dict_flight_id():
    flight = create_test_flight()

    flight_dict = flight.to_dict()

    assert flight_dict["flight_id"] == "PA9999"


def test_to_dict_capacity():
    flight = create_test_flight()

    flight_dict = flight.to_dict()

    assert flight_dict["capacity"] == 200