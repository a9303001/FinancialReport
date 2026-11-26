# collectStk 參考：日股（含 J-REIT）

> collectStk 站點知識庫（§4）／API SOP（§5）／官網 IR 路徑（§7.3）的「日股（含 J-REIT）」部分。
> 只在處理該市場公司時讀。抓取規則（§3）、存檔與過濾（§8）在 `../SKILL.md`。
> 表格格式：站點 / 網址 | 狀況 | 做法；`[yyyy-mm]` = 最後驗證月份。維護規則見 `../SKILL.md` §10。

## §4.4 日股

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| EDINET API v2 `api.edinet-fsa.go.jp/api/v2` | 官方 API，需 key（雲端環境以網路密鑰注入 header `Ocp-Apim-Subscription-Key`）；2026-11 起 4 執行緒連打約 500 天會在 HTTP 200 的 JSON 內回 `429 Too Many Requests` | **日股年報／半期報第一站**：一律用 `edinet` skill 的 `edinet.py`（已內建退避重試、快取、內容感知去重），流程見 `../SKILL.md` §7.4；EDINET 的 PDF（Producer = EDINET）經 `convert_pdf_to_markdown` 實測 0 個 `(cid:`（4979 半期報 25 頁）。2024/4 起沒有第 1、3 四半期報告書 → 用株探決算短信補 [2026-11] |
| Yahoo!ファイナンス 株つぶやき `finance.yahoo.co.jp/quote/{代碼}.T/post` | SSR，`curl` 可讀 | **日股抓 X 貼文的最佳路徑**：頁面聚合真實 X 貼文，保留 `x.com/{帳號}/status/{id}` 與到分鐘的時間；用 regex `https://x\.com/[A-Za-z0-9_]+/status/[0-9]+` 配對文字，單頁約 8~16 則。**HTML 中每個時間連結（`_cl_link:time`）後面接的是下一則貼文的作者與內文**：作者以該段結尾的 `@帳號` 為準，時間用該帳號貼文網址的 status ID 還原（§4.1 X 列公式），不要沿用相鄰的時間標籤；status ID 換算與頁面日期差距很大（如換算為兩年前）時該則不列入。限制：① J-REIT 沒有此頁（404，不是封鎖）→ 改用 `firecrawl_search` + `site:x.com`；② 社名是一般名詞的公司（如「光通信」）會混入大量無關貼文與假消息，要逐則核對；③ 常混入「爆上げ／ストップ高／四季報上修」導流垃圾帳號（附 `kubu.luhu.jp`、`naturori.com` 等短網址），一律排除，其「自社株買い／増配／優待拡充」說法要對照株探開示清單 [2026-11] |
| Yahoo JP ニュース `finance.yahoo.co.jp/quote/{代碼}.T/news` | SSR，`curl` 可讀；列表含 `news/detail/{id}` 網址、標題、來源與日期（ウエルスアドバイザー、FISCO、トレーダーズ・ウェブ、株探） | 單篇 `curl` 可讀，時間取 JSON-LD `datePublished`；TOPIX 見直し、FISCO 銘柄コメント等常只在這裡出現。列表多為技術面列名（雲抜け、MACD），要逐則核對 [2026-10] |
| Yahoo JP 掲示板 `finance.yahoo.co.jp/quote/{代碼}.T/forum` | SSR，`curl` 一次約 50~80 則，每則有 `/forum/{No}` 網址、分鐘級時間；2026-11 起為新版掲示板（無 `__PRELOADED_STATE__`） | 去標籤後用直線符號串接各欄，用 regex `\|No\.\|(\d+)\|(yyyy/m/d HH:MM)\|報告\|` 切出每則（編號可能是 4 碼，如 4979 為 No.77xx，寫死 `\d{5}` 會 0 筆），正文到 `|返信|` 為止；被刪的編號會跳號。`?page=N` 不會翻頁；熱門大型股只涵蓋約 11 小時、冷門股可涵蓋數月 → 報告註明涵蓋區間，用 5ch / 株つぶやき 補足 [2026-11] |
| 株探 `kabutan.jp` | `curl` 可讀；`/stock/kabuka?code={代碼}&ashi=shin` 回 405 | 個股頁含 PER／PBR／利回り／信用倍率（每週信用餘額明細頁不可用）；日線 `/stock/kabuka?code={代碼}` 為 SSR 表格（日期、始高安終、前日比、出来高）；`/stock/news?code={代碼}&nmode=3` 只列開示，可直接找到決算短信（含英文版）。列表連結指向包裝頁 `kabutan.jp/disclosures/pdf/{yyyymmdd}/{id}/`（HTML），PDF 實體網址 `tdnet-pdf.kabutan.jp/{yyyymmdd}/{id}.pdf` 要從該頁取出。**日股決算短信（速報）最快路徑**；有価証券報告書／半期報告書的詳細版改走 EDINET（`../SKILL.md` §7.4）。新聞第 1 頁只涵蓋約 1 個月，加 `&page=2`、`&page=3` 可再往前；大量保有報告多的公司（如 9435）與大型股決算日（如 7203，含大量市況與技術面列名稿）每頁只涵蓋數天～1 週。列表 `<time>` 有時只顯示收盤時間 15:30，單篇內文開頭的「yyyy年mm月dd日HH時MM分」才是真實發布時間。新聞列表偶爾混入申報人不是該公司的報告（如 9435 頁出現 TYK／大同特鋼的申報），要核對申報人 [2026-11] |
| 株予報 `kabuyoho.jp/sp/reportTarget?bcode={代碼}` | SSR，`curl` 可讀 | 頁頭有「次回発表予定 第N四半期決算：yyyy/mm 上/中/下旬」，可查下次決算時點；另有アナリスト目標株価平均、人數與 PBR/PER 理論株価（含下値目途）；J-REIT 各欄皆為「--」，不必查 [2026-11] |
| みんかぶ `minkabu.jp/stock/{代碼}` | `curl` 405、Apify `rag-web-browser` 405「Human Verification」（AWS WAF）、Playwright 403 | `firecrawl_scrape` 或 Apify `apify/web-fetch` 可讀。有目標株価／株価診断，常與掲示板情緒相反，可當空方對照；`firecrawl_scrape` 搭 `formats: ["query"]` directQuote（約 5 credits）可直接取「目標株価／株価診断／個人予想／アナリスト」一行摘要；J-REIT 顯示「対象外」不可用 [2026-11] |
| 5ch | `find.5ch.net` 已 301 到 `find.5ch.io` | `curl -L "https://find.5ch.io/search?q={公司名}"`（UTF-8）；討論串內文是 Shift_JIS，要 `decode('cp932')`。ニュース速報+／嫌儲 的串標題常誇大，要比對 1 樓轉貼的原始新聞。搜尋結果連結為協定相對網址（`//xxx.5ch.io/test/read.cgi/...`），要補 `https:`；短社名常撞名（如「エスコン」= Ace Combat／エスコンフィールド），要逐串核對 [2026-10] |
| note `note.com` | API 403/404；搜尋頁 `curl` 只拿到外殼 | `firecrawl_scrape` 抓 `note.com/search?q=…&context=note&mode=search&sort=new`（`waitFor: 3000`），Firecrawl 不可用時改 Apify `apify/web-fetch`（markdown 不含文章網址，要再跑一次 `formats: ["links"]`）；單篇 `curl` 可讀，時間取 JSON-LD `datePublished`；付費文章只取得免費段落 [2026-10] |
| 東洋経済オンライン `toyokeizai.net/articles/-/{id}` | SSR，後段付費；`/search/?q=` 404；四季報 `shikiho.toyokeizai.net` 為 JS 外殼 + 付費 | 找文章用全文搜尋 `toyokeizai.net/list/search?fulltext={關鍵字}`（SSR，`curl` 可讀）；單篇要 `curl -L`（會 302 到 `?display=b`，不加 `-L` 只拿到約 116 bytes 轉址頁），取公開段落與 `datePublished`；付費牆不必跑 MCP 鏈 [2026-11] |
| 日経 `nikkei.com/nkd/company/news/?scode={代碼}&ba=1` | SSR，`curl` 可讀；日期在 `m-listItem_time`，付費文章有標記 | 單篇 `curl` 取 `datePublished` 與導言段；付費牆不必跑 MCP 鏈 [2026-10] |
| E-IR 代管的官網 IR 頁（如小糸 `koito.co.jp/english/ir/info/earningsreport/`） | PDF 連結由 `eir-parts` JS 注入，`curl` 看不到 | Playwright `browser_evaluate` 列出連結；PDF 實體在 `ssl4.eir-parts.net/doc/{代碼}/{tdnet\|yuho_pdf\|…}/{id}/00.pdf`，`curl` 可直接下載（`yuho_pdf` = 有価証券報告書全文）[2026-10] |
| JAPAN-REIT.COM `japan-reit.com/meigara/{代碼}/` | `curl` 回 SSL 憑證鏈錯誤（站方問題，**不可**關閉 TLS 驗證）；`WebFetch` 回 503；2026-11 起 `firecrawl_scrape` 也回 SSL 憑證錯誤、Bright Data 45 秒逾時、Apify `apify--web-fetch` 回源站 502 | **直接用 Apify `apify/rag-web-browser`**（`query` 填網址、`maxResults: 1`，約 10 秒、200）：價格、時價總額、利回り、排名（含 NOI 利回り）、業績預測、銘柄ニュース與開示清單。`/news/` 404，改用 `/topic/` 或 `/release/` [2026-11] |
| Shared Research `sharedresearch.jp/ja/companies/{代碼}` | J-REIT 回 404（沒有覆蓋） | 小型股常是唯一的第三方研究覆蓋；J-REIT 不必查 [2026-10] |

## §7.3-JP 日股官網 IR 路徑（EDINET 之外的補充來源）

- J-REIT 經審計英文財報常在官網英文 IR 庫，無 cid 問題：ES-CON（2971）`escon-reit.jp/en/ir/library.html`「Asset Management Reports」欄；HCM（3455）`hcm3455.co.jp/en/ir/library.html`「Semi-annual report」欄。決算後約 1 個月內英文頁常只有 Summary of accounts；頁頂「As of …」日期不會更新，不能判斷新舊。
- 英文版未出時，日文 IR 庫的「資産運用報告」PDF 約決算後 3~3.5 週上架，可直接當該期年報（HCM `hcm3455.co.jp/ja/ir/library.html`；ES-CON `escon-reit.jp/ja/ir/library.html`，`/ir/library.html` 只是殼或回 S3 403）。
- MIRARTH（3492）：日文 IR 庫 `mirarth-reit.com/ja/ir/library.html`（`/ir/library.html` 回 403）列「決算短信／決算説明会資料／資産運用報告／有価証券報告書」四欄，PDF `/file/ir_library_term-{hash}.pdf`，`curl` 可下載、0 個 `(cid:`；資産運用報告約決算發表後 2.5 週上架（第 17 期：10/23 決算 → 11/9 製作），英文 `/en/ir/library.html` 晚一期以上 [2026-11]。
- 光通信（9435）決算短信 PDF 固定為 `hikari.co.jp/assets/pdf/ir/{期}th/{1st|2nd|3rd|4th}_zaimu.pdf`（第 40 期＝2027 年 3 月期），`curl` 可下載。
