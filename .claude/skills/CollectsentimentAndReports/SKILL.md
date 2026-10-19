---
name: CollectsentimentAndReports
description: 收集個股「最新財務報告（2 年報 + 1 季報）」與「近三個月輿情討論/新聞」，存入公司資料夾，轉 Markdown 後產出執行報告並 push。輸入 COMPANY_TICKER 與 COMPANY_NAME。
---
/goal
# CollectsentimentAndReports — 執行指南

> **任務**：對指定公司 ① 補齊最新財報（2 份年報 + 1 份季報）② 收集過去三個月的輿情/新聞 ③ 轉 Markdown ④ 寫執行報告並 push。
> 本指南適用所有 AI（Claude / Gemini，含輕量模型），請一步一步照做。

## 0. 四條底線（違反任一 = 任務失敗）

1. **防幻覺**：只記錄真實抓到的內容，附真實 URL 與真實發布時間。抓不到就照 §8.5 誠實記錄，**嚴禁**用訓練資料補內容、捏造連結或分配日期。
2. **不從本 repo 線上倉庫收集**：嚴禁從 GitHub `a9303001/FinancialReport` 下載財報或新聞；也嚴禁訪問 `macrotrends.net`。（本機資料夾已有的檔案可以盤點，見 §7.1）
3. **即時存檔**：每下載完一份財報、每抓完一個來源，立刻寫檔，不要等全部做完。
4. **不卡死**：抓取一律照 §3 的固定順序與次數上限，不無限重試、不空等背景任務。

---

## 1. 參數與工具對照

| 參數 | 說明 | 範例 | 若缺失 |
| :--- | :--- | :--- | :--- |
| `COMPANY_TICKER` | 股票代碼（港股補齊 5 碼） | `2881`、`UHS`、`3445`、`02318` | 必填，立刻詢問 |
| `COMPANY_NAME` | 公司名稱 | `富邦金`、`Universal Health Services` | 用代碼先搜尋查出 |

文中提到的工具名一律視為「動作」，用你手上對應的工具完成，名字對不上不要卡住：

| 動作 | Claude | Gemini / 其他 |
| :--- | :--- | :--- |
| 網路搜尋 | `WebSearch` | `search_web` / `google_search` |
| 抓網頁 | `WebFetch` | `read_url` / `read_url_content` |
| 指令 / 下載 | `Bash`（`curl` 等） | `run_shell_command` |
| 讀寫檔 | `Read` / `Edit` / `Write` | `view_file` / `write_file` / `edit_file` |
| MCP 爬取 | `firecrawl_*`、Bright Data `scrape_as_markdown` / `search_engine`、`mcp__Apify__*`、`mcp__playwright__*` | 已連接的同名 MCP 工具 |

- **內建工具** = `WebSearch` / `WebFetch` / `curl` 這類原生工具；**MCP 工具** = Firecrawl / Bright Data / Apify / Playwright。
- `curl` 一律帶瀏覽器 User-Agent：`-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"`。

---

## 2. 流程總覽

| Phase | 內容 | 執行者 |
| :--- | :--- | :--- |
| 1 | 建立/確認公司資料夾（§6） | 主代理人 |
| 2 | 盤點並下載最新財報（§7） | 每家公司一個子代理人 |
| 3 | 收集近三個月輿情/新聞（§8） | 同上子代理人 |
| 4 | 呼叫 `Convert2md` Skill 轉 Markdown（§9） | 主代理人 |
| 5 | 寫執行報告、維護本 Skill、push（§10、§11） | 主代理人 |

---

## 3. 通用抓取規則（Phase 2、3 共用，全篇唯一抓取標準）

### 3.1 固定順序

1. **先查 §4 站點知識庫**：該站有已驗證的免 MCP 捷徑（官方 API、SSR 頁、替代站），直接用，成功即止。
2. **內建工具**：`curl` / `WebFetch`。
3. **MCP 鏈**：`firecrawl_scrape` → Bright Data `scrape_as_markdown` → Apify → Playwright，依序遞補，任一成功即止。Apify 抓一般網頁用 `apify/rag-web-browser`（`query` 填網址、`maxResults: 1`，一次約 0.01 CU）。

| 規則 | 內容 |
| :--- | :--- |
| 次數上限 | 每個工具最多 2 次（失敗只重試 1 次），然後換下一個；不可對同一工具無限重試 |
| 不可跳過 | 中間的 MCP 不可略過；只有該環境確實沒連上某 MCP 才跳過，並在報告註明「{MCP} 未連線」 |
| 「不支援此站」也算失敗 | 如 Firecrawl 對 `reddit.com` 回「we do not support this site」→ 換下一個，不代表該站抓不到 |
| 整條鏈都不支援 | 改用 MCP 的搜尋功能（`firecrawl_search`、Bright Data `search_engine`）搭 `site:` 取索引 |
| 四個 MCP 都失敗 | 才可放棄該站，照 §8.5 記錄，換下一個來源 |

### 3.2 什麼算「抓取失敗」（→ 往下一步走，不是放棄理由）

- 空白、只剩選單框架、`<title>Document` 之類的 JS 外殼。
- 網站封鎖：`not accessible to our user agent`、HTTP 403 / 429、Cloudflare `Just a moment...`、Akamai `Access Denied`。

**例外：HTTP 404 或「路徑不存在」不是封鎖**，代表站方沒有這個頁面，不必跑 MCP 鏈，直接換來源（§4 有記錄的例子）。

### 3.3 純網路錯誤 → 零重試、直接換來源

`Read Timeout`、連線超過 10 秒、`EOF`、`Connection reset`、`forcibly closed`、`ECONNREFUSED`、`EHOSTUNREACH` 等 socket 錯誤：見到就放棄這個 URL，刪掉殘留暫存檔（如 `.tmp`），換下一個來源。**不可**開背景下載後空等，也不可反覆重試。

### 3.4 帳號級錯誤 → 該 MCP 本次全程停用

| 回應 | 意義 | 處置 |
| :--- | :--- | :--- |
| Firecrawl `HTTP 402` 或 `Insufficient credits` | 額度用盡 | 本次不再呼叫 Firecrawl，改用 Apify `rag-web-browser` |
| Apify `Monthly usage hard limit exceeded` | 月額度用盡 | 本次不再呼叫任何 Actor |
| Bright Data `Residential Failed (bad_endpoint)` | 帳號未完成 KYC | 需 residential 的站（雪球、LIHKG）改走其他 MCP |
| Bright Data `502 origin_bad_gateway` | MCP 閘道故障 | 照 §3.1 試 2 次即換，不要空等 `retry_after` |
| Bright Data `needs you to sign in again` | MCP 授權過期，本次無法自行重新登入 | 本次全程停用，報告註明請使用者重新授權；改走 Apify / Exa |

不要對每個網站重踩同一顆地雷；先找 §4 的免 MCP 替代路徑，也不可因此直接改用搜尋摘要打發。所有帳號級錯誤都寫進 §10 報告的 MCP 紀錄。

### 3.5 請求頻率

- 同一網域兩次請求至少間隔 3 秒。
- 多站輪流抓（A → B → C → A），不要一口氣爬完一站。
- 一般網頁同一網域單次任務最多 5 頁；官方 API 分頁不受此限。

### 3.6 搜尋摘要的使用條件

只有在 §3.1 整條鏈都失敗、或該站在 §4 註明「只能取索引」時，才可用搜尋摘要，且該筆必須加註：「⚠️ 為搜尋索引摘要，非原始頁面逐字引述」。

---

## 4. 站點知識庫（依市場分類）

> 格式：站點 / 網址 | 狀況 | 做法。`[yyyy-mm]` 是最後驗證月份。表內只留「目前仍有效」的做法；過時的寫法依 §11 刪除。

### 4.1 通用 / 英文圈

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| Reddit | 內建工具 400、Firecrawl 不支援、Playwright 與 `search.json` 回 403 | **跳過 §3.1，直接用 Apify Reddit Actor（§5.3）**。Apify 不可用時只能用 Bright Data `search_engine` 取索引並註明 [2026-10] |
| X (Twitter) | 未登入即封鎖：Firecrawl 全引擎失敗、Playwright 被導到登入頁 | 日股先用 Yahoo 株つぶやき（§4.4）。其他用 `firecrawl_search`，query 內寫 `site:x.com`（`includeDomains` 參數會回 0 筆）；Firecrawl 沒額度時用 `WebSearch` 搭 `allowed_domains: ["x.com", "twitter.com"]` 取索引。索引沒有時間時，用網址的 status ID 還原：`(id >> 22) + 1288834974657` 毫秒（UTC） [2026-10] |
| Reuters `reuters.com` | 內建 `WebSearch` 被擋（`allowed_domains` 含 reuters.com 會直接回 400） | `firecrawl_scrape`（basic proxy）可抓公司頁與文章頁全文。Firecrawl 沒額度時用 Exa `web_search_exa` 找轉載頁（`tradingview.com/news/reuters.com,...`、`marketscreener.com`），可取標題與時間，正文多半沒有 [2026-10] |
| Bloomberg | 付費牆，不是封鎖 | 取摘要即可，報告註明「付費牆」 |
| 美股分析師評級 | yfinance `get_recommendations`（`upgrades_downgrades`）可列出券商、評等、目標價與時間，但小型股常回空陣列 | 回空時用 Exa `web_search_exa`（query 寫「{公司名} {代號} stock news {月份年份}」）：會回 MarketBeat 共識稿與 `ad-hoc-news.de` 目標價異動稿全文（兩者皆為自動稿，引用時註明）。細節（理由、EBITDA 預估）用 `WebSearch` 找 `goldesel.de` 德文轉述單篇，`WebFetch` 可讀（頁面自註為 AI 輔助撰寫）；Yahoo `research/reports/ARGUS_*_{毫秒時間戳}` 頁可見 Argus 目標價標題，網址內時間戳即報告日 [2026-10] |
| Seeking Alpha | `firecrawl_scrape` 全引擎失敗 | `firecrawl_search` + `site:seekingalpha.com` + `tbs: qdr:m` 找文章；Firecrawl 沒額度時改用 `WebSearch` 搭 `allowed_domains: ["seekingalpha.com"]`（可排除仿冒 SA 的垃圾頁；不加 domain 限制會混入被入侵的 `.gov.my`、`.ca.gov`、`.edu.tw`，一律排除）。Bright Data `search_engine` 選 `bing` 會回原始 HTML、無法解析，不要用。Bright Data `scrape_as_markdown` 取標題/日期/摘要（第一次常空白，重試 1 次）；Bright Data 不可用時 Apify `apify/rag-web-browser`（`query` 填文章網址）回 200，`markdown` 含發布時間、作者、Summary 與 Quick Insights（`WebFetch` 回 403）[2026-10] |
| MSCI 新聞稿 | `ir.msci.com` 回 Akamai Access Denied | 改抓 `msci.com/downloads/documents/press-releases/media-room/*.pdf`，`curl` + `pdftotext` 可讀全文；PDF 網址用 `WebSearch` 找 [2026-10] |
| Yahoo Finance（美股新聞） | yfinance `get_yahoo_finance_news` 各市場都回「No news found」或誤配同名人物 | **不要用 yfinance 新聞**。改用 `WebFetch` 抓 `finance.yahoo.com/quote/{代號}/news/`（約 12 則標題），單篇文章頁也可讀 [2026-10] |
| `firecrawl_search` 本身 | 一個 query 放多個 `site:` 用 OR 連接會回 0 筆 | 一次只放一個 `site:`，分開查 [2026-10] |

### 4.2 台股

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| 鉅亨網 | 有官方關鍵字 API | **台股新聞與 MOPS 重訊全文第一站**，照 §5.1 [2026-09] |
| 股市爆料同學會 `cmoney.tw/forum/stock/{代號}` | 頁面是空殼，貼文由 API 載入 | **直接打官方 API**，照 §5.2 [2026-07] |
| CMoney Readmo `cmoney.tw/forum/readmo/{uuid}` | SSR，`curl` 可讀，正文在 Nuxt state `content`，JSON-LD 有 `datePublished` | **屬平台 AI 自動生成文章**，引用時標為 AI 內容，不可當網友輿情 [2026-10] |
| MOPS `mops.twse.com.tw` | `curl` 被安全性封鎖頁擋；查詢頁需 JS 表單；Firecrawl 只拿到空表單 | **不要在 MOPS 耗時**：重訊 → §5.1 鉅亨；財報版本核對 → 財報狗 e-report；上櫃進度 → TPEx。真的必要才用 Playwright 表單互動 [2026-09] |
| MOPS 法說會簡報 PDF `mopsov.twse.com.tw/nas/STR/{代號}{yyyyMMdd}M001.pdf` | 不帶 cookie 會拿到封鎖頁或被截斷的 PDF | `curl -sL -c cj -b cj {URL} -o out.pdf`，下載後用 `pdfinfo` 確認完整。簡報連結可從 `poorstock.com/earningcall/{代號}` 取得 [2026-10] |
| 財報狗 `statementdog.com/analysis/{代號}/...` | `curl` 回 202 空內容；Apify `rag-web-browser` 回 202 + `x-amzn-waf-action: challenge`（AWS WAF）；Playwright 回 403 | 只有 `firecrawl_scrape`（basic proxy）可取得完整頁（e-report 能列出 `doc.twse.com.tw` 原始檔名以核對年度/季別）。Firecrawl 沒額度時目前無替代路徑，直接記 ❌（Exa 索引的 e-report 版本落後，不可用來判斷是否有新財報）[2026-10] |
| TPEx 申請上櫃清單 `tpex.org.tw/openapi/v1/tpex_esb_applicant_companies` | JSON API，`curl` 可讀 | 含申請日、審議會日、董事會核准日、主辦承銷商；查興櫃股是否申請轉上櫃用這個 [2026-10] |
| Yahoo 股市 `tw.stock.yahoo.com/quote/{代號}.TW` / `.TWO` | SSR，`curl` 可讀。上市/上櫃股的 `/news` 可讀（HTML 內有文章 URL 與 `pubtime` 毫秒，但兩者在 HTML 中順序不固定）；興櫃股的 `/news` 會 302 回個股頁 | 上市櫃股可當台股新聞備援；**發布時間取各單篇 JSON-LD `datePublished`**，不要按位置配對 `pubtime`。興櫃股「成交」可能是造市商報價、總量可能為 0，判斷價格要同時看總量 [2026-10] |
| 經濟日報 `money.udn.com` | 搜尋頁 `search/result/1001/{關鍵字}` 與單篇 `money/story/{cate}/{id}` 皆 SSR，`curl` 可讀 | 正文在 `article-body__editor`，時間取 JSON-LD `datePublished`。搜尋頁失效時用 `WebSearch` 搭 `site:money.udn.com` 找網址 [2026-10] |
| MoneyDJ `moneydj.com` | 搜尋 `kmdj/search/list.aspx?_QueryType_=NW&_Query_={公司名}` 為 SSR（含到秒的時間）；**少了 `_QueryType_=NW` 會 302 回首頁**；單篇 `kmdj/news/newsviewer.aspx?a={GUID}` 為 SSR | 搜尋也會命中每日「投信買賣超排行」「鉅額交易」，可當籌碼資料，也會命中名稱相近的其他公司，要逐則核對。時間取 JSON-LD `datePublished`、正文取 JSON-LD `articleBody` [2026-10] |
| HiStock `histock.tw/stock/{代號}` | 個股頁 `curl` 可讀；舊討論區 `/stock/{代號}/討論` 404；`news.aspx` 渲染後仍空白 | 只用來取已發行股數、PE/PB、三大法人、融資券、借券；其新聞/重訊區落後數月，不可用來判斷近期公告 [2026-10] |
| 工商時報 `ctee.com.tw/search?q=`、旺得富 `wantrich.chinatimes.com/search?q=` | 搜尋路徑 404（站方沒有此頁） | 不跑 MCP 鏈，用 `firecrawl_search` / Bright Data `search_engine` 搭 `site:` 找個別文章 [2026-10] |
| Dcard | 搜尋 API、Apify `rag-web-browser`、Playwright 皆 403 Cloudflare | `firecrawl_search` + `site:dcard.tw {公司名} {代號}` 取索引（含發文日期）；Firecrawl 沒額度時改用 Exa `web_search_exa` 或 `WebSearch` 索引確認有無新文並依 §3.6 加註 [2026-10] |
| Mobile01 討論串 | `curl`、Playwright 皆 403（Akamai）；Apify `rag-web-browser` 直接給網址 403，但用 Google 搜尋模式（`query` 填關鍵字）曾以 200 取得討論串頁 | `firecrawl_search` + `site:mobile01.com {公司名}` + `tbs: qdr:m` 找文章，再 `firecrawl_scrape` 單篇（含發文時間）；Firecrawl 沒額度時改用 Apify `rag-web-browser` 搜尋模式，或 Exa `web_search_exa` 取索引 [2026-10] |
| yfinance 台股日線（`{代號}.TW` / `.TWO`） | `Date` 欄是前一天 UTC 16:00 | 加 8 小時（即日期 +1）才是台北交易日 [2026-10] |
| Goodinfo `goodinfo.tw` | Bright Data 60 秒逾時 | 用 `firecrawl_search` 取索引，Firecrawl 沒額度時改用 Exa `web_search_exa`，依 §3.6 加註 [2026-10] |
| 券商承銷公告頁（嘉實資訊 iframe） | Firecrawl 只拿到 iframe 外殼 | 新股申購/承銷日程改抓 HiStock 公開申購頁（靜態表格）[2026-09] |

### 4.3 港股 / 中國

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| HKEXnews 披露易 | 有官方 JSON API | **港股財報與公告第一站**，照 §5.4 [2026-09] |
| HKEX 權益披露 `di.hkex.com.hk` | SSR，`curl` 可讀 | 入口 `NSSrchCorpList.aspx?sa1=cl&scsd=dd/mm/yyyy&sced=dd/mm/yyyy&sc={5碼}&src=MAIN&lang=EN` → `NSAllFormList.aspx` → 明細 `NSForm2.aspx` / `NSForm3A.aspx?fn=...`。核實「大股東增持」類新聞最準；交易代碼 3104「Services」是以單位支付酬金，不是自掏腰包買進 [2026-10] |
| 富途新聞列表 `futunn.com/hk/stock/{5碼}-HK/news` | SSR，`curl` 可讀 | 解析 `li.news-item` 的 `news-title`、`news-source` 與時間 span。很多連結只指向騰訊通用殼頁（無文章 ID）。智通回購快訊偶爾漏日，要與 HKEX 翌日披露報表交叉核對 [2026-10] |
| 富途個股頁 `/quote`、`/announcement`、新聞內文 `news.futunn.com/hk/post/*` | JS 外殼；`/community` 導向登入頁 | 內文改用 Playwright 可取全文（MT Newswires 文章仍需登入）[2026-09] |
| AAStocks | 列表 `aastocks.com/tc/stocks/analysis/stock-aafn/{代號}/0/hk-stock-news/1` 為 SSR；`http://` 會 302 | `curl -L` 抓列表；單篇 `.../stock-aafn-con/{代號}/{來源}/{ID}/hk-stock-news` 正文就在 SSR HTML（`og:description` 只有約 50 字，不要只取它）。頁頭附沽空金額與比率 [2026-10] |
| 新浪港股新聞 `stock.finance.sina.com.cn/hkstock/news/{代號}.html` | SSR，最新 | `curl` 可讀 [2026-09] |
| 新浪財經內文 `finance.sina.com.cn`、`t.cj.sina.cn` | 本環境 proxy 持續 `Connection reset` | 依 §3.3 零重試，只引用列表標題 [2026-10] |
| 雪球 `xueqiu.com/S/{代號}` | JS 動態渲染 + WAF；Apify `rag-web-browser` 只拿到 WAF JS 外殼，Playwright 回 HTTP 567「请求异常已被安全策略拦截」（對 AI Agent 限制數小時） | 照 §5.6 [2026-10] |
| 東方財富股吧 `guba.eastmoney.com` | 第一頁是 SSR | 照 §5.5，不需 MCP [2026-09] |
| moomoo 社區/新聞 | 正文 JS 載入 | 走 §3.1 MCP 鏈 |
| LIHKG | `api_v2/thread/search` 直接打回 `error_code 5`；2026-10 起頁面自己發出的 `api_v2/thread/search`、`system/property` 也回 HTTP 503（頁面空白） | Playwright 開 `lihkg.com/search?q={關鍵字}&sort=desc_create_time`，用 `browser_network_requests`（`filter: thread/search`）看頁面 API 狀態；200 時用 `browser_network_request` 讀回應（在頁內自行 `fetch` 仍回 error 5），503 時試 2 次即記 ❌。`browser_network_request` 的 `filename` 只能寫在 repo 內，用完要移出 repo [2026-10] |
| 香港經濟日報 `hket.com` | HTTP 405 真人驗證；搜尋頁 404 | 只能找個別文章 URL |

### 4.4 日股

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| Yahoo!ファイナンス 株つぶやき `finance.yahoo.co.jp/quote/{代碼}.T/post` | SSR，`curl` 可讀 | **日股抓 X 貼文的最佳路徑**：頁面聚合真實 X 貼文，保留 `x.com/{帳號}/status/{id}` 與到分鐘的時間；用 regex `https://x\.com/[A-Za-z0-9_]+/status/[0-9]+` 配對文字，單頁約 8~10 則。限制：① J-REIT 沒有此頁（404，不是封鎖）→ 改用 `firecrawl_search` + `site:x.com`；② 社名是一般名詞的公司（如「光通信」）會混入大量無關貼文與假消息，要逐則核對；③ 常混入「爆上げ」導流垃圾帳號（連到外部「新聞」站），一律排除 [2026-10] |
| Yahoo JP 掲示板 `finance.yahoo.co.jp/quote/{代碼}.T/forum` | SSR，`curl` 一次約 50~60 則，每則有 `/forum/{No}` 網址、分鐘級時間 | `?page=N` 不會翻頁；熱門大型股只涵蓋約 11 小時、冷門股可涵蓋數月 → 報告註明涵蓋區間，用 5ch / 株つぶやき 補足 [2026-10] |
| 株探 `kabutan.jp` | `curl` 可讀 | 個股頁含每週信用餘額；`/stock/news?code={代碼}&nmode=3` 只列開示，可直接找到決算短信（含英文版）。列表連結指向包裝頁 `kabutan.jp/disclosures/pdf/{yyyymmdd}/{id}/`（HTML），PDF 實體網址 `tdnet-pdf.kabutan.jp/{yyyymmdd}/{id}.pdf` 要從該頁取出。**日股找季報最快路徑**。新聞第 1 頁只涵蓋約 1 個月，加 `&page=2` 可再往前約 1.5 個月 [2026-10] |
| みんかぶ `minkabu.jp/stock/{代碼}` | `curl` 405、Apify `rag-web-browser` 405「Human Verification」（AWS WAF）、Playwright 403 | `firecrawl_scrape` 或 Apify `apify/web-fetch` 可讀。有目標株価／株価診断，常與掲示板情緒相反，可當空方對照；J-REIT 顯示「対象外」不可用 [2026-10] |
| 5ch | `find.5ch.net` 已 301 到 `find.5ch.io` | `curl -L "https://find.5ch.io/search?q={公司名}"`（UTF-8）；討論串內文是 Shift_JIS，要 `decode('cp932')`。ニュース速報+／嫌儲 的串標題常誇大，要比對 1 樓轉貼的原始新聞 [2026-10] |
| note `note.com` | API 403/404；搜尋頁 `curl` 只拿到外殼 | `firecrawl_scrape` 抓 `note.com/search?q=…&context=note&mode=search&sort=new`（`waitFor: 3000`），Firecrawl 不可用時改 Apify `apify/web-fetch`（markdown 不含文章網址，要再跑一次 `formats: ["links"]`）；單篇 `curl` 可讀，時間取 JSON-LD `datePublished`；付費文章只取得免費段落 [2026-10] |
| 東洋経済オンライン `toyokeizai.net/articles/-/{id}` | SSR，後段付費；`/search/?q=` 404；四季報 `shikiho.toyokeizai.net` 為 JS 外殼 + 付費 | 找文章用全文搜尋 `toyokeizai.net/list/search?fulltext={關鍵字}`（SSR，`curl` 可讀）；單篇 `curl` 取公開段落與 `datePublished`；付費牆不必跑 MCP 鏈 [2026-10] |
| 日経 `nikkei.com/nkd/company/news/?scode={代碼}&ba=1` | SSR，`curl` 可讀；日期在 `m-listItem_time`，付費文章有標記 | 單篇 `curl` 取 `datePublished` 與導言段；付費牆不必跑 MCP 鏈 [2026-10] |
| E-IR 代管的官網 IR 頁（如小糸 `koito.co.jp/english/ir/info/earningsreport/`） | PDF 連結由 `eir-parts` JS 注入，`curl` 看不到 | Playwright `browser_evaluate` 列出連結；PDF 實體在 `ssl4.eir-parts.net/doc/{代碼}/{tdnet\|yuho_pdf\|…}/{id}/00.pdf`，`curl` 可直接下載（`yuho_pdf` = 有価証券報告書全文）[2026-10] |
| JAPAN-REIT.COM `japan-reit.com/meigara/{代碼}/` | `curl` 回 SSL 憑證鏈錯誤（站方問題，**不可**關閉 TLS 驗證）；`WebFetch` 回 503 | `firecrawl_scrape` 可讀：價格、利回り、排名、近一年日線、銘柄ニュース與開示。`/news/` 404，改用 `/topic/` 或 `/release/` [2026-10] |
| Shared Research `sharedresearch.jp/ja/companies/{代碼}` | J-REIT 回 404（沒有覆蓋） | 小型股常是唯一的第三方研究覆蓋；J-REIT 不必查 [2026-10] |

### 4.5 印尼（美股 ADR 的母股，如 TLK ↔ IDX `TLKM`）

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| CNBC Indonesia `cnbcindonesia.com`、Katadata `katadata.co.id`、Selular.ID `selular.id` | SSR，`curl` 可讀，JSON-LD 有 `datePublished` | 用 `WebSearch`（印尼文關鍵字，如「saham {代號} anjlok」）找網址再 `curl` 單篇；Katadata 是 IDX 公告與券商觀點的主力轉述來源 [2026-10] |
| Stockbit `stockbit.com/symbol/{代號}`、`stockbit.com/post/{id}` | JS 載入 | Exa `web_search_exa`（query 寫「Stockbit stream {代號} diskusi saham {月份年份}」）回傳單篇全文與時間，依 §3.6 標註為索引；Stockbit 自標「Potential Junk」的貼文排除。研究摘要 `snips.stockbit.com` 也在索引內 [2026-10] |
| Reddit 印尼版 | `r/finansial` 搜尋多為無關貼文；Apify 每次約 0.1 美元上限即中止 | 個股討論以 Stockbit 為主，Reddit 只取大盤情緒 [2026-10] |

---

## 5. 已驗證的 API / 站點 SOP

### 5.1 鉅亨網關鍵字 API（台股新聞 + MOPS 重訊全文）

```bash
# 步驟 1：清單（q 可填公司中文名或代號，中文要 URL-encode；limit 上限 100，可加 page=N）
curl -s -A "<UA>" "https://ess.api.cnyes.com/ess/api/v1/news/keyword?q={公司名或代號}&limit=30"
# 步驟 2：單篇全文（SSR）
curl -s -A "<UA>" "https://news.cnyes.com/news/id/{newsId}"
```

- 公司名、代號、常用簡稱（如 `AES-KY` 與 `AES`）各查一次，用 `newsId` 去重（代號常命中盤後速報，公司名常命中重訊；代號索引可能落後數週，不可只查代號）。
- `items` 欄位：`newsId`、`title`、`summary`、`publishAt`（**秒級** timestamp，不要除以 1000）、`category[].name`（`台股公告` = MOPS 重訊轉載）。
- 用中文名查時 `title` / `summary` 會被包上 `<mark>`，寫檔前用 regex 移除 `</?mark>`。
- 全文取頁面 JSON-LD 的 `"articleBody"`（純文字）。引用網址：`https://news.cnyes.com/news/id/{newsId}`。
- `api.cnyes.com/media/api/v1/newspage/{newsId}` 已失效，不要用。查不到時改用較短的簡稱或代號。
- 超出三個月的項目不必抓全文。

### 5.2 股市爆料同學會（CMoney）官方 API

```bash
# 步驟 1：訪客 token（免登入，access_token 效期約 24 小時）
curl -s -X POST "https://www.cmoney.tw/api/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=guest&client_id=cmstockcommunity-web"
# 步驟 2：貼文列表（X-Version: 3.0）
curl -s "https://www.cmoney.tw/api/mach/api/Article/Stocks/{代號}/AllLatest?fetchCount=20" \
  -H "Authorization: Bearer {access_token}" -H "X-Version: 3.0"
# 步驟 3：留言（X-Version: 2.0，參數是 fetch/offset）
curl -s "https://www.cmoney.tw/api/mach/api/Article/{文章id}/Comments?fetch=50&offset=0" \
  -H "Authorization: Bearer {access_token}" -H "X-Version: 2.0"
```

- 回傳 `{articles, hasNext, nextCursor}`；**分頁只能用 `&cursor={nextCursor}`**（`skipCount`/`offset` 無效，會一直回同一頁），並用 `id` 去重。
- 型別段：`AllLatest`（抓輿情用）、`AllHottest`、`news`。美股端點 `.../Article/USStocks/{代號}/{型別}`（未逐一驗證）。
- 欄位：`id`、`content.text`、`createTime`（**毫秒**，要除以 1000）、`commentCount`、`emojiCount`。原文網址：`https://www.cmoney.tw/forum/article/{id}`。
- 只對 `commentCount > 0` 的文章抓留言。

| 症狀 | 修法 |
| :--- | :--- |
| 回 HTML 而不是 JSON | base 必須是 `www.cmoney.tw/api/mach/api/...` |
| 400 `UnsupportedApiVersion` | 補 `X-Version`（列表 3.0、留言 2.0） |
| 401 | 缺 Bearer 或 token 過期 → 重拿 token |
| 400 `不支援的類型` | 型別段拼錯 |
| 每頁內容都一樣 | 改用 `cursor` 分頁 |

### 5.3 Reddit（Apify Actor `trudax/reddit-scraper-lite`）

```json
{
  "actor": "trudax/reddit-scraper-lite",
  "input": {
    "searches": ["{代號}", "{公司英文全名}"],
    "searchCommunityName": "wallstreetbets",
    "searchPosts": true,
    "sort": "new",
    "maxItems": 10,
    "maxPostCount": 10
  },
  "waitSecs": 45,
  "callOptions": { "maxTotalChargeUsd": 0.1 }
}
```

- `callOptions.maxTotalChargeUsd` **必填**，低於 0.04 會報 `less than the allowed minimum`。
- `searchCommunityName` 依序試 `wallstreetbets`、`stocks`、`investing` 或產業版。
- **關鍵字不可用泛用詞**（如單獨的 `stock` 會抓到卡車避震、商品補貨）。短代號（如 `UHS`）也常誤配，要再用公司全名搜一次，逐則核對是否真與該公司相關。
- 回 `RUNNING` 也不用等：直接拿 `datasetId` 呼叫 `get-dataset-items`（`fields: "title,communityName,url,createdAt,username,body"`）。
- 排除 `AutoModerator` 制式文、純表情回覆、標題與內文都沒提到該公司的貼文。
- Actor 下架時，用 Apify Actor 搜尋 `Reddit`，挑月用量高、有評分的替代品。

### 5.4 HKEXnews 官方 JSON API（港股財報/公告）

1. `https://www1.hkexnews.hk/search/prefix.do?callback=c&lang=EN&type=A&name={代號}` → 取得 `stockId`。
2. `https://www1.hkexnews.hk/search/titleSearchServlet.do?sortDir=0&sortByOptions=DateTime&category=0&market=SEHK&stockId={stockId}&documentType=-1&fromDate={yyyyMMdd}&toDate={yyyyMMdd}&lang=EN&searchType=1`
   - servlet 名稱**大小寫敏感**，必須是 `titleSearchServlet.do`（全小寫回 404）。
   - 不要帶 `t1code` / `t2Gcode` / `t2code`；若一定要帶，值是 `-2`（填 `-1` 會讓任何查詢都回 0 筆）。
3. `lang=ZH` 取中文版；`recordCnt: 0` 代表該期間確實沒有公告。中文 PDF（檔名 `_c.pdf`）用 `pdftotext` 常因缺 Adobe-GB1 字型解析失敗 → 改用 `lang=EN` 回傳的英文版 `FILE_LINK`（同編號去掉 `_c`）。
4. PDF 連結 = `https://www1.hkexnews.hk` + `FILE_LINK`。

### 5.5 東方財富股吧（A 股代碼）

- 列表：`curl -A "<UA>" https://guba.eastmoney.com/list,{A股代碼}.html`，頁內 `var article_list = {...}` 含約 40 筆（`post_id`、`post_title`、`post_publish_time`、點閱/留言數）。
- 單篇：`https://guba.eastmoney.com/news,{A股代碼},{post_id}.html`，用 `json.JSONDecoder().raw_decode` 解析 `post_article` 之後的 JSON，取 `post_content`。連續抓取時部分單篇會回約 2.8KB 空殼（無 `post_article`）→ 帶 `Referer: https://guba.eastmoney.com/list,{代碼}.html`、間隔 4 秒重試 1 次即可。
- 港股也有股吧：代碼寫 `hk{5碼}`（如 `list,hk00546.html`），格式同上 [2026-10]。

### 5.6 雪球

1. 先用 Bright Data `scrape_as_markdown` 抓 `https://xueqiu.com/S/{代號}`（雪球用 Bright Data 成功率最高，可跳過內建工具）。
2. Bright Data 失敗或回 `bad_endpoint`（KYC）→ `firecrawl_scrape` 搭 `proxy: stealth`，再依序 Apify → Playwright。
   - 整條鏈都失敗時，用 Exa `web_search_exa`（query 寫「雪球 {公司名} {代號} 讨论 {年月}」）：它回傳雪球單篇頁的索引全文，含「发布于 YYYY-MM-DD HH:MM」、回覆數與部分留言，比搜尋摘要完整；仍依 §3.6 標註為索引。要逐則確認是否屬該公司（留言頁常是其他個股的討論串）。
3. 雙重上市公司的 A 股頁（`SH601318`）與 H 股頁（`02318`）互為備援。
4. **時間要校準**：討論流顯示相對時間，且 Firecrawl 渲染時區是 `America/New_York`；一律以單篇頁的「发布于 YYYY-MM-DD HH:MM」（北京時間）為準。
5. 只抓討論，不從雪球抓財報。

---

## 6. Phase 1 — 建立資料夾

- 台/日/港股：`FinancialReport/{代碼}{名稱}/`（例：`2881富邦金/`）；美股：`FinancialReport/{代碼}/`（例：`UHS/`）。
- 若 `Routines_CollectsentimentAndReports.md` 輪替表有寫資料夾名稱，以表上為準。不存在就建立。

---

## 7. Phase 2 — 最新財報

目標：最新 **2 份年報 + 1 份季報**（只有半年報的公司，用最新半年報代替季報）。找到一份就下載、驗證、存檔，再找下一份。

### 7.1 先盤點，再下載

列出資料夾既有檔案，用檔名判斷已涵蓋哪些期別，**已有的直接跳過**。新檔一律用統一命名：

| 類型 | 命名 | 範例 |
| :--- | :--- | :--- |
| 年報 | `{TICKER}_AnnualReport_{FY}.{ext}` | `5306_AnnualReport_2025.pdf` |
| 季報 | `{TICKER}_Quarter_{FY}Q{N}.{ext}` | `5306_Quarter_2026Q2.pdf` |
| 半年報 | `{TICKER}_Quarter_{FY}H1.{ext}` | `2245_Quarter_2026H1.pdf` |

- `{FY}` 是財報所屬的年度/期間，不是申報日或下載日；檔名不要加時間戳或表單代碼。
- 舊檔名不強制改名，但盤點時要認得：`{TICKER}_annual_{FY}`、`{TICKER}_quarter_{FY}Q{N}`、`{TICKER}_interim_{FY}`、台股 `{FY}_{TICKER}_{申報日}F04/FE4`（年報）、`{yyyyMM}_{TICKER}_AI1`（季報）、美股 `{TICKER}_10K_{期末日}` / `{TICKER}_10Q_{期末日}`、日股 `有価証券報告書`、`決算短信`。
- 已有 `.md` 的期別視為已下載，不必再抓 PDF。

### 7.2 下載驗證（每份下載完立刻做）

| 檢查 | 不合格處置 |
| :--- | :--- |
| 檔案 < 10KB | 刪除，換來源 |
| 前 4 頁沒有公司名稱或代碼 | 刪除，換來源 |
| 用  `convert_pdf_to_markdown`試轉，`(cid:` ≥ 50 次或佔比 ≥ 5% | 字型缺字，無法修復 → 刪除，改抓英文版或換來源 |
| 網路錯誤 | 照 §3.3 |

- **英文版優先**：台股 MOPS 中文 PDF 常有 `(cid:` 亂碼，英文版通常乾淨。
- 保留原始副檔名（`.pdf` / `.html`），不要手動改成 `.md`。

### 7.3 搜尋來源（依序，找到即停）

- **台股**：① MOPS/TWSE（英文年報 `_AIA.pdf`；季報多只有中文 `_AI1.pdf`）② 財報狗 e-report（§4.2）③ 官網 IR。想確認「是否已公告」用 §5.1 鉅亨（它給的是重訊全文，不是財報 PDF）。興櫃公司只有半年報與年報，不會有 Q1/Q3。
- **美股**：① 官網 IR（SEC Filings）② SEC EDGAR（可用 `sec-edgar-mcp`）③ 財報狗 ④ 富途 `futunn.com/hk/stock/{代號}-US/announcement`。外國發行人（ADR）年報是 20-F、季報夾在 6-K 裡：`curl -A "{名稱} {email}" https://data.sec.gov/submissions/CIK{10碼}.json` 列出所有申報，再用 `.../Archives/edgar/data/{CIK}/{去掉 - 的 accession}/index.json` 看附件，6-K 主文件開頭會寫 "Consolidated financial statements as of …" 即為季報。
- **日股**：① 官網 IR（英文 Annual Report 優先）② 株探開示清單（§4.4，決算短信最快）③ EDINET ④ IR Bank `irbank.net/{代碼}/ir` ⑤ 富途 `{代碼}-JP/announcement`。J-REIT 的經審計英文財報常在官網英文 IR 庫，無 cid 問題：ES-CON（2971）`escon-reit.jp/en/ir/library.html` 的「Asset Management Reports」欄；HCM（3455）`hcm3455.co.jp/en/ir/library.html` 的「Semi-annual report」欄。決算後約 1 個月內英文頁常只有 Summary of accounts，簡報要到日文頁抓；頁頂「As of …」日期不會更新，不能拿來判斷新舊。
- **港股**：① HKEXnews JSON API（§5.4）② 富途 `{5碼}-HK/announcement` ③ 官網 IR。（新浪 `/hkstock/notice/` 公告頁已停更，不要用）

---

## 8. Phase 3 — 近三個月輿情/新聞

### 8.1 存檔規則

- 檔名：`FinancialReport/{資料夾}/{yyyyMM}_輿情新聞.md`（`yyyyMM` = 執行當月），一個月一檔、所有來源合併。
- **Append 模式**：檔案不存在 → 建立並寫標頭；來源章節不存在 → 在末尾新增 `## [來源名稱]`；章節已存在 → 補在該章節末尾。不可覆蓋舊內容。
- 每抓完一個來源就立刻寫入。
- 開始前先讀資料夾內的 `{YYYY}_PublicOpinion.md`（`ArrangePublicOpinionMd` 合併後的年度檔）與當月檔，確認上次收集到哪一天，只補新內容，避免重複。

### 8.2 來源（依市場，抓不到照 §3 處理，不可當成「沒資料」略過）

- **台股**：鉅亨網（§5.1）、MoneyDJ、經濟日報、PTT 股市板、Dcard、Mobile01、股市爆料同學會（§5.2）、財報狗社群、HiStock、TPEx（興櫃股）。
- **美股**：Yahoo Finance（§4.1）、Reuters、Bloomberg、Seeking Alpha、Reddit（§5.3）、X。ADR 的母股市場另查 SEC 6-K（母國公告英文版）與母國媒體/社群（印尼見 §4.5）。
- **港股 / 中國**：富途、AAStocks、新浪港股新聞、HKEX 權益披露、雪球（§5.6）、東方財富股吧（§5.5）、moomoo、LIHKG、香港經濟日報。
- **日股**：日經、Yahoo JP 掲示板與株つぶやき、株探、みんかぶ、5ch、note、Shared Research、東洋経済；J-REIT 加 JAPAN-REIT.COM。
- 雙重上市公司（如港股 + A 股、日股 + 美股 ADR）主市場來源不足時，再查另一邊市場的來源。

### 8.3 過濾規則

1. 只記錄實質的基本面/事件/觀點；略過純漲跌數字、表情符號。
2. 每筆都要和該公司直接相關；排除標題與內文都沒提到公司或代號的貼文、媒體網站自我介紹文、仿冒/垃圾站。
3. 要寫出原作者的核心論點與細節，不能只貼網址。
4. 平台 AI 生成的內容（如 CMoney Readmo）要標明「AI 生成」，不可當網友輿情。
5. 遇到明顯誇大或與官方資料矛盾的說法，可註明「與 {官方來源} 不符」，但不可自行改寫原文。

### 8.4 範本

````markdown
# [{代碼} {公司名稱}] 輿情與新聞整理 ({YYYY}/{MM})

- **分析月份**：YYYY/MM
- **資料範圍**：YYYY-MM-DD ~ YYYY-MM-DD
- **最後更新**：YYYY-MM-DD HH:MM

---

## [來源名稱]

- **抓取時間**：YYYY-MM-DD
- **抓取方式**：{實際成功的工具，如 curl 官方 API / firecrawl_scrape}
- **抓取結果**：✅ 成功 / ⚠️ 僅索引摘要 / ❌ 失敗 / ⭕ 無新內容

### 🎯 [主題]
- **來源連結**：[標題](真實 URL)
- **發布時間**：YYYY-MM-DD HH:MM（頁面上真實顯示的時間）
- **核心觀點**：
  > "原文引述"
- **關鍵要點**：
  - 重點 A（細節與原因）
  - 重點 B（市場看法）
````

### 8.5 失敗與無新內容的寫法（不可留空章節）

````markdown
## [東方財富股吧]

- **抓取時間**：YYYY-MM-DD
- **抓取結果**：❌ 失敗
- 已嘗試：curl → JS 外殼；firecrawl_scrape → 403；Bright Data → 逾時；Apify → 不支援；Playwright → 登入牆
- **結論**：本次無法取得真實輿情，非 AI 生成，下次重試。
````

查得到站但三個月內沒有該公司新內容時，結果寫 `⭕ 無新內容`，並寫明搜尋方式（關鍵字、頁面），讓下次知道這個來源已查過。

---

## 9. Phase 4 — 轉 Markdown

- Phase 2 有新下載 PDF 時，主代理人呼叫 **`Convert2md` Skill**（用 `convert_pdf_to_markdown` 轉 PDF，自動刪除 CID 亂碼失敗檔）。
- `convert_pdf_to_markdown` 輸出的 `.md` 會含指向暫存 `pdf_images/` 的圖片連結，暫存圖刪除後會失效 → 轉檔後移除 `![](…/pdf_images/…)` 行。
- `Convert2md` **只處理 PDF**。若下載的是 HTML（如 SEC 10-K/10-Q），要自己轉成同檔名 `.md`，移除 XBRL/iXBRL 標籤與內嵌 blob，確認正文可讀後再刪原始 HTML。
- 沒有新檔就略過，並在報告註明。

---

## 10. Phase 5 — 執行報告與 push

報告寫到 `FinancialReport/Log/CollectsentimentAndReports_Summary_{yyyyMMdd}.md`（一次性報告，檔名要加日期）。

````markdown
# 任務執行最終報告 - YYYY/MM/DD

- **執行日**：YYYY-MM-DD（輪替表第 N 日 → {代碼} {名稱}）
- **公司資料夾**：`{資料夾}/`

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |

**本期重點**：（條列近三個月的關鍵事件與輿情；提到金額時附每股金額）

## 2. 失敗或被擋網站
- **來源**：[網站](URL)｜**原因**：{403 / 逾時 / 付費牆…}｜**已試過**：{實際試過的工具}

## 3. 資料缺失說明
（如：財報尚未公布、興櫃只有半年報、冷門股無討論）

## 4. 異常檔案刪除紀錄
（< 10KB、無公司名稱、`(cid:` 亂碼等被刪的檔案；沒有就寫「無」）

## 5. 本次使用的 MCP
| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
（用人類可讀名稱，如 Firecrawl、Bright Data、Apify、Playwright、yfinance；帳號級錯誤也寫在這裡。完全沒用 MCP 就寫「本次未使用 MCP，僅用 {內建工具}」）

## 6. Phase 4 Convert2md
## 7. Skill 維護
（本次新增、修改、刪除了哪些 §4 / §5 內容；沒有就寫「無」）
````

> [!IMPORTANT]
> **報告寫完後，必須把所有新增與變更的檔案 commit 並 push 到 `master`，任務才算完成。不可因分支限制停下來詢問使用者。**

---

## 11. Skill 維護規則（每次更新本 Skill 都要做）

執行中發現新的網站行為（新封鎖、新 API、新捷徑、舊做法失效）時，在 Phase 5 更新本 Skill，**並同時做以下清理**：

1. **加到正確位置**：網站行為放 §4 對應市場的表格（一個站點一列）；多步驟的 API 用法放 §5。不要另開新段落或在別處重寫抓取規則。
2. **合併而不是追加**：同一站點已有一列時，直接改寫那一列，更新 `[yyyy-mm]`；不可再新增一列「補充」或「追蹤」。
3. **刪除無用資料**：
   - 已失效的做法、已被新做法取代的舊寫法、改版前的網址 → 刪除。
   - 重複的說明、與 §3 通用規則重複的敘述 → 刪除。
   - 一次性的除錯過程、實測流水帳（某天抓到幾筆、檔案多大）、指向已不存在檔案的連結 → 刪除，只留結論。
   - 環境設定細節（如 Playwright 啟動器原理）不寫在這裡；需要時看 `.claude/scripts/playwright-mcp.mjs` 開頭註解。
4. **檢查一致性**：確認內文的 § 編號引用都還對得上；`gemini/gemini_CollectsentimentAndReports.md` 若有引用本 Skill 的章節，一併更新。
5. **兩份同步**：`.claude/skills/CollectsentimentAndReports/SKILL.md` 與 `.agents/skills/CollectsentimentAndReports/SKILL.md` 內容必須完全相同（改完用 `diff` 確認）。
6. 在 §10 報告的「Skill 維護」寫明本次新增、修改、刪除了什麼。

