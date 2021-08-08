import argparse


def parse_args():
    """Define and parse the arguments"""

    p = argparse.ArgumentParser()

    # requiren arguments
    p.add_argument(
        'data_source', help='Flight data source (csv file)', type=str)

    p.add_argument('origin', help='Origin airport of the trip', type=str)

    p.add_argument('destination', help='Destination airport of the trip',
                   type=str)

    # optional arguments
    p.add_argument('--return',
                   help='Tell whether return flights should be searched, default False',
                   dest='return_flight', action='store_true')
    p.set_defaults(return_flight=False)

    p.add_argument('--bags', help='Number of bags allowed, default 0',
                   default=0, type=int)

    args = vars(p.parse_args())

    return args
