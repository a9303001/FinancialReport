import csv

for filename in ['TW.csv', 'US.csv', 'hk.csv', 'jp.csv']:
    with open('StkScreenerResult/' + filename, encoding='utf-8-sig') as f:
        reader = list(csv.reader(f))
        print(f"=== {filename} ===")
        print("Header:", reader[0])
        print("Row 1:", reader[1])
