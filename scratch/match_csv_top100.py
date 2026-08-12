import os, csv, sys, glob, re

sys.stdout.reconfigure(encoding='utf-8')
res_dir = r'd:\FinancialReport\StkScreenerResult'

# Get all tickers in Top 100
top100_files = glob.glob(os.path.join(res_dir, '[0-9]*.md'))
top100_map = {} # code -> filename
for fpath in top100_files:
    fname = os.path.basename(fpath)
    if fname.startswith('0.StkScreenerResult'): continue
    # Format: <rank>-<code>-<company>.md
    m = re.match(r'^(\d+)-([A-Za-z0-9]+)-(.*?)\.md$', fname)
    if m:
        rank = int(m.group(1))
        code = m.group(2)
        company = m.group(3)
        top100_map[code] = (rank, fname, company)

print(f"Total Top 100 tickers parsed: {len(top100_map)}")

for csv_name, market_label in [('TW.csv', 'TW'), ('US.csv', 'US'), ('hk.csv', 'HK'), ('jp.csv', 'JP')]:
    path = os.path.join(res_dir, csv_name)
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        in_top100 = []
        not_in_top100 = []
        for row in reader:
            if not row: continue
            code = row[0].strip('"\'' + '\ufeff' + ' ')
            # match with top100
            matched = False
            for t_code, (rank, fname, comp) in top100_map.items():
                if code == t_code or (code.isdigit() and t_code.isdigit() and int(code) == int(t_code)):
                    in_top100.append((rank, t_code, comp, row[1]))
                    matched = True
                    break
            if not matched:
                not_in_top100.append((code, row[1]))
    
    print(f"\n=== {csv_name} ({market_label}) ===")
    print(f"In Top 100: {len(in_top100)} tickers")
    print(f"Sample In Top 100: {in_top100[:10]}")
    print(f"Not In Top 100: {len(not_in_top100)} tickers")
    print(f"Sample Not In Top 100: {not_in_top100[:10]}")
