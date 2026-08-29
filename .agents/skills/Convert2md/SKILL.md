---
name: Convert2md
description: 掃描 FinancialReport 內所有公司資料夾，使用 pymupdf4llm-mcp（MCP 工具 convert_pdf_to_markdown）將 PDF 財報轉換為 Markdown，檢查轉換品質（CID 亂碼）並刪除失敗檔案，最後產生轉換總結報告。本 skill 只做 PDF → Markdown，不處理 HTML。
---

# Convert2md — PDF 轉 Markdown

## 這個 Skill 做什麼

**一句話**：把公司資料夾裡的 PDF 財報，用 MCP 工具轉成 `.md` 檔，轉壞的刪掉，最後寫一份報告。

**本 Skill 不做**：HTML 轉換、XBRL 標籤清理、財報內容分析。這些都不在範圍內，不要做。

---

## 絕對規則（開始前先讀完）

| # | 規則 |
|---|------|
| 1 | 轉檔**只能**用 MCP 工具 `convert_pdf_to_markdown`。|
| 2 | 所有路徑一律用**絕對路徑**。不可用相對路徑。 |
| 3 | `image_path` **必須**指向公司資料夾。 |
| 4 | 刪檔一律透過本文件提供的 Python 腳本執行。**禁止**在刪除指令中使用萬用字元 `*`。 |
| 5 | 單一檔案失敗時，**記錄後繼續下一個**，不可中止整批。 |
| 6 | 只能刪三種檔案：①轉換成功的來源 PDF ②CID 檢查失敗的 `.md` ③暫存圖片。**其他一律不可刪**（尤其是人工筆記、`.git`、設定檔）。 |

---

## 名詞定義

| 名詞 | 意思 | 範例 |
|------|------|------|
| `<REPO>` | FinancialReport 儲存庫根目錄的絕對路徑 | `D:\FinancialReport` 或 `/home/user/FinancialReport` |
| `<SCRATCH>` | 暫存工作目錄的絕對路徑 |  |
| 公司資料夾 | `<REPO>` 底下每個以公司名命名的子資料夾 | `<REPO>/UHS` |
| 待轉換 PDF | 同目錄下**沒有**同名 `.md`，或同名 `.md` 大小為 0 的 PDF | — |

---

## 執行流程（照順序做，共 5 步）

```
步驟 1  執行腳本 A  → 產生待轉換清單 convert_tasks.json
步驟 2  檢查工具    → convert_pdf_to_markdown 能不能用？
步驟 3  逐一轉檔    → 對清單中每個 PDF 呼叫一次 MCP 工具
步驟 4  執行腳本 B  → 品質檢查 + 刪檔 + 產生報告
步驟 5  回報結果    → 把報告內容貼給使用者看
```

---

## 步驟 1 — 產生待轉換清單

把下面的腳本存成 `<SCRATCH>/scan_pending.py`，然後執行：

```
python <SCRATCH>/scan_pending.py <REPO> <SCRATCH>
```

```python
# scan_pending.py — 掃描所有待轉換的 PDF
import json, os, sys

REPO = os.path.abspath(sys.argv[1])
SCRATCH = os.path.abspath(sys.argv[2])
SKIP_DIRS = {".git", ".github", ".claude", ".agents", "Log",
             "node_modules", "__pycache__", ".venv"}

pending, skipped, total = [], 0, 0
for dirpath, dirnames, filenames in os.walk(REPO):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        if not fn.lower().endswith(".pdf"):
            continue
        total += 1
        pdf = os.path.abspath(os.path.join(dirpath, fn))
        md = os.path.splitext(pdf)[0] + ".md"
        # 已存在同名且非空的 .md → 視為已轉換，跳過
        if os.path.exists(md) and os.path.getsize(md) > 0:
            skipped += 1
            continue
        pending.append({
            "company": os.path.basename(dirpath),
            "pdf": pdf,
            "md": md,
            "save_path": os.path.abspath(dirpath),
        })

os.makedirs(SCRATCH, exist_ok=True)
out = os.path.join(SCRATCH, "convert_tasks.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump({"repo": REPO, "scratch": SCRATCH, "total_pdf": total,
               "skipped": skipped, "pending": pending},
              f, ensure_ascii=False, indent=2)

print(f"總 PDF 數: {total} / 已轉換跳過: {skipped} / 待轉換: {len(pending)}")
print(f"清單檔: {out}")
for i, t in enumerate(pending, 1):
    print(f"{i}. {t['pdf']}")
```

**如果印出「待轉換: 0」** → 跳過步驟 2、3，直接做步驟 4。

---

## 步驟 2 — 檢查工具可用性

確認 MCP 工具 `convert_pdf_to_markdown`（來自 `pymupdf4llm-mcp` server）存在且可呼叫。

| 情況 | 動作 |
|------|------|
| ✅ 工具存在 | 繼續步驟 3 |
| ❌ 工具不存在 | **停止轉檔**，跳到步驟 4，並在報告最上方寫：`錯誤：找不到 pymupdf4llm-mcp 的 convert_pdf_to_markdown 工具，轉換程序已中止。` |

---

## 步驟 3 — 逐一轉檔

對步驟 1 清單中的**每一個** PDF，呼叫**一次** `convert_pdf_to_markdown`。

### 參數怎麼填

| 參數 | 填什麼 | 從哪來 |
|------|--------|--------|
| `file_path` | PDF 的絕對路徑 | 清單的 `pdf` 欄位 |
| `save_path` | PDF 所在資料夾的絕對路徑 | 清單的 `save_path` 欄位 |
| `image_path` | `<SCRATCH>/pdf_images` | 固定值，**不可**填公司資料夾 |

### 實際範例

假設清單中有這筆：

```json
{
  "company": "UHS",
  "pdf": "/home/user/FinancialReport/UHS/2024_10K.pdf",
  "md": "/home/user/FinancialReport/UHS/2024_10K.md",
  "save_path": "/home/user/FinancialReport/UHS"
}
```

就這樣呼叫工具：

```
convert_pdf_to_markdown(
    file_path  = "/home/user/FinancialReport/UHS/2024_10K.pdf",
    save_path  = "/home/user/FinancialReport/UHS",
    image_path = "<SCRATCH>/pdf_images"
)
```

### 為什麼一定要填 `save_path`

不填 `save_path` 的話，工具會把**整份 Markdown 內容當成回傳值吐出來**。年報動輒數十萬字，會塞爆對話 context。填了 `save_path`，工具直接寫檔並只回傳路徑。**一定要填。**

### 呼叫完要做的事

1. 看回傳的檔案路徑。
2. **比對檔名**：輸出的 `.md` 檔名必須跟清單的 `md` 欄位一致（就是 PDF 檔名把 `.pdf` 換成 `.md`）。
   - 一致 → 不用動。
   - 不一致 → **改名**成清單 `md` 欄位的名字。否則步驟 4 會找不到檔案，誤判成轉換失敗。
3. 若工具回傳錯誤 → 記下錯誤訊息，**繼續處理下一個 PDF**，不要停。

---

## 步驟 4 — 品質檢查、刪檔、產生報告

把下面的腳本存成 `<SCRATCH>/verify_and_report.py`，然後執行：

```
python <SCRATCH>/verify_and_report.py <SCRATCH>/convert_tasks.json
```

這支腳本會自動完成：CID 亂碼檢查 → 刪除失敗的 `.md` → 刪除成功的來源 PDF → 清除暫存圖片 → 寫出 `<REPO>/Log/conversion_summary.md`。

```python
# verify_and_report.py — 品質檢查 + 清理 + 報告
import json, os, re, shutil, sys
from datetime import datetime

CID_RE = re.compile(r'\(cid:\d+\)')

def cid_check(path):
    """回傳 (是否失敗, CID佔比, CID次數)"""
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    hits = CID_RE.findall(text)
    count, total = len(hits), len(text)
    if total == 0:
        return True, 1.0, 0          # 空檔 = 失敗
    ratio = sum(len(h) for h in hits) / total
    # 判定門檻：佔比 >= 5% 或 出現 >= 50 次
    return (ratio >= 0.05 or count >= 50), ratio, count

with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)

REPO, SCRATCH = data["repo"], data["scratch"]
ok, empty, cid_fail = [], [], []

for t in data["pending"]:
    md = t["md"]
    # A. .md 不存在或 0 KB → 轉換失敗
    if not os.path.exists(md) or os.path.getsize(md) == 0:
        if os.path.exists(md):
            os.remove(md)
        empty.append(t)
        continue
    # B. CID 亂碼檢查
    failed, ratio, count = cid_check(md)
    if failed:
        os.remove(md)                        # 刪掉沒有閱讀價值的 .md
        t.update(cid_ratio=round(ratio * 100, 2), cid_count=count)
        cid_fail.append(t)
        continue
    # C. 通過 → 刪掉來源 PDF
    if os.path.exists(t["pdf"]):
        os.remove(t["pdf"])
    ok.append(t)

# 清除暫存圖片（只清 SCRATCH 底下，絕不碰公司資料夾）
img_dir = os.path.join(SCRATCH, "pdf_images")
if os.path.isdir(img_dir):
    shutil.rmtree(img_dir, ignore_errors=True)

# 產生報告
log_dir = os.path.join(REPO, "Log")
os.makedirs(log_dir, exist_ok=True)
report = os.path.join(log_dir, "conversion_summary.md")

L = []
L.append("# PDF 轉換總結報告\n")
L.append(f"產生時間：{datetime.now():%Y-%m-%d %H:%M:%S}\n")
L.append("轉換工具：`pymupdf4llm-mcp` / `convert_pdf_to_markdown`\n")

L.append("\n## Section 1 — 統計數據概覽\n")
L.append("| 指標 | 數量 |")
L.append("|------|------|")
L.append(f"| 總掃描 PDF 檔案數 | {data['total_pdf']} |")
L.append(f"| 跳過（已轉換） | {data['skipped']} |")
L.append(f"| 本次嘗試轉換 | {len(data['pending'])} |")
L.append(f"| 成功轉換 | {len(ok)} |")
L.append(f"| 失敗：輸出 0 KB 或未產生 | {len(empty)} |")
L.append(f"| 失敗：CID 亂碼過多（已刪除） | {len(cid_fail)} |")

L.append("\n## Section 2 — 異常詳細清單\n")

L.append("\n### 表格 A — 未產生或 0 KB 的檔案\n")
L.append("| 公司名稱 | 原始 PDF | 預期的 .md | 可能原因 |")
L.append("|---------|---------|-----------|---------|")
for t in empty:
    L.append(f"| {t['company']} | {os.path.basename(t['pdf'])} | "
             f"{os.path.basename(t['md'])} | 工具未輸出內容（PDF 可能加密、損毀或為純掃描影像） |")
if not empty:
    L.append("| — | — | — | 無 |")

L.append("\n### 表格 B — CID 亂碼過多（.md 已刪除）\n")
L.append("| 公司名稱 | 原始 PDF | 被刪除的 .md | CID 次數 | CID 佔比 (%) |")
L.append("|---------|---------|-------------|---------|-------------|")
for t in cid_fail:
    L.append(f"| {t['company']} | {os.path.basename(t['pdf'])} | "
             f"{os.path.basename(t['md'])} | {t['cid_count']} | {t['cid_ratio']} |")
if not cid_fail:
    L.append("| — | — | — | — | 無 |")

L.append("\n### 表格 C — 成功轉換的檔案\n")
L.append("| 公司名稱 | 產出的 .md |")
L.append("|---------|-----------|")
for t in ok:
    L.append(f"| {t['company']} | {os.path.basename(t['md'])} |")
if not ok:
    L.append("| — | 無 |")

text = "\n".join(L) + "\n"
with open(report, "w", encoding="utf-8") as f:
    f.write(text)

print(text)
print(f"\n報告已寫入：{report}")
```

### 腳本 B 的刪檔行為（對照表）

| 轉換結果 | `.md` | 來源 PDF | 理由 |
|---------|-------|---------|------|
| ✅ 成功（CID 檢查通過） | **保留** | **刪除** | 內容已轉成 md，PDF 不再需要 |
| ❌ CID 亂碼過多 | **刪除** | **保留** | md 沒有閱讀價值；PDF 留著，日後換工具可重試 |
| ❌ 未產生 / 0 KB | **刪除**（若存在） | **保留** | 同上，PDF 留著才有機會補救 |
| ⏭️ 本來就已轉換過 | 不動 | 不動 | 不在本次待轉換清單內 |

> **重點**：轉換失敗時**絕不刪來源 PDF**。刪了就永久失去資料。

> [!CAUTION]
> **不要嘗試修補 CID 亂碼。** 經驗證，CID 亂碼過多的檔案就算清理過，剩下的內容也讀不懂。直接刪除是唯一正確做法。

### 什麼是 CID 亂碼

有些 PDF 用嵌入式字型（CIDFont），轉換工具解不開，就會輸出一堆 `(cid:123)` 這種東西：

```
(cid:20)(cid:45)(cid:88) 2024 (cid:12)(cid:33)(cid:71)(cid:19)
```

這種檔案完全沒有閱讀價值。判定門檻：**CID 字元佔全文 ≥ 5%**，或 **出現 ≥ 50 次**，符合任一條就算失敗。

---

## 步驟 5 — 回報結果

腳本 B 執行完會把報告全文印出來。把那份報告**原封不動**貼給使用者，並補一句話說明：本次掃描幾個 PDF、成功幾個、失敗幾個。

若步驟 2 判定工具不可用，就在報告最前面加上那行錯誤訊息。

---

## 錯誤處理速查表

| 遇到什麼 | 怎麼做 |
|---------|--------|
| 某個 PDF 呼叫工具回傳錯誤 | 記下錯誤訊息 → **繼續下一個** → 腳本 B 會把它歸到表格 A |
| 工具輸出的 `.md` 檔名跟預期不同 | 改名成清單 `md` 欄位的名字 |
| 工具輸出的 `.md` 是 0 KB | 不用手動處理，腳本 B 會刪掉並記錄 |
| `convert_pdf_to_markdown` 工具不存在 | 跳過步驟 3，直接執行步驟 4，報告加註錯誤訊息 |
| 待轉換清單是空的 | 跳過步驟 2、3，直接執行步驟 4（報告會顯示全部跳過） |
| 公司資料夾出現一堆 `.png` / `.jpg` | 代表 `image_path` 填錯了。刪掉那些圖片，重填 `image_path` 為 `<SCRATCH>/pdf_images` |
