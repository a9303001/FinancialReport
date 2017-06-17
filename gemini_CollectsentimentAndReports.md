/boost /goal
# 輪替排程執行器 — CollectsentimentAndReports + StockAnalysis

> **一句話任務**：按輪替表，對「一個執行日期」的所有公司，依序完成「財報收集 → 輿情收集 → 轉 md → 深度分析 → 記錄 → git push」。
>
> **執行模式**：`/boost /goal` 全自動。**嚴禁中途停下向使用者提問（禁止呼叫 `ask_question`）**，必須自主走完 Step 0 → Step 7。

---

## 🚨 不可違反規則（Invariants）— 每一步都要遵守

| # | 規則 | 違反後果 |
|:-:|:-----|:---------|
| 1 | **單輪單日**：每次啟動只做**一個執行日期**的所有公司，完成即結束 | 跨日會導致進度混亂 |
| 2 | **零阻塞**：遇到任何錯誤（逾時、被擋、API 額度）→ 記錄後繼續，不可停下等人 | 停下 = 任務失敗 |
| 3 | **繁體中文**輸出（專有名詞首次附英文，如「每股盈餘（EPS）」） | — |
| 4 | **防幻覺**：輿情/新聞必須附真實 URL + 時間戳；抓不到就寫「查無」，**嚴禁用訓練資料捏造** | 捏造 = 任務失敗 |
| 5 | **本地優先**：財報直接讀 `d:\FinancialReport\`，**嚴禁**從 GitHub 線上倉庫下載 | — |

---

## 工具對照表

> 下文用「動作」描述要做的事。請對照你實際擁有的工具執行。

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
Step 1  讀取輪替表
  ↓
Step 2  讀取上次進度
  ↓
Step 3  算出本輪執行日期 + 公司清單
  ↓
Step 4  CollectsentimentAndReports Skill（財報 + 輿情 + 轉 md）
  ↓
Step 5  StockAnalysis Skill（深度分析）
  ↓
Step 6  記錄進度 + 產出日誌
  ↓
Step 7  git add / commit / push master
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

## Step 1：讀取輪替表

1. `view_file` 讀取 `d:\FinancialReport\Routines_CollectsentimentAndReports.md`
2. 解析「每日輪替表」：
   - 有效日期：1 ~ 30
   - 排除日期 31（Skip）
   - 提取每日的 `COMPANY_TICKER`、`COMPANY_NAME`、`Folder`、`市場`

---

## Step 2：讀取上次進度

1. `view_file` 讀取 `d:\FinancialReport\Log\gemini_CollectsentimentAndReports_Summary.md`
2. 提取 `last_executed_date`（整數）
3. 若檔案不存在或無法解析 → 預設 `last_executed_date = 0`

---

## Step 3：決定本輪目標

**偽代碼：**
```
target_date = last_executed_date + 1
if target_date > 30:
    target_date = 1

companies = 輪替表中所有 [執行日期 == target_date] 的公司
# 注意：同一日期可能有多間公司（如日期 5 有 3445 RS + 688432 有研硅）
# 多公司必須在同一輪內全部依序執行完畢
```

---

## Step 4：執行 CollectsentimentAndReports Skill

> **完整規則請讀**：`d:\FinancialReport\.agents\skills\CollectsentimentAndReports\SKILL.md`
> 
> ⚠️ **以下是精簡版。遇到任何不確定的情況，以 SKILL.md 為準。**

對本輪每間公司，依序完成 4 個子階段：

### 4.1 Phase 1：確認資料夾存在

- 路徑：`d:\FinancialReport\{COMPANY_FOLDER}\`
- 不存在則建立

### 4.2 Phase 2：財報盤點與下載

**目標**：最新 **2 份年報** + **1 份季報**

**流程：**
1. `list_dir` / `find_by_name` 盤點現有檔案
2. 已有 → 跳過；缺的 → 依下方順序搜尋下載

**統一命名：**
| 類型 | 格式 | 範例 |
|:-----|:-----|:-----|
| 年報 | `{TICKER}_AnnualReport_{FY}.pdf` | `2881_AnnualReport_2025.pdf` |
| 季報 | `{TICKER}_Quarter_{FY}Q{N}.pdf` | `2881_Quarter_2026Q1.pdf` |

**搜尋來源順序（找到即停）：**
- **台股**：MOPS（英文版優先）→ 財報狗 → 官網 IR
- **美股**：官網 IR → SEC EDGAR → 財報狗 → 富途牛牛
- **日股**：官網 IR（英文優先）→ EDINET → IR Bank → 富途牛牛
- **港股**：披露易 → 新浪財經 → 富途牛牛

**下載驗證：**
- 檔案 < 10KB → 無效，刪除
- 前幾頁不含公司名稱 → 無效，刪除
- `(cid:` 出現 > 50 次 → 字型缺字，刪除，換英文版
- Read Timeout / EOF → **零重試**，直接換來源

### 4.3 Phase 3：近三個月輿情收集

**存檔**：`d:\FinancialReport\{COMPANY_FOLDER}\{yyyyMM}_輿情新聞.md`（一月一檔，Append 模式）

**抓取工具鏈**（遇阻時依序升級，詳見 SKILL.md §2）：

```
① 內建工具（search_web / read_url_content）
  ↓ 失敗
② firecrawl_scrape
  ↓ 失敗
③ brightdata scrape_as_markdown
  ↓ 失敗
④ apify
  ↓ 失敗
⑤ playwright
  ↓ 全部失敗
❌ 誠實記錄，換下一個來源
```

**特殊站點捷徑（不走一般鏈）：**

| 站點 | 做法 | 詳見 |
|:-----|:-----|:-----|
| **雪球** | 直接用 `brightdata scrape_as_markdown` | SKILL.md §2.7 |
| **CMoney 股市爆料同學會** | 直接打官方 API（curl）| SKILL.md §2.8 |
| **Reddit** | 直接用 Apify `trudax/reddit-scraper-lite` | SKILL.md §2.9 |
| **X (Twitter)** | 用 `firecrawl_search` + `site:x.com` 搜尋 | SKILL.md §2.4 |

**寫入規則：**
- 檔案不存在 → 新建，含標頭
- 檔案已存在 → Append 在末尾
- 查無資料 → **仍須寫入**「已查詢 {來源}，近三個月無重大討論」，嚴禁空白，嚴禁捏造

### 4.4 Phase 4：Convert2md 轉換

- 掃描資料夾是否有未轉 md 的 `.pdf` / `.html`
- 有 → 呼叫 MCP `convert_pdf_to_markdown` 轉換
- 清理無效轉換檔

---

## Step 5：串接 StockAnalysis Skill

> **完整規則請讀**：`d:\FinancialReport\.agents\skills\StockAnalysis\SKILL.md`
>
> ⚠️ **輸出檔名（極重要）**：本排程產出的分析報告，檔名**必須**帶 `gemini` 字眼，以區分不同 AI 模型產出的結果。

### 5.0 固定參數（Hard-coded，不可更改）

```
OUTPUT_FILENAME = hourAnalysisResult_gemini.md
```

- 此值**覆蓋** `Routines_StockAnalysis.md` 中的全域 `OUTPUT_FILENAME`。
- 理由：同一公司可能由不同 AI（Claude / Gemini）各自產出分析報告，透過檔名區分版本。

### 5.1 執行步驟

1. `view_file` 讀取 `d:\FinancialReport\Routines_StockAnalysis.md`
2. 找 `執行日期 == target_date` 的公司，取出其 `EXTRA_ANALYSIS`、`COMPANY_NAME`、`MARKET`、`COMPANY_FOLDER`
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

## Step 6：雙重記錄

### 6.1 更新進度檔

更新 `d:\FinancialReport\Log\gemini_CollectsentimentAndReports_Summary.md`：

```markdown
# Rotation Progress — CollectsentimentAndReports

| 欄位 | 值 |
|:-----|:---|
| **last_executed_date** | {target_date} |
| **last_executed_companies** | {公司清單} |
| **last_executed_time** | {YYYY-MM-DD HH:MM} |
| **next_date** | {下一輪日期，若 30 則為 1} |
| **stock_analysis_status** | {✅ / ⏭️ / ❌} |
```

### 6.2 產出當次日誌

寫入 `d:\FinancialReport\Log\CollectsentimentAndReports_Summary_{yyyyMMdd}.md`：

```markdown
# 任務執行最終報告 - YYYY/MM/DD

- **執行日期**：YYYY-MM-DD
- **輪替序號**：執行日期 {N}（{公司名稱}）
- **上一輪**：執行日期 {N-1}
- **下一輪預定**：執行日期 {N+1}

---

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生的檔案 | 狀態 |
|:----------|:---------|:-----------|:-----|
| ... | ... | ... | ... |

---

## 2. 失敗、被擋或受限網站
- **來源**: {名稱與 URL}
- **原因**: {具體錯誤}
- **處置**: {嘗試過的工具鏈}

---

## 3. 資料缺失說明
- {尚未發布的季報/年報，或冷門標的查無討論}

---

## 4. 異常檔案刪除紀錄
- {< 10KB 或 (cid:N) 亂碼的無效檔案}

---

## 5. 本次 MCP 使用紀錄（強制填寫）
| MCP 服務 | 工具/函式 | 用途 |
|:---------|:----------|:-----|
| ... | ... | ... |
| （若無）| — | 本次僅用原生工具 |

---

## 6. StockAnalysis 結果
- **狀態**：{✅ / ⏭️ / ❌}
- **產出**：`{COMPANY_FOLDER}/hourAnalysisResult_gemini.md`
```

---

## Step 7：Git Push

```powershell
git add -A
git commit -m "CollectsentimentAndReports(gemini): 執行日期 {target_date} - {公司清單}"
git push origin master
```

- 若被拒絕：`git pull --rebase origin master && git push origin master`

---

## 最終 Chat 回覆格式

Step 0 ~ 7 全部完成後，輸出以下精簡摘要：

```
✅ CollectsentimentAndReports(gemini) — YYYY-MM-DD HH:MM
- 本輪：執行日期 {N}（{公司名稱}）
- 財報：✅ 完成（2 年報 + 1 季報齊全）
- 輿情：✅ 完成（寫入 {yyyyMM}_輿情新聞.md）
- 轉換：✅ 完成
- 分析：✅ 成功（hourAnalysisResult_gemini.md）
- 記錄：✅ 已更新 Summary.md + 日誌
- Git：✅ 已 push master
- 下一輪：執行日期 {Next}（{下輪公司}）
```