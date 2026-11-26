#!/usr/bin/env python3
"""collectStk Phase 1 盤點：列出公司資料夾裡已有哪些財報期別、輿情涵蓋到哪一天。

用法：
  python .claude/skills/collectStk/scripts/inventory.py <公司資料夾> [--ticker 3445] [--json]

只讀不寫。認得統一命名與 §7.1 列出的舊命名；日股另用檔頭內容判斷實際文件種類
（有価証券報告書／半期報告書／決算短信／資産運用報告），因為舊檔常把決算短信存成 _Quarter_。
只用 Python 標準函式庫。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

# 檔頭最早出現的關鍵字決定種類（與 edinet.py 同一套規則；決算短信封面有「半期報告書提出予定日」，不可只搜有無）
KIND_PATTERNS = [
    ("有価証券報告書", re.compile(r"有価証券報告書|Annual Securities Report")),
    ("四半期報告書", re.compile(r"四半期報告書")),
    ("半期報告書", re.compile(r"(?<!四)半期報告書(?!提出)")),
    ("決算短信", re.compile(r"決算短信|Summary of (?:Consolidated )?Financial Results", re.I)),
    ("資産運用報告", re.compile(r"資産運用報告|Asset Management Report", re.I)),
    ("10-K", re.compile(r"FORM\s+10-K\b|Form 10-K\b")),
    ("10-Q", re.compile(r"FORM\s+10-Q\b|Form 10-Q\b")),
    ("20-F", re.compile(r"FORM\s+20-F\b")),
    ("40-F", re.compile(r"FORM\s+40-F\b")),
    ("6-K", re.compile(r"FORM\s+6-K\b", re.I)),
    ("港股業績公告", re.compile(r"contents of this announcement|本公告的?內容", re.I)),
    ("中期報告", re.compile(r"interim report|中期報告", re.I)),
    ("合併財務報告", re.compile(r"合併財務報告|Consolidated Financial Statements", re.I)),
    ("年報", re.compile(r"年報|Annual Report", re.I)),
]

RULES = [  # (regex on file stem, category, period-group builder)
    (r"^(?P<t>[\w-]+?)_AnnualReport_(?P<p>\d{4})_Results$", "年報(業績公告)"),
    (r"^(?P<t>[\w-]+?)_Quarter_(?P<p>\d{4}H1)_Results$", "季報(業績公告)"),
    (r"^(?P<t>[\w-]+?)_AnnualReport_(?P<p>\d{4}(?:[A-Z][a-z]{2})?)(?P<x>_EDINET|_HKEX|_EDGAR|_EX13|_EDGAR_EX13|_MOPS)?$", "年報"),
    (r"^(?P<t>[\w-]+?)_Quarter_(?P<p>\d{4}(?:Q[1-4]|H1|[A-Z][a-z]{2}))(?P<x>_EDINET|_HKEX|_EDGAR|_MOPS)?$", "季報"),
    (r"^(?P<t>[\w-]+?)_Presentation_(?P<p>.+)$", "簡報"),
    (r"^(?P<t>[\w-]+?)_annual_(?P<p>\d{4})$", "年報(舊名)"),
    (r"^(?P<t>[\w-]+?)_(?:quarter|QuarterlyReport)_(?P<p>\d{4}Q[1-4])$", "季報(舊名)"),
    (r"^(?P<t>[\w-]+?)_(?:interim|InterimReport)_(?P<p>\d{4})$", "半年報(舊名)"),
    (r"^(?P<t>[\w-]+?)_InterimResults_(?P<p>\d{4})$", "半年報(舊名業績公告)"),
    (r"^(?P<p>20\d{11})$", "港股(HKEX 編號原名)"),
    # TWSE 原檔名（可帶下載時間戳 _yyyyMMdd_HHmmss 與「2022年報」之類前綴；規則與 mops.py alias_patterns 一致）
    (r"^(?:.*?\D)?(?P<p>\d{4})_(?P<t>[0-9A-Za-z]+?)_\d{8}F(?:04|E4|E6)(?:_\d{8}_\d{6})?$", "年報(TWSE原名)"),
    (r"^(?P<p>\d{6})_(?P<t>[0-9A-Za-z]+?)_AI[1-3A-C](?:_\d{8}_\d{6})?$", "季報(TWSE原名)"),
    (r"^(?P<t>[\w-]+?)_(?P<p>\d{4})_annual_report$", "年報(舊名)"),
    (r"^(?P<t>[\w-]+?)_(?P<p>\d{4}Q[1-4])_quarterly_report$", "季報(舊名)"),
    (r"^(?P<t>[\w-]+?)_10K_(?P<p>[\d-]+)$", "年報(10-K)"),
    (r"^(?P<t>[\w-]+?)_10Q_(?P<p>[\d-]+)$", "季報(10-Q)"),
    (r"^(?P<t>[a-z][a-z0-9.]*)-(?P<p>20\d{6})$", "SEC原檔名(看檔頭)"),
    (r"^(?P<p>\d{6}).*有価証券報告書.*$", "年報(日文原名)"),
    (r"^(?P<p>\d{4}).*有価証券報告書.*$", "年報(日文原名)"),
    (r"^(?P<p>\d{8})?_?.*決算短信.*$", "決算短信(日文原名)"),
    (r"^(?P<p>\d{4})_PublicOpinion$", "輿情(年度合併)"),
    (r"^(?P<p>\d{6})_輿情新聞$", "輿情(當月)"),
    (r"^AnalysisResult$", "分析結果"),
]
DATE_RE = re.compile(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})")


def content_kind(p: Path) -> str:
    if p.suffix.lower() != ".md":
        return "(未轉檔)"
    try:
        with p.open(encoding="utf-8", errors="replace") as f:
            head = f.read(6000)
    except OSError:
        return "?"
    best = None
    for kind, pat in KIND_PATTERNS:
        m = pat.search(head)
        if m and (best is None or m.start() < best[1]):
            best = (kind, m.start())
    return best[0] if best else "?"


def latest_date(p: Path) -> str | None:
    """輿情檔內出現過、且不晚於今天的最新日期（判斷上次收集到哪一天，§8.1）。
    內文常提到未來日期（貸款到期、交割日），所以超過今天的一律排除。"""
    today = date.today().isoformat()
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    ds = []
    for y, m, d in DATE_RE.findall(text):
        try:
            if 1 <= int(m) <= 12 and 1 <= int(d) <= 31:
                ds.append(f"{y}-{int(m):02d}-{int(d):02d}")
        except ValueError:
            pass
    ds = [d for d in ds if d <= today]
    return max(ds) if ds else None


def classify(p: Path) -> dict:
    stem = p.stem
    for rx, cat in RULES:
        m = re.match(rx, stem, re.I if "舊名" in cat else 0)
        if m:
            g = m.groupdict()
            return {"file": p.name, "category": cat, "period": g.get("p") or "",
                    "ticker": g.get("t") or "", "edinet_suffix": bool(g.get("x"))}
    return {"file": p.name, "category": "其他", "period": "", "ticker": "", "edinet_suffix": False}


def main() -> None:
    ap = argparse.ArgumentParser(description="collectStk 公司資料夾盤點")
    ap.add_argument("folder")
    ap.add_argument("--ticker", help="只列這個代碼的財報（雙重上市資料夾會混有另一市場代碼，如 3445 / 688432）")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    folder = Path(a.folder)
    if not folder.is_dir():
        sys.exit(f"[inventory] 資料夾不存在：{folder}（新公司 → 依 §6 建立）")

    rows = []
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.suffix.lower() not in (".md", ".pdf", ".html", ".htm"):
            continue
        r = classify(p)
        if r["category"].startswith("SEC原檔名"):  # evtc-20260630.md：檔名看不出年報或季報 → 看檔頭
            k = content_kind(p)
            r["category"] = ("年報(SEC原檔名)" if k in ("10-K", "20-F", "40-F") else
                             "季報(SEC原檔名)" if k in ("10-Q", "6-K") else "其他")
        if r["category"].startswith(("年報", "季報", "半年報", "決算短信", "港股")):
            r["content"] = content_kind(p)
        if r["category"].startswith("輿情"):
            r["latest_date"] = latest_date(p)
        r["size_kb"] = round(p.stat().st_size / 1024)
        if a.ticker and r["ticker"] and r["ticker"].upper() != a.ticker.upper():
            r["other_ticker"] = True
        rows.append(r)

    pdf_pending = [r["file"] for r in rows if r["file"].lower().endswith(".pdf")
                   and not (folder / (Path(r["file"]).stem + ".md")).exists()]
    tiny = [r["file"] for r in rows if r["size_kb"] < 10 and r["category"].startswith(("年報", "季報"))]
    empty = [p.name for p in folder.iterdir() if p.is_file() and p.stat().st_size == 0]
    summary = {"folder": str(folder.resolve()), "files": rows, "pdf_not_converted": pdf_pending,
               "suspicious_small_reports": tiny, "empty_files": empty}
    if a.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    print(f"# 盤點：{folder.resolve()}")
    for cat_prefix in ("年報", "季報", "半年報", "港股", "決算短信", "簡報", "輿情", "分析結果", "其他"):
        sel = [r for r in rows if r["category"].startswith(cat_prefix)]
        if not sel:
            continue
        print(f"\n## {cat_prefix}")
        for r in sorted(sel, key=lambda r: r["period"], reverse=True):
            extra = []
            if r.get("content"):
                extra.append(f"內容={r['content']}")
            if r.get("latest_date"):
                extra.append(f"最新日期={r['latest_date']}")
            if r.get("other_ticker"):
                extra.append("另一市場代碼")
            print(f"- {r['period'] or '-':<10} {r['file']}  ({r['size_kb']} KB{'; ' + '; '.join(extra) if extra else ''})")
    if pdf_pending:
        print("\n⚠ 尚未轉 Markdown 的 PDF：" + "、".join(pdf_pending) + " → Phase 4 Convert2md")
    if empty:
        print("\n⚠ 0 byte 空檔：" + "、".join(empty) + " → 報告 §4 註明，確認無用後刪除")
    if tiny:
        print("\n⚠ 小於 10KB 的財報檔（可能是封鎖頁或殘檔，§7.2）：" + "、".join(tiny))


if __name__ == "__main__":
    main()
