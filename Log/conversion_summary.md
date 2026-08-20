# Convert2md 轉換總結報告

- **執行日期**：2026-08-20
- **目標資料夾**：`3252地主`（JINUSHI Co., Ltd. / 地主株式会社）
- **執行環境備註**：本機為 Linux，`markitdown` 因相依套件 `cryptography` 的 rust binding 損毀（`pyo3_runtime.PanicException`）無法使用，改以 **PyMuPDF (pymupdf)** 進行 PDF→Markdown 轉換（等效替代，文字擷取乾淨、CID 亂碼為 0）。

---

## Section 1 — 統計數據概覽

| 指標 | 數量 |
|------|------|
| 總掃描檔案數（PDF/HTML） | 3 |
| 成功轉換數 | 3 |
| 跳過（已存在）數 | 0 |
| 轉換失敗數（含 CID 亂碼過多） | 0 |
| XBRL 標籤清理檔案數 | 0（日股決算短信，無 iXBRL 標籤） |
| XBRL 純文字 Blob 清理檔案數 | 0 |
| CID 亂碼判定失敗並刪除的檔案數 | 0 |

---

## Section 2 — 轉換明細

| 原始 PDF | 生成的 .md | 字元數 | CID 次數 | 狀態 |
|---------|-----------|-------|---------|------|
| `3252_AnnualReport_2024.pdf` | `3252_AnnualReport_2024.md` | 21,453 | 0 | ✅ 成功（來源 PDF 已刪除） |
| `3252_AnnualReport_2025.pdf` | `3252_AnnualReport_2025.md` | 22,498 | 0 | ✅ 成功（來源 PDF 已刪除） |
| `3252_Quarter_2026Q2.pdf` | `3252_Quarter_2026Q2.md` | 10,591 | 0 | ✅ 成功（來源 PDF 已刪除） |

**表格 A — 輸出為 0 KB 的檔案**：無

**表格 B — 轉換失敗的檔案**：無

**表格 C — CID 亂碼過多判定失敗的檔案**：無（三檔 CID 次數皆為 0，屬標準內嵌字型，轉換乾淨）

---

## 備註
- 三份財報均為日文標準字型（決算短信〔日本基準〕），轉換後為可讀日文，無 `(cid:N)` 亂碼。
- 轉換成功後依 Skill Step 1.4 刪除原始 PDF 來源檔，僅保留最新 `.md`。
- Phase 2 / 2.5（XBRL/iXBRL 清理）為每次必跑；本批為日股決算短信、非 SEC iXBRL，無標籤或 Blob 需清理。
