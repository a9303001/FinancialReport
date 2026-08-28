---
name: CollectsentimentAndReports
description: 收集個股的「最新財報」與「輿情討論/新聞」，存成 Markdown 並 push 到 master。財務數據優先用 yfinance MCP；輿情一律「先爬蟲、後搜尋」兩階段都做，並以完整原文存檔。使用者提到收集財報、收集輿情、collect sentiment、抓某檔股票資料時觸發。
---

# CollectsentimentAndReports

> **這是操作手冊，不是參考資料。照著 A 段做，卡住才翻後面。**
> 讀完 A 段（約 80 行）就可以開始執行，不必讀完整份。
> 本文件適用任何模型（Claude / Gemini Flash / Sonnet）。每一步都寫成「做什麼 → 用什麼工具 → 存到哪個檔」，不要自行發揮。

---

# A. 一頁執行卡

## A-0 三句話版本（記不住別的就記這三句）

1. **財報數據**：先打 `yfinance` API，再下載年報／季報 PDF。
2. **輿情**：**先爬蟲（E-3）→ 再搜尋（E-4、E-5）**，兩個階段都必須做，缺一不可。
3. **輿情內容一律「完整原文照抄」**（E-2），不准只寫一行摘要，不准自己編。

## A-1 我要做什麼

給定一檔股票，把它的**財報**和**輿情**抓下來存檔，最後 push 到 `master`。

## A-2 輸入參數

| 參數 | 意思 | 範例 | 沒有的話 |
|:--|:--|:--|:--|
| `COMPANY_TICKER` | 股票代碼 | `2881`、`UHS`、`03606` | **必填** → 立刻問使用者 |
| `COMPANY_NAME` | 公司名稱 | `富邦金`、`福耀玻璃` | **必填** → 先搜尋查出來 |
| `YF_TICKER` | yfinance 專用代碼 | `2881.TW`、`UHS`、`3606.HK` | 查 **D-2 後綴表**自己推導 |

`COMPANY_FOLDER_NAME`（資料夾名）＝
- 台／日／港股：`{代碼}{名稱}`，例：`2881富邦金`、`03606福耀玻璃`（港股補滿 5 碼）
- 美股：`{代碼}`，例：`UHS`

## A-3 五個步驟（照順序做，不可跳）

| 步驟 | 做什麼 | 產出檔案 | 章節 |
|:--:|:--|:--|:--|
| **1** | 建公司資料夾 | `{COMPANY_FOLDER_NAME}/` | C |
| **2** | yfinance 抓財務數據 → 存檔<br>找財報網址 → 下載 PDF | `{代碼}_yfinance_{yyyyMMdd}.md`<br>`{代碼}_AnnualReport_{年}.pdf` | D |
| **3** | **輿情：① 先爬在地討論區 → ② 再用 Exa 搜尋 → ③ 再補 yfinance 新聞** | `{yyyyMM}_輿情新聞.md` | E |
| **4** | 呼叫 `Convert2md` skill 把 PDF 轉 Markdown | `*.md` | F |
| **5** | 寫執行報告 → `git push` 到 `master` | `Log/CollectsentimentAndReports_Summary_{yyyyMMdd}.md` | G |

## A-4 四個核心觀念（記住這四個就不會出大錯）

1. **財務數字先用 API。**
   `yfinance` 是 API，不會被 Cloudflare 擋，幾秒就有 EPS／PE／ROE。步驟 2 一定先跑它。
2. **輿情先爬、後搜，兩階段都要做。**
   - **先爬**：直接去討論區網站抓原始貼文與留言（E-3）。爬到的東西才有完整原文、有推文、有真實用戶語氣。
   - **再搜**：用 Exa／yfinance 搜尋補齊爬不到的站、法人觀點、外媒新聞（E-4、E-5）。
   - ⚠️ 只爬不搜 ❌　只搜不爬 ❌　**兩個都做才算完成**。
3. **輿情要「完整敘述」。**
   抓到什麼就完整照抄什麼：完整標題、完整內文、完整留言、完整日期、完整 URL。**禁止只寫一句摘要**。詳見 **E-2**。
4. **抓到就馬上存檔，抓不到就誠實寫「抓不到」。**
   抓完一個來源 → 立刻寫檔 → 再抓下一個。絕對不可以用自己的知識編內容、編網址、編日期。寫失敗紀錄（**E-8**）比編一段假討論好一萬倍。

## A-5 鐵律（違反＝任務失敗）

| # | 鐵律 | 白話 |
|:--|:--|:--|
| 🚫1 | **不從 `a9303001/FinancialReport` 收集資料** | 這個 repo 是**輸出目的地**，不是資料來源。不從這裡下載財報、抓新聞、讀輿情。 |
| 🚫2 | **不捏造任何內容** | 不寫模擬討論、不編 URL／日期／用戶 ID。爬失敗就記錄失敗，**不可以用訓練知識填空**。 |
| 🚫3 | **不訪問 `macrotrends.net`** | 該站長期封鎖爬蟲，純浪費時間。 |
| 🚫4 | **`null` 一律寫 `N/A`** | 不准用推估值或其他年度的數字補。 |
| 🚫5 | **輿情不准只寫摘要** | 一則貼文只寫「網友看好」＝失敗。必須有**完整原文引述**（E-2）。 |
| ✅6 | **即時存檔** | 每抓完一份財報、每爬完一個網站，立刻存檔。 |
| ✅7 | **輿情先爬後搜、兩者都做** | 爬（E-3）完成後才進搜尋（E-4、E-5）；只做其中一段＝未完成。 |
| ✅8 | **抓不到就換工具** | 依 **B-2** 的順序換，不要卡在同一個工具重試。 |

## A-6 完成定義（Definition of Done）

以下全部做到才算完成，缺一項就還沒完成：

- [ ] `{代碼}_yfinance_{yyyyMMdd}.md` 存在（或報告裡寫明為何沒有）
- [ ] `{yyyyMM}_輿情新聞.md` 存在
- [ ] 該檔**同時包含**：① 至少 1 個「爬蟲階段」章節（E-3）② `## [Exa 語意搜尋]` 章節（E-4）③ yfinance 章節（E-5）
      → 任一階段全部失敗，也**必須有該階段的失敗紀錄章節**（E-8），不可整段消失
- [ ] 每一筆輿情都有**真實 URL**、**真實日期**、**完整原文引述**（非一行摘要）
- [ ] 討論區類來源有抓到**留言／推文**（或註明該文無留言）
- [ ] 所有絕對金額都有**每股金額**標註
- [ ] 所有 `null` 都寫成 `N/A`
- [ ] 執行報告已寫入 `Log/`
- [ ] 已 `git push` 到 `master`

---

# B. 工具與抓取策略

## B-1 工具對照表（Claude / Gemini / Sonnet 通用）

> 本文件用「**動作**」描述。看到工具名，用你手上同類的工具做就好。

| 動作 | Claude | Gemini／其他 |
|:--|:--|:--|
| **爬網頁（首選）** | `firecrawl_scrape` | 同（已連接的 Firecrawl MCP） |
| **爬網頁（次選）** | `scrape_as_markdown`（Bright Data） | 同 |
| **語意搜尋** | Exa MCP `web_search_exa` | 同（已連接的 Exa MCP） |
| **讀網頁（Exa 版）** | Exa MCP `web_fetch_exa` | 同 |
| **結構化財務數據** | yfinance MCP `mcp__yfinance__*` | 同（已連接的 yfinance MCP） |
| 一般網路搜尋 | `WebSearch` | `search_web` / `google_search` |
| 一般抓網頁 | `WebFetch` | `read_url` / `read_url_content` |
| 瀏覽器自動化 | `playwright` | 同 |
| 讀寫檔案 | `Read` / `Write` / `Edit` | `view_file` / `write_file` / `edit_file` |
| 執行指令 | `Bash` | `run_shell_command` |

**三類工具的差別：**

| 類型 | 代表 | 特性 | 何時用 |
|:--|:--|:--|:--|
| **資料型 API** | `yfinance` | 直接回結構化 JSON，不受封鎖 | 抓財務數字 → **步驟 2 第 1 個跑** |
| **爬蟲** | `firecrawl` / `brightdata` / `apify` / `playwright` | 實際去爬網址，拿得到**完整正文＋留言** | 抓輿情 → **步驟 3 第 1 個跑** |
| **搜尋型 API** | `Exa` | 語意搜尋，結果附正文摘錄，不會被擋 | 爬完之後補漏、找法人觀點 → **步驟 3 第 2 個跑** |

> 📌 **為什麼輿情要先爬？** 爬蟲拿到的是完整貼文＋完整留言串，符合「完整敘述」要求；搜尋只回片段 Highlights。所以**爬是主力、搜是補漏**。

## B-2 抓不到怎麼辦：固定換手順序

### B-2-1 輿情（步驟 3）用這條

```
【階段 1｜爬】對 E-3 清單上的每個站點，依序試：
  ① 查 B-7 表 → 該站有指定工具就直接用那個（省時間）
  ② firecrawl_scrape
  ③ brightdata scrape_as_markdown
  ④ apify
  ⑤ playwright
  ⑥ 內建工具（WebFetch / read_url）
        │該站全部失敗
        ↓
  照 E-8 寫該站的失敗紀錄 → 換下一站（不要卡住）

【階段 2｜搜】不管階段 1 成功或失敗，都一定要做：
  Exa web_search_exa（E-4）→ yfinance 新聞／評等（E-5）
        │需要某篇全文
        ↓
  web_fetch_exa → 失敗則回到上面爬蟲鏈試該篇 URL
```

### B-2-2 財報下載（步驟 2）用這條

```
先用 Exa 找 PDF 網址 → 直接下載 → 驗證（D-4）
下載失敗 → firecrawl → brightdata → apify → playwright → 內建工具
```

### B-2-3 共通規則

| 規則 | 內容 |
|:--|:--|
| **順序不可跳** | 除非環境沒連上該 MCP，才可跳過並在報告註明。 |
| **每個工具最多試 2 次** | 失敗就換下一個，**禁止無限重試**。 |
| **「明確拒絕」也算失敗** | 例如 Firecrawl 回 `we do not support this site` → 立刻換下一個。 |
| **整條鏈都不行** | 改用各 MCP 的搜尋功能（`firecrawl_search`、`search_engine`）搜該站內容。 |
| **WebSearch 摘要是最後手段** | 必須標註「⚠️ 全部抓取失敗，以下為 WebSearch 摘要」。 |
| **爬失敗不等於可以跳過搜尋** | 階段 1 全掛，階段 2 照跑（鐵律 ✅7）。 |

## B-3 什麼叫「抓取失敗」（符合任一項就換工具）

- **空白／只有骨架**：回傳空白、只有選單導覽、沒有正文
- **被封鎖**：`not accessible to our user agent`、`domain not accessible`、HTTP 400
- **防護頁**：Cloudflare `Just a moment...`、HTTP 403 / 429
- **WAF 亂碼**：一長串 Base64 亂碼，或 `_waf_` 開頭的 JSON（雪球典型症狀）
- **內容太短**：正文 < 200 字且沒有任何留言 → 視同失敗，換工具再試一次

## B-4 純網路錯誤 → 零重試，直接換來源

看到以下錯誤**不要套爬蟲鏈**，直接放棄該 URL、刪掉暫存檔、換下一個來源：

- Read Timeout / EOF / Connection Reset
- `ECONNREFUSED` / `EHOSTUNREACH` 等 Socket 錯誤

> ⚠️ **Timeout 和 EOF 最容易讓 Agent 卡死。絕對不可以重試或空等。**

## B-5 頻率控制（只約束爬蟲，Exa／yfinance 不受限）

| 規則 | 說明 |
|:--|:--|
| 同網域間隔 | 至少 **3 秒** |
| 交錯爬取 | A 站 → B 站 → C 站 → A 站，不要一口氣爬完一站 |
| 單站上限 | 同一網域最多爬 **8 頁**（列表 1～2 頁 ＋ 內文 6 篇） |

## B-6 呼叫次數預算（防止卡在同一件事上）

| 階段 | 建議上限 | 超過就 |
|:--|:--|:--|
| yfinance（步驟 2） | 6 次呼叫 | 有拿到 `get_stock_info` 就先存檔往下走 |
| **輿情爬蟲（步驟 3 階段 1）** | **每站 6 次工具呼叫；全部站點合計約 25 次** | 照 E-8 記錄失敗，**進入階段 2 搜尋** |
| **Exa 搜尋（步驟 3 階段 2）** | 3～5 條 query | 換下一個來源 |
| 財報下載（步驟 2） | 每份報告 6 次工具呼叫 | 照 D-4 換來源或記錄失敗 |
| 單一公司總計 | 約 60 次工具呼叫 | 存好現有成果，在報告寫明未完成項目 |

## B-7 難爬網站查表（查表決定用哪個工具，別瞎試）

| 網站 | 網域 | 症狀 | **爬取階段建議工具** |
|:--|:--|:--|:--|
| 股市爆料同學會 | `cmoney.tw` | Nuxt SSR 殼，貼文為空 | ✅ **直接打官方 API**（附錄 I-1），可抓全文＋留言 |
| 格隆匯 | `gelonghui.com` | Nuxt.js SSR | ✅ `firecrawl_scrape`（附錄 I-2） |
| 雪球 | `xueqiu.com` | **WAF 加密**，Exa fetch 拿到亂碼 | ✅ `brightdata scrape_as_markdown`（附錄 I-3） |
| PTT 股板 | `ptt.cc` / `pttweb.cc` | 舊版頁面單純 | ✅ `firecrawl_scrape` 抓 `pttweb.cc` 文章頁（含推文）；失敗改 Exa 搜尋 |
| 東方財富股吧 | `guba.eastmoney.com` | JS 分頁載入 | ✅ `firecrawl_scrape` 抓 `guba.eastmoney.com/list,{代碼}.html`；內文頁 `/news,{代碼},{id}.html` |
| Mobile01 / Dcard | `mobile01.com` / `dcard.tw` | 部分需 JS | `firecrawl_scrape` → `playwright` |
| MOPS 台股查詢 | `mops.twse.com.tw` | 需 JS 互動／POST | `playwright` 或直接組 POST |
| moomoo 社區 | `moomoo.com` | JS 載入正文 | `firecrawl_scrape` → `playwright` |
| Yahoo 股市 JP 掲示板 | `finance.yahoo.co.jp` | JS 載入 | `firecrawl_scrape` → `playwright` |
| 5ch / minkabu / kabutan | `5ch.net` 等 | 一般可爬 | `firecrawl_scrape` |
| Reddit | `reddit.com` | 封鎖爬蟲，Firecrawl 也拒絕 | ⚠️ 爬蟲多半失敗 → 記錄失敗後改 Exa 搜尋／`firecrawl_search` |
| 新浪財經 | `finance.sina.com.cn` | — | `firecrawl_scrape` 可讀；搜尋階段 Exa 也可取全文摘錄 |
| Reuters | `reuters.com` | 封鎖 | `firecrawl_scrape` 通常可讀公司頁 |
| Bloomberg | `bloomberg.com` | 付費牆 | 取摘要即可，並註明「付費牆，僅摘要」 |

> 📌 遇到**新的**難爬網站，處理完把它加進這張表，下次不用重踩。

---

# C. 步驟 1 — 建立資料夾

建立 `FinancialReport/{COMPANY_FOLDER_NAME}/`（命名規則見 **A-2**）。資料夾不存在就自動建立。

---

# D. 步驟 2 — 財務數據與財報下載

**目標**：(a) yfinance 結構化數據，(b) 最新 2 份年報 ＋ 1 份季報。

## D-1 先做：yfinance 財務數據快照

> **為什麼先做**：幾秒內就能拿到 EPS／PE／ROE／負債比／流通股數，不受任何封鎖。
> 就算後面 PDF 全部下載失敗，這份資料仍能撐起分析。

**動作：**

1. 查 **D-2 後綴表**決定 `YF_TICKER`（⚠️ 港股不要補零）
2. 呼叫這幾個工具（一次抓齊，不要分批來回）：
   - `get_stock_info`
   - `get_financial_statement` → `income_stmt`
   - `get_financial_statement` → `balance_sheet`
   - `get_financial_statement` → `quarterly_income_stmt`
   - `get_financial_statement` → `cashflow`（需要自由現金流時）
   - `get_stock_actions`（需要配息／分割紀錄時）
3. **驗證**：`get_stock_info` 只回一兩個欄位、幾乎全是 `null`（典型 `{"trailingPegRatio": null}`）＝ **ticker 打錯了**，不是這家公司沒資料。
   - 先檢查後綴（港股別補零、台股試 `.TWO`）
   - 仍失敗 → `web_search_exa` 搜「{公司名稱} yahoo finance ticker symbol」確認
   - 再失敗 → 在報告寫「yfinance 無此標的」，改走 **D-4** 傳統下載，**不可捏造數據**
   - **最多重試 2 次**
4. **立刻存檔**（鐵律 ✅6）

**檔名**：`{TICKER}_yfinance_{yyyyMMdd}.md`，例：`2881_yfinance_20260827.md`
- `{TICKER}` 用**資料夾代碼**（`2881`），**不含** `.TW` 後綴
- 同日重跑就覆蓋；不同日期另存新檔（保留歷史快照）

**存檔範本（照抄填值）：**

````markdown
# [{代碼} {公司名稱}] yfinance 財務數據快照

- **yfinance ticker**：2881.TW
- **抓取時間**：YYYY-MM-DD HH:MM
- **資料來源**：yfinance MCP（Yahoo Finance）
- **財報幣別**：TWD（`financialCurrency`）
- **流通股數**：13,665,721,905（`sharesOutstanding`）← 每股化換算基準

## 1. 核心指標（AGENTS.md 必備數據）

| 指標 | 數值 | 來源欄位 |
|:--|:--|:--|
| 最新 EPS | 8.37 | `trailingEps` |
| 預估 EPS | 10.26 | `forwardEps` |
| PE（TTM / Forward） | 16.55 / 13.50 | `trailingPE` / `forwardPE` |
| 營業利益率 | 48.47% | `operatingMargins` |
| ROE | 18.74% | `returnOnEquity` |
| 殖利率 | 3.07% | `dividendYield` |
| 負債比率 | X.XX% | `Total Liabilities / Total Assets × 100%` |
| OPM（自定義） | X.XX% | `(營業利益率 / 稅前淨利率) × 100%` |
| 淨利 5 年 CAGR | X.XX% ⚠️ 僅 N 年資料 | `income_stmt` 各年 `Net Income` |

> 計算過程要列出算式，不可只給結果。

## 2. 年度損益表（近 N 年）
| 年度 | 營收 | 營業利益 | 稅前淨利 | 淨利 | 每股營收 | 每股淨利 |
|:--|--:|--:|--:|--:|--:|--:|

## 3. 季度損益表（近 N 季）
| 季度 | 營收 | 營業利益 | 淨利 | EPS |
|:--|--:|--:|--:|--:|

## 4. 資產負債重點
| 年度 | 總資產 | 總負債 | 股東權益 | 負債比率 |
|:--|--:|--:|--:|--:|

## 5. 流通股數變化
| 期間 | Basic Average Shares | 增減% | 說明 |
|:--|--:|--:|:--|

## 6. 資料缺口
- 例：`quarterly_income_stmt` 2025-09-30 多數欄位為 null，Yahoo 尚未補齊
- 例：年度資料僅 4 年，5 年中位數／CAGR 不足，須補其他來源
````

**三條規則：**
- ⚠️ 所有絕對金額**必須同步標註每股金額**（除以 `sharesOutstanding`）
- ⚠️ `null` 寫 `N/A`，**禁止**用訓練知識或推估值填充
- ⚠️ 這份數據**不能取代年報／季報全文**，仍要繼續做 **D-3、D-4**

**欄位對照（AGENTS.md 必備數據 ← yfinance）：**

| 要什麼 | 從哪來 | 欄位／算法 |
|:--|:--|:--|
| 最新 EPS | `get_stock_info` | `trailingEps` |
| 本益比 PE | `get_stock_info` | `trailingPE`、`forwardPE` |
| 預估 EPS | `get_stock_info` | `forwardEps`、`epsCurrentYear` |
| 營業利益率 | `get_stock_info` / `income_stmt` | `operatingMargins`；或 `Operating Income / Total Revenue` |
| 負債比率 | `balance_sheet` | `Total Liabilities Net Minority Interest / Total Assets × 100%` |
| OPM（自定義） | `income_stmt` | `(營業利益率 / 稅前淨利率) × 100%`，稅前淨利率＝`Pretax Income / Total Revenue` |
| ROE | `get_stock_info` | `returnOnEquity` |
| 殖利率 | `get_stock_info` / `get_stock_actions` | `dividendYield`、`fiveYearAvgDividendYield` |
| 淨利 CAGR | `income_stmt` | 由各年度 `Net Income` 自己算 |
| **每股化基準** | `get_stock_info` | **`sharesOutstanding`** |
| 流通股數變化 | `income_stmt` + `get_stock_actions` | `Basic/Diluted Average Shares` 逐季比對、`lastSplitFactor` |

**已知限制（必須寫進報告，不可假裝沒事）：**
- 年度財報通常**只回 4 年** → 5 年中位數／CAGR 可能不足，註明「yfinance 僅 N 年，需補其他來源」
- 最近一季常有大量 `null`（Yahoo 尚未補齊）→ 以有值的最近一季為準並註明日期
- 金融股（如 `2881.TW`）的 `Total Revenue`、`operatingCashflow` 口徑與製造業不同，要註明
- `financialCurrency` 是**財報幣別，可能不同於股價幣別**，換算每股金額前務必確認

## D-2 Ticker 後綴表（最容易出錯，務必先查）

| 市場 | 格式 | 範例 | 備註 |
|:--|:--|:--|:--|
| 美股 | `{代碼}` | `UHS`、`AAPL` | 無後綴 |
| 台股（上市） | `{4碼}.TW` | `2881.TW` | — |
| 台股（上櫃） | `{4碼}.TWO` | `6488.TWO` | `.TW` 抓不到時改試 `.TWO` |
| 港股 | `{4碼}.HK` | `3606.HK` | ⚠️ **不可補零成 5 碼**，`03606.HK` 會失敗 |
| 日股 | `{4碼}.T` | `3445.T` | — |
| 中國 A 股（滬） | `{6碼}.SS` | `600519.SS` | — |
| 中國 A 股（深） | `{6碼}.SZ` | `000333.SZ` | — |

> ⚠️ **港股陷阱**：**資料夾**要補滿 5 碼（`03606福耀玻璃`），但 **yfinance 必須用 4 碼**（`3606.HK`）。兩者不同，不要混用。

## D-3 先盤點資料夾 → 再決定缺什麼

列出資料夾現有檔案，靠檔名判斷已有哪些年報／季報，只下載缺的。

**新檔命名規則（必須遵守）：**

| 類型 | 格式 | 範例 |
|:--|:--|:--|
| 年報 | `{TICKER}_AnnualReport_{FY}.{ext}` | `5306_AnnualReport_2025.pdf` |
| 季報 | `{TICKER}_Quarter_{FY}Q{N}.{ext}` | `5306_Quarter_2026Q1.pdf` |
| yfinance 快照 | `{TICKER}_yfinance_{yyyyMMdd}.md` | `5306_yfinance_20260827.md` |

- `{ext}`：下載時保留原始 `.pdf` / `.html`，轉換後才變 `.md`
- `{FY}`：**財報所屬年度**（西元年），不是申報日期也不是下載日期
- 舊檔不強制改名

## D-4 下載財報（找到即停）

> ⚠️ D-1 給的是**數字**，不是年報原文，**不算完成這一步**。
> 這一步要拿到可做文字分析（風險因素、MD&A、管理層討論）的**原始報告檔**。

**第 0 步（所有市場共通）：先用 Exa 找下載網址**

```
web_search_exa → "{公司名稱} {代碼} annual report {年份} PDF investor relations"
web_search_exa → "{公司名稱} {代碼} {年份}年度報告 季度報告 下載"
```

Exa 常能直接給出官網 IR 的 PDF 連結，比逐一試各平台快很多。拿到 URL 直接下載，再照下面驗證。

**第 1 步以後：各市場專屬來源**

| 市場 | 順序 |
|:--|:--|
| **台股 (TW)** | 1. MOPS/TWSE（POST 取檔，英文版 `_AIA.pdf` 優先）<br>2. 財報狗 `statementdog.com/analysis/{代碼}/e-report`<br>3. 官網 IR |
| **美股 (US)** | 1. 官網 IR<br>2. SEC EDGAR<br>3. 財報狗<br>4. 富途牛牛 `futunn.com/hk/stock/{代碼}-US/announcement` |
| **日股 (JP)** | 1. 官網 IR（優先英文 Annual Report）<br>2. EDINET<br>3. IR Bank `irbank.net/{代碼}/ir`<br>4. 富途牛牛 `futunn.com/hk/stock/{代碼}-JP/announcement` |
| **港股 (HK)**（代碼補 5 碼） | 1. HKEXnews `www1.hkexnews.hk/search/titlesearch.xhtml?lang=en`<br>2. 新浪財經 `stock.finance.sina.com.cn/hkstock/notice/{5碼}.html`<br>3. 富途牛牛 `futunn.com/hk/stock/{5碼}-HK/announcement` |

**下載驗證（每下載一份就馬上驗，不要等到步驟 4 才發現是壞檔）：**

| 檢查 | 標準 | 不通過 → |
|:--|:--|:--|
| 英文優先 | 有英文版就下英文版（避免中文 PDF `(cid:N)` 亂碼） | — |
| 檔案大小 | ≥ 10KB | 刪除，換來源 |
| 內容檢查 | 前 4 頁有公司名稱或代碼 | 刪除，換來源 |
| `(cid:` 亂碼 | 整份 ≤ 50 次 | 刪除，換英文版或換來源 |
| 網路錯誤 | Timeout / EOF / Reset | 零重試，照 **B-4** |

---

# E. 步驟 3 — 輿情與新聞收集（先爬 → 再搜）

**時間範圍：過去三個月內。**

## E-0 這一步的執行順序（不可顛倒、不可省略）

```
E-1 建檔／決定要爬哪些站
      ↓
【階段 1｜爬】E-3 逐站直接爬取（主力，取完整原文＋留言）
      ↓  每爬完一站就立刻 Append 存檔
【階段 2｜搜】E-4 Exa 語意搜尋（補漏：法人觀點、爬不到的站、外媒）
      ↓  存檔
【階段 2｜搜】E-5 yfinance 新聞／評等／內部人交易
      ↓  存檔
E-6 合併去重 → E-7 過濾 → E-9 完整度自檢
```

| 常見錯誤 | 正確做法 |
|:--|:--|
| ❌ 只用 Exa 搜一搜就交差 | 階段 1 的爬蟲**一定要先跑**，至少涵蓋 E-3 清單中 3 個站 |
| ❌ 爬失敗就整個跳過輿情 | 寫失敗紀錄（E-8）後，**照樣進入階段 2** |
| ❌ 爬到全文卻只寫兩行摘要 | 照 **E-2** 完整照抄 |
| ❌ 先搜完再想要不要爬 | 順序反了。**先爬**才拿得到完整貼文與留言 |

## E-1 存檔規則（一月一檔，Append 模式）

| 項目 | 規則 |
|:--|:--|
| **檔名** | `{yyyyMM}_輿情新聞.md`（`yyyyMM` ＝ **執行當月**，如 `202608`） |
| **路徑** | `FinancialReport/{COMPANY_FOLDER_NAME}/{yyyyMM}_輿情新聞.md` |
| **寫入模式** | **Append**：新來源加到檔案末尾；該來源已有章節 → 在該章節末尾補充 |
| **不要覆蓋** | 不准砍掉舊內容 |
| **舊格式相容** | 有舊檔（如 `202607_xueqiu.md`）不強制改名，新資料一律存進新格式 |
| **找不到也要寫** | 記錄「已搜尋 {來源}，過去三個月無符合內容」，避免下次重複嘗試 |

**Append 判斷：**

| 情況 | 動作 |
|:--|:--|
| 檔案不存在 | 建新檔 → 先寫標頭 → 再加來源章節 |
| 檔案存在，該來源**沒有**章節 | 在檔案末尾新增 `## [來源名稱]` |
| 檔案存在，該來源**已有**章節 | 在該章節末尾補充 |

**檔案標頭範本（建檔時先寫這段）：**

````markdown
# [{代碼} {公司名稱}] 輿情與新聞整理 ({YYYY}/{MM})

- **分析月份**：YYYY/MM
- **資料範圍**：過去三個月（YYYY-MM-DD ~ YYYY-MM-DD）
- **收集方式**：階段 1 爬蟲直取 → 階段 2 Exa 搜尋 → 階段 2 yfinance
- **最後更新**：YYYY-MM-DD HH:MM

---
````

## E-2 完整敘述規則（🚫 鐵律 5 的細則，寫每一則都要遵守）

> **核心要求：抓到多少原文，就寫多少原文。摘要是分析階段的事，收集階段只做「完整保存」。**

### E-2-1 每一則必填的 7 個欄位

| 欄位 | 要求 | 不可以 |
|:--|:--|:--|
| **標題** | 原標題**完整照抄** | 不可自行改寫或翻譯 |
| **來源網站** | 網站名稱（如 PTT 股板、雪球） | — |
| **來源連結** | 完整真實 URL | 不可編、不可縮短成首頁 |
| **發布時間** | `YYYY-MM-DD`（有時分就寫時分） | 抓不到寫「日期不明」，**不可推測** |
| **作者／ID** | 原始用戶名或媒體名 | 抓不到寫「未顯示」 |
| **完整原文** | 見 **E-2-2** | ❌ 一行摘要 ❌ 只貼網址 |
| **利多／利空判定** | 利多／利空／中性＋一句理由 | — |

### E-2-2 「完整原文」的判定標準

| 原文長度 | 怎麼寫 |
|:--|:--|
| **≤ 2,000 字** | **全文逐字照抄**，一個字都不刪 |
| **> 2,000 字** | 保留與投資判斷相關的**完整段落**（不是句子片段），並在結尾註明：`（原文共 N 字，此處保留 M 字，省略部分為 ○○○）` |
| **只有摘要可拿**（搜尋 Highlights、付費牆） | 照抄拿到的全部摘要，並標註 `⚠️ 僅取得摘要，來源為 {工具名稱}，未取得全文` |

**額外要求：**
- **表格、數字、引用的財務數據**要一併保留，不可省略
- **原文換行、條列結構**盡量保留
- 原文為外文（英／日）→ **先貼原文**，再視需要附中文翻譯；**不可只留翻譯**

### E-2-3 討論區必須連留言一起抓

爬討論區（PTT、股吧、雪球、CMoney、5ch、Mobile01…）時：

| 規則 | 內容 |
|:--|:--|
| **留言必抓** | 主文之外，至少抓 **10 則留言／推文**（少於 10 則就全抓） |
| **留言原文照抄** | 每則寫成 `- {ID}（{推/噓/→ 或讚數}）：「{原文}」` |
| **無留言** | 明確寫「該文無留言」，不可省略此欄 |
| **只寫「網友多空分歧」＝失敗** | 必須列出具體留言原文 |

### E-2-4 一則完整紀錄的範例（照這個格式寫）

````markdown
### 🎯 [完整原標題照抄]

- **來源網站**: PTT 股板
- **來源連結**: [https://www.pttweb.cc/bbs/Stock/M.1756...](https://www.pttweb.cc/bbs/Stock/M.1756...)
- **發布時間**: 2026-08-20 14:32
- **作者／ID**: kkxxx
- **抓取方式**: firecrawl_scrape
- **完整原文**:
  > 標的：2881 富邦金
  >
  > 分類：多
  >
  > 分析/正文：
  > 富邦金 7 月自結 EPS 0.89 元，累計前七月 EPS 7.02 元，年增 21%。
  > 主要貢獻來自富邦人壽避險成本下降與資本利得實現……
  > （以下逐字照抄到文末，不刪節）
- **留言／推文**（共 43 則，節錄前 15 則原文）:
  - `aaa123`（推）：「金融股今年真的猛，但要小心匯率」
  - `bbb456`（噓）：「已經漲一波了吧，追高小心」
  - `ccc789`（→）：「壽險股看匯率跟股債市，這篇沒提到避險成本細節」
  - …（依序照抄）
- **關鍵要點**:
  - 前七月累計 EPS 7.02 元，年增 21%
  - 留言多空比約 3:1，偏多但擔憂追高與匯率風險
- **利多／利空判定**: 利多（獲利年增 21%，留言情緒偏多）
````

## E-3 【階段 1｜爬】逐站直接爬取（主力）

> **這是輿情的主要來源，必須先做。** 目標：拿到完整貼文＋完整留言。

### E-3-1 先決定要爬哪些站（依市場挑，至少挑 3 個）

| 市場 | 必爬（優先序由上而下） | 建議工具 |
|:--|:--|:--|
| **台股** | ① 股市爆料同學會 `cmoney.tw`<br>② PTT 股板 `pttweb.cc`<br>③ 鉅亨網 `cnyes.com` 個股新聞<br>④ MoneyDJ、Mobile01 投資理財、Dcard 股票板 | ① 官方 API（I-1）<br>② `firecrawl_scrape`<br>③④ `firecrawl_scrape` |
| **美股** | ① Yahoo Finance 個股頁／新聞<br>② Seeking Alpha 個股頁<br>③ StockStory / TipRanks<br>④ Reddit（⚠️ 常失敗，失敗即記錄） | `firecrawl_scrape` → `brightdata` |
| **港股／A 股** | ① 雪球 `xueqiu.com/S/{代號}`（I-3）<br>② 東方財富股吧 `guba.eastmoney.com/list,{代碼}.html`<br>③ 格隆匯 `gelonghui.com`（I-2）<br>④ 新浪財經個股頁 | ① `brightdata`<br>②③④ `firecrawl_scrape` |
| **日股** | ① Yahoo Finance JP 掲示板<br>② minkabu.jp `minkabu.jp/stock/{代碼}`<br>③ kabutan.jp `kabutan.jp/stock/news?code={代碼}`<br>④ 5ch 相關討論串 | `firecrawl_scrape` → `playwright` |

### E-3-2 每一站的固定動作（逐站重複這 5 步）

```
第 1 步：查 B-7 表 → 這站有指定工具嗎？有就直接用，沒有就從 firecrawl_scrape 開始
第 2 步：爬「列表頁」→ 拿到近三個月的貼文 URL 清單
第 3 步：從清單挑 3～6 篇「與公司直接相關、有實質內容」的貼文
第 4 步：逐篇爬「內文頁」→ 取得完整正文＋留言（照 E-2 格式整理）
第 5 步：立刻 Append 寫入 {yyyyMM}_輿情新聞.md，章節名 ## [爬取｜{網站名稱}]
```

**卡住時的處理：**

| 情況 | 動作 |
|:--|:--|
| 列表頁爬不到 | 依 **B-2-1** 換下一個工具（最多 6 棒） |
| 列表頁 OK、內文頁失敗 | 至少保留列表頁拿到的標題＋URL＋日期，標註「⚠️ 內文爬取失敗，僅有列表資訊」 |
| 該站全部失敗 | 照 **E-8** 寫失敗紀錄 → **換下一站**，不要重試 |
| 站點數已達 3 個成功 | 可停止階段 1，進入階段 2 |

**章節命名（很重要，報告要對得起來）：**
- 爬取來的：`## [爬取｜{網站名稱}]`，例：`## [爬取｜PTT 股板]`
- 搜尋來的：`## [Exa 語意搜尋]`、`## [Yahoo Finance News（yfinance MCP）]`

**存檔範例：**

````markdown
## [爬取｜東方財富股吧]

- **抓取時間**：2026-08-28
- **抓取方式**：firecrawl_scrape（列表頁 `guba.eastmoney.com/list,600519.html` → 內文頁 4 篇）
- **抓取結果**：✅ 成功（列表 32 篇，篩選後精讀 4 篇，均為近三個月）

### 🎯 [完整原標題]
（以下照 E-2-4 的 7 欄位格式逐則寫，含完整原文與留言原文）
````

## E-4 【階段 2｜搜】Exa 語意搜尋（補漏）

> 階段 1 爬完後跑這一段。Exa 負責：法人研報、外媒新聞、以及爬不動的站（Reddit、雪球等）的替代內容。

**怎麼寫 query（這是用好 Exa 的關鍵）：**

Exa 是**語意**搜尋，它要的是「你想找的理想頁面長什麼樣」，不是關鍵字堆疊。

| ❌ 不要這樣寫 | ✅ 要這樣寫 |
|:--|:--|
| `福耀玻璃 3606` | `福耀玻璃 3606 港股 近期業績分析 投資人討論` |
| `UHS earnings` | `Universal Health Services UHS stock analysis bull bear case recent quarter` |
| `2881 PTT` | `PTT 股板 2881 富邦金 討論 標的分析` |

- **一個語系寫一條 query**：中文問題用中文寫、英文問題用英文寫
- **想要「觀點」就明講**：query 裡放 `分析`、`討論`、`利多 利空`、`bull bear case`、`風險`
- **想找特定站**：直接把站名寫進 query（`雪球`、`東方財富股吧`、`Seeking Alpha`），比 `site:` 語法有效
- **針對階段 1 失敗的站補搜**：例如 Reddit 爬失敗 → query 寫 `{TICKER} stock reddit discussion bull bear`
- **`numResults` 建議 5～10**

**Query 模板（照抄改代碼／名稱，跑 3～5 條）：**

| 市場 | 建議 query |
|:--|:--|
| **台股** | ① `{公司名稱} {代碼} 法人看法 目標價 分析 利多 利空`<br>② `PTT 股板 {代碼} {公司名稱} 討論 標的分析`<br>③ `{公司名稱} 最新季報 法說會 重點 營運展望` |
| **美股** | ① `{English Name} {TICKER} stock analysis bull bear case recent quarter`<br>② `{English Name} {TICKER} earnings call takeaways guidance risk`<br>③ `{TICKER} stock reddit seeking alpha investor discussion` |
| **港股／A 股** | ① `{公司名稱} {代碼} 港股 近期業績分析 投資人討論`<br>② `{公司名稱} 券商研報 目標價 評級 上調 下調`<br>③ `{公司名稱} 雪球 東方財富股吧 討論 分析` |
| **日股** | ① `{日本語社名} {コード} 株 業績 分析 掲示板`<br>② `{English Name} {code} Japan stock earnings analysis outlook` |

**搜完之後怎麼判斷：**

| 情況 | 動作 |
|:--|:--|
| Highlights 已含完整論點、數字、日期 | 照 **E-2** 完整照抄後存檔 |
| Highlights 只有片段，但這篇很關鍵 | 挑 3～5 個最好的 URL，**一次批次**丟給 `web_fetch_exa` 讀全文 → 取得全文才符合 E-2 |
| `web_fetch_exa` 回 WAF 亂碼（雪球等） | 照 **B-7** 換工具（雪球用 brightdata） |
| 全部結果都與公司無關 | 換 query 措辭再試 1 次；仍不行照 **E-8** 記錄 |
| Exa 完全搜不到 | 照 **E-1** 寫「已用 Exa 搜尋 N 條 query，過去三個月無符合內容」 |

**規則：**
- **只寫 Exa 實際回傳的內容**，Highlights 有多少寫多少，**不可自行補完**（鐵律 🚫2）
- URL 和日期**原樣照抄**，不可改寫
- `Published: N/A` → 從內文找日期；找不到標「日期不明」，**不可推測**
- 超過三個月的文章 → 丟掉（見 **E-7**）
- 每筆註明**原始網站**（如「來源網站：新浪財經」），讓後續分析分得出是券商研報還是散戶留言
- ⚠️ **與階段 1 重複的貼文** → 照 **E-6** 去重，不要寫兩次

**存檔範例：**

````markdown
## [Exa 語意搜尋]

- **抓取時間**：YYYY-MM-DD
- **抓取方式**：Exa MCP `web_search_exa`（＋ `web_fetch_exa` 讀取 3 篇全文）
- **使用的 query**：
  1. `福耀玻璃 3606 港股 近期業績分析 投資人討論`
  2. `福耀玻璃 券商研報 目標價 評級 上調 下調`
- **抓取結果**：✅ 成功（共 10 筆，去除與階段 1 重複 2 筆後留 6 筆）

### 🎯 高盛下調評級至「中性」，目標價降至 64 港元
- **來源網站**: 新浪財經
- **來源連結**: [https://finance.sina.com.cn/...](https://finance.sina.com.cn/...)
- **發布時間**: 2026-08-25
- **作者／ID**: 新浪財經（轉載高盛研報）
- **抓取方式**: web_search_exa Highlights ＋ web_fetch_exa 全文
- **完整原文**:
  > 高盛發布研報指出，福耀玻璃二季度營收及淨利潤遜於預期，原因為海外增長放緩及匯兌損失。
  > 下調今年每股盈測 6%，但上調 2027、2028 年預測 3% 及 6%……
  > （逐字照抄到文末）
- **關鍵要點**:
  - 下調 2026 EPS 預測 6%，上調 2027／2028 預測 3%／6%
  - 理由：全球汽車生產前景停滯、市場滲透率已高
- **利多／利空判定**: 利空（評級下調、目標價下修）
````

## E-5 【階段 2｜搜】yfinance 輿情

> yfinance 提供三種**免爬蟲**的輿情素材。全部照 **E-1** Append 進 `{yyyyMM}_輿情新聞.md`。

| 呼叫 | 拿到什麼 | 寫進哪個章節 |
|:--|:--|:--|
| `get_yahoo_finance_news` | 新聞標題／摘要／**真實 URL** | `## [Yahoo Finance News（yfinance MCP）]` |
| `get_recommendations`（`upgrades_downgrades`） | 券商評等調升／調降、目標價變動 | `## [分析師評等（yfinance MCP）]` |
| `get_recommendations`（`recommendations`） | 買賣建議分布（strongBuy/buy/hold/sell） | 同上 |
| `get_holder_info`（`insider_transactions`） | 內部人買賣紀錄 | `## [內部人交易（yfinance MCP）]` |
| `get_holder_info`（`institutional_holders`） | 法人持股結構 | 同上 |

**規則：**
- `months_back` 預設 12，本 Skill **只取近三個月**的升降評，其餘不寫入
- 新聞只回標題與摘要 → **想符合 E-2 完整敘述，把 URL 交給 `web_fetch_exa` 或 `firecrawl_scrape` 讀全文**；讀不到就標註「⚠️ 僅取得摘要」
- 標題沒提到該公司的新聞 → **直接排除**（見 **E-7** 第 2 條）
- **只寫 yfinance 實際回傳的內容**，不可自行補完
- 回空 → 照 **E-1** 寫「已查詢 yfinance，過去三個月無符合內容」

> ⚠️ **市場差異（實測）**：美股（如 `UHS`）一次可回 **10 則**含真實 URL 的相關新聞；非美股（如 `2881.TW`）常只回 **1 則**且可能與公司無關。
> → yfinance 新聞**對美股是主力，對台／港／日股只是補充**，非美股務必把 E-3 爬蟲與 E-4 Exa 做完整。

**存檔範例：**

````markdown
## [Yahoo Finance News（yfinance MCP）]

- **yfinance ticker**：UHS
- **抓取時間**：YYYY-MM-DD
- **抓取方式**：yfinance MCP `get_yahoo_finance_news`（＋ firecrawl_scrape 讀 3 篇全文）
- **抓取結果**：✅ 成功（10 則，其中 N 則屬近三個月且與公司直接相關）

### 🎯 [完整原標題]
- **來源網站**: Yahoo Finance
- **來源連結**: [URL](URL)
- **發布時間**: YYYY-MM-DD
- **作者／ID**: Reuters / 記者名
- **完整原文**:
  > （全文照抄；若只拿到 Summary 就照抄 Summary 並標註 ⚠️ 僅取得摘要）
- **利多／利空判定**: 利多 / 利空 / 中性

## [分析師評等（yfinance MCP）]

- **抓取方式**：yfinance MCP `get_recommendations`（`upgrades_downgrades`, months_back=3）
- **抓取結果**：✅ 成功

| 日期 | 券商 | 前評等 → 新評等 | 動作 |
|:--|:--|:--|:--|
````

## E-6 去重規則（階段 1 和階段 2 會抓到同一篇）

| 判斷 | 動作 |
|:--|:--|
| **URL 完全相同** | 只留一則。保留**內容較完整**的那則（通常是爬蟲版） |
| **URL 不同但同一篇文章**（轉載） | 留爬到全文的那則，另一則在「關鍵要點」註明「另見 {網站} 轉載：{URL}」 |
| **同事件不同報導** | **都留**，這是不同來源的觀點，不算重複 |

## E-7 過濾規則（決定哪些內容可以寫進檔案）

| # | 規則 | 判斷方式 |
|:--|:--|:--|
| 1 | **只留實質內容** | 有基本面分析、有事件報導 → 留。只有漲跌數字或表情符號 → 丟 |
| 2 | **標題必須提到該公司** | 標題沒提到這家公司 → 一律排除（非美股 yfinance 新聞常見雜訊） |
| 3 | **內容要具體且完整** | 照 **E-2** 保留完整原文，**不能只貼網址、不能只寫一行摘要** |
| 4 | **排除網站自我介紹** | 「本網提供即時財經新聞…」→ 不算有效紀錄 |
| 5 | **必須有真實來源佐證** | 爬取／搜尋結果裡沒有的，就不寫 |
| 6 | **只留近三個月** | 超過三個月丟掉；日期不明標「日期不明」並註記來源 |

## E-8 抓取失敗的標準寫法

某個站點所有工具都失敗時**必須**寫成這樣，**禁止用 AI 生成內容填充**：

````markdown
## [爬取｜東方財富股吧]

- **抓取時間**：YYYY-MM-DD
- **抓取結果**：❌ 失敗

### 抓取嘗試紀錄（階段 1 爬蟲）
- 已嘗試：firecrawl_scrape → 回傳 HTML 骨架，無貼文
- 已嘗試：brightdata scrape_as_markdown → 連線逾時
- 已嘗試：apify → 不支援此網域
- 已嘗試：playwright → 連線失敗
- 已嘗試：內建 WebFetch → HTTP 403
- **結論**：本站本次無法取得真實輿情，非 AI 生成。
- **後續處理**：已於階段 2 以 Exa query `{公司名稱} 東方財富股吧 討論 分析` 補搜，結果見 `## [Exa 語意搜尋]`。
````

## E-9 輿情完整度自檢（寫完 E-3～E-5 後，逐條檢查）

| # | 檢查項 | 不通過就 |
|:--|:--|:--|
| 1 | 檔案裡有**至少 1 個** `## [爬取｜…]` 章節（成功或失敗紀錄皆可） | 回去做 E-3 |
| 2 | 檔案裡有 `## [Exa 語意搜尋]` 章節 | 回去做 E-4 |
| 3 | 檔案裡有 yfinance 章節 | 回去做 E-5 |
| 4 | 每一則都有 **E-2-1 的 7 個欄位** | 補齊，補不到就標「未顯示」 |
| 5 | 每一則的「完整原文」**不是一行摘要** | 回去用爬蟲讀全文，或標註「⚠️ 僅取得摘要」 |
| 6 | 討論區來源有留言原文（或註明無留言） | 回去補抓留言 |
| 7 | 沒有任何一則是**憑印象寫的** | 刪掉，改寫成失敗紀錄 |

---

# F. 步驟 4 — Convert2md 轉換

步驟 2 完成後，**呼叫 `Convert2md` Skill**：

- 掃描資料夾中的 PDF/HTML → 轉為乾淨 Markdown
- 清除 XBRL/iXBRL 標籤與 SEC blob
- ⚠️ 字型缺字的 `(cid:N)` 亂碼**無法修復**，要在 **D-4** 下載階段就換英文版避開
- ✅ `{TICKER}_yfinance_{yyyyMMdd}.md` 和 `{yyyyMM}_輿情新聞.md` 已是 Markdown，**不需轉換**，Convert2md 會自動略過

---

# G. 步驟 5 — 執行報告 ＋ Push master

報告路徑：`FinancialReport/Log/CollectsentimentAndReports_Summary_{yyyyMMdd}.md`

> **報告寫完後，強制 `git push` 所有變更到 `master`，任務才算完成。**

````markdown
# 任務執行最終報告 - YYYY/MM/DD

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 檔案名稱 | 狀態 |
|:--|:--|:--|:--|
| `2881富邦金` | yfinance MCP | `2881_yfinance_20260827.md` | 財務數據成功 |
| `2881富邦金` | 財報狗 | `2881_AnnualReport_2024.pdf` | 下載成功 |
| `2881富邦金` | 爬取＋Exa＋yfinance | `202608_輿情新聞.md` | 輿情更新成功 |

## 2. 輿情兩階段執行結果（強制填寫，缺一階段視為未完成）

### 階段 1｜爬蟲直取
| 站點 | 使用工具 | 列表頁 | 內文篇數 | 留言則數 | 結果 |
|:--|:--|:--|--:|--:|:--|
| 股市爆料同學會 | CMoney API | ✅ | 12 | 87 | ✅ 成功 |
| PTT 股板 | firecrawl_scrape | ✅ | 4 | 43 | ✅ 成功 |
| 東方財富股吧 | firecrawl → brightdata → playwright | ❌ | 0 | 0 | ❌ 全鏈失敗（見輿情檔 E-8 紀錄） |

- **成功站點數**：N（要求 ≥ 3，未達成請說明原因）

### 階段 2｜Exa 語意搜尋
| 項目 | 內容 |
|:--|:--|
| 使用的 query | 逐條列出實際送出的 query |
| `web_search_exa` | ✅ 成功（共 N 筆，去重後留 M 筆） |
| `web_fetch_exa` | ✅ 讀取 N 篇全文 / ❌ 某站回 WAF 亂碼 |
| 涵蓋的來源網站 | 新浪財經、PTT、東方財富股吧… |
| 針對階段 1 失敗站點的補搜 | 列出哪些站改用 Exa 補、補到幾筆 |

### 階段 2｜yfinance MCP
| 項目 | 內容 |
|:--|:--|
| 使用 ticker | `2881.TW` |
| `get_stock_info` | ✅ 成功 |
| `income_stmt` / `balance_sheet` | ✅ 成功（年度資料 4 年 ⚠️ 不足 5 年） |
| `quarterly_income_stmt` | ✅ 成功（最近一季部分欄位為 null） |
| `get_yahoo_finance_news` | ✅ 1 則（非美股新聞量少，已補爬蟲與 Exa） |
| `get_recommendations` | ✅ / ❌ |
| 資料缺口 | 列出所有 N/A 欄位與原因 |

## 3. 輿情完整度統計（強制填寫）
| 指標 | 數值 |
|:--|--:|
| 總筆數 | N |
| 其中「完整全文」筆數 | N |
| 其中「僅摘要」筆數（須說明原因） | N |
| 抓到留言的討論串數 / 留言總則數 | N / N |
| E-9 自檢是否全部通過 | ✅ / ❌（未通過列出項目） |

## 4. 失敗或被擋的網站
- **來源**: [網站名稱](URL)
- **原因**: (Cloudflare 阻擋／WAF 亂碼／連線逾時／付費牆等)
- **已試過的工具**: firecrawl → brightdata → apify → playwright → 內建
- **是否已用搜尋補救**: ✅ / ❌

## 5. 資料缺失說明
- 說明為何某些財報或輿情找不到

## 6. 異常檔案刪除紀錄
- 哪些檔案因 <10KB、無公司名稱、或 `(cid:` 亂碼過多而被刪除

## 7. 本次使用的 MCP（強制填寫）
| MCP 名稱 | 工具 | 用途 |
|:--|:--|:--|
| Firecrawl | `firecrawl_scrape` | 爬取 PTT／股吧／格隆匯貼文與留言 |
| Bright Data | `scrape_as_markdown` | 爬取雪球（WAF 站） |
| Exa | `web_search_exa` | 語意搜尋輿情與券商研報 |
| Exa | `web_fetch_exa` | 讀取搜尋到的文章全文 |
| yfinance | `get_stock_info` | 取得 EPS／PE／ROE／流通股數 |
| yfinance | `get_financial_statement` | 取得年度與季度損益表、資產負債表 |
| yfinance | `get_yahoo_finance_news` | 取得該股新聞清單 |
| （若無使用） | — | 本次未使用 MCP，僅使用內建工具 |
````

**MCP 紀錄規則：**
- 用人類看得懂的名稱（`Exa`、`Firecrawl`、`Bright Data`），不要用 UUID
- 每筆要有：MCP 名稱、工具名、用途一句話
- 完全沒用 MCP 時寫明「未使用 MCP，僅使用內建工具」

**最後**：回到 **A-6 完成定義**逐條打勾，全部通過才回報完成。

---

# 附錄 I — 站點專用 SOP（只有遇到該站才需要讀）

## I-1 台股 CMoney 股市爆料同學會 API（2026-07-19 驗證）

> **不要爬網頁，直接打官方 API。** 實測一次抓 294 篇 ＋ 567 則留言 → **最符合 E-2 完整敘述要求的台股來源，階段 1 優先跑它。**
> 原因：`cmoney.tw/forum/stock/{代號}` 是 Nuxt SSR 殼，貼文列表是空的。前端會先拿訪客 token 再打 API，我們模仿同樣流程。

**步驟 1：拿訪客 token**

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
- ⚠️ **`skipCount`／`offset` 無效**（會一直回同一頁），務必用 `cursor` 並以 `id` 去重
- 可用型別：`AllLatest`（最新）、`AllHottest`（最熱）、`news`（新聞）
- 重點欄位：`id`、`content.text`（**這就是完整原文，照抄進 E-2 的「完整原文」欄**）、`createTime`（**毫秒** timestamp，要除以 1000）
- 文章網址：`https://www.cmoney.tw/forum/article/{id}`

**步驟 3：抓留言（本 Skill 視為必做，E-2-3 要求留言）**

```bash
curl -s "https://www.cmoney.tw/api/mach/api/Article/{文章id}/Comments?fetch=50&offset=0" \
  -H "Authorization: Bearer {access_token}" \
  -H "X-Version: 2.0"
```

- ⚠️ **留言 API 用 `X-Version: 2.0`**（用 3.0 會回 UnsupportedApiVersion）
- 參數是 `fetch` / `offset`（不是 `fetchCount`）
- 只對 `commentCount > 0` 的文章呼叫

**常見錯誤：**

| 症狀 | 修法 |
|:--|:--|
| 回 HTML 不是 JSON | 路徑錯 → 正確 base 是 `www.cmoney.tw/api/mach/api/...` |
| 400 `UnsupportedApiVersion` | 缺 `X-Version` 或版本錯（文章 3.0、留言 2.0） |
| 401 | 缺 Bearer token 或過期 → 回步驟 1 重拿 |
| 每頁內容都一樣 | 用了 `skipCount` → 改用 `cursor` |

- 美股端點：`.../api/Article/USStocks/{代號}/{型別}`（同一套 token）
- 呼叫間隔 0.3～0.5 秒

## I-2 格隆匯 gelonghui.com（2026-08-26 驗證）

> **用 `firecrawl_scrape`，basic proxy 即可，每頁 1 credit。**
> 港股／A 股／中概股輿情重要來源，Nuxt.js SSR 架構，**內建工具必定失敗，不要浪費時間試**。

| 步驟 | 動作 | 產出 | 成本 |
|:--:|:--|:--|:--|
| 1 | `firecrawl_scrape` → `https://www.gelonghui.com/search?keyword={公司名稱}` | 搜尋結果列表（實測福耀玻璃 257 篇），含標題／摘要／作者／時間／URL（`/p/{id}`）。第一頁約 18 篇，通常足夠涵蓋近三個月 | 1 credit |
| 2（可選） | `firecrawl_search` → `{公司名稱} {股票代碼} site:gelonghui.com` | 10 筆結果，含券商研報 PDF 連結 | 2 credits |
| 3 | `firecrawl_scrape` → `https://www.gelonghui.com/p/{文章id}` | 乾淨 Markdown 全文（**照抄進 E-2 完整原文欄**） | 1 credit/篇 |

- 工具順序：**firecrawl（首選）→ brightdata / apify / playwright → ❌ 內建工具（必定失敗）**
- 快訊（`/news/{id}`）和文章（`/p/{id}`）都可用 firecrawl 爬

## I-3 雪球 xueqiu.com（2026-08-27 更新）

> 港股、A 股輿情核心來源，但有 **WAF 加密防護**。

1. **跳過內建工具**，也**跳過 Exa `web_fetch_exa`**
   （2026-08-27 實測：Exa fetch `xueqiu.com/S/03606` 回傳 `{"_waf_...":"..."}` 加密亂碼，無正文）
2. 用 `brightdata scrape_as_markdown` 抓 `https://xueqiu.com/S/{代號}`（雪球用 brightdata 成功率最高）
3. brightdata 失敗 → 依序 `firecrawl` → `apify` → `playwright`
4. 頁面上的深度專欄連結 → 再用 brightdata 抓文章頁，取完整正文與評論（E-2-3 要求留言）
5. **只記錄真實存在於頁面上的貼文、連結、時間戳**
6. 整條鏈失敗 → 照 **E-8** 記錄，並於階段 2 用 Exa query `{公司名稱} 雪球 分析` 補搜

## I-4 Exa 實測成果與已知限制（2026-08-27）

**實測成果（可信賴的預期）：**

| 測試 query | 拿到什麼 |
|:--|:--|
| `福耀玻璃 3606 港股 近期業績分析 投資人討論` | 新浪財經券商研報全文（含毛利率、匯兌損失明細）、美銀／高盛升降評與目標價、東方財富股吧貼文、FX168 財報數字 |
| `Universal Health Services UHS stock analysis bull bear case recent quarter` | StockStory 完整研究報告、Wedbush 法說會摘要、多空論點、TrendMatrix 評分 |
| `reddit discussion 富邦金 2881 PTT 股票板 討論` | PTT 正文 ＋ 上百則推文（`pttweb.cc` / `ptt.cc`）→ PTT 爬不動時的最佳替代 |

**已知限制（必須誠實面對）：**

| 限制 | 處理方式 |
|:--|:--|
| **WAF 站爬不動**：`web_fetch_exa` 對雪球回 `_waf_` 亂碼 | 照 **I-3** 改用 brightdata |
| **Highlights 是片段**，不是完整全文 → 不符合 E-2 完整敘述 | 需要全文 → `web_fetch_exa` 或 `firecrawl_scrape` 讀該 URL |
| **部分結果 `Published: N/A`** | 內容裡有日期就用；都沒有標「日期不明」，**不可推測** |
| **語意搜尋不保證時效**，可能回舊文 | 照 **E-7** 第 6 條，只留近三個月 |

**呼叫節奏：**
- 不受 **B-5** 的 3 秒間隔限制（不是爬蟲）
- 同一間公司跑 **3～5 條**不同語系／不同角度的 query
- `web_fetch_exa` **一次帶多個 URL**，不要一個一個呼叫
- 抓完立刻存檔，不要留在記憶體

## I-5 yfinance 呼叫節奏

- 同一檔股票**一次抓齊**：`get_stock_info` + `income_stmt` + `balance_sheet` + `quarterly_income_stmt`
- 不需要 3 秒間隔（非爬蟲），但**不要對同一 ticker 重複呼叫同一工具**
- 回傳是大筆 JSON，**抓完立刻依 D-1 整理存檔**
- 其他可用工具：`get_historical_stock_prices`（輿情事件對照股價反應）、`get_option_expiration_dates` / `get_option_chain`（一般不需要）
