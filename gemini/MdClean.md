/boost /goal
# 分批清理公司 md 檔 — MdClean（Gemini 版）

> **一句話任務**：用 `gemini/MdClean.py` 把「repo 根目錄 → 各公司資料夾」底下的 `.md` 清成 **AI 好解析** 的格式並**直接覆寫原檔**；每輪只處理一批，抽查品質後，把本輪結果與下一輪清單寫進 `gemini/MdClean_symmary.md`，最後 git push。
>
> **清理目標**：只考慮「AI 看得懂」，不考慮人類閱讀；**不以縮小檔案為目的**，只移除零資訊量的雜訊、修復被拆碎的結構，並在檔頭加上 AI 導讀（文件類型、單位、頁碼標記、數字慣例）。
>
> **唯一狀態檔**：`gemini/MdClean_symmary.md`（下一輪清單、本輪結果、FAIL 清單、AI 觀察 ai-notes、歷次紀錄）。
>
> **執行模式**：`/boost /goal` 全自動。**嚴禁中途停下向使用者提問（禁止呼叫 `ask_question`）**，必須自主走完 Step 0 → Step 6。

---

## 🚨 不可違反規則（Invariants）

| # | 規則 | 違反後果 |
|:-:|:-----|:---------|
| 1 | **絕不清理 `hourAnalysisResult.md`**（腳本已硬性排除；AI 也不可手動改它） | 任務失敗 |
| 2 | **只動公司資料夾**：`History`、`Log`、`Prompt`、`gemini`、`*ScreenerResult`、`.claude`、`.agents`、根目錄檔案一律不碰 | 任務失敗 |
| 3 | **數字零遺失**：清理只能刪「頁碼、失效圖片路徑、cid 亂碼」；其餘任何數字都必須保留（腳本安全閘門會擋，FAIL 的檔不覆寫） | 捏造／遺失 = 任務失敗 |
| 4 | **不整份重寫大檔**：AI 不可用 `write_to_file` 重寫 >100 KB 的財報 md；大檔只能透過腳本清理 | 內容被截斷 = 任務失敗 |
| 5 | **單輪單批**：每次啟動只跑一批（預設 20 檔或 25 MB，先到先停），完成即結束 | — |
| 6 | **零阻塞**：任何錯誤（單檔例外、編碼問題）→ 記錄到 summary 後繼續，不可停下等人 | 停下 = 任務失敗 |
| 7 | **不改標記**：檔案第一行 `<!-- MdClean:v1 | sha1:… -->` 與 `<!-- AI-META … -->` 區塊不可手動編輯；`*_PublicOpinion.md` 內的 `<!-- body:start -->`、`<!-- source-file: … -->` 一律原樣保留 | 冪等失效 |
| 8 | **繁體中文**撰寫 summary 與 ai-notes（專有名詞首次附英文） | — |

---

## 工具對照表

| 動作 | 工具 |
|:-----|:-----|
| 讀本機檔案 | `view_file`（絕對路徑，大檔用行號範圍） |
| 修改小檔 / summary 的 ai-notes 區塊 | `replace_file_content` |
| 搜尋 | `grep_search` / `find_by_name` / `list_dir` |
| 執行指令 (Git / Python) | `run_command`（cwd = `d:\FinancialReport`，PowerShell） |
| 取系統時間 | `run_command`：`Get-Date -Format "yyyy/MM/dd HH:mm:ss"` |

> Python 指令：Windows 用 `python`；若找不到改用 `py -3`。腳本需 Python 3.10+，無第三方套件依賴。

---

## 執行流程總覽

```
Step 0  git pull 同步
  ↓
Step 1  讀 gemini/MdClean_symmary.md（下一輪清單、FAIL 清單、ai-notes）
  ↓
Step 2  python gemini\MdClean.py         ← 清理本批 + 自動覆寫 + 自動更新 summary
  ↓
Step 3  AI 抽查本批 OK 檔（品質檢查表）
  ↓
Step 4  處理 FAIL 檔（重試 / 判斷 / 記錄）
  ↓
Step 5  把觀察寫進 summary 的 ai-notes 區塊
  ↓
Step 6  git add / commit / push master，輸出精簡摘要
```

---

## Step 0 — 同步

```powershell
cd d:\FinancialReport
git pull origin master
```
pull 失敗（衝突）→ `git stash` 後再 pull，並把狀況寫進 ai-notes；不可停下。

## Step 1 — 讀狀態

1. `view_file d:\FinancialReport\gemini\MdClean_symmary.md`。
2. 記下：§1「下一輪要處理的 md 檔」、§3 FAIL 清單、§5 ai-notes（上一輪 AI 留下的待辦／觀察）。
3. summary 不存在 = 第一次執行，直接進 Step 2（腳本會自動建立）。
4. 想看全體狀態時（非必要）：`python gemini\MdClean.py --list`
   - 每行：`狀態  模式  大小  路徑`；狀態 = `NEW`（未清理）/ `MODIFIED`（清理後又被改或被 append）/ `OLD_VERSION`（規則已升版）/ `CLEAN`（跳過）。

## Step 2 — 執行清理（本批）

```powershell
python gemini\MdClean.py
```

- 腳本自動挑出待處理檔（依公司資料夾 → 檔名排序，取前 20 檔或累計 25 MB），逐檔清理 → 通過安全閘門才覆寫 → 更新 `gemini/MdClean_symmary.md`（§1 下一輪清單、§2 本輪結果、§3 FAIL、§6 歷次紀錄；§5 ai-notes 原樣保留）。
- 輸出最後一行 `MdClean done: OK=a FAIL=b SKIP=c`；有 FAIL 時 exit code = 1（**正常，不是中止訊號**，繼續 Step 3）。
- 可調參數（一般不需要）：`--max-files 10 --max-mb 15`；`--dry-run`（只驗證不寫檔）；`--file "<公司>/<檔名>.md"`（指定檔，可重複）。

## Step 3 — AI 抽查（本批每個 OK 檔都要看）

對 summary §2 的每個 `[OK]` 檔，`view_file` 看 **第 1–60 行** + **任挑 2 段含表格的區域**（各約 40 行），逐項檢查：

| # | 檢查項 | 合格標準 |
|:-:|:-------|:---------|
| Q1 | 檔頭 | 第一行是 `<!-- MdClean:v1 … -->`，接著 `<!-- AI-META … -->`，`doc_type_guess` / `unit_hints` 合理 |
| Q2 | 頁碼 | 原本的「- 5 -」「12/115」「ANNUAL REPORT 2025 87」已變成 `<!-- p.N -->`；重複頁首頁尾（公司名、EDINET提出書類…）只剩第一次出現 |
| Q3 | 表格 | 沒有整欄空白、沒有整列 `|  |  |`、表格中段沒有多餘 `| --- |`；`$`、`%`、`)` 已併回數字（`$17,364,829`、`46.6%`、`(134,194)`） |
| Q4 | 結構 | 10-K/10-Q 的 `PART` / `Item` 成為標題；日本 `第N部【…】`、`N【…】` 成為標題；台灣 `壹、` 成為標題 |
| Q5 | 雜訊 | 無失效圖片連結 `![](C:/…)`、無 `<br>`、無 `(cid:n)` 亂碼（應被一行說明註解取代）、全形英數已轉半形 |
| Q6 | 內容 | 抽查段落文字與數字和清理前一致（可用 `git diff --stat` 看規模；必要時 `git diff -- "<檔>"` 抽看幾段） |

- 全部合格 → 不需動作。
- 發現**腳本規則可修**的系統性問題（同類檔案都有）→ 記到 ai-notes（Step 5），並可依「規則修改流程」改 `MdClean.py`。
- 發現**單檔局部**問題且檔案 < 100 KB → 可用 `replace_file_content` 就地修正（不可改到任何數字；改完該檔 sha1 會不符 → 下一輪自動重跑一次，屬正常）。
- 清理結果比原檔更難懂（例如表格錯位、段落被錯誤接合）→ `git checkout -- "<檔>"` 還原，並把該檔與原因寫進 ai-notes，下一輪可用 `--no-join` 重試或加入排除清單。

## Step 4 — 處理 FAIL 檔

FAIL 的檔**原檔未被覆寫**。依原因處理：

| FAIL 原因 | 動作 |
|:----------|:-----|
| `數字 token 不一致` | 先 `python gemini\MdClean.py --file "<路徑>" --no-join --dry-run`；通過 → 去掉 `--dry-run` 正式跑；仍失敗 → 記 ai-notes（附「遺失/多出」的數字），不要手動清 |
| `文字字元保留率 < 98%` | 同上先試 `--no-join`；仍失敗 → 記 ai-notes |
| `非 UTF-8 編碼` | 不處理，記 ai-notes（需重新轉檔，交給 Convert2md 流程） |
| `例外：…` | 記 ai-notes（附例外訊息），下一輪人工/AI 修腳本 |

同一檔連續 2 輪 FAIL → 在 ai-notes 標記「建議加入 SKIP_FILES」並說明原因。

## Step 5 — 更新 ai-notes

用 `replace_file_content` 只改 `gemini/MdClean_symmary.md` 中 `<!-- ai-notes:start -->` 與 `<!-- ai-notes:end -->` 之間的內容（其他區塊由腳本產生，不要手改）。格式：

```markdown
- {YYYY-MM-DD}｜抽查 {n} 檔，合格 {m}｜問題：{一句話}｜建議：{規則或動作}
- 待辦：{下一輪 AI 需要先做的事；沒有就寫「無」}
```
- 只保留仍有效的觀察；已解決的待辦刪掉（ai-notes 保持 ≤ 30 行）。

## Step 6 — 提交

```powershell
git add -A -- . ":(exclude)**/hourAnalysisResult.md"
git status --short          # 確認沒有任何 hourAnalysisResult.md 被改到
git commit -m "MdClean: batch {YYYYMMDD-HHmm} OK={a} FAIL={b}"
git push origin master
```
push 失敗（網路）→ 重試 4 次（間隔 2s/4s/8s/16s）；遠端有新提交 → `git pull --rebase origin master` 後再 push。

**最終輸出（精簡摘要）**：本輪 OK/FAIL 數、總進度（CLEAN x / 全部 y）、下一輪第一個檔、ai-notes 新增重點。

---

## 附錄 A — 腳本清理規則（`gemini/MdClean.py` v1）

**模式判定（依檔名）**
- `light`：檔名含 `PublicOpinion`、`輿情`、`新聞`、`news`、`analysis`、`Official_IR`、`Reddit`、`Xueqiu` 等（AI 產出的筆記／輿情）→ 只做：刪控制字元與零寬字元、失效圖片連結、`(cid:n)` 亂碼、多餘空行與行尾空白；**不動結構與文字**。
- `report`：其餘（年報、季報、10-K/10-Q、有価証券報告書、台灣財報 F04/FE4/AI1/AIA/AIC…）→ 全套規則。

**report 模式規則（依序執行）**
1. 全形英數字／％／全形空白 → 半形（中日文標點不動）。
2. 失效圖片 `![alt](本機路徑)` → 刪除（有 alt 時留 `[image: alt]`）；`(cid:n)` 亂碼行 → 一行 `<!-- [MdClean] … -->` 說明。
3. pymupdf4llm 的 `<!-- Start of picture text -->…<!-- End of picture text -->` → `[picture-text] a / b / c`；若內容只有頁碼 → `<!-- p.N -->`。
4. `<br>`、`<sup>` 等 HTML 標籤 → 空白。
5. 表格：刪重複分隔列（pymupdf 碎表）、刪全空列／全空欄、儲存格去反引號與粗體、`$`/`NT$`/`RMB` 併入右側數字、`)`/`%` 併入左側數字、SEC「表頭欄＋數值欄」錯位對齊、單欄表格轉純文字、字距展開（「資  產」→「資產」）；以上反覆執行到不再變化。
6. 頁碼：`- 5 -`、`12/115`（分母固定）、`Page 5`、SEC 的「頁碼＋`---`」、以及「同模板重複 ≥5 次且只有一個遞增數字」的頁首頁尾（如 `ANNUAL REPORT 2025 87`）→ `<!-- p.N -->`。
7. 固定頁首頁尾（重複 ≥5 次、≥60% 緊鄰頁碼，如 `EDINET提出書類`、公司名）→ 保留第一次，其餘刪除。
8. 標題提升：`PART I`→`##`、`Item 1A.`→`###`、`第一部【】`→`##`、`第1【】`→`###`、`1【】`→`####`、`(1)【】`→`#####`、`壹、`→`##`；既有標題去掉 `**`。
9. 斷行接合（PDF 硬換行）：英文「上一行 ≥50 字、無句尾標點、下一行小寫開頭」；中日文「上一行 ≥28 字、以漢字結尾、下一行漢字開頭」；清單、表格、標題、註解不接。
10. 空白：連續空行壓成一行、行尾空白、表格與標題前後補空行（避免 GFM 把下一行吞進表格）。
11. 檔頭加 `<!-- MdClean:v1 | sha1:… -->` 與 `<!-- AI-META … -->`（公司、檔名、文件類型、期間、來源格式、單位提示、頁碼標記意義、負數與零的慣例、套用了哪些清理與次數）。

**安全閘門（每檔必過，否則 FAIL、不覆寫）**
- 數字 token 多重集合：原檔（全形轉半形、去反引號／HTML 標籤／註解）− 刻意移除部分（頁碼、圖片路徑、cid 行）＝ 清理後（去註解）。完全相等才算過。
- 文字字元（英文字母＋中日韓文字）保留率 ≥ 98%。
- 寫入採 `.tmp` → 原子取代。

**冪等**：同一檔清理兩次結果相同；已清理且未被修改的檔（sha1 相符）自動跳過。`*_PublicOpinion.md` 被 ArrangePublicOpinionMd 重寫檔頭後標記消失 → 自動回到待處理（正常）。

## 附錄 B — 規則修改流程（只有在發現系統性問題時）

1. 改 `gemini/MdClean.py`，並把 `VERSION` 改為下一版（`v1` → `v2`）。升版後所有已清理檔會變 `OLD_VERSION`，依批次自動重跑（新規則必須能處理「已被 v1 清理過」的檔案）。
2. 全量試跑（不寫檔）：`python gemini\MdClean.py --dry-run --max-files 9999 --max-mb 99999` → 必須 `FAIL=0`（或 FAIL 數不增加）。
3. 同步更新本檔「附錄 A」與 summary 的 ai-notes（寫明改了什麼、為什麼）。
4. 與當輪批次一起 commit。
