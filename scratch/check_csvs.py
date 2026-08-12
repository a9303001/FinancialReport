import os, csv, sys, glob

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'

for fname in ['TW.csv', 'US.csv', 'hk.csv', 'jp.csv']:
    path = os.path.join(res_dir, fname)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        hdr = next(reader)
        codes = [r[0].strip().replace('"', '') for r in reader if r]
    print(f'{fname}: {len(codes)} codes, first 10: {codes[:10]}')
