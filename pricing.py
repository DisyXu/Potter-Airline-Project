import numpy as np


def calculate_price (flight):
    # check errors
    if flight.capacity <= 0:
        raise ValueError("capacity must be greater than 0")
    if flight.seats_remaining <= 0 or flight.seats_remaining > flight.capacity:
        raise ValueError("seats_remaining must be between 1 and capacity")

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
    if (days_until_departure < 0):
        raise ValueError("Days to departure must be greater than or equal to 0")

    # construct a sigmoid curve to calculate time factor
    max_premium = 0.5
    k = 0.35
    t0 = 7
    time_factor = 1 + (max_premium) / (1 + np.exp(k * (days_until_departure - t0)))

    return round(time_factor, 2)


def calculate_capacity_factor (flight):
    # error checking
    if (flight.seats_remaining <= 0):
         raise ValueError("Seats remaining must be greater than 0")
    if (flight.capacity <= 0):
        raise ValueError("Capacity must be greater than 0")
    if (flight.capacity < flight.seats_remaining):
        raise ValueError("Capacity must be greater than seats remaining")

    load_factor = 1 - (flight.seats_remaining / flight.capacity)
    capacity_factor = 1 + 0.45 * load_factor

    return(capacity_factor)


def calculate_seasonal_factor (flight):
    season = flight.season.lower()
    # error checking
    if (season != "peak" and season != "shoulder" and season != "regular"):
        raise ValueError("Season must be peak, shoulder, or regular")
    
    if (season == "peak"):
        seasonal_factor = 1.43
    elif (season == "shoulder"):
        seasonal_factor = 1.18
    else:
        seasonal_factor = 1

    return (seasonal_factor)


def calculate_weekend_factor (flight):
    # error checking
    if (not(isinstance(flight.is_weekend, bool))):
        raise TypeError("Weekend must be True or False") 
    
    if (flight.is_weekend == True):
        weekend_factor = 1.13
    else:
        weekend_factor = 1

    return (weekend_factor)



