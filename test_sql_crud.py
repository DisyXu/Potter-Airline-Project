import pandas as pd
import numpy as np
import sqlite3
from sql_crud import (
    create_database,
    load_data,
    select_flights,
    update_seat_remaining,
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


def test_update_seat_remaining():
    create_database()

    # Load the Data
    f1 = Flight("PA3012", "YYZ", "HAN", "2026-12-04", "17:20", 3000.0, 350, 141, 1.02, "medium", "regular", True)
    f2 = Flight("PA3013", "YEG", "YHZ", "2026-11-04", "17:20", 2450.0, 350, 151, 1.02, "medium", "regular", True)
    f3 = Flight("PA3014", "YWG", "YUL", "2026-10-05", "17:20", 1200.0, 350, 161, 1.02, "medium", "regular", True)

    flights_lst = [f1, f2, f3]
    load_data(flights_lst)

    # Update the data
    update_seat_remaining("PA-Non-existent", 2500)
    update_seat_remaining(f2.flight_id, f2.seat_remaining)
    update_seat_remaining(f3.flight_id, f3.seat_remaining)

    # Check the results
    flights_id_lst = ["PA3012", "PA3013", "PA3014"]
    df = select_flights(flights_id_lst)

    assert df.loc[0, "seat_remaining"] == 141
    assert df.loc[1, "seat_remaining"] == 150
    assert df.loc[2, "seat_remaining"] == 160


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

    assert df is None
