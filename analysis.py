"""
Data cleaning and multi-flight analysis for Potter Airlines.
"""
# import modules
import sqlite3

import pandas as pd

# set constants
DB_PATH = "potter_airline.db"
PRICE_COLUMN = "price"
VALID_SEASONS = ["peak", "shoulder", "regular"]

# data cleaning
def load_flights():
    # Read every flight from SQLite and return a cleaned DataFrame.
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM flights", conn)
    return clean_flights(df)


def clean_flights(df):
    # Fix column types, drop rows that break basic data rules, add derived columns.
    df = df.copy()
    df["departure_date"] = pd.to_datetime(df["departure_date"])
    # SQLite returns is_weekend as "0"/"1" text; bool("0") would be True
    df["is_weekend"] = df["is_weekend"].astype(str).isin(["1", "True"])

    # identify invalid rows based on basic data rules
    valid = (
        (df["capacity"] > 0)
        & df["seats_remaining"].between(0, df["capacity"])
        & (df["base_fare_cad"] > 0)
        & (df["demand_score"] > 0)
        & df["season"].isin(VALID_SEASONS)
    )

    # keep only valid rows and drop duplicates by flight_id
    invalid_ids = df.loc[~valid, "flight_id"].tolist()
    if invalid_ids:
        print(f"Dropped invalid flights: {invalid_ids}")
    df = df[valid].drop_duplicates(subset="flight_id")

    # checks on the cleaned dataset
    assert df["flight_id"].is_unique, "Flight IDs must be unique"
    assert (df["seats_remaining"] <= df["capacity"]).all(), "Seats cannot exceed capacity"

    # derived columns used by the analysis below
    df["route"] = df["origin"] + "-" + df["destination"]
    df["occupancy_rate"] = ((df["capacity"] - df["seats_remaining"]) / df["capacity"] * 100).round(2)
    return df

# dataset overview
def dataset_overview(df):
    # Headline facts about the cleaned dataset.
    return {
        "flights": len(df),
        "routes": df["route"].nunique(),
        "airports": len(set(df["origin"]) | set(df["destination"])),
        "first_departure": df["departure_date"].min().date(),
        "last_departure": df["departure_date"].max().date(),
        "sold_out_flights": int((df["seats_remaining"] == 0).sum()),
    }


def numeric_summary(df):
    # describe() statistics for the main numeric columns.
    columns = ["base_fare_cad", PRICE_COLUMN, "capacity", "seats_remaining",
               "demand_score", "occupancy_rate"]
    return df[columns].describe().round(2)


def category_counts(df, column):
    # Count and percentage share of each value in a categorical column.
    counts = df[column].value_counts()
    return pd.DataFrame({
        "flights": counts,
        "share_pct": (counts / counts.sum() * 100).round(1),
    })

# filter and rank
def filter_flights(df, origin=None, destination=None, max_price=None):
    # Flights matching every filter given, cheapest first; None or blank means any.
    mask = pd.Series(True, index=df.index)
    if origin:
        mask &= df["origin"] == origin.upper()
    if destination:
        mask &= df["destination"] == destination.upper()
    if max_price is not None:
        mask &= df[PRICE_COLUMN] <= max_price
    return df[mask].sort_values([PRICE_COLUMN, "flight_id"])


def rank_flights(df, by=PRICE_COLUMN, ascending=True, n=10):
    # Top-n flights sorted by any column; flight_id breaks ties.
    return df.sort_values([by, "flight_id"], ascending=[ascending, True]).head(n)

# group analysis
def summarize_by(df, by):
    # Flight count, average fare, and average occupancy per group.
    return (
        df.groupby(by)
        .agg(
            flights=("flight_id", "count"),
            avg_base_fare=("base_fare_cad", "mean"),
            avg_price=(PRICE_COLUMN, "mean"),
            avg_occupancy_rate=("occupancy_rate", "mean"),
        )
        .round(2)
        .sort_values("avg_price", ascending=False)
    )
