import os, csv, sys

sys.stdout.reconfigure(encoding='utf-8')
res_dir = r'd:\FinancialReport\StkScreenerResult'

tw_path = os.path.join(res_dir, 'TW.csv')
us_path = os.path.join(res_dir, 'US.csv')
hk_path = os.path.join(res_dir, 'hk.csv')
jp_path = os.path.join(res_dir, 'jp.csv')

def find_ticker(csv_path, code):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row: continue
            raw_code = row[0].strip('"\'' + '\ufeff' + ' ')
            if raw_code == code or (raw_code.isdigit() and code.isdigit() and int(raw_code) == int(code)):
                return row
    return None

print('=== TW.csv ===')
for c in ['2072', '3014', '2603', '6605', '2752']:
    print(c, find_ticker(tw_path, c) is not None)

print('=== US.csv ===')
for c in ['MET', 'FNF', 'SYF', 'VLO', 'DVN', 'CPB', 'INGR', 'WEN', 'VZ', 'ARLP']:
    print(c, find_ticker(us_path, c) is not None)

print('=== hk.csv ===')
for c in ['00883', '01919', '03968', '01658', '01308', '00151', '01497', '01837', '09985']:
    print(c, find_ticker(hk_path, c) is not None)

print('=== jp.csv ===')
for c in ['9107', '9104', '8750', '3635', '9101', '6626', '6643', '6750', '6912']:
    print(c, find_ticker(jp_path, c) is not None)
