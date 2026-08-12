import os, glob, re, sys, csv

sys.stdout.reconfigure(encoding='utf-8')
res_dir = r'd:\FinancialReport\StkScreenerResult'
main_file = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_file, 'r', encoding='utf-8') as f:
    main_text = f.read()

# Parse Top 100 table from Section 3
lines = main_text.split('\n')
sec3_lines = []
in_sec3 = False
for line in lines:
    if '## 三、Top 100 排名總覽' in line:
        in_sec3 = True
        continue
    if in_sec3 and line.startswith('## '):
        break
    if in_sec3 and line.startswith('|') and not line.startswith('| 排名') and not line.startswith('| :-'):
        sec3_lines.append(line)

top100_codes = set()
for line in sec3_lines:
    parts = [p.strip() for p in line.split('|')]
    if len(parts) > 2 and parts[1].isdigit():
        top100_codes.add(parts[2])

print(f"Top 100 codes count: {len(top100_codes)}")

csv_files = {
    'TW': 'TW.csv',
    'US': 'US.csv',
    'HK': 'hk.csv',
    'JP': 'jp.csv',
}

for mkt, cname in csv_files.items():
    cpath = os.path.join(res_dir, cname)
    with open(cpath, 'r', encoding='utf-8') as f:
        rows = [line.strip() for line in f if line.strip()]
    header = rows[0]
    data_rows = rows[1:]
    
    in_top = []
    not_in_top = []
    for r in data_rows:
        code = r.split(',')[0].strip('"\'')
        if code in top100_codes:
            in_top.append(code)
        else:
            not_in_top.append((code, r))
    
    print(f"\n=== {mkt} Pool ({cname}) ===")
    print(f"Total CSV rows: {len(data_rows)}")
    print(f"In Top 100: {len(in_top)}")
    print(f"Not in Top 100: {len(not_in_top)}")
    if not_in_top:
        print(f"Candidates not in Top 100 (first 10): {[c[0] for c in not_in_top[:10]]}")
