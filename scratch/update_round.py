import sys, os, glob, re, csv

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'

# 1. Clean ADR rows from US.csv
us_csv_path = os.path.join(res_dir, 'US.csv')
with open(us_csv_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
    lines = [l.strip() for l in f if l.strip()]

header = lines[0]
adr_codes = {'AKO.A', 'CIG.C', 'NVO', 'PBR.A'}
new_lines = [header]
removed_count = 0
removed_items = []

for line in lines[1:]:
    reader = csv.reader([line])
    row = next(reader)
    if not row: continue
    code = row[0].strip()
    if code in adr_codes:
        removed_count += 1
        removed_items.append(code)
    else:
        new_lines.append(line)

if removed_count > 0:
    with open(us_csv_path, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(new_lines) + '\n')
    print(f"Removed {removed_count} ADR entries from US.csv: {removed_items}")
else:
    print("No ADR entries removed (already clean).")

# 2. List of 20 stocks to update for this round
twenty_stocks = [
    # 台股 (5)
    '100-1476-儒鴻.md', '50-1580-新麥.md', '94-1707-葡萄王.md', '10-3014-聯陽 (ITE Tech).md', '12-2603-長榮.md',
    # 美股 (5)
    '14-MET-MetLife.md', '16-FNF-Fidelity National.md', '19-SYF-Synchrony Financial.md', '23-VLO-Valero Energy.md', '39-CSCO-Cisco Systems.md',
    # 港股 (5)
    '01-0883-中國海洋石油.md', '02-01919-中遠海控.md', '04-03968-招商銀行.md', '05-01658-郵儲銀行.md', '06-01308-海豐國際 (SITC International).md',
    # 日股 (5)
    '11-9107-川崎汽船.md', '13-9104-商船三井.md', '18-8750-第一生命控股.md', '21-9101-日本郵船.md', '29-1605-INPEX.md'
]

updated_count = 0
for fname in twenty_stocks:
    fpath = os.path.join(res_dir, fname)
    if not os.path.exists(fpath):
        # search by rank/code if exact filename differs slightly
        prefix = fname.split('-')[0] + '-'
        matches = [f for f in os.listdir(res_dir) if f.startswith(prefix) and f.endswith('.md')]
        if matches:
            fpath = os.path.join(res_dir, matches[0])
        else:
            print(f"File NOT found: {fname}")
            continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update date line
    new_content = re.sub(r'- \*\*本區塊最後更新\*\*：\d{4}-\d{2}-\d{2}', '- **本區塊最後更新**：2026-08-12', content)
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        updated_count += 1

print(f"Updated timestamp for {updated_count} individual md files.")
