import csv
import json
import datetime
import copy


def generate_combinations(input):

    data_source = input['data_source']
    origin = input['origin']
    destination = input['destination']
    return_flight = input['return']
    bags_count = input['bags']

    time_table = get_data(data_source)

    construct_routes(origin, destination, bags_count,
                     time_table, return_flight)


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


def add_trip_data(all_routes, origin, destination, bags_count):

    ext_data_all_routes = []  # list of all routes with additinal info

    for route in all_routes:

        travel_time = str(route[-1]['arrival'] - route[0]['departure'])

        # make copy of object since we will change a mutable object
        formatted_route = copy.deepcopy(route)

        # format datetime back to string such that it can be serialized in JSON
        for flight in formatted_route:
            flight['departure'] = flight['departure'].isoformat()
            flight['arrival'] = flight['arrival'].isoformat()

        ext_data_single_route = {}
        ext_data_single_route['flights'] = formatted_route
        ext_data_single_route['bags_allowed'] = min(
            item['bags_allowed'] for item in formatted_route)
        ext_data_single_route['bags_count'] = bags_count
        ext_data_single_route['destination'] = destination
        ext_data_single_route['origin'] = origin
        ext_data_single_route['total_price'] = sum(
            item['base_price'] + bags_count * item['bag_price'] for item in formatted_route)

        ext_data_single_route['travel_time'] = travel_time

        ext_data_all_routes.append(ext_data_single_route)

    # sort routes by their total price
    ext_data_all_routes.sort(key=lambda x: x['total_price'])

    return ext_data_all_routes


def construct_routes_helper(A, B, bags, time_table, min_layover, max_layover, start_time=None):

    final_routes = []
    intermediate_routes = []

    for flight in time_table:

        if start_time is None:
            if flight['origin'] == A and bags <= flight['bags_allowed']:

                if flight['destination'] == B:
                    final_routes.append([flight])
                else:
                    intermediate_routes.append([flight])

        else:
            if (flight['departure'] > start_time and flight['origin'] == A and
                    bags <= flight['bags_allowed']):

                if flight['destination'] == B:
                    final_routes.append([flight])
                else:
                    intermediate_routes.append([flight])

    while intermediate_routes:

        current_route = intermediate_routes.pop()
        airports_visited = set(item['origin'] for item in current_route)

        for flight in time_table:

            # consider only the airports where we arrived
            if flight['origin'] == current_route[-1]['destination']:

                # compute layover time for this leg
                layover = flight['departure'] - current_route[-1]['arrival']

                # apply the restrictions above
                if (flight['destination'] not in airports_visited and
                    layover >= min_layover and layover <= max_layover and
                        bags <= flight['bags_allowed']):

                    # create new combinations based on the previous route
                    # we need to keep the original route and make combinations
                    # starting from the original
                    current_route_copy = copy.deepcopy(current_route)

                    # add new leg of the route
                    current_route_copy.append(flight)

                    if flight['destination'] == B:
                        final_routes.append(current_route_copy)
                    else:
                        intermediate_routes.append(current_route_copy)

    return final_routes


def construct_routes(origin, destination, bags_count, time_table, return_flight):

    # select the flights with the restrictions:
    # - no airports are repeated in the route
    # - layover at least 1 hour max 6 hours

    min_layover = datetime.timedelta(hours=1)
    max_layover = datetime.timedelta(hours=6)

    final_routes = construct_routes_helper(origin, destination, bags_count,
                                           time_table, min_layover, max_layover)

    # search for the return flights
    if return_flight:
        res = []
        for one_way in final_routes:
            start_time = one_way[-1]['arrival']
            return_routes = construct_routes_helper(destination, origin,
                                                    bags_count, time_table, 
                                                    min_layover, max_layover, 
                                                    start_time)

            for item in return_routes:
                if len(item) > 0:
                    one_way_copy = copy.deepcopy(one_way)
                    res.append(one_way_copy + item)
        
        final_routes = res

    # populate the results with additinal info
    result = add_trip_data(final_routes, origin, destination, bags_count)

    # convert to JSON
    res = json.dumps(result, indent=4)
    print(res)

    print("correct travel time")
