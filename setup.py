import csv
from cs50 import SQL

db = SQL("sqlite:///nwc.db")

with open('fixtures.csv') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    for row in reader:
        print(row)
        if row[1] == 'H':
            loc_id = 1
        else:
            loc_id = 2
        db.execute("INSERT INTO matches (opponent, date, competition, location_id) VALUES (?, ?, ?, ?);", row[2], row[0], row[3], loc_id)
