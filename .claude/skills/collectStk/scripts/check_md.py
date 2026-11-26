#!/usr/bin/env python3
"""collectStk §7.2 財報 Markdown 驗證（Convert2md 之後、或 Apify/手動轉檔之後跑）。

用法：
  python .claude/skills/collectStk/scripts/check_md.py --names "ＯＡＴアグリオ,OAT Agrio,4979" \
      [--source "https://..."] <file.md> [<file.md> ...]

每個檔：
  1. 大小 < 10KB → FAIL（多半是封鎖頁或殘檔）
  2. `(cid:` 次數 ≥ 50 或佔比 ≥ 5% → FAIL（字型缺字，無法修復，改抓英文版或換來源）
  3. 前 15,000 字（約前 4 頁）找不到任何一個 --names → FAIL（抓錯公司）
  4. 刪除指向暫存 pdf_images/ 的圖片連結行（就地修改）
  5. 有 --source 且檔頭沒有來源註記 → 在第一行插入 `<!-- Source: ... -->`
只回報、不刪檔：FAIL 的檔由 AI 依 §7.2 處置並寫進報告 §4。結束碼：全部 PASS = 0，否則 1。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CID_RE = re.compile(r"\(cid:\d+\)")
IMG_RE = re.compile(r"^\s*!\[[^\]]*\]\([^)]*pdf_images[^)]*\)\s*$")


def _norm(s: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKC", s).lower()


def check(p: Path, names: list[str], source: str | None) -> tuple[bool, list[str]]:
    notes: list[str] = []
    if not p.is_file():
        return False, ["檔案不存在"]
    text = p.read_text(encoding="utf-8", errors="replace")
    ok = True

    lines = text.split("\n")
    kept = [l for l in lines if not IMG_RE.match(l)]
    removed = len(lines) - len(kept)
    if removed:
        notes.append(f"已移除 {removed} 行 pdf_images 圖片連結")
    if source and "Source:" not in "\n".join(kept[:5]) and "來源：" not in "\n".join(kept[:5]):
        kept.insert(0, f"<!-- Source: {source} -->")
        notes.append("已補來源標頭")
    if removed or len(kept) != len(lines):
        text = "\n".join(kept)
        p.write_text(text, encoding="utf-8")

    size = p.stat().st_size
    if size < 10 * 1024:
        ok = False
        notes.append(f"FAIL 檔案只有 {size} bytes（< 10KB）")
    hits = CID_RE.findall(text)
    ratio = sum(map(len, hits)) / max(len(text), 1)
    if len(hits) >= 50 or ratio >= 0.05:
        ok = False
        notes.append(f"FAIL CID 亂碼 {len(hits)} 次（{ratio:.1%}）")
    elif hits:
        notes.append(f"CID {len(hits)} 次（未達門檻）")
    if names:
        head = _norm(text[:15000])
        if not any(_norm(n) in head for n in names if n.strip()):
            ok = False
            notes.append("FAIL 前 15,000 字找不到公司名稱／代碼：" + "、".join(names))
    return ok, notes


def main() -> None:
    ap = argparse.ArgumentParser(description="collectStk 財報 Markdown 驗證")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--names", default="", help="公司名稱／英文名／代碼，逗號分隔，任一出現即通過")
    ap.add_argument("--source", help="原始來源網址（檔頭沒有來源註記時補上）")
    a = ap.parse_args()
    names = [n.strip() for n in a.names.split(",") if n.strip()]
    all_ok = True
    for f in a.files:
        ok, notes = check(Path(f), names, a.source)
        all_ok &= ok
        print(f"{'PASS' if ok else 'FAIL'}  {f}" + (f"  — {'；'.join(notes)}" if notes else ""))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
