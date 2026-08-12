import sys, os, glob, re, csv

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'

def load_csv_rows(fname):
    path = os.path.join(res_dir, fname)
    with open(path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        lines = [l.strip() for l in f if l.strip()]
    header = lines[0]
    data = []
    for line in lines[1:]:
        reader = csv.reader([line])
        row = next(reader)
        if row:
            data.append(row)
    return header, data

for fname in ['TW.csv', 'US.csv', 'hk.csv', 'jp.csv']:
    header, data = load_csv_rows(fname)
    print(f"=== {fname} Header ===")
    print(header)
    print(f"Sample first 3 rows:")
    for r in data[:3]:
        print("  ", r)
