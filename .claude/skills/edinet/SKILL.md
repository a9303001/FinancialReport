---
name: edinet
description: 用金融廳 EDINET API v2 下載日股（含 J-REIT 投資法人）的有価証券報告書（年報）、半期報告書／四半期報告書（季報），存進 repo 的公司資料夾並沿用 collectStk 命名。輸入證券代碼（如 3445、7203、2971）。需要 EDINET API key（放環境變數 EDINET_API_KEY 或 skill 資料夾的 .env，見 §2）。
---
# edinet — 日股年報／季報下載

> **任務**：證券代碼 → 查 EDINET コード → 往回掃每日提出書類清單 → 下載最新 N 份年報 + M 份季/半期報 → 存公司資料夾 → 交給 `Convert2md` 轉 Markdown。
> 全部用 `scripts/edinet.py`（只用 Python 標準函式庫，Windows / Linux / 雲端皆可）。

## 1. 一行用法

```bash
# 預設：最新 2 份年報 + 1 份季/半期報，PDF，自動存到 repo 內「3445」開頭的資料夾
python .claude/skills/edinet/scripts/edinet.py download --code 3445
```

| 子指令 | 用途 | 範例 |
| :--- | :--- | :--- |
| `checkkey` | 檢查 key 是否設定且有效（不印 key） | `edinet.py checkkey` |
| `lookup` | 用證券代碼／EDINET コード／公司名（日文、英文、ヨミ）找公司 | `edinet.py lookup トヨタ` |
| `list` | 只列出 EDINET 上的年報/季報與預定檔名，不下載 | `edinet.py list --code 7203` |
| `download` | 下載 | `edinet.py download --code 2971 --annual 3 --periodic 0` |

`download` 常用參數：

- `--annual N` / `--periodic M`：年報、季/半期報份數（預設 2 / 1）。
- `--format pdf,xbrl,csv,english,attach`：可逗號分隔多種（預設 `pdf`）。`csv` 是 XBRL 轉 CSV 的財務數據，做數字分析最好用。
- `--out DIR`：輸出資料夾。不填時自動找 repo 根目錄下「以代碼開頭」的唯一資料夾（如 `3445RS`）；找不到會報錯並提示新資料夾名稱 → 新公司請先建 `{代碼}{公司名}` 資料夾。
- `--days N`：最多往回掃幾天（預設 800）。掃到份數夠就提早停。
- `--include-amendments`：一併下載訂正報告書（檔名加 `_Amend{docID}`）。
- `--dry-run`：只列出每份「將下載／略過（已存在）／略過（舊檔名已存在）」，不下載。正式下載前先跑一次。
- `--force`：已存在也重抓。
- `--workers N`：並發數（預設 3；調高容易 429）。

輸出最後一行 `[edinet] NEW_FILES=[...]` 是本次新落地檔案的絕對路徑（JSON），下一步交給 `Convert2md` 只轉這些。

## 2. API key 放哪裡（重要）

**絕對不要**把 key 寫進會被 commit 的檔案。本 repo 的 `.claude/settings.local.json` **有被 git 追蹤**，不能放那裡。

腳本依序讀取，找到即停：

1. **環境變數 `EDINET_API_KEY`**（推薦，Claude 與 Gemini 都讀得到）
   - Windows（永久，設完重開終端機／Claude）：`setx EDINET_API_KEY "你的key"`
   - macOS / Linux：在 `~/.bashrc` 或 `~/.zshrc` 加 `export EDINET_API_KEY="你的key"`
   - 或放在**使用者層級**的 `~/.claude/settings.json`（不在 repo 內）：`{"env": {"EDINET_API_KEY": "你的key"}}`
2. 環境變數 `EDINET_API_KEY_FILE` 指向的檔案。
3. **`.claude/skills/edinet/.env`**（已列入 `.gitignore`）：複製 `.env.example` 改名為 `.env`，填 `EDINET_API_KEY=你的key`。
4. `~/.config/edinet/.env`（同格式，跨 repo 共用）。

設好後跑 `edinet.py checkkey` 確認。key 申請：EDINET 首頁 → 「API」→ API キー発行（需 Microsoft／一般帳號 + 手機簡訊認證，免費）。

**雲端 Claude Code session（已設定好，永久有效）**：容器每次重建，`.env` 不會留下，所以 key 存在雲端環境的**網路密鑰**（host `api.edinet-fsa.go.jp`、header `Ocp-Apim-Subscription-Key`）。腳本在本機找不到 key 時會送佔位值，網路代理自動換成真 key → 什麼都不用設，直接跑。

- 確認：`edinet.py checkkey` 顯示「來源：雲端網路密鑰（代理注入）」。
- 換 key：claude.ai 雲端環境設定 → Network secrets → 修改 `api.edinet-fsa.go.jp` 那筆；或請 Claude 呼叫 `request_credential` 重新存。
- 腳本一律用 header `Ocp-Apim-Subscription-Key` 傳 key（EDINET 實測接受；key 不會出現在網址或 log）。

## 3. 執行流程（AI 照做）

1. `checkkey`；失敗 → 回報使用者依 §2 設定，**改走 AGENTS.md §4.2 D/F 的替代來源**（IR Bank、Ullet、Futu），不要卡住。
2. `list --code {代碼}` 看清單與預定檔名；確認公司對、期別對。
3. `download --code {代碼} --dry-run` 確認會下載／略過哪些，再拿掉 `--dry-run` 正式下載（必要時 `--out` 指定資料夾）。
4. 下載完交給 `Convert2md` skill 把 PDF 轉 Markdown（`<SCOPE>` = 公司資料夾）。由 `collectStk` 呼叫時照 collectStk §7.4、§9 做。
5. 在回覆／執行報告中寫明：找到哪些期別、docID、提出日、哪些份數不足與原因（§4）。

## 4. 必知限制

- **2024 年 4 月起四半期報告書廢止**（金商法修正）：上市公司改為每年 1 份**半期報告書**（docTypeCode 160，檔名 `{代碼}_Quarter_{FY}H1`）。第 1、第 3 季只有交易所的**決算短信**（TDnet），**不在 EDINET** → 要最新單季請另抓 TDnet／公司 IR／IR Bank。
- 2024 年以前的舊季報仍是四半期報告書（docTypeCode 140，`{代碼}_Quarter_{FY}Q{N}`）。
- **J-REIT（投資法人）**：每 6 個月一份有価証券報告書，沒有半期報 → 用 `--annual 3 --periodic 0`；檔名 `{代碼}_AnnualReport_{YYYY}{Mon}`（如 `2971_AnnualReport_2026Jul`），與 repo 既有慣例一致。
- `{FY}` = 會計年度結束年（3 月決算公司 2026/4–9 的半期報 → `2027H1`），沿用 collectStk §命名規則。
- 每日清單快取在 `~/.cache/edinet/lists/`（可用 `EDINET_CACHE_DIR` 改），7 天前的清單不重抓 → 第二家公司起幾乎不用等。首次掃 800 天約 1–3 分鐘。
- 取下（withdrawn）或非公開的文件自動排除。
- **已存在判斷看內容不看檔名**：目標檔名已存在時，讀既有 `.md` 檔頭最早出現的文件名稱（有価証券報告書／半期報告書／四半期報告書／決算短信／資産運用報告）。同一種 → 略過；不同種（例：舊流程把決算短信存成 `_Quarter_`、把資産運用報告存成 `_AnnualReport_`）→ 新檔存成 `{名稱}_EDINET.pdf`，兩份並存不覆蓋。也認得舊命名（小寫 `annual`/`quarter`/`interim`、`H1` ↔ 舊 `Q2`、`202606有価証券報告書－第39期(20250401－20260331).md` 這類日文原檔名＋期末日）。注意：決算短信封面固定有「半期報告書提出予定日」，所以不能用「有沒有出現半期報告書」判斷。
- **429 Too Many Requests**：EDINET 會在 HTTP 200 的 JSON 內回 `StatusCode: 429`（2026-11 實測 4 執行緒連打約 500 天後出現）。腳本自動退避（5→60 秒）重試；單日仍失敗不會中止，最後列出漏掉的日期 → 隔 1 分鐘重跑同一指令，快取會接續。
- 「今天」以日本時間（JST）計算（雲端容器是 UTC）。
- EDINET PDF（Producer = EDINET）經 `convert_pdf_to_markdown` 轉檔實測 0 個 `(cid:`（2026-11，4979 半期報 25 頁），不必找英文版。

## 5. docTypeCode 對照

| code | 文件 | 本 skill 分類 |
| :--- | :--- | :--- |
| 120 | 有価証券報告書 | 年報 |
| 130 | 訂正有価証券報告書 | 年報（訂正，需 `--include-amendments`） |
| 140 | 四半期報告書（~2024/3） | 季報 |
| 150 | 訂正四半期報告書 | 訂正 |
| 160 | 半期報告書 | 季報（半期） |
| 170 | 訂正半期報告書 | 訂正 |

API 文件：EDINET API 仕様書 v2（`https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html`）。
