---
name: rg
description: 當 Gemini 或 Claude 需要使用 ripgrep（rg）進行搜尋時，一律使用本機已安裝的 D:\Prog_install\ripgrep\rg.exe，不要依賴 PATH 中的 rg 或其他搜尋工具。
---

# rg Skill — ripgrep 搜尋規範

## 核心規則
- 任何時候 AI（Gemini 或 Claude）需要以 ripgrep（rg）做內容/檔名搜尋，**一律使用以下絕對路徑的執行檔**：
  - `D:\Prog_install\ripgrep\rg.exe`
- **不要**直接呼叫 `rg`（依賴 PATH），也**不要**改用 `grep` / `findstr` / `Select-String` 取代，除非該路徑的 rg.exe 不存在。

## 使用方式

### PowerShell（用呼叫運算子 `&`，路徑含空白時必加引號）
```powershell
& "D:\Prog_install\ripgrep\rg.exe" "搜尋字串" "搜尋目錄"
```

### Bash 工具（Git Bash）
```bash
"D:/Prog_install/ripgrep/rg.exe" "pattern" "path"
```

## 常用範例
```powershell
# 在專案中搜尋關鍵字（顯示行號）
& "D:\Prog_install\ripgrep\rg.exe" -n "EPS" "D:\FinancialReport"

# 只搜尋特定副檔名
& "D:\Prog_install\ripgrep\rg.exe" -n --glob "*.md" "營收"

# 不分大小寫
& "D:\Prog_install\ripgrep\rg.exe" -in "revenue"

# 只列出有命中的檔案路徑
& "D:\Prog_install\ripgrep\rg.exe" -l "ROE"
```

## 注意事項
- 路徑含空白或中文時，務必用雙引號包住。
- 若 `D:\Prog_install\ripgrep\rg.exe` 不存在，先回報缺口，再考慮其他搜尋方式。
- 版本確認：`& "D:\Prog_install\ripgrep\rg.exe" --version`。