# Potter Airlines – Dynamic Revenue Management System (Team 13)

## Purpose

A command-line system that prices fictional Potter Airlines flights dynamically and lets a user search and book them. It loads 1,000 flight records into a database, calculates a price for each flight from time, demand, capacity, season and weekend factors, and then runs an interactive booking flow where each booking reduces seats remaining (and therefore updates the next fare).

**Dataset assumptions**
- 1,000 fictional flights, each with a unique flight ID.
- Routes are origin/destination airport codes.
- Departure dates and times are fictional but structured to support the pricing logic.
- Base fares are in Canadian dollars (CAD).
- Capacity and seats remaining give the occupancy rate.
- Demand is stored as both a numeric demand score and a categorical demand level.
- Each flight is labeled by season and whether it departs on a weekend.

## Setup / Run

1. Install Python 3 and the dependencies:
   ```
   pip install pandas pytest
   ```
2. Keep all project files (`main.py`, `analysis.py`, `flight.py`, `sql_crud.py`, `test_*.py`) and the flight CSV in the same folder.
3. Run:
   ```
   python main.py
   ```

`main.py` then runs four steps:
1. Runs every `test_*.py` file with pytest. If any test fails, the program stops.
2. Creates the database from the CSV, loads the cleaned flights, calculates prices, and shows an overview dashboard (by season and average price per route).
3. Runs system checks: price bounds, SQL insert/select/delete, and edge cases (seats remaining > capacity, over-booking).
4. Starts interactive booking: enter origin, destination and a date range, pick from results (cheapest first), confirm, and receive a receipt. Type `q` at any prompt to quit.

## Design Choices

- **Modular structure:**  `flight.py` (Flight model with validation), `sql_crud.py` (database create/load/select/update/delete), and `analysis.py` (loading priced flights, filtering, summaries) keep responsibilities separate. `main.py` is the entry point and integrates functionality from all of the other project modules.
- **Tests gate the program:** the full test suite runs on every start, so the booking system never runs on broken code.
- **Validation at the source:** invalid data (e.g., seats remaining > capacity) is rejected when a `Flight` is created, and over-booking is rejected before anything is written.
- **Parameterized SQL queries** are used for database operations. The data is cleaned of invalid flights and past flights before being loaded into the database.
- **Prices reflect live inventory:** after each booking, flights are reloaded and repriced in the database, so fares rise as seats sell.
- **Terminal dashboard:** colored boxes and occupancy bars make results easy to read; results show at most 15 flights per search.

## Pricing Logic

`calculate_price` multiplies the base fare by five factors:

`price = base fare × time × demand × capacity × seasonal × weekend`

| Factor | How it works |
|---|---|
| Time | A sigmoid function; flights departing sooner get a larger factor. |
| Demand | Taken directly from the demand data. |
| Capacity | A load factor is calculated first (fewer seats remaining → more expensive), then applied to get the capacity factor. |
| Seasonal | Peak season is highest, shoulder season is medium, regular is the baseline. |
| Weekend | Weekend departures have a higher factor than the weekday baseline. |

**Bounds:** the price never falls below `base fare × 0.7` or exceeds `base fare × 3.0`. The system checks this for every flight on startup.

## Known Limitations

- The data is fictional, so prices and demand do not reflect real markets.
- Booking is one passenger, one-way, per transaction; there are no round trips, passenger details, payment, or user accounts.
- Bookings only decrement seats remaining; individual bookings are not stored (receipt references are generated per session).
- Demand values come straight from the dataset and do not update as bookings occur; only seats remaining (capacity factor) changes.
- Search shows at most 15 results and requires exact airport codes and `YYYY-MM-DD` dates, airport codes outside the database is rejected.
- The interface is terminal-only, and the tests must all pass before the program will start.