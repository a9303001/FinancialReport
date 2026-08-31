# 任務執行最終報告 - 2026/08/31

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| 7203 Toyota | SEC EDGAR / 官網 IR / EDINET | 7203_FY2025_annual_results.md<br>7203_FY2026_annual_results.md<br>7203_Quarter_2027Q1.md | ✅ 經檢核已完整涵蓋最新「2年報 + 1季報」（FY2026 20-F 發布於 2026-06-10，FY2027 Q1 決算發布於 2026-08-04），本期無須重複下載 |
| 7203 Toyota | Reddit, Xueqiu, note.com, Nikkei, Minkabu, Reuters, Seeking Alpha, PTT | 202608_輿情新聞.md | ✅ 輿情與新聞更新成功（涵蓋日美中台 8 大平台，包含真實原文引述與真實 URL） |
| UHS Universal Health Services | SEC EDGAR / 官網 IR | UHS_10K_2024-12-31.md<br>UHS_10K_2025-12-31.md<br>UHS_10Q_2026-06-30.md | ✅ 經檢核已完整涵蓋最新「2年報 + 1季報」（2024 10-K, 2025 10-K, 2026 Q2 10-Q 申報於 2026-08-07），本期無須重複下載 |
| UHS Universal Health Services | Reddit r/ValueInvesting, S&P Global Ratings, PR Newswire, Becker's Hospital Review / Behavioral Health, Xueqiu, PTT | 202608_輿情新聞.md | ✅ 輿情與新聞更新成功（涵蓋 Reddit 深度價值分析、S&P Global 評級調升為正面、8.35億美元 Talkspace 併購案完成、Q2 財報與全年度財測微調、猶他州校區執照撤銷等重大事件） |
| 2832 台產 | 臺灣證券交易所電子書 (MOPS) | 2832_Quarter_2026Q2.md | ✅ 下載並轉換成功（115 年第 2 季個別財務報告書，於 2026-08-31 14:17 申報上傳，IFRS 17 查核無保留意見，H1 EPS 3.33 元） |
| 2832 台產 | 股市爆料同學會 (CMoney API)、工商時報、經濟日報、鉅亨網、PTT、Dcard | 202608_輿情新聞.md | ✅ 輿情與新聞更新成功（收錄 2026/08/28 董事會通過半年報 EPS 3.33 元、減資效應、無息浮存金護城河與產險五強評比等實質討論） |
| 8433 弘帆 | 公開資訊觀測站 (MOPS) / 官網 IR | 8433_annual_2024.md<br>8433_annual_2025.md<br>8433_Quarter_2026Q2.md | ✅ 經檢核已完整涵蓋最新「2年報 + 1季報」（2026 Q2 財報已於 2026-08-07 通過公告，H1 EPS 2.79 元），本期資料已齊全無須重複下載 |
| 4417 金洲 | 公開資訊觀測站 (MOPS) / 財報狗 | 4417_2024_annual_report.md<br>4417_2025_annual_report.md<br>4417_2026Q1_quarterly_report.md<br>4417_Quarter_2026Q2.md | ✅ 經檢核已完整涵蓋最新「2年報 + 1季報」（2026 Q2 財報已於 2026-08-06 通過公告，H1 EPS 2.33 元），本期資料已齊全無須重複下載 |
| 4417 金洲 | 股市爆料同學會 (CMoney API)、工商時報、鉅亨網、MoneyDJ、財報狗、PTT、雪球 | 202608_輿情新聞.md | ✅ 輿情與新聞更新成功（收錄 2026/08/06 董事會通過半年報 EPS 2.33 元、7月營收 3.69 億元創歷史新高、軍事偽裝網/無人機攔截網防衛題材、高殖利率存股與低流動性等實質討論） |
| 2881 富邦金 | 臺灣證券交易所 (MOPS) / 財報狗 | 2881_Quarter_2026Q2.md | ✅ 下載並轉換成功（115 年第 2 季合併財務報告書，經會計師核閱重編，H1 EPS 5.95 元 / 調整後 EPS 13.17 元） |
| 2881 富邦金 | 股市爆料同學會 (CMoney API)、鉅亨網、經濟日報、PTT、Dcard | 202608_輿情新聞.md | ✅ 輿情與新聞更新成功（收錄 CMoney 100 篇討論、法說會獲利與股利政策展望、人壽與銀行營運剖析、PTT/Dcard 自結獲利與 IFRS 17 處分利益討論） |

## 2. 失敗或被擋網站與 MCP 替代紀錄
- **來源**: Apify Reddit Actor (	rudax/reddit-scraper-lite)
  - **原因**: 觸發帳號月度額度上限 (Monthly usage hard limit exceeded)
  - **已依 §2 / §2.9 換過的 MCP**: 依 SOP 替代路徑切換至 Bright Data（search_engine + scrape_as_markdown），成功抓取 Reddit r/stocks、r/investing、r/ValueInvesting 真實貼文。
- **來源**: Reuters（[https://www.reuters.com/...](https://www.reuters.com/)）
  - **原因**: Bright Data 抓取時遭遇目標伺服器阻擋
  - **已依 §2 換過的 MCP**: 切換至 Firecrawl（irecrawl_scrape），成功突破並抓取路透專題報導。
- **來源**: S&P Global Ratings（[https://www.spglobal.com/ratings/...](https://www.spglobal.com/ratings/)）
  - **原因**: Bright Data scrape_as_markdown 回傳前端框架外殼
  - **已依 §2 換過的 MCP**: 切換至 Firecrawl（irecrawl_scrape），成功完整抓取 S&P Global 官方評級報告正文與分析數據。
- **來源**: 格隆匯 (Gelonghui) / 雪球 (Xueqiu) 針對 2832 台產、8433 弘帆、4417 金洲、2881 富邦金搜尋
  - **原因**: 搜尋台股標的無個股專屬社群討論版面
  - **已依 §2 換過的 MCP**: Bright Data / Firecrawl，確認回傳為通用產業觀點或無專屬貼文，已依 §5.0/§5.4 誠實記錄於各公司輿情檔中。

## 3. 資料缺失說明
- **Toyota Motor Corp (7203 / TM)**：財報完整無缺失，最新發布之 FY2027 第一季（2026年4月~6月）決算已於 2026 年 8 月初公佈並收錄。
- **Universal Health Services (UHS)**：財報完整無缺失，最新 2026 Q2 10-Q 於 2026-08-07 申報並收錄。PTT 股市板近三個月無專門標的文，已依規範於輿情檔中誠實記錄搜尋嘗試與冷門股狀態。
- **臺灣產物保險 (2832 台產)**：財報完整無缺失（2024 年報、2025 年報、2026 Q1 季報、2026 Q2 季報均已收錄轉為 Markdown）。港陸平台（雪球、格隆匯）因台股純產險公司關注度較低，無專屬個股深度討論，已如實記錄。
- **弘帆 (8433 弘帆)**：財報完整無缺失（2024 年報、2025 年報、2026 Q1 季報、2026 Q2 季報均已完整收錄）。PTT 股市板與雪球社群近三個月無新增專文討論（屬冷門定存股特性），已依規範如實記錄檢索過程。
- **金洲 (4417 金洲)**：財報完整無缺失（2024 年報、2025 年報、2026 Q1 季報、2026 Q2 季報均已完整收錄）。PTT 股市板近三個月無專門標的文，雪球亦無專版（屬台股上櫃傳產冷門股），已依規範如實記錄檢索歷程。
- **富邦金 (2881 富邦金)**：財報完整無缺失（2024 年報、2025 年報、2026 Q1 季報、2026 Q2 季報均已完整收錄轉為 Markdown）。雪球社群無台股 2881 專屬討論，已依規範如實記錄檢索歷程。

## 4. 異常檔案刪除紀錄
- 本次下載之 2832_Quarter_2026Q2.pdf (5.42 MB) 及 2881_Quarter_2026Q2.pdf (4.10 MB) 經 pymupdf4llm 成功轉換為 .md（0 處 CID 亂碼）後，依規範自動刪除來源 PDF。

## 5. 本次執行使用的 MCP（強制填寫）
| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| **Firecrawl MCP** | irecrawl_scrape<br>irecrawl_search | 突破 JS 渲染與防爬阻擋，抓取 StatementDog 電子書下載清單、鉅亨網新聞、Dcard 貼文、S&P Global Ratings 評級報告與財經專欄報導。 |
| **Bright Data MCP** | search_engine<br>scrape_as_markdown | 搜尋並抓取 Reddit（r/ValueInvesting）、雪球（Xueqiu）討論板、PR Newswire 官方重大新聞稿及財經新聞。 |
| **PyMuPDF4LLM MCP** | convert_pdf_to_markdown | 將 2832_Quarter_2026Q2.pdf 及 2881_Quarter_2026Q2.pdf 完整轉換為高品質 Markdown 格式。 |
| **Exa MCP** | web_search_exa | 搜尋 PTT 股市板、工商時報、鉅亨網、MoneyDJ、經濟日報等在 2026 年 6~8 月之報導與討論文章。 |
| **SEC EDGAR MCP** | get_cik_by_ticker<br>get_company_info<br>get_recent_filings<br>nalyze_8k | 查詢美股最新 10-K、10-Q、8-K 申報紀錄。 |
| **Apify MCP** | call-actor (	rudax/reddit-scraper-lite) | 依 §2.9 SOP 呼叫 Reddit 爬蟲 Actor 抓取美股討論。 |
