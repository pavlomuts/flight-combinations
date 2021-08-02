import argparse

def parse_args():
    # parsing the arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "data_source", help="Flight data source (csv file)", type=str)

    parser.add_argument("origin", help="Origin airport of the trip", type=str)

    parser.add_argument(
        "destination", help="Destination airport of the trip", type=str)

    parser.add_argument("-r", "--return", help="Tell whether return flights should be searched, default False",
                        default=False, type=bool)

    parser.add_argument("-b", "--bags", help="Number of bags allowed, default 0",
                        default=0, type=int)

    args = vars(parser.parse_args())

    data_source = args["data_source"]
    origin = args["origin"]
    destination = args["destination"]
    return_flight = args["return"]
    bags = args["bags"]

    return data_source, origin, destination, return_flight, bags
