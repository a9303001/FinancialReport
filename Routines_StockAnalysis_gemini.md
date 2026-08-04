/deepresearch 
/goal

# Routines — 每日輪替執行排程（Gemini 專用版）

> 本檔是 `Routines_StockAnalysis.md` 的 **Gemini 包裝層（wrapper）**。
> 流程本體不重複撰寫，一律沿用主檔；本檔**只做三件事**：覆寫輸出檔名、指定 Gemini 執行環境、把讀寫位置改到 **Google Drive**。

---

## 儲存位置 (Storage · Google Drive)

**這個排程沒有 git、也不用 GitHub。讀檔、寫檔一律在 Google Drive。**

| 項目 | 位置 |
| :--- | :--- |
| 根資料夾 | `我的雲端硬碟/FinancialReport` |
| 本檔（規格） | `FinancialReport/Routines_StockAnalysis_gemini.md` |
| 主檔（流程本體 + 輪替表） | `FinancialReport/Routines_StockAnalysis.md` |
| 上一輪基準檔（讀） | `FinancialReport/<COMPANY_FOLDER>/hourAnalysisResult_gemini.md` |
| 本次輸出檔（寫） | `FinancialReport/<COMPANY_FOLDER>/hourAnalysisResult_gemini.md`（同一個檔，直接覆寫） |

- 寫檔 = 用**同一個 `fileId` 覆寫（update）**，MIME 為 `text/markdown`（⛔ 不要存成 Google 文件格式）。
- 🔴 **一次執行只認一個 `fileId`。** ⛔ 禁止用檔名重複「新建」— 那會在公司資料夾裡堆出 `hourAnalysisResult_gemini(1).md`、`(2).md`，下次讀基準檔就分不出哪個才是本尊。
- 找到多個同名檔 → 取 `modifiedTime` **最新**的那份為準，其餘在 chat 列出請人工刪除，⛔ 不要自己刪。
- ⛔ **不做 `git commit` / `push` / `merge`，也不做 `git pull --rebase`。** 這幾項在 Google Drive 沒有對應動作。

---

## 🛑 Google Drive 失敗處理（強制 · 直接放棄）

**只要任何一步 Google Drive 讀或寫失敗，就直接放棄本次執行。**

| 失敗的是哪一步 | 怎麼做 |
| :--- | :--- |
| 讀不到本檔 / 主檔 / 輪替表 | **立刻停止**，不進入分析 |
| 讀不到上一輪基準檔（但檔案應該存在） | **立刻停止**，⛔ 不要當成「第一次執行」從零重寫，那會蓋掉既有累積 |
| 寫不回輸出檔（權限不足 / 空間已滿 / 授權過期 / 逾時） | **立刻停止**，本次分析結果直接捨棄 |

**放棄時只做一件事**：在 chat 寫明一行，說清楚**哪一步失敗**、**錯誤訊息**、**試過的資料夾與檔名**。

```
⚠️ 本次放棄執行 — Google Drive <讀/寫> 失敗：<錯誤訊息>
   目標：FinancialReport/<COMPANY_FOLDER>/hourAnalysisResult_gemini.md
```

**⛔ 明確禁止的「補救」行為（一律不准做）**：

- ⛔ **不建備援檔、不另存新檔名**（例如加日期後綴、加 `_backup`）。
- ⛔ **不改用其他儲存位置**（本機、其他資料夾、GitHub、貼進 chat 當備份都不行）。
- ⛔ **不重試到天亮**：同一步最多原樣重送 1 次，還是失敗就放棄。
- ⛔ **不要假裝成功**，也不要只回分析結果卻不講存檔失敗。

> 為什麼直接放棄？這是**每日輪替**排程，一天一家公司。今天沒跑成，明天照輪替表繼續，成本很低；相對地，半套的補救（另存新檔、換位置存）會讓下一輪讀到錯的基準檔，污染往後每一輪的累積。**寧可整天不跑，也不要留下一個來源不明的檔案。**

---

## 全域參數 (Global Parameters)

| 參數 | 值 | 說明 |
| :--- | :--- | :--- |
| `OUTPUT_FILENAME` | **`hourAnalysisResult_gemini.md`** | **強制覆寫**主檔的 `hourAnalysisResult.md`，優先權高於主檔設定 |
| 執行模型 | **Gemini** | 主檔第 2 行的「使用 latest claude OPUS model」**不適用本檔，直接忽略** |
| 儲存位置 | **Google Drive** | 覆寫 Skill §7 的 commit / push / merge，改為寫回 Drive（見上方「儲存位置」） |
| Skill 路徑 | `.agents/skills/StockAnalysis/SKILL.md` | 內容同 `.claude/skills/StockAnalysis/SKILL.md`，本檔一律讀 `.agents/` 版本 |

---

## 執行流程 (Execution Flow)

0. **讀本檔**：先從 Google Drive 讀 `FinancialReport/Routines_StockAnalysis_gemini.md`，依讀到的這一版執行（⛔ 不要憑記憶做）。讀不到 → 依「Google Drive 失敗處理」放棄。
1. **載入主檔**：從 Google Drive 讀 `FinancialReport/Routines_StockAnalysis.md`，取得完整執行流程（Step 1~5）與 `## 每日輪替表`。讀不到 → 放棄。
2. **套用覆寫**：以上方「全域參數」覆寫主檔的同名設定，**覆寫後才開始執行**。
3. **依主檔執行**：完全按主檔的 Step 1~5 進行。
   - 取得今日「日」（1~31）→ 對照輪替表鎖定公司。
   - **無對應公司** → 直接 skip 結束，不產生任何檔案、**不寫入 Google Drive**。
   - **有對應公司** → 帶入該列的 `COMPANY_NAME` / `MARKET` / `COMPANY_FOLDER` / `EXTRA_ANALYSIS`，搭配本檔覆寫後的 `OUTPUT_FILENAME`，載入並執行 `StockAnalysis` Skill。
4. **確認輸出**：用同一個 `fileId` 重讀 Google Drive 上的 `FinancialReport/<COMPANY_FOLDER>/hourAnalysisResult_gemini.md`，確認更新日期是今天 → 在對話中回覆分析報告。驗證不過 → 依「Google Drive 失敗處理」放棄。

---

## 輸出檔案規則（Output Guard · 強制）

- ✅ **只能寫入**：Google Drive 的 `FinancialReport/<COMPANY_FOLDER>/hourAnalysisResult_gemini.md`（直接覆寫，不加日期後綴）。
- ❌ **禁止寫入**：`<COMPANY_FOLDER>/hourAnalysisResult.md` —— 該檔屬 Claude 版排程（`Routines_StockAnalysis.md`）的產出，兩邊可能同時執行，覆寫會造成資料互相衝突。
- 讀取上一輪基準檔時（Skill §2 資料來源第 1 項），同樣以 Google Drive 上的 `hourAnalysisResult_gemini.md` 為準。
- Skill §6「正確性檢查」的基準檔（source of truth）亦為 Google Drive 上的 `hourAnalysisResult_gemini.md`。

---

## 收尾 (Finalize)

- 🔴 **覆寫 Skill §7**：Skill §7 寫的「commit + push + merge 回 `master`」**不適用本檔**，直接忽略。
- 分析完即把整份 `hourAnalysisResult_gemini.md` **覆寫回 Google Drive** 的 `FinancialReport/<COMPANY_FOLDER>/` 底下（同一個 `fileId`）。
- 寫入內容一律是**整份檔案**（Drive 覆寫是整檔取代，不是附加）；只寫片段 = 其餘內容被當成刪除。
- 寫完依「執行流程」第 4 項重讀驗證，確認真的寫進去了。
- 兩版排程的檔名不同（Claude 版 `hourAnalysisResult.md`／Gemini 版 `hourAnalysisResult_gemini.md`），**不會互相覆蓋**，因此不需要任何同步或衝突處理動作。
- 寫入或驗證失敗 → **直接放棄，不做備援**（見上方「Google Drive 失敗處理」）。
