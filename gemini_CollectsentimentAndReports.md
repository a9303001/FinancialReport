/boost /goal
# gemini_CollectsentimentAndReports — 輪替排程執行器（Optimized v2）

> **用途**：定期輪替執行 `CollectsentimentAndReports` skill，每次執行**一個執行日期**的所有公司。
> 完成後自動串接 `StockAnalysis` Skill，產出最新分析報告。
>
> **強制模式**：本排程以 `/boost /goal` 模式執行。必須徹底完成所有步驟，不得中途停下詢問使用者。

---

## 執行流程總覽

```mermaid
graph TD
    S0["Step 0: git pull 同步最新資料"] --> S1["Step 1: 讀取輪替表"]
    S1 --> S2["Step 2: 讀取上次進度"]
    S2 --> S3["Step 3: 決定本輪執行日期與公司"]
    S3 --> S4["Step 4: 執行 CollectsentimentAndReports Skill"]
    S4 --> S5["Step 5: 執行 StockAnalysis Skill（串接）"]
    S5 --> S6["Step 6: 更新進度檔"]
    S6 --> S7["Step 7: git commit + push master"]
    S7 --> DONE["✅ 完成"]
```

---

## Step 0：同步本地倉庫（每次啟動必做）

> **為什麼**：其他 AI Agent（如 Claude）可能在上次執行後已經 push 了新的財報或輿情檔案。若不先 pull，會導致：
> (a) 重複下載已有的財報、(b) push 時發生衝突。

```bash
cd d:\FinancialReport && git pull origin master
```

- 若 pull 失敗（如衝突），先嘗試 `git stash && git pull && git stash pop`。
- 若仍失敗，記錄錯誤，繼續執行（不阻塞整個任務）。

---

## Step 1：讀取輪替表

1. 開啟 `d:\FinancialReport\Routines_CollectsentimentAndReports.md`。
2. 解析「每日輪替表 (Rotation Table)」，取得所有「執行日期」對應的公司清單。
3. **排除** 執行日期 31（標記為「無/不執行 (Skip)」）。
4. 記錄有效的最大執行日期（目前為 30）。

---

## Step 2：讀取上次進度

1. 開啟 `d:\FinancialReport\Log\gemini_CollectsentimentAndReports_Summary.md`（進度追蹤檔）。
2. 讀取 `last_executed_date` 欄位（上次已執行的「執行日期」編號）。
3. 若進度檔**不存在**或**讀取失敗** → **隨機挑一個有效執行日期**開始。

---

## Step 3：決定本輪要執行的公司

### 3.1 計算本輪執行日期

```
本輪執行日期 = last_executed_date + 1
```

- 若超過輪替表最大日期（目前 30）→ 回到**執行日期 1**（循環）。
- 若剛好是 31（Skip）→ 跳過，繼續 +1 直到找到有效日期。

### 3.2 取出公司資訊

從輪替表中取出該日期對應的所有公司：`COMPANY_TICKER`、`COMPANY_NAME`、`本地資料夾名稱 (Folder)`、`備註 / 市場`。

> [!IMPORTANT]
> **同一日期有多間公司**（如執行日期 5 有 `3445 RS` 和 `688432 有研硅`）→ 該輪**全部執行**，視為同一批次。全部完成後才將進度推進。

### 3.3 確認結果（在繼續前輸出）

在進入 Step 4 前，先明確輸出：
```
📋 本輪執行日期：{N}
📋 待執行公司：{公司1}, {公司2}...
📋 上次完成：執行日期 {last_executed_date}（{上次公司}）
```

---

## Step 4：執行 CollectsentimentAndReports Skill

### 4.1 載入 Skill

讀取 `d:\FinancialReport\.agents\skills\CollectsentimentAndReports\SKILL.md`，取得完整執行指南。

### 4.2 逐間執行

對本輪日期的每一間公司，依序執行：

1. 呼叫 CollectsentimentAndReports skill，帶入：
   - `COMPANY_TICKER` = 該列的股票代碼
   - `COMPANY_NAME` = 該列的公司名稱
2. 依照 skill 的完整流程執行（Phase 1 ~ Phase 5）。
3. 若同一日期有多間公司，**依序逐間執行**（完成一間再做下一間）。

### 4.3 錯誤處理

- **單間公司部分失敗**（如某個輿情來源爬取失敗）→ 依 Skill 的 §2 通用抓取規則處理，記錄失敗後繼續。
- **單間公司整體失敗**（如所有工具全部不可用）→ 記錄失敗原因，繼續下一間公司。
- **不得因單間失敗而阻塞整個批次**。

---

## Step 5：串接 StockAnalysis Skill

> **目的**：收集完輿情/財報後，趁資料最新鮮，立即對同一公司做深度分析。

### 5.1 查找對應分析

1. 開啟 `d:\FinancialReport\Routines_StockAnalysis.md`。
2. 用**本輪執行日期**去比對「每日輪替表」的「執行日期」欄。

### 5.2 決策樹

```mermaid
graph TD
    A["查詢 Routines_StockAnalysis.md"] --> B{有對應公司？}
    B -->|有| C["讀取 StockAnalysis SKILL.md"]
    C --> D["執行 StockAnalysis"]
    D --> E["stock_analysis_status = ✅"]
    B -->|無| F["stock_analysis_status = ⏭️ 無對應"]
    D -->|失敗| G["stock_analysis_status = ❌ 失敗"]
```

### 5.3 執行方式

- **有對應公司** → 取出 `COMPANY_NAME`、`MARKET`、`COMPANY_FOLDER`、`EXTRA_ANALYSIS`，搭配全域參數 `OUTPUT_FILENAME = hourAnalysisResult.md`，載入並執行 StockAnalysis Skill（`.agents/skills/StockAnalysis/SKILL.md`）。
- **同一日期有多間公司** → 依序逐間執行。
- **無對應公司** → Skip，記錄「⏭️ 無對應公司」。
- **StockAnalysis 失敗不阻塞進度**：記錄 `❌ 失敗`，進度仍然推進。

---

## Step 6：更新進度檔

執行完畢後，更新 `d:\FinancialReport\Log\gemini_CollectsentimentAndReports_Summary.md`：

```markdown
# Rotation Progress — CollectsentimentAndReports

| 欄位 | 值 |
| :--- | :--- |
| **last_executed_date** | {本輪執行日期} |
| **last_executed_companies** | {本輪公司清單，如 `00941 中國移動`} |
| **last_executed_time** | {完成時間 YYYY-MM-DD HH:MM} |
| **next_date** | {下一輪預計執行日期} |
| **stock_analysis_status** | {StockAnalysis 執行結果：✅ 成功 / ⏭️ 無對應 / ❌ 失敗} |
```

---

## Step 7：推送至遠端

```bash
cd d:\FinancialReport
git add -A
git commit -m "CollectsentimentAndReports: 執行日期 {N} - {公司名}"
git push origin master
```

- 若 push 失敗（如遠端有新 commit），先 `git pull --rebase origin master` 再 push。
- 若仍失敗，記錄錯誤但不阻塞進度檔更新。

---

## 輪替範例

| 輪次 | 執行日期 | 公司 | Collect | StockAnalysis | 說明 |
| :--- | :---: | :--- | :---: | :---: | :--- |
| 第 1 輪 | 1 | `02318 中國平安` | ✅ | ✅ | 首次執行或上輪結束於 30 |
| 第 2 輪 | 2 | `00941 中國移動` | ✅ | ✅ | |
| 第 3 輪 | 3 | `01426 春泉Reit` | ✅ | ✅ | |
| 第 4 輪 | 4 | `9435 光通訊` | ✅ | ✅ | |
| 第 5 輪 | 5 | `3445 RS` + `688432 有研硅` | ✅ | ✅ | 同日期多公司，一次全做 |
| ... | ... | ... | ... | ... | |
| 第 14 輪 | 14 | `6121 新普` + `6781 AES-KY` | ✅ | ✅ | 同日期多公司 |
| ... | ... | ... | ... | ... | |
| 第 29 輪 | 29 | `00883` + `00857` + `00386` | ✅ | ✅ | 同日期三間 |
| 第 30 輪 | 30 | `8002 丸紅` | ✅ | ✅ | |
| 第 31 輪 | 跳過 31 → **回到 1** | `02318 中國平安` | ✅ | ✅ | 循環重頭開始 |

---

## 注意事項

1. **每次啟動都必須重新讀取 `Routines_CollectsentimentAndReports.md` 和 `Routines_StockAnalysis.md`**，不可快取或硬編碼輪替表。原因：使用者可能隨時新增/移除/調整公司或日期。
2. **進度追蹤依賴 `gemini_CollectsentimentAndReports_Summary.md`**，不依賴系統日期來決定該做哪間公司。系統日期僅用於記錄「完成時間」。
3. **若輪替表被修改**（例如新增了執行日期 32 的公司），下一輪會自然適應，因為每次都重新解析表格。
4. **同一「執行日期」有多間公司時**，視為同一批，全部完成後才將進度推進到該日期。若中途失敗，`last_executed_date` 不更新，下次會重新嘗試同一日期。
5. **StockAnalysis 的執行日期與 CollectsentimentAndReports 共用同一套日期編號**。若 `Routines_StockAnalysis.md` 中無對應日期，StockAnalysis 自動 Skip，不影響 CollectsentimentAndReports 的進度推進。
6. **StockAnalysis 失敗不阻塞進度**：若 StockAnalysis 執行失敗，進度檔仍然推進（記錄 `stock_analysis_status: ❌ 失敗`），下次不會因此重跑 CollectsentimentAndReports。
7. **每次只執行一個執行日期**：不要一次跑多個日期。一個日期完成後，更新進度檔並結束。下次啟動時自動輪到下一個日期。