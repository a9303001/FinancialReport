# collectStk 參考：台股

> collectStk 站點知識庫（§4）／API SOP（§5）的「台股」部分（輿情、新聞、籌碼）。台股財報（年報／季報／法說簡報）來源已移到 mops skill。
> 只在處理該市場公司時讀。抓取規則（§3）、存檔與過濾（§8）在 `../SKILL.md`。
> 表格格式：站點 / 網址 | 狀況 | 做法；`[yyyy-mm]` = 最後驗證月份。維護規則見 `../SKILL.md` §10。

## §4.2 台股

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| 鉅亨網 | 有官方關鍵字 API | **台股新聞與 MOPS 重訊全文第一站**，照 §5.1 [2026-09] |
| 股市爆料同學會 `cmoney.tw/forum/stock/{代號}` | 頁面是空殼，貼文由 API 載入 | **直接打官方 API**，照 §5.2。`curl` 無法出站時改 `firecrawl_scrape`（`waitFor: 4000`、`formats: ["query"]` directQuote）可取首屏約 8 則（作者、時間、內文、`forum/article/{id}` 網址），無法翻頁；確切時間取單篇頁 meta `publishedTime`（+08:00）[2026-11] |
| CMoney Readmo `cmoney.tw/forum/readmo/{uuid}` | SSR，`curl` 可讀，正文在 Nuxt state `content`，JSON-LD 有 `datePublished` | **屬平台 AI 自動生成文章**，引用時標為 AI 內容，不可當網友輿情 [2026-10] |
| MOPS／TWSE 電子書／法說會簡報 PDF／官網 IR 財報 | **已移到 mops skill** | 台股年報、季報、法說簡報一律用 mops skill（`.claude/skills/mops/SKILL.md`；站點行為在 `.claude/skills/mops/references/sources.md`、路徑成敗在 `learned.json`），本檔不再維護 [2026-11] |
| 財報狗 `statementdog.com/analysis/{代號}/...` | `curl` 回 202 空內容；Apify `rag-web-browser` 回 202 + `x-amzn-waf-action: challenge`（AWS WAF）；Playwright 回 403；Bright Data 45 秒逾時 | 只有 `firecrawl_scrape`（basic proxy）可取得頁面，且只對 e-report 穩定（能列出 `doc.twse.com.tw` 原始檔名以核對年度/季別）；個股首頁 `/analysis/{代號}` 時好時壞（2026-11 同日一次全引擎失敗、一次 basic + `formats: ["query"]` 成功取得市場共識 EPS 與本益比／殖利率），失敗 2 次即記 ❌；e-report 核對財報版本的用法見 `.claude/skills/mops/references/sources.md` §S3；亮點／風險內文為會員牆，社群討論目前抓不到。Firecrawl 沒額度時無替代路徑（Exa 索引的 e-report 版本落後，不可用來判斷是否有新財報）[2026-11] |
| TPEx 申請上櫃清單 `tpex.org.tw/openapi/v1/tpex_esb_applicant_companies` | JSON API，`curl` 可讀 | 含申請日、審議會日、董事會核准日、主辦承銷商；查興櫃股是否申請轉上櫃用這個 [2026-10] |
| Yahoo 股市 `tw.stock.yahoo.com/quote/{代號}.TW` / `.TWO` | SSR，`curl` 可讀。上市/上櫃股的 `/news` 可讀（HTML 內有文章 URL 與 `pubtime` 毫秒，但兩者在 HTML 中順序不固定）；興櫃股的 `/news` 會 302 回個股頁 | 上市櫃股可當台股新聞備援；**發布時間取各單篇 JSON-LD `datePublished`**，不要按位置配對 `pubtime`。月營收自動稿標題固定寫「年增」，負值（如「年增-68.63%」）即年減，不可誤讀。興櫃股「成交」可能是造市商報價、總量可能為 0，判斷價格要同時看總量 [2026-11] |
| 經濟日報 `money.udn.com` | 搜尋頁 `search/result/1001/{關鍵字}` 與單篇 `money/story/{cate}/{id}` 皆 SSR，`curl` 可讀 | 正文在 `article-body__editor`，時間取 JSON-LD `datePublished`。搜尋頁失效時用 `WebSearch` 搭 `site:money.udn.com` 找網址。-KY 股搜尋關鍵字要去掉「-KY」（`AES-KY` 只回舊文，`AES` 才有新文）[2026-11] |
| MoneyDJ `moneydj.com` | 搜尋 `kmdj/search/list.aspx?_QueryType_=NW&_Query_={公司名}` 為 SSR（含到秒的時間）；**少了 `_QueryType_=NW` 會 302 回首頁**；關鍵字含連字號（如 `AES-KY`）也會 302，改查 `AES` 或代號；單篇 `kmdj/news/newsviewer.aspx?a={GUID}` 為 SSR | 搜尋也會命中每日「投信買賣超排行」「鉅額交易」「上市櫃公司董監質設異動公告」（多家合併表格，正文中搜尋公司名取該列：身份、設質/解質/累積張數、質權人），可當籌碼資料；每季「櫃買中心：Q{N}上櫃認購/售權證標的」名單的「減少公司」可看出個股是否因流動性被剔除權證標的；「上櫃認購(售)權證彙總表」可看到新發行的個股權證。也會命中名稱相近的其他公司，要逐則核對。時間取 JSON-LD `datePublished`、正文取 JSON-LD `articleBody` 財報公布日會有兩篇 MOPS 轉載：「董事會通過第N季合併財務報告」重訊（累計營收至 EPS、期末總資產／總負債／權益）與「第N季綜合損益表，每股盈餘X元」（JSON-LD `articleBody` 含單季、去年同季、本期累計、去年同期累計全表），可在財報 PDF 抓不到時當損益表來源；鉅亨關鍵字索引常晚於 MoneyDJ（2026-11 對 2249 晚 10 天仍未收錄 Q3 重訊）[2026-11] |
| 富聯網 `ww2.money-link.com.tw/RealtimeNews/NewsContent.aspx?SN={id}&PU=0010` | SSR，`curl` 可讀；轉載時報資訊《興櫃市場》委買／委賣前 10 名等盤中排行（委買張、委賣張、成交張、股價、漲跌） | 興櫃冷門股的籌碼參考：用 `firecrawl_search`（`"{公司名}" 興櫃`、`tbs: qdr:m`）找網址；正文是全形空白對齊的表格，去標籤後在公司名附近取該列；發布時間在標題下方（到分鐘）。屬自動排行稿，無分析內容 [2026-11] |
| HiStock `histock.tw/stock/{代號}` | 個股頁 `curl` 可讀；舊討論區 `/stock/{代號}/討論` 404；`news.aspx` 渲染後仍空白 | 只用來取已發行股數、PE/PB、三大法人、融資券、借券；其新聞/重訊區更新時好時壞（2026-11 對 6781 已同步到當週，其他股曾落後數月），判斷近期公告以 §5.1 鉅亨為準 [2026-11] |
| 工商時報 `ctee.com.tw/search?q=`、旺得富 `wantrich.chinatimes.com/search?q=` | 搜尋路徑 404（站方沒有此頁） | 不跑 MCP 鏈，用 `firecrawl_search` / Bright Data `search_engine` 搭 `site:` 找個別文章 [2026-10] |
| PTT `ptt.cc/bbs/{板名}/search?q={關鍵字}` | SSR，`curl` 帶 cookie `over18=1` 可讀；列表含標題、`M.{秒}.A.xxx.html` 網址與月/日 | 冷門股多年無新文是常態（列表日期不含年份，年份從網址內 Unix 秒數換算）；Stock 板查完可再查產業板（如 `Bicycle`）[2026-10] |
| Dcard | 搜尋 API、Apify `rag-web-browser`、Playwright 皆 403 Cloudflare | `firecrawl_search` + `site:dcard.tw {公司名} {代號}` 取索引（含發文日期），單篇可用 `firecrawl_scrape`（basic）讀全文；Firecrawl 沒額度時改用 Exa `web_search_exa` 或 `WebSearch` 索引確認有無新文並依 §3.6 加註 [2026-11] |
| ToAlpha 法說 memo `toalpha.tw/memo/{代號}/{yyyy-MM-dd}` | SSR，`curl` 可讀；Q&A 需登入 | 公開段落有管理層語氣與一句話指引摘要；列表頁 `toalpha.tw/memo` 有法說隔天漲跌幅 重訊頁 `toalpha.tw/stock/{代號}/material` 對 `curl` 回 Cloudflare「Just a moment」，改用 Exa `web_search_exa` 索引（含重訊全文、發言時間與當日漲跌）[2026-11] |
| Mobile01 討論串 | `curl`、Playwright 皆 403（Akamai）；Apify `rag-web-browser` 直接給網址 403，但用 Google 搜尋模式（`query` 填關鍵字）曾以 200 取得討論串頁 | `firecrawl_search` + `site:mobile01.com {公司名} {代號}` + `tbs: qdr:m` 找文章（只放兩字公司名會被「胡搞瞎搞」之類字串誤配），再 `firecrawl_scrape` 單篇（含發文時間）；Firecrawl 沒額度時改用 Apify `rag-web-browser` 搜尋模式，或 Exa `web_search_exa` 取索引 [2026-11] |
| yfinance 台股日線（`{代號}.TW` / `.TWO`） | `Date` 欄是前一天 UTC 16:00 | 加 8 小時（即日期 +1）才是台北交易日 [2026-10] |
| Goodinfo `goodinfo.tw` | Bright Data 60 秒逾時 | 用 `firecrawl_search` 取索引，Firecrawl 沒額度時改用 Exa `web_search_exa`，依 §3.6 加註 [2026-10] |
| 券商承銷公告頁（嘉實資訊 iframe） | Firecrawl 只拿到 iframe 外殼 | 新股申購/承銷日程改抓 HiStock 公開申購頁（靜態表格）[2026-09] |

## §5.1 鉅亨網關鍵字 API（台股新聞 + MOPS 重訊全文）

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

## §5.2 股市爆料同學會（CMoney）官方 API

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

## §7.3-TW 台股財報來源與官網 IR

- **已移到 mops skill**：財報來源順序、TWSE 電子書操作、各公司官網 IR 路徑見 `.claude/skills/mops/references/sources.md`（§S1～S4），公司專屬經驗用 `mops.py lessons --code {代號}` 查。新發現的台股財報來源寫到那裡，不寫回本檔（collectStk §10.4）。
