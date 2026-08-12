import os, csv, sys

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'

def check_us_csv():
    path = os.path.join(res_dir, 'US.csv')
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        hdr = next(reader)
        rows = [r for r in reader if r]
    print(f'US.csv header: {hdr}')
    print('Sample US candidates:')
    for r in rows[:15]:
        code, name = r[0], r[1]
        pe_ttm = r[3] if len(r) > 3 else ''
        om = r[8] if len(r) > 8 else ''
        print(f'  {code:6s} | {name:20s} | PE: {pe_ttm:8s} | OM: {om}')

def check_jp_csv():
    path = os.path.join(res_dir, 'jp.csv')
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        hdr = next(reader)
        rows = [r for r in reader if r]
    print('Sample JP candidates:')
    for r in rows[:15]:
        code, name = r[0].replace('"', ''), r[1].replace('"', '')
        pe_ttm = r[3].replace('"', '') if len(r) > 3 else ''
        om = r[8].replace('"', '') if len(r) > 8 else ''
        print(f'  {code:6s} | {name:20s} | PE: {pe_ttm:8s} | OM: {om}')

check_us_csv()
print()
check_jp_csv()
