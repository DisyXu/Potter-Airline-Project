## Flight Data Assumptions

- The dataset contains 1,000 fictional Potter Airlines flight records.
- Each flight has a unique flight ID.
- Routes are represented by origin and destination airport codes.
- Departure dates and times are fictional but structured to support pricing logic.
- Base fares are stored in Canadian dollars.
- Capacity and seats remaining are used to calculate occupancy rate.
- Demand is represented by both a numeric demand score and a categorical demand level.
- Flights are labeled by season and whether the departure occurs on a weekend.


SQLite was chosen because it is lightweight, requires no separate database server, and works well for a small project. Pandas is used to load the initial flight CSV data and return query results as DataFrames. SQL queries use parameters (?) instead of directly inserting values into query strings.

The module separates the main database operations into individual functions:

create_database() creates and initializes the flight table.
load_data() inserts new Flight objects (flight record) into the database.
select_flights() retrieves flights by flight ID.
update_base_fare() updates flights' base prices.
delete_flight() removes flights from the database using flight ID.