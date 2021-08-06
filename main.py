from source.arg_parser import parse_args
from source.combinations import print_combinations


def main():
    """Main function"""
    input = parse_args()

    print_combinations(input)


if __name__ == '__main__':
    main()
