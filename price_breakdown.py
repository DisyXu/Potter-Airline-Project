"""Show how one flight's price is built, factor by factor.

Usage:  python price_breakdown.py PA0093
        python price_breakdown.py PA0282 --days 30    # pretend departure is 30 days away
"""
import sys
import pandas as pd
import pricing
from analysis import clean_flights, row_to_flight

args = sys.argv[1:]
flight_id = args[0] if args else "PA0093"
days_out = int(args[args.index("--days") + 1]) if "--days" in args else None
df = clean_flights(pd.read_csv("potter_airlines_flights.csv"))
f = row_to_flight(df[df["flight_id"] == flight_id].iloc[0])
if days_out is not None:                       # simulate "departure is N days away"
    f.days_to_departure = lambda reference_date=None: days_out

factors = [
    ("Time to departure", pricing.calculate_time_factor(f)),
    ("Demand score",      f.demand_score),
    ("Seats filled",      pricing.calculate_capacity_factor(f)),
    ("Season",            pricing.calculate_seasonal_factor(f)),
    ("Weekend",           pricing.calculate_weekend_factor(f)),
]
raw = f.base_fare_cad
when = f"{days_out} days before departure" if days_out is not None else str(f.departure_date)
print(f"\n{f.flight_id}  {f.origin} -> {f.destination}  {when}  ({f.season}, {f.seats_remaining}/{f.capacity} seats left)")
print(f"  Base fare          ${raw:>8.2f}")
for name, value in factors:
    raw *= value
    print(f"  x {name:<16} {value:>6.2f}   = ${raw:>8.2f}")
final = pricing.calculate_price(f)
note = "  <- capped at 3.0x base fare" if raw > f.base_fare_cad * 3 else ("  <- floored at 0.7x" if raw < f.base_fare_cad * 0.7 else "")
print(f"  Final price        ${final:>8.2f}{note}\n")
