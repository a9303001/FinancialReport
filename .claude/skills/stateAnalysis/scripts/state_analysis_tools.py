#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stateAnalysis 輔助腳本（Windows / Linux / macOS，Python 3.9+，只用標準函式庫，不寫入 repo）

子命令：
  skeleton  從 references/output_template.md 產生 AnalysisResult.md 草稿（印到 stdout，自行導向檔案）
  series    讀檔內「MoM 序列」區塊，算每區累計、自高點、近 6 月均值、YoY(估)、連續達標月數、
            4／5 個月規則與「房價 × 租金」聯合判定，供第七、八章填寫
  budget    逐章行數預算：各章「實際／上限」、超標行數、距 1000 行還剩多少，並提示先砍哪裡
  check     交付實測：時間戳、骨架與順序、檔頭七欄、行數／字元／單行上限、零表格、禁用空話與裝飾標題、
            樣板殘留、第〇章（大小、免責、「上次：」、NT$10 萬、禁用詞、⚠️／(舊)／(種子)）、四個強制輸出行、
            第三章逐檔欄位與行數、第四章小標、長序列格式與長度、連續空行、逐章行數預算
            --draft：寫作中使用，時間戳與樣板殘留降為 WARN
  selftest  維護自檢：SKILL.md §4.1 預算＝BUDGET、樣板骨架＝TITLES／CARD_FIELDS／FORCED、
            樣板逐檔範例符合 REIT_FIELDS、國家模組與 COUNTRY_JARGON 對得上、.claude／.agents 兩份相同

用法（路徑用絕對路徑）：
  python state_analysis_tools.py skeleton --cc jp > <REPO>/jp_state/AnalysisResult.md
  python state_analysis_tools.py series   --file <REPO>/jp_state/AnalysisResult.md
  python state_analysis_tools.py budget   --file <REPO>/jp_state/AnalysisResult.md
  python state_analysis_tools.py check    --cc jp [--file <OUT>] [--today YYYY-MM-DD] [--draft]
  python state_analysis_tools.py selftest
check／selftest 有 FAIL 時結束碼為 1；WARN 不影響結束碼，但要逐項看過並判斷。
"""
from __future__ import annotations

import argparse
import datetime as dt
import filecmp
import re
import sys
from pathlib import Path

TZ8 = dt.timezone(dt.timedelta(hours=8))
SKILL_DIR = Path(__file__).resolve().parents[1]  # <REPO>/.claude/skills/stateAnalysis
REPO = SKILL_DIR.parents[2]
TPL = SKILL_DIR / "references" / "output_template.md"
COPY_MARK = "<!-- COPY-START -->"

# ───────────────────────── 上限（SKILL.md §4.1、§8.3） ─────────────────────────
MAX_LINES, SOFT_LINES = 1000, 950
MAX_CHARS = 70_000
MAX_LINE, SOFT_LINE = 200, 120
CH0_MAX_LINES, CH0_MAX_CHARS, CH0_MAX_LINE = 100, 7_500, 100
SKILL_MAX_CHARS = 25_000
THRESHOLD = -0.10  # 達標月：MoM ≥ −0.10%（＝ Idx(t) ≥ Idx(t−1) × 0.999）
EPS = 1e-9
LIST_MAX = 12  # 同類問題最多列幾處
SERIES_LEN = {"40 個月": 40, "60 個月": 60}

# ───────────────────────── 骨架（references/output_template.md） ─────────────────────────
STAMP_RE = re.compile(r"^> \*\*更新時間（Last Updated）：(\d{4})/(\d{2})/(\d{2}) "
                      r"([01]\d|2[0-3]):([0-5]\d):([0-5]\d) \(UTC\+8\)\*\*\s*$")
CARD = "檔頭資訊卡"
PRE = "前置"
CHAPTERS = ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
TITLES = {
    "〇": "一般人 3 分鐘看懂", "一": "分析師決策摘要", "二": "景氣循環定位與進場時點",
    "三": "REIT 標的池逐檔分析", "四": "多空對照（詳細版）", "五": "總體、利率與匯率",
    "六": "房地產市場分板塊", "七": "房價 40 個月與 4 個月規則", "八": "租金 60 個月與 5 個月規則",
    "九": "政策與制度變數", "十": "輿情彙整", "十一": "資料來源與搜尋狀態", "十二": "資料缺口與下輪待辦",
}
COUNTRY_NAME = {"jp": "日本", "hk": "香港", "tw": "台灣", "us": "美國", "sg": "新加坡", "cn": "中國"}
CARD_FIELDS = ["範圍與時間", "本檔主要幣別與匯率", "一句話結論", "🆕 本輪最重要的 3 件新事",
               "本輪變更摘要", "資料新鮮度", "每單位口徑"]
FORCED = [  # （名稱, 規則, 應出現的章）
    ("五盞燈", re.compile(r"\*\*五盞燈\*\*：\s*目前\s*(\d+)\s*綠\s*/\s*(\d+)\s*黃\s*/\s*(\d+)\s*紅"), "二"),
    ("4 個月規則", re.compile(r"\*\*4 個月規則\*\*："), "七"),
    ("5 個月規則", re.compile(r"\*\*5 個月規則\*\*："), "八"),
    ("政策結論", re.compile(r"\*\*政策結論\*\*："), "九"),
]
NEED_CONCLUSION = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
NEED_SO_WHAT = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
# 第三章逐檔必備（SKILL.md §5.5；名稱 → 任一關鍵字出現即可）
REIT_FIELDS = {
    "結論": ["**結論**"], "殖利率": ["殖利率"], "股價淨值比": ["股價淨值比", "P/NAV"],
    "租金報酬率": ["租金報酬率"], "空租率": ["空租率"], "負債比率": ["負債比率", "LTV"],
    "配息品質": ["配息品質"], "所以呢": ["**所以呢**"],
}
REIT_MAX = {"完整版": 16, "精簡版": 8}
BANNED = ["持續觀察", "審慎樂觀", "有待觀察", "值得關注",
          "徹底崩跌", "末日毀滅", "泡沫幻滅", "徹底粉碎", "殘酷死鎖", "致命地雷", "殘酷出清"]
DECOR_HEADING = ["本輪全新增量", "深度穿透", "穿透備忘", "⭐ 新增"]
GLOSSARY_HEADING = ["名詞對照", "名詞解釋", "Glossary", "glossary"]
PLACEHOLDER_RE = re.compile(r"<(?![!/\s]|table|br)[^<>\n]{1,40}>")
DEMO_MARK = "9999 示範"

# 逐章行數上限（SKILL.md §4.1；空行也算）。PRE＝第一個 `##` 之前的前置行。
BUDGET = {
    PRE: 5, CARD: 20, "〇": 100, "一": 35, "二": 55, "三": 190, "四": 80, "五": 30,
    "六": 65, "七": 60, "八": 90, "九": 45, "十": 45, "十一": 25, "十二": 30,
}
CUT_HINT = {  # 超預算時的建議砍法（SKILL.md §8.3 刪減順序的章別版）
    PRE: "時間戳與主標題之間只留 1 個空行",
    CARD: "變更摘要 ≤ 5 行、3 件新事各 1 行",
    "〇": "〇.4 最多 8 檔完整寫，其餘列代號；每條 ≤ 50 字",
    "一": "速覽各留 3 條（依重要性）",
    "二": "機構預測與 Top 3 改比較式一行",
    "三": "§4.1 第三章壓縮：精簡版 6 行 → 觀察名單前 5 → 完整版合併無事項行",
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

# ───────────────────────── 第〇章禁用詞（SKILL.md §5.8 共通＋references/{cc}.md 加碼） ─────────────────────────
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


def report(title: str, fails: list[str], warns: list[str], extra: list[str] | None = None) -> int:
    out(f"- ❌ FAIL {len(fails)}｜WARN {len(warns)}" if fails else f"- ✅ 0 個 FAIL｜WARN {len(warns)}")
    if fails:
        out(f"## FAIL（全部修正後重跑 {title}）")
        for f in fails:
            out(f"  - {f}")
    if warns:
        out("## WARN（逐項看過並判斷）")
        for w in warns:
            out(f"  - {w}")
    for x in extra or []:
        out(x)
    return 1 if fails else 0


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


def section_map(lines: list[str]) -> dict:
    sec = {}
    for key, _t, s, e in sections(lines):
        if key:
            sec.setdefault(key, (s, e))
    return sec


def check_skeleton(lines: list[str], fails: list[str], warns: list[str]) -> dict:
    """章節齊全、不重複、順序正確、標題照抄、檔頭七欄。回傳 section_map。"""
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
    for key, title, s, _e in secs:
        if key is None:
            warns.append(f"第 {s + 1} 行：非骨架的 `## {title}`（改成 ### 或併入骨架章節）")
        elif key in TITLES and title != TITLES[key]:
            warns.append(f"第 {s + 1} 行：標題要照抄「{key}、{TITLES[key]}」，目前是「{key}、{title}」")
    sec = section_map(lines)
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
    return sec


def reit_blocks(lines: list[str], sec: dict):
    """第三章 `### <燈號> …` 區塊：回傳 [(標題, 起行, 區塊行)]，區塊到下一個 ### 或 ## 為止。"""
    if "三" not in sec:
        return []
    s, e = sec["三"]
    starts = [i for i in range(s, e) if re.match(r"^###\s*[🟢🟡🔴]", lines[i])]
    bounds = [i for i in range(s + 1, e) if lines[i].startswith("###")] + [e]
    res = []
    for i in starts:
        end = next(b for b in bounds if b > i)
        block = lines[i:end]
        while block and not block[-1].strip():
            block.pop()
        res.append((lines[i].lstrip("# ").strip(), i, block))
    return res


def check_reits(lines: list[str], sec: dict, fails: list[str], warns: list[str]) -> None:
    blocks = reit_blocks(lines, sec)
    for title, i, block in blocks:
        text = "\n".join(block)
        kind = "完整版" if re.search(r"\*\*現價\*\*", text) else "精簡版"
        lost = [k for k, alts in REIT_FIELDS.items() if not any(a in text for a in alts)]
        if lost:
            fails.append(f"第 {i + 1} 行 {title[:24]}：缺必備欄位 " + "、".join(lost) + "（查不到寫 N/A（原因））")
        if len(block) > REIT_MAX[kind]:
            fails.append(f"第 {i + 1} 行 {title[:24]}：{kind} {len(block)} 行 > {REIT_MAX[kind]}")
    if "三" in sec:
        s, e = sec["三"]
        dist = next((lines[k] for k in range(s, e) if "燈號分布" in lines[k]), None)
        if dist is None:
            warns.append("第三章找不到「燈號分布：🟢 X 檔｜🟡 Y 檔｜🔴 Z 檔」")
        else:
            nums = re.findall(r"[🟢🟡🔴]\s*(\d+)\s*檔", dist)
            total = sum(int(x) for x in nums)
            if nums and total != len(blocks):
                warns.append(f"燈號分布合計 {total} 檔，但第三章 `### <燈號>` 標題有 {len(blocks)} 檔")


# ───────────────────────── 行數預算 ─────────────────────────
def chapter_usage(lines: list[str]):
    """回傳 [(key, label, used, cap)]，依檔內順序；未知 `##` 併入前一章計算。"""
    secs = sections(lines)
    usage: dict = {PRE: secs[0][2] if secs else len(lines)}
    order, last_key = [PRE], PRE
    for key, _title, s, e in secs:
        k = key if key in BUDGET else last_key
        if k not in usage:
            usage[k] = 0
            order.append(k)
        usage[k] += e - s
        last_key = k
    return [(k, k if k in (PRE, CARD) else f"{k}、{TITLES.get(k, '')}", usage[k], BUDGET.get(k))
            for k in order]


def budget_report(lines: list[str]) -> tuple[list[str], list[str]]:
    """回傳 (輸出行, 超標警告)。"""
    rows, warns, over_list = [], [], []
    n = len(lines)
    for k, label, used, cap in chapter_usage(lines):
        over = used - cap
        rows.append(f"  - {label}：{used}/{cap}" + (f"　⚠️ 超標 +{over}" if over > 0 else ""))
        if over > 0:
            over_list.append((over, k, label))
    blanks = sum(1 for x in lines if not x.strip())
    head = ["## 行數預算（SKILL.md §4.1；空行也算）",
            f"- 全檔 {n}/{MAX_LINES} 行（目標 ≤ {SOFT_LINES}；預算合計 {sum(BUDGET.values())}）"
            f"｜距硬上限還剩 {MAX_LINES - n} 行｜空行 {blanks} 行"]
    tail = []
    if over_list:
        over_list.sort(reverse=True)
        tail.append("- 先砍（超標多的在前）：")
        for over, k, label in over_list:
            tail.append(f"  - {label} +{over} 行 → {CUT_HINT[k]}")
            warns.append(f"{label} {over + BUDGET[k]} 行 > 預算 {BUDGET[k]}（+{over}）→ {CUT_HINT[k]}")
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


def series_len(title: str):
    return next((n for k, n in SERIES_LEN.items() if k in title), None)


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


# ───────────────────────── skeleton ─────────────────────────
def valid_cc(raw: str) -> str:
    cc = raw.lower().strip()
    if not re.fullmatch(r"[a-z]{2,3}", cc):
        sys.exit(f"[錯誤] --cc 只收 2～3 個英文字母：{raw}")
    return cc


def template_body(cc: str) -> str:
    text = read_text(TPL)
    if COPY_MARK not in text:
        raise SystemExit(f"[錯誤] 樣板缺少 {COPY_MARK}：{TPL}")
    body = text.split(COPY_MARK, 1)[1].lstrip("\n")
    return body.replace("{國家}", COUNTRY_NAME.get(cc, cc.upper())).replace("{CC}", cc.upper())


def cmd_skeleton(a) -> int:
    sys.stdout.buffer.write(template_body(valid_cc(a.cc)).encode("utf-8"))
    return 0


# ───────────────────────── check ─────────────────────────
def cmd_check(a) -> int:
    cc = valid_cc(a.cc)
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
    soft_fail = warns if a.draft else fails  # 寫作中可暫緩的問題

    # 1. 時間戳
    first = lines[0] if lines else ""
    m = STAMP_RE.match(first)
    if not m:
        soft_fail.append(f"第 1 行不是時間戳樣板 `> **更新時間（Last Updated）：yyyy/MM/dd HH:mm:ss (UTC+8)**`：{first[:60]}")
    else:
        try:
            d = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if d != today:
                soft_fail.append(f"時間戳日期 {d} 不是今天（{today}）→ 全檔寫完後重取系統時間")
        except ValueError:
            soft_fail.append(f"時間戳日期不存在：{first[:60]}")
    n_stamp = sum("更新時間（Last Updated）" in line for line in lines)
    if n_stamp != 1:
        fails.append(f"時間戳出現 {n_stamp} 次（只能 1 次，不留版本歷史）")

    # 2. 主標題
    h1 = [i for i, line in enumerate(lines[:6]) if line.startswith("# ")]
    if not h1:
        fails.append("前 6 行找不到 `# ` 主標題")
    elif f"stateAnalysis {cc.upper()}" not in lines[h1[0]]:
        warns.append(f"主標題建議含「（stateAnalysis {cc.upper()}）」：{lines[h1[0]][:60]}")

    # 3. 骨架、檔頭七欄
    sec = check_skeleton(lines, fails, warns)

    # 4. 逐行：長度、零表格、禁用空話、裝飾標題、樣板殘留、連續空行
    too_long, soft, tables, tabs, fences, banned, decor, holders, dblank = [], 0, [], [], [], [], [], [], []
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
        if no > 1:  # 第 1 行由時間戳檢查負責
            holders += [f"{no}:{x}" for x in PLACEHOLDER_RE.findall(line)[:2]]
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
    if holders:
        soft_fail.append(brief(holders, "樣板殘留 `< >`（換成真實內容或 N/A（原因））"))
    if any(DEMO_MARK in x for x in lines):
        soft_fail.append(f"樣板的虛構範例「{DEMO_MARK}」還在（換成真實 REIT）")
    if dblank:
        warns.append(brief(dblank, "連續空行（浪費行數，刪掉）"))

    # 5. 全檔上限
    n_lines, n_text = len(lines), len(text)
    if n_lines > MAX_LINES:
        fails.append(f"全檔 {n_lines} 行 > {MAX_LINES}（看下方「行數預算」，依 SKILL.md §8.3 刪減順序刪到合格）")
    elif n_lines > SOFT_LINES:
        warns.append(f"全檔 {n_lines} 行 > 目標 {SOFT_LINES}")
    if n_text > MAX_CHARS:
        fails.append(f"全檔 {n_text:,} 字元 > {MAX_CHARS:,}")
    budget_lines, budget_warns = budget_report(lines)
    warns += budget_warns

    # 6. 第〇章
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
                          ("上次：", "溫度計「上次：X」"), ("NT$10 萬", "「每投入 NT$10 萬」收益換算")):
            if must not in body:
                fails.append(f"第〇章缺{why}")
        found = [mm.group(1) for x in ch if (mm := re.match(r"^###\s*(〇\.\d)", x))]
        need = [f"〇.{k}" for k in range(1, 8)]
        lost = [x for x in need if x not in found]
        if lost:
            fails.append("第〇章缺小節：" + "、".join(f"### {x}" for x in lost))
        elif [x for x in found if x in need] != need:
            fails.append("第〇章小節順序不對（應為 〇.1 → 〇.7）")
        stale = [str(s + k + 1) for k, x in enumerate(ch)
                 if "⚠" in x or "(舊)" in x or "（舊）" in x or "種子" in x]
        if stale:
            fails.append(brief(stale, "第〇章不得出現 ⚠️、(舊)、(種子)（未證實、過舊、未核對的數字不進第〇章）"))
        hits = jargon_hits(ch, s + 1, jargon_patterns(cc))
        if hits:
            fails.append(brief(hits, "第〇章禁用詞（改白話；必要時只在第一次出現處括號解釋）"))

    # 7. 每章「這段結論」「所以呢」
    no_concl = [k for k in NEED_CONCLUSION if k in sec and not any(
        "這段結論" in lines[i] for i in range(sec[k][0], min(sec[k][0] + 4, sec[k][1])))]
    no_so = [k for k in NEED_SO_WHAT if k in sec and not any(
        "所以呢" in lines[i] for i in range(max(sec[k][0], sec[k][1] - 4), sec[k][1]))]
    if no_concl:
        warns.append("這些章開頭 3 行內沒有「這段結論：」：第" + "、".join(no_concl) + "章")
    if no_so:
        warns.append("這些章結尾沒有「**所以呢**：」：第" + "、".join(no_so) + "章")

    # 8. 四個強制輸出行
    for name, pat, want in FORCED:
        locs = [i for i, line in enumerate(lines) if pat.search(line)]
        if not locs:
            fails.append(f"缺強制輸出行：`- **{name}**：…`（格式見 references/output_template.md）")
            continue
        if want in sec and not any(sec[want][0] <= i < sec[want][1] for i in locs):
            warns.append(f"強制輸出行 **{name}** 應寫在第{want}章")
        if name == "五盞燈":
            for i in locs:
                g, y, r = map(int, pat.search(lines[i]).groups())
                if g + y + r != 5:
                    fails.append(f"第 {i + 1} 行：五盞燈 {g} 綠＋{y} 黃＋{r} 紅 ≠ 5")

    # 9. 第三章逐檔、第四章小標
    check_reits(lines, sec, fails, warns)
    if "四" in sec:
        s, e = sec["四"]
        for sub in ("### 🟢 利多", "### 🔴 利空"):
            if not any(lines[i].startswith(sub) for i in range(s, e)):
                fails.append(f"第四章缺小標 `{sub}`")

    # 10. 長序列格式與長度
    blocks, errs = parse_series(lines)
    fails += errs
    for b in blocks:
        want = series_len(b["title"])
        n_m = len(b["months"])
        if want and n_m < want:
            warns.append(f"第 {b['line']} 行序列只有 {n_m} 個月（應 {want}）→ 缺口寫進第十二章")
        elif want and n_m > want:
            warns.append(brief(b["months"][:n_m - want], f"第 {b['line']} 行序列 {n_m} 個月 > {want}，刪最舊 {n_m - want} 個月"))
        if b["gaps"]:
            warns.append(brief(b["gaps"], f"第 {b['line']} 行序列缺月份（補 N/A 列）"))
    for key, label in (("七", "房價"), ("八", "租金")):
        if key in sec and not any(sec[key][0] < b["line"] <= sec[key][1] for b in blocks):
            warns.append(f"第{key}章找不到「{label} … MoM 序列」區塊（SKILL.md §5.4 格式），series 算不到")

    # 輸出
    longest = max((len(x) for x in lines), default=0)
    out(f"# check{'（draft）' if a.draft else ''} — {path}（今天 {today}｜cc={cc}）")
    out(f"- 行數 {n_lines}/{MAX_LINES}｜字元 {n_text:,}/{MAX_CHARS:,}｜最長行 {longest} 字"
        f"｜第〇章 {ch0_lines}/{CH0_MAX_LINES} 行、{ch0_chars:,}/{CH0_MAX_CHARS:,} 字元")
    return report("check", fails, warns, budget_lines)


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
        want = series_len(b["title"])
        if want and len(months) > want:
            out(f"- ⚠️ 超過 {want} 個月：寫回 <OUT> 時刪最舊 {len(months) - want} 個月（SKILL.md §5.4，序列長度固定）")
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


# ───────────────────────── selftest ─────────────────────────
BUDGET_LINE_RE = re.compile(r"^- (前置|檔頭資訊卡|(十二|十一|十|〇|一|二|三|四|五|六|七|八|九)、(.+?))：≤ (\d+) 行\s*$")


def cmd_selftest(_a) -> int:
    fails: list[str] = []
    warns: list[str] = []
    out(f"# selftest — {SKILL_DIR}")

    # 1. SKILL.md 大小與 §4.1 預算
    text = read_text(SKILL_DIR / "SKILL.md")
    if len(text) > SKILL_MAX_CHARS:
        fails.append(f"SKILL.md {len(text):,} 字元 > {SKILL_MAX_CHARS:,}（Read 工具會截斷；內容移到 references/）")
    got = {}
    for line in text.splitlines():
        m = BUDGET_LINE_RE.match(line)
        if not m:
            continue
        key = {"前置": PRE, "檔頭資訊卡": CARD}.get(m.group(1), m.group(2))
        got[key] = int(m.group(4))
        if m.group(2) and m.group(3) != TITLES.get(m.group(2)):
            fails.append(f"SKILL.md §4.1 標題「{m.group(1)}」≠ TITLES「{m.group(2)}、{TITLES.get(m.group(2))}」")
    if got != BUDGET:
        diff = [k for k in list(BUDGET) + [k for k in got if k not in BUDGET] if got.get(k) != BUDGET.get(k)]
        fails.append("SKILL.md §4.1 預算與 BUDGET 不一致：" + "、".join(
            f"{k}（SKILL {got.get(k)}／BUDGET {BUDGET.get(k)}）" for k in diff))
    total = re.search(r"合計 (\d+) 行", text)
    if not total or int(total.group(1)) != sum(BUDGET.values()):
        fails.append(f"SKILL.md「合計 X 行」應為 {sum(BUDGET.values())}")

    # 2. 樣板
    if not TPL.is_file():
        fails.append(f"找不到樣板：{TPL}")
    else:
        body = template_body("jp").splitlines()
        tf: list[str] = []
        tw: list[str] = []
        sec = check_skeleton(body, tf, tw)
        fails += [f"樣板：{x}" for x in tf]
        warns += [f"樣板：{x}" for x in tw]
        for name, _pat, want in FORCED:
            locs = [i for i, x in enumerate(body) if f"**{name}**：" in x]
            if not locs:
                fails.append(f"樣板缺強制輸出行 **{name}**")
            elif want in sec and not any(sec[want][0] <= i < sec[want][1] for i in locs):
                fails.append(f"樣板的強制輸出行 **{name}** 不在第{want}章")
        rf: list[str] = []
        check_reits(body, sec, rf, [])
        fails += [f"樣板逐檔範例：{x}" for x in rf]
        if not reit_blocks(body, sec):
            fails.append("樣板第三章沒有 `### <燈號>` 逐檔範例")
        if not any(DEMO_MARK in x for x in body):
            warns.append(f"樣板沒有虛構範例標記「{DEMO_MARK}」（check 用它偵測範例殘留）")
        over = [f"{label} {used}/{cap}" for _k, label, used, cap in chapter_usage(body) if used > cap]
        if over:
            fails.append("樣板本身就超出行數預算：" + "、".join(over))

    # 3. 國家模組與禁用詞
    refs = {p.stem for p in (SKILL_DIR / "references").glob("*.md") if p.name != TPL.name}
    for cc in COUNTRY_JARGON:
        if cc not in refs:
            fails.append(f"COUNTRY_JARGON 有 {cc}，但缺 references/{cc}.md")
    for cc in sorted(refs - set(COUNTRY_JARGON)):
        warns.append(f"references/{cc}.md 存在，但 COUNTRY_JARGON 沒有 {cc}（第〇章只套共通禁用詞）")
    for cc in sorted(refs):
        ref = read_text(SKILL_DIR / "references" / f"{cc}.md")
        for must in ("標的池", "發布行事曆", "預扣稅率", "第〇章加碼禁用詞", "五盞燈", "四階段"):
            if must not in ref:
                fails.append(f"references/{cc}.md 缺「{must}」")

    # 4. 兩份 Skill 相同
    s = SKILL_DIR.as_posix()
    twin = Path(s.replace("/.claude/", "/.agents/") if "/.claude/" in s else s.replace("/.agents/", "/.claude/"))
    if twin == SKILL_DIR or not twin.is_dir():
        warns.append(f"找不到另一份 Skill 目錄：{twin}")
    else:
        def walk(root: Path):
            return sorted(p.relative_to(root).as_posix() for p in root.rglob("*")
                          if p.is_file() and "__pycache__" not in p.parts)
        a, b = walk(SKILL_DIR), walk(twin)
        if a != b:
            fails.append("兩份 Skill 檔案清單不同：" + "、".join(sorted(set(a) ^ set(b))))
        diff = [f for f in set(a) & set(b) if not filecmp.cmp(SKILL_DIR / f, twin / f, shallow=False)]
        if diff:
            fails.append("兩份 Skill 內容不同：" + "、".join(sorted(diff)) + f"（同步到 {twin}）")

    out(f"- SKILL.md {len(text):,}/{SKILL_MAX_CHARS:,} 字元｜預算合計 {sum(BUDGET.values())} 行"
        f"｜國家模組 {', '.join(sorted(refs))}")
    return report("selftest", fails, warns)


def main() -> int:
    ap = argparse.ArgumentParser(description="stateAnalysis helper（不寫入 repo）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    k = sub.add_parser("skeleton", help="產生 AnalysisResult.md 草稿（stdout）")
    k.add_argument("--cc", required=True, help="國家代碼，如 jp、hk")
    s = sub.add_parser("series", help="計算長序列 4／5 個月規則")
    s.add_argument("--file", required=True)
    b = sub.add_parser("budget", help="逐章行數預算（寫作中隨時跑）")
    b.add_argument("--file", required=True)
    c = sub.add_parser("check", help="驗證 {cc}_state/AnalysisResult.md")
    c.add_argument("--cc", required=True, help="國家代碼，如 jp、hk")
    c.add_argument("--file", help="預設 <REPO>/{cc}_state/AnalysisResult.md")
    c.add_argument("--today", help="YYYY-MM-DD，預設今天（UTC+8）")
    c.add_argument("--draft", action="store_true", help="寫作中：時間戳、樣板殘留降為 WARN")
    sub.add_parser("selftest", help="維護自檢（SKILL、樣板、腳本、兩份 Skill 同步）")
    a = ap.parse_args()
    return {"skeleton": cmd_skeleton, "series": cmd_series, "budget": cmd_budget,
            "check": cmd_check, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
