# 任務執行最終報告 - 2026/10（執行日期 8 → 2832 台產）

- **執行時間**：2026-10-08 20:11～20:25 UTC（台北 2026-10-09 04:11～04:25）
- **公司**：`2832` 台產（台灣產物保險），資料夾 `2832台產/`

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `2832台產` | （本機盤點） | `2832_AnnualReport_2024.md`、`2832_AnnualReport_2025.md`、`2832_quarter_2026Q1.md`、`2832_Quarter_2026Q2.md` | 已有 2 份年報＋最新季報（2026Q2），**不需下載**。2026Q3 季報要到 11 月中才會公告 |
| `2832台產` | 鉅亨 API、Yahoo股市、MoneyDJ、經濟日報、工商時報、方格子 vocus、CMoney API、PTT、Dcard、yfinance | `202610_輿情新聞.md`（新建） | 增補 2026-09-14～10-08 的新內容，共 10 個來源章節 |

**本次重點發現**：
- 9/14 法說會：財務長表示減資後法定盈餘公積已超過資本額，「口袋更深」；外界估明年配息率五至六成以上（Yahoo），MoneyDJ 估七成起跳。2025 年度實際配息率是 89.5%，所以明年配息率不一定比今年高。
- 公司自己提到的風險：8 月台幣升值造成約 0.2 億元以上的匯損；IFRS 17 規定大額理賠時要先提列 1%～2% 再保人信用減損。
- 經濟日報：H1 固定收益收入和租金收益小幅下滑，自有資本比率降到 46.1%。
- 台產股票部位只占一成多，產業平均是 20.6%（工商時報 10/03），台產比同業保守。
- 股價從 9/16 的 59.1 元回落到 10/07 的 56.8 元，成交量縮到每天 3～14 萬股。
- 查證：搜尋引擎說「10 月減資退回每股 3 元」是 2025 年的舊聞，不是新事件。

## 2. 失敗或被擋網站
- **來源**：[經濟日報「產險雙引擎推升獲利」](https://money.udn.com/money/story/5613/9759271)
  - **原因**：`curl` 只拿到頁面殼，沒有正文
  - **處理**：改用 firecrawl_search 的索引摘要，在輿情檔標註「非原始頁面逐字引述」（文章沒有點名台產，只是產業背景，所以沒有再跑 brightdata/apify/playwright）
- **來源**：方格子 vocus 法說最速報
  - **原因**：付費牆（`isAccessibleForFree: False`），不是封鎖
  - **處理**：只引用公開摘要
- **來源**：工商時報「新產、臺產H1獲利年增靚」
  - **原因**：只有 Google News RSS 標題，WebSearch／firecrawl_search 找不到原始網址
  - **處理**：只記錄標題，不列入分析

## 3. 資料缺失說明
- **2026 年 9 月營收**：抓取時還沒公告（法定期限 10/10），下次執行要補。
- **2026Q3 季報**：還沒發布（預計 11 月中）。
- **社群輿情很少**：PTT 自 2025-04 後沒有新文章；Dcard 近一個月 0 筆；CMoney 近一個月沒有散戶自己寫的討論，只有轉貼新聞和生技股洗版文。台產是冷門小型產險股，這種情況是正常的。

## 4. 異常檔案刪除紀錄
- 本次沒有下載財報，所以沒有刪除任何檔案。暫存檔都放在 session scratchpad，不在 repo 內。

## 5. 本次執行使用的 MCP
| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_search` | 找 vocus 法說摘要、工商時報產險投資文章、經濟日報產業文章的網址；搜尋 Dcard |
| Yahoo Finance (yfinance) | `get_historical_stock_prices` | 取得 2832.TW 近一個月的股價和成交量 |
| GitHub | `create_pull_request`、`merge_pull_request` | 建立 PR，並把本次輿情檔和報告合併進 master |

**內建工具**：`Bash`（`curl`：鉅亨 API、CMoney API、Yahoo股市、MoneyDJ、經濟日報、工商時報、PTT、Google News RSS）、`WebSearch`、`WebFetch`。

**§2.4 經驗增補**：
- MoneyDJ 站內搜尋 `kmdj/search/list.aspx?_Query_={關鍵字}&_QueryType_=NW` 是 SSR，`curl` 可以直接讀；單篇文章的全文在 JSON-LD `articleBody` 裡，不需要 MCP。
- Google News RSS（`news.google.com/rss/search?q={關鍵字}+when:30d&hl=zh-TW&gl=TW&ceid=TW:zh-Hant`）適合快速找近 30 天的台股新聞標題，但連結是 Google 轉址，要再用 WebSearch／firecrawl_search 找原始網址。
