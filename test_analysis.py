import pandas as pd

from analysis import (
    category_counts, clean_flights, dataset_overview, filter_flights, rank_flights, summarize_by,
)


def make_flights():
    """Three small flights; PA3 could not be priced (price is NaN)."""
    return pd.DataFrame([
        # flight_id, origin, dest, date, fare, capacity, seats, demand, season, weekend, price
        ["PA1", "YYZ", "YVR", "2026-10-05", 200.0, 100, 50, 1.0, "regular", "0", 330.75],
        ["PA2", "YYZ", "YVR", "2026-12-20", 200.0, 100, 10, 1.4, "peak", "1", 620.00],
        ["PA3", "YUL", "YYZ", "2026-10-03", 150.0, 100, 0, 1.0, "regular", "0", None],
    ], columns=["flight_id", "origin", "destination", "departure_date",
                "base_fare_cad", "capacity", "seats_remaining", "demand_score",
                "season", "is_weekend", "price"])


def test_weekend_text_from_sqlite_is_parsed_correctly():
    flights = clean_flights(make_flights())

    assert flights["is_weekend"].tolist() == [False, True, False]


def test_invalid_rows_are_dropped():
    flights = make_flights()
    flights.loc[0, "capacity"] = 0
    flights.loc[1, "seats_remaining"] = 150

    assert clean_flights(flights)["flight_id"].tolist() == ["PA3"]


def test_filter_by_route_and_price():
    flights = clean_flights(make_flights()).dropna(subset=["price"])

    result = filter_flights(flights, origin="yyz", destination="YVR", max_price=400)

    assert result["flight_id"].tolist() == ["PA1"]


def test_rank_cheapest_first():
    flights = clean_flights(make_flights()).dropna(subset=["price"])

    assert rank_flights(flights)["flight_id"].tolist() == ["PA1", "PA2"]


def test_summary_counts_flights_per_group():
    flights = clean_flights(make_flights()).dropna(subset=["price"])

    summary = summarize_by(flights, "season")

    assert summary["flights"].sum() == 2


def test_overview_counts_routes_and_sold_out():
    overview = dataset_overview(clean_flights(make_flights()))

    assert overview["routes"] == 2
    assert overview["sold_out_flights"] == 1


def test_category_shares_sum_to_100():
    counts = category_counts(clean_flights(make_flights()), "season")

    assert counts["share_pct"].sum() == 100.0
