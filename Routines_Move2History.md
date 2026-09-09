# Routines — 移動非輪值公司資料夾至 History (Move Non-Rotation Folders to History)

> 目的：讓根目錄只保留「仍在輪值表內」的公司資料夾。已從輪值表移除（不再追蹤）的公司，一律歸檔到 `History/`，避免根目錄膨脹與誤判。

## 全域參數 (Global Parameters)

- `ROTATION_FILE`：`Routines_CollectsentimentAndReports.md`（輪值表來源，唯一真實依據）
- `HISTORY_DIR`：`History`
- `EXCLUDE_DIRS`（非公司資料夾，永不搬移）：
  - `History`
  - `AnalysisResult`
  - `StkScreenerResult`
  - `Log`
  - `Prompt`
  - `gemini`
  - 任何以 `.` 開頭的隱藏資料夾（例如 `.git`、`.claude`、`.github`）

## 執行流程 (Execution Flow)

- **Step 1**：讀取 `ROTATION_FILE`，解析「每日輪替表」表格，取出第 4 欄 `本地資料夾名稱 (Folder)` 的所有值，去除反引號與空白，組成 `輪值資料夾集合`。
  - 忽略表頭列、分隔列，以及值為 `—` 的 Skip 列。
  - 同一個資料夾可能出現在多列（例如 `3445RS` 同時對應日股 3445 與中股 688432），視為同一項。
- **Step 2**：列出根目錄下所有第一層資料夾，扣除 `EXCLUDE_DIRS` 與隱藏資料夾，得到 `根目錄公司資料夾集合`。
- **Step 3**：計算差集 `待搬移 = 根目錄公司資料夾集合 - 輪值資料夾集合`。
  - 若差集為空 → 不做任何事，直接結束（回報「無需搬移」）。
- **Step 4**：反向檢查 `輪值資料夾集合 - 根目錄公司資料夾集合`。
  - 若不為空，代表輪值表列了但根目錄沒有的資料夾 → **只回報、不自動建立**（可能是新加入、尚未收集，或誤植於 `History/`）。
- **Step 5**：對 `待搬移` 內每個資料夾執行搬移：
  - 使用 `git mv "<FOLDER>" "History/<FOLDER>"`（保留 git 歷史）。
  - 若 `History/<FOLDER>` 已存在（同名衝突）→ **不覆蓋、不合併**，跳過並回報，交由人工處理。
- **Step 6**：驗證。
  - 確認根目錄不再有該資料夾、`History/<FOLDER>` 內檔案數與搬移前一致。
  - `git status` 應只有 renamed 記錄，不得出現 deleted 而無對應 added。
- **Step 7**：commit 並回報。
  - Commit message 範例：`chore: move non-rotation company folders to History`
  - 回報內容須包含：搬移清單（含檔案數）、跳過清單與原因、Step 4 的反向檢查結果。

## 安全準則 (Safety Rules)

1. **只搬移、不刪除**：任何情況下都不得 `rm` 公司資料夾或其內檔案。
2. **輪值表是唯一依據**：不得依「資料夾看起來很舊」「檔案很少」等主觀理由自行判斷搬移。
3. **只處理第一層**：不遞迴搬移 `History/` 內部或公司資料夾內的子資料夾。
4. **衝突即停**：同名衝突一律跳過並回報，不做自動改名或合併。
5. **搬移後不改內容**：不修改被搬移資料夾內任何檔案。

## 參考：本次（2026-09-09）執行結果

| 資料夾 | 檔案數 | 動作 | 原因 |
| :--- | :---: | :--- | :--- |
| `00386中石化` | 7 | 移至 `History/` | 不在輪值表 |
| `00857中石油` | 7 | 移至 `History/` | 不在輪值表 |
| `6361荏原製作所` | 7 | 移至 `History/` | 不在輪值表 |
| `INGR宜瑞安` | 2 | 移至 `History/` | 不在輪值表 |

- 反向檢查（輪值表有、根目錄無）：無。
- 同名衝突：無。
