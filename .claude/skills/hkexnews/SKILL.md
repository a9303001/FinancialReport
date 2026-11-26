---
name: hkexnews
description: 用港交所披露易（HKEXnews）官方 JSON API 下載港股（含港股 REIT、A+H 股、GEM）的年報（Annual Report）、中期報告（Interim Report）與最新季度／全年／中期業績公告 PDF，**一律英文版優先**（既有檔只有中文版時自動補抓英文版，驗證後可刪中文重複檔；英文沒有的期別才用中文版補），存進 repo 的公司資料夾（沿用 collectStk 命名、自動認得舊檔名、HKEX 原始編號檔名與中文原檔名），再呼叫 Convert2md 轉 Markdown 並驗證。輸入 5 碼股份代號（如 02318、01426、87001）。另提供 search／fetch 給 collectState 抓任意公告。每次執行完必須依 §9 把學到的經驗寫回本 skill（learn 子指令）並自我修正。
---
# hkexnews — 港股年報／中報／業績下載（英文版優先）→ Markdown

> **一句話**：股份代號 → `stockId`（港交所完整股票清單）→ **2 次群組搜尋**拿到 6 類文件 → 推算決算月、期末、FY → 選 **2 份年報 + 1 份中期報告 + 1 份比報告更新的業績公告** → **下載英文版 PDF**（既有中文版 → 補抓英文版）→ **`Convert2md`** 轉 `.md` → `verify --prune-zh` 驗證並刪被取代的中文檔 → 寫執行報告 → **§9 經驗回寫與自我修正**。
> 腳本：`.claude/skills/hkexnews/scripts/hkexnews.py`（只用 Python 標準函式庫；Windows／macOS／Linux／Claude Code 雲端皆可；**不需要 API key**）。Gemini 用 `.agents/skills/hkexnews/`（內容必須與 `.claude` 版完全相同，`selftest` 會檢查；`learn` 會自動同步）。

## 1. AI 執行流程（照順序做，不可跳步）

下文 `H` = `python .claude/skills/hkexnews/scripts/hkexnews.py`。

| 步驟 | 指令／動作 | 失敗時 |
| :--- | :--- | :--- |
| 0 | **先讀 §8 經驗庫**，再跑 `H selftest --offline`（1 秒） | 有 FAIL → 先做 §9 修好再繼續 |
| 1 | `hkexnews.py list --code {5碼代號}` | 核對公司、決算月、期別、語言與最後的「download 預定動作」（略過／下載／補抓英文版）；`LEARN?` 先記下來（§9） |
| 2 | `hkexnews.py download --code {5碼代號}` | 已有英文（或雙語）版的期別自動略過；只有中文版 → 補抓英文版（§5.4）；找不到公司資料夾自動建 `{代號}{中文名}`；網路錯誤見 §4 |
| 3 | 若步驟 2 印出 `CONVERT2MD_SCOPE=...` → 執行 **`Convert2md` skill**，`<SCOPE>` 填該資料夾絕對路徑 | 沒印 = 沒有新 PDF，跳過 3、4 |
| 4 | `hkexnews.py verify --code {5碼代號} --prune-zh` | ❌ 的檔：CID 亂碼 → 刪 PDF，加 `--lang zh` 重抓；「應是英文卻是中文」→ 查 FILE_LINK；公司名對不上 → 刪掉重查 `list`。`--prune-zh` 只刪「英文版已驗證通過」那一期的中文檔 |
| 5 | 回報使用者：讀 `Log/hkexnews_Summary_{YYYYMMDD}.md`，寫明期別、語言、文件編號、刊發日、略過／下載／補抓英文版／刪除的中文檔、缺口與原因（AGENTS.md §4.3） | — |
| 6 | **§9 經驗回寫與自我修正**（每次都要做，不可省略） | — |
| 7 | `git add -A` 公司資料夾（含被刪的中文檔）、`Log/hkexnews_*`、（若有修正或 learn）skill 檔案與 `.agents` 鏡像 → commit → push | — |

> Convert2md 成功後會刪掉來源 PDF，只留 `.md`；下次 `download` 看到英文 `.md` 就略過該期別。
> 年報常 150～300 頁：`convert_pdf_to_markdown` 回「timed out after 60s」時伺服器仍在背景寫檔，不要重送，等 `.md` 大小連續 30 秒不變（Convert2md 錯誤處理表）。

## 2. 指令參考

| 子指令 | 用途 | 範例 |
| :--- | :--- | :--- |
| `selftest` | 自我檢查：中英文標題解析、LONG_TEXT 分類、決算月／FY／命名、選檔、語言判定、既有檔與英文優先、代號解析、SKILL.md↔CLI 一致、`.agents` 鏡像；不加 `--offline` 再測線上 API | `hkexnews.py selftest` |
| `lookup` | 股份代號／英文名／中文名 → `stockId`（含已除牌） | `hkexnews.py lookup 02318` |
| `list` | 列出近 N 天的年報／中報／業績、期末、語言、預定檔名與 download 預定動作，不下載 | `hkexnews.py list --code 02633` |
| `download` | 選檔 + 下載 + 寫執行報告 | `hkexnews.py download --code 01426` |
| `verify` | Convert2md 之後驗證 `.md`（存在、≥10KB、CID < 50、前 3 萬字有公司名／代號、下載英文版就必須是英文）；加 `--prune-zh` 刪被英文版取代的中文檔 | `hkexnews.py verify --code 01426 --prune-zh` |
| `search` | 任意公告清單（collectState 收 REIT 公告、查單位數用） | `hkexnews.py search --code 00405 --from 2026-10-26 --type all` |
| `fetch` | 下載單一公告 PDF（驗證 `%PDF` 檔頭、≥10KB，只收 hkexnews.hk 網址） | `hkexnews.py fetch --url /listedco/listconews/sehk/2026/1123/2026112301695.pdf --dest <完整路徑>.pdf` |
| `learn` | 把一條經驗寫進本檔 §8 經驗庫並同步 `.agents` 鏡像 | `hkexnews.py learn --note "情況 → 做法／結果"` |

`list` / `download` 參數：
- `--annual N`（預設 2）／`--periodic M`（預設 1，中期或季度「報告」）。
- `--no-latest`：不要額外抓「期末比所有報告都新」的業績公告（預設會抓 1 份，例如 Q3 業績、報告還沒出的中期／全年業績）。
- `--fye-month M`：決算月（1–12）。預設自動推估（§5.1），推錯時才指定。
- `--lang en|zh`：預設 `en`（英文版優先，§5.4）。`zh` 只在英文版轉檔 CID 亂碼時用。
- `--accept-zh`：既有中文版視為已涵蓋，不補抓英文版（使用者明確要中文時才用）。
- `--days N`：往回幾天（預設 1000，涵蓋 2 份年報）。
- `--out DIR`：指定輸出資料夾。不填 → repo 根目錄下「代號開頭、下一字不是數字」的唯一資料夾（如 `02318中國平安`）；`download` 找不到就自動建（加 `--no-create` 改為報錯）。
- `--force`（僅 download）：已存在也重抓。

`search` 參數：`--code`、`--from` / `--to`（YYYY-MM-DD，預設最近 30 天）、`--keyword`（標題正規表示式）、`--lang`、`--json`（給程式讀，含完整 `url` 與 `lang`）、`--type`：
`all`（全部）、`announcement`（公告及通告）、`financial`（財務資料類公告）、`annual`、`interim`、`quarterly-report`、`final-results`、`interim-results`、`quarterly-results`、`reports`（財務報表/ESG 全部）、`circular`（通函）、`monthly-return`（月報表：已發行股份／基金單位數 → 每股化用）、`next-day`（翌日披露報表：回購、增發）。

結束碼：`0` 成功、`1` 一般錯誤（含 `verify` 有 ❌）、`3` 腳本 bug（SCRIPT_BUG）。

## 3. API、分類代碼與中英文版（2026-11 實測）

1. **代號 → stockId**：`/ncms/script/eds/activestock_sehk_e.json`（英文名）＋ `activestock_sehk_c.json`（中文名），欄位 `i`=stockId、`c`=代號、`n`=名稱，**含 GEM**（約 1.1 MB，快取 7 天於 `~/.cache/hkexnews/`）；已除牌查 `inactivestock_sehk_e/_c.json`（同一代號可能被多家用過 → 取 stockId 最大的最近一家）。備援：`/search/prefix.do`（JSONP，**只回 1 筆前綴最相符**：查 `08001` 會回 `80016`，所以不當主要來源）。
2. **搜尋**：`/search/titleSearchServlet.do?sortDir=0&sortByOptions=DateTime&category=0&market=SEHK&stockId={id}&documentType=-1&fromDate={yyyyMMdd}&toDate={yyyyMMdd}&lang=EN&searchType=1&rowRange=200&t1code=…&t2Gcode=…&t2code=…`
   - servlet 名稱**大小寫敏感**（全小寫 404）。`result` 是「JSON 字串裡的 JSON」，要解兩次；`TITLE`／`LONG_TEXT` 有 HTML entity（`&#x2f;`）。
   - 不限分類填 `-2`。`hasNextRow: true` = 被 `rowRange` 截斷 → 腳本自動改逐分類搜尋。
   - **群組搜尋（每家 2 次請求）**：`t1code=40000&t2Gcode=-2&t2code=-2`（所有報告）＋ `t1code=10000&t2Gcode=3&t2code=-2`（財務資料類公告），再用 `LONG_TEXT` 方括號內的分類名（以「 / 」分隔，一份可多類）判斷是哪一類。
3. 分類代碼（完整表：`/ncms/script/eds/tierone_e.json`、`tiertwo_e.json`）：

| 文件 | t1code | t2code | LONG_TEXT 分類名（英／中） | 本 skill 用途 |
| :--- | :--- | :--- | :--- | :--- |
| Annual Report 年報 | 40000 | 40100 | Annual Report／年報 | 年報（完整版） |
| Interim/Half-Year Report 中期報告 | 40000 | 40200 | Interim/Half-Year Report／中期/半年度報告 | 季報（半年，完整版） |
| Quarterly Report 季度報告 | 40000 | 40300 | Quarterly Report／季度報告 | 季報（極少公司有） |
| Final Results 全年業績公告 | 10000 | 13300 | Final Results／末期業績 | 年報出來前的最新速報 |
| Interim Results 中期業績公告 | 10000 | 13400 | Interim Results／中期業績 | 中報出來前的最新速報 |
| Quarterly Results 季度業績 | 10000 | 13600 | Quarterly Results／季度業績 | Q1／Q3（A+H 股、部分 H 股） |
| Monthly Returns 月報表 | 51500 | -2 | — | 已發行股數（`search --type monthly-return`） |

4. **中英文版**：同一份文件的英文版與中文版是**兩個編號**、同一刊發時間（例 02318 年報 2025：英文 `2026042803045.pdf`、中文 `2026042803046_c.pdf`）。`lang=EN` 搜尋回英文版連結、`lang=ZH` 回中文版（檔名 `_c.pdf`）。2026-11 抽查 17 家（大型股、A+H、REIT、GEM）全部中英成對，沒有只有中文的報告。
5. PDF = `https://www1.hkexnews.hk` + `FILE_LINK`。

## 4. 錯誤報告 `Log/hkexnews_error.md`

腳本自動寫入（最新在最上面，保留 50 筆）：

| 種類 | 意義 | AI 要做的事 |
| :--- | :--- | :--- |
| `PROXY_BLOCKED` | 雲端代理沒放行 `www1.hkexnews.hk` | 讀 `/root/.ccr/README.md`；本次改走 collectStk §7.3 港股 ②③（富途、官網 IR），報告寫明 |
| `NETWORK` / `HTTP_ERROR` | 連線失敗、403/429/5xx 已退避重試 4 次 | 重跑一次；仍失敗 → 替代來源 |
| `API_ERROR` | 回應不是預期 JSON／股票清單壞掉（HKEXnews 改版） | `curl` 看實際回應 → §9 修腳本並補 selftest |
| `NOT_FOUND` / `AMBIGUOUS` | 代號找不到／名稱對到多檔／多個同代號資料夾 | `lookup` 確認，用 5 碼代號；資料夾用 `--out` |
| `SCRIPT_BUG`（結束碼 3，附 traceback）／`SELFTEST_FAIL` | 腳本本身有錯 | **§9 自我修正** |

## 5. 期別推算、命名、既有檔與英文優先

### 5.1 決算月與期末日

- **決算月**（依序）：① 全年業績／年報標題的「year ended 31 March 2026」② 中期業績標題的「six months ended」+6 個月 ③ 年報刊發月往回 2～4 個月的季末月（4 月刊發 → 12 月；7 月 → 3 月）④ 預設 12。`--fye-month` 最優先。
- **期末日**：標題有日期就用標題（取最後一個日期；英文「31 December 2025」「June 30, 2026」、中文「2026年9月30日」都認得）；沒有（如「Annual Report 2025」「二零二五年年報」）→ 刊發日前 14 天以前、最近一個符合該類別的月底（年報 = 決算月、中報 = 決算月 +6、Q1 = +3、Q3 = +9）。
- **季度判斷**：「nine months／first three quarters／third quarter／九個月／前三季」= Q3（要先於「first quarter」判斷）；「three months／first quarter／三個月」= Q1；「six months／interim／六個月／中期」= H1。
- **FY** = 期末日之後（含）第一個決算月的年份（3 月決算 2026/4–9 中報 → `2027H1`；與 edinet 一致）。

### 5.2 檔名（沿用 collectStk §7.1）

| 文件 | 檔名 | 例 |
| :--- | :--- | :--- |
| 年報 40100 | `{代號}_AnnualReport_{FY}` | `02318_AnnualReport_2025` |
| 中期報告 40200 | `{代號}_Quarter_{FY}H1` | `02633_Quarter_2027H1` |
| 季度報告 40300／季度業績 13600 | `{代號}_Quarter_{FY}Q{N}` | `00941_Quarter_2026Q3` |
| 中期業績公告 13400（報告還沒出） | `{代號}_Quarter_{FY}H1_Results` | `02633_Quarter_2027H1_Results` |
| 全年業績公告 13300（年報還沒出） | `{代號}_AnnualReport_{FY}_Results` | `03606_AnnualReport_2026_Results` |
| 同名檔是**中文版** → 英文版另存 | 加 `_EN` | `00941_AnnualReport_2025_EN.pdf` |
| 同名檔其實是別種文件 | 加 `_HKEX` | `02318_Quarter_2026H1_HKEX.pdf` |

### 5.3 已涵蓋就略過（不重複下載）

同資料夾有下列任一 `.pdf`／`.md` 就視為「有這一期」（再依 §5.4 看語言）：
- 新命名與舊命名（各含 `_EN`／`_HKEX`）：年報 `{代號}_annual_{FY}`、`{代號}_Annual_{FY}`；中報 `{代號}_Quarter_{FY}Q2`、`{代號}_interim_{FY}`、`{代號}_Interim_{FY}`、`{代號}_InterimReport_{FY}`、`{代號}_QuarterlyReport_{FY}Q2`；季度 `{代號}_quarter_{FY}Q{N}`；業績公告另認 `{代號}_AnnualResults_{FY}`、`{代號}_InterimResults_{FY}`。
- HKEX 原始編號檔名（`FILE_LINK` 檔名，如 `2026042200516.md`）。
- 中文原檔名：含「年報／年度報告／中期報告…」且年份相符（如 `20260423_2025年年報.md`、`20250828二零二五年中期報告.md`；開頭的 `yyyyMMdd` 刊發日不算年份，中文數字年份會轉成阿拉伯數字）。
- **`.md` 還要看內容**：前 4000 字有港交所免責聲明（「contents of this announcement」）= **業績公告**，不能頂替完整的年報／中期報告（例：`02318_Interim_2026.md` 其實是中期業績公告 → 仍會下載真正的 Interim Report）；業績公告則可被完整報告頂替。

### 5.4 英文版優先（v2.0.0 起）

| 情況 | download 動作 |
| :--- | :--- |
| 這一期沒有任何檔 | 下載英文版 |
| 已有英文或中英雙語 `.md`、或語言不明的 `.pdf` | 略過 |
| **只有中文版**（`.md` 內容判定為中文，或 `*_c.pdf`／中文檔名 PDF） | **補抓英文版**（`list` 顯示「補抓英文版」）；同名檔被中文版佔用 → 存 `_EN` |
| 英文搜尋湊不滿份數 | 用中文搜尋補「英文沒有的期別」（多 1 次請求），報告寫「HKEXnews 沒有英文版、改用中文版」 |
| 英文搜尋完全沒有報告 | 整份改用中文版 |
| `--accept-zh` | 中文版也算已涵蓋 |

- **語言靠內容判斷，不靠檔名**：前 4 萬字的中文字比例 ≥ 0.5 = 中文、0.15～0.5 = 雙語、< 0.15 = 英文（實測中文年報 0.93～0.99、英文 0.00～0.02、恒安英文年報夾中文表格 0.19）。87001 的 `20250828二零二五年中期報告.md` 是中文檔名但內容是英文 → 算英文，不會重抓。
- **刪中文重複檔**：`verify --prune-zh` 只在該期英文 `.md` 驗證通過後，刪掉 download 記錄的那幾個中文檔（同 stem 的 `.md`／`.pdf`），git 可還原；原名空出後 `_EN` 檔自動改回標準檔名（`00941_Quarter_2026Q3_EN.md` → `00941_Quarter_2026Q3.md`）。沒加 `--prune-zh` 時 verify 會印 `PRUNE?` 清單。

## 6. 選檔規則

1. 同一（分類、期末）多份 → 先排除附屬文件（標題含 debt／bond／presentation／ORA／supplement／clarification／correction／revised／dividend／ESG／債券／簡報／補充／更正／股息…），再**英文優先**，再取最早刊發的原始版（例：02318 Q1 業績另有「for 5131 debt stock」「致5131債券持有人」版本）。
2. 年報取最新 `--annual` 份；中期／季度報告取最新 `--periodic` 份。
3. 業績公告只取 1 份：期末比所有已刊發報告都新的最新一份（Q3 業績、或年報／中報刊發前的全年／中期業績）。期末相同的業績公告不抓（報告已涵蓋）。

## 7. 速度與限制

- 一家公司搜尋 **2 次請求、約 7 秒**（v1 是 6 次、約 14 秒）；第一次跑另下載股票清單 4 個檔（之後快取 7 天）。禮貌節流 0.8 秒/請求（`HKEXNEWS_MIN_INTERVAL` 可改）。PDF 串流寫入暫存檔再改名，逾時 300 秒（年報常 5～40MB）。
- 執行報告：`Log/hkexnews_Summary_{YYYYMMDD}.md`（同日多次 append，含每份的語言、HKEX 網址與 `LEARN?` 候選）；上次 download 紀錄：`~/.cache/hkexnews/last_run.json`（給 `verify` 用，含要刪的中文檔清單）。
- 港股沒有「詳細版 vs 摘要版」的監理分工：完整報告（40100/40200）才有附註、風險與管理層討論；業績公告是速報。季度業績多數只有 A+H 股與少數 H 股發布。

## 8. 經驗庫（每次執行後由 §9 更新；`learn` 只寫在兩個標記之間）

> 一行一條：`[yyyy-mm] 情況 → 做法／結果`。同一主題已有一行時直接改寫那一行（`Edit`），不要追加重複的；失效的刪掉。

<!-- LEARN:START -->
- [2026-11] `titleSearchServlet.do` 帶 `t1code=40000&t2Gcode=-2&t2code=-2`（報告）與 `t1code=10000&t2Gcode=3&t2code=-2`（財務資料公告）各 1 次即可拿齊 6 類，再用 `LONG_TEXT`「[Interim Results / Dividend or Distribution]」分類；00941 1000 天財務公告 31 筆，遠低於 rowRange 200。
- [2026-11] `prefix.do` 只回 1 筆前綴最相符（`08001` → `80016` 新鴻基地產－Ｒ），GEM／已除牌代號會查錯或拿不到中文名 → 改用 `activestock_sehk_e/_c.json`、`inactivestock_sehk_e/_c.json`。
- [2026-11] 中英文版是不同編號、同刊發時間（中文 `_c.pdf`）；17 家抽查全部成對。repo 舊檔有不少是中文版（02318 年報 2024/2025、00941 年報 2024／中報 2026、87001 年報）→ v2 會自動補抓英文版。
- [2026-11] 3 月決算公司（02633）年報標題是「2025/2026 Annual Report」、中報「2025/2026 Interim Report」（12 月刊發）、中期業績 11 月刊發 → 決算月靠全年業績標題「YEAR ENDED 31 MARCH」判斷。
- [2026-11] 港股 REIT（01426、87001）沒有季度業績；01426 的 Q1/Q3「營運數據」公告不屬 13600，要用 `search --keyword "Operating Statistics"` 另找。
- [2026-11] A+H 股（01816、03606、00883、00941）季度業績在 13600：標題寫法各異（「THIRD QUARTERLY REPORT」「FIRST THREE QUARTERS」「Nine Months Ended」），都判為 Q3。
- [2026-11] 舊流程把中期**業績公告**存成 `02318_Interim_2026`、把中期報告存成 `_Quarter_{FY}Q2`／`_InterimReport_{FY}`、87001 用中文原檔名、01426 用 HKEX 編號檔名 → 都已納入 §5.3 判定。
- [2026-11] [02318] Interim Report 2026（14MB／188 頁）convert_pdf_to_markdown 回「timed out after 60s」，背景仍在寫檔，約 1～2 分鐘後 .md 停止變大（526KB、轉到最後一頁）→ 不要重送，用迴圈等檔案大小連續 30 秒不變再跑 Convert2md 步驟 4。
<!-- LEARN:END -->

## 9. 執行後經驗回寫與自我修正（強制，每次執行完都要做）

**A. 經驗回寫（每次都做）** — 讓下一次跑得更順：
1. 收集本次的「意外」：腳本印出的 `LEARN?` 行（也在 `Log/hkexnews_Summary_*.md`）、手動補救過的步驟（換語言、指定 `--fye-month`、改用替代來源）、新發現的標題寫法／分類名／檔名慣例、只有中文版的公司、HKEXnews 行為改變。
2. 逐條判斷，放到對的地方：
   - **能寫成規則的** → 改 `scripts/hkexnews.py`（如新的標題寫法、附屬文件關鍵字、舊檔名、LONG_TEXT 分類名），並在 `selftest` 補一個用**本次真實標題／檔名**的案例鎖住。
   - **只能靠人判斷的知識**（某公司特殊慣例、站點暫時異常、替代來源）→ `hkexnews.py learn --note "[代號] 情況 → 做法／結果"`。
   - 一次性雜訊（單次逾時、當天沒新文件）→ 不寫。
3. 沒有任何意外 → 在回報中寫「本次無新經驗」。

**B. 自我修正（任一成立就要修）**：`Log/hkexnews_error.md` 本次新增 `SCRIPT_BUG`／`SELFTEST_FAIL`；`selftest` 有 FAIL；實際行為與本文件不符（API 欄位、分類代碼、期別或檔名算錯、既有檔沒被認出而重複下載、英文版被當成中文而重抓、文件寫的參數不存在）；使用者指出錯誤。流程：
1. 找根因，直接改 `scripts/hkexnews.py` 和／或 `SKILL.md`。修的是錯，不是繞過：**不可**刪掉或放寬 selftest 檢查來求綠燈。
2. 新發現的行為 → `selftest` 補案例。
3. 跑 `hkexnews.py selftest`（線上）→ 全部 PASS。
4. 把 `.claude/skills/hkexnews/` 整個複製到 `.agents/skills/hkexnews/`（`learn` 會自動做；手動改檔後要自己複製），再跑一次 `selftest` 確認鏡像一致。
5. 在 §10 變更紀錄加一行：日期、問題、修法（改腳本行為時順便升 `VERSION`，selftest 會檢查 §10 有寫本版）。
6. 重跑剛才失敗的步驟確認修好；commit 訊息以 `fix(hkexnews):`（經驗回寫用 `docs(hkexnews):`）開頭並 push。
7. 修不好（HKEXnews 故障、代理擋 host）→ 不要硬改，回報使用者並在 `Log/hkexnews_error.md` 留紀錄。

若問題出在 `Convert2md`，同樣修 `.claude/skills/Convert2md/SKILL.md` 與 `.agents/skills/Convert2md/SKILL.md`（兩份相同）。

## 10. 變更紀錄

- 2026-11-26 v2.0.0：改寫。**英文版優先**：既有檔依內容判斷語言，只有中文版就補抓英文版（同名被佔 → `_EN`），`verify --prune-zh` 在英文版驗證通過後刪中文重複檔並把 `_EN` 改回標準檔名、`verify` 檢查英文版內容不是中文，英文湊不滿份數才用中文補期別，`--accept-zh` 可關閉；搜尋由 6 次分類請求改 2 次群組請求（解析 `LONG_TEXT`，被截斷自動退回逐分類）；代號解析改用港交所完整股票清單（修 `prefix.do` 把 08001 查成 80016、GEM 無中文名）；中文標題日期／季度解析（「截至2026年9月30日止九個月」「二零二五年年報」）與中文附屬文件關鍵字；PDF 串流下載；`list` 顯示語言與 download 預定動作；`--out` 也可用於 `list`。
- 2026-11-26 v1.0.0：新建。從 collectStk `references/sites_hk_cn.md` §5.4／§7.3-HK 移入 HKEXnews 流程並腳本化：分類代碼精準搜尋、決算月／FY 推算（含 3 月決算）、2 年報 + 1 中報 + 最新業績選檔、舊檔名／HKEX 編號／中文原檔名與內容種類判定、`_HKEX` 並存、Convert2md 串接與 `verify`、`search`／`fetch` 給 collectState、`learn` 經驗回寫、`selftest`、`.agents` 鏡像。
