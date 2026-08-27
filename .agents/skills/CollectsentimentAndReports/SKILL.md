---
name: CollectsentimentAndReports
description: 收集個股的「最新財報」與「輿情討論/新聞」，存成 Markdown 並 push 到 master。優先用 yfinance MCP 抓結構化財務數據、用 Exa MCP 做語意搜尋，抓不到才用爬蟲。使用者提到收集財報、收集輿情、collect sentiment、抓某檔股票資料時觸發。
---

# CollectsentimentAndReports

> **這是操作手冊，不是參考資料。照著 A 段做，卡住才翻後面。**
> 讀完 A 段（約 60 行）就可以開始執行，不必讀完整份。

---

# A. 一頁執行卡

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
| **2** | yfinance 抓財務數據 → 存檔<br>Exa 找財報網址 → 下載 PDF | `{代碼}_yfinance_{yyyyMMdd}.md`<br>`{代碼}_AnnualReport_{年}.pdf` | D |
| **3** | Exa 搜輿情 → yfinance 新聞 → 在地討論區 | `{yyyyMM}_輿情新聞.md` | E |
| **4** | 呼叫 `Convert2md` skill 把 PDF 轉 Markdown | `*.md` | F |
| **5** | 寫執行報告 → `git push` 到 `master` | `Log/CollectsentimentAndReports_Summary_{yyyyMMdd}.md` | G |

## A-4 三個核心觀念（記住這三個就不會出大錯）

1. **先用 API，再用爬蟲。**
   `yfinance` 和 `Exa` 是 API，不會被 Cloudflare 擋。**每個步驟都先跑它們**，不夠才動用爬蟲。
2. **抓到就馬上存檔。**
   不要累積在記憶體等最後一次寫。抓完一個來源 → 立刻寫檔 → 再抓下一個。
3. **抓不到就誠實寫「抓不到」。**
   絕對不可以用自己的知識編內容、編網址、編日期。寫失敗紀錄（**E-6**）比編一段假討論好一萬倍。

## A-5 鐵律（違反＝任務失敗）

| # | 鐵律 | 白話 |
|:--|:--|:--|
| 🚫1 | **不從 `a9303001/FinancialReport` 收集資料** | 這個 repo 是**輸出目的地**，不是資料來源。不從這裡下載財報、抓新聞、讀輿情。 |
| 🚫2 | **不捏造任何內容** | 不寫模擬討論、不編 URL／日期／用戶 ID。爬失敗就記錄失敗，**不可以用訓練知識填空**。 |
| 🚫3 | **不訪問 `macrotrends.net`** | 該站長期封鎖爬蟲，純浪費時間。 |
| 🚫4 | **`null` 一律寫 `N/A`** | 不准用推估值或其他年度的數字補。 |
| ✅5 | **即時存檔** | 每抓完一份財報、每爬完一個網站，立刻存檔。 |
| ✅6 | **API 優先** | 步驟 2、3 都先跑 yfinance 和 Exa。 |
| ✅7 | **抓不到就換工具** | 依 **B-2** 的順序換，不要卡在同一個工具重試。 |

## A-6 完成定義（Definition of Done）

以下全部做到才算完成，缺一項就還沒完成：

- [ ] `{代碼}_yfinance_{yyyyMMdd}.md` 存在（或報告裡寫明為何沒有）
- [ ] `{yyyyMM}_輿情新聞.md` 存在，且**同時有 Exa 章節和 yfinance 章節**
- [ ] 每一筆輿情都有**真實 URL** 和**真實日期**
- [ ] 所有 `null` 都寫成 `N/A`
- [ ] 執行報告已寫入 `Log/`
- [ ] 已 `git push` 到 `master`

---

# B. 工具與抓取策略

## B-1 工具對照表（Claude / Gemini 通用）

> 本文件用「**動作**」描述。看到工具名，用你手上同類的工具做就好。

| 動作 | Claude | Gemini／其他 |
|:--|:--|:--|
| **語意搜尋（首選）** | Exa MCP `web_search_exa` | 同（已連接的 Exa MCP） |
| **讀網頁（Exa 版）** | Exa MCP `web_fetch_exa` | 同 |
| **結構化財務數據** | yfinance MCP `mcp__yfinance__*` | 同（已連接的 yfinance MCP） |
| 一般網路搜尋 | `WebSearch` | `search_web` / `google_search` |
| 一般抓網頁 | `WebFetch` | `read_url` / `read_url_content` |
| 爬蟲 MCP | `firecrawl_scrape`、`scrape_as_markdown` | 同 |
| 讀寫檔案 | `Read` / `Write` / `Edit` | `view_file` / `write_file` / `edit_file` |
| 執行指令 | `Bash` | `run_shell_command` |

**三類工具的差別（決定先用誰）：**

| 類型 | 代表 | 特性 | 何時用 |
|:--|:--|:--|:--|
| **資料型 API** | `yfinance` | 直接回結構化 JSON，不受封鎖 | 抓財務數字 → **第 1 個跑** |
| **搜尋型 API** | `Exa` | 語意搜尋，**結果直接附正文摘錄** | 找輿情／找報告網址 → **第 2 個跑** |
| **爬蟲** | `firecrawl` / `brightdata` / `apify` / `playwright` | 實際去爬網址，會被 WAF 擋 | 前兩者不夠 → **最後才跑** |

## B-2 抓不到怎麼辦：固定換手順序

```
【第 0 層】先搜，不要急著爬
  Exa web_search_exa ──夠用──→ ✅ 直接記錄（多數情況到這裡就結束）
        │不夠（需要全文）
        ↓
【第 1 層】爬蟲鏈：固定順序，一個失敗換下一個
  ① 內建工具（WebFetch / read_url）
  ② Exa web_fetch_exa
  ③ firecrawl_scrape
  ④ brightdata scrape_as_markdown
  ⑤ apify
  ⑥ playwright
        │全部失敗
        ↓
  ❌ 放棄 → 照 E-6 誠實寫失敗紀錄
```

| 規則 | 內容 |
|:--|:--|
| **先搜再爬** | 動用爬蟲鏈前**一定先跑 `web_search_exa`**，它的結果本身就含正文摘錄。 |
| **順序不可跳** | 除非環境沒連上該 MCP，才可跳過並在報告註明。 |
| **每個工具最多試 2 次** | 失敗就換下一個，**禁止無限重試**。 |
| **「明確拒絕」也算失敗** | 例如 Firecrawl 回 `we do not support this site` → 立刻換下一個。 |
| **整條鏈都不行** | 改用各 MCP 的搜尋功能（`firecrawl_search`、`search_engine`）搜該站內容。 |
| **WebSearch 摘要是最後手段** | 必須標註「⚠️ 全部抓取失敗，以下為 WebSearch 摘要」。 |

## B-3 什麼叫「抓取失敗」（符合任一項就換工具）

- **空白／只有骨架**：回傳空白、只有選單導覽、沒有正文
- **被封鎖**：`not accessible to our user agent`、`domain not accessible`、HTTP 400
- **防護頁**：Cloudflare `Just a moment...`、HTTP 403 / 429
- **WAF 亂碼**：一長串 Base64 亂碼，或 `_waf_` 開頭的 JSON（雪球典型症狀）

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
| 單站上限 | 同一網域最多爬 **5 頁** |

## B-6 呼叫次數預算（防止卡在同一件事上）

| 階段 | 建議上限 | 超過就 |
|:--|:--|:--|
| yfinance（步驟 2） | 6 次呼叫 | 有拿到 `get_stock_info` 就先存檔往下走 |
| Exa 搜尋（步驟 2＋3） | 2～4 條 query | 換下一個來源 |
| 單一網站爬取 | 6 次工具呼叫（鏈上 6 棒） | 照 E-6 記錄失敗 |
| 單一公司總計 | 約 40 次工具呼叫 | 存好現有成果，在報告寫明未完成項目 |

## B-7 難爬網站查表（查表決定用哪個工具，別瞎試）

| 網站 | 網域 | 症狀 | **建議工具** |
|:--|:--|:--|:--|
| PTT 股板 | `ptt.cc` / `pttweb.cc` | — | ✅ **Exa 搜尋直接回全文＋推文**，效果最好 |
| 東方財富股吧 | `guba.eastmoney.com` | JS 分頁載入 | ✅ **Exa 搜尋**取貼文摘要；要全文再走爬蟲鏈 |
| 雪球 | `xueqiu.com` | **WAF 加密**，Exa fetch 拿到亂碼 | ⚠️ 不要用 Exa fetch → 用 `brightdata`（附錄 I-3） |
| 股市爆料同學會 | `cmoney.tw` | Nuxt SSR 殼，貼文為空 | ✅ **直接打官方 API**（附錄 I-1） |
| 格隆匯 | `gelonghui.com` | Nuxt.js SSR | ✅ `firecrawl_scrape`（附錄 I-2） |
| 新浪財經 | `finance.sina.com.cn` | — | ✅ **Exa 搜尋**可直接取得券商研報全文摘錄 |
| MOPS 台股查詢 | `mops.twse.com.tw` | 需 JS 互動／POST | `playwright` 或直接組 POST |
| moomoo 社區 | `moomoo.com` | JS 載入正文 | 爬蟲鏈 |
| Reddit | `reddit.com` | 封鎖爬蟲，Firecrawl 也拒絕 | Exa 搜尋 → brightdata / apify → `firecrawl_search` |
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
4. **立刻存檔**（鐵律 ✅5）

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

# E. 步驟 3 — 輿情與新聞收集

**範圍：過去三個月內。** 逐個來源抓，每抓完一個就立刻 Append 存檔。

**執行順序（不可顛倒）：**
```
E-2 Exa 語意搜尋（主力）→ E-3 yfinance 新聞／評等 → E-4 在地討論區補漏
```

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

**標準存檔範本：**

````markdown
# [{代碼} {公司名稱}] 輿情與新聞整理 ({YYYY}/{MM})

- **分析月份**：YYYY/MM
- **資料範圍**：過去三個月
- **最後更新**：YYYY-MM-DD HH:MM

---

## [來源名稱，例如 雪球 Xueqiu]

- **抓取時間**：YYYY-MM-DD
- **抓取方式**：brightdata scrape_as_markdown（或 Exa web_search_exa 等）
- **抓取結果**：✅ 成功 / ❌ 失敗

### 🎯 [主題]
- **來源連結**: [URL](URL) ← 必須是真實 URL
- **發布時間**: YYYY-MM-DD ← 必須是真實時間
- **核心觀點**:
  > "引述原文..." ← 必須是真實抓到的原文
- **關鍵要點**:
  - 重點 A
  - 重點 B
- **利多／利空判定**: 利多 / 利空 / 中性
````

## E-2 第一步：Exa 語意搜尋（主力）

> Exa 一次搜尋就能同時拿到「法人觀點 ＋ 散戶輿情 ＋ 財務數字」，免爬蟲、不被擋。
> **先把 Exa 跑完，再決定還缺哪些在地來源要爬。**

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
- **`numResults` 建議 5～10**：太多塞爆 context，太少涵蓋不足

**Query 模板（照抄改代碼／名稱，跑 2～4 條）：**

| 市場 | 建議 query |
|:--|:--|
| **台股** | ① `{公司名稱} {代碼} 法人看法 目標價 分析 利多 利空`<br>② `PTT 股板 {代碼} {公司名稱} 討論 標的分析`<br>③ `{公司名稱} 最新季報 法說會 重點 營運展望` |
| **美股** | ① `{English Name} {TICKER} stock analysis bull bear case recent quarter`<br>② `{English Name} {TICKER} earnings call takeaways guidance risk`<br>③ `{TICKER} stock reddit seeking alpha investor discussion` |
| **港股／A 股** | ① `{公司名稱} {代碼} 港股 近期業績分析 投資人討論`<br>② `{公司名稱} 券商研報 目標價 評級 上調 下調`<br>③ `{公司名稱} 雪球 東方財富股吧 討論 分析` |
| **日股** | ① `{日本語社名} {コード} 株 業績 分析 掲示板`<br>② `{English Name} {code} Japan stock earnings analysis outlook` |

**搜完之後怎麼判斷：**

| 情況 | 動作 |
|:--|:--|
| Highlights 已含完整論點、數字、日期 | ✅ 直接照 **E-1** 存檔，**不用再爬** |
| Highlights 只有片段，但這篇很關鍵 | 挑 3～5 個最好的 URL，**一次批次**丟給 `web_fetch_exa` 讀全文 |
| `web_fetch_exa` 回 WAF 亂碼（雪球等） | 照 **B-7** 換工具（雪球用 brightdata） |
| 全部結果都與公司無關 | 換 query 措辭再試 1 次；仍不行照 **E-6** 記錄 |
| Exa 完全搜不到 | 照 **E-1** 寫「已用 Exa 搜尋 N 條 query，過去三個月無符合內容」。**不需要**跑爬蟲鏈（Exa 不是爬蟲，換爬蟲工具無意義） |

**規則：**
- **只寫 Exa 實際回傳的內容**，Highlights 有多少寫多少，**不可自行補完**（鐵律 🚫2）
- URL 和日期**原樣照抄**，不可改寫
- `Published: N/A` → 從內文找日期；找不到標「日期不明」，**不可推測**
- 超過三個月的文章 → 丟掉（見 **E-5**）
- 存檔章節名用 `## [Exa 語意搜尋]`，每筆註明**原始網站**（如「來源網站：新浪財經」），讓後續分析分得出是券商研報還是散戶留言

**存檔範例：**

````markdown
## [Exa 語意搜尋]

- **抓取時間**：YYYY-MM-DD
- **抓取方式**：Exa MCP `web_search_exa`
- **使用的 query**：
  1. `福耀玻璃 3606 港股 近期業績分析 投資人討論`
  2. `福耀玻璃 券商研報 目標價 評級 上調 下調`
- **抓取結果**：✅ 成功（共 10 筆，篩選後留 6 筆屬近三個月且與公司直接相關）

### 🎯 高盛下調評級至「中性」，目標價降至 64 港元
- **來源網站**: 新浪財經
- **來源連結**: [https://finance.sina.com.cn/...](https://finance.sina.com.cn/...)
- **發布時間**: 2026-08-25
- **核心觀點**:
  > "二季度營收及淨利潤遜於預期，原因為海外增長放緩及匯兌損失。下調今年每股盈測 6%…"
- **關鍵要點**:
  - 下調 2026 EPS 預測 6%，但上調 2027／2028 預測 3%／6%
  - 理由：全球汽車生產前景停滯、市場滲透率已高
- **利多／利空判定**: 利空（評級下調）
````

## E-3 第二步：yfinance 輿情

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
- 新聞只回標題與摘要 → 要全文時把 URL 交給 `web_fetch_exa`
- 標題沒提到該公司的新聞 → **直接排除**（見 **E-5** 第 2 條）
- **只寫 yfinance 實際回傳的內容**，摘要不足就寫摘要，不可自行補完
- 回空 → 照 **E-1** 寫「已查詢 yfinance，過去三個月無符合內容」，**不需要**跑爬蟲鏈

> ⚠️ **市場差異（實測）**：美股（如 `UHS`）一次可回 **10 則**含真實 URL 的相關新聞；非美股（如 `2881.TW`）常只回 **1 則**且可能與公司無關。
> → yfinance 新聞**對美股是主力，對台／港／日股只是補充**，非美股務必完整跑 E-2 Exa 與 E-4 在地來源。

**存檔範例：**

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
|:--|:--|:--|:--|
````

## E-4 第三步：在地來源補漏

> 標 ⚠️ 者為難爬網站，先查 **B-7** 決定工具。

| 市場 | 在地來源 |
|:--|:--|
| **台股** | 鉅亨網、MoneyDJ、經濟日報、PTT 股板（✅ Exa 搜尋最好用）、Dcard 理財、股市爆料同學會（✅ 直接打 API，附錄 I-1）、財報狗社群 |
| **美股** | Yahoo Finance（✅ yfinance 新聞量最豐富）、Seeking Alpha、StockStory、X、Bloomberg（⚠️ 付費牆）、Reuters（⚠️ 封鎖）、Reddit（⚠️ 封鎖）、格隆匯（⚠️ 附錄 I-2） |
| **港股／A 股** | 新浪財經（✅ Exa 可取券商研報全文）、雪球（⚠️ 附錄 I-3）、東方財富股吧（⚠️ 用 Exa 搜）、格隆匯（⚠️ 附錄 I-2）、moomoo（⚠️ JS）、香港經濟日報、LIHKG |
| **日股** | 日經新聞、Yahoo Finance JP 掲示板、minkabu.jp、kabutan.jp、note、5ch、X |

## E-5 過濾規則（決定哪些內容可以寫進檔案）

| # | 規則 | 判斷方式 |
|:--|:--|:--|
| 1 | **只留實質內容** | 有基本面分析、有事件報導 → 留。只有漲跌數字或表情符號 → 丟 |
| 2 | **標題必須提到該公司** | 標題沒提到這家公司 → 一律排除（非美股 yfinance 新聞常見雜訊） |
| 3 | **內容要具體** | 記錄核心論點與細節，**不能只貼網址** |
| 4 | **排除網站自我介紹** | 「本網提供即時財經新聞…」→ 不算有效紀錄 |
| 5 | **必須有真實來源佐證** | 爬取／搜尋結果裡沒有的，就不寫 |
| 6 | **只留近三個月** | 超過三個月丟掉；日期不明標「日期不明」並註記來源 |

## E-6 抓取失敗的標準寫法

全部工具都失敗時**必須**寫成這樣，**禁止用 AI 生成內容填充**：

````markdown
## [東方財富股吧]

- **抓取時間**：YYYY-MM-DD
- **抓取結果**：❌ 失敗

### 搜尋嘗試紀錄
- 已嘗試：Exa web_search_exa → 回傳結果與本公司無關
- 已嘗試：內建工具 read_url_content → 回傳 HTML 骨架
- 已嘗試：Exa web_fetch_exa → 回傳 WAF 亂碼
- 已嘗試：firecrawl_scrape → 只取得基本資料
- 已嘗試：brightdata → 連線逾時
- 已嘗試：apify → 不支援此網域
- 已嘗試：playwright → 連線失敗
- **結論**：本次無法取得真實輿情，非 AI 生成。
````

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
| `2881富邦金` | Exa、yfinance、PTT、雪球 | `202608_輿情新聞.md` | 輿情更新成功 |

## 2. 免爬蟲工具抓取結果（強制填寫）

### Exa MCP
| 項目 | 內容 |
|:--|:--|
| 使用的 query | 逐條列出實際送出的 query |
| `web_search_exa` | ✅ 成功（共 N 筆，篩選後留 M 筆） |
| `web_fetch_exa` | ✅ 讀取 N 篇全文 / ❌ 某站回 WAF 亂碼 |
| 涵蓋的來源網站 | 新浪財經、PTT、東方財富股吧… |

### yfinance MCP
| 項目 | 內容 |
|:--|:--|
| 使用 ticker | `2881.TW` |
| `get_stock_info` | ✅ 成功 |
| `income_stmt` / `balance_sheet` | ✅ 成功（年度資料 4 年 ⚠️ 不足 5 年） |
| `quarterly_income_stmt` | ✅ 成功（最近一季部分欄位為 null） |
| `get_yahoo_finance_news` | ✅ 1 則（非美股新聞量少，已補 Exa 與在地來源） |
| `get_recommendations` | ✅ / ❌ |
| 資料缺口 | 列出所有 N/A 欄位與原因 |

## 3. 失敗或被擋的網站
- **來源**: [網站名稱](URL)
- **原因**: (Cloudflare 阻擋／WAF 亂碼／連線逾時／付費牆等)
- **已試過的工具**: Exa → 內建 → firecrawl → brightdata → apify → playwright

## 4. 資料缺失說明
- 說明為何某些財報或輿情找不到

## 5. 異常檔案刪除紀錄
- 哪些檔案因 <10KB、無公司名稱、或 `(cid:` 亂碼過多而被刪除

## 6. 本次使用的 MCP（強制填寫）
| MCP 名稱 | 工具 | 用途 |
|:--|:--|:--|
| Exa | `web_search_exa` | 語意搜尋輿情與券商研報 |
| Exa | `web_fetch_exa` | 讀取搜尋到的文章全文 |
| yfinance | `get_stock_info` | 取得 EPS／PE／ROE／流通股數 |
| yfinance | `get_financial_statement` | 取得年度與季度損益表、資產負債表 |
| yfinance | `get_yahoo_finance_news` | 取得該股新聞清單 |
| Firecrawl | `firecrawl_scrape` | 抓格隆匯文章 |
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

> **不要爬網頁，直接打官方 API。** 實測一次抓 294 篇 ＋ 567 則留言。
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
- 重點欄位：`id`、`content.text`、`createTime`（**毫秒** timestamp，要除以 1000）
- 文章網址：`https://www.cmoney.tw/forum/article/{id}`

**步驟 3：抓留言（選擇性）**

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
| 3 | `firecrawl_scrape` → `https://www.gelonghui.com/p/{文章id}` | 乾淨 Markdown 全文 | 1 credit/篇 |

- 工具順序：**firecrawl（首選）→ brightdata / apify / playwright → ❌ 內建工具（必定失敗）**
- 快訊（`/news/{id}`）和文章（`/p/{id}`）都可用 firecrawl 爬

## I-3 雪球 xueqiu.com（2026-08-27 更新）

> 港股、A 股輿情核心來源，但有 **WAF 加密防護**。

1. **跳過內建工具**，也**跳過 Exa `web_fetch_exa`**
   （2026-08-27 實測：Exa fetch `xueqiu.com/S/03606` 回傳 `{"_waf_...":"..."}` 加密亂碼，無正文）
2. 用 `brightdata scrape_as_markdown` 抓 `https://xueqiu.com/S/{代號}`（雪球用 brightdata 成功率最高）
3. brightdata 失敗 → 依序 `firecrawl` → `apify` → `playwright`
4. 頁面上的深度專欄連結 → 可再用 brightdata 抓文章頁補充
5. **只記錄真實存在於頁面上的貼文、連結、時間戳**

> 💡 替代方案：先用 `web_search_exa` 搜「{公司名稱} 雪球 分析」，Exa 結果可能已含雪球文章摘錄，就不用硬爬。

## I-4 Exa 實測成果與已知限制（2026-08-27）

**實測成果（可信賴的預期）：**

| 測試 query | 拿到什麼 |
|:--|:--|
| `福耀玻璃 3606 港股 近期業績分析 投資人討論` | 新浪財經券商研報全文（含毛利率、匯兌損失明細）、美銀／高盛升降評與目標價、東方財富股吧貼文、FX168 財報數字 → **一次搜尋湊齊「法人觀點＋散戶輿情＋財務數字」** |
| `Universal Health Services UHS stock analysis bull bear case recent quarter` | StockStory 完整研究報告、Wedbush 法說會摘要、多空論點、TrendMatrix 評分 |
| `reddit discussion 富邦金 2881 PTT 股票板 討論` | **PTT 完整正文 ＋ 上百則推文**（`pttweb.cc` / `ptt.cc`）→ PTT 用 Exa 搜比爬還好用 |

**已知限制（必須誠實面對）：**

| 限制 | 處理方式 |
|:--|:--|
| **WAF 站爬不動**：`web_fetch_exa` 對雪球回 `_waf_` 亂碼 | 照 **I-3** 改用 brightdata |
| **Highlights 是片段**，不是完整全文 | 需要全文 → `web_fetch_exa` 讀該 URL |
| **部分結果 `Published: N/A`** | 內容裡有日期就用；都沒有標「日期不明」，**不可推測** |
| **語意搜尋不保證時效**，可能回舊文 | 照 **E-5** 第 6 條，只留近三個月 |

**呼叫節奏：**
- 不受 **B-5** 的 3 秒間隔限制（不是爬蟲）
- 同一間公司跑 **2～4 條**不同語系／不同角度的 query
- `web_fetch_exa` **一次帶多個 URL**，不要一個一個呼叫
- 抓完立刻存檔，不要留在記憶體

## I-5 yfinance 呼叫節奏

- 同一檔股票**一次抓齊**：`get_stock_info` + `income_stmt` + `balance_sheet` + `quarterly_income_stmt`
- 不需要 3 秒間隔（非爬蟲），但**不要對同一 ticker 重複呼叫同一工具**
- 回傳是大筆 JSON，**抓完立刻依 D-1 整理存檔**
- 其他可用工具：`get_historical_stock_prices`（輿情事件對照股價反應）、`get_option_expiration_dates` / `get_option_chain`（一般不需要）
