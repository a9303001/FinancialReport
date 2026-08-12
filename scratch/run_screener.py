import sys, os, glob, re, csv

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'
main_md = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_md, 'r', encoding='utf-8') as f:
    content = f.read()

top100_codes = set()
sec3_match = re.search(r'## 三、Top 100 排名總覽.*?\n(\|.*?\n)+', content, re.DOTALL)
if sec3_match:
    lines = [l.strip() for l in sec3_match.group(0).strip().split('\n') if l.startswith('|')]
    for l in lines[2:]:
        cols = [c.strip() for c in l.split('|')[1:-1]]
        if len(cols) >= 2 and cols[0].isdigit():
            top100_codes.add(cols[1])

print(f"Top 100 total codes: {len(top100_codes)}")
print("Top 100 codes list:", sorted(list(top100_codes)))

for fname in ['TW.csv', 'US.csv', 'hk.csv', 'jp.csv']:
    path = os.path.join(res_dir, fname)
    with open(path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    header = lines[0]
    data_lines = lines[1:]
    
    in_top100 = []
    not_in_top100 = []
    for line in data_lines:
        # handle quoted CSV line or simple split
        reader = csv.reader([line])
        row = next(reader)
        if not row: continue
        code = row[0].strip()
        matched = False
        for tcode in top100_codes:
            if code == tcode or code.zfill(5) == tcode.zfill(5) or code.lstrip('0') == tcode.lstrip('0'):
                matched = True
                break
        if matched:
            in_top100.append(code)
        else:
            not_in_top100.append(code)
    print(f"{fname}: Total={len(data_lines)}, In Top100={len(in_top100)}, New Candidates={len(not_in_top100)}")
