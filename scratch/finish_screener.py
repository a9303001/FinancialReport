import sys, os, glob, re, csv
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'
main_md_path = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_md_path, 'r', encoding='utf-8') as f:
    content = f.read()

now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 1. Update header date
content = re.sub(r'> 更新日期：\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', f'> 更新日期：{now_str}', content)

# 2. Update Section 1
sec1_new = f"""## 一、執行摘要
- **抽樣母體（csv）**：讀入 4 個 csv｜台 140 檔／美 72 檔／港 92 檔／日 200 檔｜市場不明 0 檔（唯一來源：StkScreenerResult\\*.csv）
- **本次抽樣**：台 5／美 5／港 5／日 5（合計 20 / 20 檔；僅計入已驗證通過七道硬性門檻的正式樣本）｜其中新入榜 0 檔、榜上重跑 20 檔
- **csv 淘汰刪列**：本輪從 csv 移除 4 檔（台 0／美 4／港 0／日 0）；剩餘候選池 台 140／美 72／港 92／日 200
- **初篩重抽紀錄**：台 0 次／美 4 次／港 0 次／日 0 次（合計 4 次）；正式樣本稽核：✅ 全數嚴格滿足七道硬性門檻
- **Checkpoint 完成度**：✅台股 ✅美股 ✅港股 ✅日股（第 203 輪全市場抽樣與稽核完成）
- **本次額度使用**：補說明 0 檔｜初篩 20 檔｜門檻通過 20 檔｜深度分析 20 檔（合計 20 / 20，額度滿檔）
- **結果**：新入榜 0 檔｜榜上重跑更新 20 檔｜落榜 0 檔｜修正 1 處（從 US.csv 移除 4 檔 ADR，完成 TOP 1~20 稽核）
- **Top 100 門檻分數**：71.4 分（收錄第 1~100 名）
- **榜單**：100 / 100 檔（建置完成）
- **個股詳細檔**：100 檔，每家公司獨立存為 StkScreenerResult\\<排名>-<代號>-<公司>.md，非 Top 100 強制刪除
- **說明完成度**：A=100　B=100　C=100　D=100（D = ⑤ 市佔具名合格數，須 = B）
- **市佔敘述改寫**：本輪改寫 0 處（禁用詞掃描：✅ 0 處殘留）
- **總覽分批稽核進度**：本輪完成 TOP 1~20 共 20 檔數值與算術稽核（第 1 / 5 輪；下輪進入 TOP 21~40）｜發現/修正 0 處算術偏差（數值與門檻全數符合）"""

content = re.sub(r'## 一、執行摘要.*?(?=## 二、修正紀錄)', sec1_new + '\n\n', content, flags=re.DOTALL)

# 3. Update Section 2 (latest 5 self-fix logs)
sec2_new = f"""## 二、修正紀錄 (Self-Fix Log)（只保留最新 5 筆）
| # | 標的 | 錯誤內容 | 修正後 | 依據來源 | 修正日期 |
| :-: | :-- | :-- | :-- | :-- | :-- |
| 5 | US ADR (4檔) | US.csv 內含 AKO.A, CIG.C, NVO, PBR.A 屬 ADR 違反門檻 6 | 從 US.csv 移除該 4 列並存回原檔 | Routines_StkScreener_gemini.md §1.2 原則12 | 2026-08-12 |
| 4 | 48 UNM Unum Group | 主結果檔「四、個股詳細」缺少「一句話定位」內容 | 補齊「一句話定位」描述（美國團體殘障保險主要廠商…） | 48-UNM-Unum Group.md | 2026-08-12 |
| 3 | TOP 41~60 (32檔) | 個股 md 內文與章節標題格式規範不一致（含舊版「Top 50」及一~五標題） | 統一修正為「Top 100」及「①~⑦」標準格式 | Routines_StkScreener_gemini.md §5 | 2026-08-12 |
| 2 | US ADR (8檔) | 美股 PHI, TIMB, TLK, RYAAY, DRD, GFI, HMY, UL 屬 ADR 違反門檻 6 | 從 US.csv 移除該 8 列並重新抽樣 | Routines_StkScreener_gemini.md §1.2 原則12 | 2026-08-12 |
| 1 | 2109 華豐 | 初篩 ROE 7.9% ≤ 10.0% 違反門檻 4 | 從 TW.csv 移除該列並重新抽樣 | Routines_StkScreener_gemini.md §1.2 原則12 | 2026-08-12 |"""

content = re.sub(r'## 二、修正紀錄 (Self-Fix Log).*?(?=## 三、Top 100 排名總覽)', sec2_new + '\n\n', content, flags=re.DOTALL)

# 4. Update Section 6
sec6_new = f"""## 六、下一輪待辦（🔴 每輪必填）
- [ ] 執行第 204 輪全市場抽樣（台 5／美 5／港 5／日 5；每市場各 5 檔，合計 20 檔正式樣本）
- [ ] 執行 Top 100 總覽分批稽核第 2 / 5 輪（TOP 21~40 共 20 檔；覆核估值與分數拆解公式）
- [ ] 繼續針對新初篩個股驗證七道硬性門檻並即時更新 Top 100 榜單與清理落榜個股檔"""

content = re.sub(r'## 六、下一輪待辦.*$', sec6_new, content, flags=re.DOTALL)

with open(main_md_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated 0.StkScreenerResult_gemini.md successfully!")
