/boost /goal
# 輪替排程執行器 — StockAnalysis（Gemini 版）

> **一句話任務**：按輪替表，對「一個執行日期」的所有公司，執行「深度分析 → 驗收 → 記錄 → git push」。
>
> **唯一輸出檔**：`{COMPANY_FOLDER}/hourAnalysisResult.md`（Claude、Gemini 或任何執行者共用同一份，不再依模型分檔）。
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
| 6 | **整份重寫**：交付前必須對輸出檔執行 SKILL.md §7 Final Rewrite，且第一行為真實系統時間戳 | 流水帳 = 任務失敗 |

---

## 工具對照表

| 動作 | 工具 |
|:-----|:-----|
| 讀本機檔案 | `view_file`（絕對路徑） |
| 建立/修改檔案 | `write_to_file` / `replace_file_content` |
| 搜尋檔案 | `grep_search` / `find_by_name` / `list_dir` |
| 執行指令 (Git/Curl) | `run_command`（cwd = `d:\FinancialReport`） |
| 取系統時間 | `run_command`：`Get-Date -Format "yyyy/MM/dd HH:mm:ss"` |
| 網路搜尋 | `search_web` |
| 抓取網頁 | `read_url_content` |
| MCP 進階爬取 | `call_mcp_tool`（Firecrawl / Bright Data / Apify / Playwright） |

---

## 執行流程總覽

```
Step 0  git pull 同步
  ↓
Step 1  讀輪替表 + 上次進度 → 算出本輪目標（公司清單）
  ↓
Step 2  前置盤點：資料夾存在？本地財報／輿情齊全？
  ↓
Step 3  執行 StockAnalysis Skill（深度分析 → Final Rewrite）
  ↓
Step 4  驗收：交付檢查（不過 → 就地修正後重跑）
  ↓
Step 5  記錄進度 + 產出日誌 + git add / commit / push master
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
- 若網路失敗：重試最多 3 次（間隔 2s / 4s / 8s），仍失敗則記錄錯誤，**繼續**（不中斷）

---

## Step 1：讀取輪替表 + 決定本輪目標

> ⚠️ 本步驟把輪替表**讀一次就好**，解析結果留在上下文供 Step 3 使用，不要重複讀檔。

### 1.1 讀取輪替表

1. `view_file` 讀取 `d:\FinancialReport\Routines_StockAnalysis.md`
2. 解析「每日輪替表」：
   - 有效日期：**1 ~ 30**（輪替表無 31，故日期 31 不會有對應公司）
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
# 注意：同一日期可能有多間公司（如日期 5 有 3445 RS + 中國子公司有研硅 688432.SH）
# 多公司必須在同一輪內全部依序執行完畢，不可只做第一間就收工
```

- 若 `target_date` 無對應公司 → 記錄 `⏭️ 無對應`，**仍需**更新進度檔（`last_executed_date = target_date`）讓輪替往前走，然後結束

---

## Step 2：前置盤點（Pre-flight）

對本輪每間公司做一次快速盤點，30 秒內完成，目的是讓 Step 3 知道「手上有什麼料」：

| # | 檢查 | 做法 | 缺了怎麼辦（零阻塞） |
|:-:|:-----|:-----|:---------------------|
| 1 | 公司資料夾存在？ | `list_dir d:\FinancialReport\{COMPANY_FOLDER}\` | 不存在 → 建立空資料夾，日誌記「本地無資料，全靠 deep research」 |
| 2 | 年報／季報 md 齊全？ | 看有無 `*_AnnualReport_*.md`、`*_Quarter_*.md` | 缺 → 照樣分析，並在輸出檔 §11 與日誌「資料缺失說明」寫明缺哪一期、可能原因 |
| 3 | 輿情檔存在？ | 看有無 `{yyyy}_PublicOpinion.md`、`{yyyyMM}_輿情新聞.md` | 缺 → 改以 `search_web` 補足，並記錄 |
| 4 | 上一版報告存在？ | 看有無 `hourAnalysisResult.md` | 不存在 → 視為**首輪**，全新產出 |

---

## Step 3：執行 StockAnalysis Skill

> **完整規則請讀**：`d:\FinancialReport\.agents\skills\StockAnalysis\SKILL.md`

### 3.1 執行步驟

對本輪每間公司，依序執行：

1. 從 Step 1.1 已解析的結果取出該公司的 `COMPANY_NAME`、`MARKET`、`COMPANY_FOLDER`、`EXTRA_ANALYSIS`
2. **呼叫 StockAnalysis Skill**，傳入以下參數：

   | StockAnalysis 參數 | 值的來源 | 範例 |
   |:---|:---|:---|
   | `COMPANY_NAME` | 輪替表 | `02318 中國平安` |
   | `MARKET` | 輪替表 | `港股/中股` |
   | `COMPANY_FOLDER` | 輪替表 | `02318中國平安` |
   | `EXTRA_ANALYSIS` | 輪替表（無則留空）| `房地產曝險分析…` |

   > 輸出寫入路徑固定為 `d:\FinancialReport\{COMPANY_FOLDER}\hourAnalysisResult.md`（直接覆寫，不加日期後綴）。
3. 全程核心要求（細節見 SKILL.md 對應章節）：

   | 要求 | 依據 |
   |:-----|:-----|
   | 頭部優先（最重要 × 最新放最前面） | §4.1、§4.5 |
   | 七大基本面支柱全覆蓋 | §3.1.1 |
   | 所有金額**每股化** + 每股化總表 | §4.3、§7.2 |
   | 主要幣別正確（港股／中股用 HKD） | §4.6 |
   | 寫給初級分析師看（說人話、術語寫英文、無 Glossary） | §5 |
   | 交付前**整份重寫**（Final Rewrite） | §7 |
   | 第一行為**真實系統時間戳** `yyyy/MM/dd HH:mm:ss (UTC+8)` | §4.2 第 0 項、§7.1 Step 7 |

4. 時間戳一律用指令實取，**嚴禁憑印象或沿用上一版**：

   ```powershell
   Get-Date -Format "yyyy/MM/dd HH:mm:ss"
   ```

5. 若 `Routines_StockAnalysis.md` 無對應日期 → 記錄 `⏭️ 無對應`，不影響流程

---

## Step 4：驗收（Acceptance · 不過就修，修完重跑本步）

### 交付檢查（Definition of Done）

- [ ] `{COMPANY_FOLDER}\hourAnalysisResult.md` 已更新，且**第一行**是本輪真實系統時間戳（`yyyy/MM/dd HH:mm:ss (UTC+8)`）
- [ ] 已完成 §7 Final Rewrite（整份重寫，非局部補丁、非新舊堆疊）
- [ ] 通過 SKILL.md §7.6 Final Rewrite Checklist（A 結構／B 每股化／C 汰除／D 基本面與幣別）
- [ ] 通過 SKILL.md §5.5 可讀性 checklist 與 §4.5.4 頭部檢查三題
- [ ] `EXTRA_ANALYSIS` 每一項都有對應段落與數字（沒有的要寫明查不到與原因）
- [ ] 本輪每間公司都做完（多公司日期不可漏）

> 任一項不過 → **就地修正後重跑 Step 4**，通過才進 Step 5。

---

## Step 5：記錄 + Git Push

### 5.1 更新進度檔

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

### 5.2 產出當次日誌

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
| ... | hourAnalysisResult.md | ✅ / ❌ |

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

### 5.3 Git Push

```powershell
git add -A
git commit -m "StockAnalysis(gemini): 執行日期 {target_date} - {公司清單}"
git push origin master
```

- 若被拒絕（non-fast-forward）：`git pull --rebase origin master && git push origin master`
- 若網路失敗：重試最多 4 次（間隔 2s / 4s / 8s / 16s）

---

## 錯誤處理（零阻塞 Playbook）

| 狀況 | 處置 |
|:-----|:-----|
| 網路搜尋被擋／逾時 | 換來源或升級工具鏈（內建 → Firecrawl → Bright Data → Apify → Playwright），全失敗就誠實寫「查無」 |
| MCP API 額度用盡 | 記錄後改用原生工具，繼續 |
| 本地無年報／季報 | 照樣分析，缺口寫進輸出檔 §11 與日誌第 3 節 |
| 某公司整段失敗 | 標 ❌ 記錄原因，**繼續下一間**，不可中斷全輪 |
| git pull／push 失敗 | 依 Step 0 / 5.3 的重試規則，仍失敗則記錄錯誤並在摘要標 ❌ |

---

## 最終 Chat 回覆格式

Step 0 ~ 5 全部完成後，輸出以下精簡摘要：

```
✅ StockAnalysis(gemini) — YYYY-MM-DD HH:MM
- 本輪：執行日期 {N}（{公司名稱}）
- 分析：✅ 成功（hourAnalysisResult.md）
- 記錄：✅ 已更新 Summary.md + 日誌
- Git：✅ 已 push master
- 下一輪：執行日期 {Next}（{下輪公司}）
```
