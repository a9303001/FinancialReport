---
name: collectStk
description: 收集個股「最新財務報告（2 年報 + 1 季報）」與「近三個月輿情討論/新聞」，存入公司資料夾，轉 Markdown 後產出執行報告並 push。輸入 COMPANY_TICKER 與 COMPANY_NAME。日股年報／季報詳細版（有価証券報告書、半期報告書）一律先用 edinet skill 下載、美股（含 ADR）10-K／10-Q／20-F／6-K 一律先用 edgar skill 下載，再用 Convert2md 轉 md。開工先做 MCP 預檢（§3.0）；收工前必跑自我檢查（§10），發現本 Skill、腳本或相依 skill 有錯就直接修正並驗證。（舊名 CollectsentimentAndReports）
---
/goal
# collectStk — 執行指南

> **任務**：對指定公司 ⓪ 預檢 MCP → ① 建資料夾並盤點 → ② 補齊最新財報（2 份年報 + 1 份季報）→ ③ 收集近三個月輿情/新聞 → ④ 轉 Markdown 並驗證 → ⑤ 自我檢查並修正 Skill → ⑥ 寫執行報告並 push。
> 適用所有 AI（Claude / Gemini，含輕量模型）。照章節順序一步一步做，不要跳步。

## 0. 六條底線（違反任一 = 任務失敗）

1. **防幻覺**：只記錄真實抓到的內容，附真實 URL 與真實發布時間。抓不到就照 §8.5 誠實記錄，**嚴禁**用訓練資料補內容、捏造連結或推測日期。
2. **不從本 repo 的線上倉庫收集**：嚴禁從 GitHub `a9303001/FinancialReport` 下載財報或新聞；嚴禁訪問 `macrotrends.net`。（本機資料夾已有的檔案可盤點與回查，見 §7.1、§8.3）
3. **即時存檔**：每下載完一份財報、每抓完一個來源，立刻寫檔。
4. **不卡死**：抓取照 §3 的固定順序與次數上限，不無限重試、不空等背景任務；預檢判定停用的 MCP 整輪不再呼叫。
5. **不碰帳號設定**：連接器權限、登入、額度只有使用者能改。AI 只負責偵測、改走替代路徑、在報告寫明修法（§3.0.3）。
6. **錯了就修**：執行中發現本 Skill、`references/`、`scripts/`、`edinet`、`edgar`、`Convert2md` 的指示或程式有錯（網址失效、參數錯、腳本崩潰、命名規則與實際不符），收工前照 §10 修正並重新驗證，不可只在報告抱怨。

---

## 1. 參數、工具與檔案

| 參數 | 說明 | 範例 | 若缺失 |
| :--- | :--- | :--- | :--- |
| `COMPANY_TICKER` | 股票代碼（港股補齊 5 碼） | `2881`、`UHS`、`3445`、`02318` | 必填，立刻詢問 |
| `COMPANY_NAME` | 公司名稱 | `富邦金`、`Universal Health Services` | 用代碼搜尋查出 |

工具名一律視為「動作」，用你手上對應的工具完成，名字對不上不要卡住：

| 動作 | Claude | Gemini / 其他 |
| :--- | :--- | :--- |
| 網路搜尋 | `WebSearch` | `search_web` / `google_search` |
| 抓網頁 | `WebFetch` | `read_url` / `read_url_content` |
| 指令 / 下載 / 跑腳本 | `Bash`（`curl`、`python` 等） | `run_shell_command` |
| 讀寫檔 | `Read` / `Edit` / `Write` | `view_file` / `write_file` / `edit_file` |
| MCP 爬取 | `firecrawl_*`、Bright Data `scrape_as_markdown` / `search_engine`、`mcp__Apify__*`、`mcp__playwright__*`、Exa `web_search_exa` | 已連接的同名 MCP 工具 |
| 呼叫其他 Skill | `Skill`（`edinet`、`edgar`、`Convert2md`） | 直接讀該 skill 的 `SKILL.md` 照做 |

- **內建工具** = `WebSearch` / `WebFetch` / `curl` 這類原生工具。
- `curl` 一律帶瀏覽器 User-Agent（下文寫 `<UA>`）：`-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"`。
- Claude 的 MCP 工具若是延遲載入（deferred），先用 `ToolSearch`（如 `select:mcp__brightdata__scrape_as_markdown`）載入再呼叫；搜不到才算「環境沒連上」。
- 下文路徑：`<REPO>` = repo 根目錄；`<SK>` = `<REPO>/.claude/skills/collectStk`（Gemini 用 `.agents/skills/collectStk`，內容相同）；`<SCRATCH>` = 暫存目錄；`<資料夾>` = 公司資料夾絕對路徑。

本 Skill 的檔案（`.claude/skills/collectStk/` 為唯一編輯來源，`.agents/` 是鏡像）：

| 檔案 | 用途 | 何時讀／跑 |
| :--- | :--- | :--- |
| `SKILL.md` | 流程與通用規則 | 每次 |
| `references/sites_us_global.md` | §4.1 英文圈通用、§4.5 印尼、§5.3 Reddit、美股官網 IR 備援 | 美股；其他市場查 X／Reuters／Reddit 時 |
| `references/sites_tw.md` | §4.2 台股站點、§5.1 鉅亨、§5.2 CMoney、台股官網 IR | 台股 |
| `references/sites_hk_cn.md` | §4.3 港股/中國站點、§5.4 HKEX、§5.5 股吧、§5.6 雪球、港股財報來源 | 港股、A+H 股 |
| `references/sites_jp.md` | §4.4 日股站點、日股官網 IR 補充 | 日股、J-REIT |
| `scripts/inventory.py` | 盤點資料夾已有期別、輿情涵蓋到哪天 | Phase 1 |
| `scripts/check_md.py` | 財報 md 驗證（大小、CID、公司名）＋清圖片連結＋補來源 | Phase 4 |
| `scripts/selfcheck.py` | Skill 自我檢查（路徑、§引用、腳本編譯、鏡像同步、過期標記） | Phase 5 |
| `.claude/skills/edinet/scripts/edinet.py` | 日股 EDINET 下載、驗證、自檢（edinet skill） | Phase 2、4、5 日股 |
| `.claude/skills/edgar/scripts/edgar.py` | 美股 SEC EDGAR 下載、驗證、自檢、經驗學習（edgar skill） | Phase 2、4、5 美股 |

MCP 分兩類，故障原因與修法不同：

| 類型 | 成員 | 設定位置 | 常見故障 |
| :--- | :--- | :--- | :--- |
| 本機 MCP | Playwright、yfinance、sec-edgar-mcp（只查 XBRL 數字／8-K；財報全文改用 edgar skill）、pymupdf4llm-mcp（`convert_pdf_to_markdown`） | repo `.mcp.json`（與 `.claude/mcp_config.json` 同內容），session 啟動時在本機起程序 | 啟動失敗、逾時 |
| claude.ai 連接器 | Firecrawl、Bright Data、Apify、Exa | 使用者 claude.ai 帳號的 Connectors 設定，**每個工具各自有權限** | 跳出核准卡片／`MCP tool call requires approval`、需重新登入、額度用盡 |

---

## 2. 流程總覽

| Phase | 內容 | 章節 |
| :--- | :--- | :--- |
| 0 | MCP 預檢，建立本輪「可用工具表」；開一個 `<SCRATCH>/collectStk_issues.md` 隨手記「Skill 寫的和實際不符」的地方 | §3.0、§10.1 |
| 1 | 建立/確認公司資料夾，跑 `inventory.py` 盤點；讀該市場的 `references/` 檔 | §6、§7.1 |
| 2 | 下載最新財報（日股：edinet skill；美股：edgar skill） | §7 |
| 3 | 收集近三個月輿情/新聞 | §8 |
| 4 | 呼叫 `Convert2md` 轉 Markdown，跑 `check_md.py` 驗證 | §9 |
| 5 | 自我檢查並修正 Skill／腳本（`selfcheck.py --fix` + 修 issues 清單） | §10 |
| 6 | 寫執行報告、commit、push | §11 |

多家公司同日執行：每家一個子代理人做 Phase 1~4，主代理人統一做 Phase 0、5、6。

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


## 4. 站點知識庫（依市場拆在 `references/`）

> 每個站點一列：站點 / 網址 | 狀況 | 做法，`[yyyy-mm]` 是最後驗證月份。**只讀本次公司所屬市場的檔**（加上英文圈通用檔），不必整包讀。

### 4.0 章節索引

| 章節 | 內容 | 檔案 |
| :--- | :--- | :--- |
| §4.1 | 通用 / 英文圈（Reddit、X、Reuters、Seeking Alpha、分析師評級、Yahoo Finance…） | `references/sites_us_global.md` |
| §4.2 | 台股（TWSE 電子書、MOPS、財報狗、鉅亨、MoneyDJ、PTT、Dcard…） | `references/sites_tw.md` |
| §4.3 | 港股 / 中國（HKEX 權益披露、富途、AAStocks、新浪、雪球、股吧、LIHKG…） | `references/sites_hk_cn.md` |
| §4.4 | 日股（Yahoo JP、株探、みんかぶ、5ch、note、JAPAN-REIT.COM…） | `references/sites_jp.md` |
| §4.5 | 印尼（美股 ADR 母股） | `references/sites_us_global.md` |

## 5. 已驗證的 API / 站點 SOP（同樣在 `references/`）

| 章節 | 內容 | 檔案 |
| :--- | :--- | :--- |
| §5.1 | 鉅亨網關鍵字 API（台股新聞 + MOPS 重訊全文） | `references/sites_tw.md` |
| §5.2 | 股市爆料同學會（CMoney）官方 API | `references/sites_tw.md` |
| §5.3 | Reddit（Apify Actor） | `references/sites_us_global.md` |
| §5.4 | HKEXnews 官方 JSON API（港股財報/公告） | `references/sites_hk_cn.md` |
| §5.5 | 東方財富股吧 | `references/sites_hk_cn.md` |
| §5.6 | 雪球 | `references/sites_hk_cn.md` |
| §7.4 | EDINET（日股年報／半期報） | 本檔 §7.4 + `edinet` skill |
| §7.5 | SEC EDGAR（美股 10-K／10-Q、ADR 20-F／6-K） | 本檔 §7.5 + `edgar` skill |

---

## 6. Phase 1 — 建立資料夾

- 台/日/港股：`<REPO>/{代碼}{名稱}/`（例：`2881富邦金/`）；美股：`<REPO>/{代碼}/`（例：`UHS/`）。
- `Routines_collectStk.md` 輪替表有寫資料夾名稱時，以表上為準。不存在就建立。

---

## 7. Phase 2 — 最新財報

目標：最新 **2 份年報 + 1 份季報**（只有半年報的公司，用最新半年報代替季報）。找到一份就下載、驗證、存檔，再找下一份。

### 7.1 先盤點，再下載

```bash
python <SK>/scripts/inventory.py "<資料夾>" --ticker {TICKER}
```

輸出依「年報／季報／決算短信／輿情」分組，列出期別、大小、**檔頭內容實際是哪種文件**（日股舊檔常把決算短信存成 `_Quarter_`）、輿情檔最新日期、未轉檔 PDF、可疑小檔。**已有的期別直接跳過**（已有 `.md` 視為已下載）。新檔一律用統一命名：

| 類型 | 命名 | 範例 |
| :--- | :--- | :--- |
| 年報 | `{TICKER}_AnnualReport_{FY}.{ext}` | `5306_AnnualReport_2025.pdf` |
| 季報 | `{TICKER}_Quarter_{FY}Q{N}.{ext}` | `5306_Quarter_2026Q2.pdf` |
| 半年報 | `{TICKER}_Quarter_{FY}H1.{ext}` | `2245_Quarter_2026H1.pdf` |
| J-REIT（6 個月一期） | `{TICKER}_AnnualReport_{YYYY}{Mon}` / `{TICKER}_Quarter_{YYYY}{Mon}`（決算短信） | `2971_AnnualReport_2026Jul` |
| 與既有同名但文件種類不同 | 日股加 `_EDINET`、美股加 `_EDGAR`（edinet.py／edgar.py 自動處理） | `2971_AnnualReport_2026Jul_EDINET.pdf` |

- `{FY}` 是財報所屬年度/期間，不是申報日或下載日；檔名不加時間戳或表單代碼。3 月決算公司用會計年度結束年（2026 年 4~6 月 → `{TICKER}_Quarter_2027Q1`；2026/4–9 半期報 → `2027H1`）。
- 舊檔名不強制改名，`inventory.py`、`edinet.py`、`edgar.py` 都認得：`{TICKER}_annual_{FY}`、`{TICKER}_quarter_{FY}Q{N}`、`{TICKER}_interim_{FY}`、`{TICKER}_QuarterlyReport_{FY}Q{N}`、台股 `{FY}_{TICKER}_{申報日}F04/FE4`（年報）、`{yyyyMM}_{TICKER}_AI1`（季報）、美股 `{TICKER}_10K_{期末日}` / `{TICKER}_10Q_{期末日}` / SEC 原檔名 `{ticker}-{YYYYMMDD}`、日股 `…有価証券報告書…{期末日}`、`…決算短信…`。

### 7.2 下載驗證（每份下載完立刻做）

| 檢查 | 不合格處置 |
| :--- | :--- |
| 檔案 < 10KB | 刪除，換來源 |
| 前 4 頁沒有公司名稱或代碼 | 刪除，換來源 |
| `(cid:` ≥ 50 次或佔比 ≥ 5% | 字型缺字無法修復 → 刪除，改抓英文版或換來源 |
| PDF 開頭不是 `%PDF`（封鎖頁 HTML） | 刪除，照 §3 換工具或來源 |
| 網路錯誤 | 照 §3.3 |

- PDF 階段：`pdfinfo` 看頁數與 Producer；轉 md 後統一用 `check_md.py`（§9）做名稱與 CID 檢查。日文 PDF 用 `pdftotext` 常因缺 Adobe-Japan1 字型失敗，**不要**用 `pdftotext` 判斷日文 PDF 好壞。
- **英文版優先**（台股、港股）：台股 MOPS 中文 PDF、港股 `_c.pdf` 常有 `(cid:` 亂碼，英文版通常乾淨。**日股例外**：EDINET 的日文 PDF（Producer = EDINET）實測 0 個 `(cid:`，直接用。
- 保留原始副檔名（`.pdf` / `.html`），不要手動改成 `.md`。

### 7.3 搜尋來源（依序，找到即停）

| 市場 | 順序 | 細節 |
| :--- | :--- | :--- |
| 台股 | ① TWSE 電子書（英文 `_AIA` 有就優先）② 財報狗 e-report ③ 官網 IR；「是否已公告」用 §5.1 鉅亨確認。興櫃只有半年報與年報 | `references/sites_tw.md` §7.3-TW、§4.2 |
| 美股 | ① **SEC EDGAR（§7.5，edgar skill：10-K／10-Q；ADR 20-F／6-K）** ② 官網 IR（SEC Filings 頁）③ 財報狗 ④ 富途 `{代號}-US/announcement`；未在 SEC 註冊的 ADR（如 HEGIY）直接走母國市場 | 本檔 §7.5；`references/sites_us_global.md` §7.3-US |
| 港股 | ① HKEXnews JSON API（§5.4）② 富途 `{5碼}-HK/announcement` ③ 官網 IR | `references/sites_hk_cn.md` §7.3-HK |
| 日股 | ① **EDINET（§7.4，年報與半期報的詳細版）** ② 株探開示清單（決算短信：EDINET 沒有的 Q1/Q3 與最新一期速報）③ 官網 IR ④ IR Bank `irbank.net/{代碼}/ir` ⑤ 富途 `{代碼}-JP/announcement` | 本檔 §7.4；`references/sites_jp.md` §4.4、§7.3-JP |

### 7.4 日股：edinet skill → Convert2md（固定流程）

有価証券報告書（年報）與半期報告書（季報）一律先走 EDINET，拿到的是監理機關版本的**詳細財報**；決算短信只是摘要，當作補最新一期的速報。指令細節、錯誤種類與 edinet 自己的自我修正見 `edinet` skill（`.claude/skills/edinet/SKILL.md`）。下文 `E` = `python <REPO>/.claude/skills/edinet/scripts/edinet.py`。

1. **自檢與 key**：`E selftest --offline`（有 FAIL → 先照 edinet §9 修好）→ `E checkkey`。結束碼 2 = key 錯誤（已自動寫 `Log/edinet_error.md`）→ 報告寫使用者待辦，日股財報改走 §7.3 的 ②~⑤，不要卡住。雲端 session 顯示「來源：雲端網路密鑰（代理注入）」即正常。
2. **預覽**：`E list --code {TICKER}`，確認公司、期別、預定檔名。一般日股預設 2 份有報 + 1 份半期報；**J-REIT 自動 3 份有報、0 份半期報**，不用加參數。資料夾不是唯一以代碼開頭時，下一步加 `--out "<資料夾>"`。
3. **下載**：`E download --code {TICKER}`。
   - 既有檔判定看**檔頭內容**：同期別已有同一種文件（含日文原檔名、舊命名）→ 略過；同名但其實是決算短信／資産運用報告／英文決算資料 → 新檔存成 `…_EDINET.pdf`，兩份並存不覆蓋。
   - 有新 PDF 時最後會印 `CONVERT2MD_SCOPE=<資料夾>`；沒印 = 沒有新檔，跳過第 5 步的轉檔。
   - 份數不足（新上市、變更決算期、延期提出）→ 加 `--full-scan` 再跑一次；還不足就寫進報告 §3。執行紀錄在 `Log/edinet_Summary_{yyyyMMdd}.md`，錯誤在 `Log/edinet_error.md`。
4. **補最新一期速報**：EDINET 自 2024/4 起沒有第 1、第 3 四半期報告書。若株探開示清單（`references/sites_jp.md` §4.4 株探列）有比 EDINET 最新一份更新的決算短信（Q1/Q3、有報出來前的通期決算、J-REIT 有報出來前的決算短信），下載它：一般日股命名 `{TICKER}_Quarter_{FY}Q{N}`（通期決算短信 = `Q4`），J-REIT `{TICKER}_Quarter_{YYYY}{Mon}`。已存在就跳過。
5. **轉檔與驗證**：照 §9 呼叫 `Convert2md`（`<SCOPE>` = 第 3 步印出的資料夾）→ EDINET 的檔跑 `E verify --code {TICKER}`；株探決算短信跑 `check_md.py`（§9 第 3 步）。
6. 報告 §1 寫：每份的 docID、提出日、期別、是否 `_EDINET` 並存、略過原因（可直接引用 `Log/edinet_Summary_{yyyyMMdd}.md`）。

### 7.5 美股：edgar skill → Convert2md（固定流程）

10-K／10-Q（ADR：20-F／40-F／6-K）一律先走 SEC EDGAR，所有 SEC 處理（選件、命名、6-K 判斷、HTML 轉檔、驗證、經驗學習）都在 `edgar` skill（`.claude/skills/edgar/SKILL.md`），本檔不重寫。下文 `G` = `python <REPO>/.claude/skills/edgar/scripts/edgar.py`。

1. **照 edgar §1 步驟 0–8 做**：讀經驗庫 `.claude/skills/edgar/references/lessons.md` → `G selftest --offline` → `G checkua`（結束碼 2 = 被 SEC 擋 → 報告寫使用者待辦，改走 §7.3 的 ②~④）→ `G list --code {TICKER}` → `G download --code {TICKER}`（資料夾不是 `{TICKER}/` 時加 `--out "<資料夾>"`）→ 印出 `CONVERT2MD_SCOPE=` 就照 §9 呼叫 `Convert2md`（`scan_pending.py` **加 `--html`**）→ `G verify --code {TICKER}` → 把 `LEARN:` 行照 edgar §9 寫回（`G lesson`／`G hint`）。
2. 報告 §1 寫：每份的 accession、提交日、期末日、略過原因、最新流通股數（可直接引用 `Log/edgar_Summary_{yyyyMMdd}.md`）。最新一季 10-Q／6-K 還沒出、只有 8-K 財報新聞稿時，新聞稿收在輿情（§8），不當季報。

---

## 8. Phase 3 — 近三個月輿情/新聞

### 8.1 存檔規則

- 檔名：`FinancialReport/{資料夾}/{yyyyMM}_輿情新聞.md`（`yyyyMM` = 執行當月），一個月一檔、所有來源合併。
- **開始前**先看 `inventory.py` 列出的輿情檔「最新日期」，再讀資料夾內的 `{YYYY}_PublicOpinion.md`（`ArrangePublicOpinionMd` 合併的年度檔）與當月檔，確認上次收集到哪一天，只補新內容。
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

## 9. Phase 4 — 轉 Markdown 並驗證

1. **有新檔才做**（`edinet.py`／`edgar.py download` 印出 `CONVERT2MD_SCOPE=`、或 `inventory.py` 列出「尚未轉 Markdown 的 PDF」）；沒有就略過並在報告註明。
2. 呼叫 **`Convert2md` Skill**，**一定要給 `<SCOPE>` = `<資料夾>`**（只掃這家公司，避免轉到 `History/`、`Prompt/` 等不相干資料夾並刪掉 PDF）；`edgar.py` 印出 `CONVERT2MD_HTML=1` 時 `scan_pending.py` 加 `--html`。
   - `save_path` 要填**完整 `.md` 檔案路徑**（如 `<資料夾>/{TICKER}_Quarter_2026Q3.md`）；只填資料夾會回 `[Errno 21] Is a directory` [2026-11]。
   - 150 頁以上的年報（日股有報、港股年報常見）常回「timed out after 60s」，但 MCP 伺服器仍在背景寫檔：不要重送，等 `save_path` 的 `.md` 出現且大小不再變動，再核對最後一頁有轉出。
3. 對每個新 `.md` 跑驗證（同時清掉指向暫存 `pdf_images/` 的圖片連結、補來源標頭；EDINET／EDGAR 的檔改用 `edinet.py verify`／`edgar.py verify`）：
   ```bash
   python <SK>/scripts/check_md.py --names "{公司名},{英文名},{TICKER}" --source "{原始網址或 EDINET docID}" "<資料夾>/{檔名}.md"
   ```
   `FAIL` → 依 §7.2 處置（刪 md 與 PDF、換英文版或換來源），寫進報告 §4。CID 亂碼的 md 已被 `Convert2md` 刪掉、PDF 保留 → 換來源後刪該 PDF。
4. 不經 Convert2md 的 Markdown（Apify `web-fetch` 直接輸出的 TWSE PDF 全文、自己轉的 HTML）同樣要跑第 3 步。
5. SEC 的 HTML／iXBRL 由 `edgar` skill 下載、`Convert2md --html`（`.claude/skills/Convert2md/scripts/html2md.py`）轉檔，不要自己手轉。其他來源的 HTML 財報（非 SEC）同樣可放進公司資料夾後用 `Convert2md --html` 轉，再跑第 3 步。

---

## 10. Phase 5 — 自我檢查與自動修正（每次必做，push 前）

目的：讓 Skill 越跑越準。每次執行都可能發現「Skill 寫的」和「實際發生的」不一樣，當輪就修好，不留給下一輪。

### 10.1 執行中：隨手記錄

Phase 0 開 `<SCRATCH>/collectStk_issues.md`，每遇到下列狀況立刻記一行 `- [Phase N] {檔案} §{章節}：寫的是…；實際是…（證據：錯誤訊息／HTTP 狀態／檔案大小）`：

- 指令、網址、API 參數照寫卻失敗，或站點行為與 `references/` 描述不同（新封鎖、新捷徑、改版）
- 腳本（`scripts/*.py`、`edinet.py`、`edgar.py`、`Convert2md` 內嵌腳本與 `html2md.py`）報錯、結果不合理（抓錯公司、日期錯、漏件）
- 命名規則、FY 推算、流程順序與實際檔案或財報制度不符
- 章節引用對不上、指示互相矛盾、輕量模型會看不懂而走錯的段落

### 10.2 收工前：修正流程

1. 跑 `python <SK>/scripts/selfcheck.py --fix`：自動同步 `.claude/skills` → `.agents/skills`、刪 `.playwright-mcp/`，並列出 ERROR（缺檔、§ 引用斷掉、腳本語法錯、`.env` 被追蹤、`edinet.py`／`edgar.py selftest --offline` 失敗）與 WARN（超過 6 個月的 `[yyyy-mm]`、檔案過長）。改到 edinet／edgar 時另照該 skill 的 §9（補 selftest 案例、更新其 §10 變更紀錄）；美股爬取學到的經驗寫進 `.claude/skills/edgar/references/lessons.md`，不寫在本 Skill。
2. 逐條處理 issues 清單與 selfcheck 的 ERROR：
   - **找根因**：是哪個檔哪一段錯？（站點知識 → `references/`；流程 → `SKILL.md`；程式 → 腳本）
   - **直接改**：用 `Edit` 改正確的位置（規則見 §10.4）。
   - **驗證**：用本輪的真實資料把受影響的步驟重跑一次（腳本：重跑原指令或 `--dry-run`；網址：`curl` / MCP 試 1 次）。通過才算修好；無法驗證（如需要使用者帳號）→ 該列寫 `[未驗證]` 並在報告說明。
3. 再跑一次 `selfcheck.py --fix`，直到 `0 error`。WARN 可留，但要列進報告。
4. 不要為了「看起來有修」而改：沒有證據的推測不寫進 Skill。

### 10.3 可以改／不可以改

| 可以改 | 不可以改（只能寫進報告請使用者處理） |
| :--- | :--- |
| `collectStk/` 全部檔案（`SKILL.md`、`references/`、`scripts/`） | `.claude/settings*.json`、`.mcp.json`、`.claude/mcp_config.json`（權限與 MCP 設定） |
| `edinet/SKILL.md`、`edinet/scripts/edinet.py`；`edgar/` 全部檔案 | claude.ai 連接器權限、帳號、額度、環境網路密鑰 |
| `Convert2md/SKILL.md`（含內嵌腳本）、`Convert2md/scripts/html2md.py` | 其他 skill 的內容（`collectState`、`stateAnalysis` 只可改「引用 collectStk §X」的那幾個字） |
| `.gitignore`（只增不減） | `Routines_*.md` 輪替表、公司資料夾內既有分析檔 |

### 10.4 寫法規則

1. **放對位置**：網站行為放 `references/` 對應市場的 §4.x 表格（一站一列）；多步驟 API 用法放 §5.x；官網 IR 下載路徑放該檔的 §7.3-XX；MCP 帳號級錯誤、預檢與連接器修法放 §3.0；日股 EDINET 流程放 §7.4（腳本細節放 `edinet` skill）；美股 SEC 流程放 §7.5（細節、站點行為、公司特例一律放 `edgar` skill 與 `.claude/skills/edgar/references/lessons.md`）。不另開段落、不在別處重寫抓取規則。
2. **合併不追加**：同一站點已有一列時直接改寫那一列並更新 `[yyyy-mm]`，不新增「補充」列。
3. **刪除無用資料**：失效做法、被取代的舊寫法、改版前網址、與 §3 重複的敘述、一次性除錯流水帳（某天抓到幾筆、檔案多大）、指向不存在檔案的連結 → 刪除，只留結論。環境設定細節（如 Playwright 啟動器原理）看 `.claude/scripts/playwright-mcp.mjs` 開頭註解，不寫在這裡。
4. **章節編號固定**：§3、§4.x、§5.x、§8.3、§8.5 被 `collectState`、`stateAnalysis` 引用，不可改號；新增站點放進既有表格。
5. **鏡像**：`.claude/skills/` 是唯一編輯來源，`selfcheck.py --fix` 會整份同步到 `.agents/skills/`。Gemini 若直接改了 `.agents/skills/…`，先把同檔複製回 `.claude/skills/…` 再跑 `--fix`，否則會被蓋掉。
6. 在 §11 報告「Skill 自我檢查與修正」寫明本次新增、修改、刪除了什麼、怎麼驗證。

---

## 11. Phase 6 — 執行報告與 push

報告寫到 `<REPO>/Log/collectStk_Summary_{yyyyMMdd}.md`（同日多家公司寫在同一份，每家一節）。

````markdown
# 任務執行最終報告 - YYYY/MM/DD

- **執行日**：YYYY-MM-DD（輪替表第 N 日 → {代碼} {名稱}）
- **公司資料夾**：`{資料夾}/`

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
（日股寫 EDINET docID、提出日、是否 `_EDINET` 並存；美股寫 SEC accession、提交日、期末日、是否 `_EDGAR` 並存、最新流通股數）

**本期重點**：（條列近三個月的關鍵事件與輿情，利多與利空都要寫；提到金額時附每股金額，股數寫明來源）

## 2. 失敗或被擋網站
- **來源**：[網站](URL)｜**原因**：{403 / 逾時 / 付費牆…}｜**已試過**：{實際試過的工具}

## 3. 資料缺失說明
（如：財報尚未公布、興櫃只有半年報、EDINET 無 Q1/Q3、冷門股無討論）

## 4. 異常檔案刪除紀錄
（< 10KB、無公司名稱、`(cid:` 亂碼、`check_md.py` FAIL 等被刪的檔案；沒有就寫「無」）

## 5. MCP 預檢與使用紀錄
- **預檢結果**：可用：{…}｜停用：{MCP}（{錯誤原文}）
- **使用者待辦**（有停用或跳過核准卡片才寫）：照 §3.0.3 寫出連接器與工具名，例：「到 https://claude.ai/customize/connectors 把 Firecrawl、Bright Data 的工具權限設為一律允許（Always allow）」

| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
（用人類可讀名稱，如 Firecrawl、Bright Data、Apify、Exa、Playwright、yfinance、pymupdf4llm；完全沒用 MCP 就寫「本次未使用 MCP，僅用 {內建工具}」）

## 6. Phase 4 Convert2md 與 check_md
（轉了哪些、成功/失敗、check_md 結果；沒有新檔就寫「無新 PDF」）

## 7. Skill 自我檢查與修正
- **selfcheck**：{N} error → 0 error；WARN：{…}
- **修正**：{檔案} §{章節}：{改了什麼}（原因：{證據}；驗證：{重跑結果}）
- **未解決**：{問題}（原因：{需使用者處理／無法驗證}）
（沒有就寫「無」）
````

> [!IMPORTANT]
> **報告寫完後，必須把所有新增與變更的檔案（含 §10 修正的 Skill 檔與 `.agents/` 鏡像）commit 並 push，任務才算完成。** push 前確認 `selfcheck.py` 為 `0 error`、`.playwright-mcp/` 已刪（§3.4）。
> - 雲端 session／被指定 feature 分支 → push 該分支並開 PR（auto-merge workflow 會合併進 `master`）。
> - 本機直跑 → push `master`。
> - 不可因分支限制停下來詢問使用者。
