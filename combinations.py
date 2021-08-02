import csv

def compute():
    with open('example/example0.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row['origin'])