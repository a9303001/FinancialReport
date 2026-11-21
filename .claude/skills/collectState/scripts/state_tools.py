#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collectState 輔助腳本（Windows / Linux / macOS 皆可，Python 3.9+）

子命令：
  purge     刪除 {cc}_state/ 內「三個月前」的資料（預設只列出，加 --apply 才真的刪）
  convert   把 PDF 以外的檔案（HTML / Word / Excel / PowerPoint / RTF / TXT / CSV / JSON …）轉成 .md，
            成功才刪原檔；PDF 交給 Convert2md Skill
  finalize  依 manifest 幫每份 .md 補上來源標頭、移除失效圖片連結，並重建 0.Index.md
  check     自檢：殘留非 .md 檔、檔名缺日期、超過保留期、缺來源標頭、空檔、CID 亂碼

所有子命令都只動 --folder 指定的 {cc}_state 資料夾，不碰其他目錄。

用法（路徑一律絕對路徑）：
  python state_tools.py purge    --folder <REPO>/jp_state [--months 3] [--today YYYY-MM-DD] [--apply]
  python state_tools.py convert  --folder <REPO>/jp_state --scratch <SCRATCH>
  python state_tools.py finalize --folder <REPO>/jp_state [--manifest <SCRATCH>/state_manifest.json]
  python state_tools.py check    --folder <REPO>/jp_state [--months 3]
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# 不受保留期限制、也不需要日期前綴的檔案（每次執行都會整份重寫）
PROTECTED = {"StateAnalysis.md", "0.Index.md"}
FOLDER_RE = re.compile(r"^[a-z]{2,3}_state$")
# yyyyMMdd_ 或 yyyyMM_ 開頭
DATE_PREFIX_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})?_")
META_MARK = "<!-- collectState:meta -->"
CID_RE = re.compile(r"\(cid:\d+\)")
IMG_LINE_RE = re.compile(r"^\s*!\[[^\]]*\]\((?:[^)]*pdf_images[^)]*|data:[^)]*)\)\s*$")
INLINE_DATA_IMG_RE = re.compile(r"!\[[^\]]*\]\(data:[^)]*\)")
SHELL_HINTS = ("Just a moment", "Enable JavaScript", "enable JavaScript", "Access Denied",
               "請啟用 JavaScript", "JavaScriptを有効", "Attention Required")

LEGACY_OFFICE = {".doc": "docx", ".rtf": "docx", ".odt": "docx", ".wps": "docx",
                 ".xls": "xlsx", ".ods": "xlsx", ".et": "xlsx",
                 ".ppt": "pptx", ".odp": "pptx", ".dps": "pptx"}
CONVERTIBLE = {".html", ".htm", ".xhtml", ".shtml", ".docx", ".xlsx", ".xlsm", ".pptx",
               ".csv", ".tsv", ".txt", ".json", ".xml", ".epub"} | set(LEGACY_OFFICE)
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".tif", ".tiff"}


# ───────────────────────── 共用 ─────────────────────────
def out(msg: str = "") -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", "replace"))
    sys.stdout.flush()


def safe_folder(p: str) -> Path:
    folder = Path(p).resolve()
    if not FOLDER_RE.match(folder.name):
        sys.exit(f"[拒絕] {folder} 不是 <cc>_state 資料夾（例：jp_state、hk_state）")
    if not folder.is_dir():
        sys.exit(f"[錯誤] 資料夾不存在：{folder}")
    return folder


def months_ago(d: dt.date, n: int) -> dt.date:
    y, m = d.year, d.month - n
    while m <= 0:
        m += 12
        y -= 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def parse_today(s: str | None) -> dt.date:
    return dt.date.fromisoformat(s) if s else dt.date.today()


def prefix_date(name: str):
    """回傳 (date, kind)。kind = 'day' | 'month' | None。月檔以該月最後一天計。"""
    m = DATE_PREFIX_RE.match(name)
    if not m:
        return None, None
    y, mo, d = int(m.group(1)), int(m.group(2)), m.group(3)
    try:
        if d:
            return dt.date(y, mo, int(d)), "day"
        return dt.date(y, mo, calendar.monthrange(y, mo)[1]), "month"
    except ValueError:
        return None, None


def git_added_date(path: Path):
    """檔案第一次被 commit 的日期（git clone 會重設 mtime，所以不能只看 mtime）。"""
    try:
        r = subprocess.run(["git", "log", "--diff-filter=A", "--follow", "--format=%cs", "--", path.name],
                           cwd=path.parent, capture_output=True, text=True, timeout=30)
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        if r.returncode == 0 and lines:
            return dt.date.fromisoformat(lines[-1].strip())
    except Exception:
        pass
    return None


def file_date(path: Path):
    d, kind = prefix_date(path.name)
    if d:
        return d, f"檔名前綴({kind})"
    g = git_added_date(path)
    if g:
        return g, "git 首次加入日"
    return dt.date.fromtimestamp(path.stat().st_mtime), "檔案 mtime"


def iter_files(folder: Path):
    for p in sorted(folder.rglob("*")):
        if p.is_file() and not any(part.startswith(".") for part in p.relative_to(folder).parts):
            yield p


def remove_empty_dirs(folder: Path) -> None:
    for d in sorted((p for p in folder.rglob("*") if p.is_dir()), key=lambda x: len(x.parts), reverse=True):
        try:
            d.rmdir()
        except OSError:
            pass


# ───────────────────────── purge ─────────────────────────
def cmd_purge(a) -> int:
    folder = safe_folder(a.folder)
    today = parse_today(a.today)
    cutoff = months_ago(today, a.months)
    keep, drop = [], []
    for p in iter_files(folder):
        rel = p.relative_to(folder).as_posix()
        if p.name in PROTECTED and p.parent == folder:
            keep.append((rel, "受保護檔", "-"))
            continue
        d, how = file_date(p)
        (keep if d >= cutoff else drop).append((rel, how, d.isoformat()))
    out(f"# purge {'(APPLY)' if a.apply else '(dry-run，未刪除)'}")
    out(f"- 今天：{today}｜保留期：{a.months} 個月｜截止日：{cutoff}（早於此日的資料刪除）")
    out(f"- 保留 {len(keep)} 個｜刪除 {len(drop)} 個")
    for rel, how, d in drop:
        out(f"  - 刪除：{rel}（{d}，依{how}）")
        if a.apply:
            (folder / rel).unlink()
    if a.apply:
        remove_empty_dirs(folder)
    nodate = [k for k in keep if k[1] not in ("受保護檔",) and not k[1].startswith("檔名前綴")]
    for rel, how, d in nodate:
        out(f"  - ⚠️ 無日期前綴（保留，依{how}={d}）：{rel} → 請改成 yyyyMMdd_ 開頭")
    return 0


# ───────────────────────── convert ─────────────────────────
def tidy_md(text: str) -> str:
    lines = [l.rstrip() for l in text.replace("\r\n", "\n").split("\n") if not IMG_LINE_RE.match(l)]
    text = INLINE_DATA_IMG_RE.sub("", "\n".join(lines))
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


def via_markitdown(src: Path) -> str:
    from markitdown import MarkItDown  # pip install "markitdown[all]"
    return MarkItDown().convert(str(src)).text_content


def via_pandoc(src: Path) -> str:
    fmt = {".html": "html", ".htm": "html", ".xhtml": "html", ".shtml": "html",
           ".docx": "docx", ".epub": "epub", ".odt": "odt", ".rtf": "rtf"}.get(src.suffix.lower())
    if not fmt or not shutil.which("pandoc"):
        raise RuntimeError("pandoc 不適用")
    r = subprocess.run(["pandoc", "-f", fmt, "-t", "gfm", "--wrap=none", str(src)],
                       capture_output=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace")[:300])
    return r.stdout.decode("utf-8", "replace")


def read_text_any(src: Path) -> str:
    raw = src.read_bytes()
    for enc in ("utf-8-sig", "cp932", "gb18030", "big5", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def via_builtin(src: Path) -> str:
    ext = src.suffix.lower()
    if ext in (".html", ".htm", ".xhtml", ".shtml"):
        from bs4 import BeautifulSoup
        from markdownify import markdownify
        soup = BeautifulSoup(read_text_any(src), "html.parser")
        for t in soup(["script", "style", "noscript", "nav", "footer", "header", "aside", "form", "iframe"]):
            t.decompose()
        body = soup.find("article") or soup.find("main") or soup.body or soup
        return markdownify(str(body), heading_style="ATX")
    if ext in (".txt", ".csv", ".tsv", ".xml"):
        lang = {".csv": "csv", ".tsv": "tsv", ".xml": "xml"}.get(ext, "")
        t = read_text_any(src)
        return t if ext == ".txt" else f"```{lang}\n{t}\n```"
    if ext == ".json":
        t = json.dumps(json.loads(read_text_any(src)), ensure_ascii=False, indent=2)
        return f"```json\n{t}\n```"
    raise RuntimeError("無內建轉換器")


def legacy_to_ooxml(src: Path, scratch: Path) -> Path:
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        raise RuntimeError("找不到 LibreOffice（soffice），無法轉換舊版 Office 檔")
    outdir = scratch / "state_lo"
    outdir.mkdir(parents=True, exist_ok=True)
    target = LEGACY_OFFICE[src.suffix.lower()]
    r = subprocess.run([exe, "--headless", "--convert-to", target, "--outdir", str(outdir), str(src)],
                       capture_output=True, timeout=300)
    conv = outdir / (src.stem + "." + target)
    if r.returncode != 0 or not conv.exists():
        raise RuntimeError("LibreOffice 轉換失敗：" + r.stderr.decode("utf-8", "replace")[:300])
    return conv


def quality(text: str):
    body = re.sub(r"\s+", "", text)
    if len(body) < 200:
        return False, f"內容過短（{len(body)} 字）"
    if len(body) < 3000 and any(h in text for h in SHELL_HINTS):
        return False, "疑似 JS 外殼／封鎖頁"
    cids = CID_RE.findall(text)
    if len(cids) >= 50 or (text and sum(map(len, cids)) / len(text) >= 0.05):
        return False, f"CID 亂碼 {len(cids)} 次"
    return True, "OK"


HTML_EXT = {".html", ".htm", ".xhtml", ".shtml"}


def preclean_html(src: Path, scratch: Path) -> Path:
    """先拿掉選單、頁尾、側欄、腳本等雜訊，只留正文（article > main > body）。"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return src
    soup = BeautifulSoup(read_text_any(src), "html.parser")
    for t in soup(["script", "style", "noscript", "nav", "footer", "header", "aside", "form", "iframe", "svg"]):
        t.decompose()
    body = soup.find("article") or soup.find("main") or soup.body or soup
    title = soup.title.get_text(strip=True) if soup.title else ""
    outdir = scratch / "state_lo"
    outdir.mkdir(parents=True, exist_ok=True)
    dst = outdir / (src.stem + ".clean.html")
    dst.write_text(f"<html><head><meta charset='utf-8'><title>{title}</title></head><body>{body}</body></html>",
                   encoding="utf-8")
    return dst


def convert_one(src: Path, scratch: Path):
    work = src
    if src.suffix.lower() in LEGACY_OFFICE:
        work = legacy_to_ooxml(src, scratch)
    elif src.suffix.lower() in HTML_EXT:
        work = preclean_html(src, scratch)
    errors = []
    for name, fn in (("markitdown", via_markitdown), ("pandoc", via_pandoc), ("builtin", via_builtin)):
        try:
            # builtin 的 HTML 路徑自己會清理，直接吃原檔即可
            text = tidy_md(fn(src if (name == "builtin" and work.name.endswith(".clean.html")) else work))
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {str(e)[:160]}")
            continue
        ok, why = quality(text)
        if ok:
            return text, name
        errors.append(f"{name}: {why}")
    raise RuntimeError("；".join(errors))


def cmd_convert(a) -> int:
    folder = safe_folder(a.folder)
    scratch = Path(a.scratch).resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    ok, fail, skipped, pdfs, images, unknown = [], [], [], [], [], []
    for p in iter_files(folder):
        ext = p.suffix.lower()
        if ext == ".md":
            continue
        if ext == ".pdf":
            pdfs.append(p)
            continue
        if ext in IMAGE_EXT:
            images.append(p)
            continue
        if ext not in CONVERTIBLE:
            unknown.append(p)
            continue
        md = p.with_suffix(".md")
        if md.exists() and md.stat().st_size > 0:
            p.unlink()
            skipped.append(p)
            continue
        try:
            text, how = convert_one(p, scratch)
        except Exception as e:  # noqa: BLE001
            fail.append((p, str(e)))
            continue
        md.write_text(text, encoding="utf-8")
        p.unlink()
        ok.append((p, how))
    shutil.rmtree(scratch / "state_lo", ignore_errors=True)
    rel = lambda x: x.relative_to(folder).as_posix()  # noqa: E731
    out("# convert（PDF 以外 → .md）")
    out(f"- 成功 {len(ok)}｜失敗 {len(fail)}｜已有 .md 而刪原檔 {len(skipped)}｜PDF 待 Convert2md {len(pdfs)}"
        f"｜圖片 {len(images)}｜不支援 {len(unknown)}")
    for p, how in ok:
        out(f"  - ✅ {rel(p)} → {p.with_suffix('.md').name}（{how}）")
    for p, why in fail:
        out(f"  - ❌ {rel(p)}：{why}（原檔保留）")
    for p in pdfs:
        out(f"  - 📄 PDF 尚未轉換（請跑 Convert2md）：{rel(p)}")
    for p in images:
        out(f"  - 🖼️ 圖片無法轉文字：{rel(p)} → 把圖表數字改寫進 .md 後手動刪除")
    for p in unknown:
        out(f"  - ❓ 不支援的格式：{rel(p)}")
    return 1 if fail else 0


# ───────────────────────── finalize ─────────────────────────
def meta_block(m: dict, today: dt.date) -> str:
    title = m.get("title") or "N/A"
    url = m.get("url") or ""
    src = m.get("publisher") or "N/A"
    link = f"[原文]({url})" if url else "原文網址：N/A"
    lines = [META_MARK,
             f"- **標題**：{title}",
             f"- **來源**：{src}｜{link}",
             f"- **發布日**：{m.get('published') or 'N/A'}",
             f"- **收集日**：{m.get('collected') or today.isoformat()}",
             f"- **類型**：{m.get('type') or 'N/A'}"]
    if m.get("note"):
        lines.append(f"- **備註**：{m['note']}")
    return "\n".join(lines) + "\n\n---\n\n"


def read_meta(md: Path) -> dict:
    head = md.read_text(encoding="utf-8", errors="replace")[:3000]
    meta = {}
    if META_MARK not in head:
        return meta
    for key, pat in (("title", r"\*\*標題\*\*：(.*)"), ("publisher", r"\*\*來源\*\*：([^｜\n]*)"),
                     ("url", r"\[原文\]\(([^)]*)\)"), ("published", r"\*\*發布日\*\*：(.*)"),
                     ("type", r"\*\*類型\*\*：(.*)")):
        mm = re.search(pat, head)
        if mm:
            meta[key] = mm.group(1).strip()
    return meta


def cmd_finalize(a) -> int:
    folder = safe_folder(a.folder)
    today = parse_today(a.today)
    manifest = []
    if a.manifest and Path(a.manifest).exists():
        manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    by_stem = {Path(m["file"]).stem: m for m in manifest if m.get("file")}
    tagged, cleaned, missing = 0, 0, []
    for md in iter_files(folder):
        if md.suffix.lower() != ".md" or (md.name in PROTECTED and md.parent == folder):
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        new = tidy_md(text)
        m = by_stem.get(md.stem)
        if META_MARK not in new and m:
            new = meta_block(m, today) + new
            tagged += 1
        if new != text:
            md.write_text(new, encoding="utf-8")
            cleaned += 1
    for stem, m in by_stem.items():
        if not list(folder.rglob(stem + ".md")):
            missing.append(m["file"])
    # 重建 0.Index.md
    rows = []
    for md in iter_files(folder):
        if md.suffix.lower() != ".md" or (md.name in PROTECTED and md.parent == folder):
            continue
        meta = read_meta(md)
        d, _ = prefix_date(md.name)
        rows.append((meta.get("published") or (d.isoformat() if d else "N/A"),
                     meta.get("type") or ("Digest" if "輿情新聞" in md.name else "N/A"),
                     meta.get("publisher") or "N/A",
                     (meta.get("title") or md.stem).replace("|", "／"),
                     md.relative_to(folder).as_posix(),
                     meta.get("url") or ""))
    rows.sort(key=lambda r: ("0" if r[0] == "N/A" else "1") + r[0], reverse=True)
    idx = [f"# {folder.name} 資料索引", "",
           f"- 產生時間：{dt.datetime.now():%Y-%m-%d %H:%M}（由 collectState `state_tools.py finalize` 自動產生，勿手改）",
           f"- 檔案數：{len(rows)}｜保留期：最近 3 個月", "",
           "| 發布日 | 類型 | 來源 | 標題 | 檔案 | 原文 |", "| :--- | :--- | :--- | :--- | :--- | :--- |"]
    for r in rows:
        link = f"[link]({r[5]})" if r[5] else "—"
        idx.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | [{Path(r[4]).name}]({r[4].replace(' ', '%20')}) | {link} |")
    (folder / "0.Index.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
    out("# finalize")
    out(f"- 補來源標頭 {tagged} 份｜整理（移除失效圖片／多餘空行）{cleaned} 份｜索引 {len(rows)} 筆 → 0.Index.md")
    for f in missing:
        out(f"  - ⚠️ manifest 有、資料夾找不到對應 .md：{f}（下載或轉檔失敗？）")
    return 0


# ───────────────────────── check ─────────────────────────
def cmd_check(a) -> int:
    folder = safe_folder(a.folder)
    today = parse_today(a.today)
    cutoff = months_ago(today, a.months)
    issues = []
    for p in iter_files(folder):
        rel = p.relative_to(folder).as_posix()
        if p.name in PROTECTED and p.parent == folder:
            continue
        if p.suffix.lower() != ".md":
            issues.append(f"非 .md 殘留：{rel}")
            continue
        if p.stat().st_size == 0:
            issues.append(f"空檔：{rel}")
            continue
        d, _ = prefix_date(p.name)
        if not d:
            issues.append(f"檔名缺 yyyyMMdd_／yyyyMM_ 前綴：{rel}")
        elif d < cutoff:
            issues.append(f"超過保留期（{d} < {cutoff}）：{rel}")
        text = p.read_text(encoding="utf-8", errors="replace")
        if "輿情新聞" not in p.name and META_MARK not in text[:3000]:
            issues.append(f"缺來源標頭（finalize 未補）：{rel}")
        c = len(CID_RE.findall(text))
        if c >= 50:
            issues.append(f"CID 亂碼 {c} 次：{rel}")
    for must in ("StateAnalysis.md", "0.Index.md"):
        if not (folder / must).exists():
            issues.append(f"缺必要檔：{must}")
    out(f"# check（截止日 {cutoff}）")
    out("- ✅ 全部通過" if not issues else f"- ❌ {len(issues)} 項問題")
    for i in issues:
        out(f"  - {i}")
    return 1 if issues else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="collectState helper")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("purge", "convert", "finalize", "check"):
        s = sub.add_parser(name)
        s.add_argument("--folder", required=True)
        s.add_argument("--today")
        if name in ("purge", "check"):
            s.add_argument("--months", type=int, default=3)
        if name == "purge":
            s.add_argument("--apply", action="store_true")
        if name == "convert":
            s.add_argument("--scratch", required=True)
        if name == "finalize":
            s.add_argument("--manifest")
    a = ap.parse_args()
    return {"purge": cmd_purge, "convert": cmd_convert, "finalize": cmd_finalize, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
