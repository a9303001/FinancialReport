# ArrangePublicOpinionMd 執行報告 2026-09-17 00:47

> git 可用，刪除以 `git rm` 執行，可復原。
>
> 執行前工作區有 9 個未提交的 `.md` 變更。

## Section 1 — 統計概覽

| 指標 | 數量 |
| :--- | :--- |
| 掃描公司資料夾數 | 31 |
| 掃描 `.md` 總數 | 244 |
| 判定為輿情檔 | 24 |
| 排除：年報／季報／公告 | 150 |
| 排除：分析報告／系統檔 | 39 |
| 產生／更新的彙整檔數 | 23 |
| 已刪除的原始檔數 | 0 |
| 待人工確認（灰色地帶） | 1 |


## Section 2 — 各公司明細

| 公司 | 年份 | 彙整檔 | 本次併入 | 已刪除 | 備註 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 00546阜豐 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 00883中國海洋石油 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 00941中國移動 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 01426春泉Reit | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 01816中廣核電力 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 02318中國平安 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 03606福耀玻璃 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 1264德麥 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 2245詠勝昌 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 2249湧盛 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 2832台產 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 2881富邦金 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 3445RS | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 4417金洲 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 4979OAT | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 5306桂盟 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 6121新普 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 7203Toyota | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 8433弘帆 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 87001匯賢Reit | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| 9435光通訊 | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| AES-KY | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |
| UHS | 2026 | 2026_PublicOpinion.md | 0 | 0 | — |


## Section 3 — 排除清單

| 公司 | 檔名 | 排除原因 | 命中規則 |
| :--- | :--- | :--- | :--- |
| 00546阜豐 | 00546_2025_annual_report.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 00546阜豐 | 00546_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 00546阜豐 | 00546_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 00546阜豐 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 00546阜豐 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 00883中國海洋石油 | 00883_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 00883中國海洋石油 | 00883_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 00883中國海洋石油 | 00883_Quarter_2026Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 00883中國海洋石油 | 00883_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 00883中國海洋石油 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 00883中國海洋石油 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 00883中國海洋石油 | Orange.md | 分析報告／系統檔 | 黑名單樣式 `(?i)^(readme\|index\|prompt\|agents\|claude\|orange)\.md$` |
| 00941中國移動 | 00941_analysis_report.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 00941中國移動 | 00941_annual_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 00941中國移動 | 00941_annual_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 00941中國移動 | 00941_interim_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「interim」 |
| 00941中國移動 | 00941_interim_2026.md | 年報／季報／公告／財報 | 黑名單關鍵字「interim」 |
| 00941中國移動 | 00941_quarter_2026Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 00941中國移動 | 00941_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 00941中國移動 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 00941中國移動 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 01044恒安國際 | 01044_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 01044恒安國際 | 01044_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 01044恒安國際 | 01044_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 01044恒安國際 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 01044恒安國際 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 01426春泉Reit | 01426_InterimReport_2026.md | 年報／季報／公告／財報 | 黑名單關鍵字「interim」 |
| 01426春泉Reit | 01426_InterimResults_2026.md | 年報／季報／公告／財報 | 黑名單關鍵字「interim」 |
| 01426春泉Reit | 01426_Quarter_2026Q2_OpStats.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 01426春泉Reit | 2025042201223.md | 年報／季報／公告／財報 | 黑名單樣式 `^\d{8,}\.md$` |
| 01426春泉Reit | 20260324以春泉產業信託的基金單位及現金形式向春泉資產管理有限公司支付基本費用及浮動費用.md | 年報／季報／公告／財報 | 黑名單樣式 `^\d{8}(?![_\-\d])` |
| 01426春泉Reit | 2026042200516.md | 年報／季報／公告／財報 | 黑名單樣式 `^\d{8,}\.md$` |
| 01426春泉Reit | 20260428二零二六年第一季度未經審核營運統計.md | 年報／季報／公告／財報 | 黑名單關鍵字「第一季度」 |
| 01426春泉Reit | 202606_InvestmentAnalysis.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 01426春泉Reit | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 01426春泉Reit | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 01426春泉Reit | ltn20131205481.md | 年報／季報／公告／財報 | 黑名單樣式 `^ltn\d+\.md$` |
| 01816中廣核電力 | 01816_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 01816中廣核電力 | 01816_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 01816中廣核電力 | 01816_Quarter_2026H1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 01816中廣核電力 | 01816_Quarter_2026Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 01816中廣核電力 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 01816中廣核電力 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 01866中國心連心化肥 | 01866_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 01866中國心連心化肥 | 01866_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 01866中國心連心化肥 | 01866_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 01866中國心連心化肥 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 01866中國心連心化肥 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 02232晶苑國際 | 02232_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 02232晶苑國際 | 02232_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 02232晶苑國際 | 02232_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 02232晶苑國際 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 02232晶苑國際 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 02318中國平安 | 02318_annual_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 02318中國平安 | 02318_annual_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 02318中國平安 | 02318_interim_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「interim」 |
| 02318中國平安 | 02318_Interim_2026.md | 年報／季報／公告／財報 | 黑名單關鍵字「interim」 |
| 02318中國平安 | 02318_quarter_2026Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 02318中國平安 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 02318中國平安 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 02633雅各臣科研製藥 | 02633_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 02633雅各臣科研製藥 | 02633_AnnualReport_2026.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 02633雅各臣科研製藥 | 02633_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 02633雅各臣科研製藥 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 02633雅各臣科研製藥 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 03606福耀玻璃 | 03606_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 03606福耀玻璃 | 03606_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 03606福耀玻璃 | 03606_Quarter_2026H1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 03606福耀玻璃 | 03606_Quarter_2026Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 03606福耀玻璃 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 03606福耀玻璃 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 03606福耀玻璃 | Orange.md | 分析報告／系統檔 | 黑名單樣式 `(?i)^(readme\|index\|prompt\|agents\|claude\|orange)\.md$` |
| 1264德麥 | 1264_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 1264德麥 | 1264_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 1264德麥 | 1264_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 1264德麥 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 1264德麥 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 2245詠勝昌 | 2022年報2022_2245_20230613F04_20260420_120806.md | 年報／季報／公告／財報 | 黑名單關鍵字「年報」 |
| 2245詠勝昌 | 2023年報2023_2245_20240613F04_20260420_120744.md | 年報／季報／公告／財報 | 黑名單關鍵字「年報」 |
| 2245詠勝昌 | 2024_2245_20250611F04.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| 2245詠勝昌 | 2024年報2024_2245_20250611F04_20260420_120721.md | 年報／季報／公告／財報 | 黑名單關鍵字「年報」 |
| 2245詠勝昌 | 2025_2245_20260616F04.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| 2245詠勝昌 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 2245詠勝昌 | 2245_Quarter_2026H1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 2245詠勝昌 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 2249湧盛 | 2025_2249_20260529F04_20260621_234744.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| 2249湧盛 | 202601_2249_AI1.md | 年報／季報／公告／財報 | 黑名單樣式 `_AI[0-9A-Z](_\|\.)` |
| 2249湧盛 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 2249湧盛 | 2249_2024股東會通知書.md | 年報／季報／公告／財報 | 黑名單關鍵字「股東會」 |
| 2249湧盛 | 2249_annual_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 2249湧盛 | 2249_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 2249湧盛 | 2249_quarter_2026Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 2249湧盛 | 2249_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 2249湧盛 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 2832台產 | 202601_2832_AI2.md | 年報／季報／公告／財報 | 黑名單樣式 `_AI[0-9A-Z](_\|\.)` |
| 2832台產 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 2832台產 | 2832_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 2832台產 | 2832_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 2832台產 | 2832_quarter_2026Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 2832台產 | 2832_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 2832台產 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 2881富邦金 | 2024_2881_20250613F04.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| 2881富邦金 | 2025_2881_20260612F04.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| 2881富邦金 | 202601_2881_AI1.md | 年報／季報／公告／財報 | 黑名單樣式 `_AI[0-9A-Z](_\|\.)` |
| 2881富邦金 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 2881富邦金 | 2881_annual_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 2881富邦金 | 2881_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 2881富邦金 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 3445RS | 2024有価証券報告書－第15期202401020241231.md | 年報／季報／公告／財報 | 黑名單關鍵字「有価証券報告書」 |
| 3445RS | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 3445RS | 3445_annual_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 3445RS | 3445_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 3445RS | 3445_quarter_2026Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 3445RS | 3445_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 3445RS | 688432_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 3445RS | 688432_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 3445RS | 688432_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 3445RS | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 4417金洲 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 4417金洲 | 4417_2024_annual_report.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 4417金洲 | 4417_2025_annual_report.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 4417金洲 | 4417_2026Q1_quarterly_report.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 4417金洲 | 4417_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 4417金洲 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 4979OAT | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 4979OAT | 4979_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 4979OAT | 4979_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 4979OAT | 4979_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 4979OAT | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 5306桂盟 | 2024_5306_20250529FE4.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| 5306桂盟 | 2025_5306_20260529FE4.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| 5306桂盟 | 202601_5306_AI1.md | 年報／季報／公告／財報 | 黑名單樣式 `_AI[0-9A-Z](_\|\.)` |
| 5306桂盟 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 5306桂盟 | 5306_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 5306桂盟 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 6121新普 | 2024_6121_20250529FE4_20260623_014337.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| 6121新普 | 202504_6121_AIA_20260623_015317.md | 年報／季報／公告／財報 | 黑名單樣式 `_AI[0-9A-Z](_\|\.)` |
| 6121新普 | 202504_6121_AIC_20260623_015321.md | 年報／季報／公告／財報 | 黑名單樣式 `_AI[0-9A-Z](_\|\.)` |
| 6121新普 | 2025_6121_20260529FE4_20260623_014508.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| 6121新普 | 202601_6121_AI1_20260623_014115.md | 年報／季報／公告／財報 | 黑名單樣式 `_AI[0-9A-Z](_\|\.)` |
| 6121新普 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 6121新普 | 6121_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 6121新普 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 7203Toyota | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 7203Toyota | 7203_FY2025_annual_results.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 7203Toyota | 7203_FY2026_annual_results.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 7203Toyota | 7203_FY2026_Q3_results.md | 年報／季報／公告／財報 | 黑名單樣式 `(?<![A-Za-z])[Qq][1-4](?![A-Za-z])` |
| 7203Toyota | 7203_Quarter_2027Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 7203Toyota | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 8117中央自動車工業 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 8117中央自動車工業 | 8117_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 8117中央自動車工業 | 8117_AnnualReport_2026.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 8117中央自動車工業 | 8117_Quarter_2027Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 8117中央自動車工業 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 8433弘帆 | 202504_8433_AI1_20260522_011705.md | 年報／季報／公告／財報 | 黑名單樣式 `_AI[0-9A-Z](_\|\.)` |
| 8433弘帆 | 202504_8433_AI3_20260522_011719.md | 年報／季報／公告／財報 | 黑名單樣式 `_AI[0-9A-Z](_\|\.)` |
| 8433弘帆 | 2025_8433_20260618F04.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| 8433弘帆 | 202601_8433_AI1_20260522_011635.md | 年報／季報／公告／財報 | 黑名單樣式 `_AI[0-9A-Z](_\|\.)` |
| 8433弘帆 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 8433弘帆 | 8433_annual_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 8433弘帆 | 8433_annual_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| 8433弘帆 | 8433_quarter_2026Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 8433弘帆 | 8433_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 8433弘帆 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 8433弘帆 | Orange.md | 分析報告／系統檔 | 黑名單樣式 `(?i)^(readme\|index\|prompt\|agents\|claude\|orange)\.md$` |
| 8435鉅邁 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 87001匯賢Reit | 20240415_2023年年報.md | 年報／季報／公告／財報 | 黑名單關鍵字「年報」 |
| 87001匯賢Reit | 20250424_2024年年報.md | 年報／季報／公告／財報 | 黑名單關鍵字「年報」 |
| 87001匯賢Reit | 20250828二零二五年中期報告.md | 年報／季報／公告／財報 | 黑名單關鍵字「中期報告」 |
| 87001匯賢Reit | 20260423_2025年年報.md | 年報／季報／公告／財報 | 黑名單關鍵字「年報」 |
| 87001匯賢Reit | 20260811_2026年中期業績公告.md | 年報／季報／公告／財報 | 黑名單關鍵字「公告」 |
| 87001匯賢Reit | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 87001匯賢Reit | 87001_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 87001匯賢Reit | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| 9435光通訊 | 202406有価証券報告書－第37期(20230401－20240331).md | 年報／季報／公告／財報 | 黑名單關鍵字「有価証券報告書」 |
| 9435光通訊 | 202506有価証券報告書－第38期(20240401－20250331).md | 年報／季報／公告／財報 | 黑名單關鍵字「有価証券報告書」 |
| 9435光通訊 | 20260513_2026年3月期決算短信.md | 年報／季報／公告／財報 | 黑名單關鍵字「決算短信」 |
| 9435光通訊 | 20260513_2026年3月期決算説明資料.md | 年報／季報／公告／財報 | 黑名單關鍵字「決算説明」 |
| 9435光通訊 | 202606有価証券報告書－第39期(20250401－20260331).md | 年報／季報／公告／財報 | 黑名單關鍵字「有価証券報告書」 |
| 9435光通訊 | 20260813_2027年3月期第1四半期決算説明資料.md | 年報／季報／公告／財報 | 黑名單關鍵字「四半期」 |
| 9435光通訊 | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| 9435光通訊 | 2026年3月期決算短信〔IFRS〕(連結)（1500）.md | 年報／季報／公告／財報 | 黑名單關鍵字「決算短信」 |
| 9435光通訊 | 2026年3月期第3四半期決算短信〔IFRS〕(連結)（1500）.md | 年報／季報／公告／財報 | 黑名單關鍵字「四半期」 |
| 9435光通訊 | 9435_quarter_2026Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 9435光通訊 | 9435_Quarter_2027Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| 9435光通訊 | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| AES-KY | 2024_6781_20250528FE6_20260819_231851.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| AES-KY | 2025_6781_20260528FE4_20260819_231952.md | 年報／季報／公告／財報 | 黑名單樣式 `(F04\|FE4\|FI4\|FE6)(_\|\.)` |
| AES-KY | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| AES-KY | 6781_Quarter_2026Q1.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| AES-KY | 6781_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| CF | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| CF | CF_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| CF | CF_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| CF | CF_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| CF | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| CF | orange.md | 分析報告／系統檔 | 黑名單樣式 `(?i)^(readme\|index\|prompt\|agents\|claude\|orange)\.md$` |
| EVTC | 20260627.md | 年報／季報／公告／財報 | 黑名單樣式 `^\d{8,}\.md$` |
| EVTC | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| EVTC | evtc-20241231.md | 年報／季報／公告／財報 | 黑名單樣式 `^[a-z]{2,6}-\d{8}\.md$` |
| EVTC | evtc-20251231.md | 年報／季報／公告／財報 | 黑名單樣式 `^[a-z]{2,6}-\d{8}\.md$` |
| EVTC | evtc-20260331.md | 年報／季報／公告／財報 | 黑名單樣式 `^[a-z]{2,6}-\d{8}\.md$` |
| EVTC | evtc-20260630.md | 年報／季報／公告／財報 | 黑名單樣式 `^[a-z]{2,6}-\d{8}\.md$` |
| EVTC | EVTC_Analysis.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| EVTC | EVTC_AnnualReport_2024.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| EVTC | EVTC_AnnualReport_2025.md | 年報／季報／公告／財報 | 黑名單關鍵字「annual」 |
| EVTC | evtc_eps_reconciliation_analysis20260622.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| EVTC | EVTC_Quarter_2026Q2.md | 年報／季報／公告／財報 | 黑名單關鍵字「quarter」 |
| EVTC | EVTC_stock_drop_analysis20260622.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| EVTC | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| UHS | 202606_Official_IR.md | 年報／季報／公告／財報 | 黑名單關鍵字「official_ir」 |
| UHS | 202607_Official_IR.md | 年報／季報／公告／財報 | 黑名單關鍵字「official_ir」 |
| UHS | 2026_PublicOpinion.md | 本 Skill 的輸出檔（不併入、不刪除） | §3.1-D |
| UHS | 2026Q1-10-Q.md | 年報／季報／公告／財報 | 黑名單關鍵字「10-q」 |
| UHS | hourAnalysisResult.md | 分析報告／系統檔 | 黑名單樣式 `(?i)analysis\|_summary_\|conversion_summary\|_reconciliation_` |
| UHS | UHS_10K_2024-12-31.md | 年報／季報／公告／財報 | 黑名單關鍵字「10k」 |
| UHS | UHS_10K_2025-12-31.md | 年報／季報／公告／財報 | 黑名單關鍵字「10k」 |
| UHS | UHS_10Q_2026-03-31.md | 年報／季報／公告／財報 | 黑名單關鍵字「10q」 |
| UHS | UHS_10Q_2026-06-30.md | 年報／季報／公告／財報 | 黑名單關鍵字「10q」 |


## Section 4 — 人工確認清單

| 公司 | 檔名 | 判定困難的原因 | 建議 |
| :--- | :--- | :--- | :--- |
| EVTC | 2026-claude_EPS預估.md | 前 60 行與中段皆無明確特徵 | 請人工確認後手動歸檔或刪除 |


## Section 5 — 錯誤與跳過

| 公司 | 檔名 | 錯誤／跳過原因 |
| :--- | :--- | :--- |
| 00546阜豐 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 00883中國海洋石油 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 00941中國移動 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 01426春泉Reit | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 01816中廣核電力 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 01816中廣核電力 | 202609_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 02318中國平安 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 03606福耀玻璃 | 202609_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 1264德麥 | 202609_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 2245詠勝昌 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 2249湧盛 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 2832台產 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 2881富邦金 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 3445RS | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 4417金洲 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 4979OAT | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 5306桂盟 | 202609_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 6121新普 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 7203Toyota | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 8433弘帆 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 87001匯賢Reit | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| 9435光通訊 | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| AES-KY | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |
| UHS | 202608_輿情新聞.md | C3 原文內容比對失敗：不刪除 |


## 附註

（無）


## 復原指引

```bash
git checkout HEAD -- "<公司資料夾>/<被刪檔名>"
```
