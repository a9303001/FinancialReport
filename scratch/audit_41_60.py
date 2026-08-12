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

top_41_60 = table_rows[40:60]
print(f"Found {len(top_41_60)} rows for TOP 41~60:")
for r in top_41_60:
    rank, code, name, market, ind_type, pos, s_mkt, s_gro, s_prf, s_val, s_sec, total, pe, om, sec_val = r[:15]
    
    # Check individual md file
    pattern = os.path.join(res_dir, f'{int(rank):02d}-{code}-*.md')
    matching = glob.glob(pattern)
    if not matching:
        print(f"  [WARNING] File missing for rank {rank} {code}")
    else:
        with open(matching[0], 'r', encoding='utf-8') as fp:
            md_text = fp.read()
        # Verify arithmetic in item ⑦
        m = re.search(r'總分驗算\*\*：([\d\.]+)\s*\+\s*([\d\.]+)\s*\+\s*([\d\.]+)\s*\+\s*([\d\.]+)\s*\+\s*([\d\.]+)\s*=\s*\*\*([\d\.]+)\*\*', md_text)
        if m:
            v1, v2, v3, v4, v5, v_tot = [float(x) for x in m.groups()]
            calc_tot = round(v1 + v2 + v3 + v4 + v5, 1)
            if abs(calc_tot - float(total)) > 0.15:
                print(f"  [MISMATCH] Rank {rank} {code} calc {calc_tot} vs table {total}")
            else:
                print(f"  [OK] Rank {rank} {code} {name} ({market}) - score verified: {calc_tot}")
        else:
            print(f"  [NOTICE] Item 7 math pattern not matched in {matching[0]}")
