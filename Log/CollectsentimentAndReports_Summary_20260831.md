# 任務執行最終報告 - 2026/08

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `7203 Toyota` | SEC EDGAR / 官網 IR / EDINET | `7203_FY2025_annual_results.md`<br>`7203_FY2026_annual_results.md`<br>`7203_Quarter_2027Q1.md` | ✅ 經檢核已完整涵蓋最新「2年報 + 1季報」（FY2026 20-F 發布於 2026-06-10，FY2027 Q1 決算發布於 2026-08-04），本期無須重複下載 |
| `7203 Toyota` | Reddit, Xueqiu, note.com, Nikkei, Minkabu, Reuters, Seeking Alpha, PTT | `202608_輿情新聞.md` | ✅ 輿情與新聞更新成功（涵蓋日美中台 8 大平台，包含真實原文引述與真實 URL） |

## 2. 失敗或被擋網站與 MCP 替代紀錄
- **來源**: Apify Reddit Actor (`trudax/reddit-scraper-lite`)
  - **原因**: 觸發帳號月度額度上限 (`Monthly usage hard limit exceeded`)
  - **已依 §2 / §2.9 換過的 MCP**: 依 SOP 替代路徑切換至 `Bright Data`（`search_engine` + `scrape_as_markdown`），成功抓取 Reddit r/stocks、r/investing 真實貼文。
- **來源**: Reuters（[https://www.reuters.com/...](https://www.reuters.com/)）
  - **原因**: Bright Data 抓取時遭遇目標伺服器阻擋
  - **已依 §2 換過的 MCP**: 切換至 `Firecrawl`（`firecrawl_scrape`），成功突破並抓取路透專題報導。

## 3. 資料缺失說明
- 本次檢核 Toyota Motor Corp（7203 / TM）財報完整無缺失，最新發布之 FY2027 第一季（2026年4月~6月）決算已於 2026 年 8 月初公佈並收錄。
- 輿情與新聞已覆蓋過去三個月（2026年6月~8月）所有核心平台與事件。

## 4. 異常檔案刪除紀錄
- 無。本次未下載小於 10KB、無公司名稱或 CID 亂碼之異常檔案。

## 5. 本次執行使用的 MCP（強制填寫）
| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| **SEC EDGAR MCP** | `get_cik_by_ticker`<br>`get_company_info`<br>`get_recent_filings` | 查詢 Toyota Motor Corp（TM）CIK 與 2026 年最新 20-F、6-K 申報紀錄，完成 Phase 2 財報檢核。 |
| **Apify MCP** | `call-actor` (`trudax/reddit-scraper-lite`) | 依 §2.9 SOP 呼叫 Reddit 爬蟲 Actor 抓取 TM/Toyota 討論（觸發月度上限後如實記錄）。 |
| **Bright Data MCP** | `search_engine`<br>`scrape_as_markdown` | 搜尋並抓取 Reddit 討論串、雪球（Xueqiu）深度專欄文章及日本/國際財經新聞。 |
| **Firecrawl MCP** | `firecrawl_scrape` | 突破 JS 渲染與防爬阻擋，成功抓取 note.com 深度解析、Reuters 決算報導、Seeking Alpha 分析、Nikkei 與 Minkabu 頁面。 |
