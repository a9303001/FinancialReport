# EDINET 錯誤報告

> 由 `.claude/skills/edinet/scripts/edinet.py` 自動寫入，最新在最上面（最多保留 50 筆）。
> **API key 永遠不會寫進這裡**（只記錄來源與格式檢查）。
> 種類：`AUTH_INVALID_KEY` / `AUTH_FORBIDDEN`（key 錯誤，優先處理）、`RATE_LIMIT`、`NETWORK`、`API_ERROR`、`NOT_FOUND`、`AMBIGUOUS`、`SCRIPT_BUG`（腳本本身有錯 → AI 依 SKILL.md §9 自我修正）、`SELFTEST_FAIL`。

<!-- entries -->
## 2026-11-27 04:49:33 — AUTH_INVALID_KEY

- 指令：`edinet.py checkkey`（script v2.0.1，Python 3.11.18，linux）
- 錯誤：API status 401
- 端點：`/api/v2/documents.json`
- 狀態碼：401
- API 回應：`Access denied due to invalid subscription key.Make sure to provide a valid key for an active subscription.`
- key 來源：無（佔位值 → 雲端代理注入）；本機未設定（送佔位值，靠雲端代理注入）
- 可能原因：
  - 本機沒有設定 key（環境變數與 .env 都沒有），腳本送出佔位值，但：
  - （a）目前不在 Claude Code 雲端環境（沒有代理幫忙注入 key），或
  - （b）雲端環境的 Network secret（`api.edinet-fsa.go.jp`）沒設、已刪除、key 已失效，或 header 名稱不是 `Ocp-Apim-Subscription-Key`。
- 修正步驟：
  1. 本機：設環境變數 `EDINET_API_KEY`（Windows `setx EDINET_API_KEY "你的key"` 後重開終端機／Claude；macOS/Linux 寫進 `~/.bashrc`），或把 `.claude/skills/edinet/.env.example` 複製成 `.env` 填 `EDINET_API_KEY=...`。
  2. 雲端 Claude Code：claude.ai → 雲端環境設定 → Network secrets → 檢查 host `api.edinet-fsa.go.jp`、header `Ocp-Apim-Subscription-Key` 那筆；或請 Claude 呼叫 `request_credential` 重新存 key。
  3. key 失效或遺失：EDINET 首頁 →「API」→ API キー発行，重新登入取得（重新發行後舊 key 立即失效）。
  4. 修好後執行 `python .claude/skills/edinet/scripts/edinet.py checkkey` 確認。
  5. 在修好之前：改走 AGENTS.md §4.2 D/F 替代來源（IR Bank `irbank.net/{代碼}/ir`、Ullet、Futu `{代碼}-JP/announcement`）。

## 2026-11-26 20:02:25 — AUTH_INVALID_KEY

- 指令：`edinet.py list --code 3455`（script v2.0.1，Python 3.11.18，linux）
- 錯誤：API status 401
- 端點：`/api/v2/documents.json`
- 狀態碼：401
- API 回應：`Access denied due to invalid subscription key.Make sure to provide a valid key for an active subscription.`
- key 來源：無（佔位值 → 雲端代理注入）；本機未設定（送佔位值，靠雲端代理注入）
- 可能原因：
  - 本機沒有設定 key（環境變數與 .env 都沒有），腳本送出佔位值，但：
  - （a）目前不在 Claude Code 雲端環境（沒有代理幫忙注入 key），或
  - （b）雲端環境的 Network secret（`api.edinet-fsa.go.jp`）沒設、已刪除、key 已失效，或 header 名稱不是 `Ocp-Apim-Subscription-Key`。
- 修正步驟：
  1. 本機：設環境變數 `EDINET_API_KEY`（Windows `setx EDINET_API_KEY "你的key"` 後重開終端機／Claude；macOS/Linux 寫進 `~/.bashrc`），或把 `.claude/skills/edinet/.env.example` 複製成 `.env` 填 `EDINET_API_KEY=...`。
  2. 雲端 Claude Code：claude.ai → 雲端環境設定 → Network secrets → 檢查 host `api.edinet-fsa.go.jp`、header `Ocp-Apim-Subscription-Key` 那筆；或請 Claude 呼叫 `request_credential` 重新存 key。
  3. key 失效或遺失：EDINET 首頁 →「API」→ API キー発行，重新登入取得（重新發行後舊 key 立即失效）。
  4. 修好後執行 `python .claude/skills/edinet/scripts/edinet.py checkkey` 確認。
  5. 在修好之前：改走 AGENTS.md §4.2 D/F 替代來源（IR Bank `irbank.net/{代碼}/ir`、Ullet、Futu `{代碼}-JP/announcement`）。

## 2026-11-26 20:02:20 — AUTH_INVALID_KEY

- 指令：`edinet.py checkkey`（script v2.0.1，Python 3.11.18，linux）
- 錯誤：API status 401
- 端點：`/api/v2/documents.json`
- 狀態碼：401
- API 回應：`Access denied due to invalid subscription key.Make sure to provide a valid key for an active subscription.`
- key 來源：無（佔位值 → 雲端代理注入）；本機未設定（送佔位值，靠雲端代理注入）
- 可能原因：
  - 本機沒有設定 key（環境變數與 .env 都沒有），腳本送出佔位值，但：
  - （a）目前不在 Claude Code 雲端環境（沒有代理幫忙注入 key），或
  - （b）雲端環境的 Network secret（`api.edinet-fsa.go.jp`）沒設、已刪除、key 已失效，或 header 名稱不是 `Ocp-Apim-Subscription-Key`。
- 修正步驟：
  1. 本機：設環境變數 `EDINET_API_KEY`（Windows `setx EDINET_API_KEY "你的key"` 後重開終端機／Claude；macOS/Linux 寫進 `~/.bashrc`），或把 `.claude/skills/edinet/.env.example` 複製成 `.env` 填 `EDINET_API_KEY=...`。
  2. 雲端 Claude Code：claude.ai → 雲端環境設定 → Network secrets → 檢查 host `api.edinet-fsa.go.jp`、header `Ocp-Apim-Subscription-Key` 那筆；或請 Claude 呼叫 `request_credential` 重新存 key。
  3. key 失效或遺失：EDINET 首頁 →「API」→ API キー発行，重新登入取得（重新發行後舊 key 立即失效）。
  4. 修好後執行 `python .claude/skills/edinet/scripts/edinet.py checkkey` 確認。
  5. 在修好之前：改走 AGENTS.md §4.2 D/F 替代來源（IR Bank `irbank.net/{代碼}/ir`、Ullet、Futu `{代碼}-JP/announcement`）。
