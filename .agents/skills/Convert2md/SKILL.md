---
name: Convert2md
description: 掃描 FinancialReport 內所有公司資料夾，使用 pymupdf4llm-mcp（MCP 工具 convert_pdf_to_markdown）將 PDF 財報轉換為 Markdown，偵測轉換品質不佳（CID 亂碼過多）並自動刪除轉換失敗的檔案，最後產生轉換總結報告。本 skill 僅負責 PDF → Markdown 轉換。
---
/goal
# Convert2md Skill — 完整執行說明

## 概覽

本 Skill **僅負責一件事**：把公司資料夾內的 PDF 財報，透過 `pymupdf4llm-mcp` MCP 工具轉換成 Markdown（`.md`）檔案。不處理 HTML、不做 XBRL/iXBRL 標籤清理，這些不在本 skill 範圍內。

每次執行此 Skill 時，依序執行以下流程：

| Phase | 任務說明 | 是否每次都執行？ |
|-------|---------|-----------------|
| **Phase 0** | 環境依賴檢查（確認 `pymupdf4llm-mcp` 的 `convert_pdf_to_markdown` 工具可用） | **是，最優先** |
| **Phase 1** | PDF → Markdown 轉換 + **轉換品質（CID 亂碼）檢查** | 有未轉換的 PDF 時執行 |
| **Phase 2** | 產生總結報告 `conversion_summary.md` | **是，每次都執行** |

> [!IMPORTANT]
> **與舊版的關鍵差異**：
> 1. **PDF 轉換改用 `pymupdf4llm-mcp` MCP 工具**（`convert_pdf_to_markdown`），完全移除 `markitdown.exe` / Python subprocess / PowerShell 呼叫方式。這是一個標準 MCP 工具呼叫，任何支援 MCP 的 AI 執行者（Claude、Gemini 等）呼叫方式完全相同，**不再需要**平台專屬的路徑轉譯或編碼設定。
> 2. **不再處理 HTML 檔案**。本 skill 的職責縮小為單純的 PDF → Markdown 轉換；HTML 財報的轉換與 XBRL/iXBRL 標籤清理不屬於本 skill 範圍，如有需要請另建 skill 處理。
> 3. 不嘗試清理 PDF CID 亂碼字元。若轉出的 `.md` 檔仍含有過多 CID 亂碼，直接判定為**轉換失敗**，刪除該 `.md` 檔，並在 `conversion_summary.md` 中記錄。

---

## 執行環境規範

> [!IMPORTANT]
> **AI 執行關鍵原則（Claude / Gemini 皆適用）：**
> PDF 一律使用 MCP 工具 `convert_pdf_to_markdown`（由 `pymupdf4llm-mcp` server 提供），直接以工具呼叫方式執行，**不透過終端機、subprocess 或 shell 指令**。這個工具在任何作業系統、任何具備 MCP 能力的 AI 執行環境中呼叫方式都一致，因此不會有 Windows 路徑、中文亂碼或編碼設定等平台專屬問題。

### `convert_pdf_to_markdown` 工具參數說明

| 參數 | 必填 | 說明 |
|------|------|------|
| `file_path` | 是 | 來源 PDF 的**絕對路徑** |
| `save_path` | 建議填寫 | 輸出 `.md` 的資料夾絕對路徑（**建議填入與來源 PDF 相同的資料夾**）。填寫後工具會直接把 Markdown 寫入該資料夾，避免整份轉換內容佔用大量對話 context，特別是年報這類大檔案。 |
| `image_path` | 建議填寫 | 圖片輸出資料夾絕對路徑。**務必指定到暫存目錄（非公司資料夾內）**，例如 scratch/temp 路徑；若留空，工具預設會把擷取出的圖片存到與 PDF 相同資料夾，造成公司資料夾被大量不必要的圖片檔污染。財報分析只需要文字與表格內容，不需保留圖片。 |

呼叫範例（概念示意，實際以該工具當下的呼叫介面為準）：
- `file_path` = `<公司資料夾絕對路徑>/report.pdf`
- `save_path` = `<公司資料夾絕對路徑>`（與 PDF 同資料夾）
- `image_path` = `<暫存目錄絕對路徑>`（例如系統 scratch/tmp 目錄，與財報資料夾分開）

呼叫完成後：
1. 確認回傳結果中的 `.md` 檔路徑（若使用 `save_path`，工具會回傳實際寫入的檔案路徑）。
2. 確認實際輸出的檔名是否與來源 PDF 對應（副檔名改為 `.md`，其餘檔名一致）；若工具產生的檔名不同，需**重新命名**成與來源 PDF 對應的名稱，以符合後續掃描規則（Step 1.1）。
3. 轉換過程中產生的暫存圖片檔（`image_path` 指向的目錄）**不需要**保留於財報資料夾中，分析完成後可忽略或清除暫存目錄本身（不要清除公司資料夾）。

---

## Phase 0 — 環境依賴檢查

> [!IMPORTANT]
> 此 Phase 為最優先執行步驟，任何 AI（Claude / Gemini）務必嚴格遵守。

| 檢查項目 | 結果 | 動作 |
|---------|------|------|
| MCP 工具 `convert_pdf_to_markdown`（`pymupdf4llm-mcp`）是否可呼叫 | ✅ 可用 | 繼續執行 Phase 1 |
| MCP 工具 `convert_pdf_to_markdown`（`pymupdf4llm-mcp`）是否可呼叫 | ❌ 不可用 | **立即中止**所有轉換，跳過 Phase 1，直接進入 Phase 2 產生報告，並在報告最上方寫明：`錯誤：找不到 pymupdf4llm-mcp 的 convert_pdf_to_markdown 工具，轉換程序已中止。` |

---

## Phase 1 — PDF 轉換為 Markdown

### Step 1.1 — 掃描待轉換檔案

遞迴掃描 `FinancialReport` 底下所有公司子資料夾，對每個 `.pdf` 檔案判斷：

| 條件 | 動作 |
|------|------|
| 同目錄已存在**同名** `.md` 且大小 > 0 bytes | **跳過**（已轉換） |
| 同名 `.md` 不存在，或大小為 0 bytes | **執行轉換** |

### Step 1.2 — 執行轉換

呼叫 MCP 工具 `convert_pdf_to_markdown`（`pymupdf4llm-mcp`），參數依上方「`convert_pdf_to_markdown` 工具參數說明」設定：
- `file_path` = 該 PDF 的絕對路徑
- `save_path` = 該 PDF 所在的公司資料夾絕對路徑
- `image_path` = 暫存目錄絕對路徑（非公司資料夾）

### Step 1.3 — 轉換品質檢查（CID 亂碼密度）

> [!IMPORTANT]
> **核心規則：此步驟針對所有新轉出的 `.md` 檔執行。** `pymupdf4llm` 對嵌入式字型（CIDFont）的解碼能力通常優於舊版工具，CID 亂碼機率大幅降低，但仍可能因少數特殊字型而發生，故仍需檢查把關。

轉換完成後（`.md` 存在且大小 > 0），**立即**對轉出的 `.md` 執行 CID 亂碼密度檢查。

#### 什麼是 CID 亂碼？

PDF 轉 Markdown 時，部分 PDF 使用嵌入式字型（CIDFont），轉換工具無法正確解碼這些字元，產生大量 `(cid:XX)` 標籤或其他不可讀的亂碼字元。這類檔案即使保留也**完全沒有閱讀價值**。

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
| ❌ 失敗（亂碼多） | **立即刪除**該 `.md` 檔案，**不嘗試清理**，並記錄到失敗清單中（供 Phase 2 報告使用） |

> [!CAUTION]
> **不要嘗試清理 CID 亂碼**。經驗證，CID 亂碼過多的來源檔即使清理後，剩餘內容也幾乎無法閱讀。直接刪除是最正確的做法。

### Step 1.4 — 轉換後清理

品質檢查通過後，確認 `.md` 有效（存在且大小 > 0）：

1. **刪除原始來源 PDF 檔案**。
2. **刪除同資料夾內同名或對應相同報告期間的舊版 `.md` 檔案**，只保留最新版本。
3. **刪除 PDF 轉換過程中產生於暫存目錄的圖片檔案**（`image_path` 指向的內容），這些檔案不屬於財報分析範圍，不應留在系統中累積。

**安全防護規則（嚴格執行）：**

| 規則 | 說明 |
|------|------|
| ❌ 刪除指令禁止使用萬用字元（`*`） | 必須指定精確的單一檔案路徑 |
| ❌ 禁止刪除非自動生成的檔案 | 不可刪除人工分析筆記、`.git`、設定檔或手動撰寫的文件 |
| ✅ 只允許刪除 | 已轉換成功的來源 PDF 檔、被取代的舊版同名 `.md` 檔，以及轉換過程中產生的暫存圖片檔 |

---

## Phase 2 — 產生總結報告

所有 Phase 執行完畢（或因 Phase 0 失敗而提早中止）後，在 `FinancialReport\Log` 資料夾產生 **`conversion_summary.md`**，並在最終回覆中以 Markdown 格式呈現。

> [!NOTE]
> 若 Phase 0 發現 `convert_pdf_to_markdown` 工具不可用，在報告最上方加入醒目提示：`錯誤：找不到 pymupdf4llm-mcp 的 convert_pdf_to_markdown 工具，轉換程序已中止。`，其餘統計數據可留空或填 0。

### 報告結構

#### Section 1 — 統計數據概覽

| 指標 | 數量 |
|------|------|
| 總掃描 PDF 檔案數 | |
| 成功轉換數 | |
| 跳過（已存在）數 | |
| 轉換失敗數（含 CID 亂碼過多） | |
| CID 亂碼判定失敗並刪除的檔案數 | |

#### Section 2 — 異常詳細清單

**表格 A — 輸出為 0 KB 的檔案**

| 公司名稱 | 原始 PDF 檔案 | 生成的 .md | 可能原因 |
|---------|-------------|-----------|---------|

**表格 B — 轉換失敗的檔案（含程式錯誤）**

| 公司名稱 | 原始 PDF 檔案 | 錯誤原因 / Stack Trace |
|---------|-------------|----------------------|

**表格 C — CID 亂碼過多判定失敗的檔案（轉換品質不佳）**

> [!IMPORTANT]
> 此表列出因 CID 亂碼密度超過門檻值而被判定為轉換失敗、`.md` 檔已被刪除的檔案。

| 公司名稱 | 原始 PDF 檔案 | 被刪除的 .md 檔案 | CID 出現次數 | CID 佔比 (%) | 判定原因 |
|---------|-------------|-----------------|------------|-------------|---------|

---

## 異常處理規則

| 情況 | 必要動作 |
|------|---------|
| 單一檔案轉換失敗 | 記錄錯誤 → **繼續**處理下一個檔案，不可中止整個批次 |
| 轉出的 `.md` CID 亂碼過多 | 刪除該 `.md` → 記錄到失敗清單 → 繼續處理下一個檔案 |
| `pymupdf4llm-mcp` 工具不可用 | 中止所有轉換，於報告中註明 |
| 所有錯誤 | 統一記錄至 `conversion_summary.md`，包含檔案路徑與原因 |
