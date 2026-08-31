# 任務執行最終報告 - 2026/08

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `6121 新普` | 本地已具備完整財報 | `2024_6121_20250529FE4_20260623_014337.md`<br>`2025_6121_20260529FE4_20260623_014508.md`<br>`6121_Quarter_2026Q2.md` | 2 年報 + 1 季報均已齊備，跳過重複下載 |
| `6121 新普` | CMoney、PTT、鉅亨網/經濟日報/MoneyDJ | `202608_輿情新聞.md` | 輿情收集完成，涵蓋蘋果摺疊機雙電芯趨勢、輝達 800VDC BBU 機架商機、Q2 財報後技術面及 ETF 換股與母以子貴討論 |
| `6781 AES-KY` | 財報狗 / TWSE MOPS | `6781_Quarter_2026Q2.md` | 2026 Q2 季報 PDF 下載成功並完成 Markdown 轉換；2024、2025 年報均已齊備 |
| `6781 AES-KY` | CMoney、PTT、鉅亨網/經濟日報/MoneyDJ | `202608_輿情新聞.md` | 輿情收集完成，涵蓋輝達 800VDC 白皮書 HVDC 高壓 BBU 爆發、Q2 獲利破 10 億元創歷史新高、7 月營收新高及千金股籌碼討論 |
| `87001 匯賢Reit` | HKEXnews / 官網 IR | `20250424_2024年年報.md`<br>`20260423_2025年年報.md`<br>`87001_Quarter_2026Q2.md` | 2024、2025 年報及 2026 中期報告均已齊備，跳過重複下載 |
| `87001 匯賢Reit` | 雪球、港媒 (經濟通/明報/AASTOCKS)、富途牛牛、Simply Wall St、Discuss HK | `202608_輿情新聞.md` | 輿情收集完成，涵蓋 2026 中期業績剖析（酒店復甦 vs 寫字樓零售承壓）、2050 合營屆滿清算條款與 DCF 重估、長實 60.23 億港元重大投資減值、Simply Wall St 估值鴻溝分析與港股持有人討論 |

## 2. 失敗或被擋網站
- **來源**: [Reddit](https://www.reddit.com/)
  - **原因**: 搜尋 `6121`、`AES-KY`、`Hui Xian REIT` / `87001` 無個股投資專題討論（搜尋 87001 多為美國郵遞區號）。
  - **已依 §2 換過的 MCP**: apify（月度額度超限）→ firecrawl（`firecrawl_search`）

- **來源**: [雪球 Xueqiu](https://xueqiu.com/)
  - **原因**: 台股代號（`6121`、`6781`）無專題討論；港股 `87001` 成功透過 Bright Data 爬取專欄與股友討論。
  - **已依 §2 換過的 MCP**: brightdata `scrape_as_markdown`

- **來源**: [東方財富股吧 Guba](https://guba.eastmoney.com/)
  - **原因**: 港股 `87001` 過去三個月全為系統自動同步之港交所公告，散戶受限於券商權限缺乏買賣討論。
  - **已依 §2 換過的 MCP**: brightdata `scrape_as_markdown`

- **來源**: [股市爆料同學會 CMoney / PTT]
  - **原因**: 港股 `87001` 在台灣社群無討論（CMoney API 回傳 0 篇）。

## 3. 資料缺失說明
- `87001 匯賢Reit` 之最新 2 份年報（2024、2025）及最新中期報告（2026 中期 / 2026Q2）均已完整具備，無財報缺失。
- 輿情方面，主要討論集中於雪球、香港財經媒體（長實對匯賢減值 60.23 億港元）與海外機構分析（Simply Wall St），台灣社群與 Reddit 則無討論。

## 4. 異常檔案刪除紀錄
- `d:\FinancialReport\AES-KY\6781_Quarter_2026Q2.pdf` 於轉換為乾淨 Markdown（`6781_Quarter_2026Q2.md`）並通過 0 個 CID 檢查後，依 Convert2md 規範刪除來源 PDF。

## 5. 本次執行使用的 MCP（強制填寫）
| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| `pymupdf4llm-mcp` | `convert_pdf_to_markdown` | 將財報 PDF 轉換為 Markdown 文件 |
| `brightdata` | `scrape_as_markdown` | 爬取雪球專欄/討論頁、東方財富股吧等動態渲染頁面 |
| `firecrawl-mcp` | `firecrawl_search` | 檢索 Reddit 英文社群對於個股之討論 |
| `apify` | `call-actor` | 嘗試呼叫 `trudax/reddit-scraper-lite` 抓取 Reddit（因帳號額度上限轉由 Firecrawl 替代） |
