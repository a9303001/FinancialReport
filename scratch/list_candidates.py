import sys, os, glob, re, csv

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'
main_md = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_md, 'r', encoding='utf-8') as f:
    content = f.read()

top100_map = {}
sec3_match = re.search(r'## 三、Top 100 排名總覽.*?\n(\|.*?\n)+', content, re.DOTALL)
if sec3_match:
    lines = [l.strip() for l in sec3_match.group(0).strip().split('\n') if l.startswith('|')]
    for l in lines[2:]:
        cols = [c.strip() for c in l.split('|')[1:-1]]
        if len(cols) >= 12 and cols[0].isdigit():
            rank = cols[0]
            code = cols[1]
            name = cols[2]
            top100_map[code] = (rank, name)
            top100_map[code.zfill(5)] = (rank, name)
            top100_map[code.lstrip('0')] = (rank, name)

for fname in ['TW.csv', 'US.csv', 'hk.csv', 'jp.csv']:
    path = os.path.join(res_dir, fname)
    with open(path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        lines = [l.strip() for l in f if l.strip()]
    print(f"=== {fname} Candidates list (first 15) ===")
    for line in lines[1:16]:
        reader = csv.reader([line])
        row = next(reader)
        if not row: continue
        code = row[0].strip().strip('\"').strip('\'')
        name = row[1].strip().strip('\"').strip('\'') if len(row)>1 else ''
        status = f"In Top100 (Rank {top100_map[code][0]})" if code in top100_map else "NEW"
        print(f"  [{code}] {name} -> {status}")
