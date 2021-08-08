import csv
import json
import datetime
import copy


def print_combinations(input):
    """Main function that processes data source, generates flight combination 
    and converts the results to JSON"""

    # get input data
    data_source = input['data_source']
    origin = input['origin']
    destination = input['destination']
    return_flight = input['return_flight']
    bags_count = input['bags']

    #whole timetable
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
    """Process the data source file:
    - check whether given file exist
    - check if all needed fields are provided
    - check if particular fileds can be transformed into datetime format
    - check if particular fileds can be transformed into a number
    Reurn list of flights.
    """

    try:
        data_file = open(path_to_file)
    except FileNotFoundError as e:
        print(e)
        print("Please an existing data file")
        exit()

    reader = csv.DictReader(data_file)
    
    # check if all neccessary fields exist

    # define expected field names
    expected_fields = ['flight_no', 'origin', 'destination', 'departure',
                       'arrival', 'base_price', 'bag_price', 'bags_allowed']
    
    # set for quick searching
    obtained_fields = set(reader.fieldnames)

    if any(field not in obtained_fields for field in expected_fields):
        print("Some fields are missing, please refer to the examples " 
        "provided in the folder 'example'")
        exit()

    # list of data
    time_table = []

    for flight in reader:

        # convert time strings into datetime objects
        try:
            flight['departure'] = datetime.datetime.fromisoformat(
                flight['departure'])
            flight['arrival'] = datetime.datetime.fromisoformat(
                flight['arrival'])
        except ValueError as e:
            print(e)
            print("Please provide valid iso format string for date time fields")
            exit()

        # convert some fields from string into numbers
        try:
            flight['base_price'] = float(flight['base_price'])
            flight['bag_price'] = float(flight['bag_price'])
            flight['bags_allowed'] = int(flight['bags_allowed'])
        except ValueError as e:
            print(e)
            print("Please provide valid numbers for number fields")
            exit()

        time_table.append(flight)

    return time_table


def add_trip_data(all_routes, origin, destination, bags_count, return_flight):
    """Compute for each route additional data such as travel time, 
    total price etc and sort it by total price."""

    # list of all routes with additinal info
    ext_data_all_routes = []

    for route in all_routes:
        
        # in case of a return flight do not count a stay at the destination
        if return_flight:
            
            # find the destination flight
            for i in range(len(route)):
                if route[i]['destination'] == destination:
                    break
            
            # exclude time spent at destination
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

        # make dictionary that corresponds to requirements
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
    """Construct flights combinations between A and B with given restrictions: 
    - min_layover < layover < max_layover
    - Airports in the route must be unique
    - The earliest departure time may be given as optional argument
    
    Return all combinations
    """

    # list of complete routes that have full path from origin to destination
    complete_routes = []

    # list of incomplete routes that do not have a path from origin to destination
    incomplete_routes = []

    # add initial routes to the lists above
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
