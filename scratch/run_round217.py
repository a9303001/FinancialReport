import os, sys, glob, csv, re
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'
main_md_path = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_md_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Load Top 100 entries from Section 3
lines = content.splitlines()
top100_list = []
in_table = False

for line in lines:
    if '## 三、Top 100 排名總覽' in line:
        in_table = True
        continue
    elif in_table and line.startswith('## '):
        in_table = False
    elif in_table and line.startswith('|'):
        if '代號' in line:
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) > 2 and parts[1].isdigit():
            top100_list.append({
                'rank': int(parts[1]),
                'code': parts[2],
                'name': parts[3],
                'market': parts[4],
                'type': parts[5],
                'pos': parts[6],
                's_mkt': parts[7],
                's_gro': parts[8],
                's_prf': parts[9],
                's_val': parts[10],
                's_sec': parts[11],
                'score': float(parts[12]),
                'pe': parts[13],
                'opm': parts[14],
                'sec_val': parts[15] if len(parts)>15 else ''
            })

print(f"Loaded {len(top100_list)} Top 100 stocks.")

# Check CSV files
def parse_csv(filename):
    path = os.path.join(res_dir, filename)
    with open(path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        raw_lines = [l.rstrip('\r\n') for l in f if l.strip()]
    header = raw_lines[0]
    rows = raw_lines[1:]
    return header, rows

tw_h, tw_rows = parse_csv('TW.csv')
us_h, us_rows = parse_csv('US.csv')
hk_h, hk_rows = parse_csv('hk.csv')
jp_h, jp_rows = parse_csv('jp.csv')

print(f"CSV Row Counts: TW={len(tw_rows)}, US={len(us_rows)}, HK={len(hk_rows)}, JP={len(jp_rows)}")

# Find stocks in each CSV that are in Top 100
by_market = {}
for item in top100_list:
    by_market.setdefault(item['market'], []).append(item)

print("\nTop 100 Breakdown by Market:")
for m, lst in by_market.items():
    print(f"  {m}: {len(lst)} stocks")
