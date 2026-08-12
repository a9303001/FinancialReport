import csv, sys, os, glob, re
sys.stdout.reconfigure(encoding='utf-8')

# Load Top 100 list from 0.StkScreenerResult_gemini.md
with open('StkScreenerResult/0.StkScreenerResult_gemini.md', encoding='utf-8') as f:
    main_text = f.read()

top100_list = []
in_table = False
for l in main_text.splitlines():
    if '## 三、Top 100 排名總覽' in l:
        in_table = True
        continue
    if in_table and l.startswith('## '):
        break
    if in_table and l.strip().startswith('|'):
        parts = [p.strip() for p in l.split('|')[1:-1]]
        if parts[0].isdigit():
            top100_list.append({
                'rank': int(parts[0]),
                'code': parts[1],
                'name': parts[2],
                'market': parts[3],
                'industry': parts[4],
                'total': float(parts[11])
            })

top100_codes = {item['code']: item for item in top100_list}
print(f"Top 100 list count: {len(top100_list)}")

# Read CSV files
def get_csv_rows(filename):
    filepath = os.path.join('StkScreenerResult', filename)
    with open(filepath, encoding='utf-8-sig') as f:
        reader = list(csv.reader(f))
    return reader[0], reader[1:]

tw_header, tw_rows = get_csv_rows('TW.csv')
us_header, us_rows = get_csv_rows('US.csv')
hk_header, hk_rows = get_csv_rows('hk.csv')
jp_header, jp_rows = get_csv_rows('jp.csv')

print(f"TW.csv: {len(tw_rows)} rows")
print(f"US.csv: {len(us_rows)} rows")
print(f"hk.csv: {len(hk_rows)} rows")
print(f"jp.csv: {len(jp_rows)} rows")
