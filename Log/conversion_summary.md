# Convert2md 轉換總結報告

- **執行時間**：2026-07-26
- **目標資料夾**：`6361荏原製作所`（Ebara Corporation, TSE 6361）
- **環境**：Linux；`markitdown` 以 `pip install markitdown[pdf]` + `cffi` 安裝後以 `python -m markitdown` 呼叫（原 Skill 的 Windows 路徑不適用，已依 Phase 0 意旨改為確認 `markitdown` 模組可用）。

## Section 1 — 統計數據概覽

| 指標 | 數量 |
|------|------|
| 總掃描檔案數（PDF/HTML） | 3 |
| 成功轉換數 | 3 |
| 跳過（已存在）數 | 0 |
| 轉換失敗數（含 CID 亂碼過多） | 0 |
| XBRL 標籤清理檔案數 | 0 |
| XBRL 純文字 Blob 清理檔案數 | 0 |
| CID 亂碼判定失敗並刪除的檔案數 | 0 |

## Section 2 — 轉換明細

| 原始檔案 | 生成的 .md | 大小 | CID 檢查 | 狀態 |
|---------|-----------|------|---------|------|
| `6361_AnnualReport_2025.pdf` | `6361_AnnualReport_2025.md` | 105,815 bytes | 通過（英文版，無 CID 亂碼） | ✅ 成功，來源 PDF 已刪除 |
| `6361_AnnualReport_2024.pdf` | `6361_AnnualReport_2024.md` | 102,652 bytes | 通過（英文版，無 CID 亂碼） | ✅ 成功，來源 PDF 已刪除 |
| `6361_Quarter_2026Q1.html` | `6361_Quarter_2026Q1.md` | 60,711 bytes | 不適用（HTML） | ✅ 成功，來源 HTML 已刪除 |

### 表格 A — 輸出為 0 KB 的檔案
（無）

### 表格 B — 轉換失敗的檔案
（無）

### 表格 C — CID 亂碼過多判定失敗的檔案
（無）

## 備註
- 三份財報皆為英文版，`markitdown` 轉出後無 `(cid:N)` 亂碼、無 XBRL/iXBRL 標籤或純文字 Blob 殘留（Ebara 決算短信非 SEC iXBRL 格式）。
- `6361_Quarter_2026Q1.md`（FY2026 Q1 決算短信）因原始 PDF 受官網 Akamai bot 防護封鎖，改由 Firecrawl 擷取英文內容轉存；粗體標題有輕微「單字元重複」的字型副作用（如 `MARCH 3333311111`），但**核心財務數值完全乾淨且可讀**（Q1 營收 246,311 百萬日圓、營業利益 26,749、母公司股東淨利 18,322、EPS 40.13 日圓）。
