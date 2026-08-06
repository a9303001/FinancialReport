# Convert2md 轉換總結報告

- **執行時間**：2026-08-06
- **執行範圍**：`7203Toyota/`（本次 CollectsentimentAndReports 路由對象）
- **環境註記**：本環境為 Linux，無 Windows 版 `markitdown.exe`；改用 `markitdown` Python 模組執行轉換（CLI 封裝因 `_cffi_backend` 問題不可用，模組本身正常）。

## Section 1 — 統計數據概覽

| 指標 | 數量 |
|------|------|
| 總掃描檔案數（本次目標） | 1（`7203_Quarter_2027Q1.pdf`） |
| 成功轉換數 | 1 |
| 跳過（已存在）數 | 0 |
| 轉換失敗數（含 CID 亂碼過多） | 0 |
| XBRL 標籤清理檔案數 | 0（無 iXBRL 殘留） |
| XBRL 純文字 Blob 清理檔案數 | 0 |
| CID 亂碼判定失敗並刪除的檔案數 | 0 |

## Section 2 — 轉換明細

| 原始檔案 | 生成的 .md | 大小 | CID 次數 | CID 佔比 | 結果 |
|---------|-----------|------|---------|---------|------|
| `7203_Quarter_2027Q1.pdf` | `7203_Quarter_2027Q1.md` | 71,277 bytes | 0 | 0.00% | ✅ 成功，來源 PDF 已刪除 |

## Section 2 — 異常詳細清單

- 表格 A（0 KB 檔案）：無
- 表格 B（轉換失敗）：無
- 表格 C（CID 亂碼過多刪除）：無

## 備註
- 來源為 Toyota 官方英文版決算短信（標準字型），轉換乾淨無 `(cid:N)` 亂碼。
- Phase 2 / 2.5 XBRL 清理已對 `7203Toyota/` 內所有 `.md` 執行，未發現 iXBRL 標籤或 XBRL 純文字 Blob 殘留。
