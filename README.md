# Flight combinations for between two airports
For a given route generate all combinations printed in JSON format and sorted by the total price

## Output

JSON fields (copied from task desription ;-)):

 Field          | Description                                                   |
|----------------|---------------------------------------------------------------|
| `flights`      | A list of flights in the trip according to the input dataset. |
| `origin`       | Origin airport of the trip.                                   |
| `destination`  | The final destination of the trip.                            |
| `bags_allowed` | The number of allowed bags for the trip.                      |
| `bags_count`   | The searched number of bags.                                  |
| `total_price`  | The total price for the trip.                                 |
| `travel_time`  | The total travel time. In case of return flight, it does not include stay at the destination.                                        |



## Usage

```
python main.py [-h] [--return RETURN] [--bags BAGS] data_source origin destination
```

positional arguments:

    data_source      Flight data source (csv file, see examples in folder example)
    origin           Origin airport of the trip, string
    destination      Destination airport of the trip, string

optional arguments:

    -h, --help       show this help message and exit
    --return RETURN  Tell whether return flights should be searched, bool, default False
    --bags BAGS      Number of bags allowed, integer, default 0

### Example of usage
Command
```
python main.py example/example2.csv GXV IUQ --bags=2 --return=True
```
will search for return flights between GXV and IUQ with 2 bags at the 
file example/example2.csv.

## Restrictions
- If the flght is not direct, the layover time is between 1 and 6 hours.
- The airports in the route are not repeated, i.e. A -> B -> A -> C is not valid.
- The departure time of the return flight is after the arrival time to destination.