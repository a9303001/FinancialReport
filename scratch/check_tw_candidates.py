import csv, sys, os
sys.stdout.reconfigure(encoding='utf-8')

with open('StkScreenerResult/TW.csv', encoding='utf-8-sig') as f:
    reader = list(csv.reader(f))

header = reader[0]
print("TW.csv Header:", header)

# Print first 20 rows
for i, row in enumerate(reader[1:25]):
    code = row[0]
    name = row[1]
    price = row[2]
    per = row[3]
    rev_growth = row[4]
    debt_ratio = row[12] if len(row) > 12 else ''
    roe25 = row[13] if len(row) > 13 else ''
    print(f"{i+1:2d}. {code} {name}: Price={price}, PE={per}, Debt%={debt_ratio}, ROE25%={roe25}")
