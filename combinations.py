import csv
import json
import datetime
import copy


def print_combinations(input):

    data_source = input['data_source']
    origin = input['origin']
    destination = input['destination']
    return_flight = input['return']
    bags_count = input['bags']

    time_table = get_data(data_source)

    # select the flights with the restrictions:
    # - no airports are repeated in the route
    # - layover at least 1 hour max 6 hours
    min_layover = datetime.timedelta(hours=1)
    max_layover = datetime.timedelta(hours=6)

    # get flight combinations between origin and destination, one way
    flights = construct_routes(origin, destination, bags_count, time_table,
                               min_layover, max_layover)

    # search for the return flights
    if return_flight:

        # flights including the return flights
        all_flights = []

        for one_way_route in flights:
            # use the condition that departure time of the return flight
            # cannot be prior to arrival at the destination
            start_time = one_way_route[-1]['arrival']

            # get flight combinations between destination and origin
            return_routes_all = construct_routes(destination, origin, bags_count,
                                                 time_table, min_layover,
                                                 max_layover, start_time)

            for return_route in return_routes_all:
                # if return flight is empty then we don't consider it in
                # final routes

                if len(return_route) > 0:
                    # make the copy nefore merging, since we operate with
                    # mutable object
                    one_way_copy = copy.deepcopy(one_way_route)

                    # merge one way and return route
                    all_flights.append(one_way_copy + return_route)

        flights = all_flights

    # populate the results with additinal info like travel time, total price etc.
    extended_flights = add_trip_data(flights, origin, destination, bags_count,
                                     return_flight)

    # convert to JSON and print
    print(json.dumps(extended_flights, indent=4))


def get_data(path_to_file):

    try:
        data_file = open(path_to_file)
    except FileNotFoundError as e:
        print(e)
        exit()

    reader = csv.DictReader(data_file)

    time_table = []

    for flight in reader:
        
        # convert time strings into datetime objects 
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


def add_trip_data(all_routes, origin, destination, bags_count, return_flight):

    ext_data_all_routes = []  # list of all routes with additinal info

    for route in all_routes:

        if return_flight:

            for i in range(len(route)):
                if route[i]['destination'] == destination:
                    break

            travel_time = str(route[i]['arrival'] - route[0]['departure'] +
                              route[-1]['arrival'] - route[i + 1]['departure'])
        else:
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


def construct_routes(A, B, bags, time_table, min_layover, max_layover, start_time=None):

    # list of complete routes that have full path from origin to destination
    complete_routes = []

    # list of incomplete routes that do not have a path from origin to destination
    incomplete_routes = []

    for flight in time_table:

        if start_time is None:
            if flight['origin'] == A and bags <= flight['bags_allowed']:

                if flight['destination'] == B:
                    # this route is complete
                    complete_routes.append([flight])
                else:
                    incomplete_routes.append([flight])

        else:
            # case when we have a return flight:
            # we cannot start before arrival to destination
            if (flight['departure'] > start_time and flight['origin'] == A and
                    bags <= flight['bags_allowed']):

                if flight['destination'] == B:
                    # this route is complete
                    complete_routes.append([flight])
                else:
                    incomplete_routes.append([flight])

    # use incomplete routes to continue constructing the path to destination
    while incomplete_routes:

        current_route = incomplete_routes.pop()

        # get the visited airports in order to prevent returning back to it
        airports_visited = set(item['origin'] for item in current_route)

        for flight in time_table:

            # consider only the airports where we arrived
            if flight['origin'] == current_route[-1]['destination']:

                # compute layover time for this potential leg
                layover = flight['departure'] - current_route[-1]['arrival']

                # apply the layover restrictions
                if (flight['destination'] not in airports_visited and
                    layover >= min_layover and layover <= max_layover and
                        bags <= flight['bags_allowed']):

                    # create new combinations by appending to the current route
                    # a new leg

                    # we need to keep the original incomplete route starting
                    # therefore do the copy of it
                    current_route_copy = copy.deepcopy(current_route)

                    # add new leg of the route
                    current_route_copy.append(flight)

                    if flight['destination'] == B:
                        # arrived
                        complete_routes.append(current_route_copy)
                    else:
                        incomplete_routes.append(current_route_copy)

    return complete_routes
