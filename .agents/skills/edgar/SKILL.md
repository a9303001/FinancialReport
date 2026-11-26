---
name: edgar
description: 用 SEC EDGAR 官方 API 下載美股（含 ADR／外國發行人）年報 10-K／20-F／40-F 與季報 10-Q／6-K 完整版，存進 repo 的公司資料夾（沿用 collectStk 命名、自動認得既有舊檔名與檔頭內容），再用 Convert2md（--html）轉 Markdown 並驗證。輸入 ticker 或 CIK（如 UHS、CF、EVTC、TLK）。被 SEC 擋會寫 Log/edgar_error.md；每次爬完必須依 §9 把學到的經驗寫回 references/lessons.md、company_hints.json 或腳本，下次直接用。
---
# edgar — 美股年報／季報下載 → Markdown

> **一句話**：ticker → CIK → submissions 申報清單 → 選最新 2 份年報 + 1 份季報（外國發行人：從大型 6-K 的附件找最新一期財報）→ 下載 HTML → `Convert2md --html` 轉 `.md` → `verify` 驗證、補來源標頭 → 寫執行報告 → **§9 經驗學習與自我修正**。
> 腳本：`.claude/skills/edgar/scripts/edgar.py`（只用 Python 標準函式庫；Windows／macOS／Linux／Claude Code 雲端皆可）。HTML→MD 轉換器在 `Convert2md/scripts/html2md.py`。Gemini 用 `.agents/skills/edgar/`（內容必須與 `.claude` 版完全相同，`selftest` 會檢查）。

## 1. AI 執行流程（照順序做，不可跳步）

下文 `G` = `python .claude/skills/edgar/scripts/edgar.py`。

| 步驟 | 指令／動作 | 失敗時 |
| :--- | :--- | :--- |
| 0 | **先讀 `references/lessons.md`**（經驗庫，1 分鐘）；本公司在「B. 公司特例」有寫的照做 | — |
| 1 | `G selftest --offline`（1 秒） | 有 FAIL → 先做 §9 修好再繼續 |
| 2 | `G checkua` | 結束碼 2 = 被 SEC 擋（`BLOCKED`，已寫 `Log/edgar_error.md`）→ 告訴使用者修法（§3），本次改走 collectStk §7.3 美股的其他來源 |
| 3 | `G list --code {TICKER}` | 確認公司、期別、預定檔名、`[本機已有 …]`；對到多家 → 改用 CIK；查無 → `G lookup 公司名` |
| 4 | `G download --code {TICKER}` | 已有的期別自動略過（§5.2）；找不到資料夾自動建 `{TICKER}/` |
| 5 | 若印出 `CONVERT2MD_SCOPE=...` → 執行 **`Convert2md` skill**，`<SCOPE>` 填該資料夾、`scan_pending.py` 加 **`--html`**（有印 `CONVERT2MD_HTML=1` 時必加） | 沒印 = 沒有新檔，跳過 5、6 |
| 6 | `G verify --code {TICKER}` | ❌ 照訊息處理：殘留標籤 → 修 html2md（§9）；表單／期末日不符 → 刪掉 `--force` 重抓 |
| 7 | 回報使用者：讀 `Log/edgar_Summary_{YYYYMMDD}.md`，寫明期別、accession、提交日、略過／下載／缺口與原因（AGENTS.md §4.3）、最新流通股數 | — |
| 8 | **§9 經驗學習與自我修正**（每次都要做，看報告的「本次觀察」與印出的 `LEARN:` 行） | — |
| 9 | `git add` 公司資料夾新 `.md`、`Log/edgar_*`、skill 變更（含 `.agents` 鏡像）→ commit → push | — |

> Convert2md 成功後會刪掉來源 `.htm`，只留 `.md`；下次 `download` 看到 `.md` 就略過該期別。

## 2. 指令參考

| 子指令 | 用途 | 範例 |
| :--- | :--- | :--- |
| `selftest` | 自我檢查：FY／季別命名、6-K 期別判斷、既有檔判定、html2md、SKILL.md↔CLI 一致、`.claude`/`.agents` 鏡像、`.gitignore`；不加 `--offline` 再測 SEC 連線 | `edgar.py selftest` |
| `checkua` | 檢查 User-Agent 與 SEC 連線 | `edgar.py checkua` |
| `lookup` | 用 ticker／CIK／公司名找公司 | `edgar.py lookup "universal health"` |
| `list` | 列出要抓的年報／季報、預定檔名、本機是否已有，不下載 | `edgar.py list --code UHS` |
| `download` | 下載 + 寫執行報告 | `edgar.py download --code EVTC` |
| `verify` | Convert2md 後驗證 `.md`（存在、≥10KB、CID < 50、殘留 HTML/XBRL 標籤 < 50、前 2 萬字有公司名／CIK、檔頭 FORM 與期末日相符）＋補來源標頭＋把公司資訊寫進 `company_hints.json` | `edgar.py verify --code EVTC` |
| `lesson` | 寫一條經驗到 `references/lessons.md`（同 key 改寫、自動同步 `.agents`） | `edgar.py lesson --section company --key "TLK 6-K" --text "…"` |
| `hint` | 設定公司特例（`company_hints.json`，`download` 自動套用） | `edgar.py hint --code TM --set folder=7203Toyota` |

`list` / `download` 參數：

- `--annual N` / `--periodic M`：年報、季報份數（預設 2 / 1）。
- `--days N`：年報／10-Q 往回幾天（預設 800）；6-K 固定看最近 400 天。
- `--out DIR`：輸出資料夾。不填 → `company_hints.json` 的 `folder` → repo 根目錄名稱 = ticker（或 ticker 後接中文，如 `TLK印尼電信`）的唯一資料夾；都沒有就自動建 `{TICKER}`（加 `--no-create` 改為報錯）。
- `--ticker T`：檔名用的代碼（預設 SEC ticker；`BRK-B` 這類照 SEC 寫法）。
- `--include-amendments`：一併下載 10-K/A、10-Q/A、20-F/A（檔名加 `_Amend{accession}`）。
- `--force`：已存在也重抓。

`hint --set` 可用的 key：`folder`（資料夾名）、`sixk_min_size`（6-K 候選最小 bytes，預設 400000）、`sixk_doc_type`（偏好的 6-K 附件類型，如 `EX-99.2`）；`--note` 寫一句備註。value 留空 = 刪除。

結束碼：`0` 成功、`1` 一般錯誤、`2` 被 SEC 擋（BLOCKED）、`3` 腳本 bug（SCRIPT_BUG）。

## 3. User-Agent（SEC 規定）

SEC 要求自動程式宣告 `名稱 email`，全站 ≤ 10 req/s（腳本預設 0.15 秒/請求，約 6.7 req/s；`EDGAR_MIN_INTERVAL` 可調）。不需要 API key。腳本依序讀取：

1. 環境變數 `SEC_EDGAR_USER_AGENT`（與 `sec-edgar-mcp` 共用同一個變數）
2. `.claude/skills/edgar/.env`、`.agents/skills/edgar/.env`、`~/.config/edgar/.env`（複製 `.env.example` 填寫；`.env` 已被 `.gitignore` 排除，**含個人 email，不要 commit**）
3. 預設通用值（2026-11 實測可用；若開始被擋就改用 1. 或 2.）

## 4. 錯誤報告 `Log/edgar_error.md`

| 種類 | 意義 | AI 要做的事 |
| :--- | :--- | :--- |
| `BLOCKED`（HTTP 403 或 SEC 封鎖頁） | UA 沒宣告／被判定超速（封鎖約 10 分鐘） | 把報告的修正步驟轉告使用者；本次改走其他來源；**不要**連續重試 |
| `RATE_LIMIT` / `NETWORK` / `API_ERROR` | 限流、連線、SEC 端異常 | 重跑一次（清單有快取）；仍失敗 → 其他來源並寫明 |
| `NOT_FOUND` / `AMBIGUOUS` | 代碼找不到（未在 SEC 註冊的 ADR，如 HEGIY）／對到多家 | `lookup` 確認，或改用 CIK |
| `SCRIPT_BUG`（結束碼 3，附 traceback） | 腳本本身有錯 | **§9 自我修正** |
| `SELFTEST_FAIL` | selftest 失敗 | **§9 自我修正** |

## 5. 選件、命名與既有檔判定

### 5.1 選哪幾份

| 申報人 | 年報 | 季報 |
| :--- | :--- | :--- |
| 美國公司（有 10-K/10-Q） | 最新 2 份 10-K（含 10-KT） | 最新 1 份 10-Q（依期末日，不是提交日） |
| 外國發行人（20-F/40-F） | 最新 2 份 20-F／40-F | 最近 400 天、整份提交 ≥ 400KB 的 6-K，最多看 12 份：讀每個 HTML 附件前 1.5MB，財報關鍵字 ≥ 3 個且找得到期末日者為候選，**挑期末日最新**的那份（同一期重送時取分數高、較新者） |

- 10-K 的財報若放在 **EX-13**（給股東的年報）→ 自動一併下載成 `{檔名}_EX13`。
- 6-K 附件是 PDF 時本版不會自動挑（只看 HTML）→ 報告會出現觀察，請人工下載並用 `hint` 記下。

### 5.2 檔名（沿用 collectStk §7.1）

| 文件 | 檔名 | 例 |
| :--- | :--- | :--- |
| 10-K／20-F／40-F | `{TICKER}_AnnualReport_{FY}` | `UHS_AnnualReport_2025` |
| 10-Q | `{TICKER}_Quarter_{FY}Q{N}` | `UHS_Quarter_2026Q3` |
| 6-K 季報 | `{TICKER}_Quarter_{FY}Q{N}`；只有半年資料 → `H1`；期末 = 年度結束 → `Q4` | `TLK_Quarter_2026Q3`、`TM_Quarter_2027Q2` |
| 10-K 的 EX-13 | `{年報檔名}_EX13` | `XYZ_AnnualReport_2025_EX13` |
| 修正申報 | 原檔名 + `_Amend{accession 去 -}` | `UHS_AnnualReport_2025_Amend000095017026000009` |
| 同名檔其實是別種文件（新聞稿、別期） | 加 `_EDGAR` 並存，不覆蓋 | `ZZ_Quarter_2026Q3_EDGAR` |

- `{FY}`／`Q{N}` **優先用 XBRL DEI**（companyfacts 的 `fy`/`fp`，= DocumentFiscalYearFocus／PeriodFocus）；沒有 XBRL 才用期末日 + `fiscalYearEnd` 推算。原因：Target 這類 1 月底結帳的公司，期末 2026-01-31 公司自稱 FY2025，日期推算會錯（2026-11 實測）。
- 52/53 週會計年度：期末落在月初 1–7 日視為上個月底（2026-01-03 → FY2025）。

### 5.3 已涵蓋就略過（不重複下載）

同資料夾有下列任一檔就視為已有，`list` 會標 `[本機已有 …]`：
- 新命名、`_EDGAR` 版本、舊命名 `{T}_annual_{FY}`、`{T}_quarter_…`、`{T}_QuarterlyReport_…`、`{T}_10K_{期末日}`、`{T}_10Q_{期末日}`、`{T}_20F_{期末日}`、SEC 原檔名（`uhs-20260930`、`evtc-20251231`）；Q2 與 H1 互認。
- **任意檔名的 `.md`**（10-K／10-Q／20-F／40-F）：檔頭前 5000 字有 `FORM 10-K` 等字樣，且之後 4000 字內的「fiscal year／quarterly period ended {日期}」與期末日差 ≤ 7 天。`AnalysisResult`、`PublicOpinion`、輿情、`_Presentation_` 等分析檔不參與判定。
- 名字對上但檔頭是別的表單或別期 → 不算已有；新檔另存 `_EDGAR`。
- `.htm` 已下載但還沒轉檔 → 狀態 `pending-convert`，照樣印 `CONVERT2MD_SCOPE`。

## 6. 必知限制

- **只抓 SEC 有的文件**：未在 SEC 註冊的 ADR（unsponsored、OTC，如 HEGIY）查不到 → 回 collectStk §7.3 美股的其他來源。
- 2001 年前的純文字申報（`.txt` 主文件）不處理。
- 新聞稿（8-K EX-99.1 財報速報）不是季報，本 skill 不抓；最新一季 10-Q 還沒出來時，速報由 collectStk 收在輿情／新聞。
- 外國發行人每季不一定都發 6-K 財報（只發半年報的公司 → `H1`）。

## 7. 速度、快取

- 快取在 `~/.cache/edgar/`（`EDGAR_CACHE_DIR` 可改）：`company_tickers.json` 7 天、submissions 6 小時、companyfacts 1 天、filing index 與 6-K 判斷結果永久（以 accession 為 key，內容不會變）。
- 一般美股約 5–10 次請求、10 秒內；外國發行人第一次要讀 6-K 附件，約 20–40 次請求。
- 執行報告：`Log/edgar_Summary_{YYYYMMDD}.md`（同日 append）；上次 download 紀錄 `~/.cache/edgar/last_run.json`（給 `verify` 用）。

## 8. SEC 端點

| 用途 | 端點 |
| :--- | :--- |
| ticker → CIK | `https://www.sec.gov/files/company_tickers.json` |
| 申報清單 | `https://data.sec.gov/submissions/CIK{10碼}.json`（`filings.recent` + `filings.files` 舊分頁） |
| XBRL 事實（FY／季別、流通股數） | `https://data.sec.gov/api/xbrl/companyfacts/CIK{10碼}.json` |
| 單一申報的文件表（附件類型） | `https://www.sec.gov/Archives/edgar/data/{CIK}/{accession 去 -}/{accession}-index.htm` |
| 文件本體 | `https://www.sec.gov/Archives/edgar/data/{CIK}/{accession 去 -}/{檔名}` |

`sec-edgar-mcp`（本機 MCP）適合查 XBRL 財務數字、內部人交易、8-K；**下載年報／季報全文一律用本 skill**。

## 9. 經驗學習與自我修正（強制，每次執行完都要做）

目的：每次爬完把「學到的事」寫回 skill，下一次直接用，不再重踩。

### 9.1 學什麼、寫到哪

`download`／`list` 會把異常印成 `LEARN: …` 行，並寫在執行報告的「本次觀察」。AI 逐條判斷：

| 觀察種類 | 寫到哪 | 怎麼寫 |
| :--- | :--- | :--- |
| 只跟某家公司有關（資料夾不同名、財報放在 EX-13／特定 6-K 附件、6-K 很小、多類股沒有 dei 股數） | `company_hints.json`（機器用）＋ lessons「B. 公司特例」（人看） | `G hint --code T --set k=v --note "…"`；`G lesson --section company --key "{T} …" --text "…"` |
| SEC 通用行為（新封鎖方式、端點欄位變了、分頁、Range） | lessons「A. SEC／EDGAR 行為」 | `G lesson --section sec --key … --text …` |
| FY／季別命名、DEI 與日期推算不一致的新型態 | lessons「C. 命名與會計年度」；若是規則錯 → 改腳本 + selftest 案例 | `G lesson --section naming …` |
| html2md 轉壞（殘留標籤、表格亂、標題錯） | 修 `Convert2md/scripts/html2md.py` + selftest 案例；lessons「D.」 | `G lesson --section convert …` |
| 腳本或本文件寫錯 | 直接修（9.2） | — |

寫法規則：一條一事實、附證據（accession、檔名、HTTP 狀態）；同一件事用同一個 `--key` 改寫舊條目（合併不追加）；已被腳本處理掉的觀察（例如 DEI 修正 FY 已自動採用）只在「第一次遇到新型態」時記一次。沒有新東西就不寫。

### 9.2 自我修正（任一成立就要修）

觸發：`Log/edgar_error.md` 本次新增 `SCRIPT_BUG`／`SELFTEST_FAIL`；`selftest` 有 FAIL；實際行為與本文件不符（欄位變了、命名算錯、既有檔沒被認出而重複下載、參數不存在、Convert2md 介面變了）；使用者指出錯誤。

1. 找根因，直接改 `scripts/edgar.py`、`SKILL.md`、`Convert2md/scripts/html2md.py`。修的是錯，不是繞過：**不可**刪掉或放寬 selftest 來求綠燈，**不可**把含個人 email 的 UA 寫進會 commit 的檔案。
2. 新發現的行為在 `selftest` 補一個案例鎖住。
3. `G selftest`（線上）全部 PASS。
4. 把 `.claude/skills/edgar/` 整個複製到 `.agents/skills/edgar/`（`.env` 除外）；改到 Convert2md 也同步 `.agents/skills/Convert2md/`；再跑一次 `selftest`。（`lesson`／`hint`／`verify` 寫的檔案會自動兩邊同步。）
5. 在 §10 變更紀錄加一行：日期、問題、修法。
6. 重跑剛才失敗的步驟確認修好；commit 訊息以 `fix(edgar):`（純經驗更新用 `docs(edgar):`）開頭並 push。
7. 修不好（SEC 端故障、需要使用者設定 UA）→ 不要硬改，回報使用者並在 `Log/edgar_error.md` 留紀錄。

## 10. 變更紀錄

- 2026-11-26 v1.0.0：新建。從 collectStk 移出所有 SEC EDGAR 處理（原 collectStk §7.3 美股、`references/sites_us_global.md` §7.3-US、§9 第 5 點 HTML 自轉）。功能：ticker/CIK 查詢、submissions 分頁補抓、companyfacts DEI 命名、外國發行人 6-K 財報判斷（依期末日）、EX-13、既有檔（檔名 + 檔頭）判定、`_EDGAR` 並存、`Log/edgar_error.md`／`edgar_Summary`、`verify` 補來源標頭、`lesson`／`hint` 經驗學習、`.agents` 鏡像；Convert2md 新增 `--html` 與 `scripts/html2md.py`。
  - 開發實測即修：`list` 少 `--no-create` 參數 → SCRIPT_BUG（已修）；TM 6-K 期末日誤取比較期 2025-06-30、半年報 EX-99.2 認不出「through／first half ended」→ 改「足夠常出現的日期中取最新且 ≤ 提交日」並補 2 個 selftest；html2md 跨欄表頭錯位一欄 → 移到有資料的欄並補 selftest。
