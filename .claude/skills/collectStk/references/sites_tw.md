# collectStk 參考：台股

> collectStk 站點知識庫（§4）／API SOP（§5）／官網 IR 路徑（§7.3）的「台股」部分。
> 只在處理該市場公司時讀。抓取規則（§3）、存檔與過濾（§8）在 `../SKILL.md`。
> 表格格式：站點 / 網址 | 狀況 | 做法；`[yyyy-mm]` = 最後驗證月份。維護規則見 `../SKILL.md` §10。

## §4.2 台股

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| 鉅亨網 | 有官方關鍵字 API | **台股新聞與 MOPS 重訊全文第一站**，照 §5.1 [2026-09] |
| 股市爆料同學會 `cmoney.tw/forum/stock/{代號}` | 頁面是空殼，貼文由 API 載入 | **直接打官方 API**，照 §5.2。`curl` 無法出站時改 `firecrawl_scrape`（`waitFor: 4000`、`formats: ["query"]` directQuote）可取首屏約 8 則（作者、時間、內文、`forum/article/{id}` 網址），無法翻頁；確切時間取單篇頁 meta `publishedTime`（+08:00）[2026-11] |
| CMoney Readmo `cmoney.tw/forum/readmo/{uuid}` | SSR，`curl` 可讀，正文在 Nuxt state `content`，JSON-LD 有 `datePublished` | **屬平台 AI 自動生成文章**，引用時標為 AI 內容，不可當網友輿情 [2026-10] |
| MOPS `mops.twse.com.tw` | `curl` 被安全性封鎖頁擋；查詢頁需 JS 表單；Firecrawl 只拿到空表單 | **不要在 MOPS 耗時**：重訊 → §5.1 鉅亨；財報版本核對 → 財報狗 e-report；上櫃進度 → TPEx。真的必要才用 Playwright 表單互動 [2026-09] |
| TWSE 電子書 `doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id={代號}&year={民國年}&seamon=&mtype=A&` | **依來源 IP 封鎖**：雲端容器出口是 Google Cloud 美國 IP（AS396982），`curl` 不論帶什麼 header／cookie／UA，清單頁、step=9、`/pdf/*.pdf` 一律回 947 bytes「因為安全性考量…FOR SECURITY REASONS」封鎖頁（**不可**改 header／瀏覽器去繞）；新版 `mops.twse.com.tw` 未擋 | **第一站：Apify `apify/web-fetch`（unblocker 代理，不吃 Firecrawl 額度；2026-11-23 實測清單、step=9、PDF 皆成功）**：① 清單：`apify--web-fetch` 的 `url` 填 step=1 網址、`formats: ["text"]`（Big5 中文會亂碼，但檔名、檔案大小、上傳日期是 ASCII 可讀）② 下載連結：step=9 網址（見下方）、`formats: ["links"]`，回 `doc.twse.com.tw/pdf/{檔名去副檔名}_{yyyyMMdd_HHmmss}.pdf` ③ PDF 本體：拿到連結後**立刻**用 `call-actor`（`actor: apify/web-fetch`、`waitSecs: 45`、`callOptions.timeout: 300`）跑，`formats: ["markdown"]` 直接得到 PDF 全文（可省 Convert2md），再用 `get-dataset-items`（`fields: markdown`）讀回；`formats: ["raw"]` 可取得原始 PDF（2330 Q3 英文版 1,917,922 bytes，和清單大小相同），但要把檔案搬進容器，環境必須先設 `api.apify.com` network secret（目前沒設）。限制：直接呼叫 `apify--web-fetch` 抓 PDF 會碰到 MCP 60 秒上限，PDF 一定要用 `call-actor`；actor 抓檔上限 120 秒，成敗與檔案大小不完全相關（2330 Q3 合併版 5.3 MB 失敗；2026-11-23 8433 Q3 1.6 MB 兩次皆逾時；2026-11-25 6279 Q3 1.59 MB 23 秒成功、56 頁 0 個 `(cid:`，`contentLengthBytes` 與清單大小相同可作完整性驗證），失敗 2 次即改英文版 `_AIA` 或官網 IR（§7.3）；markdown 太長時 `get-dataset-items` 可能讀不回 → 改官網 IR。Apify 不可用時才用 `firecrawl_scrape`（`formats: ["html"]`，basic 失敗或回快取封鎖頁時改 `proxy: stealth` + `maxAge: 0`，2026-11 對 4417、6121、6781 一次成功）取得完整清單：檔名（`{yyyy}0{季}_{代號}_AI1.pdf` 合併、`_AIA` 英文合併、`_AI2` 個別、`_AIB` 英文個別；年報 `mtype=F` 為 `{FY}_{代號}_{申報日}F04.pdf`）、檔案大小、上傳日期 → 判斷新季報是否已上傳並核對檔案大小；董事會通過到上傳隔 1 天（如 4417 Q2：8/6 董事會 → 8/7 上傳）～1 週以上不等，董事會當天清單不會有新檔，英文版再晚約 1~1.5 個月。下載連結：對 `t57sb01?co_id={代號}&colorchg=1&kind=A&step=9&filename={檔名}`（年報 `kind=F`）跑 `firecrawl_scrape`（stealth、html），回傳頁含 `doc.twse.com.tw/pdf/{檔名去副檔名}_{yyyyMMdd_HHmmss}.pdf`；拿到網址後立刻 `curl`（帶 UA）下載實體檔，時好時壞（2026-11 對 1521 成功取得完整 PDF，大小與清單相符）；若回約 947 bytes 封鎖頁（MCP 也無法存二進位檔）→ PDF 本體改從官網 IR 下載（§7.3）。2026-11-23 對 8433：step=9 取得連結後 `curl` 第一次傳了 360 KB 即逾時（不支援續傳 rc=33），重抓即回 947 bytes 封鎖頁 → 不必再試。**不要**用 `firecrawl_scrape`（`parsers: ["pdf"]`）或 Bright Data `scrape_as_markdown` 直接解析 `doc.twse.com.tw/pdf/*.pdf`（2026-11 對 2249 各 2 次皆逾時）；官網也沒有時，單季損益表改用 MoneyDJ 的 MOPS 轉載稿（見 MoneyDJ 列），報告列出檔名與網址待下次補抓 [2026-11] |
| MOPS 法說會簡報 PDF `mopsov.twse.com.tw/nas/STR/{代號}{yyyyMMdd}M001.pdf` | 和 TWSE 電子書同樣依 IP 封鎖：2026-11 起雲端容器 `curl` 帶 cookie 也回 307 + 947 bytes 封鎖頁（舊的 cookie 做法已失效） | `call-actor`（`actor: apify/web-fetch`、`formats: ["markdown"]`、`waitSecs: 45`）→ `get-dataset-items`（`fields: markdown`）取得簡報全文（2026-11-23 2330 Q3 法說 458,760 bytes PDF → 11 頁全文，17 秒，0 個 CID 亂碼）；要原始 PDF 改 `formats: ["raw"]`（同上，需要 `api.apify.com` network secret 才能搬進容器）。從台灣 IP 執行時（本機）`curl -sL -c cj -b cj {URL} -o out.pdf` 仍可用，下載後用 `pdfinfo` 確認完整。簡報連結可從 `poorstock.com/earningcall/{代號}` 取得 [2026-11] |
| 財報狗 `statementdog.com/analysis/{代號}/...` | `curl` 回 202 空內容；Apify `rag-web-browser` 回 202 + `x-amzn-waf-action: challenge`（AWS WAF）；Playwright 回 403；Bright Data 45 秒逾時 | 只有 `firecrawl_scrape`（basic proxy）可取得頁面，且只對 e-report 穩定（能列出 `doc.twse.com.tw` 原始檔名以核對年度/季別）；個股首頁 `/analysis/{代號}` 時好時壞（2026-11 同日一次全引擎失敗、一次 basic + `formats: ["query"]` 成功取得市場共識 EPS 與本益比／殖利率），失敗 2 次即記 ❌；亮點／風險內文為會員牆，社群討論目前抓不到。Firecrawl 沒額度時無替代路徑（Exa 索引的 e-report 版本落後，不可用來判斷是否有新財報）[2026-11] |
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

- **台股**：① MOPS/TWSE 電子書（§4.2；英文版 `_AIA.pdf` 常晚中文 `_AI1.pdf` 1~1.5 個月，有就優先用）② 財報狗 e-report（§4.2）③ 官網 IR（見下方已驗證路徑）。確認「是否已公告」用 §5.1 鉅亨（給的是重訊全文，不是財報 PDF）。興櫃公司只有半年報與年報，不會有 Q1/Q3。
  - 台產 2832：`tfmi.com.tw/investors-Financial` 列出 `/Files/TFMI/各單位上傳/財務部/財務報告/{yyyy}年/{民國年}年第{N}季財務報告.pdf`，`curl` 可下載，上架晚於 TWSE。
  - 胡連 6279：`www.hulane.com.tw/financials`（季報）與 `/conferences-and-meetings`（股東會年報）為 SSR；PDF `/admin/uploads/Investor/財務報告/{yyyy}/胡連{民國年}Q{N}合併財報電子書.pdf`、`/admin/uploads/Investor/股東會/{yyyy}/胡連-{FY}年報(中文版).pdf`，`curl` 可下載、0 個 `(cid:`；季報上架晚於 TWSE（2026-11-25 Q3 仍未上架，TWSE 11/11 已上傳）→ 先走 TWSE；舊站 `product.hulane.com` 停更。
  - 新普 6121：`simplo.com.tw/download.php?lang=tw&tb=2`（財報）／`tb=4`（法說）；下載鈕 `go_download('{base64}')` 解碼後 POST `include/download.php`（參數 `dl`），回傳頁含 `simplo.com.tw/archive/doc/download/{yyyy}Q{N}_新普合併財報.pdf`，`curl` 可下載。
  - 湧盛 2249：`young-shine.com.tw/financialreport.html` 為 SSR，PDF 在 `pdf/財務報表/{民國年}Q{N}*.pdf`，`curl` 可下載，但只上架半年報與年報（2026-11 仍只到 114 年第四季），季報要靠 TWSE。
  - AES-KY 6781：`advancedenergysolution.com.tw/download.php?lang=tw&tb=3&cid=-1` 上架晚 TWSE 數月，下載為 JS `go_download`，不能直接 curl。
  - 弘帆 8433：`www.bonfame.com/zh-tw/company.php?act=finance`（https 回 curl rc=35，改用 `http://`）SSR 列出「第N季度財報／年度合併財報」，PDF 在 `http://www.bonfame.com/zh-tw/data/finance/cover/{id}.pdf`，`curl` 可下載、0 個 `(cid:`（PDF 有加密但可轉檔）；上架比 TWSE 晚（2026-11-23 仍只到 115 年第二季）。
