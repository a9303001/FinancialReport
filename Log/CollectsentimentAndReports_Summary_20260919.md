# 任務執行最終報告 - 2026/09/19

- **執行 Skill**：`CollectsentimentAndReports`
- **觸發來源**：`Routines_CollectsentimentAndReports.md` 每日輪替表 → 當日為 **19 日** → `EVTC` / `EVERTEC, Inc.`（美股，資料夾 `EVTC`）
- **COMPANY_TICKER**：`EVTC`｜**COMPANY_NAME**：`EVERTEC, Inc.`

---

## 1. 成功紀錄

| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `EVTC` | SEC EDGAR（MCP）| `EVTC_AnnualReport_2025.md` | **已存在，跳過下載**（FY2025 10-K，最新年報）|
| `EVTC` | SEC EDGAR（MCP）| `EVTC_AnnualReport_2024.md` | **已存在，跳過下載**（FY2024 10-K，次新年報）|
| `EVTC` | SEC EDGAR（MCP）| `EVTC_Quarter_2026Q2.md` | **已存在，跳過下載**（對應 2026-08-06 申報、期間 2026-06-30 之 10-Q，為目前最新季報）|
| `EVTC` | 雪球、StockTitan、SEC EDGAR Form 4/144、MarketBeat、Simply Wall St、Zacks/Yahoo、TipRanks | `202609_輿情新聞.md` | **新建成功**（9 個來源章節，7 成功／2 失敗誠實記錄）|

### 1.1 Phase 2 財報盤點結論（§4.0）
- 依統一命名規則盤點，年報 `{FY}` 已涵蓋 **2024、2025**；季報已涵蓋 **2026Q2**。
- 以 MCP `SEC EDGAR` `get_recent_filings`（近 200 天）核對：最新 10-Q 為 `0001559865-26-000047`（申報日 2026-08-06、期間 2026-06-30），**與本地 `EVTC_Quarter_2026Q2.md` 一致**；期間內無新的 10-K。
- **結論：財報無缺口，本次不需下載任何新檔案**（Q3 2026 10-Q 依公司行事曆預計 2026-11 初才發布）。
- 附帶發現：資料夾內同時存在舊命名檔（`evtc-20241231.md`、`evtc-20251231.md`、`evtc-20260331.md`、`evtc-20260630.md`）與新命名檔，內容與大小一一對應（互為重複）。依 §4.0「舊檔不強制改名」原則本次未動，但建議下次清理以節省空間。

### 1.2 Phase 3 輿情重點（完整內容見 `EVTC/202609_輿情新聞.md`）
- **新增利多**：Zacks 2026-09-17 上調至 Rank #2（Buy），FY2026 共識 EPS $4.00、近三月上修 5.6%；董事 Brian John Smith 2026-06-12 公開市場買進 16,202 股（$26.42、42.8 萬美元）；Q2 回購 1,907,437 股、均價僅 $24.68，授權提高至 1.5 億美元。
- **新增利空**：2026-08-11 ~ 09-03 內部人 Form 4 **全為賣出**（6 筆、49,150 股、約 151 萬美元），EVP & CIO 與 EVP 單筆出清其持股 34.2%／27.4%；股價自 09-01 的 $29.16 跌至 09-18 的 $27.65，跌破 50 日（$30.08）與 200 日（$28.14）均線；MarketBeat 2026-09-15 共識為 **Hold**（4 Hold / 2 Buy、目標價 $35.00）；Business Solutions 分部營收衰退；GAAP EPS 指引 $1.61~$1.73 與 Adjusted EPS $3.94~$4.04 差距達 2.3 倍。
- **假訊息辨識**：查獲 ad-hoc-news.de（2026-09-01）一文的內部人賣出金額（誇大 100 倍）、Q2 營收與淨利皆嚴重失真，已於輿情檔中逐項比對 SEC 原始申報更正並標註「不可引用」。

---

## 2. 失敗或被擋網站

- **來源**: [Reddit](https://www.reddit.com/)
  - **原因**: 內建工具 user-agent 遭封鎖；Firecrawl **額度用盡**；Bright Data 需 KYC（`Residential Failed (bad_endpoint)`）；Apify **月用量達上限**（`Monthly usage hard limit exceeded`）；Playwright **本環境未安裝 Chromium**（`/opt/google/chrome/chrome` 不存在）。
  - **已依 §2 換過的 MCP**: firecrawl → brightdata → apify → playwright（四條全試過，全部失敗）；最後以 `brightdata search_engine` 取得 Google 索引清單作為替代（僅標題與網址，無時間戳與內文）。

- **來源**: [X (Twitter)](https://x.com/)
  - **原因**: Firecrawl 額度用盡（前次 2026-09-02 成功使用的 `firecrawl_search` + `site:x.com` 路徑本次不可用）；`brightdata search_engine` 60 秒逾時（依 §2.5 零重試換來源）；Exa 搜尋回傳結果中無任何 x.com 貼文。
  - **已依 §2 換過的 MCP**: firecrawl（額度）→ brightdata（逾時）→ Exa（無結果）。

- **來源**: [StockTitan](https://www.stocktitan.net/news/EVTC/)
  - **原因**: `firecrawl_scrape` 額度用盡。
  - **處置**: 依 §2.1 遞補至 `brightdata scrape_as_markdown`，**成功**取得完整新聞稿清單。

---

## 3. 資料缺失說明

1. **財報無缺失**：兩份年報（FY2024、FY2025）與最新季報（2026Q2）皆已齊備並經 SEC EDGAR 核對。
2. **Reddit / X 輿情缺失**：肇因於本次執行環境的**第三方服務額度與環境限制**（Firecrawl 無額度、Apify 月配額用盡、Bright Data 未完成 KYC、Playwright 無瀏覽器），非目標網站本身無資料。建議下次執行前確認上述額度狀態。
3. **台灣／華語討論區無內容**：EVTC 市值約 16.5~17.5 億美元、業務集中波多黎各與拉美，台灣與中國散戶關注度極低（雪球關注僅 79 人、討論區全為公告機器人轉發），屬長期結構性冷門，已依 §5 第 7 點記錄查詢過程。

---

## 4. 異常檔案刪除紀錄

- **無**。本次未下載任何新檔案，故無 <10KB、無公司名稱或 `(cid:` 亂碼等異常檔案需刪除。
- Phase 4 `Convert2md`：EVTC 資料夾內**無任何 PDF/HTML 待轉換**（既有檔案皆已為 `.md`），本階段無作業項。

---

## 5. 本次執行使用的 MCP

| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| SEC EDGAR | `get_recent_filings` | 核對 EVTC 近 200 天申報，確認最新 10-K／10-Q 與本地檔案是否一致 |
| SEC EDGAR | `get_insider_summary` | 取得近 120 天內部人申報統計（17 筆 Form 4、11 位內部人）|
| SEC EDGAR | `analyze_form4_transactions` | 取得每筆 Form 4 的交易日、代碼、股數、成交均價與交易後持股 |
| Bright Data | `scrape_as_markdown` | 抓取雪球 `xueqiu.com/S/EVTC` 個股頁；Firecrawl 失效後遞補抓取 StockTitan 新聞稿頁 |
| Bright Data | `search_engine` | Google `site:reddit.com` 索引搜尋（Reddit 四鏈全滅後的替代路徑）|
| Exa | `web_search_exa` | 搜尋 2026-06~09 的分析師評級、Simply Wall St、Zacks、TipRanks 原文摘錄 |
| Exa | `web_fetch_exa` | 嘗試讀取 Reddit 貼文內文（回 `SOURCE_NOT_AVAILABLE`，失敗）|
| yfinance | `get_yahoo_finance_news` | 取得 Yahoo Finance 上 EVTC 最新新聞清單（發現 Zacks 升評）|
| Firecrawl | `firecrawl_scrape` | **失敗**：`Insufficient credits`（額度用盡）|
| Apify | `call-actor`（`trudax/reddit-scraper-lite`）| **失敗**：`Monthly usage hard limit exceeded` |
| Playwright | `browser_navigate` | **失敗**：`Chromium distribution 'chrome' is not found`（環境未安裝）|
| GitHub | `create_pull_request` | 建立本次變更之 Draft PR |

> 內建工具部分另使用：`WebSearch`（EVTC 2026 年 9 月新聞概況）、`Bash`（檔案盤點與寫檔）。

---

## 6. 分支與推送說明（與 Skill §7 的差異，需留意）

- Skill §7 要求「強制 push 到 `master`」，但本次 session 的系統層指令明確指定**所有開發與推送一律使用分支 `claude/nice-allen-zlla5d`，未經明確許可不得推送到其他分支**。
- 依系統層指令優先原則，本次變更已推送至 **`claude/nice-allen-zlla5d`** 並開立 Draft PR；**合併進 `master` 需由使用者在 PR 上確認**。
