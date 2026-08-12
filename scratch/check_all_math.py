import os, sys, glob, re

sys.stdout.reconfigure(encoding='utf-8')
res_dir = r'd:\FinancialReport\StkScreenerResult'
main_file = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_file, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
table_rows = []
in_table = False
for line in lines:
    if '## 三、Top 100 排名總覽' in line:
        in_table = True
        continue
    elif in_table and line.startswith('## '):
        in_table = False
    elif in_table and line.startswith('|'):
        if '代號' in line or '排名' in line or ':-' in line:
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) > 2 and parts[1].isdigit():
            table_rows.append(parts[1:])

print(f"Checking all {len(table_rows)} stocks...")
mismatches = []
for r in table_rows:
    rank, code, name, market, ind_type, pos, s_mkt, s_gro, s_prf, s_val, s_sec, total = r[:12]
    rank_int = int(rank)
    pattern = os.path.join(res_dir, f'{rank_int:02d}-{code}-*.md')
    if rank_int == 100:
        pattern = os.path.join(res_dir, f'100-{code}-*.md')
    matching = glob.glob(pattern)
    if not matching:
        pattern = os.path.join(res_dir, f'*{code}*.md')
        matching = [m for m in glob.glob(pattern) if not '0.StkScreener' in m]
    
    if matching:
        with open(matching[0], 'r', encoding='utf-8') as fp:
            md_text = fp.read()
        
        m_dim = re.search(r'市場地位\s*([\d\.]+).*?成長性\s*([\d\.]+).*?獲利品質\s*([\d\.]+).*?估值\s*([\d\.]+).*?財務安全\s*([\d\.]+)', md_text)
        m_calc = re.search(r'總分驗算\*\*：([\d\.]+)\s*\+\s*([\d\.]+)\s*\+\s*([\d\.]+)\s*\+\s*([\d\.]+)\s*\+\s*([\d\.]+)\s*=\s*\*\*([\d\.]+)\*\*', md_text)
        
        if m_dim and m_calc:
            d1, d2, d3, d4, d5 = [float(x) for x in m_dim.groups()]
            c1, c2, c3, c4, c5, c_tot = [float(x) for x in m_calc.groups()]
            
            dim_sum = round(d1 + d2 + d3 + d4 + d5, 1)
            calc_sum = round(c1 + c2 + c3 + c4 + c5, 1)
            tbl_tot = float(total)
            
            if abs(dim_sum - tbl_tot) > 0.15 or abs(calc_sum - tbl_tot) > 0.15 or (d1,d2,d3,d4,d5) != (c1,c2,c3,c4,c5):
                mismatches.append((rank, code, name, (d1,d2,d3,d4,d5), (c1,c2,c3,c4,c5), tbl_tot, matching[0]))

print(f"Found {len(mismatches)} mismatches:")
for m in mismatches:
    print(m)
