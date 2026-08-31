# 任務執行最終報告 - 2026/08

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `5306 桂盟` | MOPS / 財報狗 / 桂盟 IR | `2024_5306_20250529FE4.md` (2024 年報), `2025_5306_20260529FE4.md` (2025 年報), `5306_Quarter_2026Q2.md` (2026 Q2 季報) | 現有財報經查核已為最新且完整 |
| `5306 桂盟` | CMoney 爆料同學會、MoneyDJ、經濟日報、工商時報、鉅亨網、PTT、Dcard、雪球、Reddit | `202608_輿情新聞.md` | 過去三個月（2026/06~08）社群輿情與新聞彙整完成 |
| `03606 福耀玻璃` | HKEXnews / 上交所 / 公司官網 | `03606_AnnualReport_2024.md` (2024 年報), `03606_AnnualReport_2025.md` (2025 年報), `03606_Quarter_2026Q1.md` (2026 Q1 季報), `03606_Quarter_2026H1.md` (2026 H1 中期業績公告) | 2026 中期業績公告於 2026-08-18 發布，現有財報已為最新且完整 |
| `03606 福耀玻璃` | 雪球（專欄/社群討論）、東方財富網（藍鯨財經/股吧）、Reddit (r/SinoDiscussion)、鉅亨網、格隆匯、上海證券報 | `202608_輿情新聞.md` | 過去三個月（2026/06~08，著重中報發布後）社群輿情與新聞彙整完成 |
| `01816 中廣核電力` | HKEXnews / 深交所 / 公司官網 | `01816_AnnualReport_2024.md` (2024 年報), `01816_AnnualReport_2025.md` (2025 年報), `01816_Quarter_2026Q1.md` (2026 Q1 季報), `01816_Quarter_2026H1.md` (2026 H1 中期業績公告) | 2026 中期業績公告於 2026-08-25 正式發布，已完整擷取並建檔 |
| `01816 中廣核電力` | 雪球（專欄「排期表裡的確定性」/中報討論）、東方財富網（上網電價機制/董秘問答）、格隆匯、美銀證券研報、Reddit | `202608_輿情新聞.md` | 過去三個月（2026/06~08）社群輿情、電價機制、大行評級與新聞整理完成 |

## 2. 失敗或被擋網站
- **來源**: [股市爆料同學會 (cmoney.tw)](https://www.cmoney.tw)
  - **原因**: 網頁前端 Nuxt SSR 渲染，HTML 內貼文為空陣列。
  - **已依 §2 換過的 MCP**: 依 §2.8 SOP 透過官方 REST API (guest token -> `/api/mach/api/Article/Stocks/5306/AllLatest`) 成功取得 49 篇真實貼文與留言。
- **來源**: [東方財富股吧列表頁 (guba.eastmoney.com/list,003816.html)](https://guba.eastmoney.com/list,003816.html)
  - **原因**: 列表頁採用前端非同步動態載入，直接抓取為空外殼。
  - **已依 §2 換過的 MCP**: 依 §2 通用抓取規則切換為 `firecrawl_search` 與 `firecrawl_scrape` 直接抓取財富號深度文章與董秘問答原文。
- **來源**: [PTT 股市板 (ptt.cc/bbs/Stock)](https://www.ptt.cc/bbs/Stock/) / [Dcard 理財板 (dcard.tw)](https://www.dcard.tw)
  - **原因**: 桂盟與中廣核電力在台灣社群過去三個月無專屬個股討論串。
  - **處理**: 誠實記錄檢索歷程，嚴格依 §5.0 防幻覺規則不造假。
- **來源**: [Reddit (reddit.com)](https://www.reddit.com)
  - **原因**: 內建搜尋與 Firecrawl 不支援 Reddit。
  - **已依 §2 換過的 MCP**: 依 §2.9 SOP 呼叫 Apify `trudax/reddit-scraper-lite` Actor 完成檢索（確認 01816 近三個月無獨立新增討論）。

## 3. 資料缺失說明
- 財報部分：
  - 桂盟最新年報為 2025 年度，最新季報為 2026 Q2 季報；2026 Q3 季報法定公告截止日為 2026 年 11 月中旬。
  - 福耀玻璃 2026 年中期業績公告已於 2026-08-18 刊發，完整版《2026年中期報告》預計於 2026 年 9 月底前刊發。
  - 中廣核電力 2026 年半年度報告及中期業績公告已於 2026-08-25 刊發，已建檔為 `01816_Quarter_2026H1.md`，完整版中期報告將於 9 月底前刊發於披露易。
- 輿情部分：散戶與社群高度聚焦於中廣核電力的「核電機組排期投產進度（惠州1/2號、蒼南1號）」、「市場化電價機制與區域托底政策（廣東、廣西、遼寧紅沿河）」、「A/H股折價與港股通股息率性價比」以及「重資產建設資本開支對自由現金流的消耗」。

## 4. 異常檔案刪除紀錄
- 無（所有檔案皆大於 10KB、包含正確公司名稱與代碼，且無 CID 亂碼）。

## 5. 本次執行使用的 MCP（強制填寫，無則註明「未使用」）
| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| **Firecrawl** (`firecrawl-mcp`) | `firecrawl_search` | 搜尋中廣核電力雪球專欄、東方財富、格隆匯 2026 年 8 月最新貼文與報導 URL |
| **Firecrawl** (`firecrawl-mcp`) | `firecrawl_scrape` | 逐頁爬取雪球「排期表裡的確定性」專欄、中報討論、東方財富財富號文章 Markdown |
| **Apify** (`apify`) | `call-actor` (`trudax/reddit-scraper-lite`) | 於 Reddit 搜尋 CGN Power / 01816 / KMC 鏈條等個股討論 |
| **Apify** (`apify`) | `get-dataset-items` | 檢索 Apify Reddit Scraper 執行後的資料集結果 |
| **Bright Data** (`brightdata`) | `scrape_as_markdown` | 嘗試抓取雪球主頁與智通財經頁面 |
| **PyMuPDF4LLM** (`pymupdf4llm-mcp`) | `convert_pdf_to_markdown` | Convert2md 轉換引擎（本次掃描確認 0 pending） |
