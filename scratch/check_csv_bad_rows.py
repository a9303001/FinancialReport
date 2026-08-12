import os, csv, sys, re

sys.stdout.reconfigure(encoding='utf-8')
res_dir = r'd:\FinancialReport\StkScreenerResult'

# ADR keywords to check in US.csv
adr_tickers = ['AKO.A', 'CIG.C', 'NVO', 'PBR.A', 'PHI', 'TIMB', 'TLK', 'RYAAY', 'DRD', 'GFI', 'HMY', 'UL', 'BTI', 'TSM', 'ASML', 'NVS', 'AZN', 'SHEL', 'TTE', 'SAP']

for csv_name in ['TW.csv', 'US.csv', 'hk.csv', 'jp.csv']:
    path = os.path.join(res_dir, csv_name)
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    
    print(f"=== {csv_name} ({len(rows)} rows) ===")
    bad_rows = []
    for idx, r in enumerate(rows):
        if not r: continue
        code = r[0].strip('"\'' + '\ufeff' + ' ')
        name = r[1] if len(r) > 1 else ''
        pe_str = r[3] if len(r) > 3 else ''
        op_str = r[8] if len(r) > 8 else (r[6] if len(r) > 6 else '')
        
        # Check if code is in adr list
        if code in adr_tickers or 'ADR' in name or 'ADR' in code:
            bad_rows.append((idx+2, code, name, 'G6 (ADR)'))
    
    if bad_rows:
        print(f"Found {len(bad_rows)} potential bad rows in {csv_name}: {bad_rows[:5]}")
    else:
        print(f"No ADR/invalid rows found in {csv_name}.")
