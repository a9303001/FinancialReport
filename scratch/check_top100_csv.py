import sys, os, glob, re, csv

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'
main_md = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_md, 'r', encoding='utf-8') as f:
    content = f.read()

top100_rows = []
sec3_match = re.search(r'## 三、Top 100 排名總覽.*?\n(\|.*?\n)+', content, re.DOTALL)
if sec3_match:
    lines = [l.strip() for l in sec3_match.group(0).strip().split('\n') if l.startswith('|')]
    for l in lines[2:]:
        cols = [c.strip() for c in l.split('|')[1:-1]]
        if len(cols) >= 12 and cols[0].isdigit():
            top100_rows.append(cols)

print(f"Top 100 rows count: {len(top100_rows)}")

# Load all CSVs
csv_maps = {}
for fname in ['TW.csv', 'US.csv', 'hk.csv', 'jp.csv']:
    path = os.path.join(res_dir, fname)
    with open(path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        lines = [l.strip() for l in f if l.strip()]
    csv_maps[fname] = []
    for line in lines[1:]:
        reader = csv.reader([line])
        row = next(reader)
        if row:
            csv_maps[fname].append(row[0].strip().strip('\"').strip('\''))

top100_in_csv = {'TW.csv': [], 'US.csv': [], 'hk.csv': [], 'jp.csv': [], 'None': []}

for r in top100_rows:
    code = r[1]
    mkt = r[3]
    found_csv = None
    for fname, codes in csv_maps.items():
        if any(code == c or code.zfill(5) == c.zfill(5) or code.lstrip('0') == c.lstrip('0') for c in codes):
            found_csv = fname
            break
    if found_csv:
        top100_in_csv[found_csv].append((code, r[2], mkt))
    else:
        top100_in_csv['None'].append((code, r[2], mkt))

for k, v in top100_in_csv.items():
    print(f"{k}: {len(v)} stocks in Top 100")
