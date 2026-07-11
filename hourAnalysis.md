/loop 1hour /goal


## 0-A. 執行期限（最重要 · 只跑 3 天就停止）

- **總執行期限：僅限 3 天（72 小時）**，到期後**自動停止**每小時排程，不再繼續執行。
- **起算基準**：以「**第一次執行（首輪 fire）**」的時間戳記為 Day 1 起點。
  - 若 `UHS/hourAnalysis.md` 檔首尚無「排程起始時間（Schedule Start）」紀錄，則本輪視為首輪，**必須先寫入起始時間戳記**再開始分析。
  - 若已有「排程起始時間」，則沿用該時間為起算點。
- **停止條件（滿足任一即停止）**：
  1. 目前時間 **≥ 排程起始時間 + 3 天（72 小時）**。
  2. 已完成的執行輪次涵蓋滿 3 天。
- **到期動作**：
  1. 於 `UHS/hourAnalysis.md` 檔首標註「**排程已於 {時間戳記} 達 3 天上限，已停止**」。
  2. **刪除／停用對應的 Routine（排程）**，確保不再產生新 session、不再每小時 fire。
  3. 做最後一次 `commit + push`（並 merge 回 `master`）後結束。
- **未到期**：照常執行下方每小時分析流程。

---

## 0. Session 執行方式（最重要 · 每次開全新 session）

- **每次觸發都開一個「全新 session」執行**（fresh session per run），**不要**綁定同一個持久化 session。
- **原因**：若綁定固定 session，一旦該 session 消失／逾時／被回收，整條每小時排程就會失效、無法再 hour 執行。改為每次開新 session，可確保排程長期穩定、不中斷。
- **狀態延續靠檔案、不靠 session**：每次都是空白 session，所以「上一輪的分析結論」一律從 `UHS/hourAnalysis.md` 讀回來延續，而非依賴 session 記憶。
- **排程設定對應**：對應的 Routine 應設為 `create_new_session_on_fire = true`（每次 fire 產生新 session），**不要**使用 `persist_session` / 固定 `persistent_session_id`。

---

## 1. 任務目標（Goal）

- 分析為什麼美股 **UHS（Universal Health Services, NYSE: UHS）** 的本益比（PE）長期 **< 8**、為什麼這麼低。
- 深入探討低本益比背後的成因，至少涵蓋：
  - 獲利品質、成長性疑慮、產業與市場情緒
  - 法遵／訴訟、政策風險（Medicaid、加州補充給付等）、資本結構與治理

---

## 2. 資料來源（Data Sources · 依序）

1. **前一輪的 `UHS/hourAnalysis.md`** — 作為延續與比對的基準（每次先讀回）。
2. **`UHS/` 資料夾**內的財報與輿情檔（10-K、10-Q、GoogleNews、Reddit、SeekingAlpha、X、Xueqiu、Official_IR 等）。
3. **網路搜尋（web search）** — 取得最新股價、PE、財報、新聞與市場動態，並與本地資料交叉驗證。

---

## 3. 研究深度（Research Depth）

- 進行 **deep research**：盡量搜尋、交叉驗證，資訊要新、要可驗證。
- 資料缺失時，**明確註記缺口與可能原因**（如財報尚未發布、資料庫延遲等）。
- **優先補齊前一輪仍缺的項目**（例如：5 年 ROE 完整年序、最新一季實績），逐輪把缺口補上。

---

## 4. 輸出規範（Output · 每次都要 optimize + rearrange）

- 分析結果 **update 到** `UHS/hourAnalysis.md`。
- **延續而非重寫**：於檔首新增一段「更新紀錄 + 時間戳記」，比對前一輪結論，補新資訊、修正舊觀點。
- **每次更新都要同步「優化與重新編排」內容（optimize & rearrange）**，讓 user 一眼看得懂：
  1. 檔首固定放「**最新結論摘要**」（現價、TTM/Forward PE、低 PE 主因 Top 3、目標價、下一催化事件）。
  2. 相同主題**合併去重**，不要讓同一觀點散落多段、也不要無限堆疊舊內容。
  3. 用**表格／條列**呈現數據與多空對照，段落簡潔、標題清楚。
  4. 過舊或已被推翻的內容**收斂或移除**，只保留「仍有效」與「有變化」的重點。

---

## 5. 收尾（Finalize）

- 每小時分析完就 **commit + push**，並 **merge 回 `master` 分支**（不必等整個 session 結束）。
- Commit 訊息寫清楚本輪更新重點（例如：補算 ROE 年序、更新 Q2 財報實績等）。
- **收尾前先檢查 `0-A. 執行期限`**：若已達 3 天（72 小時）上限，執行「到期動作」（標註已停止、停用 Routine、最後 commit/push），不再排下一輪。
