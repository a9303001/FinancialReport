# Rotation Progress — StockAnalysis (Gemini)

| 欄位 | 值 |
|:-----|:---|
| **last_executed_date** | 6 |
| **last_executed_companies** | 7203 Toyota（美股 ADR: TM） |
| **last_executed_time** | 2026-11-17 00:21 |
| **next_date** | 7 |
| **stock_analysis_status** | ✅ |

---

## 本輪執行明細（Date 6：7203 Toyota／美股 ADR: TM）

- **輸出檔案**：`d:\FinancialReport\7203Toyota\hourAnalysisResult.md`
- **更新時間戳（第 1 行）**：`2026/11/17 00:21:09 (UTC+8)`
- **驗收實測**：
  - 實測行數：`417` 行（≤ 500 行硬上限）
  - 半形豎線（`|`）數量：`0`（全檔零表格合規）
  - HTML `<table>` 數量：`0`
  - `EXTRA_ANALYSIS` 1–4 題（自駕車計劃與影響、美國關稅影響與稅率、每股日元化、未來 2 年 EPS 預估）：完整覆蓋且六欄位（`答案`／`推導`／`每股化`／`資料來源與日期`／`信心度`／`所以呢`）齊備
- **市場與報價基準（2026-11-16 收盤）**：
  - `7203.T`（東京證交所 Prime）：`3,428 JPY`（單日 `+10 JPY`／`+0.29%`；FY2026 PE `11.61 倍`、官方 Forward PE `11.43 倍`〔共識 `10.95 倍`〕、TTM PE `9.37 倍`、PB `1.08 倍`、殖利率 `2.92%`〔預估 DPS `100 JPY`〕）
  - `TM`（NYSE ADR，1 ADR = 10 股）：`212.43 USD`（換算每股 `3,391.9 JPY`，較東證收盤價折價 `1.05%`）
  - 股數口徑：`11,778.25 百萬股`（2026-09-30 期末流通在外股數，已扣除含 ESOP 信託庫藏股 `2,816.74 百萬股`）
  - 匯率基準：`1 USD = 159.67 JPY`
- **本輪重要校對與更新**：
  1. **更新 2026-11-16 東證收盤行情與重算全檔估值倍數**：以 11/16 收盤價 `3,428 JPY` 取代前版早盤暫時報價，重新計算 PE、Forward PE、TTM PE、PB、殖利率、ADR 折價率（`1.05%`）與 TOB 買回價折價率（`20.51%`）。
  2. **確認 EDINET 第 123 期半期報告書提交狀態**：確認已於 2026-11-12 正式提交東海財務局。
  3. **全檔 Final Rewrite**：統一將貨幣符號與 key-value 結構對齊 SKILL.md §4.2、§4.7 與 §7 規範。

---

- **下一輪（Date 7）**：`UHS Universal Health Services`
