
import csv

with open('example/example0.csv') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)