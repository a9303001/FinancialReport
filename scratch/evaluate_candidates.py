import os
import sys
import glob
import re

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

dir_path = r'd:\FinancialReport\StkScreenerResult'
main_file = os.path.join(dir_path, '0.StkScreenerResult_gemini.md')

with open(main_file, 'r', encoding='utf-8') as f:
    main_text = f.read()

# Parse Top 100 stocks from section 3
sec3 = main_text.split('## 三、Top 100 排名總覽')[1].split('## 四、個股詳細')[0]
rows = re.findall(r'^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|', sec3, re.MULTILINE)

top100_map = {}
for r in rows:
    rank = int(r[0].strip())
    code = r[1].strip()
    name = r[2].strip()
    mkt = r[3].strip()
    top100_map[code] = {'rank': rank, 'name': name, 'market': mkt}

print(f'Parsed {len(top100_map)} stocks in Top 100.')

# Check CSV files
csv_files = [
    ('TW', os.path.join(dir_path, 'TW.csv')),
    ('US', os.path.join(dir_path, 'US.csv')),
    ('HK', os.path.join(dir_path, 'hk.csv')),
    ('JP', os.path.join(dir_path, 'jp.csv')),
]

for mkt_name, cpath in csv_files:
    with open(cpath, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    header = lines[0]
    rows = lines[1:]
    
    in_top = []
    new_cand = []
    for line in rows:
        code = line.split(',')[0].strip('"\'' )
        if code in top100_map:
            in_top.append((code, top100_map[code]['name'], top100_map[code]['rank']))
        else:
            new_cand.append(code)
            
    print(f'=== Market {mkt_name} ({len(rows)} rows in CSV) ===')
    print(f'  In Top 100 ({len(in_top)} stocks):')
    for c, n, r in sorted(in_top, key=lambda x: x[2])[:10]:
        print(f'    Rank {r:2d}: {c} {n}')
    print(f'  New candidates ({len(new_cand)} stocks), first 5: {new_cand[:5]}')
