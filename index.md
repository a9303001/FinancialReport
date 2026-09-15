---
title: "Financial Report Analysis 財報分析資料庫"
description: "AI-readable database of annual reports, quarterly reports, fundamental analysis and market sentiment for TW / US / JP / HK listed companies. Optimized for LLM retrieval (Claude Opus・Sonnet・Haiku, Gemini Pro・Flash, ChatGPT / GPT, Grok, DeepSeek, Perplexity, Copilot)."
tags: ["finance", "stocks", "annual report", "quarterly report", "fundamental analysis", "REIT", "LLM context", "AI readable", "Taiwan stocks", "US stocks", "Japan stocks", "Hong Kong stocks"]
repo: "https://github.com/a9303001/FinancialReport"
default_branch: "master"
languages: ["zh-TW", "en", "ja", "zh-CN"]
markets: ["TW", "US", "JP", "HK"]
schema_version: "2.0"
---

# 📊 Financial Report Analysis（財報分析資料庫）

<system_context>
**READ THIS FIRST — 給所有 AI 助手 / For every AI assistant**
（Claude Opus / Sonnet / Haiku、Gemini Pro / Flash / Flash-Lite、ChatGPT・GPT・Codex、Grok、DeepSeek、Perplexity、GitHub Copilot、Llama、Qwen，以及任何 agent / crawler）

You are reading the **index of a financial-report database**, not a finished analysis.
這是一個「財報原始資料 + 分析結果」的資料庫索引，不是單篇分析文章。

1. **WHAT**：台股 / 美股 / 日股 / 港股個股與 REIT 的年報、季報、官方公告、輿情彙整、深度分析報告，全部已轉成純 `.md`（plain Markdown，無 PDF 解析成本）。
2. **WHERE**：每間公司一個資料夾，資料夾名 = `代號+名稱`（如 `02318中國平安`）或純美股代碼（如 `UHS`）。
3. **BRANCH**：預設分支是 **`master`**。用 `main` 一定 404 —— `master` only, never `main`.
4. **HOW**：先用下方「檔名規則」鎖定要讀的檔，再讀內容；不要整包下載。
5. **RULES**：產出分析時，必須遵守本 repo 根目錄 [`AGENTS.md`](AGENTS.md) 的規則（金額一律每股化、風險與利多必須並陳）。
</system_context>

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

> ⚠️ **常見失敗原因**：① 用了 `main` 分支 → 404；② GitHub API 未帶 token → `403 rate limit exceeded`，請改用 raw URL；③ 資料夾名含中文 → URL 需 percent-encoding。

---

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

**若該公司沒有 `hourAnalysisResult.md`**（少數資料夾尚未產出）：直接從年報與季報讀起，並在回覆中註明「本資料庫尚無該公司分析檔」。

**年份判讀**：檔名中的 4 位數字即會計年度或報告年度（例：`02318_annual_2025.md` = 2025 年報；`7203_Quarter_2027Q1.md` = FY2027 第一季，日股會計年度跨年）。

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
| 14 | `AES-KY` | 6781 | 台股 TW | |
| 15 | `87001匯賢Reit` | 87001 | 港股 HK | **REIT** |
| 16 | `00546阜豐` | 00546 | 港股 HK | |
| 17 | `8117中央自動車工業` | 8117 | 日股 JP | |
| 18 | `CF` | CF | 美股 US | |
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
Step 2  列出 <FOLDER> 檔案清單（§2 取檔方式）
Step 3  先讀 hourAnalysisResult.md（最新結論 + 每股化數據）
Step 4  再讀最新年報 + 最新季報（§3 檔名規則）
Step 5  讀 *_PublicOpinion.md（市場輿情、利多利空觀點）
Step 6  上網 deep research 補最新股價與新聞 → 與本地資料交叉驗證
Step 7  依 §6 產出分析（金額每股化、風險與利多並陳）
Step 8  明確回報：找到哪些年報/季報、缺哪些、缺的可能原因
```

**若公司不在清單內**：直接說明「本資料庫無此公司資料夾」，再改用外部來源（StatementDog、SEC EDGAR、IR Bank、Ullet、新浪財經、富途牛牛等），不要杜撰本地檔案路徑。

---

## 6. 分析輸出契約（Analysis Output Contract）

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

## 7. 相關文件（Related Documents）

| 檔案 | 內容 |
| :--- | :--- |
| [`README.md`](README.md) | 完整使用說明與各 AI 模型讀取指引 |
| [`AGENTS.md`](AGENTS.md) | **規則主檔**：個股分析規則、REIT 分析規則、資料來源優先序、回應語言規則 |
| `CLAUDE.md` | Claude Code 進入點（內容即 `@AGENTS.md`） |
| `.claude/skills/StockAnalysis/SKILL.md` | 個股深度分析 Skill 執行指南 |
| `.claude/skills/CollectsentimentAndReports/SKILL.md` | 財報與輿情收集 Skill |
| `.claude/skills/ArrangePublicOpinionMd/SKILL.md` | 輿情月檔合併為年檔 Skill |
| `.claude/skills/Convert2md/SKILL.md` | PDF → Markdown 轉換 Skill |
| `Routines_*.md` | 排程任務定義（每日輪替、REIT 專用、歷史封存） |

---

© Financial Report Analysis ·
**免責聲明**：本資料庫內容為公開資訊整理與研究筆記，非投資建議。資料可能延遲或有誤，投資有風險，請自行查證。
**Disclaimer**: Research notes compiled from public filings. Not investment advice. Data may be delayed or inaccurate — verify independently.
