---
name: edinet
description: 用金融廳 EDINET API v2 下載日股（含 J-REIT 投資法人）的有価証券報告書（年報）、半期報告書／四半期報告書（季報）完整版 PDF，存進 repo 的公司資料夾（沿用 collectStk 命名、自動認得既有舊檔名），再用 Convert2md 轉 Markdown 並驗證。輸入證券代碼（如 3445、7203、2971）。API key 錯誤會寫 Log/edinet_error.md；每次執行完若發現 skill 文件或腳本有錯，必須依 §9 自動修正。
---
# edinet — 日股年報／季報下載 → Markdown

> **一句話**：證券代碼 → EDINET コード → 只掃「法定申報窗口」的每日提出書類清單 → 下載最新 2 份年報 + 1 份半期報（J-REIT：3 份有報）完整 PDF → `Convert2md` 轉 `.md` → `verify` 驗證 → 寫執行報告 → **§9 自我修正**。
> 腳本：`.claude/skills/edinet/scripts/edinet.py`（只用 Python 標準函式庫；Windows／macOS／Linux／Claude Code 雲端皆可）。Gemini 用 `.agents/skills/edinet/`（內容必須與 `.claude` 版完全相同，`selftest` 會檢查）。

## 1. AI 執行流程（照順序做，不可跳步）

| 步驟 | 指令／動作 | 失敗時 |
| :--- | :--- | :--- |
| 0 | `python .claude/skills/edinet/scripts/edinet.py selftest --offline`（1 秒） | 有 FAIL → 先做 §9 修好再繼續 |
| 1 | `python .claude/skills/edinet/scripts/edinet.py checkkey` | 結束碼 2 = key 錯誤 → 已自動寫 `Log/edinet_error.md`（§4）→ 告訴使用者修法，**改走 AGENTS.md §4.2 D/F**（IR Bank、Ullet、Futu），不要卡住 |
| 2 | `python .claude/skills/edinet/scripts/edinet.py list --code {代碼}` | 確認公司、期別、預定檔名都對；對到多家 → 改用 4 碼代碼或 EDINET コード |
| 3 | `python .claude/skills/edinet/scripts/edinet.py download --code {代碼}` | 已涵蓋的期別自動略過（§5.2）；找不到公司資料夾會自動建 `{代碼}{社名}` |
| 4 | 若步驟 3 印出 `CONVERT2MD_SCOPE=...` → 執行 **`Convert2md` skill**，`<SCOPE>` 填該資料夾絕對路徑 | 沒印 = 沒有新 PDF，跳過 4、5 |
| 5 | `python .claude/skills/edinet/scripts/edinet.py verify --code {代碼}` | ❌ 的檔案：CID 亂碼 → 改抓英文版（`--format english`）或 IR Bank；公司名對不上 → 刪掉重抓 |
| 6 | 回報使用者：讀 `Log/edinet_Summary_{YYYYMMDD}.md`，寫明找到哪些期別、docID、提出日、略過／下載／缺口與原因（AGENTS.md §4.3） | — |
| 7 | **§9 自我修正檢查**（每次都要做） | — |
| 8 | `git add` 公司資料夾新 `.md`、`Log/edinet_*`、（若有修正）skill 檔案 → commit → push | — |

> Convert2md 成功後會刪掉來源 PDF，只留 `.md`；下次 `download` 看到 `.md` 就會略過該期別。

## 2. 指令參考

| 子指令 | 用途 | 範例 |
| :--- | :--- | :--- |
| `selftest` | 自我檢查：命名邏輯、申報窗口、既有檔判定、SKILL.md↔CLI 參數一致、`.claude`/`.agents` 鏡像、`.gitignore`；不加 `--offline` 再測 API key 與コードリスト | `edinet.py selftest` |
| `checkkey` | 檢查 key 是否有效（不印 key，只印來源與格式檢查） | `edinet.py checkkey` |
| `lookup` | 用證券代碼／EDINET コード／公司名（日文、英文、ヨミ）找公司 | `edinet.py lookup トヨタ` |
| `list` | 列出 EDINET 上的年報/季報與預定檔名，不下載 | `edinet.py list --code 7203` |
| `download` | 下載 + 寫執行報告 | `edinet.py download --code 2971` |
| `verify` | Convert2md 之後驗證 `.md`（存在、≥10KB、CID < 50、前 2 萬字有公司名／代碼） | `edinet.py verify --code 2971` |

`list` / `download` 參數：

- `--annual N` / `--periodic M`：年報、季/半期報份數。預設一般公司 2 / 1，**J-REIT（投資法人）自動 3 / 0**。
- `--format pdf,xbrl,csv,english,attach`：逗號分隔多種（預設 `pdf` = 完整版報告書）。`csv` 是 XBRL→CSV 財務數據（zip），做數字分析最好用；`english` 是英文版（多數公司沒有）。
- `--out DIR`：指定輸出資料夾。不填 → repo 根目錄下「代碼開頭、下一字不是數字」的唯一資料夾（如 `3445RS`）；找不到就自動建 `{代碼}{社名}`（加 `--no-create` 改為報錯）。
- `--ticker T`：檔名用的代碼（預設證券代碼前 4 碼）。
- `--days N`：最多往回幾天（預設 800）。
- `--full-scan`：不用申報窗口，逐個平日全掃（公司變更決算期、延期提出時用）。
- `--include-amendments`：一併下載訂正報告書（檔名加 `_Amend{docID}`；會自動全掃）。
- `--force`：已存在也重抓。
- `--workers N`：平行數（預設 4；限流由全域節流控制，不必調）。

結束碼：`0` 成功、`1` 一般錯誤、`2` API key 錯誤、`3` 腳本 bug（SCRIPT_BUG）。

## 3. API key 放哪裡

**絕對不要**把 key 寫進會被 commit 的檔案（`.claude/settings.local.json` **有被 git 追蹤**，不能放）。腳本依序讀取，找到即停：

1. **環境變數 `EDINET_API_KEY`**（推薦）
   - Windows（永久，設完重開終端機／Claude）：`setx EDINET_API_KEY "你的key"`
   - macOS / Linux：`~/.bashrc` 或 `~/.zshrc` 加 `export EDINET_API_KEY="你的key"`
   - 或**使用者層級** `~/.claude/settings.json`（不在 repo 內）：`{"env": {"EDINET_API_KEY": "你的key"}}`
2. 環境變數 `EDINET_API_KEY_FILE` 指向的檔案。
3. `.claude/skills/edinet/.env` 或 `.agents/skills/edinet/.env`（`.gitignore` 已排除 `.env`）：複製 `.env.example` 為 `.env`，填 `EDINET_API_KEY=你的key`。
4. `~/.config/edinet/.env`（同格式，跨 repo 共用）。
5. 都沒有 → 送佔位值，由 **Claude Code 雲端環境的網路密鑰**注入（host `api.edinet-fsa.go.jp`、header `Ocp-Apim-Subscription-Key`）。雲端已設好，`checkkey` 會顯示「來源：雲端網路密鑰（代理注入）」。換 key：claude.ai 雲端環境設定 → Network secrets；或請 Claude 呼叫 `request_credential`。
   - ⚠️ Network secret **只綁在存它的那個環境**（目前是 `FinancialReport` 環境 `env_01VgVNgx…`）。排程任務若跑在別的環境（2026-11-26 實例：排程任務跑在 `env_01QaMJgj…`）就會 401 `invalid subscription key`。修法：把排程任務的環境改成 `FinancialReport`，或在該環境也加這筆 Network secret。

key 申請：EDINET 首頁 →「API」→ API キー発行（免費；需帳號 + 手機簡訊認證；重新發行後舊 key 立即失效）。EDINET key 通常是 32 碼 0-9a-f，腳本會檢查格式（只報長度，不印內容）。

## 4. 錯誤報告 `Log/edinet_error.md`

任何錯誤都由腳本自動寫入（最新在最上面，保留 50 筆；**永遠不含 key 本身**）。AI 依種類處理：

| 種類 | 意義 | AI 要做的事 |
| :--- | :--- | :--- |
| `AUTH_INVALID_KEY`（401）/ `AUTH_FORBIDDEN`（403） | **key 錯誤／失效／沒設** | 把報告裡的「可能原因／修正步驟」轉告使用者；本次改走 IR Bank／Ullet／Futu；**不要**自己改 key 或把 key 寫進 repo |
| `RATE_LIMIT` | EDINET 限流（JSON 內 `StatusCode 429`，HTTP 仍是 200） | 腳本已自動退避重試 6 次仍失敗 → 等 5–10 分鐘重跑（清單有快取） |
| `NETWORK` / `API_ERROR` | 連線或 EDINET 端異常 | 重跑一次；仍失敗 → 替代來源，並在回報寫明 |
| `NOT_FOUND` / `AMBIGUOUS` | 代碼找不到／對到多家 | `lookup` 確認後用正確代碼 |
| `SCRIPT_BUG`（結束碼 3，附 traceback） | 腳本本身有錯 | **§9 自我修正** |
| `SELFTEST_FAIL` | selftest 失敗 | **§9 自我修正** |

## 5. 命名與既有檔判定

### 5.1 檔名（沿用 collectStk §7.1）

| 文件 | 檔名 | 例 |
| :--- | :--- | :--- |
| 有価証券報告書（一般） | `{代碼}_AnnualReport_{FY}` | `7203_AnnualReport_2026` |
| 有価証券報告書（J-REIT 6 個月期） | `{代碼}_AnnualReport_{YYYY}{Mon}` | `2971_AnnualReport_2026Jul` |
| 半期報告書 | `{代碼}_Quarter_{FY}H1` | `7203_Quarter_2027H1` |
| 四半期報告書（~2024） | `{代碼}_Quarter_{FY}Q{N}` | `7203_Quarter_2024Q3` |
| 訂正報告書 | 原檔名 + `_Amend{docID}` | `7203_AnnualReport_2026_AmendS100XXXX` |
| 非 pdf 格式 | 檔名 + `_{format}.zip` | `3445_AnnualReport_2025_csv.zip` |

- `{FY}` = 會計年度**結束年**（3 月決算公司 2026/4–9 的半期報 → `2027H1`）。
- ⚠ EDINET 對**半期報告書**回傳的 `periodStart~periodEnd` 是**整個會計年度**（例：`2026-04-01~2027-03-31`），不是半期（2026-11 實測）。命名已依此處理，不要「修正」成用半期末。

### 5.2 已涵蓋就略過（不重複下載）

同資料夾有下列任一檔（`.pdf` 或 `.md`）就視為該期別已存在：
- 新命名；舊命名 `{代碼}_annual_{FY}`、`{代碼}_quarter_…`、`{代碼}_QuarterlyReport_…`；半期報也認 `{代碼}_Quarter_{FY}Q2`、`{代碼}_interim_{FY}`；
- 日文原檔名：含「有価証券報告書／半期報告書／四半期報告書」、不含「訂正」、且數字裡有期末日 `YYYYMMDD`（如 `202606有価証券報告書－第39期(20250401－20260331).md`）。
- **`.md` 還要看檔頭內容**：檔頭最早出現的文件名稱必須是同一種（有価証券報告書／半期報告書／四半期報告書）才算已有。舊流程常把**決算短信**存成 `_Quarter_{FY}Q2`、把**資産運用報告**或英文決算資料存成 `_AnnualReport_`——它們是摘要，不能頂替詳細版。不能只搜「有沒有出現」：決算短信封面固定有「半期報告書提出予定日」。
- 目標檔名已被別種文件佔用 → 新檔存成 `{檔名}_EDINET.pdf`（例 `2971_AnnualReport_2026Jul_EDINET.pdf`），兩份並存、不覆蓋。

## 6. 必知限制

- **2024/4 起四半期報告書廢止**：上市公司每年只有 1 份**半期報告書**（160）。第 1、第 3 季只有 TDnet **決算短信**，**不在 EDINET** → 最新單季請另抓（collectStk §7.3：株探、IR Bank、公司 IR）。腳本會在報告提醒。
- **J-REIT**：每 6 個月一份有価証券報告書，沒有半期報 → 自動 `--annual 3 --periodic 0`。
- 取下（withdrawn）、非公開文件自動排除。
- EDINET PDF 由 XBRL 產生，`convert_pdf_to_markdown` 實測 CID 0（9435 半期報 2026-11）。

## 7. 速度、快取、限流

- **申報窗口掃描**（預設）：有報 = 期末 +30～+105 天、半期／四半期報 = 期末 +15～+50 天（法定期限 3 個月／45 天），只掃平日（週末清單恆為 0 件）；份數不夠才自動補掃窗口外日期。冷快取約 30–40 秒（舊版逐日全掃 800 天會 429 當掉）。
- 每日清單快取在 `~/.cache/edinet/lists/`（`EDINET_CACHE_DIR` 可改），7 天前的不重抓；コードリスト 7 天更新一次。
- 全域節流約 5 req/s（`EDINET_MIN_INTERVAL` 秒/請求，預設 0.2）；遇 429／5xx 全部執行緒一起退避（5→10→20→40→60 秒）。
- 執行報告：`Log/edinet_Summary_{YYYYMMDD}.md`（同日多次 append）；上次 download 紀錄：`~/.cache/edinet/last_run.json`（給 `verify` 用）。

## 8. docTypeCode 對照

| code | 文件 | 本 skill 分類 |
| :--- | :--- | :--- |
| 120 | 有価証券報告書 | 年報 |
| 130 | 訂正有価証券報告書 | 訂正（需 `--include-amendments`） |
| 140 | 四半期報告書（~2024） | 季報 |
| 150 | 訂正四半期報告書 | 訂正 |
| 160 | 半期報告書 | 季報（半期） |
| 170 | 訂正半期報告書 | 訂正 |

API 文件：EDINET API 仕様書 v2 `https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html`。

## 9. 執行後自我修正（強制，每次執行完都要做）

**觸發條件**（任一成立就要修）：
1. `Log/edinet_error.md` 本次新增 `SCRIPT_BUG` 或 `SELFTEST_FAIL`；
2. `selftest` 有 FAIL；
3. 實際行為與本文件不符（例：API 回傳欄位／限流方式變了、檔名或 FY 算錯、既有檔沒被認出而重複下載、文件寫的參數不存在、步驟順序不對、Convert2md 介面變了）；
4. 使用者指出本 skill 的錯誤。

**修正流程**：
1. 找出根因，直接改 `scripts/edinet.py` 和／或 `SKILL.md`（必要時含 `.env.example`）。修的是錯，不是繞過：**不可**刪掉或放寬 selftest 檢查來求綠燈、**不可**把 key 寫進任何檔案。
2. 若是新發現的行為（如 API 欄位語意），在 `selftest` 補一個測試案例鎖住它。
3. 跑 `edinet.py selftest`（線上）→ 全部 PASS。
4. 把 `.claude/skills/edinet/` 整個複製到 `.agents/skills/edinet/`（`.env` 除外），再跑一次 `selftest` 確認鏡像一致。
5. 在 §10 變更紀錄加一行：日期、問題、修法。
6. 重跑剛才失敗的步驟，確認修好；commit 訊息以 `fix(edinet):` 開頭並 push。
7. 修不好（例如 EDINET 端故障、需要使用者的 key）→ 不要硬改，回報使用者並在 `Log/edinet_error.md` 留下紀錄。

若問題出在 `Convert2md` skill，同樣修正 `.claude/skills/Convert2md/SKILL.md` 與 `.agents/skills/Convert2md/SKILL.md`（兩份保持相同）。

## 10. 變更紀錄

- 2026-11-26 v2.0.1：
  - 修：既有檔只看檔名 → `4979_Quarter_2026Q2.md`（決算短信）被當成半期報告書、`2971_AnnualReport_2026Jul.md`（資産運用報告）被當成有報，詳細版永遠不下載。改為檢查 `.md` 檔頭文件種類；同名別種文件時另存 `_EDINET`；selftest 加 5 個案例鎖住。

- 2026-11-26 v2.0.0：
  - 修：EDINET 以 HTTP 200 + JSON `StatusCode 429` 限流時舊版直接當掉 → 全域節流 + 退避重試。
  - 修：逐日全掃 800 天太慢 → 只掃法定申報窗口與平日，不足才補掃（冷快取 7203：32 秒、142 次請求、0 次 429）。
  - 修：日文原檔名（如 `202606有価証券報告書－第39期(…)`）與舊命名沒被認出 → 會重複下載。
  - 修：Windows 主控台（cp950）印日文 `UnicodeEncodeError` → stdout/stderr 改 UTF-8。
  - 修：下載檔權限 0600 → 依 umask 設成一般權限；寫檔改原子寫入，並驗證 PDF 檔頭／大小、ZIP 合法性。
  - 新：API key 錯誤與所有錯誤寫 `Log/edinet_error.md`（含原因與修法，不含 key）；未預期例外記 `SCRIPT_BUG` + traceback。
  - 新：`selftest`、`verify` 子指令；`Log/edinet_Summary_{YYYYMMDD}.md` 執行報告；J-REIT 自動 3/0；新公司自動建資料夾；`--full-scan`、`--no-create`。
  - 新：`.agents/skills/edinet/` 鏡像（Gemini）；§9 自我修正流程。
