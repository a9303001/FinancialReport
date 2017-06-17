# 任務執行最終報告 - 2026/10/19（EVTC）

- **執行日**：2026-10-19（輪替表第 19 日 → EVTC EVERTEC，美股）
- **公司資料夾**：`EVTC/`
- **備註**：同日已有使用者手動指定的 TLK 報告 `CollectsentimentAndReports_Summary_20261019.md`，本報告另以 `_EVTC` 後綴存檔，不覆蓋。

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| EVTC | 本機盤點 + SEC EDGAR submissions JSON | （無新檔） | ⭕ 已有 FY2024、FY2025 年報與 2026Q2 季報（`EVTC_AnnualReport_2024/2025.md`、`EVTC_Quarter_2026Q2.md`）；Q3 10-Q 尚未申報 |
| EVTC | Yahoo Finance、yfinance、Simply Wall St、Zacks、StockStory、GuruFocus、Argus、KBW（經 AD HOC NEWS）、MarketBeat、Seeking Alpha、Reddit、X、雪球、SEC、News is my Business | `EVTC/202610_輿情新聞.md`（新建） | ✅ 補 2026-09-19 ~ 10-19 新內容 |

**本期重點**（每股換算以流通股 59,752,542 股為基準）：
- **股價與估值**：10-16 收 30.86 美元，站上 50 日（29.31）與 200 日（28.29）均線；Trailing P/E 約 20 倍、Forward P/E 約 7 倍（Forward EPS 4.38 美元）。Trailing 與 Forward 差距大，是因為 Q2 GAAP 淨利只有 540 萬美元（每股 0.09 美元），受減損、資安事件成本、收購攤銷與稅務項目拖累。
- **分析師動向（偏中性）**：KBW 目標價 40 → 38 美元（維持 Outperform，10-05）；Argus 31 美元（10-07）→ 32 美元（10-14），只略高於現價；MarketBeat 共識 4 Hold / 2 Buy、平均目標價 35 美元；Zacks Rank #2、Value A，全年 EPS 共識 90 天上修 5.6%。
- **空方論點**：Seeking Alpha（10-11，Growth Stock Hunter）偏謹慎：高負債、利息成本上升、依賴 Popular（10% 折扣已壓低 Business Solutions 營收）、拉美匯率風險；GuruFocus 雖給 GF Value 46.34 美元，但同時標示「Possible Value Trap」、財務實力 4/10。
- **內部人**：近 90 天賣出 20,580 股、約 64.5 萬美元（每股約 0.011 美元，佔流通股 0.03%），規模小。
- **放空**：放空股數 9 月底 256 萬股（月減約 8%），佔流通股 6.3%，回補天數 5.4 天。
- **下一個催化劑**：Q3 2026 財報預計 2026-11-04 盤後（yfinance / AD HOC NEWS），公司尚未正式公告。公司 2026 指引：營收 10.85 ~ 10.95 億美元（每股約 18.2 ~ 18.3 美元）、Adjusted EPS 3.94 ~ 4.04 美元。

## 2. 失敗或被擋網站
- **來源**：[Firecrawl（firecrawl_search）](https://firecrawl.dev)｜**原因**：HTTP 402 / Insufficient credits（帳號級）｜**已試過**：firecrawl_search site:x.com → 本次全程停用，改用 Exa / WebSearch
- **來源**：[X 公司帳號頁](https://x.com/Evertec_Inc)｜**原因**：WebFetch HTTP 402｜**已試過**：firecrawl_search（無額度）、WebSearch allowed_domains 索引（僅取得無日期摘要）
- **來源**：[Evertec IR 新聞稿頁](https://ir.evertecinc.com/news-events/press-releases)｜**原因**：curl 403｜**已試過**：curl；改以 SEC EDGAR 確認 09-19 後無新 8-K
- **來源**：[Seeking Alpha 文章](https://seekingalpha.com/article/4953322-evertec-stock-latin-america-expansion-driving-growth)｜**原因**：付費牆（只取得摘要與開頭）｜**已試過**：Bright Data scrape_as_markdown（第 1 次空白，第 2 次成功）

## 3. 資料缺失說明
- Q3 2026 10-Q 尚未申報（Q3 財報預計 2026-11-04 發布），所以最新季報仍是 2026Q2，屬正常狀態。
- Reddit、X、雪球在 09-19 ~ 10-19 期間都沒有 EVTC 投資討論：小型股、社群關注度低（雪球 79 人關注）。
- Reuters / Bloomberg 在 09-19 以後沒有 EVTC 新稿。

## 4. 異常檔案刪除紀錄
無。

## 5. 本次使用的 MCP
| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| yfinance | get_stock_info、get_recommendations | 行情/估值/放空/財報日快照；評等異動（回空陣列） |
| Apify | call-actor `trudax/reddit-scraper-lite`、get-dataset-items | Reddit 搜尋（0.1 美元上限中止，15 筆皆不相關） |
| Bright Data | scrape_as_markdown | 雪球個股頁、Seeking Alpha 文章 |
| Exa | web_search_exa | 分析師目標價稿（MarketBeat、AD HOC NEWS）、Reuters 轉載搜尋 |
| Firecrawl | firecrawl_search | ❌ HTTP 402 額度用盡（帳號級錯誤，本次全程停用） |
| 內建工具 | WebFetch、WebSearch、curl | Yahoo Finance 新聞與單篇、GuruFocus、News is my Business、SEC EDGAR JSON |

## 6. Phase 4 Convert2md
本次沒有新下載 PDF / HTML，略過。

## 7. Skill 維護
- 修改 §4.1「美股分析師評級」列：補上 yfinance `upgrades_downgrades` 對小型股常回空陣列，此時改用 Exa `web_search_exa` 取得 MarketBeat 共識稿與 `ad-hoc-news.de` 目標價異動稿全文（皆為自動稿）；Argus 網址改為不限 Yahoo UK 子網域。更新 [2026-10]。
- `.claude/` 與 `.agents/` 兩份 SKILL.md 已用 diff 確認一致。
