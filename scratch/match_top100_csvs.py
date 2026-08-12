import os, csv, sys, glob, re

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'
main_file = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_file, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
in_table = False
table_rows = []
for line in lines:
    if '## 三、Top 100 排名總覽' in line:
        in_table = True
        continue
    elif in_table and line.startswith('## '):
        in_table = False
    elif in_table and line.startswith('|'):
        if '代號' in line or '排名' in line or ':-' in line:
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) > 2 and parts[1].isdigit():
            table_rows.append(parts[1:])

def get_csv_codes(fname):
    path = os.path.join(res_dir, fname)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        hdr = next(reader)
        return [r[0].strip().replace('"', '') for r in reader if r]

tw_csv = set(get_csv_codes('TW.csv'))
us_csv = set(get_csv_codes('US.csv'))
hk_csv = set(get_csv_codes('hk.csv'))
jp_csv = set(get_csv_codes('jp.csv'))

by_mkt = {'台股': [], '美股': [], '港股': [], '日股': []}

for r in table_rows:
    rank = int(r[0])
    code = r[1]
    name = r[2]
    market = r[3]
    
    in_pool = False
    if market == '台股' and code in tw_csv:
        in_pool = True
    elif market == '美股' and code in us_csv:
        in_pool = True
    elif market == '港股' and (code in hk_csv or code.zfill(5) in hk_csv):
        in_pool = True
    elif market == '日股' and code in jp_csv:
        in_pool = True
        
    by_mkt[market].append((rank, code, name, in_pool))

for mkt, lst in by_mkt.items():
    pool_hits = [x for x in lst if x[3]]
    print(f'=== {mkt} in CSV pool: {len(pool_hits)} / {len(lst)} ===')
    for x in pool_hits:
        print(f'  TOP {x[0]:02d} | {x[1]:6s} | {x[2]}')
