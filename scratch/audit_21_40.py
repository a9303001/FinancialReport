import re, glob, os

with open('StkScreenerResult/0.StkScreenerResult_gemini.md', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
table_lines = []
in_table = False
for l in lines:
    if '## 三、Top 100 排名總覽' in l:
        in_table = True
        continue
    if in_table and l.startswith('## '):
        break
    if in_table and l.strip().startswith('|'):
        table_lines.append(l.strip())

parsed = []
for l in table_lines[2:]:
    parts = [p.strip() for p in l.split('|')[1:-1]]
    if len(parts) >= 12:
        try:
            rank = int(parts[0])
            code = parts[1]
            name = parts[2]
            market = parts[3]
            mkt_pos = float(parts[6])
            growth = float(parts[7])
            profit = float(parts[8])
            val = float(parts[9])
            safety = float(parts[10])
            total = float(parts[11])
            parsed.append({
                'rank': rank, 'code': code, 'name': name, 'market': market,
                'mkt_pos': mkt_pos, 'growth': growth, 'profit': profit,
                'val': val, 'safety': safety, 'total': total,
                'raw_line': l
            })
        except ValueError:
            pass

audited_errors = []
print(f"Total parsed in table: {len(parsed)}")
for p in parsed:
    if 21 <= p['rank'] <= 40:
        calc_total = round(p['mkt_pos'] + p['growth'] + p['profit'] + p['val'] + p['safety'], 1)
        if abs(calc_total - p['total']) > 0.05:
            audited_errors.append(f"Rank {p['rank']} {p['code']}: Total in table {p['total']} != sum {calc_total}")
        
        pattern = f"StkScreenerResult/{p['rank']:02d}-{p['code']}*.md"
        matching = glob.glob(pattern)
        if not matching:
            pattern = f"StkScreenerResult/{p['rank']}-{p['code']}*.md"
            matching = glob.glob(pattern)
        
        if not matching:
            audited_errors.append(f"Rank {p['rank']} {p['code']}: file not found")
        else:
            with open(matching[0], encoding='utf-8') as f_md:
                md_text = f_md.read()
            m_score = re.search(r'總分\s*([\d\.]+)', md_text)
            if m_score:
                md_score = float(m_score.group(1))
                if abs(md_score - p['total']) > 0.05:
                    audited_errors.append(f"Rank {p['rank']} {p['code']}: table score {p['total']} != md score {md_score}")

print("Audit results for TOP 21~40:")
if not audited_errors:
    print("ALL TOP 21~40 PASSED PERFECTLY!")
else:
    for e in audited_errors:
        print(" -", e)
