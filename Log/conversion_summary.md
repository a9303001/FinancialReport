# Convert2md 轉換總結報告

- **執行時間**：2026-08-07
- **執行環境**：Linux（Claude Code remote execution）
- **目標資料夾**：`UHS`
- **工具**：`markitdown`（Python 模組，Linux 環境臨時安裝；本環境無 Windows `markitdown.exe`，已改用 `python3 -m markitdown` 等效執行）

## Section 1 — 統計數據概覽

| 指標 | 數量 |
|------|------|
| 總掃描檔案數（本次新增 PDF/HTML） | 1 |
| 成功轉換數 | 1 |
| 跳過（已存在）數 | 0 |
| 轉換失敗數（含 CID 亂碼過多） | 0 |
| XBRL 標籤清理檔案數 | 1（`markitdown` 轉檔時已剝除大部分 iXBRL 標籤，Phase 2 regex 未再匹配到殘留標籤） |
| XBRL 純文字 Blob 清理檔案數 | 1（移除 1 行超長 XBRL context blob） |
| CID 亂碼判定失敗並刪除的檔案數 | 0 |

## Section 2 — 異常詳細清單

**表格 A — 輸出為 0 KB 的檔案**：無

**表格 B — 轉換失敗的檔案**：無

**表格 C — CID 亂碼過多判定失敗的檔案**：無

## 轉換明細

| 公司 | 原始檔案 | 生成 .md | 大小 | CID 次數 | 狀態 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| UHS | `UHS_10Q_2026-06-30.htm`（SEC EDGAR 原始檔，5.65MB）| `UHS_10Q_2026-06-30.md` | 約 365KB | 0 | ✅ 轉換成功，內容乾淨（含 "Universal Health Services" ×7、"June 30, 2026" 期間標示），來源 .htm 已刪除 |

> 備註：本 10-Q 為 HTML(iXBRL) 來源，非 PDF，故不適用 CID 亂碼檢查；但仍執行 Phase 2 / Phase 2.5 XBRL 清理，移除 1 行超長純文字 XBRL blob。
