/boost /goal
# 輪替排程執行器 — StockAnalysis（Gemini 版）

> **一句話任務**：按輪替表，對「一個執行日期」的所有公司，執行「深度分析 → 記錄 → git push」。
>
> **前置條件**：該公司已完成 CollectsentimentAndReports（財報 + 輿情 + 轉 md），本地資料夾中已有最新資料。
>
> **執行模式**：`/boost /goal` 全自動。**嚴禁中途停下向使用者提問（禁止呼叫 `ask_question`）**，必須自主走完 Step 0 → Step 5。

---

## 🚨 不可違反規則（Invariants）— 每一步都要遵守

| # | 規則 | 違反後果 |
|:-:|:-----|:---------|
| 1 | **單輪單日**：每次啟動只做**一個執行日期**的所有公司，完成即結束 | 跨日會導致進度混亂 |
| 2 | **零阻塞**：遇到任何錯誤（逾時、被擋、API 額度）→ 記錄後繼續，不可停下等人 | 停下 = 任務失敗 |
| 3 | **繁體中文**輸出（專有名詞首次附英文，如「每股盈餘（EPS）」） | — |
| 4 | **防幻覺**：所有財務數據必須有來源佐證；**嚴禁用訓練資料捏造** | 捏造 = 任務失敗 |
| 5 | **本地優先**：財報直接讀 `d:\FinancialReport\`，**嚴禁**從 GitHub 線上倉庫下載 | — |

---

## 工具對照表

| 動作 | 工具 |
|:-----|:-----|
| 讀本機檔案 | `view_file`（絕對路徑） |
| 建立/修改檔案 | `write_to_file` / `replace_file_content` |
| 搜尋檔案 | `grep_search` / `find_by_name` / `list_dir` |
| 執行指令 (Git/Curl) | `run_command`（cwd = `d:\FinancialReport`） |
| 網路搜尋 | `search_web` |
| 抓取網頁 | `read_url_content` |
| MCP 進階爬取 | `call_mcp_tool`（Firecrawl / Bright Data / Apify / Playwright） |

---

## 執行流程總覽

```
Step 0  git pull 同步
  ↓
Step 1  讀取輪替表 + 上次進度 → 算出本輪目標
  ↓
Step 2  執行 StockAnalysis Skill（深度分析）
  ↓
Step 3  記錄進度 + 產出日誌
  ↓
Step 4  git add / commit / push master
  ↓
  ✅ 完成，輸出精簡摘要
```

---

## Step 0：git pull

```powershell
# cwd = d:\FinancialReport
git pull origin master
```

- 若衝突：`git stash && git pull origin master && git stash pop`
- 若失敗：記錄錯誤，繼續（不中斷）

---

## Step 1：讀取輪替表 + 決定本輪目標

### 1.1 讀取輪替表

1. `view_file` 讀取 `d:\FinancialReport\Routines_StockAnalysis.md`
2. 解析「每日輪替表」：
   - 有效日期：1 ~ 30
   - 提取每日的 `COMPANY_NAME`、`MARKET`、`COMPANY_FOLDER`、`EXTRA_ANALYSIS`

### 1.2 讀取上次進度

1. `view_file` 讀取 `d:\FinancialReport\Log\gemini_hourAnalysis_Summary.md`
2. 提取 `last_executed_date`（整數）
3. 若檔案不存在或無法解析 → 預設 `last_executed_date = 0`

### 1.3 計算目標

```
target_date = last_executed_date + 1
if target_date > 30:
    target_date = 1

companies = 輪替表中所有 [執行日期 == target_date] 的公司
```

---

## Step 2：執行 StockAnalysis Skill

> **完整規則請讀**：`d:\FinancialReport\.agents\skills\StockAnalysis\SKILL.md`
>
> ⚠️ **輸出檔名（極重要）**：本排程產出的分析報告，檔名**必須**帶 `gemini` 字眼，以區分不同 AI 模型產出的結果。

### 2.0 固定參數（Hard-coded，不可更改）

```
OUTPUT_FILENAME = hourAnalysisResult_gemini.md
```

- 此值**覆蓋** `Routines_StockAnalysis.md` 中的全域 `OUTPUT_FILENAME`。
- 理由：同一公司可能由不同 AI（Claude / Gemini）各自產出分析報告，透過檔名區分版本。

### 2.1 執行步驟

對本輪每間公司，依序執行：

1. `view_file` 讀取 `d:\FinancialReport\Routines_StockAnalysis.md`
2. 找 `執行日期 == target_date` 的公司，取出其 `COMPANY_NAME`、`MARKET`、`COMPANY_FOLDER`、`EXTRA_ANALYSIS`
3. **呼叫 StockAnalysis Skill**，傳入以下參數：

   | StockAnalysis 參數 | 值的來源 | 範例 |
   |:---|:---|:---|
   | `COMPANY_NAME` | 輪替表 | `02318 中國平安` |
   | `MARKET` | 輪替表 | `港股/中股` |
   | `COMPANY_FOLDER` | 輪替表 | `02318中國平安` |
   | `OUTPUT_FILENAME` | **本排程固定值** | **`hourAnalysisResult_gemini.md`** |
   | `EXTRA_ANALYSIS` | 輪替表（無則留空）| `房地產曝險分析…` |

4. 分析報告**寫入路徑**：`d:\FinancialReport\{COMPANY_FOLDER}\hourAnalysisResult_gemini.md`
   - 核心要求：**頭部優先** / **初級分析師可讀** / **財務數據每股化** / **完整檔案**
5. 若 Routines_StockAnalysis.md 無對應日期 → 記錄 `⏭️ 無對應`，不影響流程

---

## Step 3：雙重記錄

### 3.1 更新進度檔

更新 `d:\FinancialReport\Log\gemini_hourAnalysis_Summary.md`：

```markdown
# Rotation Progress — StockAnalysis (Gemini)

| 欄位 | 值 |
|:-----|:---|
| **last_executed_date** | {target_date} |
| **last_executed_companies** | {公司清單} |
| **last_executed_time** | {YYYY-MM-DD HH:MM} |
| **next_date** | {下一輪日期，若 30 則為 1} |
| **stock_analysis_status** | {✅ / ⏭️ / ❌} |
```

### 3.2 產出當次日誌

寫入 `d:\FinancialReport\Log\hourAnalysis_gemini_Summary_{yyyyMMdd}.md`：

```markdown
# StockAnalysis 執行報告 (Gemini) - YYYY/MM/DD

- **執行日期**：YYYY-MM-DD
- **輪替序號**：執行日期 {N}（{公司名稱}）
- **上一輪**：執行日期 {N-1}
- **下一輪預定**：執行日期 {N+1}

---

## 1. 分析結果
| 股號/名稱 | 產生的檔案 | 狀態 |
|:----------|:-----------|:-----|
| ... | hourAnalysisResult_gemini.md | ✅ / ❌ |

---

## 2. 失敗或受限紀錄
- **公司**: {名稱}
- **原因**: {具體錯誤}
- **處置**: {嘗試過的方法}

---

## 3. 資料缺失說明
- {尚未發布的季報/年報，或缺少本地資料}

---

## 4. 本次 MCP 使用紀錄（強制填寫）
| MCP 服務 | 工具/函式 | 用途 |
|:---------|:----------|:-----|
| ... | ... | ... |
| （若無）| — | 本次僅用原生工具 |
```

---

## Step 4：Git Push

```powershell
git add -A
git commit -m "StockAnalysis(gemini): 執行日期 {target_date} - {公司清單}"
git push origin master
```

- 若被拒絕：`git pull --rebase origin master && git push origin master`

---

## 最終 Chat 回覆格式

Step 0 ~ 4 全部完成後，輸出以下精簡摘要：

```
✅ StockAnalysis(gemini) — YYYY-MM-DD HH:MM
- 本輪：執行日期 {N}（{公司名稱}）
- 分析：✅ 成功（hourAnalysisResult_gemini.md）
- 記錄：✅ 已更新 Summary.md + 日誌
- Git：✅ 已 push master
- 下一輪：執行日期 {Next}（{下輪公司}）
```

