---
name: CollectsentimentAndReports
description: 收集個股「最新財務報告」與「輿情討論/新聞」
---
/goal
# CollectsentimentAndReports — 執行指南

你是 AI Agent。啟動此 Skill 時，依序完成：
1. 下載指定公司的「最新財報（2 年報 + 1 季報）」
2. 收集該公司「過去三個月內的社群輿情／新聞」
3. 轉換格式（Convert2md）
4. 產出報告並 push 到 `master`

---

## §0 鐵律（全篇最高優先，違反＝任務失敗）

| # | 鐵律 | 說明 |
|:--|:-----|:-----|
| 🚫1 | **禁止從 GitHub `a9303001/FinancialReport` 收集任何東西** | 不下載財報、不抓新聞、不讀輿情 |
| 🚫2 | **禁止捏造內容（防幻覺）** | 不可自行撰寫模擬討論、不可捏造 URL／日期／用戶 ID；爬取失敗就誠實記錄失敗，不可用訓練知識填充 |
| 🚫3 | **禁止訪問 `macrotrends.net`** | 該站持續封鎖爬蟲 |
| ✅4 | **即時存檔** | 每下載完一份財報、每爬完一個網站的輿情，立刻存檔。不要等全部做完才存 |
| ✅5 | **抓不到 → 照 §2 黃金規則跑 MCP 鏈** | 任何地方遇到抓不到／空白／被擋，統一回到 §2 處理 |

---

## §0.5 工具對照表

> 本指南用「動作」描述，不綁定特定工具名。看到任何工具名（如 `read_url`、`WebFetch`）都視為「該動作」，用你有的工具完成即可。

| 動作 | Claude | Gemini / 其他 |
|:-----|:-------|:---------------|
| 網路搜尋 | `WebSearch` | `search_web` / `google_search` |
| 抓取網頁 | `WebFetch` | `read_url` / `read_url_content` |
| MCP 爬取 | `firecrawl_scrape` 等 | 同（已連接的 MCP 工具） |
| 讀寫檔案 | `Read` / `Edit` / `Write` | `view_file` / `write_file` / `edit_file` |
| 執行指令 | `Bash` | `run_shell_command` / `run_command` |

- 「內建工具」＝ AI 原生的抓取／搜尋工具
- 「MCP 工具」＝ `firecrawl` / `brightdata` / `apify` / `playwright` 這類外接爬取服務

---

## §0.6 執行參數

| 參數 | 說明 | 範例 | 若缺失 |
|:-----|:-----|:-----|:-------|
| `COMPANY_TICKER` | 股票代碼 | `2881`, `UHS`, `03606` | **必填**，立刻詢問使用者 |
| `COMPANY_NAME` | 公司名稱 | `富邦金`, `福耀玻璃` | **必填**，若無則先搜尋查出 |

---

## §1 執行流程

```
Phase 1（主代理人）→ 建目錄
Phase 2（子代理人）→ 下載財報
Phase 3（子代理人）→ 抓輿情新聞
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

---

## §3 Phase 1 — 建立目錄

建立 `FinancialReport/{COMPANY_FOLDER_NAME}/`：
- 台／日／港股：`{代碼}{名稱}`（如 `2881富邦金`、`03606福耀玻璃`）
- 美股：`{代碼}`（如 `UHS`）
- 資料夾不存在就自動建立

---

## §4 Phase 2 — 下載財報

> 目標：最新 2 份年報 + 1 份季報。找到一份就立刻下載存檔。已存在的跳過。抓取遇阻回 §2。

### §4.1 先盤點 → 再決定缺什麼

列出資料夾現有檔案，靠檔名判斷已有哪些年報／季報，再決定要下載哪些。

**統一命名規則（新檔必須遵守）：**

| 類型 | 格式 | 範例 |
|:-----|:-----|:-----|
| 年報 | `{TICKER}_AnnualReport_{FY}.{ext}` | `5306_AnnualReport_2025.pdf` |
| 季報 | `{TICKER}_Quarter_{FY}Q{N}.{ext}` | `5306_Quarter_2026Q1.pdf` |

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

- **台股**：鉅亨網、MoneyDJ、經濟日報、PTT 股市板、Dcard 理財、股市爆料同學會（✅ 直接打 API，見 §2.8）、財報狗社群
- **美股**：Yahoo Finance、Bloomberg（⚠️ 付費牆）、Reuters（⚠️ 封鎖）、X、Reddit（⚠️ 封鎖）、Seeking Alpha、格隆匯（⚠️ JS 渲染，見 §2.9）
- **港股**：香港經濟日報、雪球（⚠️ 見 §2.7）、moomoo（⚠️ JS）、東方財富股吧（⚠️ JS）、格隆匯（⚠️ 見 §2.9）、LIHKG
- **日股**：日經新聞、Yahoo Finance JP 掲示板、note、5ch、X

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

---

## §6 Phase 4 — Convert2md 轉換

Phase 2 完成後，主代理人**自動呼叫 `Convert2md` Skill**：
- 掃描資料夾中的 PDF/HTML → 轉為乾淨 Markdown
- 清除 XBRL/iXBRL 標籤與 SEC blob
- ⚠️ 字型缺字的 `(cid:N)` 亂碼無法修復，應在 §4.2 下載階段就換英文版避開

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
| `2881富邦金` | 財報狗 | `2881_AnnualReport_2024.pdf` | 下載成功 |
| `2881富邦金` | PTT、雪球 | `202608_輿情新聞.md` | 輿情更新成功 |

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