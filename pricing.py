import numpy as np

def calculate_price (flight):
    # calculate factors
    base_fare = flight.base_fare_cad
    time_factor = calculate_time_factor(flight)
    demand_factor = flight.demand_score
    capacity_factor = calculate_capacity_factor(flight)
    seasonal_factor = calculate_seasonal_factor(flight)
    weekend_factor = calculate_weekend_factor(flight)

    # calculate price
    price = base_fare * time_factor * demand_factor * capacity_factor * seasonal_factor * weekend_factor

    # set min and max price
    min_price = base_fare * 0.7
    max_price = base_fare * 3.0

    # check min and max price
    if price < min_price:
        price = min_price
    elif price > max_price:
        price = max_price

    return round(price, 2)


def calculate_time_factor (flight):
    days_until_departure = flight.days_to_departure()
    
    # construct a sigmoid curve to calculate time factor
    max_premium = 0.5
    k = 0.35
    t0 = 7
    time_factor = 1 + (max_premium) / (1 + np.exp(k * (days_until_departure - t0)))

    return round(time_factor, 2)


def calculate_capacity_factor (flight):
    load_factor = 1 - (flight.seats_remaining / flight.capacity)
    capacity_factor = 1 + 0.45 * load_factor

    return(capacity_factor)


def calculate_seasonal_factor (flight):
    season = flight.season.lower()
    
    if (season == "peak"):
        seasonal_factor = 1.43
    elif (season == "shoulder"):
        seasonal_factor = 1.18
    else:
        seasonal_factor = 1

    return (seasonal_factor)


def calculate_weekend_factor (flight):
    if (flight.is_weekend == True):
        weekend_factor = 1.13
    else:
        weekend_factor = 1

    return (weekend_factor)