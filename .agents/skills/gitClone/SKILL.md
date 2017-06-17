---
name: gitClone
description: 執行 git clone 時一律使用淺層複製（shallow clone），只抓最新一筆 commit、不下載完整 git 歷史，以大幅加速 clone；若本機已存在該 repo，改為淺層更新（fetch --depth 1）而非重新 clone。使用者要求 clone repo、複製專案、下載程式碼、更新本機 repo 時觸發。
---

# gitClone Skill — 只抓最新 commit 的快速 clone / 本機已存在則改為更新

## 核心規則
- **禁止**使用預設的 `git clone <url>`（會下載全部歷史）。
- **一律加上 `--depth 1`**，只取最新一筆 commit。
- 預設同時加上 `--single-branch`（只抓目標分支）與 `--no-tags`（不抓標籤）。
- **clone 前必須先偵測本機目標目錄**：已存在同一個 repo 就改走「更新流程」，不要重新 clone、更不要刪掉重來。
- 若使用者未指定分支，就用遠端預設分支；本專案（`a9303001/FinancialReport`）的預設分支是 **`master`**，不是 `main`。
- **禁止**在未確認的情況下對目標目錄執行 `rm -rf` / `Remove-Item -Recurse`（可能誤刪使用者資料或未推送的工作）。
- 收尾必須回報：走的是 clone 還是更新、實際指令、分支、commit hash、耗時/大小（`du -sh .git`），並提醒這是淺層 repo。

---

## 決策流程（每次都先跑這一段）

```
目標目錄存在？
├─ 否 ──────────────────────────────► [情境 A] 淺層 clone
└─ 是
   ├─ 目錄是空的 ──────────────────► [情境 A] 直接 clone 進該目錄
   ├─ 是 git repo？
   │  ├─ 是 → remote URL 與目標相同？
   │  │        ├─ 相同 ─────────────► [情境 B] 淺層更新（最常見）
   │  │        └─ 不同 ─────────────► [情境 D] 停下來回報，等使用者決定
   │  └─ 否（有檔案但非 git）───────► [情境 C] 就地 init + fetch，不刪檔
```

### 偵測指令（唯讀，先跑這個）

```bash
TARGET=/home/user/FinancialReport          # 或 D:\FinancialReport
URL=https://github.com/a9303001/FinancialReport.git
BRANCH=master

if [ ! -d "$TARGET" ] || [ -z "$(ls -A "$TARGET" 2>/dev/null)" ]; then
  echo "STATE=absent_or_empty"
elif git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1; then
  echo "STATE=git_repo"
  echo "REMOTE=$(git -C "$TARGET" remote get-url origin 2>/dev/null)"
  echo "BRANCH=$(git -C "$TARGET" rev-parse --abbrev-ref HEAD)"
  echo "HEAD=$(git -C "$TARGET" rev-parse --short HEAD)"
  echo "SHALLOW=$(git -C "$TARGET" rev-parse --is-shallow-repository)"
  echo "DIRTY=$(git -C "$TARGET" status --porcelain | wc -l)"
else
  echo "STATE=non_git_dir"
fi
```

PowerShell 版：

```powershell
$Target = 'D:\FinancialReport'
if (-not (Test-Path $Target) -or -not (Get-ChildItem $Target -Force)) {
  'STATE=absent_or_empty'
} elseif (Test-Path (Join-Path $Target '.git')) {
  'STATE=git_repo'
  git -C $Target remote get-url origin
  git -C $Target rev-parse --abbrev-ref HEAD
  git -C $Target rev-parse --is-shallow-repository
  git -C $Target status --porcelain
} else { 'STATE=non_git_dir' }
```

> remote URL 比對要**正規化**再比：忽略結尾 `.git`、大小寫、`https://` 與 `git@github.com:` 的差異。
> 例如 `https://github.com/a9303001/FinancialReport.git`、`git@github.com:a9303001/FinancialReport.git`、`https://github.com/A9303001/financialreport` 視為**同一個 repo**。

---

## 情境 A：本機沒有 → 淺層 clone

### 基本（最快，只有最新 commit）
```bash
git clone --depth 1 --single-branch --no-tags <repo-url> <目標目錄>
```

### 指定分支
```bash
git clone --depth 1 --single-branch --no-tags --branch master <repo-url> <目標目錄>
```


### 只需要部分目錄（大 repo 再快一階）
```bash
git clone --depth 1 --single-branch --no-tags --filter=blob:none --sparse <repo-url> <目標目錄>
git -C <目標目錄> sparse-checkout set <資料夾1> <資料夾2>
```
本 repo（FinancialReport）只要分析單一公司時特別有效，例如只抓 `UHS/`。

### PowerShell 範例
```powershell
git clone --depth 1 --single-branch --no-tags --branch master https://github.com/a9303001/FinancialReport.git D:\FinancialReport
```

---

## 情境 B：本機已有同一個 repo → 淺層更新（**不要重 clone**）

重 clone 會浪費頻寬與時間，還可能毀掉本機未推送的工作。一律改用淺層 fetch。

### B-1 先檢查有沒有未提交的變更（必做）
```bash
git -C "$TARGET" status --porcelain
```
- **有變更** → 不可直接 `reset --hard`。先擇一並向使用者回報：
  ```bash
  git -C "$TARGET" stash push -u -m "gitClone-skill-autostash"   # 保留變更
  ```
  或改用不破壞工作區的 `git pull --rebase`（見 B-3）。
- **無變更** → 直接進 B-2。

### B-2 乾淨工作區：強制同步到遠端最新（維持淺層）
```bash
git -C "$TARGET" fetch --depth 1 --no-tags origin master
git -C "$TARGET" reset --hard origin/master
git -C "$TARGET" clean -fd          # 需要清掉未追蹤檔案時才加，會刪檔，先問過使用者
```

### B-3 有本地 commit / 想保留變更：淺層 rebase 更新
```bash
git -C "$TARGET" pull --rebase --depth 1 --no-tags origin master
```
若被 stash 過，最後記得還原並回報衝突狀況：
```bash
git -C "$TARGET" stash pop
```

### B-4 已經是最新就不要做多餘的事
```bash
git -C "$TARGET" fetch --depth 1 --no-tags origin master
LOCAL=$(git -C "$TARGET" rev-parse HEAD)
REMOTE=$(git -C "$TARGET" rev-parse FETCH_HEAD)
[ "$LOCAL" = "$REMOTE" ] && echo "已是最新，略過更新"
```

### B-5 本機是淺層 + single-branch，但要換到別的分支
淺層 clone 只有一條 branch 的 refspec，直接 `checkout other-branch` 會失敗。要先補抓：
```bash
git -C "$TARGET" remote set-branches --add origin <新分支>
git -C "$TARGET" fetch --depth 1 --no-tags origin <新分支>
git -C "$TARGET" checkout -B <新分支> origin/<新分支>
```

### B-6 本機是完整 clone，想瘦身成淺層
```bash
git -C "$TARGET" fetch --depth 1 --no-tags origin master
git -C "$TARGET" reset --hard origin/master
git -C "$TARGET" reflog expire --expire=now --all
git -C "$TARGET" gc --prune=now --aggressive
du -sh "$TARGET/.git"
```

### B-7 反過來：淺層 repo 需要完整歷史（要 blame / 查舊 commit 時）
```bash
git -C "$TARGET" fetch --unshallow
```
這會下載全部歷史，**只在使用者明確需要歷史時才做**，並事先告知會變慢。

---

## 情境 C：目錄有檔案但不是 git repo → 就地接管，不刪檔

`git clone` 會拒絕寫入非空目錄。**不要刪目錄**，改成就地初始化：

```bash
git -C "$TARGET" init
git -C "$TARGET" remote add origin <repo-url>
git -C "$TARGET" fetch --depth 1 --no-tags origin master
git -C "$TARGET" checkout -B master origin/master   # 同名檔案會被遠端版本覆蓋，先提醒使用者
```
若不想覆蓋既有檔案，改 clone 到新目錄（例如 `<目標目錄>-new`）再請使用者自行比對。

---

## 情境 D：目錄是 git repo 但 remote 不同 → 停下來

**不要**自動改 remote、不要刪目錄。回報以下資訊給使用者，並提供選項：

- 本機路徑、目前 remote URL、目前分支、HEAD、是否有未提交變更
- 選項：(1) clone 到另一個目錄 (2) 由使用者確認後 `git remote set-url origin <新 url>` (3) 取消

---

## 收尾回報範本

```
動作：更新既有 repo（未重新 clone）
路徑：D:\FinancialReport
遠端：https://github.com/a9303001/FinancialReport.git
分支：master
指令：git fetch --depth 1 --no-tags origin master && git reset --hard origin/master
結果：a1b2c3d → e4f5g6h（更新 12 個檔案）
.git 大小：18M（淺層 repo，無完整歷史；需要 blame 請先 git fetch --unshallow）
未提交變更：無
```

## 常見錯誤與對策
| 訊息 | 原因 | 對策 |
|---|---|---|
| `destination path ... already exists and is not an empty directory` | 目錄已有內容 | 走情境 B / C，別刪目錄 |
| `fatal: refusing to merge unrelated histories` | 本機 repo 與遠端無共同歷史 | 確認是不是同一個 repo（情境 D） |
| `error: pathspec '<branch>' did not match` | 淺層 single-branch 沒抓到該分支 | 用 B-5 補抓分支 |
| `shallow update not allowed` | 想從淺層 repo push 到別的遠端 | 先 `git fetch --unshallow` |
| `fatal: repository ... not found`（404） | 分支用了 `main` 而非 `master`，或無權限 | 本 repo 預設分支是 `master` |
