---
name: CollectsentimentAndReports
description: 收集個股「最新財務報告」與「輿情討論/新聞」，並用 yfinance MCP 抓取結構化財務數據
---
/goal
# CollectsentimentAndReports — 執行指南

你是 AI Agent。啟動此 Skill 時，依序完成：
1. **用 yfinance MCP 抓結構化財務數據**（最快、最穩，先做，見 §2.10）
2. 下載指定公司的「最新財報（2 年報 + 1 季報）」
3. 收集該公司「過去三個月內的社群輿情／新聞」
4. 轉換格式（Convert2md）
5. 產出報告並 push 到 `master`

---

## §0 鐵律（全篇最高優先，違反＝任務失敗）

| # | 鐵律 | 說明 |
|:--|:-----|:-----|
| 🚫1 | **禁止從 GitHub `a9303001/FinancialReport` 收集任何東西** | 不下載財報、不抓新聞、不讀輿情 |
| 🚫2 | **禁止捏造內容（防幻覺）** | 不可自行撰寫模擬討論、不可捏造 URL／日期／用戶 ID；爬取失敗就誠實記錄失敗，不可用訓練知識填充 |
| 🚫3 | **禁止訪問 `macrotrends.net`** | 該站持續封鎖爬蟲 |
| ✅4 | **即時存檔** | 每下載完一份財報、每爬完一個網站的輿情，立刻存檔。不要等全部做完才存 |
| ✅5 | **抓不到 → 照 §2 黃金規則跑 MCP 鏈** | 任何地方遇到抓不到／空白／被擋，統一回到 §2 處理 |
| ✅6 | **yfinance MCP 優先呼叫** | Phase 2 和 Phase 3 都先跑 yfinance（§2.10），再跑爬蟲。它不是爬蟲，**不套 §2 黃金規則鏈** |
| 🚫7 | **yfinance 的 `null` 一律寫 `N/A`** | 禁止用訓練知識、推估或其他年度數字填補空欄位 |

---

## §0.5 工具對照表

> 本指南用「動作」描述，不綁定特定工具名。看到任何工具名（如 `read_url`、`WebFetch`）都視為「該動作」，用你有的工具完成即可。

| 動作 | Claude | Gemini / 其他 |
|:-----|:-------|:---------------|
| 網路搜尋 | `WebSearch` | `search_web` / `google_search` |
| 抓取網頁 | `WebFetch` | `read_url` / `read_url_content` |
| MCP 爬取 | `firecrawl_scrape` 等 | 同（已連接的 MCP 工具） |
| **結構化財務數據** | **yfinance MCP（`mcp__yfinance__*`）** | 同（已連接的 yfinance MCP） |
| 讀寫檔案 | `Read` / `Edit` / `Write` | `view_file` / `write_file` / `edit_file` |
| 執行指令 | `Bash` | `run_shell_command` / `run_command` |

- 「內建工具」＝ AI 原生的抓取／搜尋工具
- 「MCP 工具」＝ `firecrawl` / `brightdata` / `apify` / `playwright` 這類外接爬取服務
- 「**資料型 MCP**」＝ `yfinance` 這類直接回傳結構化數據的 API 型 MCP，**不需爬蟲、不受 Cloudflare 影響**，應優先使用（見 §2.10）

---

## §0.6 執行參數

| 參數 | 說明 | 範例 | 若缺失 |
|:-----|:-----|:-----|:-------|
| `COMPANY_TICKER` | 股票代碼（用於資料夾與檔名） | `2881`, `UHS`, `03606` | **必填**，立刻詢問使用者 |
| `COMPANY_NAME` | 公司名稱 | `富邦金`, `福耀玻璃` | **必填**，若無則先搜尋查出 |
| `YF_TICKER` | yfinance 專用代碼（含後綴） | `2881.TW`, `UHS`, `3606.HK` | 由 `COMPANY_TICKER` 依 §2.10.2 推導；⚠️ 港股不補零 |

---

## §1 執行流程

```
Phase 1（主代理人）→ 建目錄
Phase 2（子代理人）→ ① yfinance 結構化財務數據（§4.0，先做）
                    ② 下載年報／季報原檔（§4.1–§4.3）
Phase 3（子代理人）→ ① yfinance 新聞／評等／內部人（§5.6，先做）
                    ② 各在地討論區與新聞（§5.2）
Phase 4（主代理人）→ Convert2md 轉換
Phase 5（主代理人）→ 產出報告 + git push master
```

- **每間公司用一個獨立子代理人** 執行 Phase 2 + Phase 3
- 主代理人負責 Phase 1、4、5

---

## §2 通用抓取規則（唯一標準，Phase 2 和 Phase 3 都套用）

### §2.1 黃金規則（一句話）

> **內建工具抓不到（空白／報錯／被擋），依序試 firecrawl → brightdata → apify → playwright，四個 MCP 全失敗才可放棄。**

**固定順序，不可跳過：**

```
① 內建工具 ──成功──→ ✅ 記錄內容
      │失敗
② firecrawl_scrape ──成功──→ ✅
      │失敗
③ brightdata scrape_as_markdown ──成功──→ ✅
      │失敗
④ apify ──成功──→ ✅
      │失敗
⑤ playwright ──成功──→ ✅
      │失敗
❌ 放棄，照 §5.5 誠實記錄
```

| 規則 | 內容 |
|:-----|:-----|
| 順序不可跳 | 除非該環境沒連上某 MCP，才可跳過並在報告註明 |
| 每工具最多 2 次 | 失敗就換下一個，禁止無限重試 |
| 「明確拒絕」也算失敗 | 如 Firecrawl 回「we do not support this site」→ 換下一個 MCP |
| 整條鏈都不行的替代 | 可改用 MCP 搜尋功能（如 `firecrawl_search`）搜該站內容 |
| WebSearch 摘要是最後手段 | 必須在內容加註「⚠️ MCP 抓取失敗，以下為 WebSearch 摘要」 |

### §2.2 什麼算「抓取失敗」？

符合任一項就換下一個工具：
- **空白／JS 渲染**：回傳空白、只有選單框架、沒有正文（見 §2.3 清單）
- **被封鎖**：回 `not accessible to our user agent`、`domain not accessible`、HTTP 400（見 §2.4 清單）
- **防護頁**：Cloudflare `Just a moment...`、HTTP 403 / 429

### §2.3 已知 JS 動態渲染網站（內建工具必抓空白 → 直接用 MCP）

| 網站 | 網域 | 說明 |
|:-----|:-----|:-----|
| 雪球 | `xueqiu.com` | JS 動態載入，用 brightdata 優先（SOP 見 §2.7） |
| 股市爆料同學會 | `cmoney.tw` | Nuxt SSR 殼，直接打官方 API（SOP 見 §2.8） |
| MOPS 台股查詢 | `mops.twse.com.tw` | 需 JS 互動／POST |
| moomoo 社區 | `moomoo.com` | JS 載入正文 |
| 東方財富股吧 | `guba.eastmoney.com` | JS 分頁載入 |
| 格隆匯 | `gelonghui.com` | Nuxt.js SSR，用 firecrawl 優先（SOP 見 §2.9） |

### §2.4 已知封鎖爬蟲的網站（用 MCP，不是放棄）

| 網站 | 網域 | 建議做法 |
|:-----|:-----|:---------|
| Reddit | `reddit.com` | Firecrawl 也拒絕 → 換 brightdata / apify / playwright → 都不行用 `firecrawl_search` 搜 |
| Reuters | `reuters.com` | `firecrawl_scrape` 通常可讀公司頁 |
| Bloomberg | `bloomberg.com` | 付費牆限制，取得摘要即可並註明 |

> 每次遇到新的被擋網站，處理完後加進 §2.3 或 §2.4。

### §2.5 純網路錯誤 → 零重試、直接換來源

以下錯誤**不套 MCP 鏈**，見到即放棄該 URL、刪除臨時檔、換下一個來源：
- Read Timeout / EOF / Connection Reset
- `ECONNREFUSED` / `EHOSTUNREACH` 等 Socket 錯誤

> ⚠️ Read Timeout 和 EOF 最容易讓 Agent 卡死。絕對不可重試或空等。

### §2.6 頻率控制

| 規則 | 說明 |
|:-----|:-----|
| 同網域間隔 | 至少 **3 秒** |
| 交錯爬取 | A 站 → B 站 → C 站 → A 站，不要一口氣爬完一站 |
| 單站上限 | 同一網域最多爬 **5 個頁面** |

### §2.7 雪球（xueqiu.com）SOP ── 2026-07-03 驗證

> 雪球是港股、A 股輿情核心來源，但 JS 動態渲染，內建工具抓空白。

1. **直接跳過內建工具**，用 `brightdata scrape_as_markdown` 抓 `https://xueqiu.com/S/{代號}`（雪球用 brightdata 成功率最高）
2. brightdata 失敗 → 依序 `firecrawl` → `apify` → `playwright`
3. 頁面有深度專欄連結 → 可再用 brightdata 抓文章頁補充
4. **只記錄真實存在於頁面上的貼文、連結、時間戳**

### §2.8 股市爆料同學會（cmoney.tw）API SOP ── 2026-07-19 驗證

> **不要爬網頁，直接打 CMoney 官方 API。** 實測一次抓 294 篇＋567 則留言。

**背景**：`cmoney.tw/forum/stock/{代號}` 是 Nuxt SSR 殼，貼文列表為空。前端先拿訪客 token 再打 API，我們直接模仿。

**步驟 1：取得訪客 token**

```bash
curl -s -X POST "https://www.cmoney.tw/api/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=guest&client_id=cmstockcommunity-web"
# 回傳 JSON → 取 access_token（JWT，效期約 24 小時）
```

**步驟 2：抓貼文列表（用 cursor 分頁）**

```bash
curl -s "https://www.cmoney.tw/api/mach/api/Article/Stocks/{股票代號}/AllLatest?fetchCount=20" \
  -H "Authorization: Bearer {access_token}" \
  -H "X-Version: 3.0"
```

- 回傳 `{ "articles": [...], "hasNext": true/false, "nextCursor": <數字> }`
- 下一頁帶 `&cursor={nextCursor}`，直到 `hasNext=false`
- ⚠️ **`skipCount`/`offset` 無效**（會重複），務必用 `cursor` 並以 `id` 去重
- 型別可用：`AllLatest`（最新）、`AllHottest`（最熱）、`news`（新聞）
- 重點欄位：`id`、`content.text`、`createTime`（**毫秒** timestamp，除以 1000 轉日期）
- 文章 URL：`https://www.cmoney.tw/forum/article/{id}`

**步驟 3：抓留言（選擇性）**

```bash
curl -s "https://www.cmoney.tw/api/mach/api/Article/{文章id}/Comments?fetch=50&offset=0" \
  -H "Authorization: Bearer {access_token}" \
  -H "X-Version: 2.0"
```

- ⚠️ **留言 API 用 `X-Version: 2.0`**（3.0 會回 UnsupportedApiVersion）
- 參數是 `fetch` / `offset`（不是 fetchCount）
- 只對 `commentCount > 0` 的文章呼叫

**常見錯誤對照：**

| 症狀 | 修法 |
|:-----|:-----|
| 回 HTML 不是 JSON | 路徑錯 → 正確 base 是 `www.cmoney.tw/api/mach/api/...` |
| 400 `UnsupportedApiVersion` | 缺 `X-Version` 或版本錯（文章 3.0、留言 2.0） |
| 401 | 缺 Bearer token 或 token 過期 → 回步驟 1 重拿 |
| 每頁內容都一樣 | 用了 `skipCount` → 改用 `cursor` |

- 美股端點：`.../api/Article/USStocks/{代號}/{型別}`（同一套 token）
- 間隔 0.3~0.5 秒，遵守 §2.6

### §2.9 格隆匯（gelonghui.com）SOP ── 2026-08-26 驗證

> **用 `firecrawl_scrape`，basic proxy 即可，每頁 1 credit。** 格隆匯是港股／A 股／中概股輿情重要來源，Nuxt.js SSR 架構，內建工具必定失敗。

**步驟 1：搜尋文章列表**

```
firecrawl_scrape → https://www.gelonghui.com/search?keyword={公司名稱}
```
- 回傳完整搜尋結果（實測福耀玻璃取得 257 篇），含標題、摘要、作者、時間、URL（`/p/{id}` 格式）
- 第一頁約 18 篇，通常足夠涵蓋近三個月
- 1 credit

**步驟 2：（可選）firecrawl_search 補充**

```
firecrawl_search → {公司名稱} {股票代碼} site:gelonghui.com
```
- 10 筆結果，也會包含券商研報 PDF 連結
- 2 credits

**步驟 3：抓單篇深度文章**

```
firecrawl_scrape → https://www.gelonghui.com/p/{文章id}
```
- 篩選近三個月有實質分析的文章
- 回傳乾淨 Markdown 全文
- 1 credit/篇

**此站工具順序：** firecrawl（首選）→ brightdata / apify / playwright（遞補）→ ❌ 內建工具（必定失敗，不要試）

- 快訊（`/news/{id}`）和文章（`/p/{id}`）都可用 firecrawl 爬取
- 遵守 §2.6 頻率原則

### §2.10 yfinance MCP SOP ── 2026-08-27 驗證

> **yfinance MCP 不是爬蟲，是 Yahoo Finance 官方資料的 API 封裝。**
> 它**不套用 §2.1 黃金規則的爬蟲鏈**，而是「**最優先、第一個呼叫**」的資料來源：
> 零 Cloudflare、零 JS 渲染、零頻率限制問題，回傳即為結構化 JSON。

#### §2.10.1 可用工具一覽

| 工具 | 用途 | 本 Skill 用在哪 |
|:-----|:-----|:----------------|
| `get_stock_info` | 股價、市值、EPS、PE、margins、ROE、負債、股利、**流通股數** | Phase 2（§4.0 核心） |
| `get_financial_statement` | 損益表／資產負債表／現金流（年 + 季） | Phase 2（§4.0 核心） |
| `get_yahoo_finance_news` | 該股新聞（含真實標題／摘要／URL） | Phase 3（§5.2 新聞來源） |
| `get_recommendations` | 分析師評等、升降評（`upgrades_downgrades`） | Phase 3（法人輿情） |
| `get_holder_info` | 大股東、法人持股、**內部人交易** | Phase 3（內部人動向輿情） |
| `get_stock_actions` | 配息與股票分割紀錄 | Phase 2（殖利率／股數變化佐證） |
| `get_historical_stock_prices` | 歷史股價（Date/Open/High/Low/Close/Volume） | 選用（輿情事件對照股價反應） |
| `get_option_expiration_dates` / `get_option_chain` | 選擇權到期日與鏈 | 選用（一般不需要） |

#### §2.10.2 Ticker 後綴對照（**最容易出錯，務必先查表**）

| 市場 | yfinance ticker 格式 | 範例 | 備註 |
|:-----|:---------------------|:-----|:-----|
| 美股 | `{代碼}` | `UHS`、`AAPL` | 無後綴 |
| 台股（上市） | `{4碼}.TW` | `2881.TW` | — |
| 台股（上櫃） | `{4碼}.TWO` | `6488.TWO` | `.TW` 抓不到時改試 `.TWO` |
| 港股 | `{4碼}.HK` | `3606.HK` | ⚠️ **不可補零成 5 碼**，`03606.HK` 會失敗 |
| 日股 | `{4碼}.T` | `3445.T` | — |
| 中國 A 股（滬） | `{6碼}.SS` | `600519.SS` | — |
| 中國 A 股（深） | `{6碼}.SZ` | `000333.SZ` | — |

> ⚠️ **港股陷阱**：本 Skill 的資料夾命名（§3）港股補齊 5 碼（`03606福耀玻璃`），但 **yfinance 必須用 4 碼**（`3606.HK`）。兩者不同，不要混用。

#### §2.10.3 怎麼判斷「ticker 抓錯了」

`get_stock_info` 回傳**只有一兩個欄位且幾乎全是 `null`**（典型為 `{"trailingPegRatio": null}`）＝ **ticker 無效**，不是公司沒資料。

處理順序：
1. 檢查後綴是否照 §2.10.2（港股別補零、台股試 `.TWO`）
2. 仍失敗 → 用 `WebSearch` 查「{公司名稱} yahoo finance ticker」確認正確代碼
3. 再失敗 → 在報告 §3 記錄「yfinance 無此標的」，改走傳統財報下載（§4.3），**不可捏造數據**

#### §2.10.4 欄位 → AGENTS.md 必備數據對照

| AGENTS.md 要求 | yfinance 來源 | 欄位／算法 |
|:---------------|:--------------|:-----------|
| 最新 EPS | `get_stock_info` | `trailingEps` |
| 本益比 PE | `get_stock_info` | `trailingPE`、`forwardPE` |
| 預估 EPS | `get_stock_info` | `forwardEps`、`epsCurrentYear` |
| 營業利益率 | `get_stock_info` / `income_stmt` | `operatingMargins`；或 `Operating Income / Total Revenue` |
| 負債比率 | `get_financial_statement` → `balance_sheet` | `Total Liabilities Net Minority Interest / Total Assets × 100%` |
| OPM（自定義） | `income_stmt` | `(營業利益率 / 稅前淨利率) × 100%`，稅前淨利率＝`Pretax Income / Total Revenue` |
| ROE | `get_stock_info` | `returnOnEquity` |
| 殖利率 | `get_stock_info` / `get_stock_actions` | `dividendYield`、`fiveYearAvgDividendYield` |
| 淨利 CAGR | `income_stmt` | 由各年度 `Net Income` 自行計算 |
| **每股化換算基準** | `get_stock_info` | **`sharesOutstanding`**（AGENTS.md 每股化規則的除數） |
| 流通股數變化 | `income_stmt` + `get_stock_actions` | `Basic/Diluted Average Shares` 逐季比對、`lastSplitFactor` |

**已知限制（必須誠實在報告寫明）：**
- 年度財報通常**只回 4 年**，AGENTS.md 要求的「5 年中位數／5 年 CAGR」可能不足 → 須註明「yfinance 僅提供 N 年，5 年數據需補其他來源」
- 最近一季常有大量 `null`（Yahoo 尚未補齊）→ 以有值的最近一季為準並註明日期
- 金融股（如 2881.TW）的 `Total Revenue`、`operatingCashflow` 口徑與一般製造業不同，解讀時要註明
- `financialCurrency` 欄位標示財報幣別，**與股價幣別可能不同**，換算每股金額前務必確認

#### §2.10.5 呼叫節奏

- 同一檔股票建議一次抓齊：`get_stock_info` + `income_stmt` + `balance_sheet` + `quarterly_income_stmt`
- 無需 §2.6 的 3 秒間隔（非爬蟲），但**不要對同一 ticker 重複呼叫同一工具**
- 回傳為大筆 JSON，**抓完立刻依 §4.0 整理存檔**，不要留在記憶體等最後才寫

---

## §3 Phase 1 — 建立目錄

建立 `FinancialReport/{COMPANY_FOLDER_NAME}/`：
- 台／日／港股：`{代碼}{名稱}`（如 `2881富邦金`、`03606福耀玻璃`）
- 美股：`{代碼}`（如 `UHS`）
- 資料夾不存在就自動建立

---

## §4 Phase 2 — 財務數據與財報下載

> 目標：(a) yfinance 結構化財務數據，(b) 最新 2 份年報 + 1 份季報。
> 找到一份就立刻存檔。已存在的跳過。抓取遇阻回 §2。

### §4.0 【第一步】yfinance 結構化財務數據（先做，不可跳過）

> **為什麼先做**：yfinance 幾秒內就能拿到 EPS／PE／ROE／負債比／流通股數等 AGENTS.md 必備數據，
> 不受爬蟲封鎖影響。就算後面 §4.1–§4.3 的 PDF 全部下載失敗，這份資料仍能支撐分析。

**步驟：**

1. 依 §2.10.2 決定 ticker（港股別補零！）
2. 依序呼叫：
   - `get_stock_info`
   - `get_financial_statement`（`income_stmt`）
   - `get_financial_statement`（`balance_sheet`）
   - `get_financial_statement`（`quarterly_income_stmt`）
   - `get_financial_statement`（`cashflow`）— 需要自由現金流時
   - `get_stock_actions` — 需要配息／分割紀錄時
3. 驗證回傳（§2.10.3）：只有 `null` ＝ ticker 錯 → 修正後重試，最多 2 次
4. **立刻存檔**（即時存檔鐵律 ✅4）

**檔名與路徑：**

| 項目 | 規則 |
|:-----|:-----|
| 檔名 | `{TICKER}_yfinance_{yyyyMMdd}.md` |
| 範例 | `2881_yfinance_20260827.md` |
| 路徑 | `FinancialReport/{COMPANY_FOLDER_NAME}/` |
| `{TICKER}` | 用資料夾代碼（如 `2881`），不含 `.TW` 後綴 |
| 寫入模式 | 覆蓋同日檔案；不同日期另存新檔（保留歷史快照） |

**存檔範本：**

````markdown
# [{代碼} {公司名稱}] yfinance 財務數據快照

- **yfinance ticker**：2881.TW
- **抓取時間**：YYYY-MM-DD HH:MM
- **資料來源**：yfinance MCP（Yahoo Finance）
- **財報幣別**：TWD（`financialCurrency`）
- **流通股數**：13,665,721,905（`sharesOutstanding`）← 每股化換算基準

## 1. 核心指標（AGENTS.md 必備數據）

| 指標 | 數值 | 來源欄位 |
|:-----|:-----|:---------|
| 最新 EPS | 8.37 | `trailingEps` |
| 預估 EPS | 10.26 | `forwardEps` |
| PE（TTM / Forward） | 16.55 / 13.50 | `trailingPE` / `forwardPE` |
| 營業利益率 | 48.47% | `operatingMargins` |
| ROE | 18.74% | `returnOnEquity` |
| 殖利率 | 3.07% | `dividendYield` |
| 負債比率 | X.XX% | `Total Liabilities / Total Assets` |
| OPM（自定義） | X.XX% | `(營業利益率 / 稅前淨利率) × 100%` |
| 淨利 5 年 CAGR | X.XX% ⚠️ 僅 N 年資料 | `income_stmt` 各年 `Net Income` |

> 計算過程請列出算式，不可只給結果。

## 2. 年度損益表（近 N 年）
| 年度 | 營收 | 營業利益 | 稅前淨利 | 淨利 | 每股營收 | 每股淨利 |
|:-----|-----:|---------:|---------:|-----:|---------:|---------:|

## 3. 季度損益表（近 N 季）
| 季度 | 營收 | 營業利益 | 淨利 | EPS |
|:-----|-----:|---------:|-----:|----:|

## 4. 資產負債重點
| 年度 | 總資產 | 總負債 | 股東權益 | 負債比率 |
|:-----|-------:|-------:|---------:|---------:|

## 5. 流通股數變化（§5 對應 AGENTS.md 流通股規則）
| 期間 | Basic Average Shares | 增減% | 說明 |
|:-----|---------------------:|------:|:-----|

## 6. 資料缺口
- 例：`quarterly_income_stmt` 2025-09-30 多數欄位為 null，Yahoo 尚未補齊
- 例：年度資料僅 4 年，5 年中位數／CAGR 不足，須補其他來源
````

**規則：**
- ⚠️ **所有絕對金額必須依 AGENTS.md 同步標註每股金額**（除以 `sharesOutstanding`）
- ⚠️ **null 就寫 `N/A`，禁止用訓練知識或推估值填充**（鐵律 🚫2）
- ⚠️ yfinance 數據**不能取代年報／季報全文**，仍須繼續執行 §4.1–§4.3 下載原始財報
- 若 §4.3 的財報下載全部失敗，本檔即為 Phase 2 的唯一產出，須在報告 §3 寫明

### §4.1 先盤點 → 再決定缺什麼

列出資料夾現有檔案，靠檔名判斷已有哪些年報／季報，再決定要下載哪些。

**統一命名規則（新檔必須遵守）：**

| 類型 | 格式 | 範例 |
|:-----|:-----|:-----|
| 年報 | `{TICKER}_AnnualReport_{FY}.{ext}` | `5306_AnnualReport_2025.pdf` |
| 季報 | `{TICKER}_Quarter_{FY}Q{N}.{ext}` | `5306_Quarter_2026Q1.pdf` |
| yfinance 快照 | `{TICKER}_yfinance_{yyyyMMdd}.md` | `5306_yfinance_20260827.md` |

- `{ext}`：下載時保留原始 `.pdf` / `.html`，轉換後改 `.md`
- `{FY}`：財報所屬年度（西元年），不用申報日期或下載時間戳
- 舊檔不強制改名

### §4.2 下載驗證規則

| 驗證項目 | 標準 | 不通過 → |
|:---------|:-----|:---------|
| 英文優先 | 有英文版就下英文版（避免中文 PDF `(cid:N)` 亂碼） | — |
| 檔案大小 | ≥ 10KB | 刪除，換來源 |
| 內容檢查 | 前 4 頁有公司名稱或代碼 | 刪除，換來源 |
| `(cid:` 亂碼 | 整份 ≤ 50 次 | 刪除，換英文版或換來源 |
| 網路錯誤 | Timeout / EOF / Reset | 零重試，照 §2.5 |

> 下載完一份後**馬上試轉換驗證**，不要等到 Phase 4。

### §4.3 財報來源順序（找到即停）

> yfinance（§4.0）提供的是**結構化數據**，不是年報／季報原文，**不算完成本節**。
> 本節目標是取得可供 §4.1 文字分析（風險因素、MD&A、管理層討論）的原始報告檔。

**台股 (TW)**
1. MOPS/TWSE（POST 取檔，英文版 `_AIA.pdf` 優先；JS 動態渲染見 §2.3）
2. 財報狗（`statementdog.com/analysis/{代碼}/e-report`）
3. 官網 IR 頁面

**美股 (US)**
1. 官網 IR 頁面
2. SEC EDGAR
3. 財報狗
4. 富途牛牛（`futunn.com/hk/stock/{代碼}-US/announcement`）

**日股 (JP)**
1. 官網 IR（優先英文 Annual Report）
2. EDINET
3. IR Bank（`irbank.net/{代碼}/ir`）
4. 富途牛牛（`futunn.com/hk/stock/{代碼}-JP/announcement`）

**港股 (HK)**（代碼補齊 5 碼，如 `02318`）
1. HKEXnews 披露易（`www1.hkexnews.hk/search/titlesearch.xhtml?lang=en`）
2. 新浪財經（`stock.finance.sina.com.cn/hkstock/notice/{5碼}.html`）
3. 富途牛牛（`futunn.com/hk/stock/{5碼}-HK/announcement`）

---

## §5 Phase 3 — 輿情與新聞收集

> 範圍：過去三個月內。逐源抓取，每爬完一個網站立刻以 Append 模式存檔。抓取遇阻回 §2。

### §5.1 存檔規則（一月一檔，Append 模式）

| 項目 | 規則 |
|:-----|:-----|
| **檔名** | `{yyyyMM}_輿情新聞.md`（`yyyyMM` = 執行當月，如 `202608`） |
| **路徑** | `FinancialReport/{COMPANY_FOLDER_NAME}/{yyyyMM}_輿情新聞.md` |
| **寫入模式** | Append：新來源加到末尾。同來源已有章節 → 在章節末尾補充 |
| **不要覆蓋** | 不要砍掉舊內容 |
| **舊格式相容** | 若有舊檔（如 `202607_xueqiu.md`）不強制改名，新資料一律存入新格式 |
| **找不到內容也要寫** | 在該來源章節記錄「已搜尋 {來源}，過去三個月無符合內容」，避免下次重複嘗試 |

### §5.2 搜尋來源

> 標 ⚠️ 者為 JS 渲染或封鎖爬蟲網站，抓不到時照 §2 換 MCP。

**【第一個來源，所有市場共通】yfinance MCP** ✅ 免爬蟲，見 §5.6

- **台股**：鉅亨網、MoneyDJ、經濟日報、PTT 股市板、Dcard 理財、股市爆料同學會（✅ 直接打 API，見 §2.8）、財報狗社群
- **美股**：yfinance（✅ 新聞量最豐富）、Yahoo Finance、Bloomberg（⚠️ 付費牆）、Reuters（⚠️ 封鎖）、X、Reddit（⚠️ 封鎖）、Seeking Alpha、格隆匯（⚠️ JS 渲染，見 §2.9）
- **港股**：香港經濟日報、雪球（⚠️ 見 §2.7）、moomoo（⚠️ JS）、東方財富股吧（⚠️ JS）、格隆匯（⚠️ 見 §2.9）、LIHKG
- **日股**：日經新聞、Yahoo Finance JP 掲示板、note、5ch、X

> ⚠️ **yfinance 新聞的市場差異（2026-08-27 實測）**：美股（如 `UHS`）一次可回 10 則含真實 URL 的相關新聞；
> 非美股（如 `2881.TW`）常只回 1 則且可能與公司無直接關聯。
> 因此 **yfinance 新聞對美股是主力來源，對台／港／日股只是補充**，非美股仍必須完整跑 §5.2 各在地來源。

### §5.3 過濾規則

1. **只記錄實質內容**：基本面分析、事件報導。忽略純漲跌數字或表情
2. **標題必須提到該公司**：不相關的一律排除
3. **內容要具體**：記錄核心論點與細節，不能只貼網址
4. **排除網站自我介紹文字**：「本網提供即時財經新聞…」→ 不算有效紀錄
5. **每筆必須有真實來源佐證**：爬取結果沒有的就不寫

### §5.4 Markdown 存檔範本

````markdown
# [{代碼} {公司名稱}] 輿情與新聞整理 ({YYYY}/{MM})

- **分析月份**：YYYY/MM
- **資料範圍**：過去三個月
- **最後更新**：YYYY-MM-DD HH:MM

---

## [雪球 Xueqiu]

- **抓取時間**：YYYY-MM-DD
- **抓取方式**：brightdata scrape_as_markdown
- **抓取結果**：✅ 成功 / ❌ 失敗

### 🎯 [主題]
- **來源連結**: [URL](URL) ← 必須是真實 URL
- **發布時間**: YYYY-MM-DD ← 必須是真實時間
- **核心觀點**:
  > "引述原文..." ← 必須是真實爬取到的原文
- **關鍵要點**:
  - 重點A
  - 重點B
````

**Append 操作：**
- 檔案不存在 → 建新檔，先寫標頭，再加來源章節
- 檔案存在但該來源無章節 → 在末尾 Append 新 `## [來源名稱]`
- 檔案存在且該來源有章節 → 在該章節末尾補充

### §5.5 爬取失敗的標準寫法

全部 MCP 都失敗時，**必須**寫以下格式，禁止用 AI 生成內容填充：

````markdown
## [東方財富股吧]

- **抓取時間**：YYYY-MM-DD
- **抓取結果**：❌ 失敗

### 搜尋嘗試紀錄
- 已嘗試：內建工具 read_url_content → 回傳 HTML 骨架
- 已嘗試：firecrawl_scrape → 只取得基本資料
- 已嘗試：brightdata → 連線逾時
- 已嘗試：apify → 不支援此網域
- 已嘗試：playwright → 連線失敗
- **結論**：本次無法取得真實輿情，非 AI 生成。
````

### §5.6 yfinance 輿情 SOP（Phase 3 的第一個來源）

> yfinance 提供三種**免爬蟲**的輿情素材，是 Phase 3 最穩定的起點。全部照 §5.1 Append 進 `{yyyyMM}_輿情新聞.md`。

| 呼叫 | 取得什麼 | 歸類到哪個章節 |
|:-----|:---------|:---------------|
| `get_yahoo_finance_news` | 新聞標題／摘要／**真實 URL** | `## [Yahoo Finance News（yfinance MCP）]` |
| `get_recommendations`（`upgrades_downgrades`） | 券商評等調升／調降、目標價變動 | `## [分析師評等（yfinance MCP）]` |
| `get_recommendations`（`recommendations`） | 買賣建議分布（strongBuy/buy/hold/sell） | 同上 |
| `get_holder_info`（`insider_transactions`） | 內部人買賣紀錄 | `## [內部人交易（yfinance MCP）]` |
| `get_holder_info`（`institutional_holders`） | 法人持股結構 | 同上 |

**規則：**
- `months_back` 預設 12，本 Skill 只取**近三個月**的升降評，其餘不寫入
- 新聞只回標題與摘要 → **需要全文分析時**，拿回傳的 URL 再照 §2.1 黃金規則爬全文
- 標題未提到該公司的新聞，照 §5.3 第 2 條**直接排除**（非美股常見雜訊）
- **只寫 yfinance 實際回傳的內容**，摘要不足就寫摘要，不可自行補完（鐵律 🚫2）
- yfinance 回空 → 照 §5.1 寫「已查詢 yfinance，過去三個月無符合內容」，**不需**跑 §2 MCP 鏈（它不是爬蟲，換爬蟲工具無意義）

**存檔範本：**

````markdown
## [Yahoo Finance News（yfinance MCP）]

- **yfinance ticker**：UHS
- **抓取時間**：YYYY-MM-DD
- **抓取方式**：yfinance MCP `get_yahoo_finance_news`
- **抓取結果**：✅ 成功（10 則，其中 N 則屬近三個月且與公司直接相關）

### 🎯 [主題]
- **來源連結**: [URL](URL) ← yfinance 回傳的真實 URL
- **發布時間**: YYYY-MM-DD
- **核心觀點**:
  > "yfinance 回傳的 Summary 原文..."
- **利多／利空判定**: 利多 / 利空 / 中性

## [分析師評等（yfinance MCP）]

- **抓取方式**：yfinance MCP `get_recommendations`（`upgrades_downgrades`, months_back=3）
- **抓取結果**：✅ 成功

| 日期 | 券商 | 前評等 → 新評等 | 動作 |
|:-----|:-----|:----------------|:-----|
````

---

## §6 Phase 4 — Convert2md 轉換

Phase 2 完成後，主代理人**自動呼叫 `Convert2md` Skill**：
- 掃描資料夾中的 PDF/HTML → 轉為乾淨 Markdown
- 清除 XBRL/iXBRL 標籤與 SEC blob
- ⚠️ 字型缺字的 `(cid:N)` 亂碼無法修復，應在 §4.2 下載階段就換英文版避開
- ✅ **§4.0 的 `{TICKER}_yfinance_{yyyyMMdd}.md` 已是 Markdown，不需轉換，Convert2md 會自動略過**

---

## §7 Phase 5 — 產出報告 + Push master

報告路徑：`FinancialReport/Log/CollectsentimentAndReports_Summary_{yyyyMMdd}.md`

> **報告產出後，強制 push 所有變更到 `master` branch，任務才算完成。**

### §7.1 報告範本

```markdown
# 任務執行最終報告 - YYYY/MM/DD

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 檔案名稱 | 狀態 |
|:----------|:---------|:---------|:-----|
| `2881富邦金` | yfinance MCP | `2881_yfinance_20260827.md` | 財務數據成功 |
| `2881富邦金` | 財報狗 | `2881_AnnualReport_2024.pdf` | 下載成功 |
| `2881富邦金` | yfinance、PTT、雪球 | `202608_輿情新聞.md` | 輿情更新成功 |

## 1.5 yfinance 抓取結果（強制填寫）
| 項目 | 內容 |
|:-----|:-----|
| 使用 ticker | `2881.TW` |
| `get_stock_info` | ✅ 成功 |
| `income_stmt` / `balance_sheet` | ✅ 成功（年度資料 4 年 ⚠️ 不足 5 年） |
| `quarterly_income_stmt` | ✅ 成功（最近一季部分欄位為 null） |
| `get_yahoo_finance_news` | ✅ 1 則（非美股新聞量少，已補在地來源） |
| `get_recommendations` | ✅ / ❌ |
| 資料缺口 | 列出所有 N/A 欄位與原因 |

## 2. 失敗或被擋網站
- **來源**: [網站名稱](URL)
- **原因**: (Cloudflare 阻擋／連線逾時／付費牆等)
- **已試過的 MCP**: firecrawl / brightdata / apify / playwright

## 3. 資料缺失說明
- 說明為何某些財報或輿情找不到

## 4. 異常檔案刪除紀錄
- 說明哪些檔案因 <10KB、無公司名稱、或 (cid: 亂碼過多而被刪除

## 5. 本次使用的 MCP（強制填寫）
| MCP 名稱 | 工具 | 用途 |
|:---------|:-----|:-----|
| yfinance | `get_stock_info` | 取得 EPS／PE／ROE／流通股數 |
| yfinance | `get_financial_statement` | 取得年度與季度損益表、資產負債表 |
| yfinance | `get_yahoo_finance_news` | 取得該股新聞清單 |
| Firecrawl | `firecrawl_scrape` | 抓格隆匯文章 |
| （若無使用） | — | 本次未使用 MCP，僅使用內建工具 |
```

**MCP 紀錄規則：**
- 用人類可讀名稱（`Firecrawl`、`Bright Data` 等），不要用 UUID
- 每筆含：MCP 名稱、工具名、用途一句話
- 完全沒用 MCP 時寫明「未使用 MCP，僅使用內建工具」

---

## §8 完整性保護

- 放棄某網站也**不要留空白檔案** → 改用 §5.5 誠實記錄格式
- 某來源被擋 → 先照 §2 跑 MCP 鏈 → 全失敗才換下一個來源