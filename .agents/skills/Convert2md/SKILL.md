---
name: Convert2md
description: 掃描 FinancialReport 內公司資料夾，用 MCP 工具 convert_pdf_to_markdown 將 PDF 轉 Markdown，檢查 CID 亂碼並刪除失敗檔案，產生報告。只做 PDF → Markdown，不處理 HTML。
---

# Convert2md — PDF 轉 Markdown

把公司資料夾裡的 PDF 用 MCP 工具轉成 `.md`，轉壞的刪掉，最後寫報告。

## 規則

1. 轉檔**只能**用 MCP 工具 `convert_pdf_to_markdown`
2. 所有路徑一律用**絕對路徑**
3. `image_path` 填 `<SCRATCH>/pdf_images`，**不可**填公司資料夾
4. 刪檔透過本文件的 Python 腳本執行，**禁止**用萬用字元 `*`
5. 單一檔案失敗 → 記錄後**繼續下一個**，不可中止
6. 只能刪：①成功轉換的來源 PDF ②CID 失敗的 `.md` ③暫存圖片。**其他不可刪**

## 名詞

- `<REPO>`：`D:\FinancialReport`（儲存庫根目錄絕對路徑）
- `<SCRATCH>`：暫存工作目錄絕對路徑
- 公司資料夾：`<REPO>` 底下以公司名命名的子資料夾（如 `<REPO>/UHS`）
- 待轉換 PDF：同目錄下沒有同名非空 `.md` 的 PDF

## 流程（共 5 步）

```
步驟 1  執行腳本 A → 產生待轉換清單 convert_tasks.json
步驟 2  檢查工具   → convert_pdf_to_markdown 能不能用？
步驟 3  逐一轉檔   → 對清單中每個 PDF 呼叫一次 MCP 工具
步驟 4  執行腳本 B → 品質檢查 + 刪檔 + 產生報告
步驟 5  回報結果   → 把報告貼給使用者
```

---

## 步驟 1 — 產生待轉換清單

存成 `<SCRATCH>/scan_pending.py` 並執行 `python <SCRATCH>/scan_pending.py <REPO> <SCRATCH>`：

```python
# scan_pending.py
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

**待轉換為 0** → 跳過步驟 2、3，直接做步驟 4。

---

## 步驟 2 — 檢查工具

確認 MCP 工具 `convert_pdf_to_markdown`（來自 `pymupdf4llm-mcp`）可用。不可用 → 跳到步驟 4，報告加註錯誤訊息。

---

## 步驟 3 — 逐一轉檔

對清單中每個 PDF 呼叫 `convert_pdf_to_markdown`，參數：

| 參數 | 值 |
|------|-----|
| `file_path` | 清單的 `pdf` 欄位（PDF 絕對路徑） |
| `save_path` | 清單的 `save_path` 欄位（PDF 所在資料夾絕對路徑） |
| `image_path` | `<SCRATCH>/pdf_images`（固定值） |

**`save_path` 必填**，否則工具會把整份 Markdown 吐回 context，塞爆對話。

呼叫後：
1. 確認輸出的 `.md` 檔名 = PDF 檔名換成 `.md`。不一致就改名。
2. 工具回傳錯誤 → 記下錯誤，**繼續下一個**。

--- 

## 步驟 4 — 品質檢查 + 刪檔 + 報告

存成 `<SCRATCH>/verify_and_report.py` 並執行 `python <SCRATCH>/verify_and_report.py <SCRATCH>/convert_tasks.json`：

```python
# verify_and_report.py
import json, os, re, shutil, sys
from datetime import datetime

CID_RE = re.compile(r'\(cid:\d+\)')

def cid_check(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    hits = CID_RE.findall(text)
    count, total = len(hits), len(text)
    if total == 0:
        return True, 1.0, 0
    ratio = sum(len(h) for h in hits) / total
    return (ratio >= 0.05 or count >= 50), ratio, count

with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)

REPO, SCRATCH = data["repo"], data["scratch"]
ok, empty, cid_fail = [], [], []

for t in data["pending"]:
    md = t["md"]
    if not os.path.exists(md) or os.path.getsize(md) == 0:
        if os.path.exists(md):
            os.remove(md)
        empty.append(t)
        continue
    failed, ratio, count = cid_check(md)
    if failed:
        os.remove(md)
        t.update(cid_ratio=round(ratio * 100, 2), cid_count=count)
        cid_fail.append(t)
        continue
    if os.path.exists(t["pdf"]):
        os.remove(t["pdf"])
    ok.append(t)

img_dir = os.path.join(SCRATCH, "pdf_images")
if os.path.isdir(img_dir):
    shutil.rmtree(img_dir, ignore_errors=True)

log_dir = os.path.join(REPO, "Log")
os.makedirs(log_dir, exist_ok=True)
report = os.path.join(log_dir, "conversion_summary.md")

L = []
L.append("# PDF 轉換總結報告\n")
L.append(f"產生時間：{datetime.now():%Y-%m-%d %H:%M:%S}\n")
L.append("轉換工具：`pymupdf4llm-mcp` / `convert_pdf_to_markdown`\n")
L.append("\n## 統計\n")
L.append("| 指標 | 數量 |")
L.append("|------|------|")
L.append(f"| 總掃描 PDF | {data['total_pdf']} |")
L.append(f"| 跳過（已轉換） | {data['skipped']} |")
L.append(f"| 本次嘗試轉換 | {len(data['pending'])} |")
L.append(f"| 成功 | {len(ok)} |")
L.append(f"| 失敗：0 KB 或未產生 | {len(empty)} |")
L.append(f"| 失敗：CID 亂碼（已刪除） | {len(cid_fail)} |")
L.append("\n## 異常清單\n")
L.append("\n### 未產生或 0 KB\n")
L.append("| 公司 | PDF | 預期 .md | 原因 |")
L.append("|------|-----|---------|------|")
for t in empty:
    L.append(f"| {t['company']} | {os.path.basename(t['pdf'])} | "
             f"{os.path.basename(t['md'])} | PDF 可能加密、損毀或純掃描 |")
if not empty:
    L.append("| — | — | — | 無 |")
L.append("\n### CID 亂碼過多（.md 已刪除）\n")
L.append("| 公司 | PDF | 被刪的 .md | CID 次數 | CID 佔比% |")
L.append("|------|-----|-----------|---------|----------|")
for t in cid_fail:
    L.append(f"| {t['company']} | {os.path.basename(t['pdf'])} | "
             f"{os.path.basename(t['md'])} | {t['cid_count']} | {t['cid_ratio']} |")
if not cid_fail:
    L.append("| — | — | — | — | 無 |")
L.append("\n### 成功轉換\n")
L.append("| 公司 | .md |")
L.append("|------|-----|")
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

### 刪檔規則

| 結果 | `.md` | PDF |
|------|-------|-----|
| ✅ 成功 | 保留 | 刪除 |
| ❌ CID 亂碼 | 刪除 | **保留** |
| ❌ 未產生/0KB | 刪除 | **保留** |

> **轉換失敗時絕不刪 PDF。**

### CID 亂碼

PDF 嵌入式字型（CIDFont）解不開，產出 `(cid:123)` 亂碼。判定失敗門檻：佔比 ≥ 5% 或出現 ≥ 50 次。不要嘗試修補。

---

## 步驟 5 — 回報

把腳本 B 印出的報告貼給使用者，說明：掃描幾個 PDF、成功幾個、失敗幾個。

---

## 錯誤處理

| 狀況 | 處理 |
|------|------|
| 某 PDF 工具回傳錯誤 | 記錄 → 繼續下一個 |
| 輸出 `.md` 檔名不同 | 改名成清單 `md` 欄位的名字 |
| 輸出 `.md` 是 0 KB | 腳本 B 會處理 |
| 工具不存在 | 跳過步驟 3，直接步驟 4，報告加錯誤訊息 |
| 待轉換清單空 | 跳過步驟 2、3，直接步驟 4 |
| 公司資料夾出現 `.png/.jpg` | `image_path` 填錯了，刪圖片，改填 `<SCRATCH>/pdf_images` |
