import csv, os

for filename in ['TW.csv', 'US.csv', 'hk.csv', 'jp.csv']:
    filepath = os.path.join('StkScreenerResult', filename)
    with open(filepath, encoding='cp950', errors='ignore') as f:
        reader = list(csv.reader(f))
        print(f"{filename} cp950: Header: {reader[0][:4]}, Row 1: {reader[1][:4]}")
