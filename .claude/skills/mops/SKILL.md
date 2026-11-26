---
name: mops
description: 台股（上市／上櫃／興櫃，含 KY）年報（股東會年報）與季報（財務報告書）專用下載 skill：從 TWSE 電子書（MOPS 財報檔的官方存放處）取清單 → 選最新 2 份年報 + 1 份季報 → 比對公司資料夾既有檔（自動認得舊檔名）→ 下載（本機直連／Apify）或依 script 指示走 MCP（雲端 IP 被封鎖時）→ 用 Convert2md 轉 Markdown → verify 驗證。輸入股票代號（如 6279、2881、6781）。每次爬蟲的成敗與新發現都要寫回經驗庫（learned.json、references/sources.md），下次自動套用；發現 skill 有錯依 §9 自我修正。collectStk 的台股財報一律呼叫本 skill。
---
# mops — 台股年報／季報下載 → Markdown

> **一句話**：代號 → OpenAPI 查公司 → TWSE 電子書清單（`t57sb01`）→ 選 2 份年報 + 1 份季報 → 既有檔略過 → 下載／MCP 落地 → `Convert2md` → `verify` → **§7 寫回經驗** → §9 自我修正。
> 腳本：`.claude/skills/mops/scripts/mops.py`（只用 Python 標準函式庫）；經驗庫：`learned.json`；站點知識：`references/sources.md`。Gemini 用 `.agents/skills/mops/`（必須與 `.claude` 版完全相同，`selftest` 會檢查）。
> 下文 `M` = `python .claude/skills/mops/scripts/mops.py`（Gemini 用 `.agents/...`）。

## 0. 為什麼要這樣做（先懂再做）

- MOPS 財報 PDF 實際放在 **TWSE 電子書 `doc.twse.com.tw`**；MOPS 網頁本身是 JS 表單，不要在上面耗時。
- TWSE／MOPS **依來源 IP 封鎖**：雲端容器（海外 IP）一律拿到 947 bytes「FOR SECURITY REASONS」頁；台灣本機 IP 可直連。script 會自己偵測（環境 `blocked_ip` / `open_ip`），能做的自己做，做不到就印出 MCP 步驟並以結束碼 4 交還給 AI。
- 每條路徑的成敗都記在 `learned.json`，script 依經驗自動排序路徑（連敗 ≥ 2 次的往後排）。**你的工作之一就是讓下次更快**（§7）。

## 1. AI 執行流程（照順序做，不可跳步）

| 步驟 | 指令／動作 | 結果與下一步 |
| :--- | :--- | :--- |
| 0 | `M selftest --offline`（1 秒） | 有 FAIL → 先做 §9 修好再繼續 |
| 1 | `M lessons --code {代號}`（看這家公司與各路徑的過往經驗） | 有公司專屬經驗（IR 網址、上架時差）就照著用 |
| 2 | `M plan --code {代號}` | 結束碼 0 → 步驟 4；結束碼 4（`NEED_MCP=list`）→ 步驟 3 |
| 3 | **MCP 取清單**：對 script 印出的網址跑 `firecrawl_scrape`（§4.1；標「選抓」的那頁只在年報不足 2 份時才抓），每頁存一個檔 → `M plan --code {代號} --html <檔1> <檔2> …` | 解析失敗 → 換 §4 下一條路徑，加 `--route` 註明用哪條 |
| 4 | 看 plan 輸出：每份是「已有」還是「待下載」。全部已有 → 跳到步驟 8 | 缺口（年報不足、興櫃無 Q1/Q3、英文版未出）照抄進報告 |
| 5 | `M download --code {代號}` | 結束碼 0 → 步驟 7；結束碼 4（`NEED_MCP=pdf`）→ 步驟 6 |
| 6 | **MCP 取 PDF**：照 script 印出的 ①②③ 逐份做（§4.2），最後 `M ingest …` 落地 | 某路徑失敗 → `M learn --route … --fail --note "…"` → 換下一條（§4.3） |
| 7 | 有新 PDF（印出 `CONVERT2MD_SCOPE=`）→ 執行 **`Convert2md` skill**，`<SCOPE>` 填該資料夾 | 用 `apify_markdown_mcp` 直接拿到 `.md` 的不必轉 |
| 8 | `M verify --code {代號}` | ❌ CID 亂碼 → `M plan --code {代號} --lang en` 重來；公司名對不上 → 刪檔重抓 |
| 9 | 回報：讀 `Log/mops_Summary_{YYYYMMDD}.md`，寫明找到哪些期別、原始檔名、上傳日、略過／下載／缺口與原因（AGENTS.md §4.3） | — |
| 10 | **§7 寫回經驗**（每次都要做）→ **§9 自我修正檢查** | — |
| 11 | `git add` 公司資料夾新 `.md`、`Log/mops_*`、`.claude/skills/mops/` 與 `.agents/skills/mops/` → commit → push（被 collectStk 呼叫時由 collectStk 統一 push） | — |

> Convert2md 成功後會刪掉來源 PDF，只留 `.md`；下次 `plan` 看到 `.md` 就會判定已有。

## 2. 指令參考

| 子指令 | 用途 | 範例 |
| :--- | :--- | :--- |
| `lookup` | 用代號／簡稱／英文簡稱找公司（上市、上櫃、興櫃），印出市場別、已發行股數（每股化用）、官網 | `mops.py lookup 胡連` |
| `plan` | 取清單、選檔、比對既有檔、存計畫（`~/.cache/mops/plan_{代號}.json`） | `mops.py plan --code 6279` |
| `download` | 依計畫下載；做不到印 MCP 步驟，結束碼 4 | `mops.py download --code 6279` |
| `ingest` | 把 MCP 拿到的檔（Apify 結果 JSON 的 raw／markdown、PDF、MD）用正確檔名落地 | `mops.py ingest --code 6279 --file 202603_6279_AI1.pdf --from <檔>` |
| `verify` | Convert2md 後驗證 `.md`（≥10KB、CID < 50、前 3 萬字有公司名／代號、季報期別字樣）；本次 mops 落地的檔自動在檔頭補「來源」註解（原始 PDF 網址、清單大小、上傳日、路徑） | `mops.py verify --code 6279` |
| `learn` | 記錄路徑成敗或公司經驗 | `mops.py learn --route pdf.apify_raw_mcp --ok` |
| `lessons` | 顯示經驗庫與建議路徑順序 | `mops.py lessons --code 6279` |
| `selftest` | 自我檢查（解析、命名、既有檔判定、SKILL.md↔CLI、鏡像、learned.json）；不加 `--offline` 另測 OpenAPI 與直連 | `mops.py selftest` |

參數：
- `plan`：`--code`（代號或簡稱）、`--html F…`（MCP 清單檔，可多個；接受 HTML、Firecrawl／Apify 回傳 JSON、文字）、`--route`（搭配 `--html`，預設 `list.firecrawl_stealth`）、`--annual N`（預設 2）、`--quarter M`（預設 1）、`--lang zh|en`（預設 zh；英文版當備援）、`--out DIR`、`--env blocked_ip|open_ip`（強制環境）、`--name`（OpenAPI 查不到時的簡稱）。
- `download`：`--code`、`--force`（已有也重抓）、`--try-direct`（被判定封鎖時仍試直連一次）、`--no-create`（資料夾不存在時報錯；預設自動建 `{代號}{簡稱}`）。
- `ingest`：`--file`（清單原始檔名，會核對位元組數）或 `--target`（自訂檔名，如官網 IR 下載的 `6279_Quarter_2026Q3`）、`--from`（來源檔）、`--route`（預設依內容推定：Apify raw → `pdf.apify_raw_mcp`、markdown → `pdf.apify_markdown_mcp`、`--target` → `pdf.company_ir`）、`--link`（PDF 原始網址，同時記一筆 `--link-route` 成功，預設 `link.firecrawl_stealth`）、`--force`。
- `learn`：`--route <階段.做法> [--ok|--fail] [--note "…"] [--env]`（`--env` 預設 `blocked_ip`；只給 `--note` = 只更新做法說明、不計數。`plan --html`、`ingest`、`download` 已自動計數，成功時**不要**再 `--ok` 重複計）；`--code {代號} --note "…" [--ir URL]`（名稱、市場自動從 OpenAPI 補上）。
- `verify`、`lessons`：`--code`（預設上次 plan 的公司）。

結束碼：`0` 成功、`1` 一般錯誤（寫 `Log/mops_error.md`）、`3` 腳本 bug（SCRIPT_BUG）、`4` 需要 AI 走 MCP（看最後一行 `NEED_MCP=list|pdf`）。

## 3. 命名與既有檔判定

### 3.1 檔名（與 collectStk §7.1 相同）

| 文件 | 檔名 | 例 |
| :--- | :--- | :--- |
| 股東會年報（F04／FE4／FE6） | `{代號}_AnnualReport_{FY}` | `6279_AnnualReport_2025` |
| 季報（AI1 等，`{yyyy}0{N}`） | `{代號}_Quarter_{FY}Q{N}`；年度財報 = `Q4` | `6279_Quarter_2026Q3` |
| 興櫃半年報（`{yyyy}02`） | `{代號}_Quarter_{FY}H1` | `2245_Quarter_2026H1` |
| 目標檔名被「不合格檔」佔用 | 加 `_MOPS`（兩份並存不覆蓋） | `1264_Quarter_2026Q3_MOPS.pdf` |

- `{FY}` = 西元資料年度（清單檔名前 4 碼），不是上傳日。KY 公司代號用數字代號（AES-KY = `6781`）。
- 年報選法：股東會清單裡最新 2 個資料年度；中文 F04 優先，英文 FE4／FE6 列為備援（`--lang en` 反過來）。
- 季報選法：財報清單最新 1 個期別；合併（AI1）> 個體（AI3）> 個別（AI2）。

### 3.2 已有就略過（不重複下載）

同資料夾有下列任一檔（`.pdf` ≥ 10KB，或 `.md` ≥ 30KB 且檔頭像完整財報／年報）即視為已有：
- 新命名、`_MOPS`；舊命名 `{代號}_annual_{FY}`、`{代號}_{FY}_annual_report`、`{代號}_quarter_…`、`{代號}_QuarterlyReport_…`、`{代號}_{FY}Q{N}_quarterly_report`；Q2 也認 `H1`、`{代號}_interim_{FY}`；
- TWSE 原檔名（可帶下載時間戳與前綴）：`{FY}_{代號}_{日期}F04/FE4/FE6[_yyyyMMdd_HHmmss]`、`2022年報2022_2245_…F04_…`、`{yyyy}0{N}_{代號}_AI1/AI3/AIA…[_yyyyMMdd_HHmmss]`。
- 檔名對上但太小或檔頭不像財報（例如 MoneyDJ 損益表轉載、新聞摘要）→ **不算已有**，新檔存 `_MOPS`。

## 4. 路徑（route）與 MCP 操作

路徑名 = `<階段>.<做法>`，階段：`list` 取清單、`link` 取 step=9 下載連結、`pdf` 取 PDF 本體。script 能自己跑的只有 `direct` 與 `apify_rest`（需 `APIFY_TOKEN`）；其餘由 AI 用 MCP 執行。**實際順序以 `M lessons` 的建議為準**（經驗會調整）。

| 路徑 | 誰做 | 做法 |
| :--- | :--- | :--- |
| `list.direct` / `link.direct` / `pdf.direct` | script | 台灣 IP 直連（`open_ip`）；雲端一定被封鎖 |
| `list.apify_rest` / `link.apify_rest` / `pdf.apify_rest` | script | 有 Apify token 時 script 自己呼叫 `apify/web-fetch`（REST，raw／html）。token：環境變數 `APIFY_TOKEN`、`.claude/skills/mops/.env`（`APIFY_TOKEN=…`，已被 .gitignore 排除），或雲端 network secret（host `api.apify.com`）+ 環境變數 `MOPS_APIFY_PROXY_AUTH=1` [未驗證：2026-11 尚未設 token] |
| `list.firecrawl_stealth` | AI | §4.1 |
| `list.apify_webfetch_mcp` | AI | `apify--web-fetch`（GET `/`，query `url`、`formats: ["html"]`）；Big5 中文可能亂碼，但檔名／大小／日期可解析 → `plan --html … --route list.apify_webfetch_mcp` |
| `link.firecrawl_stealth` | AI | `firecrawl_scrape` step=9 網址（`proxy: "stealth"`、`formats: ["html"]`、`maxAge: 0`） |
| `link.apify_webfetch_mcp` | AI | `apify--web-fetch` step=9 網址，`formats: ["links"]` |
| `pdf.apify_raw_mcp` | AI | §4.2（雲端首選，2026-11 實測位元組數與清單完全相同） |
| `pdf.apify_markdown_mcp` | AI | 同 §4.2 但 `formats: ["markdown"]`、`get-dataset-items` 的 `fields: "markdown"`；得到的是全文 Markdown → `ingest` 直接存 `.md`（不經 Convert2md）。actor 抓檔上限約 120 秒，大檔易逾時 |
| `pdf.company_ir` | AI | 官網 IR（`references/sources.md` §S4、`M lessons` 的 IR 網址）；`curl` 下載後 `M ingest --code {代號} --target {目標檔名} --from <pdf>` |

### 4.1 MCP 取清單（`NEED_MCP=list`）

1. 對 plan 印出的網址（A 今年、A 去年、F 今年、F 去年；F 前年標「選抓」）呼叫 `firecrawl_scrape`：`formats: ["html"]`、`proxy: "stealth"`、`maxAge: 0`、`onlyMainContent: false`。同一則回應可平行送出。
2. 每頁存一個檔：工具結果被自動存成檔案時直接用那個路徑；否則把回傳的 `html` 用 Write 寫到 `<SCRATCH>/mops_{代號}_{A115|F114…}.html`。只有表頭沒資料列的頁（該年度沒申報）也照樣傳入，不影響。
3. `M plan --code {代號} --html <所有檔>`。

### 4.2 MCP 取 PDF（`NEED_MCP=pdf`，每份照做）

1. **連結**：`firecrawl_scrape` script 印出的 step=9 網址（stealth、html）→ 取 `https://doc.twse.com.tw/pdf/…_{yyyyMMdd_HHmmss}.pdf`。連結有時效，**拿到就馬上做第 2 步**。
2. **PDF**：Apify `call-actor`：`actor: "apify/web-fetch"`、`input: {"url": "<連結>", "formats": ["raw"]}`、`waitSecs: 45`、`callOptions: {"timeout": 300}`；未完成就 `get-actor-run`（`waitSecs: 45`）等到 `SUCCEEDED`（1.6 MB 約 80～95 秒）。actor 抓檔上限 120 秒、input 沒有逾時參數：`FAILED`「Timed out after 120s」→ `M learn --route pdf.apify_raw_mcp --fail --note "…"`，**用同一個連結再跑一次**（算第 2 次；1264 Q3 第 2 次 79 秒成功）。
3. **取回**：`get-dataset-items`（`datasetId`、`fields: "raw,fetch.contentLengthBytes"`、`limit: 1`）。結果是 base64、通常超過上限而被**自動存成檔案**（訊息會給路徑）——不要讀進對話，直接用路徑。若你的環境不會自動存檔、會把整段 base64 塞進對話，改走 `pdf.apify_markdown_mcp` 或 `pdf.company_ir`。
4. **落地**：`M ingest --code {代號} --file {清單原始檔名} --from <第 3 步檔案路徑> --link <第 1 步連結>`。script 會解 base64、核對位元組數＝清單大小、存成正確檔名、記錄路徑成功。
5. 全部落地後回到 §1 步驟 7（Convert2md）。

### 4.3 失敗處理（固定上限，不卡死）

- 每條路徑最多 2 次（失敗重試 1 次），然後 `M learn --route {路徑} --fail --note "{錯誤原文}"`，換下一條。
- 純網路錯誤（逾時、`Connection reset`）不重試，直接換下一條。
- 中文 PDF 轉檔 CID 亂碼（Convert2md 已刪 `.md`、保留 PDF）→ 刪該 PDF，`M plan --code {代號} --lang en` 改抓英文版；英文版還沒上傳 → 官網 IR。
- 所有路徑失敗：報告寫明檔名、清單大小、上傳日、已試路徑與錯誤，下次再補；**不可**用 MoneyDJ 轉載或搜尋摘要冒充財報檔（`references/sources.md` §S3）。

## 5. 台股申報制度須知

- 法定期限（證交法 §36）：年度財報 3 月底前；第 1／2／3 季財報各季結束後 45 天內（5/15、8/14、11/14 前後）。董事會通過到 TWSE 上傳可能隔 1 天～1 週以上；「是否已公告」用鉅亨重訊確認（`references/sources.md` §S3）。
- 股東會年報：股東常會前上傳，多數公司 5～6 月；所以 1～5 月時「最新 2 份年報」通常是前年與大前年度，最新年度財務數字看 `Q4`（年度財報）。
- 興櫃：只有半年報（H1）與年度財報，沒有 Q1／Q3；轉上櫃後才開始有季報（OpenAPI `DateOfListing` 可確認，如 2249 於 2026-10-22 轉上櫃）。
- 英文版：通常晚中文 1～1.5 個月；`plan` 會依經驗庫的 `en_lag_days` 提醒。
- TWSE PDF 多有加密（copy:no），`convert_pdf_to_markdown` 仍可正常轉檔（6279 Q3 實測 0 CID）。

## 6. 錯誤報告與執行報告

- `Log/mops_error.md`：所有錯誤自動寫入（最新在上、留 50 筆、不含 token）。種類：`NETWORK`、`NOT_FOUND`、`AMBIGUOUS`、`PARSE_ERROR`、`SIZE_MISMATCH`、`APIFY_AUTH`／`APIFY_ERROR`、`NO_PLAN`、`BAD_ARGS`、`LEARNED_CORRUPT`、`SCRIPT_BUG`、`SELFTEST_FAIL`。後四種（含 `PARSE_ERROR`）→ §9。
- `Log/mops_Summary_{YYYYMMDD}.md`：plan／download／ingest／verify 的紀錄（同日 append）。
- 被 IP 封鎖不是錯誤，只寫進執行報告與經驗庫。

## 7. 寫回經驗（強制，每次執行完都要做）

目的：每次爬蟲學到的事，下次直接用，不重踩坑。

### 7.1 自動記錄（script 已做，不用手動）
- `plan`／`download`／`ingest` 自動記錄各路徑成敗到 `learned.json` 的 `routes.{環境}`；`plan` 自動更新公司的 `en_lag_days`。

### 7.2 AI 手動記錄（script 看不到的事）
1. **MCP 失敗**：每次 MCP 路徑失敗都要 `M learn --route {路徑} --fail --note "{錯誤原文／HTTP 狀態／秒數}"`（成功會由 `plan --html`、`ingest` 自動計數；想補充做法說明用 `M learn --route {路徑} --note "…"`，不加 `--ok`）。
2. **新路徑**：用了表上沒有的做法且成功（例如新 actor、新參數）→ `M learn --route pdf.{新名稱} --ok --note "{完整做法}"`，新路徑會自動加入排序；同時在 §4 路徑表補一列。
3. **公司專屬**：官網 IR 網址、上架時差、特殊檔名（只有個體財報、KY 英文年報）、轉上市櫃 → `M learn --code {代號} --note "…" [--ir URL]`。
4. **站點行為改變**（新封鎖、改版、參數失效）→ 改 `references/sources.md` 對應那一列並更新 `[yyyy-mm]`。
5. 跑 `M lessons --code {代號}` 確認記錄正確。

### 7.3 寫法規則
1. **放對位置**：統計 → `learned.json`（只用 `learn` 指令寫，不手改）；站點行為 → `references/sources.md` §S1～S3（一站一列）；官網 IR → §S4；流程與路徑 → 本檔 §1、§4；制度 → §5。
2. **合併不追加**：同一站點已有一列就改寫那一列，不新增「補充」列。
3. **刪除無用資料**：失效做法、改版前網址、一次性除錯流水帳（某天幾秒幾 KB）→ 刪除，只留結論與一個代表性實例。
4. **沒有證據不寫**：推測不寫進 skill；無法驗證就標 `[未驗證]`。

## 8. 與其他 skill 的關係

- **collectStk**：台股財報（Phase 2）一律呼叫本 skill（collectStk §7.7）；輿情、重訊仍歸 collectStk（鉅亨、MoneyDJ 等在 collectStk 的 `references/sites_tw.md`）。
- **Convert2md**：只轉 PDF → `.md`；`<SCOPE>` 一定要填公司資料夾，`save_path` 填完整 `.md` 檔案路徑。
- 鏡像：`.claude/skills/mops/` 是唯一編輯來源；collectStk 的 `selfcheck.py --fix` 會整份同步到 `.agents/skills/mops/`（`learned.json` 由 script 兩邊同時寫）。

## 9. 執行後自我修正（強制）

**觸發條件**（任一成立就要修）：
1. `Log/mops_error.md` 本次新增 `SCRIPT_BUG`、`SELFTEST_FAIL`、`PARSE_ERROR` 或 `LEARNED_CORRUPT`；
2. `selftest` 有 FAIL；
3. 實際行為與本文件不符（清單格式改了、檔名代碼新出現、既有檔沒認出而重複下載、期別或命名算錯、MCP 參數失效、Convert2md 介面變了）；
4. 使用者指出錯誤。

**修正流程**：
1. 找根因，直接改 `scripts/mops.py` 和／或 `SKILL.md`、`references/sources.md`。修的是錯，不是繞過：**不可**刪掉或放寬 selftest 檢查求綠燈、**不可**把 token 寫進任何檔案。
2. 新發現的行為（新檔名代碼、新舊檔名格式）→ 在 `selftest` 補案例鎖住。
3. `M selftest` → 全部 PASS。
4. 同步鏡像：`python .claude/skills/collectStk/scripts/selfcheck.py --fix`（或手動把 `.claude/skills/mops/` 複製到 `.agents/skills/mops/`，`.env` 除外），再跑一次 `M selftest --offline`。
5. §10 變更紀錄加一行：日期、問題、修法。
6. 重跑剛才失敗的步驟確認修好；commit 訊息以 `fix(mops):` 開頭。
7. 修不好（TWSE 端故障、需要使用者的 token）→ 回報使用者，`Log/mops_error.md` 留紀錄。

若問題出在 `Convert2md`，同樣修正 `.claude/skills/Convert2md/SKILL.md` 與 `.agents` 版（兩份保持相同）。

## 10. 變更紀錄

- 2026-11-26 v1.0.0：新建。從 collectStk 搬入 MOPS／TWSE 電子書／法說簡報／台股官網 IR 知識（collectStk `sites_tw.md` §4.2 三列與 §7.3-TW）。
  - 實測：雲端 IP 對 doc.twse、mops、mopsov、isin 一律 947 bytes 封鎖；TWSE／TPEx OpenAPI 可直連。
  - 新路徑 `pdf.apify_raw_mcp`：Apify raw → 結果自動存檔 → `ingest` 解 base64，6279 Q3 1,586,330 bytes 與清單相同、56 頁、Convert2md 0 CID（取代舊的「PDF 無法落地到容器」限制）。
  - 經驗庫 `learned.json`：路徑成敗自動排序、公司專屬經驗、英文版時差。
  - 首次實跑 1264 德麥 Q3（雲端）：清單 4 頁 Firecrawl 全成功；Apify raw 第 1 次 120 秒逾時、同連結第 2 次 79 秒成功 → `ingest` 1,558,406 bytes 與清單相同 → Convert2md 0 CID → verify 3/3。依此修正：自動記錄改寫 `last_msg` 不再覆蓋人工 `note`；`learn` 可只寫說明不重複計數；F 前年清單改為選抓；verify 只替本次落地的檔補來源標頭（既有檔不可冒標來源）；MCP 指示的連結編號筆誤。
