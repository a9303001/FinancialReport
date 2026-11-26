---
name: Convert2md
description: 掃描 FinancialReport 內公司資料夾，用 MCP 工具 convert_pdf_to_markdown 將 PDF 轉 Markdown；加 `--html` 時另用 scripts/html2md.py 把 SEC EDGAR 的 HTML／iXBRL（edgar skill 下載的 .htm）轉 Markdown。檢查 CID 亂碼並刪除失敗檔案，產生報告。
---

# Convert2md — PDF／HTML 轉 Markdown

把公司資料夾裡的 PDF 用 MCP 工具轉成 `.md`（加 `--html` 時，HTML 用 `scripts/html2md.py` 轉），轉壞的刪掉，最後寫報告。

## 規則

1. PDF 轉檔**只能**用 MCP 工具 `convert_pdf_to_markdown`；HTML（`.htm`/`.html`）**只能**用本 skill 的 `scripts/html2md.py`（只用 Python 標準函式庫，SEC iXBRL 實測 2026-11）
2. 所有路徑一律用**絕對路徑**
3. `image_path` 填 `<SCRATCH>/pdf_images`，**不可**填公司資料夾
4. 刪檔透過本文件的 Python 腳本執行，**禁止**用萬用字元 `*`
5. 單一檔案失敗 → 記錄後**繼續下一個**，不可中止
6. 只能刪：①成功轉換的來源 PDF／HTML ②CID 失敗的 `.md` ③暫存圖片。**其他不可刪**
7. HTML 只在加 `--html` 時才處理（目前只有 `edgar` skill 會加）；不加就和以前一樣只轉 PDF

## 名詞

- `<REPO>`：儲存庫根目錄絕對路徑（Windows 本機如 `D:\FinancialReport`；Claude Code 雲端如 `/home/user/FinancialReport`）
- `<SCRATCH>`：暫存工作目錄絕對路徑
- 公司資料夾：`<REPO>` 底下以公司名命名的子資料夾（如 `<REPO>/UHS`）
- `<SCOPE>`（選填）：只掃描這個資料夾（`<REPO>` 內的絕對路徑）。不填 = 掃整個 `<REPO>`（預設行為）
- 待轉換檔：同目錄下沒有同名非空 `.md` 的 PDF（加 `--html` 時含 `.htm`/`.html`）
- `<SKILL>`：本 skill 資料夾（Claude `<REPO>/.claude/skills/Convert2md`；Gemini `<REPO>/.agents/skills/Convert2md`，內容相同）

## 流程（共 5 步）

```
步驟 1  執行腳本 A → 產生待轉換清單 convert_tasks.json
步驟 2  檢查工具   → convert_pdf_to_markdown 能不能用？
步驟 3  逐一轉檔   → PDF：每個呼叫一次 MCP 工具；HTML：跑一次 html2md.py --tasks
步驟 4  執行腳本 B → 品質檢查 + 刪檔 + 產生報告
步驟 5  回報結果   → 把報告貼給使用者
```

---

## 步驟 1 — 產生待轉換清單

存成 `<SCRATCH>/scan_pending.py` 並執行 `python <SCRATCH>/scan_pending.py <REPO> <SCRATCH> [<SCOPE>] [--html]`：

- 只想轉某個資料夾時**一定要加 `<SCOPE>`**（例：`collectState` 加 `<REPO>/jp_state`），否則會把 `History/`、`Prompt/` 等不相干資料夾的 PDF 也轉掉並刪除。
- 加不加 `<SCOPE>`，報告都寫到 `<REPO>/Log/conversion_summary.md`。
- `--html`：一併列出 `.htm`/`.html`（`edgar` skill 印出 `CONVERT2MD_HTML=1` 時要加）。

```python
# scan_pending.py
import json, os, sys

ARGS = [a for a in sys.argv[1:] if a != "--html"]
HTML = "--html" in sys.argv[1:]           # 一併轉 SEC EDGAR 的 .htm/.html
REPO = os.path.abspath(ARGS[0])
SCRATCH = os.path.abspath(ARGS[1])
# 選填第 3 個參數：只掃描這個資料夾（須在 REPO 內），不填 = 整個 REPO
SCOPE = os.path.abspath(ARGS[2]) if len(ARGS) > 2 else REPO
try:
    inside = os.path.commonpath([REPO, SCOPE]) == REPO
except ValueError:  # Windows 不同磁碟
    inside = False
if not inside or not os.path.isdir(SCOPE):
    sys.exit(f"[錯誤] 掃描範圍必須是 REPO 內既有的資料夾：{SCOPE}")
SKIP_DIRS = {".git", ".github", ".claude", ".agents", "Log",
             "node_modules", "__pycache__", ".venv"}
EXTS = {".pdf": "pdf"} | ({".htm": "html", ".html": "html"} if HTML else {})

pending, skipped, total = [], 0, 0
for dirpath, dirnames, filenames in os.walk(SCOPE):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        kind = EXTS.get(os.path.splitext(fn)[1].lower())
        if not kind:
            continue
        total += 1
        src = os.path.abspath(os.path.join(dirpath, fn))
        md = os.path.splitext(src)[0] + ".md"
        if os.path.exists(md) and os.path.getsize(md) > 0:
            skipped += 1
            continue
        pending.append({
            "company": os.path.basename(dirpath),
            "type": kind,
            "src": src,
            "md": md,
            "save_path": os.path.abspath(dirpath),
        })

os.makedirs(SCRATCH, exist_ok=True)
out = os.path.join(SCRATCH, "convert_tasks.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump({"repo": REPO, "scratch": SCRATCH, "scope": SCOPE, "html": HTML, "total_pdf": total,
               "skipped": skipped, "pending": pending},
              f, ensure_ascii=False, indent=2)

print(f"掃描範圍: {SCOPE}")
print(f"總檔數（PDF{'+HTML' if HTML else ''}）: {total} / 已轉換跳過: {skipped} / 待轉換: {len(pending)}")
print(f"清單檔: {out}")
for i, t in enumerate(pending, 1):
    print(f"{i}. [{t['type']}] {t['src']}")
```

**待轉換為 0** → 跳過步驟 2、3，直接做步驟 4。

---

## 步驟 2 — 檢查工具

清單有 `type: pdf` 時：確認 MCP 工具 `convert_pdf_to_markdown`（來自 `pymupdf4llm-mcp`）可用。不可用 → PDF 跳過步驟 3（HTML 照轉），報告加註錯誤訊息。
清單只有 `type: html` → 不需要 MCP。

---

## 步驟 3 — 逐一轉檔

**3a. HTML**（清單有 `type: html` 才做）：一次轉完全部，單檔失敗會印 `FAIL` 並繼續：

```bash
python <SKILL>/scripts/html2md.py --tasks <SCRATCH>/convert_tasks.json
```

**3b. PDF**：對清單中每個 `type: pdf` 呼叫 `convert_pdf_to_markdown`，參數：

| 參數 | 值 |
|------|-----|
| `file_path` | 清單的 `src` 欄位（PDF 絕對路徑） |
| `save_path` | 清單的 `md` 欄位（**輸出 `.md` 的完整檔案絕對路徑**）。⚠️ 工具說明寫「directory」但實測（2026-09、2026-11）填資料夾會回 `[Errno 21] Is a directory`，必須填檔案路徑 |
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
# 指向暫存 pdf_images/ 的圖片連結：轉檔後圖片會被刪，連結變死鏈 → 成功的 .md 一律移除
IMG_RE = re.compile(r'^[ \t]*!\[[^\]]*\]\([^)]*pdf_images[^)]*\)[ \t]*\n?', re.M)

def strip_images(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    new, n = IMG_RE.subn('', text)
    if n:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    return n

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
    t["img_links_removed"] = strip_images(md)
    if os.path.exists(t["src"]):
        os.remove(t["src"])
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
L.append("轉換工具：PDF `pymupdf4llm-mcp` / `convert_pdf_to_markdown`；HTML `Convert2md/scripts/html2md.py`\n")
L.append(f"掃描範圍：`{data.get('scope', REPO)}`\n")
L.append("\n## 統計\n")
L.append("| 指標 | 數量 |")
L.append("|------|------|")
L.append(f"| 總掃描檔（PDF{'+HTML' if data.get('html') else ''}） | {data['total_pdf']} |")
L.append(f"| 跳過（已轉換） | {data['skipped']} |")
L.append(f"| 本次嘗試轉換 | {len(data['pending'])} |")
L.append(f"| 成功 | {len(ok)} |")
L.append(f"| 失敗：0 KB 或未產生 | {len(empty)} |")
L.append(f"| 失敗：CID 亂碼（已刪除） | {len(cid_fail)} |")
L.append("\n## 異常清單\n")
L.append("\n### 未產生或 0 KB\n")
L.append("| 公司 | 來源檔 | 預期 .md | 原因 |")
L.append("|------|-----|---------|------|")
for t in empty:
    why = "PDF 可能加密、損毀或純掃描" if t["type"] == "pdf" else "html2md 失敗（看步驟 3a 的 FAIL 訊息）"
    L.append(f"| {t['company']} | {os.path.basename(t['src'])} | "
             f"{os.path.basename(t['md'])} | {why} |")
if not empty:
    L.append("| — | — | — | 無 |")
L.append("\n### CID 亂碼過多（.md 已刪除）\n")
L.append("| 公司 | 來源檔 | 被刪的 .md | CID 次數 | CID 佔比% |")
L.append("|------|-----|-----------|---------|----------|")
for t in cid_fail:
    L.append(f"| {t['company']} | {os.path.basename(t['src'])} | "
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

| 結果 | `.md` | 來源 PDF／HTML |
|------|-------|-----|
| ✅ 成功 | 保留 | 刪除 |
| ❌ CID 亂碼 | 刪除 | **保留** |
| ❌ 未產生/0KB | 刪除 | **保留** |

> **轉換失敗時絕不刪來源檔。**

### CID 亂碼

PDF 嵌入式字型（CIDFont）解不開，產出 `(cid:123)` 亂碼。判定失敗門檻：佔比 ≥ 5% 或出現 ≥ 50 次。不要嘗試修補。

---

## 步驟 5 — 回報

把腳本 B 印出的報告貼給使用者，說明：掃描幾個 PDF（／HTML）、成功幾個、失敗幾個。

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
| `.md` 內有 `![](…/pdf_images/…)` | 腳本 B 會自動移除（成功的檔才處理） |
| 150 頁以上回「timed out after 60s」 | 伺服器仍在背景寫檔：不要重送，等 `.md` 出現且大小不再變動再做步驟 4 |
| html2md 印 `FAIL` | 記錄錯誤訊息 → 繼續；若是腳本 bug，修 `scripts/html2md.py`（`.claude` 與 `.agents` 兩份保持相同），`edgar.py selftest --offline` 有 html2md 測試案例 |
| HTML 轉出的 `.md` 還有大量 `<div`／`ix:` 標籤 | html2md 沒處理到的新 HTML 寫法 → 修 `scripts/html2md.py` 並在 `edgar.py selftest` 補案例 |
