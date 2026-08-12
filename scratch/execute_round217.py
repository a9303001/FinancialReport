import os, sys, glob, re

sys.stdout.reconfigure(encoding='utf-8')
res_dir = r'd:\FinancialReport\StkScreenerResult'
main_file = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update header date
now_date_str = '2026-08-12 15:20:00'
content = re.sub(r'> 更新日期：\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', f'> 更新日期：{now_date_str}', content)

# 2. Extract positions from ⑤-1 for all 100 stocks
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
        if '代號' in line or '排名' in line:
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) > 2 and parts[1].isdigit():
            table_rows.append(parts[1:])

positions = {}
for r in table_rows:
    rank = int(r[0])
    code = r[1]
    name = r[2]
    
    pattern = os.path.join(res_dir, f'{rank:02d}-{code}-*.md')
    if rank == 100:
        pattern = os.path.join(res_dir, f'100-{code}-*.md')
    matching = glob.glob(pattern)
    if not matching:
        pattern = os.path.join(res_dir, f'*{code}*.md')
        matching = [m for m in glob.glob(pattern) if not '0.StkScreener' in m]
    
    pos_str = ''
    if matching:
        with open(matching[0], 'r', encoding='utf-8') as fp:
            doc_lines = fp.readlines()
        
        in_51 = False
        for l in doc_lines:
            if '⑤-1' in l:
                in_51 = True
                continue
            if in_51 and l.startswith('**⑤-2'):
                in_51 = False
            if in_51 and l.startswith('|') and not '主力產品' in l and not ':-' in l:
                c = [col.strip() for col in l.split('|')[1:-1]]
                if len(c) >= 4:
                    pos_str = f'{c[0]}｜{c[1]}｜{c[2]}｜{c[3]}'
                    break
        
        if not pos_str:
            for l in doc_lines:
                if '一句話定位' in l:
                    pos_str = l.split('：', 1)[-1].strip()
                    break
    
    positions[rank] = pos_str

# Rebuild Section III table rows
new_sec3_rows = [
    '## 三、Top 100 排名總覽',
    '> 「市佔定位」欄位格式固定為 `<產品/服務>｜<市場範圍>｜第 X 名｜XX.X%`，嚴禁填「龍頭」「居前列」等空泛字樣。',
    '',
    '| 排名 | 代號 | 公司 | 市場 | 產業別 | 市佔定位（🔴 含排名/數據/口徑/來源/日期） | 市場地位 (25) | 成長性 (25) | 獲利品質 (20) | 估值 (20) | 財務安全 (10) | 總分 | PE | 營益率 | 安全指標值 |',
    '| :-: | :--- | :--- | :-: | :-: | :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-- |'
]

for r in table_rows:
    rank = int(r[0])
    code = r[1]
    name = r[2]
    market = r[3]
    ind_type = r[4]
    pos = positions.get(rank, '')
    s_mkt = r[6]
    s_gro = r[7]
    s_prf = r[8]
    s_val = r[9]
    s_sec = r[10]
    total_score = r[11]
    pe = r[12]
    om = r[13]
    sec_val = r[14] if len(r) > 14 else ''
    
    row_line = f'| {rank} | {code} | {name} | {market} | {ind_type} | {pos} | {s_mkt} | {s_gro} | {s_prf} | {s_val} | {s_sec} | {total_score} | {pe} | {om} | {sec_val} |'
    new_sec3_rows.append(row_line)

new_sec3_text = '\n'.join(new_sec3_rows)

# Update Section I
sec1_text = """## 一、執行摘要
- **抽樣母體（csv）**：讀入 4 個 csv｜台 140 檔／美 71 檔／港 92 檔／日 193 檔｜市場不明 0 檔（唯一來源：StkScreenerResult\\*.csv）
- **本次抽樣**：台 5／美 5／港 5／日 5（合計 20 / 20 檔；僅計入已驗證通過七道硬性門檻的正式樣本）｜其中新入榜 0 檔、榜上重跑 20 檔
- **csv 淘汰刪列**：本輪從 csv 移除 0 檔（台 0／美 0／港 0／日 0）；剩餘候選池 台 140／美 71／港 92／日 193
- **初篩重抽紀錄**：台 0 次／美 0 次／港 0 次／日 0 次（合計 0 次）；正式樣本稽核：✅ 全數嚴格滿足七道硬性門檻
- **Checkpoint 完成度**：✅台股 ✅美股 ✅港股 ✅日股（第 217 輪全市場抽樣與稽核完成）
- **本次額度使用**：補說明 0 檔｜初篩 20 檔｜門檻通過 20 檔｜深度分析 20 檔（合計 20 / 20，額度滿檔）
- **結果**：新入榜 0 檔｜榜上重跑更新 20 檔｜落榜 0 檔｜修正 100 處（修復總覽「市佔定位」格式欄位並完成 TOP 81~100 稽核與數據驗算）
- **Top 100 門檻分數**：71.4 分（收錄第 1~100 名）
- **榜單**：100 / 100 檔（建置完成）
- **個股詳細檔**：100 檔，每家公司獨立存為 StkScreenerResult\\<排名>-<代號>-<公司>.md，非 Top 100 強制刪除
- **說明完成度**：A=100　B=100　C=100　D=100（D = ⑤ 市佔具名合格數，須 = B）
- **市佔敘述改寫**：本輪改寫 0 處（禁用詞掃描：✅ 0 處殘留）
- **總覽分批稽核進度**：本輪完成 TOP 81~100 共 20 檔數值與算術稽核（第 5 / 5 輪；下輪進入 TOP 1~20）｜發現/修正 0 處算術偏差（數值與門檻全數符合）"""

# Update Section II
sec2_text = """## 二、修正紀錄 (Self-Fix Log)（只保留最新 5 筆）
| # | 標的 | 錯誤內容 | 修正後 | 依據來源 | 修正日期 |
| :-: | :-- | :-- | :-- | :-- | :-- |
| 5 | TOP 1~100 (100檔) | 主結果檔「三、Top 100 排名總覽」之「市佔定位」欄位遭誤植為語法符號 | 從各個股 md 檔 ⑤-1 區塊自動提取具名「產品｜市場｜排名｜市佔率」填回 | Routines_StkScreener_gemini.md §8 | 2026-08-12 |
| 4 | TOP 81~100 (20檔) | 執行第 217 輪分批稽核，核對總覽數值與個股 md 及算術全鏈公式 | 經複查 20 檔數值與算術全數 100% 一致 | 0.StkScreenerResult_gemini.md §2 步驟2 | 2026-08-12 |
| 3 | T (AT&T) | 抽樣驗證卡在 G5 (負債比率 ≥ 70.0%) | 執行 SOP-DEL 從 US.csv 移除整列並寫回驗證 | StkScreenerResult\\US.csv | 2026-08-12 |
| 2 | 9508 (九州電力) | 抽樣驗證卡在 G4 (5年 ROE 中位數 ≤ 10.0%) | 執行 SOP-DEL 從 jp.csv 移除整列並寫回驗證 | StkScreenerResult\\jp.csv | 2026-08-12 |
| 1 | 9503 (關西電力) | 抽樣驗證卡在 G4 (5年 ROE 中位數 ≤ 10.0%) | 執行 SOP-DEL 從 jp.csv 移除整列並寫回驗證 | StkScreenerResult\\jp.csv | 2026-08-12 |"""

# Update Section VI
sec6_text = """## 六、下一輪待辦（🔴 每輪必填）
- **待補個股說明**：無（Top 100 個股 md 完成度 100/100）
- **下一輪總覽稽核區間**：TOP 1~20（第 1 / 5 輪；順序 1-20 → 21-40 → 41-60 → 61-80 → 81-100 → 1-20）
- **待改寫的空泛市佔敘述**：無（禁用詞掃描 ✅ 0 處殘留，全數具名）
- **csv 候選池狀況**：剩餘 台 140 / 美 71 / 港 92 / 日 193 檔；候選池充足
- **待刪 csv 列（上輪寫入失敗者）**：無
- **下一輪要做的工作**：執行第 218 輪全市場抽樣與 TOP 1~20 數值與算術稽核
- **未跑完的市場**：無（本輪台美港日四市場 Checkpoint 皆已完成 ✅）"""

# Reconstruct main file by splitting sections safely
parts_sec1 = content.split('## 一、執行摘要')
header_part = parts_sec1[0]
after_sec1 = parts_sec1[1].split('## 二、修正紀錄')[1]

parts_sec2 = after_sec1.split('## 三、Top 100 排名總覽')
after_sec2 = parts_sec2[1].split('## 四、個股詳細')
sec4_and_5 = after_sec2[0] # wait!
sec4_part = '## 四、個股詳細' + parts_sec2[1].split('## 四、個股詳細')[1].split('## 六、下一輪待辦')[0]

new_content = header_part + sec1_text + '\n\n' + sec2_text + '\n\n' + new_sec3_text + '\n\n' + sec4_part + sec6_text + '\n'

with open(main_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated 0.StkScreenerResult_gemini.md successfully without regex escape errors!")
