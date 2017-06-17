---
name: Convert2md
description: 掃描 FinancialReport 內所有公司資料夾，將財報（PDF/HTML）轉換為 Markdown，清除 XBRL/iXBRL 標籤與 PDF CID 亂碼，最後產生轉換總結報告。
---
/goal
# Convert2md Skill — 完整執行說明

## 概覽

每次執行此 Skill 時，依序執行以下五個 Phase：

| Phase | 任務說明 | 是否每次都執行？ |
|-------|---------|---------------|
| **Phase 1** | 將 PDF/HTML 財報轉換為 `.md` 檔案 | 僅在有未轉換的檔案時執行 |
| **Phase 2** | 清除所有 `.md` 檔案中的 XBRL / iXBRL **XML 標籤** | **是，每次都執行** |
| **Phase 2.5** | 清除所有 `.md` 檔案中的 **XBRL 純文字 Blob**（iXBRL R-section 殘留） | **是，每次都執行** |
| **Phase 3** | 清除所有 `.md` 檔案中的 PDF CID 亂碼字元 | **是，每次都執行** |
| **Phase 4** | 產生總結報告 `conversion_summary.md` | **是，每次都執行** |

---

## 執行環境規範與防錯指南

> [!IMPORTANT]
> **AI 執行關鍵限制（避免 Convert2md 失敗）：**
> 1. **不可直接呼叫 `markitdown.exe`**：系統中的 `D:\Prog_install\FinanceTool\Scripts\markitdown.exe` 封裝檔有問題，直接呼叫會回傳 `ExitCode 1` 且無任何輸出。
> 2. **必須使用 Python 模組呼叫**：轉換指令必須改為 `D:\Prog_install\FinanceTool\Scripts\python.exe -m markitdown`。
> 3. **避免 Windows 命令列中文路徑亂碼**：若直接在 PowerShell/CMD 傳遞包含中文（如 `00546阜豐`）的 inline Python 指令（例如 `python -c "..."`），會因為 Windows 終端機參數編碼解析問題導致路徑損毀。**強烈建議：先在 Scratch 目錄建立暫存 `.py` 檔案再執行，或使用 PowerShell 傳遞原生參數。**

- **工具絕對路徑與正確指令**：
  * Python 執行檔路徑：`D:\Prog_install\FinanceTool\Scripts\python.exe`
  * 轉換指令：`D:\Prog_install\FinanceTool\Scripts\python.exe -m markitdown`
- **推薦做法 (A)：撰寫並執行暫存 Python 腳本（最穩定，推薦 AI 使用）**
  1. 在 `<appDataDir>\brain\<conversation-id>\scratch\` 底下建立暫存 `convert.py`
  2. 使用 `open(..., encoding='utf-8')` 讀寫檔案，並使用 `subprocess.run(["D:\\Prog_install\\FinanceTool\\Scripts\\python.exe", "-m", "markitdown", src, "-o", dest], capture_output=True, text=True, encoding='utf-8')` 進行轉換。
  3. 執行該 Python 檔案：`D:\Prog_install\FinanceTool\Scripts\python.exe convert.py`
- **推薦做法 (B)：使用 PowerShell `Start-Process`（適合直接命令行執行）**
  若要直接透過 PowerShell 執行，為避免編碼與空格問題，必須使用以下格式：
  ```powershell
  $proc = Start-Process -FilePath "D:\Prog_install\FinanceTool\Scripts\python.exe" `
    -ArgumentList "-m markitdown `"$pdfPath`" -o `"$mdPath`"" `
    -Wait -PassThru -NoNewWindow `
    -RedirectStandardError "C:\Temp\mkd_err.txt" `
    -RedirectStandardOutput "C:\Temp\mkd_out.txt"
  if ($proc.ExitCode -ne 0) { Write-Error "Convert failed: $(Get-Content C:\Temp\mkd_err.txt)" }
  ```
- **編碼設定**：
  - 若使用 PowerShell，執行前先強制設定 UTF-8：
    ```powershell
    [System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
    ```
  - 若使用 Python `subprocess`，設定 `encoding='utf-8'`，並在環境變數加入 `PYTHONIOENCODING=utf-8`。

---

## Phase 1 — 將 PDF / HTML 轉換為 Markdown
### Step 1.1 — 掃描待轉換檔案
遞迴掃描 `FinancialReport` 底下所有公司子資料夾，對每個 `.pdf` 或 `.html` 檔案執行以下判斷：
| 條件 | 動作 |
|------|------|
| 同目錄下已存在**同名** `.md` 檔案，且檔案大小 > 0 bytes | **跳過**（視為已轉換） |
| 同名 `.md` 不存在，或現有 `.md` 大小為 0 bytes | **執行轉換** |
### Step 1.2 — 執行轉換
對每個需轉換的檔案執行以下指令：
```
D:\Prog_install\FinanceTool\Scripts\python.exe -m markitdown "C:\絕對路徑\report.pdf" -o "C:\絕對路徑\report.md"
```
### Step 1.3 — 轉換後清理

確認轉換**成功**（輸出的 `.md` 存在且大小 > 0）後：

1. **刪除原始來源檔案**（PDF 或 HTML）。
2. **刪除同資料夾內同名或對應相同報告期間的舊版 `.md` 檔案**，只保留最新生成的版本。

**安全防護規則（嚴格執行）：**

| 規則 | 說明 |
|------|------|
| ❌ 刪除指令禁止使用萬用字元（`*`） | 必須指定精確的單一檔案路徑 |
| ❌ 禁止刪除非自動生成的檔案 | 不可刪除人工分析筆記、`.git`、設定檔或任何手動撰寫的文件 |
| ✅ 只允許刪除 | 已轉換成功的 PDF/HTML 來源檔，以及被取代的舊版同名 `.md` 檔 |

---

## Phase 2 — 清除所有 `.md` 檔案中的 XBRL / iXBRL 標籤
> **此 Phase 每次都必須執行**，無論 Phase 1 是否有執行。
### 掃描範圍

遞迴掃描 `FinancialReport` 底下**所有子目錄**中的 `.md` 檔案。
### 黃金法則

| 規則 | 範例 |
|------|------|
| ✅ 只刪標籤，保留標籤內的內容 | `<ix:nonFraction ...>123,456</ix:nonFraction>` → 清理後保留 `123,456` |
| ❌ 禁止整行或整塊刪除含有數值或文字的內容 | 含財報數據的行不可直接整行刪除 |
| ✅ 使用 Python，Regex 加上 `re.DOTALL` flag | 標籤可能跨越多行 |
| ✅ 用迴圈逐檔處理 | 不可用手動或純 Shell 替換 |

### 清理規則（依序套用，共 4 條）
---
**規則 1 — 整塊刪除：iXBRL header 與 metadata 區塊**

這些區塊對閱讀完全無益，**直接整塊刪除**（標籤與其內部所有內容一起刪）。

| 目標 | Regex | 替換為 |
|------|-------|--------|
| `<ix:header>` 整塊 | `<ix:header[\s\S]*?</ix:header>` | `""` |
| `<link:schemaRef>` 自閉合標籤 | `<link:schemaRef[^>]*/\s*>` | `""` |

---

**規則 2 — 剝標籤，保留內容：iXBRL 數值與文字標籤**

這些標籤包裹著真實的財務數值，**只刪標籤，保留括號內的內容**。

| 目標標籤 | Regex | 替換為 |
|---------|-------|--------|
| `<ix:nonFraction>` | `<ix:nonFraction[^>]*>(.*?)</ix:nonFraction>` | `\1` |
| `<ix:nonNumeric>` | `<ix:nonNumeric[^>]*>(.*?)</ix:nonNumeric>` | `\1` |
| 其他所有 `<ix:*>` 標籤 | `<ix:[a-zA-Z0-9_-]+[^>]*>([\s\S]*?)</ix:[a-zA-Z0-9_-]+>` | `\1` |

---

**規則 3 — 刪除：自閉合或空的 ix 標籤**

未包裹任何內容的自閉合標籤，**直接刪除**。

| 目標 | Regex | 替換為 |
|------|-------|--------|
| 自閉合 `<ix:*/>` | `<ix:[^>]+/>` | `""` |

---

**規則 4 — 選擇性清理：XML namespace 聲明**

**僅在** namespace 聲明出現於段落中間、影響閱讀時才執行。

| 目標 | Regex | 替換為 |
|------|-------|--------|
| `xmlns:ix="..."` | `xmlns:ix="[^"]*"` | `""` |
| `xmlns:xbrli="..."` | `xmlns:xbrli="[^"]*"` | `""` |
| 其他 xmlns 聲明 | `xmlns:[a-z]+="[^"]*"` | `""` |

---

## Phase 2.5 — 清除所有 `.md` 檔案中的 XBRL 純文字 Blob
> **此 Phase 每次都必須執行**，無論 Phase 1 是否有執行。

### 背景說明（為何需要此 Phase）

`markitdown` 在轉換 SEC iXBRL 格式財報（如 10-K、10-Q）時，會把 `<ix:header>` 區塊內的 **XBRL R-section（context/footnote 鍵值對映射表）** 的 XML 標籤剝除，並將內容以**超長純文字**直接輸出到 `.md` 檔案頂部。

這類殘留**沒有任何 XML 標籤**，因此 Phase 2 的 Regex 規則完全無法匹配。

典型外觀（單行，長度可達 30,000–60,000 字元）：
```
falseP4Y0000352915--12-31FY0.010.01http://fasb.org/us-gaap/2023#Other...0000352915uhs:UniversalHealthRealtyIncomeTrustMemberus-gaap:InvestmentAdviceMember2022-01-012022-12-31...
```

### 掃描範圍

遞迴掃描 `FinancialReport` 底下**所有子目錄**中的 `.md` 檔案。

### 偵測條件（同時滿足以下三個條件才視為 XBRL Blob）

| 條件 | 說明 |
|------|------|
| ① 行長 > 500 字元 | 正常財報段落不會有如此長的單行 |
| ② 含 ≥ 3 個 CIK+Namespace 模式 | Regex：`\d{10}[a-zA-Z][a-zA-Z0-9_\-]*:[a-zA-Z]`，代表 SEC CIK 碼接 XBRL namespace |
| ③ 空白比例 < 2% | 計算 `空格數 / 行長`，正常英文句子空白比遠高於 2% |

### 清理規則

| 動作 | 說明 |
|------|------|
| ✅ 整行刪除符合條件的 XBRL Blob 行 | 這類行完全沒有財報閱讀價值 |
| ✅ 同時偵測並刪除 unit/measure 尾段 Blob | 單行由純 `namespace:Name` 串接組成、無空格、長度 20–500 字元，Regex：`^(?:[a-zA-Z][a-zA-Z0-9_\-]*:[a-zA-Z][a-zA-Z0-9_\-]*){3,}$` |
| ✅ 清除後收縮多餘空行 | 將連續 4 個以上空行壓縮為 3 個 |
| ❌ 禁止刪除含有正常財報數字或文字的行 | 任何包含財務數據、段落標題的行絕對不可刪 |

### Python 實作要點

```python
import re

CIK_NAMESPACE_PATTERN = re.compile(r'\d{10}[a-zA-Z][a-zA-Z0-9_\-]*:[a-zA-Z]')
UNIT_BLOB_PATTERN = re.compile(r'^(?:[a-zA-Z][a-zA-Z0-9_\-]*:[a-zA-Z][a-zA-Z0-9_\-]*){3,}$')

for line in lines:
    stripped = line.strip()
    # 偵測主 Blob（超長行）
    if len(stripped) > 500:
        cik_matches = CIK_NAMESPACE_PATTERN.findall(stripped)
        space_ratio = stripped.count(' ') / len(stripped)
        if len(cik_matches) >= 3 and space_ratio < 0.02:
            continue  # 刪除此行
    # 偵測 unit/measure 尾段 Blob
    if 20 < len(stripped) < 500 and ':' in stripped:
        if UNIT_BLOB_PATTERN.match(stripped) and stripped.count(' ') == 0:
            continue  # 刪除此行
    cleaned_lines.append(line)
```

---

## Phase 3 — 清除所有 `.md` 檔案中的 PDF CID 亂碼
> **此 Phase 每次都必須執行**，無論 Phase 1 是否有執行。
### 掃描範圍

遞迴掃描 `FinancialReport` 底下**所有子目錄**中的 `.md` 檔案。

### 偵測條件（符合任一條件即需清理）

| 條件 | 偵測方式 |
|------|---------|
| 含有 CID 標籤 | 檔案內容符合 Regex `\(cid:\d+\)` |
| 高密度亂碼字元 | 某段落充斥 `æ`、`fl`、`(cid:129)` 等孤立、無語意的字元 |

### 清理規則

| 動作 | 說明 |
|------|------|
| ✅ 將所有 `(cid:\d+)` 替換掉 | 替換為 `""` 或單一空格（避免字詞黏連） |
| ✅ 移除明顯的轉檔雜訊字元 | 僅限於孤立的 `æ`、`fl` 等確定是垃圾的字元，不可誤刪正常英文單字或中文字元 |
| ✅ 刪除純亂碼段落 | 僅限於整段完全由 CID 標籤或無意義字元組成、無任何財報數據的段落 |
| ❌ 禁止刪除含有真實數字或會計科目的行或段落 | 財報數據必須完整保留 |

---

## Phase 4 — 產生總結報告

所有 Phase 執行完畢後，在 `FinancialReport` 根目錄產生 **`conversion_summary.md`**，並在最終回覆中以 Markdown 格式呈現。

### 報告結構

#### Section 1 — 統計數據概覽

| 指標 | 數量 |
|------|------|
| 總掃描檔案數 | |
| 成功轉換數 | |
| 跳過（已存在）數 | |
| 轉換失敗數 | |
| XBRL 標籤清理檔案數 | |
| XBRL 純文字 Blob 清理檔案數 | |
| CID 亂碼清理檔案數 | |
| 異常警告數（含 0 KB 檔案 + CID 亂碼） | |

#### Section 2 — 異常詳細清單（Markdown 表格）
**表格 A — 輸出為 0 KB 的檔案**

| 公司名稱 | 原始檔案 | 生成的 .md | 可能原因 |
|---------|---------|-----------|---------|

**表格 B — 轉換失敗的檔案**

| 公司名稱 | 原始檔案 | 錯誤原因 / Stack Trace |
|---------|---------|----------------------|

**表格 C — 偵測到 CID 亂碼的檔案**

| 公司名稱 | 生成的 .md | 亂碼特徵 | 是否已清理？ |
|---------|-----------|---------|------------|

---

## 異常處理規則

| 情況 | 必要動作 |
|------|---------|
| 單一檔案轉換失敗 | 記錄錯誤 → **繼續**處理下一個檔案，不可中止整個批次 |
| 單一檔案標籤清理失敗（如編碼錯誤） | 記錄錯誤 → 繼續處理下一個檔案 |
| 所有錯誤 | 統一記錄至 `conversion_summary.md`，包含檔案路徑與原因 |
