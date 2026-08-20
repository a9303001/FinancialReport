# 財報檔案轉換 Markdown 總結報告 (Conversion Summary Report)

- **執行日期**：2026-08-21
- **執行工具**：Python `markitdown` 模組 (`D:\Prog_install\FinanceTool\Scripts\python.exe -m markitdown`)
- **執行範疇**：`d:\FinancialReport` 公司資料夾（特別針對 `8002丸紅` 與 `01816中廣核電力`）

---

## Section 1 — 統計數據概覽

| 指標 | 數量 |
| :--- | :--- |
| **總掃描檔案數** | 3 |
| **成功轉換數** | 3 |
| **跳過（已存在有效 .md）數** | 0 |
| **轉換失敗數（含程式錯誤）** | 0 |
| **CID 亂碼判定失敗並刪除數** | 0 |
| **XBRL 標籤清理檔案數** | 3 |
| **XBRL 純文字 Blob 清理檔案數** | 3 |

---

## Section 2 — 轉換清單明細

| 公司名稱 | 原始來源檔案 | 產出 .md 檔案 | 狀態 | 處理說明 |
| :--- | :--- | :--- | :--- | :--- |
| **8002丸紅** | `8002_AnnualReport_2025.pdf` | `8002_AnnualReport_2025.md` | ✅ 成功 | CID 檢查通過，XBRL 標籤與 Blob 清理完成，已刪除來源 PDF |
| **8002丸紅** | `8002_AnnualReport_2026.pdf` | `8002_AnnualReport_2026.md` | ✅ 成功 | CID 檢查通過，XBRL 標籤與 Blob 清理完成，已刪除來源 PDF |
| **8002丸紅** | `8002_Quarter_2027Q1.pdf` | `8002_Quarter_2027Q1.md` | ✅ 成功 | CID 檢查通過，XBRL 標籤與 Blob 清理完成，已刪除來源 PDF |

---

## Section 3 — 異常詳細清單

- **輸出為 0 KB 的檔案**：無
- **轉換失敗的檔案（含程式錯誤）**：無
- **CID 亂碼過多判定失敗的檔案**：無
