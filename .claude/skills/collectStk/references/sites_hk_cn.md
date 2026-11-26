# collectStk 參考：港股 / 中國

> collectStk 站點知識庫（§4）／API SOP（§5）／官網 IR 路徑（§7.3）的「港股 / 中國」部分。
> 只在處理該市場公司時讀。抓取規則（§3）、存檔與過濾（§8）在 `../SKILL.md`。
> 表格格式：站點 / 網址 | 狀況 | 做法；`[yyyy-mm]` = 最後驗證月份。維護規則見 `../SKILL.md` §10。

## §4.3 港股 / 中國

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| HKEXnews 披露易 | 有官方 JSON API | **港股財報與公告第一站**，照 §5.4 [2026-09] |
| HKEX 權益披露 `di.hkex.com.hk` | SSR，`curl` 可讀 | 入口 `NSSrchCorpList.aspx?sa1=cl&scsd=dd/mm/yyyy&sced=dd/mm/yyyy&sc={5碼}&src=MAIN&lang=EN` → `NSAllFormList.aspx` → 明細 `NSForm2.aspx` / `NSForm3A.aspx?fn=...`。核實「大股東增持」類新聞最準；交易代碼 3104「Services」是以單位支付酬金，不是自掏腰包買進。A+H 股公司的 A 股類別大股東減持若附代價 CNY 且第 27 欄寫「可交换公司债券进入换股期」（如 01816 廣東恆健，代碼 1203），是可交換債持有人換股，不是二級市場拋售。代碼 1201「sale」搭代價 3102「Assets other than cash」時要看大股東 Form 2 第 27 欄 Supplementary information（例：春泉管理人以基金單位派實物股息），新浪/智通自動快訊一律寫成「減持」，不可直接當市場拋售 [2026-11] |
| 富途新聞列表 `futunn.com/hk/stock/{5碼}-HK/news` | 只列最新 20 則（財報後熱門期僅涵蓋約 1~2 天，冷門期可涵蓋約 1 個月）；`curl` 時而 SSR、時而只回約 11KB `<title>Document` JS 外殼 | `curl` 有 SSR 時解析 `li.news-item` 的 `news-title`、`news-source` 與時間 span；回外殼時直接改 Playwright（snapshot 每則 link 含標題、摘要、來源與時間，時間為 UTC，+8 小時；`curl` SSR 拿到的時間已是香港時間，不必換算；snapshot 存在 `.playwright-mcp/page-*.yml`，用 `grep "link "` 取各則）。很多連結只指向騰訊通用殼頁（無文章 ID）。智通回購/CCASS 快訊偶爾漏日，要與 HKEX 披露交叉核對。較早期間改看 AAStocks／股吧 [2026-11] |
| 富途個股頁 `/quote`、`/announcement`、新聞內文 `news.futunn.com/hk/post/*` | JS 外殼；`/community` 導向登入頁 | 內文改用 Playwright 可取全文（MT Newswires 文章仍需登入）；Playwright 渲染出的發文時間是 UTC，+8 小時才是香港時間 [2026-10] |
| AAStocks | 列表 `aastocks.com/tc/stocks/analysis/stock-aafn/{代號}/0/hk-stock-news/1` 為 SSR；`http://` 會 302 | `curl -L` 抓列表（約 20 則；`/hk-stock-news/2` 回傳與第 1 頁相同，無法翻頁）；單篇 `.../stock-aafn-con/{代號}/{來源}/{ID}/hk-stock-news` 正文就在 SSR HTML（`og:description` 只有約 50 字，不要只取它）。頁頭附沽空金額與比率。市場異動快訊 `aastocks.com/tc/stocks/news/aamm-content/{id}/price-dropped`（`id` 如 `aad2611022327`，前 6 碼為 yyMMdd）不在個股新聞列表內，用 `WebSearch`「{公司名} {代號} 急跌 {月日}」找網址，`curl -L` 單篇可取標題與分鐘級時間；約 3 週後頁面只剩框架，只能引用搜尋標題 [2026-11] |
| 新浪港股新聞 `stock.finance.sina.com.cn/hkstock/news/{代號}.html` | SSR，最新；只列約 30 則（財報後熱門期僅涵蓋約 2 天，冷門期可涵蓋約 1 個月），含券商研報標題 | `curl`（gb18030 解碼）可讀；研報頁 `stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/search/rptid/{id}/` 為 SSR（gb18030），正文在 `div.blk_container`、機構/研究員/日期在 `div.creab`，可取研報摘要全文。即時／收市報價 `curl -H "Referer: https://finance.sina.com.cn" https://hq.sinajs.cn/list=rt_hk{5碼}`（gb18030）：逗號分隔依序為英文名、中文名、開、前收、高、低、現價、漲跌、漲跌%、買、賣、成交額、成交量…日期、時間；yfinance 港股最新一日 OHLC 常為空值時用它補 [2026-11] |
| 新浪財經內文 `finance.sina.com.cn`、`t.cj.sina.cn`、`cj.sina.cn` | 時好時壞，且依路徑不同：`/stock/relnews/`、`/stock/aiassist/`（平台 AI 稿）、`/jjxw/`（2026-11 新華財經稿可讀）與研報頁可讀；`/stock/hkstock/marketalerts/`、`/stock/hkstock/hkstocknews/`、`/stock/aigc/`、`/roll/` 與 `cj.sina.cn/articles/view/*` 常回 curl rc=35（SSL connect error／agent-proxy `ws_closed_mid_exchange`） | 先 `curl -m 10` 試 1 次；正文在 `id="artibody"` 之後、時間在 `span.date`。rc=35 時改用 `firecrawl_scrape`（basic，`formats: ["query"]` directQuote，約 5 credits）2026-11 對 `cj.sina.cn`／`/roll/`／`/jjxw/` 4/4 成功，可取正文與 `publishedTime`；Firecrawl 不可用時改找轉載全文：智通「港股異動」稿用富途 `news.futunn.com/hk/post/*`（§4.3 富途列）；A+H 股的上證報／證券時報轉載稿常在東方財富股吧單篇（§5.5）可讀全文；或 Exa `web_search_exa`（依 §3.6 標註為索引）。都沒有才只引用列表標題 [2026-11] |
| 雪球 `xueqiu.com/S/{代號}` | JS 動態渲染 + WAF；Apify `rag-web-browser` 只拿到 WAF JS 外殼，Playwright 回 HTTP 567「请求异常已被安全策略拦截」（對 AI Agent 限制數小時，2026-11 依舊） | 照 §5.6 [2026-11] |
| 東方財富股吧 `guba.eastmoney.com` | 第一頁是 SSR，但會連續回空殼 | 照 §5.5 [2026-11] |
| 東方財富公告 API `np-anotice-stock.eastmoney.com/api/security/ann?sr=-1&page_size=40&page_index=1&ann_type=A&client_source=web&stock_list={A股代碼}` | JSON，`curl` 可讀 | **A 股公告／季報第一站**（子公司為 A 股時也適用，如 3445 ↔ 688432）：`list[].notice_date`、`art_code`、`title`；PDF 實體 `https://pdf.dfcfw.com/pdf/H2_{art_code}_1.pdf`，`curl` 可直接下載、`pdftotext` 0 個 `(cid:` [2026-11] |
| moomoo 社區 `moomoo.com/hk/stock/{5碼}-HK/community` | Bright Data 回 403「Operations too frequent」或 `Document` 外殼；Apify `rag-web-browser` 回 200 但只有 `Document` 外殼；同一 session 剛用 Playwright 開過富途頁後，Playwright 與 `firecrawl_scrape` 都會被導到 `moomoo.com/403`「Operations too frequent」，Apify `apify--web-fetch`（wait 5000）MCP 60 秒逾時 | **直接用 Playwright**（會導向 `/hant/stock/...`），且**要排在富途新聞之前開**（富途與 moomoo 同屬 Futu，連續請求會觸發頻率限制）；snapshot 內含作者、`yyyy/MM/dd HH:MM` 時間連結與貼文摘要；頁面下半部「Moomoo Insights」與熱門文章是平台推薦、與個股無關，要排除；冷門港股常數月才一則；被 403 後試 2 次即記 ❌ [2026-11] |
| LIHKG | `api_v2/thread/search` 直接打回 `error_code 5`；頁面自己發出的 `api_v2/thread/search` 時好時壞（2026-10 上旬 503、10-22 起多次回 200） | Playwright 開 `lihkg.com/search?q={關鍵字}&sort=desc_create_time`，用 `browser_network_requests`（`filter: thread/search`）看頁面 API 狀態；200 時用 `browser_network_request` 讀回應（在頁內自行 `fetch` 仍回 error 5；`create_time` 為 Unix 秒），503 時試 2 次即記 ❌；200 但內容為 `{"success":0,"error_code":100,"error_message":"沒有相關文章"}` 代表站內確實沒有符合的討論串，記 ⭕；不帶 `filename` 時回應會直接回傳在結果內，最省事（收尾見 §3.4）[2026-11] |
| 新聞農場（如爽報 `yesdaily.com`） | Exa／搜尋常把它排在最前，頁面「发布时间」自動標成抓取當天，內容是多年前的舊公告重貼 | 一律不當新聞；若收錄須註明「假時效，與 {官方來源} 不符」（例：87001「長實 30%→70% 增持管理人」實為舊交易，2026 中報已是長實 100%）[2026-11] |
| 香港經濟日報 `hket.com` | `inews` 回 HTTP 405 真人驗證；`invest.hket.com/article/{id}` 用 `curl` 回 200 但只有約 1.3KB 外殼；搜尋頁 404 | 用 `WebSearch` 搭 `allowed_domains: ["hket.com"]` 找文章網址，再 `firecrawl_scrape`（basic proxy）取標題、作者、發布日期與導言（網址要帶搜尋結果中的完整 slug，只填 `article/{id}` 會全引擎失敗）；後段為會員牆，不必再跑 MCP 鏈 [2026-11] |

## §5.4 HKEXnews 官方 JSON API（港股財報/公告）

1. `https://www1.hkexnews.hk/search/prefix.do?callback=c&lang=EN&type=A&name={代號}` → 取得 `stockId`。
2. `https://www1.hkexnews.hk/search/titleSearchServlet.do?sortDir=0&sortByOptions=DateTime&category=0&market=SEHK&stockId={stockId}&documentType=-1&fromDate={yyyyMMdd}&toDate={yyyyMMdd}&lang=EN&searchType=1`
   - servlet 名稱**大小寫敏感**，必須是 `titleSearchServlet.do`（全小寫回 404）。
   - 不要帶 `t1code` / `t2Gcode` / `t2code`；若一定要帶，值是 `-2`（填 `-1` 會讓任何查詢都回 0 筆）。
3. `lang=ZH` 取中文版；`recordCnt: 0` 代表該期間確實沒有公告。中文 PDF（檔名 `_c.pdf`）用 `pdftotext` 常因缺 Adobe-GB1 字型解析失敗 → 改用 `lang=EN` 回傳的英文版 `FILE_LINK`（同編號去掉 `_c`）。季報日常有兩份英文檔：「Announcement of Unaudited Results…」才是正式季報，「ORA - … Quarterly Results」是業績簡報。
4. PDF 連結 = `https://www1.hkexnews.hk` + `FILE_LINK`。

## §5.5 東方財富股吧（A 股代碼）

- 列表：`curl -A "<UA>" https://guba.eastmoney.com/list,{A股代碼}.html`，頁內 `var article_list = {...}` 含約 40 筆（`post_id`、`post_title`、`post_publish_time`、點閱/留言數）。
- 單篇：`https://guba.eastmoney.com/news,{A股代碼},{post_id}.html`，用 `json.JSONDecoder().raw_decode` 解析 `post_article` 之後的 JSON，取 `post_content`。連續抓取時部分單篇會回約 2.8KB 空殼（無 `post_article`）→ 帶 `Referer: https://guba.eastmoney.com/list,{代碼}.html`、間隔 4 秒重試 1 次；連抓約 3 篇後常整批回空殼且重試無效 → 每吧單篇最多抓 3~4 篇，雙重上市股兩個吧輪流抓，抓不到全文就只引用列表標題 [2026-10]。
- 港股也有股吧：代碼寫 `hk{5碼}`（如 `list,hk00546.html`），格式同上。H 股吧與 A 股吧都可能連續回約 2.8KB 空殼、無 `article_list`（如 `hk03606` 曾空殼而 600660 正常——2026-11 `hk03606` 第 1 次即成功；`003816` 空殼而 `hk01816` 正常），雙重上市股兩邊互為備援；純港股（無 A 股）或單一 A 股吧（如 688432）兩次皆空殼時，`firecrawl_scrape`（basic proxy）可取得完整列表表格（閱讀、評論、標題、最後更新）[2026-11]。

## §5.6 雪球

1. 先用 Bright Data `scrape_as_markdown` 抓 `https://xueqiu.com/S/{代號}`（可跳過內建工具）。單篇長文 `xueqiu.com/{用戶id}/{貼文id}` 也用 Bright Data，第一次常回空白，重試 1 次即可取得全文與「发布于」時間 [2026-10]。2026-11 對 `S/SZ003816` 個股頁 45 秒逾時。
2. Bright Data 失敗或回 `bad_endpoint`（KYC）→ `firecrawl_scrape` 搭 `proxy: stealth`（`waitFor: 3000`、`formats: ["query"]` directQuote，約 5 credits）：2026-11 一次成功取得個股頁討論流（作者、相對時間「N小时前」或 `MM-DD HH:MM`、單篇網址與摘要）。Apify 只拿到 WAF 外殼、Playwright 回 567，兩者不必再試。
3. Bright Data 與 Firecrawl 都不可用（預檢停用或失敗）→ 直接用 Exa `web_search_exa`（query 寫「雪球 {公司名} {代號} 讨论 {年月}」）[2026-11]：
   - 會回傳雪球單篇頁的索引全文，含「发布于 YYYY-MM-DD HH:MM」、回覆數與部分留言（Exa `Published` 欄位標 `Z` 但實為北京時間，以「发布于」為準）。
   - 也常回傳個股的 `/S/{代號}/hots?page=N` 與 `/S/{代號}/time?page=1` 索引頁，列出最近十幾則討論的作者、`MM-DD HH:MM` 與摘要，可用來確認「最新一則是哪天」；索引可能落後數天，查不到新貼文時寫「索引內無新貼文，不能排除漏抓」。
   - 依 §3.6 標註為索引；逐則確認是否屬該公司（留言頁常是其他個股的討論串）。
4. 雙重上市公司的 A 股頁（`SH601318`）與 H 股頁（`02318`）互為備援。
5. **時間要校準**：討論流顯示相對時間，且 Firecrawl 渲染時區是 `America/New_York`；一律以單篇頁的「发布于 YYYY-MM-DD HH:MM」（北京時間）為準。
6. 只抓討論，不從雪球抓財報。

## §7.3-HK 港股財報來源

- **港股**：① HKEXnews JSON API（§5.4）② 富途 `{5碼}-HK/announcement` ③ 官網 IR。（新浪 `/hkstock/notice/` 已停更，不要用）
