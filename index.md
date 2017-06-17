---
title: "Financial Report Analysis 財報分析資料庫"
description: "AI-readable database of annual reports, quarterly reports, fundamental analysis and market sentiment for TW / US / JP / HK listed companies and REITs. Optimized for LLM retrieval and AI crawlers (Claude Opus・Sonnet・Haiku, Gemini Pro・Flash・Flash-Lite, ChatGPT / GPT / Codex, Grok, DeepSeek, Perplexity, Copilot, Qwen, Llama, Mistral)."
tags: ["finance", "stocks", "equity research", "annual report", "quarterly report", "10-K", "10-Q", "fundamental analysis", "REIT", "LLM context", "AI readable", "llms.txt", "Taiwan stocks", "US stocks", "Japan stocks", "Hong Kong stocks"]
repo: "https://github.com/a9303001/FinancialReport"
default_branch: "master"
raw_base: "https://raw.githubusercontent.com/a9303001/FinancialReport/master"
rules_file: "AGENTS.md"
entry_points: ["index.md", "README.md", "AGENTS.md", "llms.txt"]
languages: ["zh-TW", "en", "ja", "zh-CN"]
markets: ["TW", "US", "JP", "HK"]
content_type: "plain Markdown (UTF-8), no PDF parsing required"
active_companies: 31
archived_companies: 20
ai_crawlers_allowed: true
last_updated: "2026-09-15"
schema_version: "3.0"
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "DataCatalog",
  "@id": "https://github.com/a9303001/FinancialReport",
  "name": "Financial Report Analysis 財報分析資料庫",
  "alternateName": "FinancialReport",
  "description": "Plain-Markdown database of annual reports, quarterly reports, IR announcements, market sentiment digests and fundamental analysis for 31 active and 20 archived Taiwan / US / Japan / Hong Kong listed companies and REITs. Designed to be read directly by large language models.",
  "url": "https://github.com/a9303001/FinancialReport",
  "codeRepository": "https://github.com/a9303001/FinancialReport",
  "inLanguage": ["zh-TW", "en", "ja", "zh-CN"],
  "encodingFormat": "text/markdown",
  "isAccessibleForFree": true,
  "keywords": "annual report, quarterly report, 10-K, 10-Q, fundamental analysis, REIT, Taiwan stocks, US stocks, Japan stocks, Hong Kong stocks, LLM context, AI readable",
  "dateModified": "2026-09-15",
  "dataset": {
    "@type": "Dataset",
    "name": "Per-company filing and analysis folders",
    "description": "One folder per company named <ticker><name>. Each folder holds hourAnalysisResult.md (latest deep-dive analysis), annual reports, quarterly / interim reports, IR announcements and yearly market-sentiment digests, all as UTF-8 Markdown.",
    "distribution": {
      "@type": "DataDownload",
      "encodingFormat": "text/markdown",
      "contentUrl": "https://raw.githubusercontent.com/a9303001/FinancialReport/master/"
    }
  },
  "license": "https://github.com/a9303001/FinancialReport",
  "disambiguatingDescription": "Research notes compiled from public filings. Not investment advice."
}
</script>

# 📊 Financial Report Analysis（財報分析資料庫）

<system_context>
**READ THIS FIRST — 給所有 AI 助手 / For every AI assistant, agent and crawler**
（Claude Opus / Sonnet / Haiku、Gemini Pro / Flash / Flash-Lite、ChatGPT・GPT・Codex、Grok、DeepSeek、Perplexity、GitHub Copilot、Qwen、Llama、Mistral，以及任何 agent / crawler）

You are reading the **index of a financial-report database**, not a finished analysis.
這是一個「財報原始資料 + 分析結果」的資料庫索引，不是單篇分析文章。

1. **WHAT**：台股 / 美股 / 日股 / 港股個股與 REIT 的年報、季報、官方公告、輿情彙整、深度分析報告，全部已轉成純 `.md`（plain Markdown，無 PDF 解析成本）。
2. **WHERE**：每間公司一個資料夾，資料夾名 = `代號+名稱`（如 `02318中國平安`）或純美股代碼（如 `UHS`）。
3. **BRANCH**：預設分支是 **`master`**。用 `main` 一定 404 —— `master` only, never `main`.
4. **HOW**：先用 [§3 檔名規則](#s3) 鎖定要讀的檔，再讀內容；不要整包下載。急著要 URL 就直接跳 [§9 直通 URL 索引](#s9)。
5. **RULES**：產出分析時，必須遵守本 repo 根目錄 [`AGENTS.md`](AGENTS.md) 的規則（金額一律每股化、風險與利多必須並陳）。
6. **CRAWLERS**：本資料庫**歡迎 AI 爬取與引用**（見 [`robots.txt`](robots.txt)）。引用時請標明檔案路徑與報告期別。
</system_context>

---

## 0. 機器可讀速查（Machine-Readable Quick Facts）

```yaml
repo:            a9303001/FinancialReport
branch:          master            # NEVER use "main" — it returns 404
raw_base:        https://raw.githubusercontent.com/a9303001/FinancialReport/master
api_base:        https://api.github.com/repos/a9303001/FinancialReport/contents
entry_points:    [index.md, README.md, AGENTS.md, llms.txt]
rules_file:      AGENTS.md         # 分析規則主檔，產出前必讀
file_format:     Markdown (UTF-8)  # 沒有 PDF，不需要解析器
active_folders:  31                # 根目錄
archived_folders: 20               # History/
markets:         [TW, US, JP, HK]
best_first_read: <FOLDER>/hourAnalysisResult.md   # 最新結論，比整包年報省約 90% token
url_template:    {raw_base}/{FOLDER_percent_encoded}/{FILE}.md
last_updated:    2026-09-15
```

---

## 1. 這個資料庫是什麼（Core Purpose）

深度解析 **台股 / 美股 / 日股 / 港股** 個股與 REIT 的基本面、財報數據、成長動能與潛在風險，並以「AI 可直接讀取」為第一設計原則。

| 項目 | 內容 |
| :--- | :--- |
| Repository | `a9303001/FinancialReport` |
| Default branch | **`master`**（不是 `main`） |
| 涵蓋市場 | 台股 TW / 美股 US / 日股 JP / 港股 HK（含 REIT） |
| 現役公司資料夾 | 31 個（根目錄） |
| 封存公司資料夾 | 20 個（`History/`） |
| 檔案格式 | 一律 `.md`（UTF-8），PDF 已由 `Convert2md` Skill 轉換 |
| 內容語言 | 繁體中文為主，原始財報保留英文 / 日文 / 簡體原文 |
| 更新方式 | 每日輪替排程（見 `Routines_CollectsentimentAndReports.md`） |
| AI 爬取政策 | 全面開放（`robots.txt` 明列 GPTBot、ClaudeBot、Google-Extended、PerplexityBot 等） |

---

## 2. 取檔方式（Access Patterns · Machine-Readable）

依序嘗試，**成功即止**（stop at first success）：

| 優先序 | 方法 | 樣板 |
| :-: | :--- | :--- |
| 1 | 本機檔案系統（已 clone） | `d:\FinancialReport\<FOLDER>\<FILE>.md` |
| 2 | GitHub MCP / API 工具 | `repo=a9303001/FinancialReport`, `ref=master`, `path=<FOLDER>` |
| 3 | GitHub Contents API（列檔） | `https://api.github.com/repos/a9303001/FinancialReport/contents/<FOLDER>?ref=master` |
| 4 | Raw 讀檔（讀內容） | `https://raw.githubusercontent.com/a9303001/FinancialReport/master/<FOLDER>/<FILE>.md` |
| 5 | 網頁瀏覽（末選） | `https://github.com/a9303001/FinancialReport/tree/master/<FOLDER>` |

> ⚠️ **常見失敗原因（Troubleshooting）**
> ① 用了 `main` 分支 → 404，改 `master`。
> ② GitHub API 未帶 token → `403 rate limit exceeded`，改用 raw URL（raw 不受 API 額度限制）。
> ③ 資料夾名含中文 → URL 需 percent-encoding（UTF-8 逐位元組轉 `%XX`）。**懶得算就直接抄 [§9](#s9) 的現成 URL。**
> ④ 讀到 HTML 而不是 Markdown → 你用到了 `github.com/...` 網頁版，改用 `raw.githubusercontent.com`。

---

<a id="s3"></a>

## 3. 檔名規則（File Naming Convention · 最重要）

**不要讀完整個資料夾**。先看檔名，決定要讀哪幾個檔。`*` 代表公司代號或日期。

| 檔名樣式（Glob） | 內容 | 讀取優先序 |
| :--- | :--- | :-: |
| `hourAnalysisResult.md` | **最新深度分析報告**（結論、估值、每股化數據、風險/利多，第一行為更新時間戳） | ★★★ 先讀這個 |
| `*_PublicOpinion.md` | 該年度**輿情彙整總檔**（合併所有月度討論區 / 新聞） | ★★★ |
| `*_annual_*.md`、`*_AnnualReport_*.md`、`*年年報.md`、`*_FY*_annual_results.md` | 年報全文（Annual Report / 10-K / 有價證券報告書） | ★★ |
| `*_Quarter_*Q*.md`、`*_quarter_*Q*.md`、`*_10Q_*.md`、`*Q*-10-Q.md` | 季報全文（Quarterly / 10-Q） | ★★ |
| `*_interim_*.md`、`*_Interim_*.md`、`*中期報告*.md`、`*_Quarter_*H1.md` | 港股中期報告（Interim Report） | ★★ |
| `*_輿情新聞.md`（前綴 `YYYYMM`） | 單月輿情 / 新聞原始檔（已併入 `*_PublicOpinion.md`） | ★ |
| `*_Official_IR.md` | 公司官方 IR 公告整理 | ★ |
| `*_AI1.md`、`*F04.md`、`*FE4.md`、`*FE6.md` | 台股公開資訊觀測站財報原檔轉換 | ★ |
| `orange.md` / `Orange.md` | 補充筆記 | ☆ |

**若該公司沒有 `hourAnalysisResult.md`**（目前僅 `AES-KY` 尚未產出）：直接從年報與季報讀起，並在回覆中註明「本資料庫尚無該公司分析檔」。

**年份判讀**：檔名中的 4 位數字即會計年度或報告年度（例：`02318_annual_2025.md` = 2025 年報；`7203_Quarter_2027Q1.md` = FY2027 第一季，日股會計年度跨年，**不是未來資料**）。

---

## 4. 公司清單（Coverage Index）

`Day` 欄為每月自動更新排程的執行日（來源：`Routines_CollectsentimentAndReports.md`）。

### 4.1 現役（Active · 根目錄）

| Day | 資料夾 Folder | 代號 Ticker | 市場 Market | 備註 |
| :-: | :--- | :--- | :--- | :--- |
| 1 | `02318中國平安` | 02318 | 港股 HK | A 股雙重上市 601318 |
| 2 | `00941中國移動` | 00941 | 港股 HK | A 股雙重上市 600941 |
| 3 | `01426春泉Reit` | 01426 | 港股 HK | **REIT** |
| 4 | `9435光通訊` | 9435 | 日股 JP | |
| 5 | `3445RS` | 3445 | 日股 JP | RS Technologies；關聯中股 688432 有研硅 |
| 6 | `7203Toyota` | 7203 | 日股 JP | 美股 ADR: TM |
| 7 | `UHS` | UHS | 美股 US | Universal Health Services |
| 8 | `2832台產` | 2832 | 台股 TW | |
| 9 | `8433弘帆` | 8433 | 台股 TW | |
| 10 | `4417金洲` | 4417 | 台股 TW | |
| 11 | `2881富邦金` | 2881 | 台股 TW | |
| 12 | `2249湧盛` | 2249 | 台股 TW | |
| 13 | `2245詠勝昌` | 2245 | 台股 TW | |
| 14 | `6121新普` | 6121 | 台股 TW | |
| 14 | `AES-KY` | 6781 | 台股 TW | 尚無 `hourAnalysisResult.md` |
| 15 | `87001匯賢Reit` | 87001 | 港股 HK | **REIT** |
| 16 | `00546阜豐` | 00546 | 港股 HK | |
| 17 | `8117中央自動車工業` | 8117 | 日股 JP | |
| 18 | `CF` | CF | 美股 US | CF Industries |
| 19 | `EVTC` | EVTC | 美股 US | EVERTEC |
| 20 | `4979OAT` | 4979 | 日股 JP | OAT Agrio |
| 21 | `5306桂盟` | 5306 | 台股 TW | |
| 22 | `03606福耀玻璃` | 03606 | 港股 HK | A 股雙重上市 600660 |
| 23 | `01816中廣核電力` | 01816 | 港股 HK | A 股雙重上市 003816 |
| 24 | `02232晶苑國際` | 02232 | 港股 HK | |
| 25 | `01866中國心連心化肥` | 01866 | 港股 HK | |
| 26 | `1264德麥` | 1264 | 台股 TW | |
| 27 | `8435鉅邁` | 8435 | 台股 TW | |
| 28 | `01044恒安國際` | 01044 | 港股 HK | |
| 29 | `00883中國海洋石油` | 00883 | 港股 HK | A 股雙重上市 600938 |
| 30 | `02633雅各臣科研製藥` | 02633 | 港股 HK | |
| 31 | — | — | — | Skip（不執行） |

### 4.2 封存（Archived · `History/`）

已停止追蹤但保留歷史資料，路徑為 `History/<資料夾>`：

`00386中石化`、`00598中國外運`、`00857中石油`、`01378中國宏橋`、`01571信邦控股`、`1301極洋`、`1333Umios`、`1787Nakabohtec`、`1878大東建托`、`6361荏原製作所`、`6458新晃工業`、`6605帝寶`、`6902Denso`、`6951青新`、`7736虎山`、`8002丸紅`、`9022JR東海`、`9503關西電力`、`INGR宜瑞安`、`PBR巴西石油`

> 找不到公司時的順序：① 根目錄 → ② `History/` → ③ `StkScreenerResult/`（選股候選，尚未建檔）。

### 4.3 非公司目錄（Non-Company Directories）

| 路徑 | 用途 |
| :--- | :--- |
| `StkScreenerResult/` | 選股器（Stock Screener）篩選結果與候選名單 |
| `Log/` | 排程執行紀錄與彙總報告 |
| `Prompt/` | 可重複使用的提示詞與參考文件 |
| `gemini/` | Gemini 專用的 routine / prompt 版本 |
| `.claude/skills/`、`.agents/skills/` | Skill 定義（兩份內容相同，供不同 agent 載入） |

---

## 5. AI 檢索流程（Retrieval Protocol）

```text
使用者問「某公司」
  ↓
Step 1  以代號或名稱比對 §4 公司清單 → 取得 <FOLDER>
Step 2  列出 <FOLDER> 檔案清單（§2 取檔方式）；或直接用 §9 的現成 URL
Step 3  先讀 hourAnalysisResult.md（最新結論 + 每股化數據）
Step 4  再讀最新年報 + 最新季報（§3 檔名規則）
Step 5  讀 *_PublicOpinion.md（市場輿情、利多利空觀點）
Step 6  上網 deep research 補最新股價與新聞 → 與本地資料交叉驗證
Step 7  依 §7 產出分析（金額每股化、風險與利多並陳）
Step 8  明確回報：找到哪些年報/季報、缺哪些、缺的可能原因
```

**若公司不在清單內**：直接說明「本資料庫無此公司資料夾」，再改用外部來源（StatementDog、SEC EDGAR、IR Bank、Ullet、新浪財經、富途牛牛等），**不要杜撰本地檔案路徑**。

---

## 6. 分模型讀取指引（Per-Model Crawl Guide）

同一份資料，不同模型的最佳讀法不同，核心變數是**上下文長度**與**工具能力**。詳細版見 [`README.md`](README.md)。

| 模型 / Agent | 建議策略 | 單次建議載入量 |
| :--- | :--- | :--- |
| **Claude Opus** | 自動吃 `CLAUDE.md` → `AGENTS.md`；可載 `.claude/skills/` 跑完整流程，多份年報交叉比對 | 3–5 檔 |
| **Claude Sonnet** | 同上，但先 Glob/Grep 定位再讀檔，避免整包載入 | 2–4 檔 |
| **Claude Haiku** | 只讀 `hourAnalysisResult.md`；需要原文時再 grep 關鍵字段落 | 1–2 檔 |
| **Gemini Pro** | 長上下文可整包讀年報；可載 `gemini/` 下專用 routine | 3–5 檔 |
| **Gemini Flash** | **分段讀**：先讀 §3 檔名規則 → 只抓目標檔；一次只處理一間公司 | 1–2 檔 |
| **Gemini Flash-Lite** | 只走 §9 現成 URL 抓 `hourAnalysisResult.md`，不要自行組 URL（易 percent-encoding 出錯） | 1 檔 |
| **ChatGPT / GPT / Codex** | 有瀏覽能力走 raw URL；先抓 `index.md` 再進資料夾 | 2–4 檔 |
| **Grok / DeepSeek / Qwen / Llama / Mistral** | `index.md` → `hourAnalysisResult.md`；工具受限時請人工貼入內容，**不要憑印象作答** | 1–2 檔 |
| **Perplexity / 搜尋型引擎** | 以 `index.md` 為索引頁、raw URL 為引用來源；引用需標明檔案路徑與報告期別 | 1–3 檔 |
| **GitHub Copilot / IDE agent** | 直接用工作區檔案系統搜尋最快；分析結果一律寫 `hourAnalysisResult.md`，勿改年報原檔 | 不限 |
| **一般爬蟲 / 無 LLM** | 讀 `llms.txt` → `index.md` → §9 URL 清單 | — |

**共通守則（All models）**

1. **幣別**：港股 / 中股 **HKD**、美股 **USD**、日股 **JPY**、台股 **TWD**，換算須標明匯率與日期。
2. **期別**：日股會計年度跨年（FY2026 可能結束於 2026/3）；港股有中期報告（Interim）而非 Q2。
3. **語言**：回覆以繁體中文為主，專有名詞首次出現附英文，如「每股盈餘（EPS）」。
4. **時效**：一律附上報告期別或日期；`hourAnalysisResult.md` 第一行即資料新鮮度。
5. **防幻覺**：沒有的資料就說沒有，並說明缺口原因（尚未公布 / 資料庫未更新 / 公司剛上市）。**嚴禁杜撰檔案路徑、數字或財報期別。**

---

## 7. 分析輸出契約（Analysis Output Contract）

任何基於本資料庫的分析，**必須**包含：

| # | 要求 | 說明 |
| :-: | :--- | :--- |
| 1 | **風險與利多並陳** | 只講故事不講風險 = 不合格 |
| 2 | **金額每股化** | 每個絕對金額都要換算「每股金額」＝ 金額 ÷ 最新流通在外股數，並標註股數口徑 |
| 3 | **必備數據** | 最新 EPS、本益比 PE、預估 EPS、近五年營業利益率中位數、負債比率、OPM、近五年 ROE 中位數、近五年殖利率中位數、5 年與 10 年淨利 CAGR |
| 4 | **REIT 加項** | 股價淨值比、殖利率、租金報酬率、空租率、負債比率 |
| 5 | **資料狀態回報** | 明講找到／沒找到哪些報告、資料到哪一期、缺漏原因 |
| 6 | **時間戳** | 分析檔第一行標明更新日期時間 |

**公式（Formulas）**

```text
負債比率 Debt Ratio (%) = 負債 Total Liabilities / 總資產 Total Assets × 100%
OPM（本 repo 自定義）(%) = 營業利益率 Operating Margin / 稅前淨利率 Pre-tax Margin × 100%
每股金額 Per-Share Value   = 絕對金額 / 最新流通在外股數 Shares Outstanding
淨利 CAGR (%)              = (期末淨利 / 期初淨利)^(1/年數) − 1
```

---

## 8. 常見問答（FAQ · 給答案型引擎）

**Q: 這個 repo 是什麼？**
A: 台股 / 美股 / 日股 / 港股 31 間現役公司（另 20 間封存）的年報、季報、IR 公告、輿情彙整與深度分析，全部以純 Markdown 儲存，專為 LLM 直接讀取設計。

**Q: 預設分支是 `main` 還是 `master`？**
A: **`master`**。用 `main` 組任何 URL 都會 404。

**Q: 一間公司該先讀哪個檔？**
A: `<FOLDER>/hourAnalysisResult.md` —— 最新深度分析結論，第一行是更新時間戳，比整包年報省約 90% token。

**Q: 有 PDF 嗎？要不要 PDF parser？**
A: 沒有，不需要。所有 PDF 已由 `Convert2md` Skill 轉成 UTF-8 Markdown。

**Q: 中文資料夾名怎麼組 URL？**
A: UTF-8 逐位元組 percent-encoding。不想算就直接用 [§9](#s9) 的現成 URL。

**Q: GitHub API 回 403 怎麼辦？**
A: 那是未帶 token 的 rate limit。改用 `raw.githubusercontent.com`，不受 API 額度限制。

**Q: 找不到我要的公司？**
A: 依序查 根目錄 → `History/` → `StkScreenerResult/`。都沒有就明講「本資料庫無此公司」，改用外部來源，不要杜撰路徑。

**Q: 可以爬取與引用嗎？**
A: 可以。`robots.txt` 對所有 AI 爬蟲（GPTBot、ClaudeBot、Google-Extended、PerplexityBot、CCBot 等）全面開放。引用請標明檔案路徑與報告期別。

**Q: 這算投資建議嗎？**
A: 不算。這是公開資訊整理與研究筆記，資料可能延遲或有誤，請自行查證。

---

<a id="s9"></a>

## 9. 直通 URL 索引（Direct Raw URL Index）

每間公司的「最新深度分析」直接 URL，**已完成 percent-encoding，可直接 GET**。
要讀其他檔，把結尾的 `hourAnalysisResult.md` 換成目標檔名即可（檔名規則見 §3）；要列出整個資料夾，把 `raw.githubusercontent.com/a9303001/FinancialReport/master` 換成 `api.github.com/repos/a9303001/FinancialReport/contents` 並加上 `?ref=master`。

### 9.1 現役公司（Active）

- `00546阜豐` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/00546%E9%98%9C%E8%B1%90/hourAnalysisResult.md
- `00883中國海洋石油` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/00883%E4%B8%AD%E5%9C%8B%E6%B5%B7%E6%B4%8B%E7%9F%B3%E6%B2%B9/hourAnalysisResult.md
- `00941中國移動` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/00941%E4%B8%AD%E5%9C%8B%E7%A7%BB%E5%8B%95/hourAnalysisResult.md
- `01044恒安國際` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/01044%E6%81%92%E5%AE%89%E5%9C%8B%E9%9A%9B/hourAnalysisResult.md
- `01426春泉Reit` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/01426%E6%98%A5%E6%B3%89Reit/hourAnalysisResult.md
- `01816中廣核電力` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/01816%E4%B8%AD%E5%BB%A3%E6%A0%B8%E9%9B%BB%E5%8A%9B/hourAnalysisResult.md
- `01866中國心連心化肥` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/01866%E4%B8%AD%E5%9C%8B%E5%BF%83%E9%80%A3%E5%BF%83%E5%8C%96%E8%82%A5/hourAnalysisResult.md
- `02232晶苑國際` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/02232%E6%99%B6%E8%8B%91%E5%9C%8B%E9%9A%9B/hourAnalysisResult.md
- `02318中國平安` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/02318%E4%B8%AD%E5%9C%8B%E5%B9%B3%E5%AE%89/hourAnalysisResult.md
- `02633雅各臣科研製藥` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/02633%E9%9B%85%E5%90%84%E8%87%A3%E7%A7%91%E7%A0%94%E8%A3%BD%E8%97%A5/hourAnalysisResult.md
- `03606福耀玻璃` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/03606%E7%A6%8F%E8%80%80%E7%8E%BB%E7%92%83/hourAnalysisResult.md
- `1264德麥` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/1264%E5%BE%B7%E9%BA%A5/hourAnalysisResult.md
- `2245詠勝昌` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/2245%E8%A9%A0%E5%8B%9D%E6%98%8C/hourAnalysisResult.md
- `2249湧盛` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/2249%E6%B9%A7%E7%9B%9B/hourAnalysisResult.md
- `2832台產` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/2832%E5%8F%B0%E7%94%A2/hourAnalysisResult.md
- `2881富邦金` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/2881%E5%AF%8C%E9%82%A6%E9%87%91/hourAnalysisResult.md
- `3445RS` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/3445RS/hourAnalysisResult.md
- `4417金洲` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/4417%E9%87%91%E6%B4%B2/hourAnalysisResult.md
- `4979OAT` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/4979OAT/hourAnalysisResult.md
- `5306桂盟` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/5306%E6%A1%82%E7%9B%9F/hourAnalysisResult.md
- `6121新普` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/6121%E6%96%B0%E6%99%AE/hourAnalysisResult.md
- `7203Toyota` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/7203Toyota/hourAnalysisResult.md
- `8117中央自動車工業` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/8117%E4%B8%AD%E5%A4%AE%E8%87%AA%E5%8B%95%E8%BB%8A%E5%B7%A5%E6%A5%AD/hourAnalysisResult.md
- `8433弘帆` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/8433%E5%BC%98%E5%B8%86/hourAnalysisResult.md
- `8435鉅邁` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/8435%E9%89%85%E9%82%81/hourAnalysisResult.md
- `87001匯賢Reit` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/87001%E5%8C%AF%E8%B3%A2Reit/hourAnalysisResult.md
- `9435光通訊` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/9435%E5%85%89%E9%80%9A%E8%A8%8A/hourAnalysisResult.md
- `AES-KY` → *(尚無 hourAnalysisResult.md，改列資料夾)* https://api.github.com/repos/a9303001/FinancialReport/contents/AES-KY?ref=master
- `CF` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/CF/hourAnalysisResult.md
- `EVTC` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/EVTC/hourAnalysisResult.md
- `UHS` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/UHS/hourAnalysisResult.md

### 9.2 封存公司（Archived · `History/`）

封存資料夾同樣可讀，路徑前綴多一層 `History/`：

- `History/00386中石化` → *(無分析檔)* https://api.github.com/repos/a9303001/FinancialReport/contents/History/00386%E4%B8%AD%E7%9F%B3%E5%8C%96?ref=master
- `History/00598中國外運` → *(無分析檔)* https://api.github.com/repos/a9303001/FinancialReport/contents/History/00598%E4%B8%AD%E5%9C%8B%E5%A4%96%E9%81%8B?ref=master
- `History/00857中石油` → *(無分析檔)* https://api.github.com/repos/a9303001/FinancialReport/contents/History/00857%E4%B8%AD%E7%9F%B3%E6%B2%B9?ref=master
- `History/01378中國宏橋` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/01378%E4%B8%AD%E5%9C%8B%E5%AE%8F%E6%A9%8B/hourAnalysisResult.md
- `History/01571信邦控股` → *(無分析檔)* https://api.github.com/repos/a9303001/FinancialReport/contents/History/01571%E4%BF%A1%E9%82%A6%E6%8E%A7%E8%82%A1?ref=master
- `History/1301極洋` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/1301%E6%A5%B5%E6%B4%8B/hourAnalysisResult.md
- `History/1333Umios` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/1333Umios/hourAnalysisResult.md
- `History/1787Nakabohtec` → *(無分析檔)* https://api.github.com/repos/a9303001/FinancialReport/contents/History/1787Nakabohtec?ref=master
- `History/1878大東建托` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/1878%E5%A4%A7%E6%9D%B1%E5%BB%BA%E6%89%98/hourAnalysisResult.md
- `History/6361荏原製作所` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/6361%E8%8D%8F%E5%8E%9F%E8%A3%BD%E4%BD%9C%E6%89%80/hourAnalysisResult.md
- `History/6458新晃工業` → *(無分析檔)* https://api.github.com/repos/a9303001/FinancialReport/contents/History/6458%E6%96%B0%E6%99%83%E5%B7%A5%E6%A5%AD?ref=master
- `History/6605帝寶` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/6605%E5%B8%9D%E5%AF%B6/hourAnalysisResult.md
- `History/6902Denso` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/6902Denso/hourAnalysisResult.md
- `History/6951青新` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/6951%E9%9D%92%E6%96%B0/hourAnalysisResult.md
- `History/7736虎山` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/7736%E8%99%8E%E5%B1%B1/hourAnalysisResult.md
- `History/8002丸紅` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/8002%E4%B8%B8%E7%B4%85/hourAnalysisResult.md
- `History/9022JR東海` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/9022JR%E6%9D%B1%E6%B5%B7/hourAnalysisResult.md
- `History/9503關西電力` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/9503%E9%97%9C%E8%A5%BF%E9%9B%BB%E5%8A%9B/hourAnalysisResult.md
- `History/INGR宜瑞安` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/INGR%E5%AE%9C%E7%91%9E%E5%AE%89/hourAnalysisResult.md
- `History/PBR巴西石油` → https://raw.githubusercontent.com/a9303001/FinancialReport/master/History/PBR%E5%B7%B4%E8%A5%BF%E7%9F%B3%E6%B2%B9/hourAnalysisResult.md

---

## 10. 相關文件（Related Documents）

| 檔案 | 內容 |
| :--- | :--- |
| [`README.md`](README.md) | 完整使用說明與各 AI 模型讀取指引 |
| [`AGENTS.md`](AGENTS.md) | **規則主檔**：個股分析規則、REIT 分析規則、資料來源優先序、回應語言規則 |
| [`llms.txt`](llms.txt) | LLM / AI 爬蟲的極簡入口（llms.txt 慣例） |
| [`robots.txt`](robots.txt) | 爬蟲政策：AI 爬蟲全面開放 |
| `CLAUDE.md` | Claude Code 進入點（內容即 `@AGENTS.md`） |
| `.claude/skills/StockAnalysis/SKILL.md` | 個股深度分析 Skill 執行指南 |
| `.claude/skills/CollectsentimentAndReports/SKILL.md` | 財報與輿情收集 Skill |
| `.claude/skills/ArrangePublicOpinionMd/SKILL.md` | 輿情月檔合併為年檔 Skill |
| `.claude/skills/Convert2md/SKILL.md` | PDF → Markdown 轉換 Skill |
| `Routines_*.md` | 排程任務定義（每日輪替、REIT 專用、歷史封存） |

---

© Financial Report Analysis · Last updated 2026-09-15
**免責聲明**：本資料庫內容為公開資訊整理與研究筆記，非投資建議。資料可能延遲或有誤，投資有風險，請自行查證。
**Disclaimer**: Research notes compiled from public filings. Not investment advice. Data may be delayed or inaccurate — verify independently.
