---
name: gitClone
description: 執行 git clone 時一律使用淺層複製（shallow clone），只抓最新一筆 commit、不下載完整 git 歷史，以大幅加速 clone。使用者要求 clone repo、複製專案、下載程式碼時觸發。
---

# gitClone Skill — 只抓最新 commit 的快速 clone

## 核心規則
- **禁止**使用預設的 `git clone <url>`（會下載全部歷史）。
- **一律加上 `--depth 1`**，只取最新一筆 commit。
- 預設同時加上 `--single-branch`（只抓目標分支）與 `--no-tags`（不抓標籤）。
- 若使用者未指定分支，就用遠端預設分支；本專案（`a9303001/FinancialReport`）的預設分支是 **`master`**，不是 `main`。
- clone 完成後回報：實際使用的指令、分支、耗時/大小（可用 `du -sh .git`），並提醒這是淺層 repo。

## 標準指令

### 基本（最快，只有最新 commit）
```bash
git clone --depth 1 --single-branch --no-tags <repo-url> <目標目錄>
```

### 指定分支
```bash
git clone --depth 1 --single-branch --no-tags --branch master <repo-url> <目標目錄>
```

### 含子模組（submodule 也淺層）
```bash
git clone --depth 1 --single-branch --no-tags --shallow-submodules --recurse-submodules <repo-url> <目標目錄>
```

### PowerShell 範例
```powershell
git clone --depth 1 --single-branch --no-tags --branch master https://github.com/a9303001/FinancialReport.git D:\FinancialReport
```

## 淺層 repo 的後續操作

### 更新（維持淺層，不長回完整歷史）
```bash
git pull --depth 1
# 或
git fetch --depth 1 origin master && git reset --hard origin/master
```
