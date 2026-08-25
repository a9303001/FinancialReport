# Convert2md 轉換總結報告 — 2026/08/25

## Section 1 — 統計數據概覽

| 指標 | 數量 |
|------|------|
| 總掃描檔案數（本次目標） | 2（1 PDF + 1 HTML） |
| 成功轉換數 | 1（`PBR.A_Quarter_2026Q2.html` → `.md`） |
| 跳過（已存在）數 | 0 |
| 轉換失敗數（含 CID 亂碼過多） | 1（見表格 C） |
| XBRL 標籤清理檔案數 | 1（Q2 HTML 轉出檔，套用 Phase 2） |
| XBRL 純文字 Blob 清理檔案數 | 0（Q2 HTML 轉出檔無 Blob 殘留） |
| CID 亂碼判定失敗並刪除的檔案數 | 1 |

> 註：環境為 Linux，非 Skill 文件假設的 Windows。`markitdown` 原未安裝，已於本次 `pip install markitdown[pdf]` 並修復 `cryptography` 相依後成功匯入。

## Section 2 — 異常詳細清單

**表格 A — 輸出為 0 KB 的檔案**

| 公司名稱 | 原始檔案 | 生成的 .md | 可能原因 |
|---------|---------|-----------|---------|
| （無） | — | — | — |

**表格 B — 轉換失敗的檔案（含程式錯誤）**

| 公司名稱 | 原始檔案 | 錯誤原因 / Stack Trace |
|---------|---------|----------------------|
| （無） | — | — |

**表格 C — CID 亂碼過多判定失敗的檔案（PDF 轉換品質不佳）**

| 公司名稱 | 原始 PDF 檔案 | 被刪除的 .md 檔案 | CID 出現次數 | CID 佔比 (%) | 判定原因 |
|---------|-------------|-----------------|------------|-------------|---------|
| `PBR巴西石油` | `PBR.A_Quarter_2026Q2.pdf`（IR 版，內容實為 Q1） | `PBR.A_Quarter_2026Q2.md`（markitdown 版） | 3,139 | 10.64% | CID 佔比 ≥ 5% 門檻，且該 PDF 內容經核實為 **2026 Q1**（截至 2026-03-31）之重複檔，非真正 Q2 → 一併刪除來源 PDF |

## Section 3 — 補充說明

1. **子代理人下載之「Q2」PDF 實為 Q1 內容**：Petrobras IR「Financial Statements in US$」連結取得的 PDF，經 `pypdfium2` 抽取核實，全文出現「As of March 31, 2026」60 次、「June 30, 2026」0 次，與既有 `PBR.A_Quarter_2026Q1.md` 重複；且 markitdown 轉出 CID 亂碼達 10.64%。依 Convert2md §1.3 判定失敗，PDF 與 .md 皆刪除。
2. **改抓 SEC EDGAR 之真正 Q2 2026 6-K（HTML）**：來源
   `https://www.sec.gov/Archives/edgar/data/0001119639/000129281426004133/pbrfs2q26usd_6k.htm`
   （USD 版，截至 2026-06-30，董事會 2026-08-06 核准發布）。HTML 檔 1.95MB，「June 30, 2026」出現 70 次。
3. **HTML → Markdown 轉換成功**：`PBR.A_Quarter_2026Q2.md`（≈188KB，`(cid:` 0 次），已套用 Phase 2 iXBRL 標籤清理與 Phase 2.5 Blob 檢查（無殘留），來源 HTML 依 §1.4 已刪除。
