import pandas as pd
import numpy as np
import pytest


from sql_crud import (
    create_database,
    load_data,
    select_flights,
    update_seats_remaining,
    delete_flight,
)
from flight import Flight





def test_create_database_and_select_data():
    create_database()
    flights_id_lst = ["PA0001", "PA0002"]
    df = select_flights(flights_id_lst)

    assert df.loc[0, "origin"] == "YUL"
    assert df.loc[1, "destination"] == "YYZ"


def test_load_data():
    create_database()
    f1 = Flight("PA3012", "YYZ", "HAN", "2026-12-04", "17:20", 3000.0, 350, 140, 1.02, "medium", "regular", True)
    f2 = Flight("PA3013", "YEG", "YHZ", "2026-11-04", "17:20", 2450.0, 350, 140, 1.02, "medium", "regular", True)
    f3 = Flight("PA3014", "YWG", "YUL", "2026-10-05", "17:20", 1200.0, 350, 140, 1.02, "medium", "regular", True)

    flights_lst = [f1, f2, f3]
    load_data(flights_lst)

    flights_id_lst = ["PA3012", "PA3013", "PA3014"]
    df = select_flights(flights_id_lst)

    assert df.loc[0, "flight_id"] == "PA3012"
    assert df.loc[1, "flight_id"] == "PA3013"
    assert df.loc[2, "flight_id"] == "PA3014"


def test_update_seats_remaining():
    create_database()

    # Load the Data
    f1 = Flight("PA3012", "YYZ", "HAN", "2026-12-04", "17:20", 3000.0, 350, 141, 1.02, "medium", "regular", True)
    f2 = Flight("PA3013", "YEG", "YHZ", "2026-11-04", "17:20", 2450.0, 350, 151, 1.02, "medium", "regular", True)
    f3 = Flight("PA3014", "YWG", "YUL", "2026-10-05", "17:20", 1200.0, 350, 161, 1.02, "medium", "regular", True)

    flights_lst = [f1, f2, f3]
    load_data(flights_lst)

    # Update the data
    update_seats_remaining(f2.flight_id)
    update_seats_remaining(f3.flight_id, 5)

    # Check the results
    flights_id_lst = ["PA3012", "PA3013", "PA3014"]
    df = select_flights(flights_id_lst)

    assert df.loc[0, "seats_remaining"] == 141
    assert df.loc[1, "seats_remaining"] == 150
    assert df.loc[2, "seats_remaining"] == 156


def test_update_seats_remaining_invalid_requests():
    create_database()
    f1 = Flight("PA3012", "YYZ", "HAN", "2026-12-04", "17:20", 3000.0, 350, 10, 1.02, "medium", "regular", True)
    load_data([f1])
 
    # unknown flight, too many seats, zero, negative, and non-integer requests are all rejected
    with pytest.raises(ValueError):
        update_seats_remaining("PA-Non-existent", 1)
    with pytest.raises(ValueError):
        update_seats_remaining("PA3012", 11)
    with pytest.raises(ValueError):
        update_seats_remaining("PA3012", 0)
    with pytest.raises(ValueError):
        update_seats_remaining("PA3012", -1)
    with pytest.raises(ValueError):
        update_seats_remaining("PA3012", 1.5)
 
    # nothing was changed by the rejected requests
    assert select_flights(["PA3012"]).loc[0, "seats_remaining"] == 10


def test_update_seats_remaining_sold_out():
    create_database()
    f1 = Flight("PA3012", "YYZ", "HAN", "2026-12-04", "17:20", 3000.0, 350, 2, 1.02, "medium", "regular", True)
    load_data([f1])
 
    # cannot book more seats than are available
    update_seats_remaining("PA3012", 2)
    assert select_flights(["PA3012"]).loc[0, "seats_remaining"] == 0
    with pytest.raises(ValueError):
        update_seats_remaining("PA3012", 1)


def test_delete_flight():
    create_database()

    # Load the Data
    f1 = Flight("PA3012", "YYZ", "HAN", "2026-12-04", "17:20", 3000.0, 350, 140, 1.02, "medium", "regular", True)
    f2 = Flight("PA3013", "YEG", "YHZ", "2026-11-04", "17:20", 2450.0, 350, 140, 1.02, "medium", "regular", True)
    f3 = Flight("PA3014", "YWG", "YUL", "2026-10-05", "17:20", 1200.0, 350, 140, 1.02, "medium", "regular", True)

    flights_lst = [f1, f2, f3]
    load_data(flights_lst)

    # Delete the flights
    flight_delete_lst = ["PA-Non-existent", "PA3012", "PA3013", "PA3014"]
    delete_flight(flight_delete_lst)

    # Check the results
    df = select_flights(flight_delete_lst)

    assert df.empty
