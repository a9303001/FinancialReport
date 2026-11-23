# 任務執行最終報告 - 2026/11/23（2249 湧盛）

- **執行日**：2026-11-23（使用者手動指定 → 2249 湧盛；輪替表第 12 日公司）
- **公司資料夾**：`2249湧盛/`
- **備註**：同日 `collectStk_Summary_20261123.md` 已為 87001 匯賢Reit 使用，本檔另以 `_2249` 區分，避免覆蓋。

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| 2249 湧盛 | 本機盤點 | 年報 FY2024（`2249_AnnualReport_2024.md`）、FY2025（`2249_annual_2025.md`、`2025_2249_20260529F04_…md`） | ✅ 2 份年報已齊，跳過 |
| 2249 湧盛 | TWSE 電子書（`firecrawl_scrape` stealth） | 確認 `202603_2249_AI1.pdf`（1,189,385 bytes，115/11/13 15:56 上傳）已存在 | ❌ PDF 本體無法落地（見 §2），本機最新季報仍為 2026Q2 |
| 2249 湧盛 | MoneyDJ（MOPS 轉載）、財訊快報、CMoney API、yfinance、HiStock、財報狗／nStock／領富 AI、鉅亨、Yahoo、經濟日報、工商時報、PTT、Dcard/Mobile01 | `2249湧盛/202611_輿情新聞.md`（新建，增量 11/12~11/23） | ✅ Q3 完整損益表已由 MOPS 轉載取得 |

**本期重點**（換算基準：已發行 31,679,690 股）：
- 🟢 **Q3 單季轉強**：營收 4.09 億元（約每股 12.91 元，年增 6.0%）、毛利率 24.16%（今年單季最高，H1 為 22.34%）、營業利益 5,224 萬元（約每股 1.65 元，年增 17.0%）、單季 EPS 1.64 元（年增 10.8%、季增約 23%）。
- 🔴 **前三季本業衰退**：營收 15.73 億元（約每股 49.66 元，年減 14.3%）、營業利益 2.23 億元（約每股 7.03 元，**年減 26.8%**）；稅後 1.83 億元（約每股 5.76 元）只年減 3.8%，是因去年匯損 5,827 萬元今年轉為業外利益 1,232 萬元（差額約每股 2.23 元）。
- 🟢 **財務體質**：9/30 負債比率 27.7%（Q2 末 33.2%）；10/20 現增 2.37 億元（約每股 7.49 元）尚未計入。
- 🔴 **股價**：11/13 盤中 +7.1% 至 60.2 元後連跌，11/20 −6.9% 至 52.8 元（查無重訊），11/23 台股大跌日盤中最低 49.6 元；較承銷價 66 元低約 20%，PE 5.86 倍、PB 0.98 倍、殖利率 5.68%（114 年度現金股利 3.0 元，已由 Q2 財報附註證實）。
- ⚠️ **Q4 疑慮**：財報狗市場預估 2026 EPS 8.45 元（稅後 2.68 億元）→ Q4 需賺 0.85 億元，較 Q3 多 85%；但 10 月營收僅 0.74 億元（年減 68.6%），預估明顯偏樂觀。關鍵驗證點：**11 月營收（12/10 前公布）**能否回補「遞延至 11 月的約 5,000 萬元」。
- 輿情：CMoney 由 11/10~11 的「騙子公司」憤怒轉為「財報不差但資金不在這、只能買便宜價」的冷淡偏多；法人幾乎不參與（外資每日 ±15 張以內、投信 0）。

## 2. 失敗或被擋網站
- **來源**：[TWSE 電子書 PDF](https://doc.twse.com.tw/pdf/202603_2249_AI1_20261123_114256.pdf)｜**原因**：`curl` 回 947 bytes「安全性考量」封鎖頁（依 IP 封鎖）｜**已試過**：`curl`（帶 UA）、`mopsov.twse.com.tw/nas/ifrs/2026/…` 與 `FileDownLoad` 路徑（帶 cookie，皆封鎖頁）、`firecrawl_scrape`（`parsers: pdf`，2 次 60 秒逾時）、Bright Data `scrape_as_markdown`（2 次 45 秒逾時）。
  - **下次補抓**：檔名 `202603_2249_AI1.pdf`（1,189,385 bytes）→ 存為 `2249湧盛/2249_Quarter_2026Q3.pdf`；先用 `firecrawl_scrape` 跑 `t57sb01?co_id=2249&colorchg=1&kind=A&step=9&filename=202603_2249_AI1.pdf`（stealth、html）取得新的時間戳下載網址再 `curl`。
- **來源**：[湧盛官網 財務報告書](https://www.young-shine.com.tw/financialreport.html)｜**原因**：只上架到 114 年第四季，無 2026 季報｜**已試過**：`curl`。
- **來源**：[ToAlpha 重訊頁](https://toalpha.tw/stock/2249/material)｜**原因**：Cloudflare「Just a moment」｜**已試過**：`curl` → 改用 Exa 索引取得。
- **來源**：Firecrawl `firecrawl_search`（Dcard、Mobile01、新聞搜尋）｜**原因**：執行中回「Insufficient credits」｜**已試過**：改 Exa `web_search_exa`、`WebSearch`。

## 3. 資料缺失說明
- **2026Q3 季報 PDF 未下載**：已於 11/13 上傳 TWSE，但本環境 IP 被 TWSE 封鎖、MCP 解析逾時，官網未上架季報。Q3 損益表全表（單季＋累計＋去年同期）已由 MoneyDJ 的 MOPS 轉載取得；**資產負債表只有總資產／總負債／權益三個數字，現金流量表、附註（客戶集中、產品別、借款）缺**。
- 鉅亨關鍵字 API 至 11/23 仍未收錄 11/13 的 Q3 重訊（資料源落後）。
- 冷門新上櫃股：PTT、Dcard、Mobile01、經濟日報、工商時報 11/12 後皆無新文。

## 4. 異常檔案刪除紀錄
- `2249湧盛/2249_Quarter_2026Q3.pdf`（947 bytes，內容為 TWSE「安全性考量」HTML 封鎖頁，< 10KB）→ 已刪除。

## 5. MCP 預檢與使用紀錄
- **預檢結果**：可用：Firecrawl、Bright Data、Exa、Playwright、yfinance、curl｜未預檢：Apify（本輪未使用）
- **執行中帳號級錯誤**：Firecrawl 在 2 次 PDF 解析逾時後回「Insufficient credits for this connected-app request…allowance resets at 2026-11-23T14:59Z」→ 依 §3.0.2 本輪停用。
- **使用者待辦**：Firecrawl 每日 MCP 額度約 11 小時後重置；如需當天補抓 Q3 PDF 或 Dcard/Mobile01，請到 https://www.firecrawl.dev/billing 加值。

| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape` | 預檢；TWSE 電子書清單與下載頁（成功）；Q3 PDF 解析（逾時 ×2） |
| Firecrawl | `firecrawl_search` | Dcard／Mobile01／新聞（額度用盡失敗） |
| Bright Data | `scrape_as_markdown` | 預檢；Q3 PDF（逾時 ×2） |
| Exa | `web_search_exa` | 預檢；Q3 新聞（MoneyDJ、財訊、nStock、財報狗、鉅亨、工商時報索引） |
| Playwright | `browser_navigate` | 預檢 |
| yfinance | `get_historical_stock_prices` | `2249.TWO` 1 個月日線 |

## 6. Phase 4 Convert2md
- 本次無新 PDF 落地，略過 `Convert2md`。

## 7. Skill 維護
- §4.2 TWSE 電子書列：新增「不要用 Firecrawl `parsers: pdf`／Bright Data 直接解析 `doc.twse.com.tw/pdf/*.pdf`（逾時且耗盡 Firecrawl 額度），改用 MoneyDJ MOPS 轉載當損益表來源」。
- §4.2 MoneyDJ 列：新增財報日兩篇 MOPS 轉載（重訊＋完整綜合損益表）的用法；鉅亨索引落後 MoneyDJ。
- §4.2 ToAlpha 列：新增重訊頁 `toalpha.tw/stock/{代號}/material` 被 Cloudflare 擋，改用 Exa 索引。
- §7.3 台股官網 IR：新增湧盛 2249 `young-shine.com.tw/financialreport.html`（只有半年報與年報）。
- `.claude/skills/collectStk/SKILL.md` 與 `.agents/skills/collectStk/SKILL.md` 已用 `diff` 確認相同。
