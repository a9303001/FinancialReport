---
name: collectStk
description: 收集個股「最新財務報告（2 年報 + 1 季報）」與「近三個月輿情討論/新聞」，存入公司資料夾，轉 Markdown 後產出執行報告並 push。輸入 COMPANY_TICKER 與 COMPANY_NAME。開工先做 MCP 預檢（§3.0）：Firecrawl／Bright Data 等連接器若被「需要核准」擋住，自動改走替代路徑並在報告寫明使用者修法。（舊名 CollectsentimentAndReports）
---
/goal
# collectStk — 執行指南

> **任務**：對指定公司 ⓪ 預檢 MCP → ① 補齊最新財報（2 份年報 + 1 份季報）→ ② 收集近三個月輿情/新聞 → ③ 轉 Markdown → ④ 寫執行報告並 push。
> 適用所有 AI（Claude / Gemini，含輕量模型）。照章節順序一步一步做，不要跳步。

## 0. 五條底線（違反任一 = 任務失敗）

1. **防幻覺**：只記錄真實抓到的內容，附真實 URL 與真實發布時間。抓不到就照 §8.5 誠實記錄，**嚴禁**用訓練資料補內容、捏造連結或推測日期。
2. **不從本 repo 的線上倉庫收集**：嚴禁從 GitHub `a9303001/FinancialReport` 下載財報或新聞；嚴禁訪問 `macrotrends.net`。（本機資料夾已有的檔案可盤點與回查，見 §7.1、§8.3）
3. **即時存檔**：每下載完一份財報、每抓完一個來源，立刻寫檔。
4. **不卡死**：抓取照 §3 的固定順序與次數上限，不無限重試、不空等背景任務；預檢判定停用的 MCP 整輪不再呼叫。
5. **不碰帳號設定**：連接器權限、登入、額度只有使用者能改。AI 只負責偵測、改走替代路徑、在報告寫明修法（§3.0.3）。

---

## 1. 參數與工具

| 參數 | 說明 | 範例 | 若缺失 |
| :--- | :--- | :--- | :--- |
| `COMPANY_TICKER` | 股票代碼（港股補齊 5 碼） | `2881`、`UHS`、`3445`、`02318` | 必填，立刻詢問 |
| `COMPANY_NAME` | 公司名稱 | `富邦金`、`Universal Health Services` | 用代碼搜尋查出 |

工具名一律視為「動作」，用你手上對應的工具完成，名字對不上不要卡住：

| 動作 | Claude | Gemini / 其他 |
| :--- | :--- | :--- |
| 網路搜尋 | `WebSearch` | `search_web` / `google_search` |
| 抓網頁 | `WebFetch` | `read_url` / `read_url_content` |
| 指令 / 下載 | `Bash`（`curl` 等） | `run_shell_command` |
| 讀寫檔 | `Read` / `Edit` / `Write` | `view_file` / `write_file` / `edit_file` |
| MCP 爬取 | `firecrawl_*`、Bright Data `scrape_as_markdown` / `search_engine`、`mcp__Apify__*`、`mcp__playwright__*`、Exa `web_search_exa` | 已連接的同名 MCP 工具 |

- **內建工具** = `WebSearch` / `WebFetch` / `curl` 這類原生工具。
- `curl` 一律帶瀏覽器 User-Agent（下文寫 `<UA>`）：`-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"`。
- Claude 的 MCP 工具若是延遲載入（deferred），先用 `ToolSearch`（如 `select:mcp__brightdata__scrape_as_markdown`）載入再呼叫；搜不到才算「環境沒連上」。

MCP 分兩類，故障原因與修法不同：

| 類型 | 成員 | 設定位置 | 常見故障 |
| :--- | :--- | :--- | :--- |
| 本機 MCP | Playwright、yfinance、sec-edgar-mcp、pymupdf4llm-mcp（`convert_pdf_to_markdown`） | repo `.mcp.json`（與 `.claude/mcp_config.json` 同內容），session 啟動時在本機起程序 | 啟動失敗、逾時 |
| claude.ai 連接器 | Firecrawl、Bright Data、Apify、Exa | 使用者 claude.ai 帳號的 Connectors 設定，**每個工具各自有權限** | 跳出核准卡片／`MCP tool call requires approval`、需重新登入、額度用盡 |

---

## 2. 流程總覽

| Phase | 內容 | 執行者 |
| :--- | :--- | :--- |
| 0 | MCP 預檢，建立本輪「可用工具表」（§3.0） | 主代理人 |
| 1 | 建立/確認公司資料夾（§6） | 主代理人 |
| 2 | 盤點並下載最新財報（§7） | 主代理人（多家公司時每家一個子代理人） |
| 3 | 收集近三個月輿情/新聞（§8） | 同上 |
| 4 | 呼叫 `Convert2md` Skill 轉 Markdown（§9） | 主代理人 |
| 5 | 寫執行報告、維護本 Skill、push（§10、§11） | 主代理人 |

---

## 3. 通用抓取規則（Phase 2、3 共用，全篇唯一抓取標準）

### 3.0 Phase 0 — MCP 預檢（開工前必做，約 1 分鐘）

#### 3.0.1 怎麼測

**測「真正要用的抓取工具」**，不要測統計／目錄類工具：連接器權限是逐工具設定，`session_stats`、`search-actors` 能用不代表 `scrape_as_markdown`、`apify--web-fetch` 能用。

同一則回應內平行送出（目標都用 `https://example.com`，花費最低）：

| MCP | 探測呼叫 | 成功判準 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape`（url `https://example.com`、`formats: ["markdown"]`） | 回傳含 `documentation examples`，或 `metadata.title` 為 `Example Domain` |
| Bright Data | `scrape_as_markdown`（同上） | 回傳 `title` 為 `Example Domain` |
| Apify | `apify--web-fetch`（`GET /`，query `url=https://example.com`）；沒有此工具就用 `call-actor` 跑 `apify/rag-web-browser` | 同上 |
| Exa | `web_search_exa`（`numResults: 1`，查該公司名） | 有結果 |
| Playwright | `browser_navigate` 到 `https://example.com` | 頁面標題 `Example Domain` |
| yfinance | `get_historical_stock_prices`（該公司代碼、`period: 5d`） | 有資料（順便取最新價） |

#### 3.0.2 怎麼判讀（帳號級錯誤 → 該 MCP 本輪全程停用）

| 回應 | 意義 | 本輪處置 |
| :--- | :--- | :--- |
| 成功 | 可用 | 列入可用工具表 |
| 跳出核准卡片（互動式 session） | 該工具在 claude.ai 被設成「需要核准」 | 使用者按下允許就繼續用；報告仍照 §3.0.3 提醒改成一律允許，否則排程執行會失敗 |
| `MCP tool call requires approval`（排程／無人值守） | 同上，但沒有人能按核准 | 停用該 MCP；**不要重送、不要換同連接器的其他抓取工具硬試**（通常整組一起被擋）；照 §3.0.4 走替代路徑 |
| `needs you to sign in again`、`Customer is not active`、401 | 連接器授權過期或帳號停用 | 停用，報告請使用者重新登入／檢查帳號 |
| Firecrawl `HTTP 402`、`Insufficient credits` | 額度用盡 | 停用 Firecrawl |
| Apify `Monthly usage hard limit exceeded` | 月額度用盡 | 停用所有 Actor |
| Bright Data `Residential Failed (bad_endpoint)` | 帳號未完成 KYC | 只停用需要 residential 的站（雪球、LIHKG），其他照用 |
| Bright Data `502 origin_bad_gateway` | 閘道暫時故障 | 不算帳號級；照 §3.1 試 2 次即換，不空等 `retry_after` |
| 雲端代理回 `connect_rejected`（`curl` rc=56，host 未放行） | 環境網路政策擋直連，不是網站封鎖 | 本輪 `curl` 直連改走 MCP；新聞與公告頁用 `firecrawl_scrape` 搭 `formats: ["query"]` + `queryOptions.mode: directQuote` 只取正文；財報 PDF 無法落地時，報告列出檔名與下載網址供下次補抓 |

預檢結果寫成一行並寫進報告 §5，例：`可用：Firecrawl、Bright Data、Exa、Playwright、yfinance、curl｜停用：Apify（Monthly usage hard limit exceeded）`。

#### 3.0.3 「需要核准」的根因與修法（寫進報告給使用者；AI 不可自行處理）

- **根因**：claude.ai 連接器的工具權限設成「需要核准（Needs approval）」時，claude.ai 會把 `always_ask` 政策推給 session。這一層高於 repo 設定：`.claude/settings.json` 的 `permissions.allow`（已含 `mcp__*`、`mcp__brightdata__*`、`mcp__firecrawl-mcp__*`）與 `PermissionRequest` 自動允許 hook 都管不到；雲端 session 也會忽略 `defaultMode: bypassPermissions`。**不要再為此改 repo 設定。**
- **修法（使用者做一次，之後所有雲端與排程執行都生效）**：開 `https://claude.ai/customize/connectors` → 點 **Firecrawl** → 工具權限（Tool permissions）設為「一律允許（Always allow）」；**Bright Data**、**Apify**、**Exa** 同樣處理。可直接整個連接器設一律允許；最少要開：Firecrawl `firecrawl_scrape`、`firecrawl_search`；Bright Data `scrape_as_markdown`、`search_engine`；Apify `apify--web-fetch`、`call-actor`、`get-dataset-items`；Exa `web_search_exa`。選項是灰的 = 組織管理員鎖住，要請管理員開。
- **需重新登入**：同一頁面點該連接器重新連線。
- **額度**：到該服務後台加值或等下個計費週期。
- [2026-11-23] 雲端互動 session 實測：`firecrawl_scrape` 與 Bright Data `scrape_as_markdown` 皆回傳成功；排程執行若仍回 `requires approval`，就是上述連接器權限尚未改成一律允許。

#### 3.0.4 連接器被停用時的替代路徑

| 停用 | 改走 |
| :--- | :--- |
| 只有 Firecrawl | 鏈上改 Bright Data → Apify `rag-web-browser` → Playwright；`site:` 索引改 Bright Data `search_engine` 或 `WebSearch` |
| Firecrawl＋Bright Data＋Apify 全停 | ① §4、§5 的免 MCP 捷徑（官方 API、SSR 頁、`curl`）照常是第一站：港股 HKEX／AAStocks／新浪／股吧、台股鉅亨／CMoney、日股株探／Yahoo JP 都不受影響 ② JS 頁改 Playwright（富途新聞、moomoo、LIHKG 已驗證）③ Playwright 也被擋的站（雪球 567、X 登入牆、Dcard、Mobile01、Seeking Alpha）改 Exa `web_search_exa` 取索引，依 §3.6 標註 ④ `site:` 搜尋改 `WebSearch`（`allowed_domains`）⑤ Reddit 只能 `WebSearch` 搭 `allowed_domains: ["reddit.com"]` 取索引 |
| Exa 也停 | 索引只剩 `WebSearch`；雪球記 ❌ 並寫明原因 |

### 3.1 固定順序

1. **先查 §4 站點知識庫**：該站有已驗證的免 MCP 捷徑（官方 API、SSR 頁、替代站），直接用，成功即止。
2. **內建工具**：`curl` / `WebFetch`。
3. **MCP 鏈**：`firecrawl_scrape` → Bright Data `scrape_as_markdown` → Apify → Playwright，依序遞補，任一成功即止；**預檢停用的直接略過**。Apify 抓一般網頁用 `apify--web-fetch` 或 `apify/rag-web-browser`（`query` 填網址、`maxResults: 1`，一次約 0.01 CU）。
4. **索引**：整條鏈失敗、或 §4 註明「只能取索引」→ `firecrawl_search` / Bright Data `search_engine` / Exa `web_search_exa` / `WebSearch`（搭 `site:` 或 `allowed_domains`），依 §3.6 標註。

| 規則 | 內容 |
| :--- | :--- |
| 次數上限 | 每個工具最多 2 次（失敗只重試 1 次），然後換下一個 |
| 不可跳過 | 可用的 MCP 不可略過；只有預檢停用或環境沒連上才跳過，並在報告註明 |
| 「不支援此站」也算失敗 | 如 Firecrawl 對 `reddit.com` 回「we do not support this site」→ 換下一個，不代表該站抓不到 |
| 執行中才出現帳號級錯誤 | 依 §3.0.2 立刻停用該 MCP，整輪不再呼叫 |
| 可用工具全失敗 | 才可放棄該站，照 §8.5 記錄，換下一個來源 |

### 3.2 什麼算「抓取失敗」（→ 往下一步走，不是放棄理由）

- 空白、只剩選單框架、`<title>Document` 之類的 JS 外殼。
- 網站封鎖：`not accessible to our user agent`、HTTP 403 / 429 / 567、Cloudflare `Just a moment...`、Akamai `Access Denied`。
- **例外：HTTP 404 或「路徑不存在」不是封鎖**，代表站方沒有這個頁面，不必跑 MCP 鏈，直接換來源。

### 3.3 純網路錯誤 → 零重試、直接換來源

`Read Timeout`、連線超過 10 秒、`EOF`、`Connection reset`、`forcibly closed`、`ECONNREFUSED`、`EHOSTUNREACH` 等 socket 錯誤：放棄這個 URL，刪掉殘留暫存檔（如 `.tmp`），換下一個來源。**不可**開背景下載後空等，也不可反覆重試。

### 3.4 Playwright 收尾

Playwright 的 snapshot、console log 會寫進 repo 根目錄 `.playwright-mcp/`；`browser_network_request` 的 `filename` 也只能寫在 repo 內。需要的內容移出後，**push 前刪除 `.playwright-mcp/`**。

### 3.5 請求頻率

- 同一網域兩次請求至少間隔 3 秒；多站輪流抓（A → B → C → A）。
- 一般網頁同一網域單次任務最多 5 頁；官方 API 分頁不受此限。

### 3.6 搜尋摘要的使用條件

只有 §3.1 可用工具都失敗、或 §4 註明「只能取索引」時，才可用搜尋摘要，且該筆必須加註：「⚠️ 為搜尋索引摘要，非原始頁面逐字引述」。索引標示的日期不等於發布日（新聞農場會把舊聞標成當天，見 §4.3），要用原文或官方資料核對。

---

## 4. 站點知識庫（依市場分類）

> 格式：站點 / 網址 | 狀況 | 做法。`[yyyy-mm]` 是最後驗證月份。表內只留「目前仍有效」的做法；過時的寫法依 §11 刪除。

### 4.1 通用 / 英文圈

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

### 4.2 台股

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| 鉅亨網 | 有官方關鍵字 API | **台股新聞與 MOPS 重訊全文第一站**，照 §5.1 [2026-09] |
| 股市爆料同學會 `cmoney.tw/forum/stock/{代號}` | 頁面是空殼，貼文由 API 載入 | **直接打官方 API**，照 §5.2。`curl` 無法出站時改 `firecrawl_scrape`（`waitFor: 4000`、`formats: ["query"]` directQuote）可取首屏約 8 則（作者、時間、內文、`forum/article/{id}` 網址），無法翻頁；確切時間取單篇頁 meta `publishedTime`（+08:00）[2026-11] |
| CMoney Readmo `cmoney.tw/forum/readmo/{uuid}` | SSR，`curl` 可讀，正文在 Nuxt state `content`，JSON-LD 有 `datePublished` | **屬平台 AI 自動生成文章**，引用時標為 AI 內容，不可當網友輿情 [2026-10] |
| MOPS `mops.twse.com.tw` | `curl` 被安全性封鎖頁擋；查詢頁需 JS 表單；Firecrawl 只拿到空表單 | **不要在 MOPS 耗時**：重訊 → §5.1 鉅亨；財報版本核對 → 財報狗 e-report；上櫃進度 → TPEx。真的必要才用 Playwright 表單互動 [2026-09] |
| TWSE 電子書 `doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id={代號}&year={民國年}&seamon=&mtype=A&` | **依來源 IP 封鎖**：雲端容器出口是 Google Cloud 美國 IP（AS396982），`curl` 不論帶什麼 header／cookie／UA，清單頁、step=9、`/pdf/*.pdf` 一律回 947 bytes「因為安全性考量…FOR SECURITY REASONS」封鎖頁（**不可**改 header／瀏覽器去繞）；新版 `mops.twse.com.tw` 未擋 | **第一站：Apify `apify/web-fetch`（unblocker 代理，不吃 Firecrawl 額度；2026-11-23 實測清單、step=9、PDF 皆成功）**：① 清單：`apify--web-fetch` 的 `url` 填 step=1 網址、`formats: ["text"]`（Big5 中文會亂碼，但檔名、檔案大小、上傳日期是 ASCII 可讀）② 下載連結：step=9 網址（見下方）、`formats: ["links"]`，回 `doc.twse.com.tw/pdf/{檔名去副檔名}_{yyyyMMdd_HHmmss}.pdf` ③ PDF 本體：拿到連結後**立刻**用 `call-actor`（`actor: apify/web-fetch`、`waitSecs: 45`、`callOptions.timeout: 300`）跑，`formats: ["markdown"]` 直接得到 PDF 全文（可省 Convert2md），再用 `get-dataset-items`（`fields: markdown`）讀回；`formats: ["raw"]` 可取得原始 PDF（2330 Q3 英文版 1,917,922 bytes，和清單大小相同），但要把檔案搬進容器，環境必須先設 `api.apify.com` network secret（目前沒設）。限制：直接呼叫 `apify--web-fetch` 抓 PDF 會碰到 MCP 60 秒上限，PDF 一定要用 `call-actor`；5 MB 以上的 PDF 可能超過 120 秒（2330 Q3 合併版 5.3 MB 失敗），改抓英文版 `_AIA` 或官網 IR（§7.3）；markdown 太長時 `get-dataset-items` 可能讀不回 → 改官網 IR。Apify 不可用時才用 `firecrawl_scrape`（`formats: ["html"]`，basic 失敗或回快取封鎖頁時改 `proxy: stealth` + `maxAge: 0`，2026-11 對 4417、6121、6781 一次成功）取得完整清單：檔名（`{yyyy}0{季}_{代號}_AI1.pdf` 合併、`_AIA` 英文合併、`_AI2` 個別、`_AIB` 英文個別；年報 `mtype=F` 為 `{FY}_{代號}_{申報日}F04.pdf`）、檔案大小、上傳日期 → 判斷新季報是否已上傳並核對檔案大小；董事會通過到上傳隔 1 天（如 4417 Q2：8/6 董事會 → 8/7 上傳）～1 週以上不等，董事會當天清單不會有新檔，英文版再晚約 1~1.5 個月。下載連結：對 `t57sb01?co_id={代號}&colorchg=1&kind=A&step=9&filename={檔名}`（年報 `kind=F`）跑 `firecrawl_scrape`（stealth、html），回傳頁含 `doc.twse.com.tw/pdf/{檔名去副檔名}_{yyyyMMdd_HHmmss}.pdf`；拿到網址後立刻 `curl`（帶 UA）下載實體檔，時好時壞（2026-11 對 1521 成功取得完整 PDF，大小與清單相符）；若回約 947 bytes 封鎖頁（MCP 也無法存二進位檔）→ PDF 本體改從官網 IR 下載（§7.3）[2026-11] |
| MOPS 法說會簡報 PDF `mopsov.twse.com.tw/nas/STR/{代號}{yyyyMMdd}M001.pdf` | 和 TWSE 電子書同樣依 IP 封鎖：2026-11 起雲端容器 `curl` 帶 cookie 也回 307 + 947 bytes 封鎖頁（舊的 cookie 做法已失效） | `call-actor`（`actor: apify/web-fetch`、`formats: ["markdown"]`、`waitSecs: 45`）→ `get-dataset-items`（`fields: markdown`）取得簡報全文（2026-11-23 2330 Q3 法說 458,760 bytes PDF → 11 頁全文，17 秒，0 個 CID 亂碼）；要原始 PDF 改 `formats: ["raw"]`（同上，需要 `api.apify.com` network secret 才能搬進容器）。從台灣 IP 執行時（本機）`curl -sL -c cj -b cj {URL} -o out.pdf` 仍可用，下載後用 `pdfinfo` 確認完整。簡報連結可從 `poorstock.com/earningcall/{代號}` 取得 [2026-11] |
| 財報狗 `statementdog.com/analysis/{代號}/...` | `curl` 回 202 空內容；Apify `rag-web-browser` 回 202 + `x-amzn-waf-action: challenge`（AWS WAF）；Playwright 回 403；Bright Data 45 秒逾時 | 只有 `firecrawl_scrape`（basic proxy）可取得頁面，且只對 e-report 穩定（能列出 `doc.twse.com.tw` 原始檔名以核對年度/季別）；個股首頁 `/analysis/{代號}` 時好時壞（2026-11 同日一次全引擎失敗、一次 basic + `formats: ["query"]` 成功取得市場共識 EPS 與本益比／殖利率），失敗 2 次即記 ❌；亮點／風險內文為會員牆，社群討論目前抓不到。Firecrawl 沒額度時無替代路徑（Exa 索引的 e-report 版本落後，不可用來判斷是否有新財報）[2026-11] |
| TPEx 申請上櫃清單 `tpex.org.tw/openapi/v1/tpex_esb_applicant_companies` | JSON API，`curl` 可讀 | 含申請日、審議會日、董事會核准日、主辦承銷商；查興櫃股是否申請轉上櫃用這個 [2026-10] |
| Yahoo 股市 `tw.stock.yahoo.com/quote/{代號}.TW` / `.TWO` | SSR，`curl` 可讀。上市/上櫃股的 `/news` 可讀（HTML 內有文章 URL 與 `pubtime` 毫秒，但兩者在 HTML 中順序不固定）；興櫃股的 `/news` 會 302 回個股頁 | 上市櫃股可當台股新聞備援；**發布時間取各單篇 JSON-LD `datePublished`**，不要按位置配對 `pubtime`。月營收自動稿標題固定寫「年增」，負值（如「年增-68.63%」）即年減，不可誤讀。興櫃股「成交」可能是造市商報價、總量可能為 0，判斷價格要同時看總量 [2026-11] |
| 經濟日報 `money.udn.com` | 搜尋頁 `search/result/1001/{關鍵字}` 與單篇 `money/story/{cate}/{id}` 皆 SSR，`curl` 可讀 | 正文在 `article-body__editor`，時間取 JSON-LD `datePublished`。搜尋頁失效時用 `WebSearch` 搭 `site:money.udn.com` 找網址。-KY 股搜尋關鍵字要去掉「-KY」（`AES-KY` 只回舊文，`AES` 才有新文）[2026-11] |
| 富聯網 `ww2.money-link.com.tw/RealtimeNews/NewsContent.aspx?SN={id}&PU=0010` | SSR，`curl` 可讀；轉載時報資訊《興櫃市場》委買／委賣前 10 名等盤中排行（委買張、委賣張、成交張、股價、漲跌） | 興櫃冷門股的籌碼參考：用 `firecrawl_search`（`"{公司名}" 興櫃`、`tbs: qdr:m`）找網址；正文是全形空白對齊的表格，去標籤後在公司名附近取該列；發布時間在標題下方（到分鐘）。屬自動排行稿，無分析內容 [2026-11] |
| MoneyDJ `moneydj.com` | 搜尋 `kmdj/search/list.aspx?_QueryType_=NW&_Query_={公司名}` 為 SSR（含到秒的時間）；**少了 `_QueryType_=NW` 會 302 回首頁**；關鍵字含連字號（如 `AES-KY`）也會 302，改查 `AES` 或代號；單篇 `kmdj/news/newsviewer.aspx?a={GUID}` 為 SSR | 搜尋也會命中每日「投信買賣超排行」「鉅額交易」「上市櫃公司董監質設異動公告」（多家合併表格，正文中搜尋公司名取該列：身份、設質/解質/累積張數、質權人），可當籌碼資料；每季「櫃買中心：Q{N}上櫃認購/售權證標的」名單的「減少公司」可看出個股是否因流動性被剔除權證標的；「上櫃認購(售)權證彙總表」可看到新發行的個股權證。也會命中名稱相近的其他公司，要逐則核對。時間取 JSON-LD `datePublished`、正文取 JSON-LD `articleBody` [2026-11] |
| HiStock `histock.tw/stock/{代號}` | 個股頁 `curl` 可讀；舊討論區 `/stock/{代號}/討論` 404；`news.aspx` 渲染後仍空白 | 只用來取已發行股數、PE/PB、三大法人、融資券、借券；其新聞/重訊區更新時好時壞（2026-11 對 6781 已同步到當週，其他股曾落後數月），判斷近期公告以 §5.1 鉅亨為準 [2026-11] |
| 工商時報 `ctee.com.tw/search?q=`、旺得富 `wantrich.chinatimes.com/search?q=` | 搜尋路徑 404（站方沒有此頁） | 不跑 MCP 鏈，用 `firecrawl_search` / Bright Data `search_engine` 搭 `site:` 找個別文章 [2026-10] |
| PTT `ptt.cc/bbs/{板名}/search?q={關鍵字}` | SSR，`curl` 帶 cookie `over18=1` 可讀；列表含標題、`M.{秒}.A.xxx.html` 網址與月/日 | 冷門股多年無新文是常態（列表日期不含年份，年份從網址內 Unix 秒數換算）；Stock 板查完可再查產業板（如 `Bicycle`）[2026-10] |
| Dcard | 搜尋 API、Apify `rag-web-browser`、Playwright 皆 403 Cloudflare | `firecrawl_search` + `site:dcard.tw {公司名} {代號}` 取索引（含發文日期），單篇可用 `firecrawl_scrape`（basic）讀全文；Firecrawl 沒額度時改用 Exa `web_search_exa` 或 `WebSearch` 索引確認有無新文並依 §3.6 加註 [2026-11] |
| ToAlpha 法說 memo `toalpha.tw/memo/{代號}/{yyyy-MM-dd}` | SSR，`curl` 可讀；Q&A 需登入 | 公開段落有管理層語氣與一句話指引摘要；列表頁 `toalpha.tw/memo` 有法說隔天漲跌幅 [2026-11] |
| Mobile01 討論串 | `curl`、Playwright 皆 403（Akamai）；Apify `rag-web-browser` 直接給網址 403，但用 Google 搜尋模式（`query` 填關鍵字）曾以 200 取得討論串頁 | `firecrawl_search` + `site:mobile01.com {公司名} {代號}` + `tbs: qdr:m` 找文章（只放兩字公司名會被「胡搞瞎搞」之類字串誤配），再 `firecrawl_scrape` 單篇（含發文時間）；Firecrawl 沒額度時改用 Apify `rag-web-browser` 搜尋模式，或 Exa `web_search_exa` 取索引 [2026-11] |
| yfinance 台股日線（`{代號}.TW` / `.TWO`） | `Date` 欄是前一天 UTC 16:00 | 加 8 小時（即日期 +1）才是台北交易日 [2026-10] |
| Goodinfo `goodinfo.tw` | Bright Data 60 秒逾時 | 用 `firecrawl_search` 取索引，Firecrawl 沒額度時改用 Exa `web_search_exa`，依 §3.6 加註 [2026-10] |
| 券商承銷公告頁（嘉實資訊 iframe） | Firecrawl 只拿到 iframe 外殼 | 新股申購/承銷日程改抓 HiStock 公開申購頁（靜態表格）[2026-09] |

### 4.3 港股 / 中國

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| HKEXnews 披露易 | 有官方 JSON API | **港股財報與公告第一站**，照 §5.4 [2026-09] |
| HKEX 權益披露 `di.hkex.com.hk` | SSR，`curl` 可讀 | 入口 `NSSrchCorpList.aspx?sa1=cl&scsd=dd/mm/yyyy&sced=dd/mm/yyyy&sc={5碼}&src=MAIN&lang=EN` → `NSAllFormList.aspx` → 明細 `NSForm2.aspx` / `NSForm3A.aspx?fn=...`。核實「大股東增持」類新聞最準；交易代碼 3104「Services」是以單位支付酬金，不是自掏腰包買進。代碼 1201「sale」搭代價 3102「Assets other than cash」時要看大股東 Form 2 第 27 欄 Supplementary information（例：春泉管理人以基金單位派實物股息），新浪/智通自動快訊一律寫成「減持」，不可直接當市場拋售 [2026-11] |
| 富途新聞列表 `futunn.com/hk/stock/{5碼}-HK/news` | 只列最新 20 則（財報後熱門期僅涵蓋約 1~2 天，冷門期可涵蓋約 1 個月）；`curl` 時而 SSR、時而只回約 11KB `<title>Document` JS 外殼 | `curl` 有 SSR 時解析 `li.news-item` 的 `news-title`、`news-source` 與時間 span；回外殼時直接改 Playwright（snapshot 每則 link 含標題、摘要、來源與時間，時間為 UTC，+8 小時；`curl` SSR 拿到的時間已是香港時間，不必換算；snapshot 存在 `.playwright-mcp/page-*.yml`，用 `grep "link "` 取各則）。很多連結只指向騰訊通用殼頁（無文章 ID）。智通回購/CCASS 快訊偶爾漏日，要與 HKEX 披露交叉核對。較早期間改看 AAStocks／股吧 [2026-11] |
| 富途個股頁 `/quote`、`/announcement`、新聞內文 `news.futunn.com/hk/post/*` | JS 外殼；`/community` 導向登入頁 | 內文改用 Playwright 可取全文（MT Newswires 文章仍需登入）；Playwright 渲染出的發文時間是 UTC，+8 小時才是香港時間 [2026-10] |
| AAStocks | 列表 `aastocks.com/tc/stocks/analysis/stock-aafn/{代號}/0/hk-stock-news/1` 為 SSR；`http://` 會 302 | `curl -L` 抓列表（約 20 則；`/hk-stock-news/2` 回傳與第 1 頁相同，無法翻頁）；單篇 `.../stock-aafn-con/{代號}/{來源}/{ID}/hk-stock-news` 正文就在 SSR HTML（`og:description` 只有約 50 字，不要只取它）。頁頭附沽空金額與比率。市場異動快訊 `aastocks.com/tc/stocks/news/aamm-content/{id}/price-dropped`（`id` 如 `aad2611022327`，前 6 碼為 yyMMdd）不在個股新聞列表內，用 `WebSearch`「{公司名} {代號} 急跌 {月日}」找網址，`curl -L` 單篇可取標題與分鐘級時間；約 3 週後頁面只剩框架，只能引用搜尋標題 [2026-11] |
| 新浪港股新聞 `stock.finance.sina.com.cn/hkstock/news/{代號}.html` | SSR，最新；只列約 30 則（財報後熱門期僅涵蓋約 2 天，冷門期可涵蓋約 1 個月），含券商研報標題 | `curl`（gb18030 解碼）可讀；研報頁 `stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/search/rptid/{id}/` 為 SSR（gb18030），正文在 `div.blk_container`、機構/研究員/日期在 `div.creab`，可取研報摘要全文。即時／收市報價 `curl -H "Referer: https://finance.sina.com.cn" https://hq.sinajs.cn/list=rt_hk{5碼}`（gb18030）：逗號分隔依序為英文名、中文名、開、前收、高、低、現價、漲跌、漲跌%、買、賣、成交額、成交量…日期、時間；yfinance 港股最新一日 OHLC 常為空值時用它補 [2026-11] |
| 新浪財經內文 `finance.sina.com.cn`、`t.cj.sina.cn`、`cj.sina.cn` | 時好時壞，且依路徑不同：`/stock/relnews/`、`/stock/aiassist/`（平台 AI 稿）、`/jjxw/`（2026-11 新華財經稿可讀）與研報頁可讀；`/stock/hkstock/marketalerts/`、`/stock/hkstock/hkstocknews/`、`/stock/aigc/`、`/roll/` 與 `cj.sina.cn/articles/view/*` 常回 curl rc=35（SSL connect error／agent-proxy `ws_closed_mid_exchange`） | 先 `curl -m 10` 試 1 次；正文在 `id="artibody"` 之後、時間在 `span.date`。rc=35 時改用 `firecrawl_scrape`（basic，`formats: ["query"]` directQuote，約 5 credits）2026-11 對 `cj.sina.cn`／`/roll/`／`/jjxw/` 4/4 成功，可取正文與 `publishedTime`；Firecrawl 不可用時改找轉載全文：智通「港股異動」稿用富途 `news.futunn.com/hk/post/*`（§4.3 富途列）；A+H 股的上證報／證券時報轉載稿常在東方財富股吧單篇（§5.5）可讀全文；或 Exa `web_search_exa`（依 §3.6 標註為索引）。都沒有才只引用列表標題 [2026-11] |
| 雪球 `xueqiu.com/S/{代號}` | JS 動態渲染 + WAF；Apify `rag-web-browser` 只拿到 WAF JS 外殼，Playwright 回 HTTP 567「请求异常已被安全策略拦截」（對 AI Agent 限制數小時，2026-11 依舊） | 照 §5.6 [2026-11] |
| 東方財富股吧 `guba.eastmoney.com` | 第一頁是 SSR，但會連續回空殼 | 照 §5.5 [2026-11] |
| 東方財富公告 API `np-anotice-stock.eastmoney.com/api/security/ann?sr=-1&page_size=40&page_index=1&ann_type=A&client_source=web&stock_list={A股代碼}` | JSON，`curl` 可讀 | **A 股公告／季報第一站**（子公司為 A 股時也適用，如 3445 ↔ 688432）：`list[].notice_date`、`art_code`、`title`；PDF 實體 `https://pdf.dfcfw.com/pdf/H2_{art_code}_1.pdf`，`curl` 可直接下載、`pdftotext` 0 個 `(cid:` [2026-11] |
| moomoo 社區 `moomoo.com/hk/stock/{5碼}-HK/community` | Firecrawl 需額度；Bright Data 回 403「Operations too frequent」或 `Document` 外殼；Apify `rag-web-browser` 回 200 但只有 `Document` 外殼 | **直接用 Playwright**（會導向 `/hant/stock/...`），snapshot 內含作者、`yyyy/MM/dd HH:MM` 時間連結與貼文摘要；頁面下半部「Moomoo Insights」與熱門文章是平台推薦、與個股無關，要排除；冷門港股常數月才一則 [2026-11] |
| LIHKG | `api_v2/thread/search` 直接打回 `error_code 5`；頁面自己發出的 `api_v2/thread/search` 時好時壞（2026-10 上旬 503、10-22 起多次回 200） | Playwright 開 `lihkg.com/search?q={關鍵字}&sort=desc_create_time`，用 `browser_network_requests`（`filter: thread/search`）看頁面 API 狀態；200 時用 `browser_network_request` 讀回應（在頁內自行 `fetch` 仍回 error 5；`create_time` 為 Unix 秒），503 時試 2 次即記 ❌；200 但內容為 `{"success":0,"error_code":100,"error_message":"沒有相關文章"}` 代表站內確實沒有符合的討論串，記 ⭕；不帶 `filename` 時回應會直接回傳在結果內，最省事（收尾見 §3.4）[2026-11] |
| 新聞農場（如爽報 `yesdaily.com`） | Exa／搜尋常把它排在最前，頁面「发布时间」自動標成抓取當天，內容是多年前的舊公告重貼 | 一律不當新聞；若收錄須註明「假時效，與 {官方來源} 不符」（例：87001「長實 30%→70% 增持管理人」實為舊交易，2026 中報已是長實 100%）[2026-11] |
| 香港經濟日報 `hket.com` | `inews` 回 HTTP 405 真人驗證；`invest.hket.com/article/{id}` 用 `curl` 回 200 但只有約 1.3KB 外殼；搜尋頁 404 | 用 `WebSearch` 搭 `allowed_domains: ["hket.com"]` 找文章網址，再 `firecrawl_scrape`（basic proxy）取標題、作者、發布日期與導言（網址要帶搜尋結果中的完整 slug，只填 `article/{id}` 會全引擎失敗）；後段為會員牆，不必再跑 MCP 鏈 [2026-11] |

### 4.4 日股

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| Yahoo!ファイナンス 株つぶやき `finance.yahoo.co.jp/quote/{代碼}.T/post` | SSR，`curl` 可讀 | **日股抓 X 貼文的最佳路徑**：頁面聚合真實 X 貼文，保留 `x.com/{帳號}/status/{id}` 與到分鐘的時間；用 regex `https://x\.com/[A-Za-z0-9_]+/status/[0-9]+` 配對文字，單頁約 8~16 則。**HTML 中每個時間連結（`_cl_link:time`）後面接的是下一則貼文的作者與內文**：作者以該段結尾的 `@帳號` 為準，時間用該帳號貼文網址的 status ID 還原（§4.1 X 列公式），不要沿用相鄰的時間標籤；status ID 換算與頁面日期差距很大（如換算為兩年前）時該則不列入。限制：① J-REIT 沒有此頁（404，不是封鎖）→ 改用 `firecrawl_search` + `site:x.com`；② 社名是一般名詞的公司（如「光通信」）會混入大量無關貼文與假消息，要逐則核對；③ 常混入「爆上げ／ストップ高／四季報上修」導流垃圾帳號（附 `kubu.luhu.jp`、`naturori.com` 等短網址），一律排除，其「自社株買い／増配／優待拡充」說法要對照株探開示清單 [2026-11] |
| Yahoo JP ニュース `finance.yahoo.co.jp/quote/{代碼}.T/news` | SSR，`curl` 可讀；列表含 `news/detail/{id}` 網址、標題、來源與日期（ウエルスアドバイザー、FISCO、トレーダーズ・ウェブ、株探） | 單篇 `curl` 可讀，時間取 JSON-LD `datePublished`；TOPIX 見直し、FISCO 銘柄コメント等常只在這裡出現。列表多為技術面列名（雲抜け、MACD），要逐則核對 [2026-10] |
| Yahoo JP 掲示板 `finance.yahoo.co.jp/quote/{代碼}.T/forum` | SSR，`curl` 一次約 50~80 則，每則有 `/forum/{No}` 網址、分鐘級時間；2026-11 起為新版掲示板（無 `__PRELOADED_STATE__`） | 去標籤後用直線符號串接各欄，用 regex `\|No\.\|(\d+)\|(yyyy/m/d HH:MM)\|報告\|` 切出每則（編號可能是 4 碼，如 4979 為 No.77xx，寫死 `\d{5}` 會 0 筆），正文到 `|返信|` 為止；被刪的編號會跳號。`?page=N` 不會翻頁；熱門大型股只涵蓋約 11 小時、冷門股可涵蓋數月 → 報告註明涵蓋區間，用 5ch / 株つぶやき 補足 [2026-11] |
| 株探 `kabutan.jp` | `curl` 可讀；`/stock/kabuka?code={代碼}&ashi=shin` 回 405 | 個股頁含 PER／PBR／利回り／信用倍率（每週信用餘額明細頁不可用）；日線 `/stock/kabuka?code={代碼}` 為 SSR 表格（日期、始高安終、前日比、出来高）；`/stock/news?code={代碼}&nmode=3` 只列開示，可直接找到決算短信（含英文版）。列表連結指向包裝頁 `kabutan.jp/disclosures/pdf/{yyyymmdd}/{id}/`（HTML），PDF 實體網址 `tdnet-pdf.kabutan.jp/{yyyymmdd}/{id}.pdf` 要從該頁取出。**日股找季報最快路徑**。新聞第 1 頁只涵蓋約 1 個月，加 `&page=2`、`&page=3` 可再往前；大量保有報告多的公司（如 9435）與大型股決算日（如 7203，含大量市況與技術面列名稿）每頁只涵蓋數天～1 週。列表 `<time>` 有時只顯示收盤時間 15:30，單篇內文開頭的「yyyy年mm月dd日HH時MM分」才是真實發布時間。新聞列表偶爾混入申報人不是該公司的報告（如 9435 頁出現 TYK／大同特鋼的申報），要核對申報人 [2026-11] |
| 株予報 `kabuyoho.jp/sp/reportTarget?bcode={代碼}` | SSR，`curl` 可讀 | 頁頭有「次回発表予定 第N四半期決算：yyyy/mm 上/中/下旬」，可查下次決算時點；另有アナリスト目標株価平均、人數與 PBR/PER 理論株価（含下値目途）[2026-11] |
| みんかぶ `minkabu.jp/stock/{代碼}` | `curl` 405、Apify `rag-web-browser` 405「Human Verification」（AWS WAF）、Playwright 403 | `firecrawl_scrape` 或 Apify `apify/web-fetch` 可讀。有目標株価／株価診断，常與掲示板情緒相反，可當空方對照；`firecrawl_scrape` 搭 `formats: ["query"]` directQuote（約 5 credits）可直接取「目標株価／株価診断／個人予想／アナリスト」一行摘要；J-REIT 顯示「対象外」不可用 [2026-11] |
| 5ch | `find.5ch.net` 已 301 到 `find.5ch.io` | `curl -L "https://find.5ch.io/search?q={公司名}"`（UTF-8）；討論串內文是 Shift_JIS，要 `decode('cp932')`。ニュース速報+／嫌儲 的串標題常誇大，要比對 1 樓轉貼的原始新聞。搜尋結果連結為協定相對網址（`//xxx.5ch.io/test/read.cgi/...`），要補 `https:`；短社名常撞名（如「エスコン」= Ace Combat／エスコンフィールド），要逐串核對 [2026-10] |
| note `note.com` | API 403/404；搜尋頁 `curl` 只拿到外殼 | `firecrawl_scrape` 抓 `note.com/search?q=…&context=note&mode=search&sort=new`（`waitFor: 3000`），Firecrawl 不可用時改 Apify `apify/web-fetch`（markdown 不含文章網址，要再跑一次 `formats: ["links"]`）；單篇 `curl` 可讀，時間取 JSON-LD `datePublished`；付費文章只取得免費段落 [2026-10] |
| 東洋経済オンライン `toyokeizai.net/articles/-/{id}` | SSR，後段付費；`/search/?q=` 404；四季報 `shikiho.toyokeizai.net` 為 JS 外殼 + 付費 | 找文章用全文搜尋 `toyokeizai.net/list/search?fulltext={關鍵字}`（SSR，`curl` 可讀）；單篇要 `curl -L`（會 302 到 `?display=b`，不加 `-L` 只拿到約 116 bytes 轉址頁），取公開段落與 `datePublished`；付費牆不必跑 MCP 鏈 [2026-11] |
| 日経 `nikkei.com/nkd/company/news/?scode={代碼}&ba=1` | SSR，`curl` 可讀；日期在 `m-listItem_time`，付費文章有標記 | 單篇 `curl` 取 `datePublished` 與導言段；付費牆不必跑 MCP 鏈 [2026-10] |
| E-IR 代管的官網 IR 頁（如小糸 `koito.co.jp/english/ir/info/earningsreport/`） | PDF 連結由 `eir-parts` JS 注入，`curl` 看不到 | Playwright `browser_evaluate` 列出連結；PDF 實體在 `ssl4.eir-parts.net/doc/{代碼}/{tdnet\|yuho_pdf\|…}/{id}/00.pdf`，`curl` 可直接下載（`yuho_pdf` = 有価証券報告書全文）[2026-10] |
| JAPAN-REIT.COM `japan-reit.com/meigara/{代碼}/` | `curl` 回 SSL 憑證鏈錯誤（站方問題，**不可**關閉 TLS 驗證）；`WebFetch` 回 503；2026-11 起 `firecrawl_scrape` 也回 SSL 憑證錯誤、Bright Data 45 秒逾時 | **直接用 Apify `apify/rag-web-browser`**（`query` 填網址、`maxResults: 1`，約 10 秒、200）：價格、時價總額、利回り、排名（含 NOI 利回り）、業績預測、銘柄ニュース與開示清單。`/news/` 404，改用 `/topic/` 或 `/release/` [2026-11] |
| Shared Research `sharedresearch.jp/ja/companies/{代碼}` | J-REIT 回 404（沒有覆蓋） | 小型股常是唯一的第三方研究覆蓋；J-REIT 不必查 [2026-10] |

### 4.5 印尼（美股 ADR 的母股，如 TLK ↔ IDX `TLKM`）

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| CNBC Indonesia `cnbcindonesia.com`、Katadata `katadata.co.id`、Selular.ID `selular.id`、periskop.id `periskop.id` | SSR，`curl` 可讀，JSON-LD 有 `datePublished` | 用 `WebSearch`（印尼文關鍵字，如「saham {代號} anjlok」）找網址再 `curl` 單篇；Katadata 是 IDX 公告與券商觀點的主力轉述來源；periskop.id 常逐條轉述公司對 BEI 異常波動詢問的回覆（keterbukaan informasi）[2026-10] |
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

- 公司名、代號、常用簡稱（如 `AES-KY` 與 `AES`）各查一次，用 `newsId` 去重（代號常命中盤後速報，公司名常命中重訊；代號索引可能落後數週，不可只查代號；純數字代號也會命中內文含該數字的無關文章，如「鏈文」加密貨幣稿，要依 `category` 與標題逐則排除；KY 股可能沒有中文名，不可拿相似名稱查詢，如 6781 AES-KY ≠ 4931 新盛力）[2026-11]。
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

### 5.3 Reddit（Apify Actor `harshmaur/reddit-scraper`）

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

### 5.4 HKEXnews 官方 JSON API（港股財報/公告）

1. `https://www1.hkexnews.hk/search/prefix.do?callback=c&lang=EN&type=A&name={代號}` → 取得 `stockId`。
2. `https://www1.hkexnews.hk/search/titleSearchServlet.do?sortDir=0&sortByOptions=DateTime&category=0&market=SEHK&stockId={stockId}&documentType=-1&fromDate={yyyyMMdd}&toDate={yyyyMMdd}&lang=EN&searchType=1`
   - servlet 名稱**大小寫敏感**，必須是 `titleSearchServlet.do`（全小寫回 404）。
   - 不要帶 `t1code` / `t2Gcode` / `t2code`；若一定要帶，值是 `-2`（填 `-1` 會讓任何查詢都回 0 筆）。
3. `lang=ZH` 取中文版；`recordCnt: 0` 代表該期間確實沒有公告。中文 PDF（檔名 `_c.pdf`）用 `pdftotext` 常因缺 Adobe-GB1 字型解析失敗 → 改用 `lang=EN` 回傳的英文版 `FILE_LINK`（同編號去掉 `_c`）。季報日常有兩份英文檔：「Announcement of Unaudited Results…」才是正式季報，「ORA - … Quarterly Results」是業績簡報。
4. PDF 連結 = `https://www1.hkexnews.hk` + `FILE_LINK`。

### 5.5 東方財富股吧（A 股代碼）

- 列表：`curl -A "<UA>" https://guba.eastmoney.com/list,{A股代碼}.html`，頁內 `var article_list = {...}` 含約 40 筆（`post_id`、`post_title`、`post_publish_time`、點閱/留言數）。
- 單篇：`https://guba.eastmoney.com/news,{A股代碼},{post_id}.html`，用 `json.JSONDecoder().raw_decode` 解析 `post_article` 之後的 JSON，取 `post_content`。連續抓取時部分單篇會回約 2.8KB 空殼（無 `post_article`）→ 帶 `Referer: https://guba.eastmoney.com/list,{代碼}.html`、間隔 4 秒重試 1 次；連抓約 3 篇後常整批回空殼且重試無效 → 每吧單篇最多抓 3~4 篇，雙重上市股兩個吧輪流抓，抓不到全文就只引用列表標題 [2026-10]。
- 港股也有股吧：代碼寫 `hk{5碼}`（如 `list,hk00546.html`），格式同上。H 股吧與 A 股吧都可能連續回約 2.8KB 空殼、無 `article_list`（如 `hk03606` 曾空殼而 600660 正常——2026-11 `hk03606` 第 1 次即成功；`003816` 空殼而 `hk01816` 正常），雙重上市股兩邊互為備援；純港股（無 A 股）或單一 A 股吧（如 688432）兩次皆空殼時，`firecrawl_scrape`（basic proxy）可取得完整列表表格（閱讀、評論、標題、最後更新）[2026-11]。

### 5.6 雪球

1. 先用 Bright Data `scrape_as_markdown` 抓 `https://xueqiu.com/S/{代號}`（雪球用 Bright Data 成功率最高，可跳過內建工具）。單篇長文 `xueqiu.com/{用戶id}/{貼文id}` 也用 Bright Data，第一次常回空白，重試 1 次即可取得全文與「发布于」時間 [2026-10]。
2. Bright Data 失敗或回 `bad_endpoint`（KYC）→ `firecrawl_scrape` 搭 `proxy: stealth`。Apify 只拿到 WAF 外殼、Playwright 回 567，兩者不必再試。
3. Bright Data 與 Firecrawl 都不可用（預檢停用或失敗）→ 直接用 Exa `web_search_exa`（query 寫「雪球 {公司名} {代號} 讨论 {年月}」）[2026-11]：
   - 會回傳雪球單篇頁的索引全文，含「发布于 YYYY-MM-DD HH:MM」、回覆數與部分留言（Exa `Published` 欄位標 `Z` 但實為北京時間，以「发布于」為準）。
   - 也常回傳個股的 `/S/{代號}/hots?page=N` 與 `/S/{代號}/time?page=1` 索引頁，列出最近十幾則討論的作者、`MM-DD HH:MM` 與摘要，可用來確認「最新一則是哪天」；索引可能落後數天，查不到新貼文時寫「索引內無新貼文，不能排除漏抓」。
   - 依 §3.6 標註為索引；逐則確認是否屬該公司（留言頁常是其他個股的討論串）。
4. 雙重上市公司的 A 股頁（`SH601318`）與 H 股頁（`02318`）互為備援。
5. **時間要校準**：討論流顯示相對時間，且 Firecrawl 渲染時區是 `America/New_York`；一律以單篇頁的「发布于 YYYY-MM-DD HH:MM」（北京時間）為準。
6. 只抓討論，不從雪球抓財報。

---

## 6. Phase 1 — 建立資料夾

- 台/日/港股：`FinancialReport/{代碼}{名稱}/`（例：`2881富邦金/`）；美股：`FinancialReport/{代碼}/`（例：`UHS/`）。
- `Routines_collectStk.md` 輪替表有寫資料夾名稱時，以表上為準。不存在就建立。

---

## 7. Phase 2 — 最新財報

目標：最新 **2 份年報 + 1 份季報**（只有半年報的公司，用最新半年報代替季報）。找到一份就下載、驗證、存檔，再找下一份。

### 7.1 先盤點，再下載

列出資料夾既有檔案，用檔名判斷已涵蓋哪些期別，**已有的直接跳過**（已有 `.md` 的期別視為已下載）。新檔一律用統一命名：

| 類型 | 命名 | 範例 |
| :--- | :--- | :--- |
| 年報 | `{TICKER}_AnnualReport_{FY}.{ext}` | `5306_AnnualReport_2025.pdf` |
| 季報 | `{TICKER}_Quarter_{FY}Q{N}.{ext}` | `5306_Quarter_2026Q2.pdf` |
| 半年報 | `{TICKER}_Quarter_{FY}H1.{ext}` | `2245_Quarter_2026H1.pdf` |

- `{FY}` 是財報所屬年度/期間，不是申報日或下載日；檔名不加時間戳或表單代碼。3 月決算公司用會計年度結束年（2026 年 4~6 月 → `{TICKER}_Quarter_2027Q1`）。
- 舊檔名不強制改名，但盤點時要認得：`{TICKER}_annual_{FY}`、`{TICKER}_quarter_{FY}Q{N}`、`{TICKER}_interim_{FY}`、`{TICKER}_QuarterlyReport_{FY}Q{N}`、台股 `{FY}_{TICKER}_{申報日}F04/FE4`（年報）、`{yyyyMM}_{TICKER}_AI1`（季報）、美股 `{TICKER}_10K_{期末日}` / `{TICKER}_10Q_{期末日}`、日股 `有価証券報告書`、`決算短信`。

### 7.2 下載驗證（每份下載完立刻做）

| 檢查 | 不合格處置 |
| :--- | :--- |
| 檔案 < 10KB | 刪除，換來源 |
| 前 4 頁沒有公司名稱或代碼 | 刪除，換來源 |
| `convert_pdf_to_markdown` 試轉，`(cid:` ≥ 50 次或佔比 ≥ 5% | 字型缺字無法修復 → 刪除，改抓英文版或換來源 |
| 網路錯誤 | 照 §3.3 |

- **英文版優先**：台股 MOPS 中文 PDF 常有 `(cid:` 亂碼，英文版通常乾淨。
- 日文 PDF 用 `pdftotext` 常因缺 Adobe-Japan1 字型失敗，名稱與 cid 檢查改用 `convert_pdf_to_markdown` 試轉。
- 保留原始副檔名（`.pdf` / `.html`），不要手動改成 `.md`。

### 7.3 搜尋來源（依序，找到即停）

- **台股**：① MOPS/TWSE 電子書（§4.2；英文版 `_AIA.pdf` 常晚中文 `_AI1.pdf` 1~1.5 個月，有就優先用）② 財報狗 e-report（§4.2）③ 官網 IR（見下方已驗證路徑）。確認「是否已公告」用 §5.1 鉅亨（給的是重訊全文，不是財報 PDF）。興櫃公司只有半年報與年報，不會有 Q1/Q3。
  - 台產 2832：`tfmi.com.tw/investors-Financial` 列出 `/Files/TFMI/各單位上傳/財務部/財務報告/{yyyy}年/{民國年}年第{N}季財務報告.pdf`，`curl` 可下載，上架晚於 TWSE。
  - 胡連 6279：`www.hulane.com.tw/financials`（季報）與 `/conferences-and-meetings`（股東會年報）為 SSR；PDF `/admin/uploads/Investor/財務報告/{yyyy}/胡連{民國年}Q{N}合併財報電子書.pdf`、`/admin/uploads/Investor/股東會/{yyyy}/胡連-{FY}年報(中文版).pdf`，`curl` 可下載、0 個 `(cid:`；舊站 `product.hulane.com` 停更。
  - 新普 6121：`simplo.com.tw/download.php?lang=tw&tb=2`（財報）／`tb=4`（法說）；下載鈕 `go_download('{base64}')` 解碼後 POST `include/download.php`（參數 `dl`），回傳頁含 `simplo.com.tw/archive/doc/download/{yyyy}Q{N}_新普合併財報.pdf`，`curl` 可下載。
  - AES-KY 6781：`advancedenergysolution.com.tw/download.php?lang=tw&tb=3&cid=-1` 上架晚 TWSE 數月，下載為 JS `go_download`，不能直接 curl。
- **美股**：① 官網 IR（SEC Filings）② SEC EDGAR（`sec-edgar-mcp`）③ 財報狗 ④ 富途 `futunn.com/hk/stock/{代號}-US/announcement`。外國發行人（ADR）年報是 20-F、季報夾在 6-K：`curl -A "{名稱} {email}" https://data.sec.gov/submissions/CIK{10碼}.json` 列出申報，再看 `.../Archives/edgar/data/{CIK}/{去掉 - 的 accession}/index.json` 附件，6-K 主文件開頭寫 "Consolidated financial statements as of …" 即為季報。
- **日股**：① 官網 IR（英文 Annual Report 優先）② 株探開示清單（§4.4，決算短信最快）③ EDINET ④ IR Bank `irbank.net/{代碼}/ir` ⑤ 富途 `{代碼}-JP/announcement`。
  - J-REIT 經審計英文財報常在官網英文 IR 庫，無 cid 問題：ES-CON（2971）`escon-reit.jp/en/ir/library.html`「Asset Management Reports」欄；HCM（3455）`hcm3455.co.jp/en/ir/library.html`「Semi-annual report」欄。決算後約 1 個月內英文頁常只有 Summary of accounts；頁頂「As of …」日期不會更新，不能判斷新舊。
  - 英文版未出時，日文 IR 庫的「資産運用報告」PDF 約決算後 3~3.5 週上架，可直接當該期年報（HCM `hcm3455.co.jp/ja/ir/library.html`；ES-CON `escon-reit.jp/ja/ir/library.html`，`/ir/library.html` 只是殼或回 S3 403）。
  - 光通信（9435）決算短信 PDF 固定為 `hikari.co.jp/assets/pdf/ir/{期}th/{1st|2nd|3rd|4th}_zaimu.pdf`（第 40 期＝2027 年 3 月期），`curl` 可下載。
- **港股**：① HKEXnews JSON API（§5.4）② 富途 `{5碼}-HK/announcement` ③ 官網 IR。（新浪 `/hkstock/notice/` 已停更，不要用）

---

## 8. Phase 3 — 近三個月輿情/新聞

### 8.1 存檔規則

- 檔名：`FinancialReport/{資料夾}/{yyyyMM}_輿情新聞.md`（`yyyyMM` = 執行當月），一個月一檔、所有來源合併。
- **開始前**先讀資料夾內的 `{YYYY}_PublicOpinion.md`（`ArrangePublicOpinionMd` 合併的年度檔）與當月檔，確認上次收集到哪一天，只補新內容。
- **Append 模式**：檔案不存在 → 建立並寫標頭；來源章節不存在 → 末尾新增 `## [來源名稱]`；章節已存在 → 補在該章節末尾。不可覆蓋舊內容。每抓完一個來源立刻寫入。

### 8.2 來源（依市場；抓不到照 §3 處理，不可當成「沒資料」略過）

- **台股**：鉅亨網（§5.1）、MoneyDJ、經濟日報、PTT 股市板、Dcard、Mobile01、股市爆料同學會（§5.2）、財報狗、HiStock、TPEx（興櫃股）。
- **美股**：Yahoo Finance（§4.1）、Reuters、Bloomberg、Seeking Alpha、Reddit（§5.3）、X、分析師評級（§4.1）。ADR 另查母國公告（SEC 6-K）與母國媒體/社群（印尼見 §4.5）。
- **港股 / 中國**：富途、AAStocks、新浪港股新聞、HKEX 權益披露、雪球（§5.6）、東方財富股吧（§5.5）、moomoo、LIHKG、香港經濟日報。
- **日股**：日經、Yahoo JP 掲示板／株つぶやき／ニュース、株探、みんかぶ、5ch、note、Shared Research、東洋経済；J-REIT 加 JAPAN-REIT.COM。
- 雙重上市公司主市場來源不足時，再查另一邊市場。

### 8.3 過濾與查證

1. 只記錄實質的基本面/事件/觀點；略過純漲跌數字、表情符號。
2. 每筆都要和該公司直接相關；排除標題與內文都沒提到公司或代號的貼文、媒體自我介紹文、仿冒/垃圾站。
3. 寫出原作者的核心論點與細節，不能只貼網址。
4. 平台 AI 生成的內容（如 CMoney Readmo、新浪 `/aiassist/`）標明「AI 生成」，不可當網友輿情。
5. 明顯誇大或與官方資料矛盾的說法，註明「與 {官方來源} 不符」，不可自行改寫原文。
6. **具體財務事件要回查本機財報**：網友或媒體提到可驗證的事件（貸款到期、回購、增發、收購、管理費），先 `rg` 公司資料夾內的年報／季報 md。查得到註明「已證實（{報告} {段落/附註}）」，查不到才寫「尚待公告確認」。債務到期日要從「提用日＋期限」推算，不要只看最新一期的到期區間（例：87001「11 月到期 15 億港元貸款」= 2023 年報附註 18 的 2023-11-30 三年期提用 → 已證實）。
7. **新聞日期要核對**：頁面標示當天、內容卻是舊公告（新聞農場重貼）→ 註明「假時效，與 {官方來源} 不符」，不可當新事件。

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
- 已嘗試：curl → JS 外殼；firecrawl_scrape → 403；Bright Data → 逾時；Apify → 預檢停用（requires approval）；Playwright → 登入牆
- **結論**：本次無法取得真實輿情，非 AI 生成，下次重試。
````

查得到站但三個月內沒有該公司新內容 → 寫 `⭕ 無新內容`，並寫明搜尋方式（關鍵字、頁面），讓下次知道已查過。

---

## 9. Phase 4 — 轉 Markdown

- Phase 2 有新 PDF 時，呼叫 **`Convert2md` Skill**（用 `convert_pdf_to_markdown` 轉檔，自動刪除 CID 亂碼失敗檔）。沒有新檔就略過並在報告註明。
- 150 頁以上的年報常回「timed out after 60s」，但 MCP 伺服器仍在背景寫檔：不要重送，等 `save_path` 的 `.md` 出現且大小不再變動，再核對最後一頁有轉出。
- 輸出的 `.md` 含指向暫存 `pdf_images/` 的圖片連結，轉檔後移除 `![](…/pdf_images/…)` 行。
- `Convert2md` **只處理 PDF**。HTML（如 SEC 10-K/10-Q）要自己轉成同檔名 `.md`：移除 XBRL/iXBRL 標籤與內嵌 blob，確認正文可讀後刪原始 HTML。

---

## 10. Phase 5 — 執行報告與 push

報告寫到 `FinancialReport/Log/collectStk_Summary_{yyyyMMdd}.md`。

````markdown
# 任務執行最終報告 - YYYY/MM/DD

- **執行日**：YYYY-MM-DD（輪替表第 N 日 → {代碼} {名稱}）
- **公司資料夾**：`{資料夾}/`

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |

**本期重點**：（條列近三個月的關鍵事件與輿情，利多與利空都要寫；提到金額時附每股金額）

## 2. 失敗或被擋網站
- **來源**：[網站](URL)｜**原因**：{403 / 逾時 / 付費牆…}｜**已試過**：{實際試過的工具}

## 3. 資料缺失說明
（如：財報尚未公布、興櫃只有半年報、冷門股無討論）

## 4. 異常檔案刪除紀錄
（< 10KB、無公司名稱、`(cid:` 亂碼等被刪的檔案；沒有就寫「無」）

## 5. MCP 預檢與使用紀錄
- **預檢結果**：可用：{…}｜停用：{MCP}（{錯誤原文}）
- **使用者待辦**（有停用或跳過核准卡片才寫）：照 §3.0.3 寫出連接器與工具名，例：「到 https://claude.ai/customize/connectors 把 Firecrawl、Bright Data 的工具權限設為一律允許（Always allow）」

| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
（用人類可讀名稱，如 Firecrawl、Bright Data、Apify、Exa、Playwright、yfinance；執行中才出現的帳號級錯誤也寫這裡。完全沒用 MCP 就寫「本次未使用 MCP，僅用 {內建工具}」）

## 6. Phase 4 Convert2md
## 7. Skill 維護
（本次新增、修改、刪除了哪些 §3.0 / §4 / §5 內容；沒有就寫「無」）
````

> [!IMPORTANT]
> **報告寫完後，必須把所有新增與變更的檔案 commit 並 push，任務才算完成。** push 前刪除 `.playwright-mcp/`（§3.4）。
> - 雲端 session／被指定 feature 分支 → push 該分支並開 PR（auto-merge workflow 會合併進 `master`）。
> - 本機直跑 → push `master`。
> - 不可因分支限制停下來詢問使用者。

---

## 11. Skill 維護規則（每次更新本 Skill 都要做）

執行中發現新的網站行為（新封鎖、新 API、新捷徑、舊做法失效）時，在 Phase 5 更新本 Skill，並同時清理：

1. **放對位置**：網站行為放 §4 對應市場表格（一站一列）；多步驟 API 用法放 §5；MCP 帳號級錯誤、預檢與連接器修法放 §3.0；官網 IR 下載路徑放 §7.3。不另開段落、不在別處重寫抓取規則。
2. **合併不追加**：同一站點已有一列時直接改寫那一列並更新 `[yyyy-mm]`，不新增「補充」列。
3. **刪除無用資料**：失效做法、被取代的舊寫法、改版前網址、與 §3 重複的敘述、一次性除錯流水帳（某天抓到幾筆、檔案多大）、指向不存在檔案的連結 → 刪除，只留結論。環境設定細節（如 Playwright 啟動器原理）看 `.claude/scripts/playwright-mcp.mjs` 開頭註解，不寫在這裡。
4. **檢查一致性**：內文 § 編號引用要對得上；`rg -n "collectStk" Analysis/` 找引用本 Skill 章節的檔案一併更新。
5. **兩份同步**：`.claude/skills/collectStk/SKILL.md` 與 `.agents/skills/collectStk/SKILL.md` 必須完全相同（改完用 `diff` 確認）。
6. 在 §10 報告「Skill 維護」寫明本次新增、修改、刪除了什麼。
