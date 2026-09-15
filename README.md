# 📈 財報分析與研究筆記（Financial Report Analysis）

> 台股 / 美股 / 日股 / 港股個股與 REIT 的**年報、季報、官方公告、輿情彙整與深度分析**資料庫。
> 全部檔案皆為純 Markdown，專為 **AI 助手直接讀取**而設計。
>
> A plain-Markdown database of annual reports, quarterly filings, IR announcements, market sentiment and fundamental analysis for TW / US / JP / HK equities and REITs — built to be read by LLMs.

<llm_context>
**TL;DR for AI assistants** — Claude (Opus / Sonnet / Haiku)、Gemini (Pro / Flash / Flash-Lite)、ChatGPT・GPT・Codex、Grok、DeepSeek、Perplexity、GitHub Copilot、Llama、Qwen，以及任何 agent / crawler：

1. **Branch is `master`, never `main`.** 用 `main` 組 URL 一律 404。
2. **本地優先（Local First）**：回答某公司問題前，**先掃描本 repo 對應公司資料夾**的 `.md`，再上網補最新資訊並交叉驗證。不要只靠訓練資料回答。
3. **先讀 `hourAnalysisResult.md`**：那是該公司最新的深度分析結論（第一行是更新時間戳），比整包年報省 90% token。
4. **風險與利多必須並陳**：Investment risks (利空) AND growth drivers (利多)，缺一不合格。
5. **金額一律每股化**：任何絕對金額都要換算「每股金額」＝ 金額 ÷ 最新流通在外股數，並標註股數口徑。
6. **規則主檔是 [`AGENTS.md`](AGENTS.md)**：真正的執行規則寫在那裡，本 README 只是導覽。
7. **防幻覺（No Fabrication）**：找不到就說找不到，並說明缺漏原因；**嚴禁**杜撰檔案路徑、數字或財報期別。
</llm_context>

---

## 📌 這個 repo 在做什麼

整理台股、美股、日股及港股個股的**基本面分析、歷史財報追蹤、成長潛力與潛在投資風險**，並把 PDF 財報全部轉為 `.md`，讓 LLM 無需 PDF 解析即可讀取。

- **現役追蹤**：31 間公司（根目錄），每月依日期輪替自動更新
- **封存資料**：20 間公司（`History/`）
- **資料型態**：年報 / 季報 / 中期報告 / IR 公告 / 月度輿情 / 年度輿情彙整 / 深度分析報告
- **完整索引**：見 [`index.md`](index.md)（含公司清單、檔名規則、取檔 URL 樣板）

---

## 📂 目錄結構（Repository Layout）

```text
FinancialReport/
├── index.md                       # AI 入口索引：公司清單 + 檔名規則 + 取檔方式
├── README.md                      # 本檔：使用說明與各模型讀取指引
├── AGENTS.md                      # ★ 規則主檔（分析規則、資料來源優先序、語言規則）
├── CLAUDE.md                      # Claude Code 進入點（內容 = @AGENTS.md）
│
├── <代號><公司名>/                # 現役公司資料夾，如 02318中國平安、2881富邦金、UHS
│   ├── hourAnalysisResult.md      #   ★ 最新深度分析（先讀這個）
│   ├── <代號>_annual_<年>.md      #   年報全文
│   ├── <代號>_Quarter_<年>Q<季>.md #   季報全文
│   ├── <年>_PublicOpinion.md      #   年度輿情彙整總檔
│   └── <年月>_輿情新聞.md          #   月度輿情原始檔
│
├── History/<代號><公司名>/        # 已停止追蹤的公司（結構同上）
├── StkScreenerResult/             # 選股器篩選結果與候選名單
├── Log/                           # 排程執行紀錄與彙總
├── Prompt/                        # 可重複使用的提示詞與參考文件
├── gemini/                        # Gemini 專用 routine / prompt 版本
│
├── Routines_CollectsentimentAndReports.md  # ★ 每日輪替表（Single Source of Truth）
├── Routines_StockAnalysis.md      # 每日深度分析排程
├── Routines_Move2History.md       # 根目錄 ↔ History 雙向歸檔同步
├── Routines_HkReit_gemini.md      # 港股 REIT 殖利率 Top10 篩選
├── Routines_JPReit_gemini.md      # 日股 REIT 殖利率 Top10 篩選
├── hourAnalysis.md                # 臨時指定的個股分析任務
│
└── .claude/skills/ , .agents/skills/   # Skill 定義（兩份內容相同，供不同 agent 載入）
```

---

## 🗂️ 檔名規則（File Naming Convention）

看檔名就知道內容，**不要整包讀**。`*` 代表公司代號或日期。

| 檔名樣式 | 內容 | 建議讀取順序 |
| :--- | :--- | :-: |
| `hourAnalysisResult.md` | 最新深度分析報告（結論、估值、每股化數據、風險/利多） | 1 |
| `*_PublicOpinion.md` | 年度輿情彙整總檔（含各論壇原文合併） | 2 |
| `*_annual_*.md`・`*_AnnualReport_*.md`・`*年年報.md`・`*_FY*_annual_results.md` | 年報 / 10-K / 有價證券報告書 | 3 |
| `*_Quarter_*Q*.md`・`*_10Q_*.md`・`*Q*-10-Q.md` | 季報 / 10-Q | 3 |
| `*_interim_*.md`・`*中期報告*.md`・`*_Quarter_*H1.md` | 港股中期報告 | 3 |
| `*_輿情新聞.md`（前綴 `YYYYMM`） | 單月輿情 / 新聞原始檔 | 4 |
| `*_Official_IR.md` | 官方 IR 公告整理 | 4 |
| `*_AI1.md`・`*F04.md`・`*FE4.md`・`*FE6.md` | 台股公開資訊觀測站財報原檔轉換 | 4 |

檔名中的 4 位數字＝會計年度（例：`7203_Quarter_2027Q1.md` = Toyota FY2027 Q1，日股會計年度跨年，勿誤判為未來資料）。

---

## 🤖 給 AI 助手的執行規則（Execution Rules）

### 標準流程

| Step | 動作 | 注意事項 |
| :-: | :--- | :--- |
| 1 | 由代號 / 名稱對應到公司資料夾 | 找不到 → 查 `History/` → 再查 `StkScreenerResult/` |
| 2 | 列出資料夾檔案清單 | 用檔名規則過濾，別全讀 |
| 3 | 讀 `hourAnalysisResult.md` | 第一行時間戳即資料新鮮度 |
| 4 | 讀最新年報 + 最新季報 | 「過去兩年年報 + 最新季報」是分析底線 |
| 5 | 讀 `*_PublicOpinion.md` | 取市場利多 / 利空觀點，需辨識真假訊息 |
| 6 | 上網 deep research | 補最新股價、財測、公告，與本地資料**交叉驗證** |
| 7 | 產出分析 | 金額每股化、風險利多並陳、標註時間戳 |
| 8 | 回報資料狀態 | 找到哪些、缺哪些、缺的原因（如尚未公布） |

### 讀取管道優先序（成功即止）

1. 本機檔案系統：`d:\FinancialReport\<資料夾>\`（零延遲、無 API 限制）
2. GitHub MCP 工具：`repo=a9303001/FinancialReport`、`ref=master`
3. GitHub Contents API：`https://api.github.com/repos/a9303001/FinancialReport/contents/<資料夾>?ref=master`
   → 遇 `403` 表示額度耗盡，改用下一項
4. Raw 讀檔：`https://raw.githubusercontent.com/a9303001/FinancialReport/master/<資料夾>/<檔名>.md`
5. 瀏覽器爬取：`https://github.com/a9303001/FinancialReport/tree/master/<資料夾>`

### 分析輸出必備項目

- **必備數據**：最新 EPS、本益比（PE）、預估 EPS、近五年營業利益率中位數、負債比率、OPM、近五年 ROE 中位數、近五年殖利率中位數、5 年與 10 年淨利 CAGR
- **REIT 加項**：股價淨值比、殖利率、租金報酬率、空租率、負債比率
- **公式**：

```text
負債比率 (%) = 負債 / 總資產 × 100%
OPM (%)      = 營業利益率 / 稅前淨利率 × 100%    （本 repo 自定義）
每股金額     = 絕對金額 / 最新流通在外股數
淨利 CAGR    = (期末淨利 / 期初淨利)^(1/年數) − 1
```

- **股數變動**：若近兩年流通在外股數變動 > 10%，必須說明原因（庫藏股、增發、員工認股、可轉債轉換）與對 EPS 的影響
- **輿情來源**：Reddit、X、Seeking Alpha、PTT、Mobile01、股市爆料同學會、雪球、東方財富股吧、LIHKG、minkabu、kabutan、5ch 等

---

## 🧠 各 AI 模型讀取指引（Per-Model Guidance）

同一份資料，不同模型的最佳讀法不同。核心變數是**上下文長度**與**工具能力**。

| 模型家族 | 建議讀取策略 | 提醒 |
| :--- | :--- | :--- |
| **Claude Opus / Sonnet**（Claude Code、Claude Desktop） | 自動載入 `CLAUDE.md` → `AGENTS.md`；可直接載入 `.claude/skills/` 下的 Skill 執行完整流程。可一次讀多個年報做交叉比對 | 用 Glob/Grep 先定位再讀檔，避免整包載入 |
| **Claude Haiku**（低成本、快） | 只讀 `hourAnalysisResult.md` + `*_PublicOpinion.md` 摘要段落；需要原文時再針對性 grep 關鍵字 | 不要一次塞整份 10-K，會擠掉推理空間 |
| **Gemini Pro** | 長上下文可整包讀年報；可載入 `gemini/` 下的專用 routine 與 `AGENTS.md` | 中文資料夾名在 URL 需 percent-encoding |
| **Gemini Flash / Flash-Lite** | **分段讀**：先讀本 README §檔名規則 → 只抓 1–2 個目標檔；每次回答聚焦單一公司 | 避免同時處理多公司多年報，易混淆年度與幣別 |
| **ChatGPT / GPT / Codex** | 有瀏覽能力時走 raw URL；先抓 `index.md` 取得公司清單再進資料夾 | GitHub API 未帶 token 易 403，直接用 raw URL |
| **Grok / DeepSeek / Qwen / Llama** | 同上，先 `index.md` → 再 `hourAnalysisResult.md`；工具受限時請人工貼入檔案內容 | 無法讀檔時**明講無法讀取**，不要憑印象作答 |
| **Perplexity / 搜尋型** | 以 `index.md` 為索引頁，raw URL 為引用來源 | 引用時請標明檔案路徑與報告期別 |
| **GitHub Copilot / IDE agent** | 直接用工作區檔案系統搜尋，最快 | 勿把分析結果寫進年報原檔，分析一律寫 `hourAnalysisResult.md` |

**共通守則（All models）**

1. 幣別要對：港股 / 中股以 **HKD** 為主要幣別；美股用 **USD**；日股用 **JPY**；台股用 **TWD**。
2. 期別要對：日股會計年度跨年（FY2026 可能結束於 2026/3）；港股有中期報告而非 Q2。
3. 語言：回覆以**繁體中文**為主，專有名詞首次出現附英文（如「每股盈餘（EPS）」）。
4. 時效：財報與輿情有時間性，引用時一律附上**報告期別或日期**。
5. 沒有的資料就說沒有——缺口要明講原因（尚未公布 / 資料庫未更新 / 公司剛上市）。

---

## ⚙️ Skills 與自動化排程

### Skills（`.claude/skills/` 與 `.agents/skills/`，內容相同）

| Skill | 功能 |
| :--- | :--- |
| `StockAnalysis` | 個股深度分析：讀回既有資料 → deep research → 每股化 → 整份重寫 `hourAnalysisResult.md` |
| `CollectsentimentAndReports` | 收集個股最新財務報告與輿情討論 / 新聞 |
| `ArrangePublicOpinionMd` | 把零散月度輿情 `.md` 依年份合併成 `<YYYY>_PublicOpinion.md`，驗證後刪除原檔（年報 / 季報不動） |
| `Convert2md` | 用 MCP `convert_pdf_to_markdown` 把 PDF 轉 Markdown，檢查 CID 亂碼並刪除失敗檔 |

### 排程（Routines）

| 檔案 | 觸發 | 行為 |
| :--- | :--- | :--- |
| `Routines_CollectsentimentAndReports.md` | 每日 | 依「今天幾號」對照輪替表，收集當日公司的財報與輿情 |
| `Routines_StockAnalysis.md` | 每日 | 依同一輪替表執行深度分析，輸出 `hourAnalysisResult.md` |
| `Routines_Move2History.md` | 不定期 | 讓根目錄公司資料夾集合等於輪替表；不在表上的移入 `History/`（雙向搬移、不刪資料） |
| `Routines_HkReit_gemini.md` / `Routines_JPReit_gemini.md` | 不定期 | 港股 / 日股 REIT 殖利率 Top10 篩選與分析 |

> **輪替表是唯一真實依據**：要新增或停止追蹤公司，改 `Routines_CollectsentimentAndReports.md`，再跑 `Routines_Move2History.md` 同步資料夾。

---

## ➕ 新增一間公司（How to Add a Company）

1. 在 `Routines_CollectsentimentAndReports.md` 輪替表加一列：執行日期、`COMPANY_TICKER`、`COMPANY_NAME`、資料夾名稱、市場。
2. 建立資料夾，命名沿用慣例：`<代號><中文名>`（台股 / 港股 / 日股）或純代碼（美股，如 `UHS`）。
3. 放入年報 / 季報：PDF 先用 `Convert2md` Skill 轉 `.md`，檔名沿用 §檔名規則。
4. 執行 `StockAnalysis` Skill 產生 `hourAnalysisResult.md`。
5. 若公司原本在 `History/`，跑 `Routines_Move2History.md` 讓它搬回根目錄。

---

## 📄 授權與免責（License & Disclaimer）

本儲存庫為公開資訊整理與個人研究筆記。年報、季報原文著作權屬各發行公司；分析內容僅供研究參考。

**投資有風險，本資料庫不構成任何投資建議，資料可能延遲或有誤，請自行查證。**

*Research notes compiled from publicly available filings. Not investment advice. Data may be delayed or inaccurate — verify independently before making any investment decision.*
