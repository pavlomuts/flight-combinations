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

    # set of flight numbers used to remove duplicates in given timetable
    flight_numbers = set()

    # construct time table without duplicates
    time_table = []
    for flight in reader:
        if flight['flight_no'] not in flight_numbers:

            flight_numbers.add(flight['flight_no'])

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


def add_trip_data(routes, bags_count):
    extended_routes = []

    for flights in routes:
        travel_time = str(flights[-1]['arrival'] - flights[0]['departure'])

        # datetime format back to string
        for flight in flights:
            flight['departure'] = flight['departure'].isoformat()
            flight['arrival'] = flight['arrival'].isoformat()

        extended_route = {}
        extended_route['flights'] = flights
        extended_route['bags_allowed'] = min(item['bags_allowed'] for item in flights)
        extended_route['bags_count'] = bags_count
        extended_route['destination'] = flights[-1]['destination']
        extended_route['origin'] = flights[0]['origin']
        extended_route['total_price'] = sum(
            item['base_price'] + bags_count * item['bag_price'] for item in flights)

        extended_route['travel_time'] = travel_time

        extended_routes.append(extended_route)

    return extended_routes


def construct_routes(origin, destination, bags_count, time_table):

    final_routes = []
    intermediate_routes = []

    for flight in time_table:
        print(flight)
        if flight['origin'] == origin:
            if flight['destination'] == destination:
                final_routes.append([flight])
            else:
                intermediate_routes.append([flight])

    while intermediate_routes:
        current_route = intermediate_routes.pop()
        airports_visited = set(item['origin'] for item in current_route)

    result = add_trip_data(final_routes, bags_count)
    res = json.dumps(result, indent=4)
    print(res)
