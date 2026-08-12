import csv, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('StkScreenerResult/hk.csv', encoding='utf-8-sig') as f:
    reader = list(csv.reader(f))

print("hk.csv Header:", reader[0])
for i, row in enumerate(reader[1:30]):
    code = row[0]
    name = row[1]
    price = row[2]
    pe_ttm = row[3]
    ind = row[5] if len(row) > 5 else ''
    div = row[6] if len(row) > 6 else ''
    opm = row[8] if len(row) > 8 else ''
    print(f"{i+1:2d}. {code} {name}: Price={price}, PE={pe_ttm}, Industry={ind}, OPM={opm}")
