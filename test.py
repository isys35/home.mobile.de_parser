import csv

with open('data.csv', "r", newline="", encoding='utf8') as file:
    reader = csv.reader(file,delimiter=';')
    for row in reader:
        print(row)