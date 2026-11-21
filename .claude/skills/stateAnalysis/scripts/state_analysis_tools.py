#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stateAnalysis 輔助腳本（Windows / Linux / macOS 皆可，Python 3.9+，只用標準函式庫，只讀不寫）

子命令：
  budget  逐章行數預算：各章「實際／上限」、超標行數、全檔距 1000 行還剩多少，並提示先砍哪裡（寫作中隨時跑）
  check   驗證 {cc}_state/AnalysisResult.md：第一行時間戳、章節骨架與順序、檔頭資訊卡七欄、
          行數／字元／單行長度上限、零表格（含 code block、Tab、HTML table）、禁用空話與裝飾標題、
          第〇章（大小、每行長度、免責、「上次：」、禁用詞、⚠️／(舊)）、四個強制輸出行、長序列格式、
          連續空行、逐章行數預算（附 budget 同一段輸出）
  series  讀檔內「MoM 序列」區塊，算出每區累計、自高點、近 6 月均值、YoY(估)、連續達標月數、
          4／5 個月規則與「房價 × 租金」聯合判定，供第七、八章填寫

用法（路徑用絕對路徑）：
  python state_analysis_tools.py budget --file <REPO>/jp_state/AnalysisResult.md
  python state_analysis_tools.py check  --cc jp [--file <REPO>/jp_state/AnalysisResult.md] [--today YYYY-MM-DD]
  python state_analysis_tools.py series --file <REPO>/jp_state/AnalysisResult.md
check 有 FAIL 時結束碼為 1；WARN 不影響結束碼，但要逐項看過並判斷。
上限、骨架、BUDGET 與禁用詞要和 SKILL.md §4、§4.0、§5.8、§8.3 及 references/{cc}.md 保持同步。
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

TZ8 = dt.timezone(dt.timedelta(hours=8))
REPO = Path(__file__).resolve().parents[4]  # <REPO>/.claude/skills/stateAnalysis/scripts/本檔

# ───────────────────────── 上限（SKILL.md §4.0、§8.3） ─────────────────────────
MAX_LINES, SOFT_LINES = 1000, 950
MAX_CHARS = 70_000
MAX_LINE, SOFT_LINE = 200, 120
CH0_MAX_LINES, CH0_MAX_CHARS, CH0_MAX_LINE = 100, 7_500, 100
THRESHOLD = -0.10  # 達標月：MoM ≥ −0.10%（＝ Idx(t) ≥ Idx(t−1) × 0.999）
EPS = 1e-9
LIST_MAX = 12  # 同類問題最多列幾處

# ───────────────────────── 骨架（SKILL.md §4） ─────────────────────────
STAMP_RE = re.compile(r"^> \*\*更新時間（Last Updated）：(\d{4})/(\d{2})/(\d{2}) "
                      r"([01]\d|2[0-3]):([0-5]\d):([0-5]\d) \(UTC\+8\)\*\*\s*$")
CARD = "檔頭資訊卡"
CHAPTERS = ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
TITLES = {
    "〇": "一般人 3 分鐘看懂", "一": "分析師決策摘要", "二": "景氣循環定位與進場時點",
    "三": "REIT 標的池逐檔分析", "四": "多空對照（詳細版）", "五": "總體、利率與匯率",
    "六": "房地產市場分板塊", "七": "房價 40 個月與 4 個月規則", "八": "租金 60 個月與 5 個月規則",
    "九": "政策與制度變數", "十": "輿情彙整", "十一": "資料來源與搜尋狀態", "十二": "資料缺口與下輪待辦",
}
# 逐章行數上限（SKILL.md §4 骨架括號與 §4.0；空行也算）。PRE＝第一個 `##` 之前的前置行。
PRE = "前置"
BUDGET = {
    PRE: 5, CARD: 20, "〇": 100, "一": 35, "二": 55, "三": 190, "四": 80, "五": 30,
    "六": 65, "七": 60, "八": 90, "九": 45, "十": 45, "十一": 25, "十二": 30,
}
# 超預算時的建議砍法（SKILL.md §8.3 刪減順序的章別版）
CUT_HINT = {
    PRE: "時間戳與主標題之間只留 1 個空行",
    CARD: "變更摘要 ≤ 5 行、3 件新事各 1 行",
    "〇": "〇.4 最多 8 檔完整寫，其餘列代號；每條 ≤ 50 字",
    "一": "速覽各留 3 條（依重要性）",
    "二": "機構預測與 Top 3 改比較式一行",
    "三": "§4.0 第三章自動壓縮：精簡版 6 行 → 觀察名單前 5 → 完整版合併無事項行",
    "四": "重要性「中」以下改一行、「低」刪",
    "五": "只留會改變便宜度／借錢成本判定的指標",
    "六": "每卡寫到階段＋2～3 個數字就停",
    "七": "序列只留 40 個月；摘要一行一區",
    "八": "序列只留 60 個月；摘要一行一區",
    "九": "非焦點 A 輪且里程碑無變化 → 全章標＝、壓到 15 行",
    "十": "一則一行；刪低可信度且無法量化的",
    "十一": "一檔 REIT 一行；成功來源合併一行",
    "十二": "已清償的刪，只留未結待辦與 30 天行事曆",
}
CARD_FIELDS = ["範圍與時間", "本檔主要幣別與匯率", "一句話結論", "🆕 本輪最重要的 3 件新事",
               "本輪變更摘要", "資料新鮮度", "每單位口徑"]
FORCED = [  # （名稱, 規則, 應出現的章）
    ("五盞燈", re.compile(r"\*\*五盞燈\*\*：\s*目前\s*(\d+)\s*綠\s*/\s*(\d+)\s*黃\s*/\s*(\d+)\s*紅"), "二"),
    ("4 個月規則", re.compile(r"\*\*4 個月規則\*\*："), "七"),
    ("5 個月規則", re.compile(r"\*\*5 個月規則\*\*："), "八"),
    ("政策結論", re.compile(r"\*\*政策結論\*\*："), "九"),
]
BANNED = ["持續觀察", "審慎樂觀", "有待觀察", "值得關注",
          "徹底崩跌", "末日毀滅", "泡沫幻滅", "徹底粉碎", "殘酷死鎖", "致命地雷", "殘酷出清"]
DECOR_HEADING = ["本輪全新增量", "深度穿透", "穿透備忘", "⭐ 新增"]
GLOSSARY_HEADING = ["名詞對照", "名詞解釋", "Glossary", "glossary"]

# ───────────────────────── 第〇章禁用詞（SKILL.md §5.8 共通＋§6 各國加碼） ─────────────────────────
COMMON_JARGON = [
    "REIT", "房託", "產業信託", "投資法人",
    "DPU", "分派", "可分派收入", "分配金", "殖利率",
    "NOI", "NPI", "FFO", "AFFO", "LTV", "借貸比率", "槓桿比率", "NAV", "P/NAV",
    "Cap Rate", "cap rate", "利差", "bp", "pp", "pt",
    "MoM", "YoY", "環比", "同比", "Idx", "指數化", "串接",
    "出租率", "空置率", "空室率", "空租率", "續租調整率", "租金改定率", "租金報酬率",
    "五盞燈", "階段①～④", "4 個月規則", "5 個月規則", "Focus", "A／B 組",
]
COUNTRY_JARGON = {
    "jp": ["J-REIT", "JGB", "BOJ", "日銀", "政策金利", "契約率", "REINS", "三鬼商事", "稼働率",
           "賃料改定", "巡航", "PO", "增資", "口數稀釋", "再融資懸崖", "RevPAR", "Inbound", "都心"],
    "hk": ["HIBOR", "LPR", "Fed", "FOMC", "一線", "甲辦", "去化週期", "到位資金", "PIR",
           "房價所得比", "土地使用權"],
}
JARGON_REGEX = {  # 顯示名稱 → 正規表示式（容許空白差異）
    "階段①～④": r"階段\s*[①②③④]",
    "4 個月規則": r"4\s*個月規則",
    "5 個月規則": r"5\s*個月規則",
    "A／B 組": r"(?<![A-Za-z])[AB]\s*組",
}
# 「名稱（代號）」：術語後面 15 字內接（3～6 碼代號）＝ REIT 正式名稱，不算術語
TICKER_AFTER = re.compile(r"[^，。；：、（）()\n]{0,15}?[（(][0-9A-Z]{3,6}[）)]")

# ───────────────────────── 長序列格式（SKILL.md §5.4） ─────────────────────────
SERIES_HEAD_RE = re.compile(r"^\s*[-*]\s.*MoM\s*序列")
MONTH_RE = re.compile(r"^\s+[-*]\s*(\d{4})-(\d{2})\s*[：:]\s*(.*?)\s*$")
VAL_RE = re.compile(r"([+\-−–]?)\s*(\d+(?:\.\d+)?)\s*%")


# ───────────────────────── 共用 ─────────────────────────
def out(msg: str = "") -> None:
    try:
        sys.stdout.buffer.write((msg + "\n").encode("utf-8", "replace"))
        sys.stdout.flush()
    except (BrokenPipeError, ValueError):  # 輸出被 | head 截斷時照樣做完
        pass


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def brief(items: list, label: str) -> str:
    shown = "、".join(str(x) for x in items[:LIST_MAX])
    more = f"…共 {len(items)} 處" if len(items) > LIST_MAX else ""
    return f"{label}：{shown}{more}"


def pct(x, ratio: bool = False) -> str:
    if x is None:
        return "N/A"
    v = x * 100 if ratio else x
    return f"+{v:.2f}%" if v >= 0 else f"−{abs(v):.2f}%"


def mark(ok: bool) -> str:
    return "✅" if ok else "❌"


# ───────────────────────── 章節切分 ─────────────────────────
H2_RE = re.compile(r"^##(?!#)\s*(.+?)\s*$")
NUM_RE = re.compile(r"^(十二|十一|十|〇|一|二|三|四|五|六|七|八|九)、\s*(.*)$")


def sections(lines: list[str]):
    """回傳 [(key, title, start, end)]；key＝'檔頭資訊卡'、'〇'…'十二'，非骨架標題為 None。"""
    heads = []
    for i, line in enumerate(lines):
        m = H2_RE.match(line)
        if not m:
            continue
        title = m.group(1)
        if title.startswith(CARD):
            heads.append((CARD, title, i))
            continue
        mm = NUM_RE.match(title)
        heads.append((mm.group(1), mm.group(2).strip(), i) if mm else (None, title, i))
    return [(k, t, s, heads[n + 1][2] if n + 1 < len(heads) else len(lines))
            for n, (k, t, s) in enumerate(heads)]


# ───────────────────────── 行數預算 ─────────────────────────
def chapter_usage(lines: list[str]):
    """回傳 [(key, label, used, cap)]，依檔內順序；未知 `##` 併入前一章計算。"""
    secs = sections(lines)
    usage: dict = {}
    order: list = []
    first = secs[0][2] if secs else len(lines)
    usage[PRE] = first
    order.append(PRE)
    last_key = PRE
    for key, title, s, e in secs:
        k = key if key in BUDGET else last_key
        if k not in usage:
            usage[k] = 0
            order.append(k)
        usage[k] += e - s
        last_key = k
    res = []
    for k in order:
        label = k if k in (PRE, CARD) else f"{k}、{TITLES.get(k, '')}"
        res.append((k, label, usage[k], BUDGET.get(k)))
    return res


def budget_report(lines: list[str]) -> tuple[list[str], list[str]]:
    """回傳 (輸出行, 超標警告)。"""
    rows, warns = [], []
    usage = chapter_usage(lines)
    n = len(lines)
    total_cap = sum(BUDGET.values())
    over_list = []
    for k, label, used, cap in usage:
        if cap is None:
            rows.append(f"  - {label}：{used} 行")
            continue
        over = used - cap
        flag = f"　⚠️ 超標 +{over}" if over > 0 else ""
        rows.append(f"  - {label}：{used}/{cap}{flag}")
        if over > 0:
            over_list.append((over, k, label))
    blanks = sum(1 for x in lines if not x.strip())
    head = [f"## 行數預算（SKILL.md §4.0；空行也算）",
            f"- 全檔 {n}/{MAX_LINES} 行（目標 ≤ {SOFT_LINES}；預算合計 {total_cap}）｜距硬上限還剩 {MAX_LINES - n} 行"
            f"｜空行 {blanks} 行"]
    tail = []
    if over_list:
        over_list.sort(reverse=True)
        tail.append("- 先砍（超標多的在前）：")
        for over, k, label in over_list:
            tail.append(f"  - {label} +{over} 行 → {CUT_HINT.get(k, '依 §8.3 刪減順序')}")
            warns.append(f"{label} {over + BUDGET[k]} 行 > 預算 {BUDGET[k]}（+{over}）→ {CUT_HINT.get(k, '')}")
    if n > MAX_LINES:
        tail.append(f"- ❌ 至少要刪 {n - MAX_LINES} 行才合格；建議刪到 ≤ {SOFT_LINES}（再刪 {n - SOFT_LINES} 行）")
    elif n > SOFT_LINES:
        tail.append(f"- ⚠️ 超過目標 {SOFT_LINES}，建議再刪 {n - SOFT_LINES} 行")
    return head + rows + tail, warns


# ───────────────────────── 第〇章禁用詞 ─────────────────────────
def jargon_patterns(cc: str):
    pats = []
    for term in dict.fromkeys(COMMON_JARGON + COUNTRY_JARGON.get(cc, [])):
        if term in JARGON_REGEX:
            pats.append((term, re.compile(JARGON_REGEX[term])))
        elif re.fullmatch(r"[A-Za-z][A-Za-z/\- ]*", term):  # 英文術語：前後不可緊鄰英文字母
            pats.append((term, re.compile(r"(?<![A-Za-z])" + re.escape(term) + r"s?(?![A-Za-z])")))
        else:
            pats.append((term, re.compile(re.escape(term))))
    return pats


def jargon_hits(lines: list[str], first_no: int, pats) -> list[str]:
    explained, hits = set(), []
    for k, line in enumerate(lines):
        for name, pat in pats:
            for m in pat.finditer(line):
                rest = line[m.end():]
                if TICKER_AFTER.match(rest):
                    continue  # REIT 正式名稱（後面接代號）
                if name not in explained and rest[:1] in ("（", "("):
                    explained.add(name)  # 第一次出現且括號白話解釋，放行一次
                    continue
                hits.append(f"{first_no + k}:{name}")
    return hits


# ───────────────────────── 長序列解析與統計 ─────────────────────────
def parse_val(cell: str):
    """回傳 (值或 None, 是否無法解讀)。N/A、—、空白 → None。"""
    c = cell.strip()
    if re.match(r"^N/?A", c, re.I):
        return None, False
    m = VAL_RE.search(c)
    if m:
        sign = -1.0 if m.group(1) in ("-", "−", "–") else 1.0
        return sign * float(m.group(2)), False
    if c in ("", "—", "－", "-"):
        return None, False
    return None, True


def ym_next(ym: str) -> str:
    y, m = map(int, ym.split("-"))
    y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return f"{y:04d}-{m:02d}"


def missing_months(months: list[str]) -> list[str]:
    if not months:
        return []
    have, miss, cur = set(months), [], months[0]
    while cur < months[-1]:
        cur = ym_next(cur)
        if cur not in have:
            miss.append(cur)
    return miss


def parse_series(lines: list[str]):
    """找出所有「MoM 序列」母條目與其下的月份子條目。回傳 (blocks, errors)。"""
    blocks, errors = [], []
    i = 0
    while i < len(lines):
        if not SERIES_HEAD_RE.match(lines[i]):
            i += 1
            continue
        head = lines[i]
        title = re.sub(r"\*\*", "", head).strip().lstrip("-* ").strip()
        m = re.search(r"序列\s*[（(]([^）)]*)[）)]", head)
        regions = [r.strip() for r in re.split(r"[；;]", m.group(1))[0].split("｜") if r.strip()] if m else []
        rows, j = {}, i + 1
        while j < len(lines):
            mm = MONTH_RE.match(lines[j])
            if not mm:
                break
            ym = f"{mm.group(1)}-{mm.group(2)}"
            cells = [c.strip() for c in mm.group(3).split("｜")]
            if not 1 <= int(mm.group(2)) <= 12:
                errors.append(f"第 {j + 1} 行：月份 {ym} 不存在")
            elif ym in rows:
                errors.append(f"第 {j + 1} 行：月份 {ym} 重複")
            else:
                if not regions:
                    regions = [f"區{k + 1}" for k in range(len(cells))]
                if len(cells) != len(regions):
                    errors.append(f"第 {j + 1} 行：{ym} 有 {len(cells)} 個值，母條目列了 {len(regions)} 區")
                else:
                    vals = []
                    for c in cells:
                        v, bad = parse_val(c)
                        if bad:
                            errors.append(f"第 {j + 1} 行：無法解讀「{c}」（請寫 +0.42%、−0.05% 或 N/A）")
                        vals.append(v)
                    rows[ym] = vals
            j += 1
        months = sorted(rows)
        blocks.append({"title": title, "regions": regions, "line": i + 1,
                       "months": months, "values": [rows[x] for x in months],
                       "gaps": missing_months(months)})
        i = j
    return blocks, errors


def region_stats(months: list[str], vals: list):
    idx = [100.0]  # 首月 = 100，逐月 ×（1 + MoM）；N/A 以 0% 串接
    for v in vals[1:]:
        idx.append(idx[-1] * (1 + (v if v is not None else 0.0) / 100))
    n = len(vals)
    peak = max(range(n), key=lambda k: (idx[k], k))
    trough = min(range(n), key=lambda k: (idx[k], -k))
    last6 = [v for v in vals[-6:] if v is not None]
    streak = 0
    for v in reversed(vals):
        if v is None or v < THRESHOLD - EPS:
            break
        streak += 1
    run = worst = 0
    for v in vals[-12:]:
        run = run + 1 if v is None else 0
        worst = max(worst, run)
    eligible = worst < 3
    return {
        "cum": idx[-1] / idx[0] - 1,
        "peak_m": months[peak], "from_peak": idx[-1] / idx[peak] - 1,
        "trough_m": months[trough], "from_trough": idx[-1] / idx[trough] - 1,
        "avg6": sum(last6) / len(last6) if last6 else None,
        "last": vals[-1], "last_m": months[-1],
        "yoy": idx[-1] / idx[-13] - 1 if n >= 13 else None,
        "streak": streak, "eligible": eligible, "last5": vals[-5:],
        "pass4": eligible and streak >= 4, "pass5": eligible and streak >= 5,
    }


# ───────────────────────── check ─────────────────────────
def cmd_check(a) -> int:
    cc = a.cc.lower().strip()
    if not re.fullmatch(r"[a-z]{2,3}", cc):
        sys.exit(f"[錯誤] --cc 只收 2～3 個英文字母：{a.cc}")
    path = Path(a.file).resolve() if a.file else REPO / f"{cc}_state" / "AnalysisResult.md"
    today = dt.date.fromisoformat(a.today) if a.today else dt.datetime.now(TZ8).date()
    if not path.is_file():
        out(f"# check\n- ❌ 找不到檔案：{path}")
        return 1
    try:
        text = read_text(path)
    except UnicodeDecodeError:
        out(f"# check\n- ❌ 不是 UTF-8 編碼：{path}")
        return 1
    lines = text.splitlines()
    fails: list[str] = []
    warns: list[str] = []

    # 1. 時間戳
    first = lines[0] if lines else ""
    m = STAMP_RE.match(first)
    if not m:
        fails.append(f"第 1 行不是時間戳樣板 `> **更新時間（Last Updated）：yyyy/MM/dd HH:mm:ss (UTC+8)**`：{first[:60]}")
    else:
        try:
            d = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if d != today:
                fails.append(f"時間戳日期 {d} 不是今天（{today}）→ 全檔寫完後重取系統時間")
        except ValueError:
            fails.append(f"時間戳日期不存在：{first[:60]}")
    n_stamp = sum("更新時間（Last Updated）" in line for line in lines)
    if n_stamp != 1:
        fails.append(f"時間戳出現 {n_stamp} 次（只能 1 次，不留版本歷史）")

    # 2. 主標題
    h1 = [i for i, line in enumerate(lines[:6]) if line.startswith("# ")]
    if not h1:
        fails.append("前 6 行找不到 `# ` 主標題")
    elif f"stateAnalysis {cc.upper()}" not in lines[h1[0]]:
        warns.append(f"主標題建議含「（stateAnalysis {cc.upper()}）」：{lines[h1[0]][:60]}")

    # 3. 章節骨架與順序
    secs = sections(lines)
    expect = [CARD] + CHAPTERS
    keys = [s[0] for s in secs if s[0]]
    for k in expect:
        c = keys.count(k)
        label = f"## {CARD}" if k == CARD else f"## {k}、{TITLES[k]}"
        if c == 0:
            fails.append(f"缺章節：{label}")
        elif c > 1:
            fails.append(f"章節重複 {c} 次：{label}")
    firsts = list(dict.fromkeys(keys))
    if firsts != [k for k in expect if k in firsts]:
        fails.append("章節順序錯誤：" + " → ".join(firsts))
    sec = {}
    for key, title, s, e in secs:
        if key is None:
            warns.append(f"第 {s + 1} 行：非骨架的 `## {title}`（改成 ### 或併入骨架章節）")
            continue
        sec.setdefault(key, (s, e))
        if key in TITLES and title != TITLES[key]:
            warns.append(f"第 {s + 1} 行：標題建議照抄「{key}、{TITLES[key]}」，目前是「{key}、{title}」")

    # 4. 檔頭資訊卡七欄
    if CARD in sec:
        s, e = sec[CARD]
        pos = []
        for f in CARD_FIELDS:
            hit = next((i for i in range(s, e) if f"**{f}**" in lines[i]), None)
            if hit is None:
                fails.append(f"檔頭資訊卡缺欄位：**{f}**")
            else:
                pos.append(hit)
        if pos != sorted(pos):
            fails.append("檔頭資訊卡欄位順序不對（應為：" + "、".join(CARD_FIELDS) + "）")

    # 5. 逐行：長度、零表格、禁用空話、裝飾標題
    too_long, soft, tables, tabs, fences, banned, decor, dblank = [], 0, [], [], [], [], [], []
    for no, line in enumerate(lines, 1):
        if no > 1 and not line.strip() and not lines[no - 2].strip():
            dblank.append(no)
        n_chars = len(line)
        if n_chars > MAX_LINE:
            too_long.append(f"{no}（{n_chars} 字）")
        elif n_chars > SOFT_LINE:
            soft += 1
        if line.count("|") >= 2 or "<table" in line.lower():
            tables.append(no)
        if "\t" in line:
            tabs.append(no)
        if line.lstrip().startswith(("```", "~~~")):
            fences.append(no)
        banned += [f"{no}:{b}" for b in BANNED if b in line]
        if line.lstrip().startswith("#"):
            decor += [f"{no}:{w}" for w in DECOR_HEADING + GLOSSARY_HEADING if w in line]
    if too_long:
        fails.append(brief(too_long, f"單行超過 {MAX_LINE} 字（拆行或刪字）"))
    if soft:
        warns.append(f"{soft} 行超過 {SOFT_LINE} 字（建議拆短）")
    if tables:
        fails.append(brief(tables, "疑似表格（ASCII `|` ≥ 2 個或 <table>，改寫成 key-value）"))
    if tabs:
        fails.append(brief(tabs, "含 Tab（疑似對齊假表格）"))
    if fences:
        fails.append(brief(fences, "含 code block（輸出檔不用 code block，引用原文改用 >）"))
    if banned:
        fails.append(brief(banned, "禁用空話／形容詞堆疊"))
    if decor:
        fails.append(brief(decor, "裝飾標題或 Glossary 標題"))
    if dblank:
        warns.append(brief(dblank, "連續空行（浪費行數，刪掉）"))

    # 6. 全檔上限
    n_lines, n_text = len(lines), len(text)
    if n_lines > MAX_LINES:
        fails.append(f"全檔 {n_lines} 行 > {MAX_LINES}（看下方「行數預算」，依 SKILL.md §8.3 刪減順序刪到合格）")
    elif n_lines > SOFT_LINES:
        warns.append(f"全檔 {n_lines} 行 > 目標 {SOFT_LINES}")
    budget_lines, budget_warns = budget_report(lines)
    warns += budget_warns
    if n_text > MAX_CHARS:
        fails.append(f"全檔 {n_text:,} 字元 > {MAX_CHARS:,}")

    # 7. 第〇章
    ch0_lines = ch0_chars = 0
    if "〇" in sec:
        s, e = sec["〇"]
        ch = lines[s:e]
        while ch and not ch[-1].strip():  # 章末空行不計
            ch.pop()
        ch0_lines, ch0_chars = len(ch), sum(len(x) + 1 for x in ch)
        if ch0_lines > CH0_MAX_LINES:
            fails.append(f"第〇章 {ch0_lines} 行 > {CH0_MAX_LINES}")
        if ch0_chars > CH0_MAX_CHARS:
            fails.append(f"第〇章 {ch0_chars:,} 字元 > {CH0_MAX_CHARS:,}")
        over = [f"{s + k + 1}（{len(x)} 字）" for k, x in enumerate(ch) if len(x) > CH0_MAX_LINE]
        if over:
            fails.append(brief(over, f"第〇章單行超過 {CH0_MAX_LINE} 字"))
        body = "\n".join(ch)
        for must, why in (("不是個人化投資建議", "免責一行"), ("資料截至", "「資料截至 YYYY-MM-DD」"),
                          ("上次：", "溫度計「上次：X」")):
            if must not in body:
                fails.append(f"第〇章缺{why}")
        found = [mm.group(1) for x in ch if (mm := re.match(r"^###\s*(〇\.\d)", x))]
        need = [f"〇.{k}" for k in range(1, 8)]
        lost = [x for x in need if x not in found]
        if lost:
            fails.append("第〇章缺小節：" + "、".join(f"### {x}" for x in lost))
        elif [x for x in found if x in need] != need:
            fails.append("第〇章小節順序不對（應為 〇.1 → 〇.7）")
        stale = [str(s + k + 1) for k, x in enumerate(ch) if "⚠" in x or "(舊)" in x or "（舊）" in x]
        if stale:
            fails.append(brief(stale, "第〇章不得出現 ⚠️ 或 (舊)（未證實與過舊數字不進第〇章）"))
        hits = jargon_hits(ch, s + 1, jargon_patterns(cc))
        if hits:
            fails.append(brief(hits, "第〇章禁用詞（改白話；必要時只在第一次出現處括號解釋）"))

    # 8. 四個強制輸出行
    for name, pat, want in FORCED:
        locs = [i for i, line in enumerate(lines) if pat.search(line)]
        if not locs:
            fails.append(f"缺強制輸出行：`- **{name}**：…`（格式見 SKILL.md §4.4）")
            continue
        if want in sec and not any(sec[want][0] <= i < sec[want][1] for i in locs):
            warns.append(f"強制輸出行 **{name}** 應寫在第{want}章")
        if name == "五盞燈":
            for i in locs:
                g, y, r = map(int, pat.search(lines[i]).groups())
                if g + y + r != 5:
                    fails.append(f"第 {i + 1} 行：五盞燈 {g} 綠＋{y} 黃＋{r} 紅 ≠ 5")

    # 9. 第三章燈號分布
    if "三" in sec:
        s, e = sec["三"]
        n_blocks = sum(1 for i in range(s, e) if re.match(r"^###\s*[🟢🟡🔴]", lines[i]))
        dist = next((lines[i] for i in range(s, e) if "燈號分布" in lines[i]), None)
        if dist is None:
            warns.append("第三章找不到「燈號分布：🟢 X 檔｜🟡 Y 檔｜🔴 Z 檔」")
        else:
            total = sum(int(x) for x in re.findall(r"[🟢🟡🔴]\s*(\d+)\s*檔", dist))
            if total != n_blocks:
                warns.append(f"燈號分布合計 {total} 檔，但第三章 `### <燈號>` 標題有 {n_blocks} 檔")

    # 10. 長序列格式
    blocks, errs = parse_series(lines)
    fails += errs
    for b in blocks:
        want = 40 if "40 個月" in b["title"] else 60 if "60 個月" in b["title"] else None
        if want and len(b["months"]) < want:
            warns.append(f"第 {b['line']} 行序列只有 {len(b['months'])} 個月（應 {want}）→ 缺口寫進第十二章")
        elif want and len(b["months"]) > want:
            warns.append(f"第 {b['line']} 行序列有 {len(b['months'])} 個月 > {want} → 刪最舊 {len(b['months']) - want} 個月"
                         f"（{'、'.join(b['months'][:len(b['months']) - want][:LIST_MAX])}）")
        if b["gaps"]:
            warns.append(brief(b["gaps"], f"第 {b['line']} 行序列缺月份（補 N/A 列）"))
    for key, label in (("七", "房價"), ("八", "租金")):
        if key in sec and not any(sec[key][0] < b["line"] <= sec[key][1] for b in blocks):
            warns.append(f"第{key}章找不到「{label} … MoM 序列」區塊（SKILL.md §5.4 格式），series 算不到")

    # 輸出
    longest = max((len(x) for x in lines), default=0)
    out(f"# check — {path}（今天 {today}｜cc={cc}）")
    out(f"- 行數 {n_lines}/{MAX_LINES}｜字元 {n_text:,}/{MAX_CHARS:,}｜最長行 {longest} 字"
        f"｜第〇章 {ch0_lines}/{CH0_MAX_LINES} 行、{ch0_chars:,}/{CH0_MAX_CHARS:,} 字元")
    out(f"- ❌ FAIL {len(fails)}｜WARN {len(warns)}" if fails else f"- ✅ 0 個 FAIL｜WARN {len(warns)}")
    if fails:
        out("## FAIL（全部修正後重跑）")
        for f in fails:
            out(f"  - {f}")
    if warns:
        out("## WARN（逐項看過並判斷）")
        for w in warns:
            out(f"  - {w}")
    for x in budget_lines:
        out(x)
    return 1 if fails else 0


# ───────────────────────── budget ─────────────────────────
def cmd_budget(a) -> int:
    path = Path(a.file).resolve()
    if not path.is_file():
        out(f"# budget\n- ❌ 找不到檔案：{path}")
        return 1
    lines = read_text(path).splitlines()
    out(f"# budget — {path}")
    rows, _ = budget_report(lines)
    for x in rows:
        out(x)
    return 1 if len(lines) > MAX_LINES else 0


# ───────────────────────── series ─────────────────────────
def cmd_series(a) -> int:
    path = Path(a.file).resolve()
    if not path.is_file():
        out(f"# series\n- ❌ 找不到檔案：{path}")
        return 1
    lines = read_text(path).splitlines()
    blocks, errors = parse_series(lines)
    out(f"# series — {path}")
    out(f"- 達標月：MoM ≥ {pct(THRESHOLD)}；N/A 不算達標；最近 12 個月連續 N/A ≥ 3 的地區不得參與判定")
    if errors:
        out("## 格式錯誤（先修正，結果才可信）")
        for e in errors:
            out(f"  - {e}")
    if not blocks:
        out("- 找不到「MoM 序列」區塊（格式見 SKILL.md §5.4）")
        return 1
    results = []
    for b in blocks:
        months = b["months"]
        out(f"## {b['title']}（第 {b['line']} 行）")
        if not months:
            out("- 沒有可用的月份資料")
            continue
        n_na = sum(v is None for row in b["values"] for v in row)
        out(f"- 期間：{months[0]} ～ {months[-1]}，共 {len(months)} 個月｜缺月 {len(b['gaps'])}｜N/A {n_na} 格"
            "｜Idx 以首月 = 100 串接 (估)")
        want = 40 if "40 個月" in b["title"] else 60 if "60 個月" in b["title"] else None
        if want and len(months) > want:
            out(f"- ⚠️ 超過 {want} 個月：寫回 <OUT> 時刪最舊 {len(months) - want} 個月（SKILL.md §5.4，序列行數固定）")
        stats = {}
        for k, reg in enumerate(b["regions"]):
            st = region_stats(months, [row[k] for row in b["values"]])
            stats[reg] = st
            flag = "" if st["eligible"] else "｜⚠️ 最近 12 個月連續 N/A ≥ 3，不得參與判定"
            out(f"- {reg}：累計 {pct(st['cum'], True)}｜自高點 {pct(st['from_peak'], True)}（高點 {st['peak_m']}）"
                f"｜自低點 {pct(st['from_trough'], True)}（低點 {st['trough_m']}）｜近 6 月均 {pct(st['avg6'])}"
                f"｜最新 {pct(st['last'])}（{st['last_m']}）｜YoY(估) {pct(st['yoy'], True)}"
                f"｜連續達標 {st['streak']} 月 → 4 個月 {mark(st['pass4'])}｜5 個月 {mark(st['pass5'])}{flag}")
            out("  - 最近 5 個月（舊 → 新）：" + "｜".join(pct(v) for v in st["last5"]))
        for n_rule, key in ((4, "pass4"), (5, "pass5")):
            ok = [r for r, st in stats.items() if st[key]]
            out(f"- {n_rule} 個月達標：{len(ok)}/{len(stats)} 區（"
                + "、".join(f"{r}{mark(st[key])}" for r, st in stats.items()) + "）")
        results.append((b["title"], stats, months[-1]))
    price = next((r for r in results if "房價" in r[0]), None)
    rent = next((r for r in results if "租金" in r[0]), None)
    if price and rent:
        out("## 房價 × 租金聯合判定（4 個月規則）")
        if price[2] != rent[2]:
            out(f"- ⚠️ 最新月份不同：房價 {price[2]}、租金 {rent[2]}（各用自己最近 4 個月判定，正文要註明）")
        common = [r for r in price[1] if r in rent[1]]
        if not common:
            out("- 兩個序列沒有同名地區 → 地區名稱要一字不差（SKILL.md §5.4）")
        else:
            ok = [r for r in common if price[1][r]["pass4"] and rent[1][r]["pass4"]]
            for r in common:
                out(f"- {r}：房價 {mark(price[1][r]['pass4'])}｜租金 {mark(rent[1][r]['pass4'])} → 聯合 {mark(r in ok)}")
            out(f"- 聯合通過 {len(ok)}/{len(common)} 區 → " + ("≥ 3 區＝確認" if len(ok) >= 3 else "< 3 區＝未確認"))
    return 1 if errors else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="stateAnalysis helper（只讀不寫）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("budget", help="逐章行數預算（寫作中隨時跑）")
    b.add_argument("--file", required=True)
    c = sub.add_parser("check", help="驗證 {cc}_state/AnalysisResult.md")
    c.add_argument("--cc", required=True, help="國家代碼，如 jp、hk")
    c.add_argument("--file", help="預設 <REPO>/{cc}_state/AnalysisResult.md")
    c.add_argument("--today", help="YYYY-MM-DD，預設今天（UTC+8）")
    s = sub.add_parser("series", help="計算長序列 4／5 個月規則")
    s.add_argument("--file", required=True)
    a = ap.parse_args()
    return {"check": cmd_check, "budget": cmd_budget, "series": cmd_series}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
