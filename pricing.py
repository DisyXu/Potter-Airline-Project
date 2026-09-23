def calculate_price (flight):
    # calculate factors
    time_factor = calculate_time_factor(flight)
    demand_factor = flight.demand_score
    capacity_factor = calculate_capacity_factor(flight)
    seasonal_factor = calculate_seasonal_factor(flight)
    weekend_factor = calculate_weekend_factor(flight)

    # initialize variables
    min_price = 45
    max_price = 1500

    # calculate price
    price = flight.base_fare_cad * time_factor * demand_factor * capacity_factor * seasonal_factor * weekend_factor

    # check min and max price
    if price < min_price:
        price = min_price
    elif price > max_price:
        price = max_price

    return (price)

def calculate_time_factor (flight):
    days_until_departure = flight.days_to_departure()
    if (days_until_departure < 0):
        raise ValueError("Days to departure must be greater than or equal to 0")
    
    if days_until_departure <= 7:
            time_factor = 1.35
    elif 8 <=days_until_departure <= 21:
        time_factor = 1.10
    else:
        time_factor = 1.00

    return (time_factor)

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
    # error checking
    if (flight.season != "peak" and flight.season != "shoulder" and flight.season != "regular"):
        raise ValueError("Season must be peak, shoulder, or regular")
    
    if (flight.season == "peak"):
        seasonal_factor = 1.43
    elif (flight.season == "shoulder"):
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



