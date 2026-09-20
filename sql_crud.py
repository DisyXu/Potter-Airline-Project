import pandas as pd
import numpy as np
import sqlite3


def create_database():
    df_flights = pd.read_csv(r"potter_airlines_flights.csv")

    with sqlite3.connect("potter_airline.db") as conn:
        conn.execute("""
            DROP TABLE IF EXISTS flights
        """)

        conn.execute("""
                CREATE TABLE flights (
                    flight_id TEXT PRIMARY KEY,
                    origin TEXT,
                    destination TEXT,
                    departure_date DATE,
                    departure_time TEXT,
                    base_fare_cad FLOAT,
                    capacity INT,
                    seats_remaining INT,
                    demand_score FLOAT,
                    demand_level TEXT,
                    season TEXT,
                    is_weekend TEXT
                )
            """)

        df_flights.to_sql("flights", conn, if_exists="append", index=False)
        print("Database created successfully")


def load_data(flights_lst):
    with sqlite3.connect("potter_airline.db") as conn:
        for flight in flights_lst:
            conn.execute("""
                INSERT INTO flights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                flight.flight_id,
                flight.origin,
                flight.destination,
                flight.departure_date,
                flight.departure_time,
                flight.base_fare_cad,
                flight.capacity,
                flight.seats_remaining,
                flight.demand_score,
                flight.demand_level,
                flight.season,
                flight.is_weekend,
            ))
    print("Flight(s) loaded successfully into the database")


def select_flights(flights_id_lst):
    with sqlite3.connect("potter_airline.db") as conn:
        all_results = []
        for flight_id in flights_id_lst:
            result_df = pd.read_sql_query("""
                        SELECT *
                        FROM flights
                        WHERE flight_id = ?
                        """, conn, params=(flight_id,))
            if result_df.empty:
                print(f"Flight {flight_id} can not be found in the database")
            all_results.append(result_df)
        if not pd.concat(all_results, ignore_index=True).empty:
            return pd.concat(all_results, ignore_index=True)


def update_base_fare(flight_update_lst):
    with sqlite3.connect("potter_airline.db") as conn:
        for flight in flight_update_lst:
            result = conn.execute("""
                        UPDATE flights
                        SET base_fare_cad = ?
                        WHERE flight_id = ?
                        """, (flight[1], flight[0]))


def delete_flight(flight_delete_lst):
    with sqlite3.connect("potter_airline.db") as conn:
        for flight_id in flight_delete_lst:
            if select_flights([flight_id]) is not None:
                conn.execute("""
                    DELETE FROM flights
                    WHERE flight_id = ?
                    """, (flight_id,))
                print(f"Flight {flight_id} deleted from database")