# 任務執行最終報告 - 2026/08

- **執行日期**：2026-08-31
- **輪替日期編號**：16
- **執行標的**：`00546` 阜豐集團有限公司 (Fufeng Group Limited)
- **所屬市場**：港股 (00546.HK / 546)

---

## 1. 成功紀錄

| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `00546 阜豐` | HKEXnews / 披露易 | `00546_AnnualReport_2024.md` | 2024 年報（本地已存在且完整） |
| `00546 阜豐` | HKEXnews / 披露易 | `00546_2025_annual_report.md` | 2025 年報（本地已存在且完整） |
| `00546 阜豐` | HKEXnews / 披露易 | `00546_Quarter_2026Q2.md` | 2026 中期業績報告（2026-08-28 公佈，本地已存在且為最新） |
| `00546 阜豐` | 雪球、智通財經、同花順、中金公司、HKEX披露 | `202608_輿情新聞.md` | 輿情與重大新聞彙整（涵蓋 2026/06~08 盈警、回購、中報、中金評級、哈薩克基地進度） |

---

## 2. 失敗或被擋網站

- **來源**: Apify Reddit Actor (`trudax/reddit-scraper-lite`)
- **原因**: 帳號配額超限 (`Monthly usage hard limit exceeded`)
- **處理方式**: 依 §2 通用抓取規則啟動 Exa 與原生 Search Web 進行全網檢索 fallback，確認過去三個月內 Reddit 無 00546 股票投資相關討論（僅有歷史土地案回顧及無關遊戲名詞）。

---

## 3. 資料缺失說明

- **財報資料**：最新之 2026 中期報告已於 2026 年 8 月 28 日發布並已收錄於本地；目前無缺失。
- **輿情資料**：已完整涵蓋雪球投資人深度討論、中金最新券商研報、6月盈警暴跌、7月股份回購、8月中報利潤下滑、哈薩克斯坦產能爬坡及大宗商品（味精/蘇氨酸/賴氨酸/黃原膠/玉米）價格現況。

---

## 4. 異常檔案刪除紀錄

- 本次無小於 10KB、無公司名稱或 CID 亂碼過多之異常檔案刪除。

---

## 5. 本次執行使用的 MCP（強制填寫，無則註明「未使用」）

| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| **Bright Data** | `scrape_as_markdown` | 抓取雪球 00546 專頁、智通財經/同花順 6/18 盈警報導全文 |
| **Bright Data** | `search_engine` | 檢索東方財富、新浪港股、富途、格隆匯之新聞索引 |
| **Apify** | `call-actor` (`trudax/reddit-scraper-lite`) | 嘗試抓取 Reddit 討論串（配額超限後記錄） |
| **Exa** | `web_search_exa` | 搜尋 Reddit 相關討論與最新研報驗證 |
| **PyMuPDF4LLM** | `convert_pdf_to_markdown` | 執行 Convert2md 掃描轉換驗證流程 |

---
---

# 任務執行最終報告 - 2026/08/31（排程輪替執行：第 17 輪）

- **執行日期**：2026-08-31
- **輪替日期編號**：17
- **執行標的**：`1301` 株式会社 極洋 (KYOKUYO CO., LTD.)
- **本地資料夾**：`1301極洋/`
- **所屬市場**：日股 (東証プライム 1301)

---

## 1. 成功紀錄

| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `1301 極洋` | EDINET / 官網 IR | `S100W543.md` | 第 102 期有價證券報告書（FY2025: 2024/4/1~2025/3/31，本地已完整轉換） |
| `1301 極洋` | EDINET / 官網 IR | `S100YE8K.md` | 第 103 期有價證券報告書（FY2026: 2025/4/1~2026/3/31，本地已完整轉換） |
| `1301 極洋` | 東証 TDnet / 官網 IR | `1301_Quarter_2027Q1.md` | 2027 年 3 月期 第 1 四半期決算短信（FY2027 Q1，發布日 2026-08-07，本地已完整轉換） |
| `1301 極洋` | 株探 (Kabutan)、みんかぶ (Minkabu)、Yahoo!ファイナンス 掲示板、note.com、PR TIMES、Reddit | `1301極洋/202608_輿情新聞.md` | 輿情與重大新聞彙整（涵蓋 8/18 罐頭/香腸調價 10~25%、8/7 1Q 決算純益成長 29%、壽司郎/元氣壽司供應鏈需求、黑鮪魚配額擴增 25%、200 億日圓政策保有股期待、歐美 r/CannedSardines 社群口碑） |

---

## 2. 失敗或被擋網站

- **來源**: Apify Reddit Actor (`trudax/reddit-scraper-lite`)
- **原因**: 帳號月度額度限制 (`Monthly usage hard limit exceeded`)
- **處理方式**: 依 §2 通用抓取規則 fallback 採用 Exa 與原生 Search Web 檢索 Reddit，成功取得 r/CannedSardines 海鮮罐頭社群針對極洋味噌鯖魚、沙丁魚罐頭之真實消費者評價並完整收錄。
- **CMoney / PTT / 雪球**: 依規範檢索並誠實記錄：CMoney 與 PTT 代號 1301 主要討論台股台塑；雪球無日股 1301 專版，近三個月無極洋討論。

---

## 3. 資料缺失說明

- **財報資料**：最新之 FY2027 Q1 決算短信已於 2026 年 8 月 7 日發布並已收錄於本地；最新 2 份年報（第 102 期、第 103 期有價證券報告書）均完整收錄，無資料缺失。
- **輿情資料**：涵蓋日本主流財經媒體、社群討論板、深度專欄以及歐美消費社群，資料齊全。

---

## 4. 異常檔案刪除紀錄

- 本次無小於 10KB、無公司名稱或 CID 亂碼過多之異常檔案刪除。Convert2md 掃描確認目前無待轉換之 PDF/HTML 檔案。

---

## 5. 本次執行使用的 MCP（強制填寫，無則註明「未使用」）

| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| **Firecrawl** | `firecrawl_scrape` | 抓取 Kabutan 新聞、Minkabu 評價、note.com 深度決算分析專欄 |
| **Bright Data** | `scrape_as_markdown` | 爬取雪球日股頁面進行驗證 |
| **Exa** | `web_search_exa` | 檢索 Reddit 海外社群討論與官方新聞發布 |
| **Apify** | `call-actor` (`trudax/reddit-scraper-lite`) | 嘗試呼叫 Reddit scraper 取得貼文 |
| **PyMuPDF4LLM** | `convert_pdf_to_markdown` | 執行 Convert2md 掃描轉換驗證流程 |

---
---

# 任務執行最終報告 - 2026/08/31（排程輪替執行：第 18 輪）

- **執行日期**：2026-08-31
- **輪替日期編號**：18
- **執行標的**：`CF` CF Industries Holdings, Inc.
- **本地資料夾**：`CF/`
- **所屬市場**：美股 (NYSE: CF)

---

## 1. 成功紀錄

| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `CF` | SEC EDGAR / 官網 IR | `CF_AnnualReport_2024.md` | 2024 年報 (Form 10-K，本地已完整收錄) |
| `CF` | SEC EDGAR / 官網 IR | `CF_AnnualReport_2025.md` | 2025 年報 (Form 10-K，本地已完整收錄) |
| `CF` | SEC EDGAR / 官網 IR | `CF_Quarter_2026Q2.md` | 2026 Q2 季報 (Form 10-Q，截至 2026-06-30，本地已完整收錄且為最新) |
| `CF` | Reddit、Seeking Alpha、Yahoo Finance、Quartr 法說逐字稿、富途牛牛/Moomoo、雪球、CMoney API、PTT | `CF/202608_輿情新聞.md` | 輿情與重大新聞彙整（涵蓋 8/27 路易斯安那州 140 萬噸 Blue Point 藍氨廠動工、Q2 財報獲利與 Yazoo City 廠復原進度、中期循環 EBITDA 上修至 29 億美元/2030 年 33 億美元、季度股息上調 20% 至 $0.60/股、2021 年以來股數縮減 29%、華爾街最新評級區間 $125~$140、機構持倉與中東地緣政治供需分析） |

---

## 2. 失敗或被擋網站

- **來源**: Apify Reddit Actor (`trudax/reddit-scraper-lite`)
- **原因**: 帳號配額限制
- **處理方式**: 依 §2 通用抓取規則 fallback 採用 Exa 與原生 Search Web 進行多維度檢索，成功取得 Reddit (`r/UsaNewsLive`, `r/EverHint`, `r/ClaudeCode`, `r/wallstreetbets`) 相關真實貼文、量化訊號與基本面討論，並完整收錄真實 URL 與原文。

---

## 3. 資料缺失說明

- **財報資料**：經 `sec-edgar-mcp` 實時查詢確認，CF 最新 10-Q 為 2026 Q2（截至 2026-06-30），最新 2 份 10-K（2024、2025）均已完整收錄於本地，無資料缺失。
- **輿情資料**：已完整涵蓋美股主流財經媒體、法說會關鍵訊息、專業量化/投資社群、華爾街券商評級與華語市場討論，資料詳實完整。

---

## 4. 異常檔案刪除紀錄

- 本次無小於 10KB、無公司名稱或 CID 亂碼過多之異常檔案刪除。Convert2md 掃描確認目前無待轉換之 PDF/HTML 檔案。

---

## 5. 本次執行使用的 MCP（強制填寫，無則註明「未使用」）

| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| **sec-edgar-mcp** | `get_cik_by_ticker`, `get_company_info`, `get_company_facts` | 查詢並核實 CF Industries 最新 SEC EDGAR 申報紀錄與關鍵財務指標 |
| **Exa** | `web_search_exa` | 檢索最新 Seeking Alpha、Yahoo Finance 新聞與法說會逐字稿重點 |
| **Firecrawl** | `firecrawl_scrape` | 爬取富途牛牛/Moomoo 即時新聞與華爾街評級資料 |
| **Bright Data** | `scrape_as_markdown` | 爬取雪球美股頁面驗證社群討論熱度 |
| **PyMuPDF4LLM** | `convert_pdf_to_markdown` | 執行 Convert2md 轉換檢查驗證流程 |
| **內建工具 (pwsh / WebSearch / File)** | `run_command`, `search_web`, `write_to_file`, `view_file`, `list_dir` | 執行 CMoney 官方 API 檢索、全網多來源檢索及檔案維護管理 |

---
---

# 任務執行最終報告 - 2026/08/31（排程輪替執行：第 19 輪）

- **執行日期**：2026-08-31
- **輪替日期編號**：19
- **執行標的**：`EVTC` EVERTEC, Inc.
- **本地資料夾**：`EVTC/`
- **所屬市場**：美股 (NYSE: EVTC)

---

## 1. 成功紀錄

| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `EVTC` | SEC EDGAR / 官網 IR | `EVTC_AnnualReport_2024.md` | 2024 年報 (Form 10-K，本地已完整收錄) |
| `EVTC` | SEC EDGAR / 官網 IR | `EVTC_AnnualReport_2025.md` | 2025 年報 (Form 10-K，本地已完整收錄) |
| `EVTC` | SEC EDGAR / 官網 IR | `EVTC_Quarter_2026Q2.md` | 2026 Q2 季報 (Form 10-Q，截至 2026-06-30，發布日 2026-08-06，本地已完整收錄且為最新) |
| `EVTC` | SEC EDGAR (Form 8-K/4)、Seeking Alpha、Yahoo Finance、MarketBeat、Reddit (r/StockTitan, r/Quantisnow)、CMoney / 富途牛牛 | `EVTC/202608_輿情新聞.md` | 輿情與重大新聞彙整（涵蓋 2026 Q2 財報營收超預期年增 20%、上調全年營收指引至 10.85~10.95 億美元、Dimensa 併購整合綜效、智利 Transbank 與墨西哥 Clip 新約、股票回購擴大至 1.5 億美元、5月資安事件 Form 8-K 後續、8月 Form 4 內部人持股處分、華爾街目標價區間 $30~$40 / 平均 $35.00~$35.60 及華語市場護城河評價） |

---

## 2. 失敗或被擋網站

- **來源**: Apify Reddit Actor (`trudax/reddit-scraper-lite`)
- **原因**: 帳號月度額度限制 (`Monthly usage hard limit exceeded`)
- **處理方式**: 依 §2 通用抓取規則 fallback 採用 Firecrawl search (site:reddit.com) 與 search_web 檢索，成功取得 Reddit (`r/StockTitan`, `r/Quantisnow`) 針對 EVTC 2026 Q2 財報發布與全年指引上修之真實討論與原文。

---

## 3. 資料缺失說明

- **財報資料**：經 `sec-edgar-mcp` 實時檢索確認，EVTC 最新 10-Q 季報為 2026 Q2（申報日 2026-08-06，報告期截至 2026-06-30），最新 2 份 10-K 年報（2024、2025）均已完整收錄於本地，無資料缺失。
- **輿情資料**：已完整涵蓋美股主流財經媒體、SEC 官方申報（8-K / 4）、華爾街券商評級與目標價、Reddit 投資社群與華語討論區觀點，資料詳實完整。

---

## 4. 異常檔案刪除紀錄

- 本次無小於 10KB、無公司名稱或 CID 亂碼過多之異常檔案刪除。Convert2md 掃描確認目前無待轉換之 PDF/HTML 檔案。

---

## 5. 本次執行使用的 MCP（強制填寫，無則註明「未使用」）

| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| **sec-edgar-mcp** | `get_cik_by_ticker`, `get_company_info`, `get_recent_filings`, `analyze_8k`, `get_filing_content`, `analyze_form4_transactions` | 查詢並分析 EVTC 最新 SEC Filings（Form 10-Q, 8-K 資安公告, 8 月 Form 4 內部人交易） |
| **Firecrawl** | `firecrawl_search` | 檢索 Reddit (`site:reddit.com`) 取得最新社群貼文與 Q2 業績討論 |
| **Apify** | `call-actor` (`trudax/reddit-scraper-lite`) | 嘗試呼叫 Reddit scraper（因配額超限記錄並 fallback） |
| **PyMuPDF4LLM** | `convert_pdf_to_markdown` | 執行 Convert2md 掃描轉換驗證流程 |
| **內建工具 (pwsh / WebSearch / File)** | `run_command`, `search_web`, `replace_file_content`, `view_file`, `list_dir` | 檢索華爾街目標價、驗證財報與更新輿情維護 |

