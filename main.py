"""
Potter Airlines Project - Team 13: 
    main.py is the entry point for the program. 
    It integrates all the modules and runs the main program.
 
Workflow:
  1. Run every test_*.py file with pytest and confirm that all tests pass.
  2. Create the database from the CSV, load and calculate price for all flights.
  3. Short system demo (multi-flight analysis, SQL CRUD, edge cases).
  4. Interactive booking: search -> ranked results -> choose a flight -> confirm -> seats - 1.
"""

import contextlib
import io
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from analysis import load_priced_flights, filter_flights, summarize_by, dataset_overview
from flight import Flight
from sql_crud import (create_database, load_data, select_flights,
                      delete_flight, update_seats_remaining)

BASE_DIR = Path(__file__).resolve().parent
BOX_WIDTH = 66          # inner width of boxes (banner and boxes line up at 70 columns)
MAX_SHOWN = 15          # max flights listed per search

# terminal colours
BOLD, DIM, RED, GREEN, YELLOW, CYAN = "1", "2", "31", "32", "33", "36"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
FILL_FROM, FILL_TO, TRACK_GREY = 238, 248, 254

class QuitProgram(Exception):
    """Raised when the user types 'q' at any prompt."""


# ------------------------------------- 0. Set up display dashboard -------------------------------------
def style(text, code):
    return f"\033[{code}m{text}\033[0m"


def vlen(text):
    # visible length of a string (ignores colour codes)
    return len(ANSI.sub("", text))


def money(value):
    return f"${value:,.2f}"


def bar(pct, width=10):
    # Cells are coloured spaces: a gradient grey for filled seats, a pale grey track for the rest.
    filled = round(pct / 100 * width)
    cells = []
    for i in range(width):
        if i < filled:
            grey = round(FILL_FROM + (FILL_TO - FILL_FROM) * i / max(width - 1, 1))
        else:
            grey = TRACK_GREY
        cells.append(f"\033[48;5;{grey}m \033[0m")
    return "".join(cells)


def banner(title, subtitle):
    print("\n╔" + "═" * (BOX_WIDTH + 2) + "╗")
    print("║" + style(title.center(BOX_WIDTH + 2), f"{BOLD};{YELLOW}") + "║")
    print("║" + subtitle.center(BOX_WIDTH + 2) + "║")
    print("╚" + "═" * (BOX_WIDTH + 2) + "╝")


def box(title, lines, color=CYAN):
    # Print lines inside a titled box; the box grows if a line is too wide.
    width = max([vlen(line) for line in lines] + [vlen(title) + 4, BOX_WIDTH])
    print("\n┌─ " + style(title, f"{BOLD};{color}") + " " + "─" * (width - vlen(title) - 1) + "┐")
    for line in lines:
        print("│ " + line + " " * (width - vlen(line)) + " │")
    print("└" + "─" * (width + 2) + "┘")


# ------------------------------------- 1. Run tests -------------------------------------
class ResultCollector:
    # pytest plugin that records the outcome of every test
    def __init__(self):
        self.results = []

    def pytest_runtest_logreport(self, report):
        if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
            self.results.append((report.nodeid, report.outcome))


def run_tests():
    test_files = sorted(BASE_DIR.glob("test_*.py"))
    if not test_files:
        box("Step 1: Test Results", ["No test files (test_*.py) found."], RED)
        return False

    collector, output = ResultCollector(), io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        exit_code = pytest.main(["-q", "--tb=short", "-p", "no:cacheprovider"]
                                + [str(f) for f in test_files], plugins=[collector])

    tags = {"passed": style("PASS", GREEN), "failed": style("FAIL", RED), "skipped": style("SKIP", YELLOW)}
    lines, current = [], None
    for nodeid, outcome in collector.results:
        file_name, _, test_name = nodeid.partition("::")
        if file_name != current:
            current = file_name
            lines.append(style(file_name, BOLD))
        lines.append(f"  {tags[outcome]}  {test_name}")

    passed = sum(outcome == "passed" for _, outcome in collector.results)
    failed = sum(outcome == "failed" for _, outcome in collector.results)
    ok = int(exit_code) == 0
    lines += ["", style(f"{passed} passed, {failed} failed, {len(collector.results)} total", GREEN if ok else RED)]
    box("Step 1: Test results", lines, GREEN if ok else RED)

    if not ok:
        print("\n--- pytest details ---")
        print(output.getvalue())
    return ok


# ------------------------------------- 2. Display flights overview -------------------------------------
def summary_box(title, label, summary):
    lines = [style(f"{label:<9}{'Flights':>8}{'Base fare':>12}{'Avg price':>12}  {'Occupancy':<16}", DIM)]
    for name, row in summary.iterrows():
        lines.append(f"{name:<9}{int(row['flights']):>8}{money(row['avg_base_fare']):>12}"
                     f"{money(row['avg_price']):>12}  {bar(row['avg_occupancy_rate'])} {row['avg_occupancy_rate']:>4.0f}%")
    box(title, lines)


def show_dashboard(flights):
    info = dataset_overview(flights)
    box("Step 2: Flights data overview", [
        f"Flights {info['flights']:<8}Routes {info['routes']:<8}Airports {info['airports']}",
        f"Departures  {info['first_departure']}  to  {info['last_departure']}",
        f"Sold out {info['sold_out_flights']:<7}Avg price {money(info['avg_price']):<11}Avg occupancy {info['avg_occupancy']}%",
    ])
    summary_box("Average price by season", "Season", summarize_by(flights, "season"))
    summary_box("Top 5 routes by average price", "Route", summarize_by(flights, "route").head(5))


# ------------------------------------- 3. Check assumptions and edge cases -------------------------------------
def run_system_checks(flights):
    results = []

    # price bounds (vectorized): every fare must stay within 0.7x - 3.0x of the base fare
    lower = flights["base_fare_cad"] * 0.7 - 0.01
    upper = flights["base_fare_cad"] * 3.0 + 0.01

    failed = flights[
        (flights["price"] < lower) |
        (flights["price"] > upper)
    ]

    results.append(("All prices within 0.7x - 3.0x of base fare", failed.empty))


    # SQL: insert -> select -> delete a test flight (parameterized queries)

    test_flight = Flight("PA9999", "YYZ", "YVR", "2026-12-24", "09:00", 300.0, 200, 50, 1.2, "medium", "peak", False)
    with contextlib.redirect_stdout(io.StringIO()):          # silence the CRUD print messages
        delete_flight(["PA9999"])
        load_data([test_flight])
        inserted = not select_flights(["PA9999"]).empty
        delete_flight(["PA9999"])
        deleted = select_flights(["PA9999"]).empty
    results.append(("SQL insert -> select -> delete", inserted and deleted))

    # edge case 1: more seats remaining than capacity is rejected
    try:
        Flight("PA0000", "YYZ", "YUL", "2026-12-01", "08:00", 150.0, 100, 150, 1.0, "medium", "regular", False)
        rejected = False
    except ValueError:
        rejected = True
    results.append(("Edge case: seats remaining > capacity is rejected", rejected))

    # edge case 2: booking more seats than a flight has is rejected (nothing is written)
    try:
        update_seats_remaining(flights.iloc[0]["flight_id"], 10**6)
        rejected = False
    except ValueError:
        rejected = True
    results.append(("Edge case: over-booking is rejected", rejected))

    lines = [f"{style('PASS', GREEN) if ok else style('FAIL', RED)}  {name}" for name, ok in results]
    box("Step 3: Check assumptions and edge cases", lines, GREEN if all(ok for _, ok in results) else RED)


# ------------------------------------- 4. Interactive booking -------------------------------------
def ask(prompt):
    answer = input(f"  {prompt} > ").strip()
    if answer.lower() in ("q", "quit", "exit"):
        raise QuitProgram
    return answer


def ask_yes_no(prompt):
    while True:
        answer = ask(f"{prompt} (y/n)").lower()
        if answer in ("y", "yes", "n", "no"):
            return answer.startswith("y")
        print("  Please answer y or n.")


def ask_airport(prompt, airports):
    while True:
        code = ask(prompt).upper()
        if code in airports:
            return code
        print(f"  Unknown airport '{code}'. Choose from: {' '.join(airports)}")


def ask_date(prompt):
    while True:
        try:
            return datetime.strptime(ask(prompt), "%Y-%m-%d").date()
        except ValueError:
            print("  Please enter a date as YYYY-MM-DD, e.g. 2026-10-15.")


def ask_trip(airports):
    origin = ask_airport("From (airport code)", airports)
    destination = ask_airport("To (airport code)", airports)
    while destination == origin:
        print("  Origin and destination must be different.")
        destination = ask_airport("To (airport code)", airports)
    start = ask_date("Earliest departure date (YYYY-MM-DD)")
    end = ask_date("Latest departure date   (YYYY-MM-DD)")
    while end < start:
        print("  The latest date must not be before the earliest date.")
        end = ask_date("Latest departure date   (YYYY-MM-DD)")
    return origin, destination, start, end


def show_results(origin, destination, start, end, results, shown):
    header = (f"{'#':>2}  {'Flight':<8}{'Route':<11}{'Date':<10}  {'Time':<7}"
              f"{'Seats':>5}  {'Occupancy':<15}  {'Price':>10}")
    lines = [style(header, DIM)]
    for i, (_, r) in enumerate(shown.iterrows(), start=1):
        price = f"{money(r['price']):>10}"
        lines.append(f"{i:>2}  {r['flight_id']:<8}{r['origin'] + '->' + r['destination']:<11}"
                     f"{r['departure_date']:%Y-%m-%d}  {r['departure_time']:<7}{r['seats_remaining']:>5}  "
                     f"{bar(r['occupancy_rate'])} {r['occupancy_rate']:>3.0f}%  "
                     f"{style(price, GREEN) if i == 1 else price}")
    lines.append("")
    lines.append(f"{len(results)} flight(s) found, cheapest first"
                 + (f" (showing {MAX_SHOWN})" if len(results) > MAX_SHOWN else ""))
    box(f"{origin} -> {destination}   {start} to {end}", lines)


def choose_flight(shown):
    # Ask which flight to book and confirm; returns the chosen row, or None.
    while True:
        raw = ask("Enter the # of the flight to book (0 = cancel)")
        if raw.isdigit() and 0 <= int(raw) <= len(shown):
            break
        print(f"  Please enter a number from 0 to {len(shown)}.")
    if int(raw) == 0:
        return None

    flight = shown.iloc[int(raw) - 1]
    box("Your trip", [
        f"Flight     {flight['flight_id']}",
        f"Route      {flight['origin']} -> {flight['destination']}",
        f"Departure  {flight['departure_date']:%Y-%m-%d} at {flight['departure_time']}",
        f"Fare       {style(money(flight['price']), BOLD)}  (1 passenger)",
    ])
    if not ask_yes_no("Confirm booking?"):
        print("  Booking cancelled.")
        return None
    return flight


def show_receipt(flight, flights):
    updated = flights.loc[flights["flight_id"] == flight["flight_id"]].iloc[0]
    next_fare = "sold out" if updated["seats_remaining"] == 0 else money(updated["price"])
    box("BOOKING CONFIRMED", [
        f"Reference   PB-{uuid.uuid4().hex[:6].upper()}",
        f"Flight      {flight['flight_id']}   {flight['origin']} -> {flight['destination']}",
        f"Departure   {flight['departure_date']:%Y-%m-%d} at {flight['departure_time']}",
        f"Fare paid   {money(flight['price'])}",
        "",
        f"Seats left  {int(updated['seats_remaining'])} of {int(updated['capacity'])}",
        f"Next fare   {next_fare}",
    ], GREEN)


def booking_loop(flights):
    info = dataset_overview(flights)
    airports = sorted(set(flights["origin"]) | set(flights["destination"]))
    box("Step 4: Book a flight", [
        "Airports    " + " ".join(airports[:12]),
        *["            " + " ".join(airports[i:i + 12]) for i in range(12, len(airports), 12)],
        f"Departures  {info['first_departure']} to {info['last_departure']}",
        style("Type q at any prompt to quit", DIM),
    ])

    while True:
        print()
        origin, destination, start, end = ask_trip(airports)
        results = filter_flights(flights, origin, destination, start_date=start,
                                 end_date=end, available_only=True)
        if results.empty:
            box("No flights found", [f"No available flights from {origin} to {destination}",
                                     f"between {start} and {end}."], YELLOW)
        else:
            shown = results.head(MAX_SHOWN)
            show_results(origin, destination, start, end, results, shown)
            chosen = choose_flight(shown)
            if chosen is not None:
                try:
                    update_seats_remaining(chosen["flight_id"], 1)
                except ValueError as error:
                    print(f"  Booking failed: {error}")
                else:
                    flights = load_priced_flights()          # prices now reflect the new seat count
                    show_receipt(chosen, flights)
        if not ask_yes_no("Search for another trip?"):
            break
    print("\n  Thank you for flying with Potter Airlines!\n")


# ----------------------------------------------- main -----------------------------------------------
def main():
    os.chdir(BASE_DIR)                                       # so the CSV and .db paths resolve
    banner("POTTER AIRLINES", "Dynamic Revenue Management System")

    if not run_tests():
        print(style("\nSome tests failed. Fix them before starting the booking system.", RED))
        sys.exit(1)

    with contextlib.redirect_stdout(io.StringIO()):
        create_database()
    flights = load_priced_flights()
    show_dashboard(flights)
    run_system_checks(flights)

    try:
        booking_loop(flights)
    except (QuitProgram, KeyboardInterrupt, EOFError):
        print("\n\n  Goodbye!\n")


if __name__ == "__main__":
    main()