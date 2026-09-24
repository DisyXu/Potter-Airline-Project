"""
Integrate all the modules and run the main program. This is the entry point for the Potter Airlines project.
"""
# import modules
import sqlite3
import pandas as pd

# import functions from other modules
from analysis import load_flights, clean_flights, filter_flights, rank_flights, summarize_by
from flight import Flight
from pricing import calculate_price
from sql_crud import create_database, load_data, select_flights, delete_flight, update_seat_remaining

# helper function to calculate price for a single flight
def get_price(row):
    # Turn one row of the table into a Flight, then calculate its price
    flight = Flight(row["flight_id"], row["origin"], row["destination"],
                    row["departure_date"], row["departure_time"], row["base_fare_cad"],
                    row["capacity"], row["seats_remaining"], row["demand_score"],
                    row["demand_level"], row["season"], row["is_weekend"])
    return round(calculate_price(flight), 2)

# main program
def main():
    # show every column when printing tables (no "..." in the middle)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)

    columns = ["flight_id", "origin", "destination", "departure_date",
               "seats_remaining", "base_fare_cad", "price"]

    # Step 1: create the SQLite database from the CSV file
    print("\n--- Step 1: Create database ---")
    create_database()

    # Step 2: read all flights back from SQLite and clean them
    print("\n--- Step 2: Load flights ---")
    flights = load_flights()
    print("Number of flights:", len(flights))

    # Step 3: calculate a price for every flight
    print("\n--- Step 3: Price all flights ---")
    # apply() calls get_price on every row (axis=1 means row by row)
    flights["price"] = flights.apply(get_price, axis=1)

    # sold-out or departed flights have no price, so remove them
    flights = flights.dropna(subset=["price"])
    print("Flights with a price:", len(flights))

    # Step 4: filter, rank, and group the flights
    print("\n--- Step 4a: 10 cheapest flights ---")
    print(rank_flights(flights)[columns])

    print("\n--- Step 4b: YYZ to YVR under $400 ---")
    print(filter_flights(flights, "YYZ", "YVR", max_price=400)[columns])

    print("\n--- Step 4c: Average price by season ---")
    print(summarize_by(flights, "season"))

    # Step 5: update seats remaining, then show the new price
    print("\n--- Step 5: Update seats remaining ---")
    row = clean_flights(select_flights(["PA0059"])).iloc[0]
    print("Before: seats =", row["seats_remaining"], " price =", get_price(row))

    # with sqlite3.connect("potter_airline.db") as conn:
    #     conn.execute("UPDATE flights SET seats_remaining = ? WHERE flight_id = ?",
    #                  (5, "PA0059"))
    current_seats = select_flights(["PA0059"])["seats_remaining"]
    update_seat_remaining("PA0059", current_seats)

    row = clean_flights(select_flights(["PA0059"])).iloc[0]
    print("After:  seats =", row["seats_remaining"], " price =", get_price(row))

    # Step 6: insert a test flight, read it back, then delete it
    print("\n--- Step 6: Insert and delete a flight ---")
    test_flight = Flight("PA9999", "YYZ", "YVR", "2026-12-24", "09:00",
                         300.0, 200, 50, 1.2, "high", "peak", False)
    load_data([test_flight])
    print(select_flights(["PA9999"]))
    delete_flight(["PA9999"])

    # Step 7: edge case - a flight with more seats left than its capacity
    print("\n--- Step 7: Edge case ---")
    bad_flight = Flight("PA0000", "YYZ", "YUL", "2026-12-01", "08:00",
                        150.0, 100, 150, 1.0, "medium", "regular", False)
    try:
        calculate_price(bad_flight)
    except ValueError as error:
        print("Caught a problem:", error)


if __name__ == "__main__":
    main()
