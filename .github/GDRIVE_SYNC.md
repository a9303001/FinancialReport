# GitHub → Google Drive 自動同步（GitHub Actions + rclone）

Workflow：`.github/workflows/sync-gdrive.yml`

## 運作方式

- **方向**：單向。GitHub `master` → Google Drive `FinancialReport/`。Drive 上手動改的檔案會在下次同步時被 GitHub 版本蓋掉（不做備份）。
- **何時跑**：
  - 有人直接 push 到 `master`
  - `Auto merge into master` workflow 成功跑完（auto-merge 用 `GITHUB_TOKEN` 合併，GitHub 不會因此發 push 事件，所以要靠 `workflow_run` 接手）
  - 每天台灣時間 03:43 一次保險
  - 手動：Actions → Sync to Google Drive → Run workflow（可勾 dry run / force）
- **不重傳**：用 `--checksum`（MD5）比對，只傳有變動的檔案；同一個 commit 同步成功後會記在 Actions cache，下次 master 沒變就直接跳過。
- **不同步**：`.git/`。其餘（含 `.github/`、`.claude/`）全部同步。
- **不做備份**：被覆蓋的檔案直接換成新版；repo 已刪除的檔案會移到 Google Drive **垃圾桶**（30 天後永久刪除）。要找舊版請看 GitHub 的 git 歷史。
- **安全網**：單次要刪超過 1000 個檔案就中止（防止設錯路徑把 Drive 清空）

## 一次性設定（約 10 分鐘）

### 1. 建立自己的 Google OAuth Client（強烈建議）

rclone 文件寫明內建的共用 client ID 會在 2026 年內停用，所以一定要自己建一個。

1. 開 <https://console.cloud.google.com/> → 左上專案選單 → **New Project**（例如 `rclone-sync`）→ 建好後切換到這個專案
2. 左側選單 **APIs & Services → Library** → 搜尋 `Google Drive API` → **Enable**
3. 左側選單 **Google Auth Platform**（舊版叫 *OAuth consent screen*）→ **Get started**：
   - App name：`rclone`；User support email：自己的 Gmail
   - Audience：**External**
   - Contact information：自己的 Gmail → 勾同意條款 → **Create**
4. **Data Access** → **Add or remove scopes** → 勾 `https://www.googleapis.com/auth/drive`（找不到就貼到 *Manually add scopes*）→ **Update** → **Save**
5. **Audience** → Test users **+ Add users** → 加自己的 Gmail → Save
6. **Clients**（或 Overview → *Create OAuth client*）→ Application type 選 **Desktop app** → Name 隨意 → **Create** → 記下 *Client ID* 與 *Client secret*（可按 Download JSON 備份）
7. ⚠️ **Audience** → Publishing status 下按 **Publish app** → Confirm，狀態變成 **In production**。
   若停留在 *Testing*，refresh token **7 天就會失效**，同步會開始報 `invalid_grant`。
   個人使用（< 100 人）不需要送 Google 審核；授權時出現「Google 尚未驗證這個應用程式」→ **進階 → 前往 rclone（不安全）** 即可。
   若 *Publish app* 是灰色的：到 **Branding** 填 App home page、Privacy policy 連結並加 Authorized domain 後再回來按。

### 2. 在自己電腦產生 rclone.conf

安裝 rclone（<https://rclone.org/downloads/>），然後：

```bash
rclone config
# n) New remote
# name> gdrive                      ← 名稱要是 gdrive（或另外設 Variable GDRIVE_REMOTE）
# Storage> drive
# client_id> （貼上步驟 1 的 Client ID）
# client_secret> （貼上 Client secret）
# scope> 1   (drive，完整存取；若只想讓 rclone 碰它自己建的檔案可選 3 = drive.file)
# 其餘一路 Enter，Use web browser to automatically authenticate? y → 瀏覽器登入授權
# Configure this as a Shared Drive? n

rclone lsd gdrive:          # 測試，能列出 Drive 根目錄就成功
rclone config file          # 顯示 rclone.conf 的路徑
```

### 3. 把 rclone.conf 存進 GitHub Secret

GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**

- Name：`RCLONE_CONF`
- Secret：把 `rclone.conf` 裡 `[gdrive]` 那一段**整段**貼上（純文字即可；也接受 base64 編碼後的內容）

```ini
[gdrive]
type = drive
client_id = xxxxx.apps.googleusercontent.com
client_secret = xxxxx
scope = drive
token = {"access_token":"...","token_type":"Bearer","refresh_token":"...","expiry":"..."}
team_drive =
```

> rclone.conf 裡有 refresh token，等同你 Google Drive 的鑰匙，**只放在 Secret，絕對不要 commit 進 repo**。

### 4.（選用）用 Variables 改設定

**Settings → Secrets and variables → Actions → Variables**

| Variable | 預設值 | 說明 |
|---|---|---|
| `GDRIVE_REMOTE` | `gdrive` | rclone.conf 中的 remote 名稱 |
| `GDRIVE_PATH` | `FinancialReport` | Drive 上的目標資料夾（從 My Drive 根目錄算起，可用 `A/B/C`） |
| `GDRIVE_MAX_DELETE` | `1000` | 單次最多刪幾個檔，超過就中止；`-1` 表示不限制 |

### 5. 第一次執行

Actions → **Sync to Google Drive** → Run workflow：

1. 先勾 **dry_run** 跑一次，看 Summary 確認目的地與檔案數對不對
2. 再取消 dry_run 正式跑（第一次約 800+ 個檔案、~100 MB）

## 常見問題

- **`invalid_grant` / `token expired`**：OAuth app 還在 *Testing*（7 天過期）或 6 個月沒用。改成 *In production* 後在電腦重跑 `rclone config reconnect gdrive:`，再把新的 rclone.conf 更新到 Secret。
- **`403 rateLimitExceeded`**：通常是用了 rclone 共用 client ID，改用自己的 client（步驟 1）。workflow 已設 `--tpslimit 10` 與重試。
- **`Max delete limit reached`**：一次要刪的檔案超過 `GDRIVE_MAX_DELETE`。確認不是路徑設錯後，暫時把 Variable 調高再跑。
- **為什麼不用 Service Account**：個人 Gmail 的 Service Account 沒有 My Drive 儲存空間，上傳會出現 `storageQuotaExceeded`；只有 Google Workspace 的共用雲端硬碟（Shared Drive）才適用。
- **舊的 `FinancialReport_sync_backup/` 資料夾**：早期版本用 `--backup-dir` 留下的備份，現在已不再產生，可直接在 Drive 上手動刪除。
