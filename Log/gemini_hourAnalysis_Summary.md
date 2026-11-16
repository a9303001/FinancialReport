# Rotation Progress — StockAnalysis (Gemini)

| 欄位 | 值 |
|:-----|:---|
| **last_executed_date** | 7 |
| **last_executed_companies** | UHS Universal Health Services |
| **last_executed_time** | 2026-11-16 08:50 |
| **next_date** | 8 |
| **stock_analysis_status** | ✅ |

---

## 本輪執行明細（Date 7：UHS Universal Health Services）

- **輸出檔案**：`d:\FinancialReport\UHS\hourAnalysisResult.md`
- **更新時間戳（第 1 行）**：`2026/11/16 08:50:13 (UTC+8)`
- **驗收實測**：
  - 實測行數：`420` 行（≤ 500 行硬上限）
  - 半形豎線（`|`）數量：`0`（全檔零表格合規）
  - HTML `<table>` 數量：`0`
- **市場與報價基準**：
  - NYSE UHS（11/13 收盤）：`194.07 USD`（市值 `111.89 億美元`；TTM PE `8.12 倍`、Forward PE `8.43 倍`、PB `1.47 倍`）
  - 股數口徑：`5,765.21` 萬股（2026-10-31 期末流通在外四類普通股合計，出自 2026 Q3 10-Q 封面；22 個月較 2024 年底縮減 `11.27%`）
- **本輪重要新發現與修正**：
  1. **納入 11/10 UBS Global Healthcare Conference 最新指引**：CFO 重申 2027 年有 `1.75–2.00 億美元` 跨期 DPP 逆風（稅後每股 `−2.31` 至 `−2.64 USD`），但首度明確提出未認列的佛州 2026／2027 年 DPP 若獲 CMS 核准可部分對沖（2026 待批額 `5,800 萬美元` ＝ 稅後每股 `+0.77 USD`／年，兩年約 `+1.53 USD`），且今年三家問題院虧損（`8,000 萬–1 億美元`）明年可回收顯著比重，Talkspace（10-Q 淨價 `8.20 億美元`）2027 下半年加速貢獻。
  2. **更新 11 月中旬華爾街評級與同業即時估值比較**：11/11 RBC 升目標價 `183 → 207 USD`（Sector Perform）、Mizuho 升 `200 → 225 USD`（Outperform），17 位分析師均價升至 `196.71 USD`；11/10 Zacks 將 2027E EPS 由 `24.25` 下調至 `22.69 USD`（Strong Sell）。另以 yfinance 11/13 收盤補齊 HCA（TTM PE `16.55`／Forward `15.94`）、THC（`8.34`／`14.08`）、ACHC（Forward `18.54`）同業估值對照。
  3. **重算 5 年歷史 PE／殖利率並釐清 GAAP vs Adjusted 口徑**：將 5 年年底 PE（中位數 `10.97 倍`）與殖利率（中位數 `0.52%`）改採未還原除息實際收盤價重算；釐清 FY2025 GAAP EPS `23.10`（含 AI 投資收益）與 Adjusted EPS `21.74` 差異，並完成 OBBBA 衝擊（2032 年稅後每股 `−6.60 USD`／`−26.0%`）與 FY2026E–FY2029E（`22.40 → 21.85 → 23.00 → 23.90 USD`）對照華爾街共識（`22.45 → 23.01 → 25.34 USD`）之專題剖析。
- **工具備援紀錄**：直接讀取本地 `UHS_10Q_2026-09-30.md`、`UHS_10K_2025-12-31.md`、`UHS_10K_2024-12-31.md`、`2026_PublicOpinion.md`（11/9 更新），並以 SEC EDGAR API／MCP（含 10/27 8-K Ex.99.1、11/12 CEO Form 4、10 年 XBRL）、yfinance MCP、Exa 及內建搜尋完成全數交叉驗證。
- **下一輪（Date 8）**：`2832 台產`（台股）
