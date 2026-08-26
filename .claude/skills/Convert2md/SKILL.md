---
name: Convert2md
description: 掃描 FinancialReport 內所有公司資料夾，將財報（PDF/HTML）轉換為 Markdown，清除 XBRL/iXBRL 標籤與 XBRL 純文字殘留，偵測 PDF CID 亂碼並自動刪除轉換失敗的檔案，最後產生轉換總結報告。
---
/goal
# Convert2md Skill — 完整執行說明

## 概覽

每次執行此 Skill 時，依序執行以下流程（若 Phase 0 檢查失敗則直接跳至 Phase 4）：

| Phase | 任務說明 | 是否每次都執行？ |
|-------|---------|-----------------|
| **Phase 0** | 環境依賴檢查（確認 `markitdown` 可用） | **是，最優先** |
| **Phase 1** | PDF/HTML → Markdown 轉換 + **CID 亂碼檢查** | 有未轉換檔案時執行 |
| **Phase 2** | 清除 `.md` 中的 XBRL / iXBRL XML 標籤 | **是，每次都執行** |
| **Phase 2.5** | 清除 `.md` 中的 XBRL 純文字 Blob | **是，每次都執行** |
| **Phase 3** | 產生總結報告 `conversion_summary.md` | **是，每次都執行** |

> [!IMPORTANT]
> **與舊版的關鍵差異**：不再嘗試清理 PDF CID 亂碼字元。
> 若 PDF 轉出的 `.md` 檔含有過多 CID 亂碼，直接判定為**轉換失敗**，刪除該 `.md` 檔，並在 `conversion_summary.md` 中記錄。

---

## 執行環境規範與防錯指南

> [!IMPORTANT]
> **AI 執行關鍵限制（Claude / Gemini 必讀）：**
> 1. **禁止直接呼叫 `markitdown.exe`**：`D:\Prog_install\FinanceTool\Scripts\markitdown.exe` 封裝檔有問題，直接呼叫會回傳 `ExitCode 1` 且無輸出。
> 2. **必須用 Python 模組方式呼叫**：`D:\Prog_install\FinanceTool\Scripts\python.exe -m markitdown`。
> 3. **Windows 中文路徑問題**：PowerShell/CMD 中傳遞含中文的 inline Python 指令（`python -c "..."`）會導致路徑亂碼。**請用暫存 `.py` 檔案或 PowerShell 原生參數傳遞。**

### 工具路徑

| 項目 | 路徑 |
|------|------|
| Python 執行檔 | `D:\Prog_install\FinanceTool\Scripts\python.exe` |
| 轉換指令 | `D:\Prog_install\FinanceTool\Scripts\python.exe -m markitdown` |

### 推薦做法 A：暫存 Python 腳本（最穩定，AI 首選）

1. 在 `<appDataDir>\brain\<conversation-id>\scratch\` 建立暫存 `convert.py`。
2. 使用 `open(..., encoding='utf-8')` 讀寫檔案。
3. 用 `subprocess.run(["D:\\Prog_install\\FinanceTool\\Scripts\\python.exe", "-m", "markitdown", src, "-o", dest], capture_output=True, text=True, encoding='utf-8')` 執行轉換。
4. 執行：`D:\Prog_install\FinanceTool\Scripts\python.exe convert.py`

### 推薦做法 B：PowerShell Start-Process

```powershell
$proc = Start-Process -FilePath "D:\Prog_install\FinanceTool\Scripts\python.exe" `
  -ArgumentList "-m markitdown `"$pdfPath`" -o `"$mdPath`"" `
  -Wait -PassThru -NoNewWindow `
  -RedirectStandardError "D:\Prog_install\FinanceTool\mkd_err.txt" `
  -RedirectStandardOutput "D:\Prog_install\FinanceTool\mkd_out.txt"
if ($proc.ExitCode -ne 0) { Write-Error "Convert failed: $(Get-Content D:\Prog_install\FinanceTool\mkd_err.txt)" }
```

### 編碼設定

- **PowerShell**：執行前設定 `[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8` 和 `$OutputEncoding = [System.Text.Encoding]::UTF8`。
- **Python subprocess**：設定 `encoding='utf-8'`，環境變數加入 `PYTHONIOENCODING=utf-8`。

---

## Phase 0 — 環境依賴檢查

> [!IMPORTANT]
> 此 Phase 為最優先執行步驟，任何 AI（Claude / Gemini）務必嚴格遵守。

在執行任何轉換之前，**必須**先確認以下檔案存在：
`D:\Prog_install\FinanceTool\Scripts\markitdown.exe`

| 結果 | 動作 |
|------|------|
| ✅ 檔案存在 | 繼續執行 Phase 1 ~ Phase 3 |
| ❌ 檔案不存在 | **立即中止**所有轉換與清理（跳過 Phase 1/2/2.5），直接跳至 Phase 3 產生報告，並在報告最上方寫明：`錯誤：找不到 markitdown.exe，轉換程序已中止。` |

---

## Phase 1 — PDF / HTML 轉換為 Markdown

### Step 1.1 — 掃描待轉換檔案

遞迴掃描 `FinancialReport` 底下所有公司子資料夾，對每個 `.pdf` 或 `.html` 檔案判斷：

| 條件 | 動作 |
|------|------|
| 同目錄已存在**同名** `.md` 且大小 > 0 bytes | **跳過**（已轉換） |
| 同名 `.md` 不存在，或大小為 0 bytes | **執行轉換** |

### Step 1.2 — 執行轉換

```
D:\Prog_install\FinanceTool\Scripts\python.exe -m markitdown "D:\絕對路徑\report.pdf" -o "D:\絕對路徑\report.md"
```

### Step 1.3 — CID 亂碼品質檢查（PDF 轉換專用）

> [!IMPORTANT]
> **核心規則：此步驟僅針對 PDF 轉出的 `.md` 檔執行。HTML 轉出的 `.md` 不需要此檢查。**

轉換完成後（`.md` 存在且大小 > 0），**立即**對 PDF 來源的 `.md` 執行 CID 亂碼密度檢查。

#### 什麼是 CID 亂碼？

PDF 轉 Markdown 時，部分 PDF 使用嵌入式字型（CIDFont），`markitdown` 無法正確解碼這些字元，產生大量 `(cid:XX)` 標籤或其他不可讀的亂碼字元（如孤立的 ``、``、` ` 等）。這類檔案即使保留也**完全沒有閱讀價值**。

#### 偵測方法

使用以下 Python 邏輯計算 CID 亂碼密度：

```python
import re

def check_cid_density(md_content: str) -> tuple[bool, float, int]:
    """
    檢查 .md 檔案的 CID 亂碼密度。
    
    回傳值：
        - is_failure: bool  — True 表示亂碼過多，應判定為轉換失敗
        - cid_ratio: float  — CID 標籤佔總字元數的比例
        - cid_count: int    — CID 標籤出現次數
    """
    cid_pattern = re.compile(r'\(cid:\d+\)')
    cid_matches = cid_pattern.findall(md_content)
    cid_count = len(cid_matches)
    
    # 計算 CID 標籤佔據的總字元數
    cid_chars = sum(len(m) for m in cid_matches)
    total_chars = len(md_content)
    
    if total_chars == 0:
        return True, 1.0, 0  # 空檔案也視為失敗
    
    cid_ratio = cid_chars / total_chars
    
    # 判定標準：CID 標籤佔比 >= 5% 或 CID 出現次數 >= 50 次
    is_failure = (cid_ratio >= 0.05) or (cid_count >= 50)
    
    return is_failure, cid_ratio, cid_count
```

#### 判定標準

| 條件（符合**任一**即為失敗） | 說明 |
|----------------------------|------|
| CID 標籤字元佔總字元數 ≥ 5% | 表示內容中有大量不可讀的亂碼 |
| CID 標籤 `(cid:\d+)` 出現次數 ≥ 50 次 | 即使比例不高，數量多也代表轉換品質差 |

#### 判定結果處理

| 結果 | 動作 |
|------|------|
| ✅ 通過（亂碼少） | 保留 `.md`，繼續後續流程 |
| ❌ 失敗（亂碼多） | **立即刪除**該 `.md` 檔案，**不嘗試清理**，並記錄到失敗清單中（供 Phase 3 報告使用） |

> [!CAUTION]
> **不要嘗試清理 CID 亂碼**。經驗證，CID 亂碼過多的 PDF 即使清理後，剩餘內容也幾乎無法閱讀。直接刪除是最正確的做法。

### Step 1.4 — 轉換後清理

CID 品質檢查通過後，確認 `.md` 有效（存在且大小 > 0）：

1. **刪除原始來源檔案**（PDF 或 HTML）。
2. **刪除同資料夾內同名或對應相同報告期間的舊版 `.md` 檔案**，只保留最新版本。

**安全防護規則（嚴格執行）：**

| 規則 | 說明 |
|------|------|
| ❌ 刪除指令禁止使用萬用字元（`*`） | 必須指定精確的單一檔案路徑 |
| ❌ 禁止刪除非自動生成的檔案 | 不可刪除人工分析筆記、`.git`、設定檔或手動撰寫的文件 |
| ✅ 只允許刪除 | 已轉換成功的 PDF/HTML 來源檔，以及被取代的舊版同名 `.md` 檔 |

---

## Phase 2 — 清除所有 `.md` 檔案中的 XBRL / iXBRL 標籤

> **此 Phase 每次都必須執行**，無論 Phase 1 是否有執行。

### 掃描範圍

遞迴掃描 `FinancialReport` 底下**所有子目錄**中的 `.md` 檔案。

### 黃金法則

| 規則 | 範例 |
|------|------|
| ✅ 只刪標籤，保留標籤內的內容 | `123,456` → 清理後保留 `123,456` |
| ❌ 禁止整行或整塊刪除含有數值或文字的內容 | 含財報數據的行不可直接整行刪除 |
| ✅ 使用 Python，Regex 加上 `re.DOTALL` flag | 標籤可能跨越多行 |
| ✅ 用迴圈逐檔處理 | 不可用手動或純 Shell 替換 |

### 清理規則（依序套用，共 4 條）

---
**規則 1 — 整塊刪除：iXBRL header 與 metadata 區塊**

這些區塊對閱讀完全無益，**直接整塊刪除**（標籤與其內部所有內容一起刪）。

| 目標 | Regex | 替換為 |
|------|-------|--------|
| `` | `""` |
| `<link:schemaRef>` 自閉合標籤 | `<link:schemaRef[^>]*/\s*>` | `""` |

---

**規則 2 — 剝標籤，保留內容：iXBRL 數值與文字標籤**

這些標籤包裹著真實的財務數值，**只刪標籤，保留括號內的內容**。

| 目標標籤 | Regex | 替換為 |
|---------|-------|--------|
| `` | `<ix:nonFraction[^>]*>(.*?)` | `\1` |
| `` | `<ix:nonNumeric[^>]*>(.*?)` | `\1` |
| 其他所有 `<ix:*>` 標籤 | `<ix:[a-zA-Z0-9_-]+[^>]*>([\s\S]*?)</ix:[a-zA-Z0-9_-]+>` | `\1` |

---

**規則 3 — 刪除：自閉合或空的 ix 標籤**

未包裹任何內容的自閉合標籤，**直接刪除**。

| 目標 | Regex | 替換為 |
|------|-------|--------|
| 自閉合 `` | `<ix:[^>]+/>` | `""` |

---

**規則 4 — 選擇性清理：XML namespace 聲明**

**僅在** namespace 聲明出現於段落中間、影響閱讀時才執行。

| 目標 | Regex | 替換為 |
|------|-------|--------|
| `xmlns:ix` | `]*"` | `""` |
| `xmlns:link` | `]*"` | `""` |
| 其他 xmlns 聲明 | `xmlns:[a-z]+="[^"]*"` | `""` |

---

## Phase 2.5 — 清除所有 `.md` 檔案中的 XBRL 純文字 Blob

> **此 Phase 每次都必須執行**，無論 Phase 1 是否有執行。

### 背景說明

`markitdown` 在轉換 SEC iXBRL 格式財報（如 10-K、10-Q）時，會將 `<ix:header>` 區塊內的 **XBRL R-section（context/footnote 鍵值對映射表）** 的 XML 標籤剝除後，以**超長純文字**直接輸出到 `.md` 頂部。

這類殘留**沒有任何 XML 標籤**，所以 Phase 2 的 Regex 完全無法匹配。

典型外觀（單行，長度 30,000–60,000 字元）：
```
falseP4Y0000352915--12-31FY0.010.01http://fasb.org/us-gaap/2023#Other...
```

### 掃描範圍

遞迴掃描 `FinancialReport` 底下**所有子目錄**中的 `.md` 檔案。

### 偵測條件（三個條件**同時滿足**才視為 XBRL Blob）

| 條件 | 說明 |
|------|------|
| ① 行長 > 500 字元 | 正常段落不會有如此長的單行 |
| ② 含 ≥ 3 個 CIK+Namespace 模式 | Regex：`\d{10}[a-zA-Z][a-zA-Z0-9_\-]*:[a-zA-Z]`（SEC CIK 碼接 XBRL namespace） |
| ③ 空白比例 < 2% | `空格數 / 行長`，正常英文句子遠高於 2% |

### 清理規則

| 動作 | 說明 |
|------|------|
| ✅ 整行刪除符合條件的 XBRL Blob 行 | 完全沒有閱讀價值 |
| ✅ 同時偵測並刪除 unit/measure 尾段 Blob | 純 `namespace:Name` 串接，無空格，20–500 字元，Regex：`^(?:[a-zA-Z][a-zA-Z0-9_\-]*:[a-zA-Z][a-zA-Z0-9_\-]*){3,}$` |
| ✅ 清除後收縮多餘空行 | 連續 4+ 空行壓縮為 3 個 |
| ❌ 禁止刪除含正常財報數字或文字的行 | 財務數據必須完整保留 |

### Python 實作參考

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

## Phase 3 — 產生總結報告

所有 Phase 執行完畢（或因 Phase 0 失敗而提早中止）後，在 `FinancialReport\Log` 資料夾產生 **`conversion_summary.md`**，並在最終回覆中以 Markdown 格式呈現。

> [!NOTE]
> 若 Phase 0 發現缺少 `markitdown.exe`，在報告最上方加入醒目提示：`錯誤：找不到 markitdown.exe，轉換程序已中止。`，其餘統計數據可留空或填 0。

### 報告結構

#### Section 1 — 統計數據概覽

| 指標 | 數量 |
|------|------|
| 總掃描檔案數 | |
| 成功轉換數 | |
| 跳過（已存在）數 | |
| 轉換失敗數（含 CID 亂碼過多） | |
| XBRL 標籤清理檔案數 | |
| XBRL 純文字 Blob 清理檔案數 | |
| CID 亂碼判定失敗並刪除的檔案數 | |

#### Section 2 — 異常詳細清單

**表格 A — 輸出為 0 KB 的檔案**

| 公司名稱 | 原始檔案 | 生成的 .md | 可能原因 |
|---------|---------|-----------|---------|

**表格 B — 轉換失敗的檔案（含程式錯誤）**

| 公司名稱 | 原始檔案 | 錯誤原因 / Stack Trace |
|---------|---------|----------------------|

**表格 C — CID 亂碼過多判定失敗的檔案（PDF 轉換品質不佳）**

> [!IMPORTANT]
> 此表列出因 CID 亂碼密度超過門檻值而被判定為轉換失敗、`.md` 檔已被刪除的檔案。

| 公司名稱 | 原始 PDF 檔案 | 被刪除的 .md 檔案 | CID 出現次數 | CID 佔比 (%) | 判定原因 |
|---------|-------------|-----------------|------------|-------------|---------|

---

## 異常處理規則

| 情況 | 必要動作 |
|------|---------|
| 單一檔案轉換失敗 | 記錄錯誤 → **繼續**處理下一個檔案，不可中止整個批次 |
| 單一檔案標籤清理失敗（如編碼錯誤） | 記錄錯誤 → 繼續處理下一個檔案 |
| PDF 轉出的 `.md` CID 亂碼過多 | 刪除該 `.md` → 記錄到失敗清單 → 繼續處理下一個檔案 |
| 所有錯誤 | 統一記錄至 `conversion_summary.md`，包含檔案路徑與原因 |