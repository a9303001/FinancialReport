import os, sys, glob, csv, re

sys.stdout.reconfigure(encoding='utf-8')
res_dir = r'd:\FinancialReport\StkScreenerResult'

# Let's inspect US.csv, TW.csv, hk.csv, jp.csv for potential gate violations
def check_csv_gates(filename, market_name):
    path = os.path.join(res_dir, filename)
    with open(path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        lines = [l.strip() for l in f if l.strip()]
    header = lines[0]
    rows = lines[1:]
    
    print(f"=== Screening {market_name} ({filename}) ===")
    rejections = []
    
    for row_str in rows:
        # handle quotes
        parts = [p.strip().strip('"') for p in row_str.split(',')]
        code = parts[0]
        name = parts[1] if len(parts) > 1 else ''
        
        # Check ADRs in US.csv
        if filename == 'US.csv':
            # Check known ADRs or OTC
            # e.g., TSMC (TSM), BABA ADR, etc.
            pass
        
        # Check PER / PE if present
        pe_val = None
        if len(parts) > 3:
            try:
                pe_val = float(parts[3])
            except ValueError:
                pass
        
        if pe_val is not None:
            if pe_val <= 5.0 or pe_val >= 15.0:
                rejections.append((code, name, f"G2 PE={pe_val} not in (5.0, 15.0)"))
    
    print(f"Total rows: {len(rows)}, Gate 2 Rejections found in CSV: {len(rejections)}")
    for r in rejections[:5]:
        print("  Rejected:", r)

check_csv_gates('TW.csv', '台股')
check_csv_gates('US.csv', '美股')
check_csv_gates('hk.csv', '港股')
check_csv_gates('jp.csv', '日股')
