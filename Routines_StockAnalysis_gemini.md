/deepresearch 
/goal

# Routines — 每日輪替執行排程（Gemini 專用版）

> 本檔是 `Routines_StockAnalysis.md` 的 **Gemini 包裝層（wrapper）**。
> 流程本體不重複撰寫，一律沿用主檔；本檔**只做兩件事**：覆寫輸出檔名、指定 Gemini 執行環境。

---

## 全域參數 (Global Parameters)

| 參數 | 值 | 說明 |
| :--- | :--- | :--- |
| `OUTPUT_FILENAME` | **`hourAnalysisResult_gemini.md`** | **強制覆寫**主檔的 `hourAnalysisResult.md`，優先權高於主檔設定 |
| 執行模型 | **Gemini** | 主檔第 2 行的「使用 latest claude OPUS model」**不適用本檔，直接忽略** |
| Skill 路徑 | `.agents/skills/StockAnalysis/SKILL.md` | 內容同 `.claude/skills/StockAnalysis/SKILL.md`，本檔一律讀 `.agents/` 版本 |

---

## 執行流程 (Execution Flow)

1. **載入主檔**：讀取 `Routines_StockAnalysis.md`，取得完整執行流程（Step 1~5）與 `## 每日輪替表`。
2. **套用覆寫**：以上方「全域參數」覆寫主檔的同名設定，**覆寫後才開始執行**。
3. **依主檔執行**：完全按主檔的 Step 1~5 進行。
   - 取得今日「日」（1~31）→ 對照輪替表鎖定公司。
   - **無對應公司**→ 直接 skip 結束，不產生任何檔案、不 commit。
   - **有對應公司** → 帶入該列的 `COMPANY_NAME` / `MARKET` / `COMPANY_FOLDER` / `EXTRA_ANALYSIS`，搭配本檔覆寫後的 `OUTPUT_FILENAME`，載入並執行 `StockAnalysis` Skill。
4. **確認輸出**：確認 `<COMPANY_FOLDER>/hourAnalysisResult_gemini.md` 已更新 → 在對話中回覆分析報告。

---

## 輸出檔案規則（Output Guard · 強制）

- ✅ **只能寫入**：`<COMPANY_FOLDER>/hourAnalysisResult_gemini.md`（直接覆寫，不加日期後綴）。
- ❌ **禁止寫入**：`<COMPANY_FOLDER>/hourAnalysisResult.md` —— 該檔屬 Claude 版排程（`Routines_StockAnalysis.md`）的產出，兩邊可能同時執行，覆寫會造成資料互相衝突。
- 讀取上一輪基準檔時（Skill §2 資料來源第 1 項），同樣以 `hourAnalysisResult_gemini.md` 為準。
- Skill §6「正確性檢查」的基準檔（source of truth）亦為 `hourAnalysisResult_gemini.md`。

---

## 收尾 (Finalize)

- 依 Skill §7：分析完即 **commit + push** 並 merge 回 `master`。
- commit 前先 `git pull --rebase`，避免與 Claude 版排程的 commit 衝突。