# collectStk 參考：美股 / 英文圈通用 / 印尼

> collectStk 站點知識庫（§4）／API SOP（§5）／官網 IR 備援（§7.3）的「美股 / 英文圈通用 / 印尼 ADR」部分。SEC EDGAR 在 `edgar` skill。
> 只在處理該市場公司時讀。抓取規則（§3）、存檔與過濾（§8）在 `../SKILL.md`。
> 表格格式：站點 / 網址 | 狀況 | 做法；`[yyyy-mm]` = 最後驗證月份。維護規則見 `../SKILL.md` §10。

## §4.1 通用 / 英文圈

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| Reddit | 內建工具 400、Firecrawl 不支援、Playwright 與 `search.json` 回 403 | **跳過 §3.1，直接用 Apify Reddit Actor（§5.3）**。Apify 停用時用 Bright Data `search_engine`；兩者都停用時用 `WebSearch` 搭 `allowed_domains: ["reddit.com"]` 取索引，依 §3.6 註明 [2026-11] |
| X (Twitter) | 未登入即封鎖：Playwright 被導到登入頁；`firecrawl_scrape` 單篇 `x.com/{帳號}/status/{id}` 自 2026-11 起經 Firecrawl x-com provider 回傳全文、`created_at` 與讚數（約 5 credits） | 日股先用 Yahoo 株つぶやき（§4.4）。其他用 `firecrawl_search`，query 內寫 `site:x.com`（`includeDomains` 參數會回 0 筆）找貼文，重要的再 `firecrawl_scrape` 單篇取全文；Firecrawl 沒額度時用 `WebSearch` 搭 `allowed_domains: ["x.com", "twitter.com"]` 取索引。索引沒有時間時，用網址的 status ID 還原：`(id >> 22) + 1288834974657` 毫秒（UTC） [2026-11] |
| Reuters `reuters.com` | 內建 `WebSearch` 被擋（`allowed_domains` 含 reuters.com 會直接回 400） | `firecrawl_scrape`（basic proxy）可抓公司頁與文章頁全文。Firecrawl 沒額度時用 Exa `web_search_exa` 找轉載頁（`tradingview.com/news/reuters.com,...`、`marketscreener.com`），可取標題與時間，正文多半沒有 [2026-10] |
| Bloomberg | 付費牆，不是封鎖 | 取摘要即可，報告註明「付費牆」 |
| 美國地方媒體（中資美國廠，如福耀 FGA：Dayton Daily News `daytondailynews.com`、WHIO `whio.com`） | 中文媒體與 HKEX 不一定轉載；SSR，`curl -L` 可讀 | 用 `firecrawl_search` + `site:x.com {公司英文名}` 找地方媒體 X 貼文（訴訟、火災、勞資常只在這裡出現），再 `curl` 原文：Dayton Daily News（TNCMS）正文在 `<p>`、時間取 JSON-LD `datePublished`；WHIO（Arc）正文在 JSON `"content":"..."` 欄位 [2026-11] |
| 美股分析師評級 | yfinance `get_recommendations`（`upgrades_downgrades`）可列出券商、評等、目標價與時間，但小型股常回空陣列，2026-11 對 CF、EVTC 回錯誤 `'GradeDate'` | 回空或錯誤時先用 `firecrawl_search`（query 寫 `site:x.com ${代號} {公司名}` 之類個股查詢時，回應 `answer` 欄會附 Benzinga news/search 結構化結果：券商、評等、目標價異動標題與 UTC 時間），或 Exa `web_search_exa`（query 寫「{公司名} {代號} stock news {月份年份}」）：會回 MarketBeat 共識稿、`ad-hoc-news.de` 目標價異動稿、TipRanks blurbs（含其他券商同週評等）全文（皆為自動稿，引用時註明），以及 Yahoo `research/stock-forecast/{代號}/` 的 Argus 評等／目標價異動列表與 `finabase.io/symbol/{代號}/analysts` 共識 EPS／營收預估（本季、下季、本年、明年）。細節（理由、EBITDA 預估）用 `WebSearch` 找 `goldesel.de` 德文轉述單篇，`WebFetch` 可讀（頁面自註為 AI 輔助撰寫）；Yahoo `research/reports/ARGUS_*_{毫秒時間戳}` 頁可見 Argus 目標價標題，網址內時間戳即報告日 [2026-11] |
| Seeking Alpha | `firecrawl_scrape` 全引擎失敗 | `firecrawl_search` + `site:seekingalpha.com` + `tbs: qdr:m` 找文章；Firecrawl 沒額度時改用 `WebSearch` 搭 `allowed_domains: ["seekingalpha.com"]`（可排除仿冒 SA 的垃圾頁；不加 domain 限制會混入被入侵的 `.gov.my`、`.ca.gov`、`.edu.tw`，一律排除）。Bright Data `search_engine` 選 `bing` 會回原始 HTML、無法解析，不要用。Bright Data `scrape_as_markdown` 取標題/日期/摘要（第一次常空白，重試 1 次）；Bright Data 不可用時 Apify `apify/rag-web-browser`（`query` 填文章網址）回 200，`markdown` 含發布時間、作者、Summary 與 Quick Insights（`WebFetch` 回 403）[2026-10] |
| MSCI 新聞稿 | `ir.msci.com` 回 Akamai Access Denied | 改抓 `msci.com/downloads/documents/press-releases/media-room/*.pdf`，`curl` + `pdftotext` 可讀全文；PDF 網址用 `WebSearch` 找 [2026-10] |
| Yahoo Finance（美股新聞） | yfinance `get_yahoo_finance_news` 各市場都回「No news found」或誤配同名人物 | **不要用 yfinance 新聞**。改用 `WebFetch` 抓 `finance.yahoo.com/quote/{代號}/news/`（約 12 則標題），單篇文章頁也可讀 [2026-10] |
| `firecrawl_search` 本身 | 一個 query 放多個 `site:` 用 OR 連接會回 0 筆 | 一次只放一個 `site:`，分開查 [2026-10] |

## §4.5 印尼（美股 ADR 的母股，如 TLK ↔ IDX `TLKM`）

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| CNBC Indonesia `cnbcindonesia.com`、Katadata `katadata.co.id`、Selular.ID `selular.id`、periskop.id `periskop.id` | SSR，`curl` 可讀，JSON-LD 有 `datePublished` | 用 `WebSearch`（印尼文關鍵字，如「saham {代號} anjlok」）找網址再 `curl` 單篇；Katadata 是 IDX 公告與券商觀點的主力轉述來源；periskop.id 常逐條轉述公司對 BEI 異常波動詢問的回覆（keterbukaan informasi）[2026-10] |
| Stockbit `stockbit.com/symbol/{代號}`、`stockbit.com/post/{id}` | JS 載入 | Exa `web_search_exa`（query 寫「Stockbit stream {代號} diskusi saham {月份年份}」）回傳單篇全文與時間，依 §3.6 標註為索引；Stockbit 自標「Potential Junk」的貼文排除。研究摘要 `snips.stockbit.com` 也在索引內 [2026-10] |
| Reddit 印尼版 | `r/finansial` 搜尋多為無關貼文；Apify 每次約 0.1 美元上限即中止 | 個股討論以 Stockbit 為主，Reddit 只取大盤情緒 [2026-10] |

## §5.3 Reddit（Apify Actor `harshmaur/reddit-scraper`）

```json
{
  "actor": "harshmaur/reddit-scraper",
  "input": {
    "searchTerms": ["\"{公司英文全名}\"", "{代號} stock {產業詞}"],
    "searchPosts": true,
    "searchComments": false,
    "searchCommunities": false,
    "searchSort": "new",
    "searchTime": "month",
    "maxPostsCount": 10,
    "maxItems": 15
  },
  "waitSecs": 45,
  "callOptions": { "maxTotalChargeUsd": 0.1 }
}
```

- 原用的 `trudax/reddit-scraper-lite` 自 2026-11 起約 1.6 秒即 FAILED（exitCode 4，run log：「Actor is under maintainence. Runs are currently disabled.」），改用本 Actor（約 20 秒完成、約 0.003 CU）。看失敗原因用 `ReadMcpResourceTool` 讀 `https://api.apify.com/v2/actor-runs/{runId}/log` [2026-11]。
- `callOptions.maxTotalChargeUsd` **必填**，低於 0.04 會報 `less than the allowed minimum`。
- 要限定版面時用 `withinCommunity`（依序試 `wallstreetbets`、`stocks`、`investing` 或產業版）；不限定時是全站搜尋。
- **關鍵字不可用泛用詞**（如單獨的 `stock` 會抓到卡車避震、商品補貨）。短代號（如 `UHS`）也常誤配（`University Health Services` 等），公司全名要加引號精確比對，逐則核對是否真與該公司相關。
- 取結果：`get-dataset-items`（`fields: "title,communityName,postUrl,createdAt,authorName,upVotes,commentsCount"`，需要內文再取 `body`）。
- 排除 `AutoModerator` 制式文、純表情回覆、標題與內文都沒提到該公司的貼文；r/TickerWorth、r/EverHint 等是平台自動生成文，要標明。
- Actor 下架時，用 Apify `search-actors`（keywords `Reddit posts`）挑月用量高、有評分的替代品。

## §7.3-US 美股財報來源與官網 IR

- **SEC EDGAR 一律走 `edgar` skill**（collectStk §7.5）：10-K／10-Q、ADR 的 20-F／40-F／6-K 選件、命名、轉檔、驗證與 SEC 端行為、公司特例都記在 `.claude/skills/edgar/SKILL.md` 與 `.claude/skills/edgar/references/lessons.md`，本檔不再重寫。
- edgar 被 SEC 擋或公司不在 SEC（unsponsored ADR，如 HEGIY）時的備援：② 官網 IR（Investor Relations → SEC Filings／Quarterly Results，PDF 存公司資料夾後跑 `Convert2md`）③ 財報狗 `statementdog.com/analysis/{代號}/e-report` ④ 富途 `futunn.com/hk/stock/{代號}-US/announcement`。
