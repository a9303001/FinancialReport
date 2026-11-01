#!/usr/bin/env python3
"""MdClean — 公司資料夾 .md 機械清理器（規則見 gemini/MdClean.md）。

目標：把 PDF / SEC HTML 轉出的 Markdown 清成「AI 好解析」的格式，直接覆寫原檔。
不以縮小檔案為目的；只移除 0 資訊量的雜訊、修復被拆碎的結構，並加上 AI 導讀註記。

安全閘門（每檔必過，否則不覆寫、記 FAIL）：
    原檔所有數字 token（全形轉半形後）− 刻意移除的數字（頁碼、圖片路徑、cid 亂碼）
    必須與清理後的數字 token「完全相同」（多重集合比對）；文字字元保留率 ≥ 98%。

用法（在 REPO_ROOT 執行；Windows 用 python，Linux 用 python3）：
    python gemini/MdClean.py --list                 # 只列狀態，不改檔
    python gemini/MdClean.py                        # 跑下一批（預設 20 檔 / 25 MB）並更新 summary
    python gemini/MdClean.py --dry-run              # 試跑下一批：只驗證、不覆寫、不改 summary
    python gemini/MdClean.py --file "UHS/UHS_10K_2025-12-31.md"   # 指定檔（可重複）
    python gemini/MdClean.py --max-files 10 --max-mb 15
    python gemini/MdClean.py --file X --no-join     # 關閉斷行接合（FAIL 重試用）
    python gemini/MdClean.py --file X --force       # 已清理過也重跑（規則升版時用）

狀態判定（冪等）：
    檔案第一行 = <!-- MdClean:vN | sha1:xxxxxxxxxxxx | ... -->，且 sha1(第二行起內容) 相符 → CLEAN（跳過）
    有標記但 sha1 不符（清理後又被修改／被 append）→ MODIFIED（重新排入待處理）
    無標記 → NEW（待處理）
輸出最後一行 "MdClean done: OK=a FAIL=b SKIP=c"；有 FAIL 時 exit code = 1。
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import re
import sys
from pathlib import Path

VERSION = 'v1'
ROOT = Path(__file__).resolve().parent.parent
SUMMARY = ROOT / 'gemini' / 'MdClean_symmary.md'

SKIP_DIRS = {'.git', '.github', '.claude', '.agents', '.vscode', '.idea', 'Log', 'Prompt',
             'History', 'gemini', 'StkScreenerResult', 'HkReitScreenerResult',
             'JpReitScreenerResult', 'node_modules', '__pycache__'}
SKIP_FILES = {'hourAnalysisResult.md'.lower()}

# 檔名 → light 模式（AI 產出的筆記／輿情／分析：只做無損空白與雜訊清理，不動結構）
LIGHT_NAME_RE = re.compile(
    r'(PublicOpinion|輿情|討論|新聞|news|analysis|report_summary|Official_IR|_IR\b|IR\.md$|'
    r'Reddit|Twitter|Xueqiu|SeekingAlpha|GoogleNews|PTT|Dcard|Mobile01|^\d{12}\.md$)',
    re.I)

MARK_RE = re.compile(r'^<!-- MdClean:(v\d+) \| sha1:([0-9a-f]{12}) \|.*-->\s*$')
META_START = '<!-- AI-META'
FENCE_RE = re.compile(r'^\s*(```|~~~)')
NUM_RE = re.compile(r'\d+(?:[.,]\d+)*')
LETTER_RE = re.compile(r'[A-Za-z぀-ヿ㐀-鿿가-힯]')
COMMENT_RE = re.compile(r'<!--.*?-->', re.S)
CJK = r'぀-ヿ㐀-鿿가-힯'

CTRL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f​-‍⁠﻿­]')
IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)]*)\)')
PIC_RE = re.compile(r'<!--\s*Start of picture text\s*-->(.*?)<!--\s*End of picture text\s*-->', re.S)
BR_RE = re.compile(r'<br\s*/?>', re.I)
CID_RE = re.compile(r'\(cid:\d+\)')
TAG_RE = re.compile(r'</?(?:br|sup|sub|span|font|b|i|u|em|strong|p|div)\b[^>]{0,80}>', re.I)

CURRENCY = {'$', 'NT$', 'US$', 'HK$', 'S$', 'A$', 'C$', 'RMB', 'HKD', 'USD', 'NTD', 'JPY',
            '¥', '￥', '€', '£', 'Rp', 'IDR', '元'}
SUFFIX = {')', '%', ')%', '%)', '）', 'pts', 'bps', 'x', '倍'}
NUMERIC_CELL = re.compile(r'^\(?[-−–]?[\d,]+(?:\.\d+)?\)?%?$')
SEP_CELL = re.compile(r'^:?-{3,}:?$')


# ---------------------------------------------------------------------------
# 掃描與狀態
# ---------------------------------------------------------------------------

def sha12(text: str) -> str:
    return hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]


def read_text(path: Path) -> tuple[str, bool]:
    raw = path.read_bytes()
    try:
        return raw.decode('utf-8-sig'), True
    except UnicodeDecodeError:
        return raw.decode('utf-8', errors='replace'), False


def company_dirs() -> list[Path]:
    return sorted(p for p in ROOT.iterdir()
                  if p.is_dir() and p.name not in SKIP_DIRS and not p.name.startswith('.'))


def eligible_files() -> list[Path]:
    out = []
    for d in company_dirs():
        for f in sorted(d.rglob('*.md')):
            if f.name.lower() in SKIP_FILES or f.name.endswith('.tmp'):
                continue
            if any(part in SKIP_DIRS for part in f.relative_to(ROOT).parts[:-1]):
                continue
            out.append(f)
    return out


def file_state(path: Path) -> str:
    text, _ = read_text(path)
    first, _, rest = text.partition('\n')
    m = MARK_RE.match(first)
    if not m:
        return 'NEW'
    if m.group(2) != sha12(rest):
        return 'MODIFIED'
    if m.group(1) != VERSION:
        return 'OLD_VERSION'
    return 'CLEAN'


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


# ---------------------------------------------------------------------------
# 清理規則
# ---------------------------------------------------------------------------

class Stats(collections.Counter):
    pass


def fw_to_ascii(text: str) -> str:
    """全形英數字／％／空白 → 半形（標點不動，避免改變中日文語氣）。"""
    def conv(ch: str) -> str:
        o = ord(ch)
        if 0xFF10 <= o <= 0xFF19 or 0xFF21 <= o <= 0xFF3A or 0xFF41 <= o <= 0xFF5A or o == 0xFF05:
            return chr(o - 0xFEE0)
        return ch
    return ''.join(conv(c) for c in text) if re.search('[％０-ｚ]', text) else text


def strip_old_meta(text: str) -> str:
    lines = text.split('\n')
    if lines and MARK_RE.match(lines[0]):
        lines = lines[1:]
    if lines and lines[0].startswith(META_START):
        for i, ln in enumerate(lines):
            if ln.rstrip().endswith('-->'):
                lines = lines[i + 1:]
                break
    while lines and not lines[0].strip():
        lines = lines[1:]
    return '\n'.join(lines)


def base_normalize(text: str, st: Stats, removed: list[str]) -> str:
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    n = len(CTRL_RE.findall(text))
    if n:
        st['control_chars_removed'] += n
        text = CTRL_RE.sub('', text)
    text = text.replace(' ', ' ').replace('　', ' ')
    # 失效圖片（本機暫存路徑、AI 無法讀取）→ 留 alt 文字
    def img(m: re.Match) -> str:
        st['image_links_removed'] += 1
        removed.append(m.group(2))
        alt = m.group(1).strip()
        if alt:
            return f'[image: {alt}]'
        removed.append(alt)
        return ''
    text = IMG_RE.sub(img, text)
    # cid 字型亂碼：整行多數為 (cid:n) → 換成一行說明
    out, run = [], 0
    for ln in text.split('\n'):
        cids = CID_RE.findall(ln)
        if cids and len(''.join(cids)) >= 0.5 * len(ln.strip()):
            removed.append(ln)
            run += 1
            continue
        if run:
            out.append(f'<!-- [MdClean] 此處 {run} 行為 PDF 字型編碼亂碼 (cid:n)，已移除；需要原文請查原始 PDF -->')
            st['cid_lines_removed'] += run
            run = 0
        out.append(ln)
    if run:
        out.append(f'<!-- [MdClean] 此處 {run} 行為 PDF 字型編碼亂碼 (cid:n)，已移除；需要原文請查原始 PDF -->')
        st['cid_lines_removed'] += run
    return '\n'.join(out)


def picture_text(text: str, st: Stats, removed: list[str]) -> str:
    def rep(m: re.Match) -> str:
        st['picture_text_blocks'] += 1
        inner = BR_RE.sub('\n', m.group(1))
        parts = [p.strip() for p in inner.split('\n') if p.strip()]
        if not parts:
            return ''
        if len(parts) == 1 and re.fullmatch(r'\d{1,4}', parts[0].strip('*')):
            removed.append(parts[0])
            st['page_markers'] += 1
            return f'\n<!-- p.{int(parts[0].strip("*"))} -->\n'
        return '\n[picture-text] ' + ' / '.join(parts) + '\n'
    return PIC_RE.sub(rep, text)


# ---- 表格 -----------------------------------------------------------------

def split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|') and not s.endswith('\\|'):
        s = s[:-1]
    return [c.strip() for c in re.split(r'(?<!\\)\|', s)]


def clean_cell(c: str) -> str:
    c = BR_RE.sub(' ', c)
    c = c.replace('`', '').replace('**', '').replace('__', '')
    c = re.sub(r'\s+', ' ', c).strip()
    if re.fullmatch(rf'[{CJK}](?: +[{CJK}]){{1,6}}', c):     # 「資  產」→「資產」
        c = c.replace(' ', '')
    return c


def merge_cells(cells: list[str]) -> list[str]:
    """SEC 表格把「$」「)」「%」拆成獨立儲存格 → 併回相鄰（緊鄰、無空格）的數字儲存格。"""
    cells = cells[:]
    n = len(cells)
    for i in range(n - 1):
        nxt = cells[i + 1]
        if cells[i] in CURRENCY and (NUMERIC_CELL.match(nxt) or nxt in {'-', '–', '—', '−'}):
            if cells[i] == '元':
                cells[i + 1] = f'{nxt} 元'
            else:
                cells[i + 1] = f'{cells[i]}{" " if cells[i][-1].isalpha() else ""}{nxt}'
            cells[i] = ''
    for i in range(1, n):
        prev = cells[i - 1]
        if cells[i] in SUFFIX and re.search(r'[\d)]$', prev) and not (
                cells[i].startswith('%') and re.fullmatch(r'(?:19|20)\d{2}', prev)):
            cells[i - 1] = prev + cells[i]
            cells[i] = ''
    return cells


VALUE_CELL = re.compile(r'^(?:[A-Z]{0,3}\$|RMB|HK\$|¥|￥|€|£)?\s?\(?[-−–]?[\d,]*\d(?:\.\d+)?\)?%?$')
YEAR_CELL = re.compile(r'^(?:19|20)\d{2}$')


def align_header_cols(frag: list[list[str]], st: Stats) -> list[list[str]]:
    """SEC 表頭（2025、Amount）常落在數值欄左邊一格：
    「只在表頭列有值」的欄 + 右側緊鄰「只在數值列有值」的欄，且逐列互補 → 合併成一欄。"""
    if not frag or len(frag[0]) < 3:
        return frag
    is_data = [any(VALUE_CELL.match(c) and not YEAR_CELL.match(c) for c in r[1:]) for r in frag]
    if not any(is_data) or all(is_data):
        return frag
    width = len(frag[0])
    def only(j: int, data: bool) -> bool:
        cells = [r[j] for r, d in zip(frag, is_data) if r[j]]
        return bool(cells) and all(d == data for r, d in zip(frag, is_data) if r[j])
    j, merged = 1, 0
    while j < width - 1:
        if only(j, False) and only(j + 1, True) and all(not (r[j] and r[j + 1]) for r in frag):
            for r in frag:
                r[j + 1] = r[j] or r[j + 1]
                r[j] = ''
            merged += 1
            j += 2
        else:
            j += 1
    st['header_cols_aligned'] += merged
    return frag


def drop_empty_cols(frag: list[list[str]], st: Stats) -> list[list[str]]:
    width = max(len(r) for r in frag)
    frag = [r + [''] * (width - len(r)) for r in frag]
    keep = [j for j in range(width) if any(r[j] for r in frag)]
    st['empty_cols_removed'] += width - len(keep)
    return [[r[j] for j in keep] for r in frag]


def render_table(rows: list[list[str]]) -> list[str]:
    width = max(len(r) for r in rows)
    rows = [r + [''] * (width - len(r)) for r in rows]
    out = ['| ' + ' | '.join(rows[0]) + ' |', '|' + '|'.join([' --- '] * width) + '|']
    out += ['| ' + ' | '.join(r) + ' |' for r in rows[1:]]
    return out


def process_table_block(lines: list[str], st: Stats) -> list[str]:
    st['tables_seen'] += 1
    frags: list[list[list[str]]] = [[]]
    for ln in lines:
        cells = split_row(ln)
        if all(SEP_CELL.match(c) or c == '' for c in cells) and any(SEP_CELL.match(c) for c in cells):
            st['separator_rows_removed'] += 1
            if frags[-1]:                       # pymupdf 碎片：分隔線前一列其實是資料列 → 新碎片起點
                head = frags[-1].pop()
                frags.append([head])
            continue
        frags[-1].append([clean_cell(c) for c in cells])
    groups: list[list[list[str]]] = []
    for frag in frags:
        before = len(frag)
        frag = [r for r in frag if any(r)]
        st['empty_rows_removed'] += before - len(frag)
        if not frag:
            continue
        for _ in range(8):                      # 合併 → 對齊 → 刪空欄，反覆到不再變化（確保冪等）
            prev = [r[:] for r in drop_empty_cols(frag, st)]
            frag = drop_empty_cols(align_header_cols([merge_cells(r) for r in prev], st), st)
            if frag == prev:
                break
        if groups and len(groups[-1][0]) == len(frag[0]):
            groups[-1].extend(frag)
        else:
            groups.append(frag)
    out: list[str] = []
    for g in groups:
        out.append('')
        if len(g[0]) == 1:                      # 單欄表格 = 純文字
            out += [r[0] for r in g]
            st['single_col_tables_to_text'] += 1
        else:
            out += render_table(g)
        out.append('')
    return out


# ---- 頁碼／頁首頁尾 ----------------------------------------------------------

def is_table(ln: str) -> bool:
    return ln.lstrip().startswith('|')


def plain_key(ln: str) -> str:
    if ln.lstrip().startswith('<!--'):
        return ''
    s = re.sub(r'^#{1,6}\s+', '', ln.strip())
    return re.sub(r'\s+', ' ', s.replace('**', '').replace('__', '').replace('`', '')).strip()


def detect_pages(lines: list[str], fence: list[bool], st: Stats, removed: list[str]) -> list[str]:
    n = len(lines)
    page_at: dict[int, int | None] = {}     # 行號 → 頁碼（None = 純刪除）
    drop: set[int] = set()

    def next_nonblank(i: int) -> int:
        j = i + 1
        while j < n and not lines[j].strip():
            j += 1
        return j

    frac = re.compile(r'^\s*(\d{1,4})\s*/\s*(\d{1,4})\s*$')
    dens = collections.Counter(m.group(2) for ln in lines if (m := frac.match(ln)))
    for i, ln in enumerate(lines):
        if fence[i] or is_table(ln):
            continue
        s = plain_key(ln)
        if m := re.fullmatch(r'-\s*(\d{1,4})\s*-', s):
            page_at[i] = int(m.group(1))
        elif (m := frac.match(s)) and dens[m.group(2)] >= 3:
            page_at[i] = int(m.group(1))
        elif m := re.fullmatch(r'(?:Page|頁)\s*(\d{1,4})(?:\s*of\s*\d{1,4})?|第\s*(\d{1,4})\s*頁', s, re.I):
            page_at[i] = int(m.group(1) or m.group(2))
        elif re.fullmatch(r'\d{1,4}|[ivxlc]{1,6}', s):
            j = next_nonblank(i)
            if j < n and lines[j].strip() in {'---', '***', '___'}:
                page_at[i] = int(s) if s.isdigit() else None
                drop.add(j)

    # 帶頁碼的頁首頁尾：同一模板（數字→#）重複 ≥5 次，且恰好一個數字位置遞增
    groups: dict[str, list[int]] = collections.defaultdict(list)
    for i, ln in enumerate(lines):
        if fence[i] or is_table(ln) or i in page_at:
            continue
        s = plain_key(ln)
        if 0 < len(s) <= 90 and LETTER_RE.search(s) and re.search(r'\d', s):
            groups[re.sub(r'\d+', '#', s)].append(i)
    const_keys: dict[str, list[int]] = {}
    for key, idx in groups.items():
        if len(idx) < 5:
            continue
        nums = [re.findall(r'\d+', plain_key(lines[i])) for i in idx]
        if len({len(x) for x in nums}) != 1:
            continue
        varying = [p for p in range(len(nums[0])) if len({x[p] for x in nums}) > 1]
        if not varying:
            const_keys[key] = idx
            continue
        if len(varying) != 1:
            continue
        vals = [int(x[varying[0]]) for x in nums]
        steps = [b - a for a, b in zip(vals, vals[1:])]
        good = sum(1 for d in steps if 1 <= d <= 6)
        if max(vals) <= 3000 and steps and good >= 0.7 * len(steps):
            for i, v in zip(idx, vals):
                page_at[i] = v

    # 無頁碼的固定頁首頁尾：重複 ≥5 次、≥60% 出現在頁碼 4 行內 → 保留第一次，其餘刪除
    marks = sorted(page_at)
    def near_mark(i: int) -> bool:
        import bisect
        k = bisect.bisect_left(marks, i)
        for j in (k - 1, k):
            if 0 <= j < len(marks):
                a, b = sorted((i, marks[j]))
                if sum(1 for t in range(a, b) if lines[t].strip()) <= 4:
                    return True
        return False
    if marks:
        counts: dict[str, list[int]] = collections.defaultdict(list)
        for i, ln in enumerate(lines):
            if fence[i] or is_table(ln) or i in page_at:
                continue
            s = plain_key(ln)
            if 0 < len(s) <= 70 and not s.startswith('<!--'):
                counts[s].append(i)
        for key, idx in list(counts.items()) + [(k, v) for k, v in const_keys.items()]:
            if len(idx) < 5:
                continue
            near = [i for i in idx if near_mark(i)]
            if len(near) >= 0.6 * len(idx):
                for i in idx[1:]:
                    drop.add(i)

    out = []
    for i, ln in enumerate(lines):
        if i in page_at:
            removed.append(ln)
            v = page_at[i]
            st['page_markers'] += 1
            if v is not None:
                out.append(f'<!-- p.{v} -->')
            continue
        if i in drop:
            removed.append(ln)
            st['running_header_lines_removed'] += 1
            continue
        out.append(ln)
    return out


# ---- 標題提升、斷行接合 ------------------------------------------------------

HEADING_RULES = [
    (re.compile(r'^PART\s+[IVX]+\b\.?(?:\s*[-–—:]?\s*[A-Z][A-Za-z ,&\-]{0,60})?$'), '##'),
    (re.compile(r'^(?:Item|ITEM)\s+\d{1,2}[A-Ca-c]?\.\s+[A-Z][^|]{2,110}$'), '###'),
    (re.compile(r'^第[0-9一二三四五六七八九十]+部\s*【[^】]{1,40}】$'), '##'),
    (re.compile(r'^第[0-9一二三四五六七八九十]+\s*【[^】]{1,40}】$'), '###'),
    (re.compile(r'^[0-9]{1,2}\s*【[^】]{1,40}】$'), '####'),
    (re.compile(r'^[(（][0-9]{1,2}[)）]\s*【[^】]{1,40}】$'), '#####'),
    (re.compile(r'^[①-⑳]\s*【[^】]{1,40}】$'), '######'),
    (re.compile(r'^[壹貳參肆伍陸柒捌玖拾]{1,3}、\s*\S.{0,28}$'), '##'),
]
LIST_RE = re.compile(r'^\s*(?:[-*+•●○■□◆◇▪]\s|\d{1,3}[.)、]\s|[(（][0-9a-zA-Z一二三四五六七八九十]{1,3}[)）]|[①-⑳]|[a-z][.)]\s)')
END_PUNCT = re.compile(r'[.:;!?。：；！？」』）)\]】]$')


def promote_headings(lines: list[str], fence: list[bool], st: Stats) -> list[str]:
    out = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not fence[i] and s and not s.startswith(('#', '|', '<!--')) and len(s) <= 120:
            for rx, h in HEADING_RULES:
                if rx.match(s):
                    ln = f'{h} {s}'
                    st['headings_promoted'] += 1
                    break
        elif not fence[i] and s.startswith('#'):
            m = re.match(r'^(#{1,6})\s+(.*)$', s)
            if m and '**' in m.group(2):
                ln = f'{m.group(1)} {m.group(2).replace("**", "").strip()}'
        out.append(ln)
    return out


def joinable(ln: str) -> bool:
    s = ln.strip()
    return bool(s) and not (s.startswith(('#', '|', '<!--', '>', '[picture-text]', '```', '~~~'))
                            or LIST_RE.match(s))


def join_lines(lines: list[str], fence: list[bool], st: Stats) -> list[str]:
    out: list[str] = []
    out_fence: list[bool] = []
    for i, ln in enumerate(lines):
        if out and not fence[i] and not out_fence[-1] and joinable(ln) and joinable(out[-1]):
            prev = out[-1].rstrip()
            cur = ln.strip()
            latin = (len(prev) >= 50 and not END_PUNCT.search(prev) and re.match(r'[a-z(]', cur)
                     and re.search(r'[A-Za-z,\-]$', prev))
            cjk = (len(prev) >= 28 and re.search(rf'[{CJK}，、]$', prev) and re.match(rf'[{CJK}]', cur))
            if latin or cjk:
                glue = '' if (cjk or prev.endswith('-')) else ' '
                out[-1] = prev + glue + cur
                st['wrapped_lines_joined'] += 1
                continue
        out.append(ln)
        out_fence.append(fence[i])
    return out


def letter_spaced(lines: list[str], fence: list[bool]) -> list[str]:
    rx = re.compile(rf'^(#{{0,6}}\s*)([{CJK}](?: +[{CJK}]){{1,6}})\s*$')
    return [(m.group(1) + m.group(2).replace(' ', '')) if (not f and (m := rx.match(ln))) else ln
            for ln, f in zip(lines, fence)]


# ---- 主流程 ------------------------------------------------------------------

def fence_flags(lines: list[str]) -> list[bool]:
    flags, inside = [], False
    for ln in lines:
        if FENCE_RE.match(ln):
            flags.append(True)
            inside = not inside
        else:
            flags.append(inside)
    return flags


def table_pass(lines: list[str], st: Stats) -> list[str]:
    fence = fence_flags(lines)
    out, block = [], []
    for ln, f in zip(lines, fence):
        if not f and is_table(ln):
            block.append(ln)
            continue
        if block:
            out += process_table_block(block, st)
            block = []
        out.append(ln)
    if block:
        out += process_table_block(block, st)
    return out


def tidy_whitespace(lines: list[str], light: bool) -> list[str]:
    fence = fence_flags(lines)
    out: list[str] = []
    for i, ln in enumerate(lines):
        if fence[i]:
            out.append(ln)
            continue
        ln = ln.rstrip()
        if not light:
            ln = re.sub(r'(?<=\S) {2,}', ' ', ln) if not is_table(ln) else ln
        if not ln.strip():
            if out and not out[-1].strip():
                continue
            out.append('')
            continue
        # 表格前後、標題前要有空行，避免 GFM 把下一行吞進表格
        if out and out[-1].strip():
            if (is_table(ln) != is_table(out[-1])) or (not light and ln.startswith('#')):
                out.append('')
        out.append(ln)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


UNIT_RE = re.compile(
    r'(\((?:[Dd]ollar amounts |[Aa]mounts )?in (?:thousands|millions|billions)[^)]{0,60}\)|'
    r'\(Expressed in [^)]{1,40}\)|In (?:Thousands|Millions) of [A-Z][A-Za-z ]{2,30}|'
    r'[（(]單位[：:][^）)]{1,30}[）)]|單位[：:]\s?[^\s|，,]{1,20}|'
    r'[（(]単位[：:][^）)]{1,20}[）)]|\((?:千円|百万円|千元|百萬元|人民幣千元|RMB.?000|RMB million|HK\$.?000)\)|'
    r'RMB.?000|RMB [Mm]illion|HK\$.?000|NT\$ ?thousand)')


def doc_type(name: str) -> str:
    n = name.lower()
    rules = [('10k', 'annual_report (SEC 10-K)'), ('10-k', 'annual_report (SEC 10-K)'),
             ('10q', 'quarterly_report (SEC 10-Q)'), ('10-q', 'quarterly_report (SEC 10-Q)'),
             ('20-f', 'annual_report (SEC 20-F)'), ('publicopinion', 'public_opinion (輿情彙整)'),
             ('輿情', 'public_opinion (輿情)'), ('analysis', 'analysis_note (AI 分析)'),
             ('_ir', 'company_ir_news (公司 IR／公告摘要)'), ('有価証券報告書', 'annual_report (日本 有価証券報告書)'),
             ('四半期', 'quarterly_report (日本 四半期報告書)'), ('半期', 'interim_report (日本 半期報告書)'),
             ('interim', 'interim_report (半年報)'), ('quarter', 'quarterly_report (季報)'),
             ('annual', 'annual_report (年報)'), ('f04', 'annual_report (台灣 股東會年報)'),
             ('fe4', 'annual_report (台灣 股東會年報 英文版)'),
             ('aia', 'financial_statements (台灣 年度合併財報)'), ('aic', 'financial_statements (台灣 年度個體財報)'),
             ('ai1', 'financial_statements (台灣 第一季合併財報)'), ('ai2', 'financial_statements (台灣 半年度合併財報)'),
             ('ai3', 'financial_statements (台灣 第三季合併財報)')]
    for k, v in rules:
        if k in n:
            return v
    return 'unknown (請由內容判斷)'


def source_format(text: str) -> str:
    head = text[:5000]
    if 'SECURITIES AND EXCHANGE COMMISSION' in head:
        return 'sec_html (SEC EDGAR HTML 轉 md)'
    if 'EDINET' in head:
        return 'pdf_text (EDINET PDF 轉 md)'
    if 'Start of picture text' in text or '<br>' in text:
        return 'pdf_text (pymupdf4llm 新版轉 md)'
    if text.count('| --- |') > 20 or re.search(r'\n- \d+ -\n', text):
        return 'pdf_text (PDF 轉 md)'
    return 'markdown (AI／人工撰寫)'


def build_meta(path: Path, original: str, light: bool, st: Stats, units: list[str], fmt: str) -> str:
    period = sorted(set(re.findall(r'(20\d{2}(?:Q[1-4]|[-_]?\d{2}[-_]?\d{2})?)', path.name)))[:3]
    done = ', '.join(f'{k}={v}' for k, v in sorted(st.items()) if v) or 'none'
    lines = [
        META_START,
        f'company_folder: {path.parent.name}',
        f'file: {path.name}',
        f'doc_type_guess: {doc_type(path.name)}',
        f'period_hint_from_filename: {", ".join(period) or "unknown"}',
        f'source_format: {fmt}',
        f'clean_mode: {"light (AI 筆記；內容未改寫，只清空白與失效連結)" if light else "report (財報類；已重整表格與頁碼)"}',
    ]
    if not light:
        lines += [
            f'unit_hints: {" ; ".join(units) if units else "未偵測到；請以各表標題/表頭為準"}',
            'page_markers: "<!-- p.N -->" = 原始文件印刷頁碼 N 出現的位置（頁首或頁尾），引用頁數時用它',
            'number_conventions: (1,234) = 負數；表格內單獨的 "-" / "–" / "−" = 零或無；% 已併回數字',
            'tables: 已刪空白欄/空白列與重複分隔列；表格第一列為表頭（PDF 碎表的表頭可能其實是資料列）',
            'tables_as_text: PDF 轉檔時部分表格列被輸出成「項目 數字 數字」的純文字行，數字依序對應上方表頭的期間欄',
        ]
    lines += [f'cleanup_applied: {done}', '-->']
    return '\n'.join(lines)


def visible(text: str) -> str:
    """驗證用：去掉 HTML 註解與 <br> 標籤（標籤字母不算內容）。"""
    return TAG_RE.sub(' ', COMMENT_RE.sub(' ', text)).replace('`', '')


def count_nums(text: str) -> collections.Counter:
    return collections.Counter(NUM_RE.findall(visible(text)))


def count_letters(text: str) -> int:
    return len(LETTER_RE.findall(visible(text)))


def clean_text(path: Path, text: str, light: bool, no_join: bool) -> tuple[str, Stats, str | None]:
    st = Stats()
    removed: list[str] = []
    original = strip_old_meta(text)
    work = original if light else fw_to_ascii(original)
    baseline = work
    work = base_normalize(work, st, removed)
    if not light:
        work = picture_text(work, st, removed)
        work = TAG_RE.sub(' ', work) if '<' in work else work
    lines = work.split('\n')
    if not light:
        lines = table_pass(lines, st)
        lines = detect_pages(lines, fence_flags(lines), st, removed)
        lines = promote_headings(lines, fence_flags(lines), st)
        lines = letter_spaced(lines, fence_flags(lines))
        if not no_join:
            lines = join_lines(lines, fence_flags(lines), st)
    lines = tidy_whitespace(lines, light)
    body = '\n'.join(lines) + '\n'

    # ---- 安全閘門 ----
    expect = count_nums(baseline)
    for r in removed:
        expect.subtract(NUM_RE.findall(visible(r)))
    expect = +expect
    got = count_nums(body)
    if expect != got:
        miss = (expect - got).most_common(5)
        extra = (got - expect).most_common(5)
        return '', st, f'數字 token 不一致：遺失 {miss}｜多出 {extra}'
    base_letters = count_letters(baseline) - sum(count_letters(r) for r in removed)
    got_letters = count_letters(body)
    if base_letters > 0 and got_letters < 0.98 * base_letters:
        return '', st, f'文字字元保留率 {got_letters / base_letters:.1%} < 98%'

    units = []
    for m in UNIT_RE.finditer(body):
        u = m.group(0).strip()
        if u not in units:
            units.append(u)
        if len(units) >= 4:
            break
    meta = build_meta(path, original, light, st, units, source_format(original))
    rest = meta + '\n\n' + body
    mark = f'<!-- MdClean:{VERSION} | sha1:{sha12(rest)} | cleaned:{dt.date.today().isoformat()} | mode:{"light" if light else "report"} -->'
    return mark + '\n' + rest, st, None


def is_light(path: Path) -> bool:
    return bool(LIGHT_NAME_RE.search(path.name))


def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(content, encoding='utf-8', newline='\n')
    if tmp.stat().st_size == 0:
        tmp.unlink()
        raise IOError('暫存檔為空')
    tmp.replace(path)


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def keep_block(text: str, name: str) -> str:
    m = re.search(rf'<!-- {name}:start -->\n(.*?)<!-- {name}:end -->', text, re.S)
    return m.group(1) if m else ''


def pick_batch(pending: list[Path], max_files: int, max_mb: float) -> list[Path]:
    batch, size = [], 0
    for f in pending:
        s = f.stat().st_size
        if batch and (len(batch) >= max_files or size + s > max_mb * 1024 * 1024):
            break
        batch.append(f)
        size += s
    return batch


def write_summary(results: list[dict], states: dict[Path, str], next_batch: list[Path],
                  args: argparse.Namespace, started: dt.datetime) -> None:
    old = SUMMARY.read_text(encoding='utf-8') if SUMMARY.exists() else ''
    history = keep_block(old, 'history')
    ai_notes = keep_block(old, 'ai-notes') or (
        '- （下一輪 AI 抽查後把觀察寫在這裡：哪類檔案還有殘留雜訊、建議新增的規則、需人工處理的檔案。腳本會原樣保留本區塊。）\n')
    failed_old = keep_block(old, 'fail-list')
    total = len(states)
    cnt = collections.Counter(states.values())
    ok = [r for r in results if r['status'] == 'OK']
    fail = [r for r in results if r['status'] == 'FAIL']
    now = dt.datetime.now()
    hist_line = (f'- {now:%Y-%m-%d %H:%M}｜{VERSION}｜本輪 OK {len(ok)}｜FAIL {len(fail)}｜'
                 f'累計 CLEAN {cnt["CLEAN"]}/{total}｜待處理 {total - cnt["CLEAN"]}\n')
    history = hist_line + history
    history = ''.join(history.splitlines(True)[:30])

    fail_map: dict[str, str] = {}
    for ln in failed_old.splitlines():
        m = re.match(r'^- `([^`]+)`｜(.*)$', ln)
        if m and states.get(ROOT / m.group(1)) not in (None, 'CLEAN'):
            fail_map[m.group(1)] = m.group(2)
    for r in results:
        if r['status'] == 'FAIL':
            fail_map[r['file']] = r['reason']
        else:
            fail_map.pop(r['file'], None)

    def kb(n: int) -> str:
        return f'{n / 1024:,.0f} KB'

    L = [
        '# MdClean 執行摘要（給下一輪 AI 讀）',
        '',
        f'- **最後執行時間**：{now:%Y-%m-%d %H:%M:%S}（耗時 {(now - started).total_seconds():.1f} 秒）',
        f'- **腳本版本**：`gemini/MdClean.py` {VERSION}｜規則說明：`gemini/MdClean.md`',
        f'- **批次參數**：max_files={args.max_files}｜max_mb={args.max_mb}｜no_join={args.no_join}',
        f'- **整體進度**：共 {total} 個可清理 md｜CLEAN {cnt["CLEAN"]}｜NEW {cnt["NEW"]}｜MODIFIED {cnt["MODIFIED"]}｜OLD_VERSION {cnt["OLD_VERSION"]}｜FAIL 待處理 {len(fail_map)}',
        f'- **排除**：`hourAnalysisResult.md`、非公司資料夾（{", ".join(sorted(SKIP_DIRS - {".git", ".github", ".vscode", ".idea", "node_modules", "__pycache__"}))}）',
        '',
        '## 1. 下一輪要處理的 md 檔',
        '',
        '> 下一輪直接執行 `python gemini/MdClean.py` 即會依序處理下列檔案（腳本以檔頭標記自動判斷，不需手動指定）。',
        '> 若清單為空 = 全部完成；之後只有新檔或被修改的檔會再次出現。',
        '',
    ]
    L += [f'{i}. `{rel(f)}`｜{states[f]}｜{kb(f.stat().st_size)}｜{"light" if is_light(f) else "report"}'
          for i, f in enumerate(next_batch, 1)] or ['- （無：全部 md 都已是 CLEAN）']
    rest_n = total - cnt['CLEAN'] - len(next_batch)
    L += ['', f'- 下一輪之後尚餘：{max(rest_n, 0)} 檔', '']
    L += ['## 2. 本輪處理結果', '']
    if not results:
        L.append('- （本輪未處理任何檔案）')
    for r in results:
        if r['status'] == 'OK':
            L.append(f'- [OK] `{r["file"]}`｜{r["mode"]}｜{kb(r["before"])} → {kb(r["after"])}'
                     f'（{(r["after"] - r["before"]) / max(r["before"], 1):+.0%}）｜{r["detail"]}')
        else:
            L.append(f'- [FAIL] `{r["file"]}`｜{r["mode"]}｜未覆寫｜{r["reason"]}')
    L += ['', '## 3. FAIL 清單（未覆寫原檔，需下一輪 AI 處理）', '',
          '<!-- fail-list:start -->']
    L += [f'- `{k}`｜{v}' for k, v in sorted(fail_map.items())]
    L += ['<!-- fail-list:end -->', '',
          '- 處理方式：先 `python gemini/MdClean.py --file "<路徑>" --no-join --dry-run` 重試；仍失敗 → 依 `gemini/MdClean.md` Step 4 判斷，'
          '必要時把該檔加入 `MdClean.py` 的 `SKIP_FILES` 並在 ai-notes 註明原因。',
          '',
          '## 4. 下一輪 AI 必讀重點',
          '',
          '- 清理後檔案第一行是 `<!-- MdClean:v1 | sha1:… -->`，第二段是 `<!-- AI-META … -->` 導讀（公司、文件類型、單位、頁碼標記、數字慣例）。**不要手動修改這兩段**；改了內容後 sha1 不符會自動重排入待處理。',
          '- `*_PublicOpinion.md` 由 ArrangePublicOpinionMd 每次 append 並重寫檔頭 → MdClean 標記會消失，該檔自動回到待處理（正常現象）。`<!-- body:start -->`、`<!-- source-file: … -->` 一律原樣保留。',
          '- 安全閘門：數字 token 必須 100% 保留（頁碼、圖片路徑、cid 亂碼除外）；FAIL 的檔不會被覆寫。',
          '- 腳本是確定性規則；AI 不要整份重寫大檔。只允許：(a) 小檔（<100 KB）局部修正；(b) 把觀察寫進下方 ai-notes；(c) 修改 `MdClean.py` 規則並升版（VERSION → v2 後舊檔會變 OLD_VERSION 自動重跑）。',
          '',
          '## 5. AI 觀察與待辦（ai-notes，腳本會保留）',
          '',
          '<!-- ai-notes:start -->',
          ai_notes.rstrip('\n'),
          '<!-- ai-notes:end -->',
          '',
          '## 6. 歷次執行紀錄（最新在上，保留 30 筆）',
          '',
          '<!-- history:start -->',
          history.rstrip('\n'),
          '<!-- history:end -->',
          '']
    SUMMARY.write_text('\n'.join(L), encoding='utf-8', newline='\n')


# ---------------------------------------------------------------------------

def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--list', action='store_true', help='只列出狀態')
    ap.add_argument('--dry-run', action='store_true', help='只驗證，不覆寫、不改 summary')
    ap.add_argument('--file', action='append', default=[], help='指定檔（相對 REPO_ROOT），可重複')
    ap.add_argument('--max-files', type=int, default=20)
    ap.add_argument('--max-mb', type=float, default=25.0)
    ap.add_argument('--no-join', action='store_true', help='關閉斷行接合')
    ap.add_argument('--force', action='store_true', help='CLEAN 也重跑')
    args = ap.parse_args()
    started = dt.datetime.now()

    files = eligible_files()
    states = {f: file_state(f) for f in files}
    if args.list:
        for f in files:
            print(f'{states[f]:<11} {"light " if is_light(f) else "report"} {f.stat().st_size / 1024:>8,.0f} KB  {rel(f)}')
        print(f'total={len(files)} ' + ' '.join(f'{k}={v}' for k, v in collections.Counter(states.values()).items()))
        return 0

    if args.file:
        batch = []
        for x in args.file:
            p = (ROOT / x.replace('\\', '/')).resolve()
            if not p.exists():
                print(f'找不到：{x}')
                continue
            if p.name.lower() in SKIP_FILES:
                print(f'禁止清理：{x}')
                continue
            if states.get(p) == 'CLEAN' and not args.force:
                print(f'已是 CLEAN（要重跑請加 --force）：{x}')
                continue
            batch.append(p)
    else:
        pending = [f for f in files if states[f] != 'CLEAN' or args.force]
        batch = pick_batch(pending, args.max_files, args.max_mb)

    results = []
    for f in batch:
        text, utf8_ok = read_text(f)
        light = is_light(f)
        r = {'file': rel(f), 'mode': 'light' if light else 'report', 'before': f.stat().st_size}
        if not utf8_ok:
            r.update(status='FAIL', reason='非 UTF-8 編碼（含無法解碼位元組），未處理')
            results.append(r)
            print(f'[FAIL] {r["file"]} | {r["reason"]}')
            continue
        try:
            cleaned, st, err = clean_text(f, text, light, args.no_join)
        except Exception as e:                                   # 零阻塞：記錄後繼續
            cleaned, st, err = '', Stats(), f'例外：{type(e).__name__}: {e}'
        if err:
            r.update(status='FAIL', reason=err)
        else:
            r.update(status='OK', after=len(cleaned.encode('utf-8')),
                     detail=', '.join(f'{k}={v}' for k, v in sorted(st.items()) if v) or '無需變更（僅加導讀）')
            if not args.dry_run:
                atomic_write(f, cleaned)
                states[f] = 'CLEAN'
        results.append(r)
        print(f'[{r["status"]}] {r["file"]} | {r.get("detail") or r.get("reason")}')

    if not args.dry_run:
        pending = [f for f in files if states[f] != 'CLEAN']
        next_batch = pick_batch(pending, args.max_files, args.max_mb)
        write_summary(results, states, next_batch, args, started)
        print(f'summary → {rel(SUMMARY)}')
    ok = sum(r['status'] == 'OK' for r in results)
    fail = sum(r['status'] == 'FAIL' for r in results)
    print(f'MdClean done: OK={ok} FAIL={fail} SKIP={len(files) - len(batch)}')
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
