# Potter Airlines – Dynamic Revenue Management System (Team 13)

## Purpose

A command-line system that prices fictional Potter Airlines flights dynamically and lets a user search and book them. It loads 1,000 flight records into a database, calculates a price for each flight from time, demand, capacity, season and weekend factors, and then runs an interactive booking flow where each booking reduces seats remaining (and therefore updates the next fare).

## Dataset

The project uses one synthetic file, `potter_airlines_flights.csv`, with **1,000 flights** and **12 columns**.
Each row is one scheduled flight. The data has no missing values, no duplicate `flight_id`s, and no flights
where origin equals destination. All values are fictional but structured to support the pricing logic.

  
### Columns

| Column | Type | Description | Values in the data |
|---|---|---|---|
| `flight_id` | text | Unique flight identifier (primary key in SQLite) | `PA0001` to `PA1000` |
| `origin` | text | Departure airport code | 8 airports |
| `destination` | text | Arrival airport code | 8 airports, never equal to `origin` |
| `departure_date` | date | Departure date (`YYYY-MM-DD`) | 2026-09-18 to 2027-03-16 |
| `departure_time` | text | Local departure time (`HH:MM`) | 7 slots: 06:30, 08:15, 10:45, 13:20, 16:10, 18:35, 21:05 |
| `base_fare_cad` | float | Base fare in CAD before any pricing factors | 85.83 to 285.98 (mean 149.72) |
| `capacity` | int | Total seats on the aircraft | 120, 150, 180 or 220 |
| `seats_remaining` | int | Unsold seats; the only column that changes when a flight is booked | 0 to 202 (mean 83.3) |
| `demand_score` | float | Demand multiplier used directly as a pricing factor | 0.72 to 1.45 (mean 1.10) |
| `demand_level` | text | Category of `demand_score` | `low` (0.72 to 0.94), `medium` (0.95 to 1.14), `high` (1.15 to 1.45) |
| `season` | text | Travel season of the departure date | `regular` (509), `peak` (318), `shoulder` (173) |
| `is_weekend` | bool | True if the departure date is a Saturday or Sunday | True (279), False (721) |


- `origin` and `destination` are from 8 Canadian airports (YEG, YHZ, YOW, YUL, YVR, YWG, YYC, YYZ) with 20 directional routes
- `season` follows the calendar: `peak` is 1 Dec to 31 Jan, `shoulder` is November, and every other date is `regular`


### Sample rows

First five rows of the CSV:

| flight_id | origin | destination | departure_date | departure_time | base_fare_cad | capacity | seats_remaining | demand_score | demand_level | season | is_weekend |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PA0001 | YUL | YYZ | 2026-09-24 | 18:35 | 110.46 | 180 | 0 | 1.32 | high | regular | False |
| PA0002 | YWG | YYZ | 2026-10-10 | 16:10 | 146.71 | 220 | 1 | 1.05 | medium | regular | True |
| PA0003 | YHZ | YUL | 2026-09-24 | 16:10 | 132.83 | 150 | 150 | 0.81 | low | regular | False |
| PA0004 | YYC | YEG | 2027-02-15 | 10:45 | 93.53 | 120 | 84 | 0.88 | low | regular | False |
| PA0005 | YYZ | YHZ | 2026-10-27 | 08:15 | 165.21 | 180 | 46 | 1.08 | medium | regular | False |

  
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

- **Modular structure:**  `flight.py` (Flight model with validation), `sql_crud.py` (database create/load/select/update/delete), `pricing.py` (dynamic flight pricing calculation) and `analysis.py` (loading priced flights, filtering, summaries) keep responsibilities separate. `main.py` is the entry point and integrates functionality from all of the other project modules.
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
