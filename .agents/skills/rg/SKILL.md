---
name: rg
description: 當 Gemini 或 Claude 需要使用 ripgrep（rg）進行搜尋時的執行檔選用規範。優先使用環境預設的 rg（PATH 或內建 Grep 工具）；找不到時改用 D:\Prog_install\ripgrep\rg.exe；兩者皆無時由 AI 自行判斷最佳搜尋方式。
---

# rg Skill — ripgrep 搜尋規範

## 核心規則：依序 fallback

AI（Gemini 或 Claude）需要以 ripgrep（rg）做內容／檔名搜尋時，**依下列順序**選用執行方式，**找到可用的就停止，不要再往下試**：

### 第 1 順位：環境預設的 rg
- Claude Code 內建的 **Grep 工具**本身就是 ripgrep 實作，能用就優先用（免權限提示、輸出已最佳化）。
- 或直接呼叫 PATH 中的 `rg`。
- 適用環境：Claude Code Cloud（Linux container，已內建 `/usr/bin/rg`）、WSL、macOS、以及已把 rg 加入 PATH 的 Windows 本機。
- 確認方式：
  ```bash
  # Linux / macOS / Git Bash
  which rg && rg --version
  ```
  ```powershell
  # PowerShell
  Get-Command rg -ErrorAction SilentlyContinue
  ```

### 第 2 順位：Windows 本機絕對路徑
- 若第 1 順位不可用（PATH 沒有 rg、內建 Grep 工具也不能用），改用本機已安裝的執行檔：
  - `D:\Prog_install\ripgrep\rg.exe`
- **限 Windows 本機環境**。在 Linux／雲端 container 中不存在 D 槽，不需嘗試。

### 第 3 順位：AI 自行判斷最佳做法
- 若上述兩者皆不存在，**不要卡住或直接放棄**，由 AI 依當下環境自行選擇最合適的替代方案，例如：
  - 內建檔案搜尋工具（Grep / Glob / `grep_search`）
  - `grep -rn` / `git grep`（Linux、macOS、Git Bash）
  - `Select-String` / `findstr`（Windows PowerShell、CMD）
  - 以套件管理器安裝 rg（`apt install ripgrep`、`brew install ripgrep`、`winget install BurntSushi.ripgrep.MSVC`）
- **回報義務**：在回覆中簡短註明「預設 rg 與 D 槽 rg.exe 皆不可用，改用 ○○ 方式搜尋」，讓使用者知道實際採用的管道。

## 使用方式

### 第 1 順位（PATH 中的 rg）
```bash
# Linux / macOS / Git Bash
rg -n "pattern" "path"
```
```powershell
# PowerShell
rg -n "pattern" "path"
```

### 第 2 順位（Windows 絕對路徑）
```powershell
# PowerShell：用呼叫運算子 &，路徑含空白時必加引號
& "D:\Prog_install\ripgrep\rg.exe" "搜尋字串" "搜尋目錄"
```
```bash
# Git Bash
"D:/Prog_install/ripgrep/rg.exe" "pattern" "path"
```

## 常用範例

以下以第 1 順位的 `rg` 為例；若退到第 2 順位，把 `rg` 換成 `& "D:\Prog_install\ripgrep\rg.exe"` 即可，參數完全相同。

```bash
# 在專案中搜尋關鍵字（顯示行號）
rg -n "EPS" /home/user/FinancialReport

# 只搜尋特定副檔名
rg -n --glob "*.md" "營收"

# 不分大小寫
rg -in "revenue"

# 只列出有命中的檔案路徑
rg -l "ROE"
```

## 注意事項
- 路徑含空白或中文時，務必用雙引號包住。
- 跨平台路徑差異：雲端／Linux 用 `/home/user/FinancialReport`，Windows 本機用 `D:\FinancialReport`；不要把兩者混用。
- 版本確認：`rg --version`，或 `& "D:\Prog_install\ripgrep\rg.exe" --version`。
- 不需為了「確認第 2 順位是否存在」而在 Linux 環境嘗試存取 D 槽——先判斷作業系統再決定。
