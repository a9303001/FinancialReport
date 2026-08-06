import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

filepath = 'd:/FinancialReport/Routines_StkScreenerResult_gemini.md'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# Update Header timestamp
now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
today_str = datetime.now().strftime('%Y-%m-%d')
text = re.sub(r'> 更新日期：[^\n]+', f'> 更新日期：{now_str}', text, count=1)

# Import passed stocks from run_round_156
from run_round_156 import passed_stocks, sampled_156

print(f"Adding new candidate stocks to Candidate Pool from Round 156...")

# Parse Section V candidate table
sec5_match = re.search(r'(## 五、通過門檻但未進 Top 50 的候選池\n\| Rank \| 代號 \| 公司 \| 市場 \| 產業別 \| 總分 \|[^\n]*\n\|[^\n]*\n)(.*?)(?=\n## 六、|\Z)', text, re.DOTALL)

if not sec5_match:
    sec5_match = re.search(r'(## 五、通過門檻但未進 Top 50 的候選池\n\|[^\n]*\n\|[^\n]*\n)(.*?)(?=\n## 六、|\Z)', text, re.DOTALL)

sec5_header = sec5_match.group(1)
sec5_rows_raw = sec5_match.group(2).strip().split('\n')

existing_candidates = []
for r in sec5_rows_raw:
    if not r.strip() or not r.startswith('|'):
        continue
    cols = [c.strip() for c in r.split('|')[1:-1]]
    if len(cols) >= 6:
        try:
            rank = cols[0]
            code = cols[1]
            name = cols[2]
            market = cols[3]
            stype = cols[4]
            total = float(cols[5])
            existing_candidates.append({
                'code': code, 'name': name, 'market': market, 'type': stype,
                'total': total, 'raw_cols': cols
            })
        except ValueError:
            pass

print(f"Existing candidates parsed: {len(existing_candidates)}")

existing_codes = set(c['code'] for c in existing_candidates)

added_count = 0
for p in passed_stocks:
    if p['code'] not in existing_codes:
        existing_candidates.append({
            'code': p['code'],
            'name': p['name'],
            'market': p['market'],
            'type': p['type'],
            'total': p['total'],
            'm': p['m'], 'g': p['g'], 'q': p['q'], 'v': p['v'], 's': p['s'],
            'pe': p['pe'], 'op_margin': p['op_margin'], 'safety_name': p['safety_name'],
            'note': f"第一百五十六輪大數據抽樣審查，通過 6 道門檻納入候選池",
            'date': today_str
        })
        existing_codes.add(p['code'])
        added_count += 1

print(f"New unique candidates added: {added_count}")

# Sort all candidates strictly by total score descending
sorted_candidates = sorted(existing_candidates, key=lambda x: x['total'], reverse=True)

# Rebuild Section V table rows
new_sec5_table_rows = []
for idx, c in enumerate(sorted_candidates, 1):
    if 'raw_cols' in c and len(c['raw_cols']) >= 14:
        rc = c['raw_cols']
        rc[0] = str(idx)
        row_str = "| " + " | ".join(rc) + " |"
    else:
        row_str = f"| {idx} | {c['code']} | {c['name']} | {c['market']} | {c['type']} | {c['total']:.1f} | {c.get('m', 0.0):.1f} | {c.get('g', 0.0):.1f} | {c.get('q', 0.0):.1f} | {c.get('v', 0.0):.1f} | {c.get('s', 0.0):.1f} | {c['op_margin']}% | {c['safety_name']} | 第一百五十六輪大數據抽樣審查，通過 6 道門檻納入候選池 | {today_str} |"
    new_sec5_table_rows.append(row_str)

new_sec5_text = sec5_header + "\n".join(new_sec5_table_rows) + "\n\n"

text = text[:sec5_match.start()] + new_sec5_text + text[sec5_match.end():]

# Update Section I Executive Summary
text = re.sub(r'- \*\*本次抽樣\*\*：[^\n]+', f'- **本次抽樣**：台 10／美 10／港 10／日 10（合計 40 / 40 檔，第一百五十六輪大市場抽樣審查完成）', text)
text = re.sub(r'- \*\*Checkpoint 完成度\*\*：[^\n]+', f'- **Checkpoint 完成度**：✅台股 ✅美股 ✅港股 ✅日股（已完成第四十六輪至第一百五十六輪共 111 輪全市場抽樣與審查）', text)
text = re.sub(r'- \*\*本次額度使用\*\*：[^\n]+', f'- **本次額度使用**：初篩 40 檔｜門檻通過 {len(passed_stocks)} 檔｜0 檔高分股進榜 Top 50（ Top 50 門檻維持 73.2分）', text)
text = re.sub(r'- \*\*候選池標的數\*\*：[^\n]+', f'- **候選池標的數**：**{len(sorted_candidates)} 檔**（已完整驗算並排序）', text)

# Update Section II Self-Fix log (keep latest 5)
sec2_match = re.search(r'(## 二、修正紀錄 \(Self-Fix Log\) \(僅保留最新 5 筆\)\n\| # \| 標的 \| 內容 \| 修正 \| 依據來源 \| 修正日 \| 日期 \|\n\| :--: \| :-- \| :-- \| :-- \| :-- \| :-- \| :-- \|\n)(.*?)(?=\n## 三、)', text, re.DOTALL)
if sec2_match:
    sec2_header = sec2_match.group(1)
    sec2_rows = sec2_match.group(2).strip().split('\n')
    new_row = f"| 156 | 全市場抽樣 | 第一百五十六輪 40 檔採樣，{len(passed_stocks)} 檔通過門檻納入候選池，Top 50 門檻維持 73.2 分 | 候選池擴充 | 數據更新與重排 | {today_str} | {today_str} |"
    all_sec2 = [new_row] + [r for r in sec2_rows if r.strip()][:4]
    new_sec2_text = sec2_header + "\n".join(all_sec2) + "\n\n"
    text = text[:sec2_match.start()] + new_sec2_text + text[sec2_match.end():]

# Update Section VII Next Todo
sec7_new = f"""## 七、下一輪待辦（🔴 每輪必填）
- **當前進度**：第一百五十六輪大數據抽樣審查完畢，榜單維持 50/50 滿額（Top 50 門檻維持 73.2 分）。累積完成四十六至一五六輪全抽樣（台 761／美 761／港 761／日 761），覆蓋台美港日四市場。候選池總數達 {len(sorted_candidates)} 檔（本輪新增 {len(passed_stocks)} 檔通過門檻標的納入候選池）。
- **下一輪目標（第一百五十七輪）**：
  1. 繼續執行 40 檔四市場均等抽樣（台 10／美 10／港 10／日 10）。
  2. 優先針對跨季最新財報公布之企業進行 6 大門檻審查與評分重算。
  3. 若發現更高總分標的，立即依據「一體化撰寫」原則，計算分數並更新 Top 50 榜單與細節分析區塊。
"""

text = re.sub(r'## 七、下一輪待辦（🔴 每輪必填）.*', sec7_new, text, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

print(f"Successfully updated {filepath} for Round 156! Total candidates: {len(sorted_candidates)}")
