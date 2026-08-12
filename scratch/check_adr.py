import sys, os, glob, re, csv

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'

with open(os.path.join(res_dir, 'US.csv'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    lines = [l.strip() for l in f if l.strip()]

adr_symbols = ['RYAAY', 'DRD', 'GFI', 'HMY', 'UL', 'PHI', 'TIMB', 'TLK', 'TSM', 'BABA', 'NVO', 'AZN', 'ASML', 'SHEL', 'TTE', 'SAP']

header = lines[0]
adr_found = []
for line in lines[1:]:
    reader = csv.reader([line])
    row = next(reader)
    if not row: continue
    code = row[0].strip()
    if code in adr_symbols or '.' in code or 'ADR' in row[1] or 'ADR' in line:
        adr_found.append((code, row[1]))

print(f"ADR/OTC candidates found in US.csv: {len(adr_found)}")
for a in adr_found:
    print(" ", a)
