# mops 參考：台股財報來源知識庫

> mops skill 的「站點行為」與「官網 IR 路徑」。流程與指令在 `../SKILL.md`；路徑成敗統計在 `../learned.json`（script 自動維護）。
> 表格格式：站點 / 網址 | 狀況 | 做法；`[yyyy-mm]` = 最後驗證月份。維護規則見 `../SKILL.md` §7.3（合併不追加、刪除過時、只留結論）。

## §S1 官方來源（TWSE／MOPS）

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| TWSE 電子書清單 `doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id={代號}&year={民國年}&seamon=&mtype={A\|F}&` | **依來源 IP 封鎖**：雲端容器（Google Cloud 美國 IP）不論 header／cookie／UA 一律回 947 bytes「因為安全性考量…FOR SECURITY REASONS」頁（不可嘗試繞過）；台灣 IP 可直連，頁面 Big5 | `mtype=A` 財報（`year` = 資料年度）、`mtype=F` 股東會資料（`year` = 開會年度，年報資料年度 = 開會年度 −1）。雲端：`firecrawl_scrape`（`formats: ["html"]`、`proxy: "stealth"`、`maxAge: 0`、`onlyMainContent: false`）回 UTF-8 HTML，含說明欄 [2026-11] |
| TWSE 電子書下載頁 `…t57sb01?step=9&kind={A\|F}&co_id={代號}&filename={檔名}&colorchg=1` | 同上 IP 封鎖；回傳頁含 `doc.twse.com.tw/pdf/{檔名去副檔名}_{yyyyMMdd_HHmmss}.pdf` | 雲端用 `firecrawl_scrape`（stealth、html）取連結；連結帶時間戳，拿到就立刻抓 PDF [2026-11] |
| TWSE 電子書 PDF `doc.twse.com.tw/pdf/*.pdf` | 雲端 `curl` 時好時壞（多半 947 bytes 封鎖頁；曾傳 360 KB 後斷線，不支援續傳） | 雲端首選 Apify `call-actor`（`apify/web-fetch`、`formats: ["raw"]`）→ `get-dataset-items`（`fields: "raw,fetch.contentLengthBytes"`）→ 結果過大會自動存檔 → `mops.py ingest`。actor 抓檔上限 120 秒、無逾時參數，成敗看 TWSE 當下回應速度（同約 1.6 MB：6279 95 秒成功；1264 第 1 次逾時、同連結重跑 79 秒成功）→ 逾時就重跑一次；step=9 連結數分鐘內可重用。`firecrawl_scrape`（`parsers: ["pdf"]`）與 Bright Data 直接解析 PDF 各 2 次皆逾時，**不要用** [2026-11] |
| MOPS 新版 `mops.twse.com.tw/mops/#/web/t57sb01_q1`、舊版 `mopsov.twse.com.tw` | 雲端同樣 947 bytes 封鎖；查詢頁需 JS 表單，Firecrawl 只拿到空表單 | **不要在 MOPS 網頁耗時**：財報檔一律走 TWSE 電子書；重訊走鉅亨（collectStk §5.1）[2026-11] |
| MOPS 法說會簡報 `mopsov.twse.com.tw/nas/STR/{代號}{yyyyMMdd}M001.pdf` | 雲端 307 + 947 bytes 封鎖頁 | Apify `call-actor`（`apify/web-fetch`、`formats: ["markdown"]`）→ `get-dataset-items`（`fields: markdown`）取全文（2330 Q3 法說 11 頁 17 秒、0 CID）；本機台灣 IP 可 `curl -sL -c cj -b cj`。簡報連結可從 `poorstock.com/earningcall/{代號}` 取得；存成 `{代號}_Presentation_{yyyyMMdd}.md` [2026-11] |
| TWSE OpenAPI `openapi.twse.com.tw/v1/opendata/t187ap03_L`（上市公司基本資料） | 雲端可直連 JSON | `mops.py lookup` 的資料來源：代號、簡稱、英文簡稱、**已發行普通股數**（每股化用）、官網 [2026-11] |
| TPEx OpenAPI `tpex.org.tw/openapi/v1/mopsfin_t187ap03_O`（上櫃）、`mopsfin_t187ap03_R`（興櫃） | 雲端可直連 JSON；舊路徑 `mopsfe_t187ap03_O` 回 302 | 同上；`DateOfListing` 可看出興櫃轉上櫃（2249：2026-10-22）[2026-11] |
| TWSE `twse.com.tw/rwd/zh/api/codeQuery`、`isin.twse.com.tw` | 雲端 307／947 bytes 封鎖 | 查代號改用上面的 OpenAPI [2026-11] |

## §S2 清單檔名規則（t57sb01）

| 檔名 | 意義 | mops 處理 |
| :--- | :--- | :--- |
| `{yyyy}0{季}_{代號}_AI1.pdf` | IFRS 合併財報（中文） | 季報首選；`{yyyy}04` = 年度財報（Q4） |
| `_AI3` / `_AI2` | 個體 / 個別財報（中文；無子公司的公司只有個體） | 沒有合併版時才選 |
| `_AIA` / `_AIC` / `_AIB` | 英文版 合併 / 個體 / 個別 | `--lang en` 或中文 CID 亂碼時用；通常晚中文 1~1.5 個月 |
| `{FY}_{代號}_{股東會日}F04.pdf` | 股東會年報（中文） | 年報首選；說明欄「股東會年報(尚未適用永續揭露準則)」 |
| `FE4` / `FE6` | 英文版股東會年報（FE6 見於 KY 公司 6781） | 英文偏好或中文缺件時用 |
| `F01` 開會通知、`F02` 議事手冊、`F05` 議事錄、`F13` 議案參考、`F17` 年報前十大股東關係表、`FE1`/`FE2` 英文版 | 非年報 | 一律忽略（說明欄含「前十大」也排除） |

## §S3 輔助來源（判斷「是否已公告」、PDF 抓不到時的替代）

| 站點 / 網址 | 狀況 | 做法 |
| :--- | :--- | :--- |
| 鉅亨網關鍵字 API | 雲端可直連 | 確認「董事會通過第 N 季財報」重訊是否已出（collectStk §5.1）；董事會到 TWSE 上傳隔 1 天～1 週以上，董事會當天清單不會有新檔 [2026-11] |
| 財報狗 e-report `statementdog.com/analysis/{代號}/e-report` | 只有 `firecrawl_scrape`（basic）穩定 | 可列出 `doc.twse.com.tw` 原始檔名，核對年度／季別；Exa 索引版本落後，不可用來判斷有無新財報 [2026-11] |
| MoneyDJ MOPS 轉載稿 | SSR，`curl` 可讀 | 財報 PDF 全部路徑都失敗時，「第N季綜合損益表，每股盈餘X元」轉載（JSON-LD `articleBody`）可暫代損益表；**只能當速報，不可存成 `_Quarter_` 財報檔**，報告列出待補檔名 [2026-11] |

## §S4 官網 IR 路徑（`pdf.company_ir` 路徑；上架通常晚於 TWSE）

- 台產 2832：`tfmi.com.tw/investors-Financial` 列出 `/Files/TFMI/各單位上傳/財務部/財務報告/{yyyy}年/{民國年}年第{N}季財務報告.pdf`，`curl` 可下載 [2026-11]。
- 胡連 6279：`www.hulane.com.tw/financials`（季報）、`/conferences-and-meetings`（股東會年報），SSR；PDF `/admin/uploads/Investor/財務報告/{yyyy}/胡連{民國年}Q{N}合併財報電子書.pdf`、`/admin/uploads/Investor/股東會/{yyyy}/胡連-{FY}年報(中文版).pdf`，`curl` 可下載、0 CID；舊站 `product.hulane.com` 停更 [2026-11]。
- 新普 6121：`simplo.com.tw/download.php?lang=tw&tb=2`（財報）／`tb=4`（法說）；下載鈕 `go_download('{base64}')` 解碼後 POST `include/download.php`（參數 `dl`），回傳頁含 `simplo.com.tw/archive/doc/download/{yyyy}Q{N}_新普合併財報.pdf` [2026-11]。
- 湧盛 2249：`young-shine.com.tw/financialreport.html`，PDF 在 `pdf/財務報表/{民國年}Q{N}*.pdf`；只上架半年報與年報 [2026-11]。
- AES-KY 6781：`advancedenergysolution.com.tw/download.php?lang=tw&tb=3&cid=-1`，下載為 JS `go_download`，不能直接 `curl`；上架晚 TWSE 數月 [2026-11]。
- 弘帆 8433：`http://www.bonfame.com/zh-tw/company.php?act=finance`（https 回 curl rc=35），PDF 在 `http://www.bonfame.com/zh-tw/data/finance/cover/{id}.pdf`，有加密但可轉檔 [2026-11]。
