import csv
import json
import datetime


def generate_combinations(input):

    data_source = input['data_source']
    origin = input['origin']
    destination = input['destination']
    return_flight = input['return']
    bags_count = input['bags']

    time_table = get_data(data_source)

    construct_routes(origin, destination, bags_count, time_table)


def get_data(path_to_file):

    try:
        data_file = open(path_to_file)
    except FileNotFoundError as e:
        print(e.args)
        exit()

    reader = csv.DictReader(data_file)

    time_table = []

    for flight in reader:
        flight['departure'] = datetime.datetime.fromisoformat(
            flight['departure'])
        flight['arrival'] = datetime.datetime.fromisoformat(
            flight['arrival'])

        # convert some fields from string into numbers
        flight['base_price'] = float(flight['base_price'])
        flight['bag_price'] = float(flight['bag_price'])
        flight['bags_allowed'] = int(flight['bags_allowed'])

        time_table.append(flight)

    # todo make validation of data

    return time_table


def add_trip_data(routes, origin, destination, bags_count):
    ext_data_routes = [] # list of all routes with additinal info

    for flights in routes:
        travel_time = str(flights[-1]['arrival'] - flights[0]['departure'])
        
        # format datetime back to string such that json can serialize it
        for flight in flights:
            flight['departure'] = flight['departure'].isoformat()
            flight['arrival'] = flight['arrival'].isoformat()

        single_route = {}
        single_route['flights'] = flights
        single_route['bags_allowed'] = min(item['bags_allowed'] for item in flights)
        single_route['bags_count'] = bags_count
        single_route['destination'] = destination
        single_route['origin'] = origin
        single_route['total_price'] = sum(
            item['base_price'] + bags_count * item['bag_price'] for item in flights)

        single_route['travel_time'] = travel_time

        ext_data_routes.append(single_route)
    
    # sort routes by their total price
    ext_data_routes.sort(key=lambda x: x['total_price'])

    return ext_data_routes


def construct_routes(origin, destination, bags_count, time_table):

    final_routes = []
    intermediate_routes = []

    for flight in time_table:
        if flight['origin'] == origin:
            if flight['destination'] == destination:
                final_routes.append([flight])
            else:
                intermediate_routes.append([flight])

    while intermediate_routes:
        current_route = intermediate_routes.pop()
        airports_visited = set(item['origin'] for item in current_route)

    # populate the results with additinal info
    result = add_trip_data(final_routes, origin, destination, bags_count)

    # convert to JSON
    res = json.dumps(result, indent=4)
    print(res)
