import os
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

dir_path = r'd:\FinancialReport\StkScreenerResult'

csvs = ['TW.csv', 'US.csv', 'hk.csv', 'jp.csv']

for fname in csvs:
    fpath = os.path.join(dir_path, fname)
    with open(fpath, 'r', encoding='utf-8-sig') as f:
        lines = [l.strip() for l in f if l.strip()]
    print(f'=== {fname} ===')
    print('Header:', lines[0])
    for l in lines[1:6]:
        print('  Row:', l)
