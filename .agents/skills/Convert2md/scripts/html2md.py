#!/usr/bin/env python3
"""Convert2md — HTML → Markdown（SEC EDGAR 10-K / 10-Q / 20-F / 6-K 的 HTML / iXBRL）。

只用 Python 標準函式庫（Windows / macOS / Linux / Claude Code 雲端皆可）。

用法：
  python html2md.py <in.htm> <out.md>              # 轉單一檔
  python html2md.py --tasks <SCRATCH>/convert_tasks.json   # 轉清單內所有 type=html 的任務

處理重點（SEC 實測 2026-11）：
  - 丟掉 <ix:header>、display:none、<script>/<style>/<head>（iXBRL 隱藏 context 會塞爆 md）
  - 表格：合併 "$" / ")" / "%" 這類獨立儲存格、刪全空欄與全空列；單欄／單格的排版用表格改成段落
  - 粗體短段落 → `### 標題`（SEC 用粗體 span 當 Item 標題，方便 AI 跳段）
  - 移除零寬字元、把 &nbsp; 換成空白、刪掉每頁重複的「Table of Contents」連結列
結束碼：0 成功／1 有檔案失敗。
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

VOID = {"br", "img", "hr", "meta", "link", "input", "col", "area", "base", "wbr", "source", "param"}
SKIP = {"script", "style", "head", "title", "noscript", "ix:header", "xbrli:context", "template"}
BLOCK = {"p", "div", "section", "article", "center", "blockquote", "li", "ul", "ol", "dl", "dt", "dd",
         "h1", "h2", "h3", "h4", "h5", "h6", "pre", "address", "header", "footer", "body", "html",
         "font"}  # 舊式 EDGAR HTML 常用 <font> 包整段，當成區塊較安全
HEAD = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "####", "h6": "####"}
HIDDEN_RE = re.compile(r"display\s*:\s*none", re.I)
BOLD_RE = re.compile(r"font-weight\s*:\s*(bold|[6-9]00)", re.I)
ZW_RE = re.compile(r"[​‌‍﻿­]")
JOIN_PREV = re.compile(r"^(\)|%|\)%|%\)|\)\s*%|pts?\.?|bps)$", re.I)
JOIN_NEXT = re.compile(r"^(\$|US\$|€|£|¥|NT\$|HK\$|Rp|RMB|\(|\$\s*\()$")


class _Cell:
    __slots__ = ("parts", "span")

    def __init__(self, span: int):
        self.parts: list[str] = []
        self.span = span


class H2M(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []          # 已完成的 markdown 區塊
        self.buf: list[str] = []          # 目前段落文字
        self.bold_chars = 0
        self.all_chars = 0
        self.stack: list[tuple[str, bool, bool]] = []  # (tag, hidden, bold)
        self.hidden = 0
        self.bold = 0
        self.skip = 0
        self.tables: list[list[list[_Cell]]] = []  # 巢狀表格堆疊；每個 table = rows；row = cells
        self.cell_stack: list[_Cell | None] = []
        self.head_level: str | None = None

    # ------------------------------------------------------------ text sinks
    def _emit_text(self, s: str) -> None:
        if self.tables and self.cell_stack and self.cell_stack[-1] is not None:
            self.cell_stack[-1].parts.append(s)
            return
        if self.tables:  # 表格內但不在儲存格（雜訊空白）
            return
        self.buf.append(s)
        n = len(s.strip())
        self.all_chars += n
        if self.bold:
            self.bold_chars += n

    def _flush(self) -> None:
        text = re.sub(r"[ \t]+", " ", "".join(self.buf)).strip()
        self.buf = []
        bold_all = self.all_chars > 0 and self.bold_chars >= self.all_chars * 0.95
        self.bold_chars = self.all_chars = 0
        if not text:
            return
        if self.head_level:
            text = f"{HEAD[self.head_level]} {text}"
        elif bold_all and len(text) <= 150 and not text.startswith(("(", "$")) and re.search(r"[A-Za-z]", text):
            text = f"### {text}"
        self.out.append(text)

    # ------------------------------------------------------------ parser hooks
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        a = {k.lower(): (v or "") for k, v in attrs}
        style = a.get("style", "")
        if tag in VOID:
            if self.skip or self.hidden:
                return
            if tag == "br":
                if self.tables and self.cell_stack and self.cell_stack[-1] is not None:
                    self.cell_stack[-1].parts.append(" ")
                else:
                    self._flush()
            elif tag == "hr":
                self._flush()
            return
        hidden = bool(HIDDEN_RE.search(style)) or tag in SKIP or "hidden" in a
        bold = tag in ("b", "strong") or bool(BOLD_RE.search(style))
        self.stack.append((tag, hidden, bold))
        self.hidden += hidden
        self.bold += bold
        if self.hidden:
            return
        if tag == "table":
            self._flush()
            self.tables.append([])
            self.cell_stack.append(None)
        elif tag == "tr" and self.tables:
            self._close_cell()
            self.tables[-1].append([])
        elif tag in ("td", "th") and self.tables:
            self._close_cell()
            if not self.tables[-1]:
                self.tables[-1].append([])
            try:
                span = max(1, min(20, int(a.get("colspan", "1") or 1)))
            except ValueError:
                span = 1
            c = _Cell(span)
            self.tables[-1][-1].append(c)
            self.cell_stack[-1] = c
        elif tag in HEAD and not self.tables:
            self._flush()
            self.head_level = tag
        elif tag in BLOCK or tag == "p":
            if self.tables and self.cell_stack and self.cell_stack[-1] is not None:
                self.cell_stack[-1].parts.append(" ")
            else:
                self._flush()

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in VOID:
            self.handle_starttag(tag, attrs)
        # 自閉合的非 void 元素（如 <div/>）不影響結構

    def _close_cell(self) -> None:
        if self.cell_stack:
            self.cell_stack[-1] = None

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in VOID:
            return
        idx = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i][0] == tag), None)
        if idx is None:
            return  # 多餘的結束標籤（舊式 HTML）→ 忽略
        was_hidden_before = self.hidden
        for t, h, b in reversed(self.stack[idx:]):
            self.hidden -= h
            self.bold -= b
            if not (was_hidden_before and h):  # 隱藏區塊內的結構不處理
                self._end_struct(t, inside_hidden=self.hidden > 0)
        del self.stack[idx:]

    def _end_struct(self, tag: str, inside_hidden: bool) -> None:
        if inside_hidden:
            return
        if tag == "table" and self.tables:
            self._close_cell()
            rows = self.tables.pop()
            self.cell_stack.pop()
            md = render_table(rows)
            if self.tables and self.cell_stack and self.cell_stack[-1] is not None:
                self.cell_stack[-1].parts.append(" " + re.sub(r"\s*\n\s*", " ; ", md) + " ")
            elif md:
                self.out.append(md)
        elif tag in ("td", "th"):
            self._close_cell()
        elif tag in HEAD and self.head_level == tag:
            self._flush()
            self.head_level = None
        elif (tag in BLOCK or tag == "p") and not self.tables:
            self._flush()

    def handle_data(self, data: str) -> None:
        if self.hidden or not data:
            return
        data = ZW_RE.sub("", data.replace("\xa0", " "))
        if not data:
            return
        self._emit_text(re.sub(r"\s+", " ", data))

    def result(self) -> str:
        self._flush()
        lines = []
        for blk in self.out:
            if blk.strip().lower() in ("table of contents", "[table of contents]", "index"):
                continue
            lines.append(blk)
        text = "\n\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip() + "\n"


def _cell_text(c: _Cell) -> str:
    return re.sub(r"\s+", " ", "".join(c.parts)).strip().replace("|", "\\|")


def render_table(rows: list[list[_Cell]]) -> str:
    grid: list[list[str]] = []
    spans: list[list[tuple[int, int]]] = []  # 每列的 (起始欄, 跨幾欄)，只記 colspan > 1 的格
    for r in rows:
        cells: list[str] = []
        sp: list[tuple[int, int]] = []
        for c in r:
            t = _cell_text(c)
            if c.span > 1:
                sp.append((len(cells), c.span))
            cells.append(t)
            cells.extend([""] * (c.span - 1))  # colspan 展開，維持欄位對齊
        spans.append(sp)
        # 合併 "$" → 下一格、")"/"%" → 上一格
        merged = list(cells)
        for i, t in enumerate(merged):
            if t and JOIN_NEXT.match(t):
                j = next((k for k in range(i + 1, len(merged)) if merged[k]), None)
                if j is not None and not JOIN_NEXT.match(merged[j]):
                    merged[j] = (t + merged[j]) if t.endswith("(") else (t + " " + merged[j]).replace("$ ", "$")
                    merged[i] = ""
            elif t and JOIN_PREV.match(t):
                j = next((k for k in range(i - 1, -1, -1) if merged[k]), None)
                if j is not None:
                    merged[j] = merged[j] + t
                    merged[i] = ""
        grid.append(merged)
    if not grid:
        return ""
    width = max(len(r) for r in grid)
    for r in grid:
        r.extend([""] * (width - len(r)))
    # 跨欄表頭（如「2026」跨 $ 欄 + 數字欄）：文字落在沒有資料的欄 → 移到跨距內第一個有資料的欄，避免錯位
    spanned = {(i, k) for i, sp in enumerate(spans) for s, n in sp for k in range(s, s + n)}
    data_cols = {j for i, r in enumerate(grid) for j, t in enumerate(r) if t and (i, j) not in spanned}
    for i, sp in enumerate(spans):
        for s, n in sp:
            if grid[i][s] and s not in data_cols:
                tgt = next((k for k in range(s, min(s + n, width)) if k in data_cols and not grid[i][k]), None)
                if tgt is not None:
                    grid[i][tgt], grid[i][s] = grid[i][s], ""
    grid = [r for r in grid if any(c for c in r)]
    if not grid:
        return ""
    keep = [j for j in range(width) if any(r[j] for r in grid)]
    grid = [[r[j] for j in keep] for r in grid]
    if not keep:
        return ""
    if len(keep) == 1 or len(grid) == 1 and sum(1 for c in grid[0] if c) <= 2:
        # 排版用表格（單欄、或只有一列一兩格，如頁首、勾選框說明）→ 段落
        return "\n\n".join(" ".join(c for c in r if c) for r in grid)
    out = ["| " + " | ".join(grid[0]) + " |", "|" + " --- |" * len(keep)]
    out += ["| " + " | ".join(r) + " |" for r in grid[1:]]
    return "\n".join(out)


def _decode(raw: bytes) -> str:
    head = raw[:2048].decode("ascii", "ignore")
    m = re.search(r"""(?:charset|encoding)\s*=\s*["']?([\w-]+)""", head, re.I)
    for enc in ([m.group(1)] if m else []) + ["utf-8", "cp1252"]:
        try:
            return raw.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("utf-8", "replace")


def convert(src: Path, dst: Path) -> tuple[int, int]:
    """回傳 (輸入 bytes, 輸出 bytes)。原子寫入。"""
    raw = src.read_bytes()
    text = _decode(raw)
    # EDGAR 完整提交檔（.txt）裡的 <DOCUMENT> 包裝：只取第一份 HTML
    m = re.search(r"(?is)<html.*?</html>", text)
    if m and text.lstrip().startswith("<SEC-DOCUMENT>"):
        text = m.group(0)
    p = H2M()
    p.feed(text)
    p.close()
    md = p.result()
    tmp = dst.with_suffix(dst.suffix + ".part")
    tmp.write_text(md, encoding="utf-8")
    tmp.replace(dst)
    return len(raw), dst.stat().st_size


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "--tasks":
        data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        tasks = [t for t in data.get("pending", []) if t.get("type") == "html"]
        bad = 0
        for t in tasks:
            try:
                a, b = convert(Path(t["src"]), Path(t["md"]))
                print(f"OK   {Path(t['md']).name}  {a / 1024:.0f} KB → {b / 1024:.0f} KB")
            except Exception as e:  # noqa: BLE001 — 單檔失敗記錄後繼續（Convert2md 規則 5）
                bad += 1
                print(f"FAIL {Path(t['src']).name}：{type(e).__name__}: {e}")
        print(f"[html2md] {len(tasks) - bad}/{len(tasks)} 成功")
        return 1 if bad else 0
    if len(argv) == 2:
        a, b = convert(Path(argv[0]), Path(argv[1]))
        print(f"[html2md] {argv[0]} → {argv[1]}（{a / 1024:.0f} KB → {b / 1024:.0f} KB）")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
