#!/usr/bin/env python3
"""HKEXnews（披露易）downloader — 港股年報（Annual Report）/ 中期報告（Interim Report）/ 季度業績.

只用 Python 標準函式庫（Windows / Linux / macOS / Claude Code 雲端皆可）。不需要 API key。

子指令:
  lookup   <查詢>                          用股份代號 / 英文名 / 中文名找 stockId
  list     --code 02318                    列出 HKEXnews 上的年報/中報/季度業績與預定檔名（不下載）
  download --code 02318 [--annual 2 --periodic 1] [--out DIR]
  verify   [--code 02318]                  Convert2md 之後驗證 .md（存在、大小、公司名、CID）
  search   --code 01426 --from 2026-10-26 [--type all] [--keyword X] [--json]   任意公告清單（collectState 用）
  fetch    --url /listedco/.../xxx.pdf --dest <檔案路徑>                        下載單一公告 PDF（驗證檔頭）
  learn    --note "..."                    把本次學到的經驗寫進 SKILL.md §8 經驗庫並同步 .agents 鏡像
  selftest [--offline]                     自我檢查：標題解析、FY/命名、既有檔判定、SKILL.md↔CLI、鏡像、線上 API

結束碼：0 成功／1 一般錯誤／3 腳本 bug（會寫 SCRIPT_BUG 到 Log/hkexnews_error.md）
"""
from __future__ import annotations

import argparse
import html
import http.client
import json
import os
import re
import shutil
import sys
import tempfile
import time
import traceback
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

VERSION = "1.0.0"

for _s in (sys.stdout, sys.stderr):  # Windows 主控台（cp950）印中文 → 一律 UTF-8
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BASE = "https://www1.hkexnews.hk"
PREFIX_URL = BASE + "/search/prefix.do"
SEARCH_URL = BASE + "/search/titleSearchServlet.do"  # 大小寫敏感：全小寫會 404
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"

SKILL_DIR = Path(__file__).resolve().parent.parent


def _find_repo_root() -> Path:
    env = os.environ.get("HKEXNEWS_REPO")
    if env:
        return Path(env).expanduser().resolve()
    for p in SKILL_DIR.parents:
        if (p / ".git").exists() or (p / "AGENTS.md").is_file():
            return p
    return SKILL_DIR.parents[2]


REPO_ROOT = _find_repo_root()
LOG_DIR = REPO_ROOT / "Log"
ERROR_LOG = LOG_DIR / "hkexnews_error.md"
CACHE = Path(os.environ.get("HKEXNEWS_CACHE_DIR") or (Path.home() / ".cache" / "hkexnews"))
MANIFEST = CACHE / "last_run.json"
MIN_PDF_BYTES = 10 * 1024

# 文件分類代碼（https://www1.hkexnews.hk/ncms/script/eds/tiertwo_e.json，2026-11 實測）
#   t1code 40000 Financial Statements/ESG：40100 Annual Report、40200 Interim/Half-Year Report、40300 Quarterly Report
#   t1code 10000 Announcements and Notices（t2Gcode 3 Financial Information）：13300 Final Results、13400 Interim Results、13600 Quarterly Results
CAT = {
    "40100": ("40000", "Annual Report", "年報"),
    "40200": ("40000", "Interim/Half-Year Report", "中期報告"),
    "40300": ("40000", "Quarterly Report", "季度報告"),
    "13300": ("10000", "Final Results", "全年業績公告"),
    "13400": ("10000", "Interim Results", "中期業績公告"),
    "13600": ("10000", "Quarterly Results", "季度業績公告"),
}
REPORTS = ("40100", "40200", "40300")
RESULTS = ("13300", "13400", "13600")
# search --type 預設組合：(t1code, t2Gcode, t2code)；-2 = 不限（填 -1 在部分組合會回 0 筆，一律用 -2）
SEARCH_TYPES = {
    "all": ("-2", "-2", "-2"),
    "announcement": ("10000", "-2", "-2"),
    "financial": ("10000", "3", "-2"),
    "annual": ("40000", "-2", "40100"),
    "interim": ("40000", "-2", "40200"),
    "quarterly-report": ("40000", "-2", "40300"),
    "final-results": ("10000", "-2", "13300"),
    "interim-results": ("10000", "-2", "13400"),
    "quarterly-results": ("10000", "-2", "13600"),
    "reports": ("40000", "-2", "-2"),
    "circular": ("20000", "-2", "-2"),
    "monthly-return": ("51500", "-2", "-2"),
    "next-day": ("50000", "-2", "-2"),
}
MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august", "september",
     "october", "november", "december"], 1)}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
MONTHS["sept"] = 9
OBS: list[str] = []  # 本次執行觀察到、值得寫回 skill 的現象（LEARN? 候選）


class HkexError(Exception):
    def __init__(self, kind: str, msg: str, *, status: int | None = None, endpoint: str | None = None,
                 detail: str | None = None):
        super().__init__(msg)
        self.kind, self.status, self.endpoint, self.detail = kind, status, endpoint, detail


def observe(msg: str) -> None:
    if msg not in OBS:
        OBS.append(msg)


# ---------------------------------------------------------------- HTTP
MIN_INTERVAL = float(os.environ.get("HKEXNEWS_MIN_INTERVAL", "0.8"))  # 秒/請求（禮貌節流）
_last = [0.0]
STATS = {"requests": 0, "retries": 0}


def http_get(url: str, params: dict | None = None, retries: int = 4, timeout: int = 60,
             referer: str | None = None) -> tuple[bytes, str]:
    full = url + ("?" + urllib.parse.urlencode(params) if params else "")
    headers = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    if referer:
        headers["Referer"] = referer
    endpoint = urllib.parse.urlsplit(url).path
    err = None
    for i in range(retries):
        wait = _last[0] + MIN_INTERVAL - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.monotonic()
        STATS["requests"] += 1
        try:
            with urllib.request.urlopen(urllib.request.Request(full, headers=headers), timeout=timeout) as r:
                return r.read(), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            body = e.read()[:300].decode("utf-8", "replace")
            if e.code == 404:
                raise HkexError("NOT_FOUND", f"HTTP 404 {endpoint}", status=404, endpoint=endpoint, detail=body) from None
            if e.code in (403, 407) and "agent-proxy" in body.lower():
                raise HkexError("PROXY_BLOCKED", f"雲端代理擋下 {endpoint}", status=e.code, endpoint=endpoint,
                                detail=body) from None
            if e.code in (403, 429) or e.code >= 500:
                err = f"HTTP {e.code} {body[:150]}"
                STATS["retries"] += 1
                time.sleep(min(60, 5 * 2 ** i))
                continue
            raise HkexError("HTTP_ERROR", f"HTTP {e.code}", status=e.code, endpoint=endpoint, detail=body) from None
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException) as e:
            err = str(e)
            STATS["retries"] += 1
            time.sleep(min(30, 3 * 2 ** i))
    raise HkexError("NETWORK", f"已重試 {retries} 次仍失敗：{err}", endpoint=endpoint)


# ---------------------------------------------------------------- 股份代號 → stockId
def norm_code(code: str) -> str:
    c = code.strip().upper().removesuffix(".HK").removesuffix("-HK")
    return c.zfill(5) if c.isdigit() else c


def _prefix(name: str, lang: str = "EN", typ: str = "A") -> list[dict]:
    data, _ = http_get(PREFIX_URL, {"callback": "c", "lang": lang, "type": typ, "name": name, "market": "SEHK"})
    t = data.decode("utf-8", "replace")
    try:
        return json.loads(t[t.index("(") + 1:t.rindex(")")]).get("stockInfo") or []
    except ValueError:
        raise HkexError("API_ERROR", "prefix.do 回應不是 JSONP", endpoint="/search/prefix.do", detail=t[:200]) from None


def resolve_stock(query: str) -> dict:
    """回傳 {stockId, code, name_en, name_zh}；先查快取。代號查不到在上市清單（type=A）時再查已除牌（type=I）。"""
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_p = CACHE / "stocks.json"
    try:
        cache = json.loads(cache_p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cache = {}
    q = norm_code(query) if query.strip().isdigit() else query.strip()
    if q in cache:
        return cache[q]
    hit = None
    if q.isdigit():
        for typ in ("A", "I"):
            cands = [x for x in _prefix(q, "EN", typ) if x.get("code") == q]
            if cands:
                hit = cands[0]
                if typ == "I":
                    observe(f"{q} 不在上市清單（type=A），在已除牌清單（type=I）找到")
                break
    else:
        cands = _prefix(q, "EN") or _prefix(q, "ZH")
        if len(cands) == 1:
            hit = cands[0]
        elif cands:
            lines = "\n".join(f"  {x['code']}  {x['name']}" for x in cands[:15])
            raise HkexError("AMBIGUOUS", f"「{query}」對到多檔，請改用 5 碼股份代號：\n{lines}")
    if not hit:
        raise HkexError("NOT_FOUND", f"HKEXnews 找不到「{query}」（港股請用 5 碼代號，如 02318）")
    zh = next((x["name"] for x in _prefix(hit["code"], "ZH") if x.get("code") == hit["code"]), "")
    info = {"stockId": hit["stockId"], "code": hit["code"], "name_en": hit["name"], "name_zh": zh}
    cache[q] = info
    cache[hit["code"]] = info
    cache_p.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


# ---------------------------------------------------------------- 搜尋
def search(stock_id: int, t1: str, t2g: str, t2: str, d_from: date, d_to: date, lang: str = "EN",
           rows: int = 200) -> list[dict]:
    params = {"sortDir": "0", "sortByOptions": "DateTime", "category": "0", "market": "SEHK",
              "stockId": str(stock_id), "documentType": "-1", "fromDate": d_from.strftime("%Y%m%d"),
              "toDate": d_to.strftime("%Y%m%d"), "lang": lang, "searchType": "1", "rowRange": str(rows),
              "t1code": t1, "t2Gcode": t2g, "t2code": t2}
    data, _ = http_get(SEARCH_URL, params)
    try:
        j = json.loads(data.decode("utf-8"))
    except ValueError:
        raise HkexError("API_ERROR", "titleSearchServlet 回應不是 JSON", endpoint="/search/titleSearchServlet.do",
                        detail=data[:200].decode("utf-8", "replace")) from None
    res = j.get("result")
    out = json.loads(res) if res and res != "null" else []
    if j.get("hasNextRow"):
        observe(f"搜尋結果超過 rowRange={rows}（stockId {stock_id}, t2code {t2}），可能漏件 → 縮短期間或加大 rowRange")
    for x in out:
        x["TITLE"] = html.unescape(x.get("TITLE") or "").replace("\n", " ").strip()
        x["LONG_TEXT"] = html.unescape(x.get("LONG_TEXT") or "")
        x["_date"] = datetime.strptime(x["DATE_TIME"], "%d/%m/%Y %H:%M")
        x["_docno"] = Path(x.get("FILE_LINK") or "").stem
    return out


# ---------------------------------------------------------------- 標題解析與期別
_DATE_RES = [
    re.compile(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\.?,?\s+(20\d\d)"),   # 31 December 2025
    re.compile(r"([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d\d)"),   # December 31, 2025
]


def _mk(y: int, m: int, d: int) -> date | None:
    try:
        return date(y, m, d)
    except ValueError:
        return None


def title_dates(title: str) -> list[date]:
    found: list[tuple[int, date]] = []
    for i, rx in enumerate(_DATE_RES):
        for m in rx.finditer(title):
            if i == 0:
                d, mon, y = m.group(1), m.group(2), m.group(3)
            else:
                mon, d, y = m.group(1), m.group(2), m.group(3)
            mm = MONTHS.get(mon.lower())
            if mm and (dt := _mk(int(y), mm, int(d))):
                found.append((m.start(), dt))
    return [d for _, d in sorted(found)]


def title_part(title: str) -> str | None:
    """Q1 / Q3 / H1 / FY；認不出 → None。順序重要：「FIRST THREE QUARTERS」要先於「FIRST QUARTER」。"""
    t = title.lower()
    if re.search(r"nine months|three quarters|third quarter|第三季|前三季", t):
        return "Q3"
    if re.search(r"six months|interim|half[- ]year|中期|半年", t):
        return "H1"
    if re.search(r"three months|first quarter|第一季", t):
        return "Q1"
    if re.search(r"second quarter|第二季", t):
        return "H1"
    if re.search(r"year ended|annual|final results|全年|年度", t):
        return "FY"
    return None


def title_years(title: str) -> list[int]:
    t = re.sub(r"\d{1,2}\s+[A-Za-z]+\s+20\d\d|[A-Za-z]+\s+\d{1,2},?\s+20\d\d", " ", title)
    ys = [int(y) for y in re.findall(r"(?<!\d)(20\d\d)(?!\d)", t)]
    ys += [2000 + int(y) for y in re.findall(r"20\d\d\s*/\s*(\d\d)(?!\d)", t)]
    return sorted(set(ys))


def _month_end(y: int, m: int) -> date:
    y2, m2 = (y + 1, 1) if m == 12 else (y, m + 1)
    return date(y2, m2, 1) - timedelta(days=1)


def _latest_month_end(months: set[int], before: date) -> date:
    y, m = before.year, before.month
    for _ in range(36):
        if m in months and _month_end(y, m) <= before:
            return _month_end(y, m)
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    return before


def _shift(m: int, k: int) -> int:
    return (m - 1 + k) % 12 + 1


def infer_fye(docs: list[dict]) -> tuple[int, str]:
    """決算月：① 全年/年報標題的 year ended 日期 ② 中期標題的 six months ended +6 ③ 年報刊發月往回 2–4 個月的季末 ④ 12。"""
    votes: dict[int, int] = {}
    for d in docs:
        ds = title_dates(d["TITLE"])
        if not ds:
            continue
        part = title_part(d["TITLE"])
        if d["_cat"] in ("40100", "13300") and part in ("FY", None):
            votes[ds[-1].month] = votes.get(ds[-1].month, 0) + 2
        elif d["_cat"] in ("40200", "13400") and part == "H1":
            votes[_shift(ds[-1].month, 6)] = votes.get(_shift(ds[-1].month, 6), 0) + 1
    if votes:
        return max(votes, key=votes.get), "標題日期"
    ann = [d for d in docs if d["_cat"] == "40100"]
    for d in ann:
        r = d["_date"].month
        for k in (2, 3, 4):
            q = _shift(r, -k)
            if q in (3, 6, 9, 12):
                votes[q] = votes.get(q, 0) + 1
                break
    if votes:
        m = max(votes, key=votes.get)
        if m != 12:  # 12 月決算是常態；非 12 月又沒有標題日期佐證才值得人工確認
            observe(f"決算月由年報刊發月份推估為 {m} 月（標題沒有期末日）→ 確認後若不對用 --fye-month 指定")
        return m, "年報刊發月推估"
    observe("找不到年報可推估決算月，預設 12 月 → 若不對用 --fye-month 指定")
    return 12, "預設"


def fy_of(pe: date, fye: int) -> int:
    return pe.year if pe.month <= fye else pe.year + 1


def classify(doc: dict, fye: int) -> dict:
    """算出 period_end、part（FY/H1/Q1/Q3）、FY，與檔名 base。"""
    cat, title = doc["_cat"], doc["TITLE"]
    part = title_part(title)
    if cat in ("40100", "13300"):
        part = "FY"
    elif cat in ("40200", "13400"):
        part = "H1"
    elif part in (None, "FY"):
        part = None
    ds = title_dates(title)
    release = doc["_date"].date()
    how = "標題日期"
    pe = ds[-1] if ds and ds[-1] < release else None
    if pe is None:
        how = "刊發日推估"
        months = {"FY": {fye}, "H1": {_shift(fye, 6)}, "Q1": {_shift(fye, 3)}, "Q3": {_shift(fye, 9)},
                  None: {_shift(fye, 3), _shift(fye, 9)}}[part]
        pe = _latest_month_end(months, release - timedelta(days=14))
        ys = title_years(title)
        if ys and pe.year not in ys and fy_of(pe, fye) not in ys:
            observe(f"標題年份 {ys} 與推估期末 {pe} 不符：「{title}」（{doc['_docno']}）→ 檢查決算月或標題規則")
    if part is None:
        k = (pe.month - fye) % 12
        part = {3: "Q1", 6: "H1", 9: "Q3", 0: "FY"}.get(k)
        if part is None:
            observe(f"季度業績期末 {pe} 不在季末（決算月 {fye}）：「{title}」")
            part = f"Q{max(1, min(3, k // 3))}"
    fy = fy_of(pe, fye)
    t = doc["_ticker"]
    if cat == "40100":
        base = f"{t}_AnnualReport_{fy}"
    elif cat == "13300":
        base = f"{t}_AnnualReport_{fy}_Results"
    elif cat == "40200":
        base = f"{t}_Quarter_{fy}H1"
    elif part == "H1":
        base = f"{t}_Quarter_{fy}H1_Results"
    elif part == "FY":
        base = f"{t}_AnnualReport_{fy}_Results"
    else:
        base = f"{t}_Quarter_{fy}{part}"
    doc.update(_pe=pe, _part=part, _fy=fy, _fye=fye, _base=base, _how=how)
    return doc


# 同一期別多份候選時，排除附屬文件（債券版、簡報、更正、股息表格…）
_PENALTY = re.compile(r"debt|presentation|\bora\b|supplement|clarification|correction|corrigend|erratum|"
                      r"revised|dividend|announcement form|monthly return|summary|abstract|esg|sustainab", re.I)


def _score(doc: dict) -> tuple:
    return (bool(_PENALTY.search(doc["TITLE"])), doc["_date"])


def pick(docs: list[dict]) -> list[dict]:
    """同一 (分類, 期末) 只留一份：先排除附屬文件，再取最早刊發（原始版）。"""
    by: dict[tuple, list[dict]] = {}
    for d in docs:
        by.setdefault((d["_cat"], d["_pe"]), []).append(d)
    out = []
    for k, ds in by.items():
        ds.sort(key=_score)
        if len(ds) > 1 and _score(ds[0])[0] == _score(ds[1])[0]:  # 附屬文件規則分不出來才值得記
            observe(f"{CAT[k[0]][1]} 期末 {k[1]} 有 {len(ds)} 份：選「{ds[0]['TITLE'][:60]}」，略過 "
                    + "；".join(f"「{x['TITLE'][:50]}」" for x in ds[1:3]))
        out.append(ds[0])
    return sorted(out, key=lambda d: (d["_pe"], d["_date"]), reverse=True)


def collect(stock: dict, days: int, lang: str, fye_month: int | None) -> tuple[list[dict], int, str]:
    today = date.today()
    d_from = today - timedelta(days=days)
    docs: list[dict] = []
    for cat, (t1, _n, _z) in CAT.items():
        rows = search(stock["stockId"], t1, "-2", cat, d_from, today, lang)
        for r in rows:
            if (r.get("FILE_TYPE") or "").upper() != "PDF":
                observe(f"{cat} 有非 PDF 文件（{r.get('FILE_TYPE')}）：「{r['TITLE'][:60]}」→ 略過")
                continue
            r["_cat"], r["_ticker"] = cat, stock["code"]
            docs.append(r)
    if lang == "EN" and not any(d["_cat"] in REPORTS for d in docs):
        observe(f"{stock['code']} 英文搜尋沒有任何年報/中報 → 改用中文（lang=ZH）")
        return collect(stock, days, "ZH", fye_month)
    fye, how = (fye_month, "--fye-month") if fye_month else infer_fye(docs)
    for d in docs:
        classify(d, fye)
    return pick(docs), fye, how + ("" if lang == "EN" else "；中文版")


def select(docs: list[dict], annual_n: int, periodic_n: int, latest: bool) -> list[dict]:
    ann = [d for d in docs if d["_cat"] == "40100"][:annual_n]
    per = [d for d in docs if d["_cat"] in ("40200", "40300")][:periodic_n]
    sel = ann + per
    if latest:
        newest_pe = max((d["_pe"] for d in docs if d["_cat"] in REPORTS), default=date.min)
        newer = [d for d in docs if d["_cat"] in RESULTS and d["_pe"] > newest_pe]
        # 季度報告（40300）與季度業績（13600）同期別：已有報告就不要業績
        if newer:
            sel.append(newer[0])
    return sel


# ---------------------------------------------------------------- 既有檔判定
CN_DIGITS = str.maketrans("〇零一二三四五六七八九", "00123456789")
DISCLAIMER = re.compile(r"contents of this announcement|本公告的?內容|对本公告的内容|對本公告的內容", re.I)
KIND_PATTERNS = [
    ("annual", re.compile(r"annual report|年報|年度報告|年度报告", re.I)),
    ("interim", re.compile(r"interim report|中期報告|中期报告|半年度報告|半年度报告", re.I)),
    ("quarterly", re.compile(r"quarterly report|季度報告|季度报告", re.I)),
]
ACCEPT = {"40100": {"annual"}, "40200": {"interim"}, "40300": {"quarterly", "results"},
          "13300": {"results", "annual"}, "13400": {"results", "interim"}, "13600": {"results", "quarterly"}}


def doc_kind(path: Path, head_chars: int = 8000) -> str | None:
    """.md 實際是哪種文件：'results'（公告：前 4000 字有港交所免責聲明）/'annual'/'interim'/'quarterly'；PDF 或認不出 → None。"""
    if path.suffix.lower() != ".md":
        return None
    try:
        with path.open(encoding="utf-8", errors="replace") as f:
            head = f.read(head_chars)
    except OSError:
        return None
    if DISCLAIMER.search(head[:4000]):
        return "results"
    best = None
    for kind, pat in KIND_PATTERNS:
        m = pat.search(head)
        if m and (best is None or m.start() < best[1]):
            best = (kind, m.start())
    return best[0] if best else None


def _same_doc(cat: str, p: Path) -> bool:
    k = doc_kind(p)
    return k is None or k in ACCEPT[cat]


def aliases(base: str) -> list[str]:
    """同一期別在 repo 裡可能出現的檔名（新命名、collectStk 舊命名、手動命名）。"""
    m = re.match(r"^(.+?)_(AnnualReport|Quarter)_(\d{4})(H1|Q[1-4])?(_Results|_HKEX)?$", base)
    if not m:
        return [base]
    t, kind, fy, part, res = m.group(1), m.group(2), m.group(3), m.group(4) or "", m.group(5) or ""
    out = [base, base + "_HKEX"]  # _HKEX = 上次因同名檔是別種文件而另存
    if kind == "AnnualReport":
        full = [f"{t}_AnnualReport_{fy}", f"{t}_annual_{fy}", f"{t}_Annual_{fy}"]
        out += full + ([f"{t}_AnnualResults_{fy}", f"{t}_FinalResults_{fy}"] if res else [])
    elif part == "H1":
        full = [f"{t}_Quarter_{fy}H1", f"{t}_Quarter_{fy}Q2", f"{t}_quarter_{fy}Q2", f"{t}_QuarterlyReport_{fy}Q2",
                f"{t}_interim_{fy}", f"{t}_Interim_{fy}", f"{t}_InterimReport_{fy}"]
        out += full + ([f"{t}_InterimResults_{fy}"] if res else [])
    else:
        out += [f"{t}_Quarter_{fy}{part}", f"{t}_quarter_{fy}{part}", f"{t}_QuarterlyReport_{fy}{part}"]
    return list(dict.fromkeys(out))


_ORIG_KW = {"40100": re.compile(r"年報|年度報告|annual ?report", re.I),
            "13300": re.compile(r"年報|年度報告|annual|全年業績|年度業績", re.I),
            "40200": re.compile(r"中期報告|半年度報告|interim ?report", re.I),
            "13400": re.compile(r"中期|interim", re.I),
            "40300": re.compile(r"季度|quarter", re.I), "13600": re.compile(r"季度|quarter", re.I)}


def _years_in_name(stem: str) -> set[int]:
    # 「20250828二零二五年」：中文數字年份前後加空白再轉，免得和刊發日黏成 12 位數
    s = re.sub(r"[〇零一二三四五六七八九]{4}", lambda m: " " + m.group().translate(CN_DIGITS) + " ", stem)
    s = re.sub(r"(?<!\d)20\d{6}(?!\d)|(?<!\d)20\d{4}(?!\d)", " ", s)  # 去掉 yyyyMMdd / yyyyMM 刊發日前綴
    return {int(y) for y in re.findall(r"(?<!\d)(20\d\d)(?!\d)", s)}


def existing_cover(out: Path, doc: dict) -> Path | None:
    """資料夾內已涵蓋該期別的檔：①同名或別名（.md 要內容種類相符）②HKEX 原始編號檔名（如 2026042200516.md）
    ③中文原檔名（如 20260423_2025年年報.md、20250828二零二五年中期報告.md）。"""
    if not out.is_dir():
        return None
    cat = doc["_cat"]
    files = {p.name.lower(): p for p in out.iterdir() if p.is_file() and p.suffix.lower() in (".md", ".pdf")}
    for b in aliases(doc["_base"]):
        for ext in (".md", ".pdf"):
            hit = files.get((b + ext).lower())
            if hit and _same_doc(cat, hit):
                return hit
    for p in files.values():
        if p.stem == doc["_docno"] or p.stem.startswith(doc["_docno"] + "_"):
            return p
    # 非 12 月決算的會計年度跨兩個年曆年（「2025/2026 Annual Report」）→ 前一年也算
    fy_labels = {doc["_fy"]} | ({doc["_fy"] - 1} if doc.get("_fye", 12) != 12 else set())
    for p in files.values():
        st = p.stem
        if re.match(r"^\d{5}_", st) or not _ORIG_KW[cat].search(st):
            continue
        if cat in ("40100", "13300") and re.search(r"中期|interim|季度|quarter", st, re.I):
            continue
        if cat in ("40100", "40200", "40300") and re.search(r"業績|results|公告", st, re.I):
            continue  # 業績公告不能頂替完整報告
        if _years_in_name(st) & fy_labels and _same_doc(cat, p):
            return p
    return None


def name_taken_by_other(out: Path, doc: dict) -> Path | None:
    p = out / f"{doc['_base']}.md"
    return p if p.is_file() and not _same_doc(doc["_cat"], p) else None


# ---------------------------------------------------------------- 資料夾 / 下載
def find_company_folder(code: str) -> list[Path]:
    """repo 根目錄下「代號開頭、下一字不是數字」的資料夾（02318 → 02318中國平安）。"""
    return [p for p in REPO_ROOT.iterdir() if p.is_dir() and p.name.startswith(code)
            and not p.name[len(code):len(code) + 1].isdigit()]


def _safe(s: str) -> str:
    return re.sub(r'[\s<>:"/\\|?*]', "", unicodedata.normalize("NFKC", s))


def resolve_out(a, stock: dict) -> tuple[Path, bool]:
    if getattr(a, "out", None):
        return Path(a.out).expanduser().resolve(), False
    cands = sorted(set(find_company_folder(stock["code"])))
    if len(cands) == 1:
        return cands[0], False
    if len(cands) > 1:
        raise HkexError("AMBIGUOUS", "repo 內有多個以「%s」開頭的資料夾：%s → 用 --out 指定"
                        % (stock["code"], ", ".join(p.name for p in cands)))
    if getattr(a, "no_create", False):
        raise HkexError("NOT_FOUND", f"repo 內找不到以「{stock['code']}」開頭的公司資料夾，請用 --out 指定")
    return REPO_ROOT / f"{stock['code']}{_safe(stock['name_zh'] or stock['name_en'])}", True


def _valid_pdf(data: bytes) -> str | None:
    if not data.startswith(b"%PDF"):
        head = data[:200].decode("utf-8", "replace").lower()
        return "不是 PDF（" + ("HTML 封鎖頁" if "<html" in head else "檔頭不是 %PDF") + "）"
    if len(data) < MIN_PDF_BYTES:
        return f"PDF 太小（{len(data)} bytes < 10KB）"
    return None


def save_pdf(link: str, dest: Path) -> tuple[str, str]:
    url = link if link.startswith("http") else BASE + link
    if urllib.parse.urlsplit(url).hostname not in ("www1.hkexnews.hk", "www.hkexnews.hk"):
        return "failed", f"只接受 hkexnews.hk 網址：{url}"
    data, ctype = http_get(url, timeout=300, referer=BASE + "/search/titlesearch.xhtml")
    if (bad := _valid_pdf(data)) is not None:
        return "failed", f"{bad}；content-type={ctype}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False, suffix=".part") as tf:
        tf.write(data)
    umask = os.umask(0)
    os.umask(umask)
    os.chmod(tf.name, 0o666 & ~umask)
    Path(tf.name).replace(dest)
    return "downloaded", f"{len(data) / 1024:.0f} KB"


def download_doc(doc: dict, out: Path, force: bool) -> dict:
    base = doc["_base"]
    other = name_taken_by_other(out, doc)
    r = {"file": f"{base}.pdf", "status": "", "note": ""}
    if not force and (hit := existing_cover(out, doc)):
        r.update(status="skipped", note=f"已存在 {hit.name}", cover=hit.name)
        return r
    if other is not None:  # 同名檔其實是別種文件（如業績公告存成報告名）→ 另存，不覆蓋
        base += "_HKEX"
        r.update(file=f"{base}.pdf", note=f"{other.name} 是別種文件，改存 {base}.pdf；")
        observe(f"{other.name} 內容種類與檔名不符（{doc_kind(other)}），新檔另存 {base}.pdf")
    st, note = save_pdf(doc["FILE_LINK"], out / f"{base}.pdf")
    r.update(status=st, note=r["note"] + note, cover=f"{base}.pdf" if st == "downloaded" else None)
    if st == "failed":
        observe(f"下載驗證失敗 {doc['FILE_LINK']}：{note}")
    return r


def _row(d: dict) -> str:
    return (f"{d['_date']:%Y-%m-%d}  {d['_docno']}  {d['_cat']} {CAT[d['_cat']][2]:<6} 期末 {d['_pe']}"
            f"（{d['_how']}）→ {d['_base']}  | {d['TITLE'][:90]}")


# ---------------------------------------------------------------- logs
ERROR_HEADER = """# HKEXnews 錯誤報告

> 由 `.claude/skills/hkexnews/scripts/hkexnews.py` 自動寫入，最新在最上面（最多保留 50 筆）。
> 種類：`NETWORK`、`PROXY_BLOCKED`（雲端代理擋 host）、`HTTP_ERROR`、`API_ERROR`（回應格式變了）、`NOT_FOUND`、`AMBIGUOUS`、`SCRIPT_BUG`（腳本本身有錯 → AI 依 SKILL.md §9 自我修正）、`SELFTEST_FAIL`。

<!-- entries -->
"""


def log_error(e: HkexError | None, argv: list[str], *, kind: str | None = None, detail: str = "",
              tb: str | None = None) -> Path:
    kind = kind or (e.kind if e else "SCRIPT_BUG")
    L = [f"## {datetime.now():%Y-%m-%d %H:%M:%S} — {kind}", "",
         f"- 指令：`hkexnews.py {' '.join(argv)}`（script v{VERSION}，Python {sys.version.split()[0]}，{sys.platform}）"]
    if e is not None:
        L.append(f"- 錯誤：{e}")
        if e.endpoint:
            L.append(f"- 端點：`{e.endpoint}`")
        if e.status is not None:
            L.append(f"- 狀態碼：{e.status}")
        if e.detail:
            L.append(f"- 回應：`{str(e.detail).strip()[:300]}`")
    if detail:
        L.append(f"- 說明：{detail}")
    if kind == "PROXY_BLOCKED":
        L.append("- 處理：雲端環境網路政策沒放行 `www1.hkexnews.hk` → 讀 `/root/.ccr/README.md`；"
                 "本次改走 collectStk §7.3 港股 ②③（富途、官網 IR）或 MCP（firecrawl_scrape 抓 PDF 連結）。")
    elif kind == "NETWORK":
        L.append("- 處理：重跑一次；仍失敗 → 改走富途 `{5碼}-HK/announcement` / 官網 IR，並在回報寫明。")
    elif kind == "API_ERROR":
        L.append("- 處理：HKEXnews 回應格式可能改版 → 用 curl 看實際回應，修 `scripts/hkexnews.py` 並補 selftest（§9）。")
    elif kind in ("SCRIPT_BUG", "SELFTEST_FAIL"):
        L.append("- 處理：**AI 必須依 SKILL.md §9 自我修正**：修腳本／SKILL.md → `hkexnews.py selftest` 全過 → "
                 "同步 `.agents/skills/hkexnews/` → §10 變更紀錄記一筆 → commit & push。")
    if tb:
        L += ["", "```text", tb.strip()[-3000:], "```"]
    entry = "\n".join(L) + "\n"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    old = ERROR_LOG.read_text(encoding="utf-8") if ERROR_LOG.is_file() else ERROR_HEADER
    if "<!-- entries -->" not in old:
        old = ERROR_HEADER + old
    head, _, rest = old.partition("<!-- entries -->\n")
    entries = [x for x in re.split(r"(?m)^(?=## \d{4}-\d{2}-\d{2} )", rest) if x.strip()][:49]
    ERROR_LOG.write_text(head + "<!-- entries -->\n" + entry + "\n" + "\n".join(x.rstrip() + "\n" for x in entries),
                         encoding="utf-8")
    return ERROR_LOG


def write_summary(lines: list[str]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    p = LOG_DIR / f"hkexnews_Summary_{date.today():%Y%m%d}.md"
    head = "" if p.is_file() else f"# HKEXnews 執行報告 {date.today():%Y-%m-%d}\n\n"
    with p.open("a", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n\n")
    return p


def _obs_lines() -> list[str]:
    if not OBS:
        return []
    return ["- LEARN? 候選（AI 依 SKILL.md §9 判斷：寫進經驗庫、修腳本或忽略）："] + [f"  - {o}" for o in OBS]


# ---------------------------------------------------------------- verify
CID_RE = re.compile(r"\(cid:\d+\)")


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "").lower()


def verify_md(md: Path, stock: dict) -> tuple[bool, str]:
    if not md.is_file():
        return False, "尚未轉成 .md（PDF 還在 → Convert2md 未跑或失敗）"
    size = md.stat().st_size
    if size < MIN_PDF_BYTES:
        return False, f".md 太小（{size} bytes）"
    text = md.read_text(encoding="utf-8", errors="replace")
    cid = len(CID_RE.findall(text))
    if cid >= 50:
        return False, f"CID 亂碼 {cid} 次 → 改抓另一語言版（--lang）"
    head = _norm(text[:30000])
    en = _norm(stock["name_en"])
    names = [en, en.split(" ")[0] if len(en.split(" ")[0]) >= 4 else "", _norm(stock["name_zh"]),
             stock["code"].lstrip("0"), stock["code"]]
    if not any(n and len(n) >= 2 and n in head for n in names):
        return False, "前 3 萬字找不到公司名／股份代號 → 檔案可能抓錯"
    return True, f"OK（{size / 1024:.0f} KB，CID {cid}）"


# ---------------------------------------------------------------- learn（經驗回寫）
LEARN_START, LEARN_END = "<!-- LEARN:START -->", "<!-- LEARN:END -->"


def sync_mirror() -> Path | None:
    """把 .claude/skills/hkexnews 整份複製到 .agents/skills/hkexnews（Gemini 用）。"""
    src = REPO_ROOT / ".claude/skills/hkexnews"
    dst = REPO_ROOT / ".agents/skills/hkexnews"
    if not src.is_dir() or not (REPO_ROOT / ".agents").is_dir():
        return None
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".env", "__pycache__", "*.pyc"))
    return dst


def _cmd_learn(a) -> int:
    p = REPO_ROOT / ".claude/skills/hkexnews/SKILL.md"
    text = p.read_text(encoding="utf-8")
    if LEARN_START not in text or LEARN_END not in text:
        raise HkexError("API_ERROR", f"{p} 找不到 {LEARN_START}/{LEARN_END} 標記（§8 經驗庫被改壞）")
    note = " ".join(a.note.split())
    if len(note) < 8:
        raise HkexError("API_ERROR", "--note 太短：寫清楚「什麼情況 → 怎麼做／結果」")
    head, _, rest = text.partition(LEARN_START + "\n")
    body, _, tail = rest.partition(LEARN_END)
    if note in body:
        print(f"[hkexnews] 經驗庫已有同樣內容，未重複寫入")
        return 0
    line = f"- [{date.today():%Y-%m}] {note}\n"
    p.write_text(head + LEARN_START + "\n" + body + line + LEARN_END + tail, encoding="utf-8")
    m = sync_mirror()
    print(f"[hkexnews] 已寫入 {p.relative_to(REPO_ROOT)} §8：{line.strip()}")
    if m:
        print(f"[hkexnews] 已同步鏡像 {m.relative_to(REPO_ROOT)}")
    return 0


# ---------------------------------------------------------------- selftest
def _cmd_selftest(a, parser: argparse.ArgumentParser) -> int:
    fails: list[str] = []

    def check(name: str, cond: bool, info: str = "") -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {name}{('  — ' + info) if info and not cond else ''}")
        if not cond:
            fails.append(f"{name}：{info}")

    def mk(cat: str, title: str, dt: str, t: str = "02318", no: str = "2026000000001") -> dict:
        return {"_cat": cat, "TITLE": title, "_date": datetime.strptime(dt, "%Y-%m-%d %H:%M"), "_ticker": t,
                "_docno": no, "FILE_LINK": f"/listedco/listconews/sehk/x/{no}.pdf"}

    print("[selftest] 標題解析（2026-11 實際標題）")
    check("title_dates 31 DECEMBER 2025", title_dates("ANNUAL RESULTS ANNOUNCEMENT FOR THE YEAR ENDED 31 DECEMBER 2025")
          == [date(2025, 12, 31)])
    check("title_dates June 30, 2026", title_dates("ANNOUNCEMENT OF INTERIM RESULTS FOR THE SIX MONTHS ENDED JUNE 30, 2026")
          == [date(2026, 6, 30)])
    check("title_dates FROM…TO 取最後", title_dates("INTERIM RESULTS ANNOUNCEMENT FOR THE PERIOD FROM 1 JANUARY 2026 "
                                                 "TO 30 JUNE 2026")[-1] == date(2026, 6, 30))
    for t, want in (("RESULTS FOR THE FIRST THREE QUARTERS OF 2026", "Q3"), ("RESULTS FOR THE FIRST QUARTER OF 2026", "Q1"),
                    ("INSIDE INFORMATION - THIRD QUARTERLY REPORT OF 2026", "Q3"),
                    ("Announcement of Unaudited Results for the Three Months Ended March 31, 2026", "Q1"),
                    ("Announcement of Unaudited Results for the Nine Months Ended September 30, 2026", "Q3"),
                    ("2026 FIRST QUARTERLY REPORT", "Q1"), ("2026 INTERIM RESULTS", "H1")):
        check(f"title_part {want}：{t[:40]}", title_part(t) == want, f"得到 {title_part(t)}")
    check("title_years 2025/2026", title_years("2025/2026 Annual Report") == [2025, 2026])

    print("[selftest] 決算月與 FY 命名")
    dec = [mk("40100", "Annual Report 2025", "2026-04-28 18:40"), mk("13300", "2025 ANNUAL RESULTS", "2026-03-26 16:30")]
    check("12 月決算（年報刊發 4 月推估）", infer_fye(dec)[0] == 12)
    mar = [mk("40100", "2025/2026 Annual Report", "2026-07-16 20:22", "02633"),
           mk("13300", "ANNUAL RESULTS ANNOUNCEMENT FOR THE YEAR ENDED 31 MARCH 2026", "2026-06-23 19:42", "02633")]
    check("3 月決算（標題 year ended 31 MARCH）", infer_fye(mar)[0] == 3)
    cases = [
        (mk("40100", "Annual Report 2025", "2026-04-28 18:40"), 12, "02318_AnnualReport_2025"),
        (mk("40200", "Interim Report 2026", "2026-09-10 06:08"), 12, "02318_Quarter_2026H1"),
        (mk("13600", "Announcement of Unaudited Results for the Nine Months Ended September 30, 2026",
            "2026-10-28 16:51"), 12, "02318_Quarter_2026Q3"),
        (mk("13600", "RESULTS FOR THE FIRST QUARTER OF 2026", "2026-04-20 20:49", "00941"), 12, "00941_Quarter_2026Q1"),
        (mk("13600", "ANNOUNCEMENT Third Quarterly Report of 2026", "2026-10-30 16:31", "00883"), 12, "00883_Quarter_2026Q3"),
        (mk("13300", "2025 ANNUAL RESULTS ANNOUNCEMENT", "2026-03-17 20:18", "03606"), 12, "03606_AnnualReport_2025_Results"),
        (mk("40100", "2025/2026 Annual Report", "2026-07-16 20:22", "02633"), 3, "02633_AnnualReport_2026"),
        (mk("40200", "2025/2026 Interim Report", "2025-12-12 16:46", "02633"), 3, "02633_Quarter_2026H1"),
        (mk("13400", "INTERIM RESULTS ANNOUNCEMENT FOR THE SIX MONTHS ENDED 30 SEPTEMBER 2026", "2026-11-24 21:32",
            "02633"), 3, "02633_Quarter_2027H1_Results"),
        (mk("13400", "INTERIM RESULTS ANNOUNCEMENT FOR THE PERIOD FROM 1 JANUARY 2026 TO 30 JUNE 2026",
            "2026-08-11 21:12", "87001"), 12, "87001_Quarter_2026H1_Results"),
    ]
    for doc, fye, want in cases:
        got = classify(doc, fye)["_base"]
        check(f"classify → {want}", got == want, f"得到 {got}")

    print("[selftest] 選檔（2 年報 + 1 中報 + 比報告更新的最新業績）")
    sel_docs = [classify(d, 12) for d in (
        mk("40100", "Annual Report 2025", "2026-04-28 18:40", no="A25"), mk("40100", "Annual Report 2024", "2025-04-16 17:06", no="A24"),
        mk("40100", "Annual Report 2023", "2024-04-26 17:29", no="A23"), mk("40200", "Interim Report 2026", "2026-09-10 06:08", no="I26"),
        mk("13400", "2026 INTERIM RESULTS", "2026-08-13 16:30", no="R26"),
        mk("13600", "Announcement of Unaudited Results for the Nine Months Ended September 30, 2026", "2026-10-28 16:51", no="Q3"),
        mk("13600", "Announcement of Unaudited Results for the Nine Months Ended September 30, 2026 (for 5131 debt stock)",
           "2026-10-28 22:29", no="Q3D"))]
    sel = select(pick(sel_docs), 2, 1, True)
    check("選到 A25、A24、I26、Q3（不含債券版、不含舊中期業績）", [d["_docno"] for d in sel] == ["A25", "A24", "I26", "Q3"],
          str([d["_docno"] for d in sel]))

    print("[selftest] 既有檔判定（repo 2026-11 實際檔名／內容）")
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        disc = "Hong Kong Exchanges and Clearing Limited ... take no responsibility for the contents of this announcement"
        files = {
            "02318_Interim_2026.md": disc + "\nANNOUNCEMENT OF UNAUDITED RESULTS FOR THE SIX MONTHS ENDED JUNE 30, 2026",
            "02318_annual_2025.md": "Ping An Annual Report 2025",
            "02318_Quarter_2026Q3.md": "# 中國平安 2026 前三季\n" + disc,
            "2026042200516.md": "Spring REIT 2025 Annual Report",
            "01426_InterimReport_2026.md": "ABOUT SPRING REIT ... 2026 Interim Report",
            "20260423_2025年年報.md": "HUI XIAN REIT ANNUAL REPORT 2025",
            "20250828二零二五年中期報告.md": "HUI XIAN REIT INTERIM REPORT 2025",
            "20260811_2026年中期業績公告.md": disc,
            "02633_Quarter_2026Q2.md": "JACOBSON PHARMA Interim Report 2025/2026",
        }
        for n, body in files.items():
            (tdp / n).write_text(body, encoding="utf-8")

        def cov(cat, title, dt, t, no="X", fye=12):
            return existing_cover(tdp, classify(mk(cat, title, dt, t, no), fye))
        check("業績公告（02318_Interim_2026）不可頂替中期報告", cov("40200", "Interim Report 2026", "2026-09-10 06:08", "02318") is None)
        check("02318_annual_2025 涵蓋年報 2025", cov("40100", "Annual Report 2025", "2026-04-28 18:40", "02318") is not None)
        check("季度業績 Q3 已有", cov("13600", "Results for the Nine Months Ended September 30, 2026", "2026-10-28 16:51",
                                    "02318") is not None)
        check("HKEX 編號檔名 2026042200516.md 涵蓋", cov("40100", "2025 Annual Report", "2026-04-22 16:39", "01426",
                                                     "2026042200516") is not None)
        check("01426_InterimReport_2026 涵蓋中報", cov("40200", "2026 Interim Report", "2026-08-28 16:35", "01426") is not None)
        check("中文原檔名 20260423_2025年年報 涵蓋年報 2025", cov("40100", "ANNUAL REPORT 2025", "2026-04-23 17:28", "87001")
              is not None)
        check("刊發日前綴 20260423 不可誤配年報 2026", cov("40100", "ANNUAL REPORT 2026", "2027-04-23 17:28", "87001") is None)
        check("中文數字 二零二五年中期報告 涵蓋中報 2025", cov("40200", "2025 INTERIM REPORT", "2025-08-28 17:59", "87001")
              is not None)
        check("中期業績公告不可頂替 2026 中期報告", cov("40200", "2026 INTERIM REPORT", "2026-08-28 17:26", "87001") is None)
        check("3 月決算舊名 _Quarter_2026Q2 涵蓋 2025/26 中報", cov("40200", "2025/2026 Interim Report", "2025-12-12 16:46",
                                                              "02633", fye=3) is not None)
        d = classify(mk("40200", "Interim Report 2026", "2026-09-10 06:08", "02318"), 12)
        (tdp / "02318_Quarter_2026H1.md").write_text(disc, encoding="utf-8")
        check("同名檔是業績公告 → 改存 _HKEX", name_taken_by_other(tdp, d) is not None)

    print("[selftest] SKILL.md 與 CLI 參數一致、經驗庫標記")
    skill_md = SKILL_DIR / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else ""
    check("SKILL.md 存在", bool(text), str(skill_md))
    check("SKILL.md 有經驗庫標記", LEARN_START in text and LEARN_END in text)
    subs = {}
    for act in parser._actions:  # noqa: SLF001
        if isinstance(act, argparse._SubParsersAction):  # noqa: SLF001
            subs = act.choices
    opts = {o for sp in subs.values() for act in sp._actions for o in act.option_strings}  # noqa: SLF001
    for sc in sorted(set(re.findall(r"hkexnews\.py\s+([a-z]+)", text))):
        check(f"SKILL.md 提到的子指令 `{sc}` 存在", sc in subs, f"CLI 沒有 {sc}")
    for op in sorted(set(re.findall(r"(?<![\w-])(--[a-z][a-z-]+)", text))):
        check(f"SKILL.md 提到的參數 `{op}` 存在", op in opts, f"CLI 沒有 {op}")
    for sc in subs:
        check(f"子指令 `{sc}` 有寫進 SKILL.md", f"hkexnews.py {sc}" in text, "SKILL.md 漏寫")
    for t in SEARCH_TYPES:
        check(f"search --type {t} 有寫進 SKILL.md", f"`{t}`" in text, "SKILL.md §2 漏寫")

    print("[selftest] .claude / .agents 鏡像同步")
    if (REPO_ROOT / ".agents").is_dir():
        for rel in ("SKILL.md", "scripts/hkexnews.py"):
            a1, a2 = REPO_ROOT / ".claude/skills/hkexnews" / rel, REPO_ROOT / ".agents/skills/hkexnews" / rel
            same = a1.is_file() and a2.is_file() and a1.read_bytes() == a2.read_bytes()
            check(f"鏡像一致 {rel}", same, "複製 .claude 版到 .agents（或跑 collectStk selfcheck.py --fix）")

    if not a.offline:
        print("[selftest] 線上：prefix.do、titleSearchServlet")
        try:
            s = resolve_stock("02318")
            check("02318 → stockId 7641", s["stockId"] == 7641, str(s))
            rows = search(s["stockId"], "40000", "-2", "40100", date.today() - timedelta(days=800), date.today())
            check("02318 近 800 天年報 ≥ 2 份", len(rows) >= 2, f"{len(rows)} 份")
            check("FILE_LINK 是 /listedco/ PDF", bool(rows) and rows[0]["FILE_LINK"].startswith("/listedco/"),
                  rows[0]["FILE_LINK"] if rows else "")
        except HkexError as e:
            p = log_error(e, sys.argv[1:])
            check("HKEXnews API 可用", False, f"{e.kind}：{e} → 已寫 {p}")

    print(f"[selftest] {'全部通過' if not fails else f'{len(fails)} 項失敗'}")
    OBS.clear()
    if fails:
        p = log_error(None, sys.argv[1:], kind="SELFTEST_FAIL", detail="；".join(fails[:20]))
        print(f"[selftest] 失敗明細已寫入 {p}", file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------- CLI
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=f"HKEXnews 港股年報/中報/季度業績下載器 v{VERSION}")
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lookup", help="找 stockId")
    s.add_argument("query")
    s = sub.add_parser("selftest", help="自我檢查")
    s.add_argument("--offline", action="store_true", help="不連網（只跑邏輯、文件、鏡像檢查）")
    s = sub.add_parser("verify", help="Convert2md 後驗證 .md")
    s.add_argument("--code", help="只驗證這家公司（預設：上次 download 的公司）")
    s = sub.add_parser("learn", help="經驗寫回 SKILL.md §8")
    s.add_argument("--note", required=True, help="一句話：情況 → 做法／結果")
    s = sub.add_parser("fetch", help="下載單一公告 PDF")
    s.add_argument("--url", required=True, help="FILE_LINK（/listedco/...pdf）或完整 hkexnews.hk 網址")
    s.add_argument("--dest", required=True, help="存檔完整路徑（.pdf）")
    s = sub.add_parser("search", help="列出任意公告")
    s.add_argument("--code", required=True)
    s.add_argument("--from", dest="date_from", help="起日 YYYY-MM-DD（預設 30 天前）")
    s.add_argument("--to", dest="date_to", help="迄日 YYYY-MM-DD（預設今天）")
    s.add_argument("--type", default="all", choices=sorted(SEARCH_TYPES))
    s.add_argument("--keyword", help="標題過濾（正規表示式，不分大小寫）")
    s.add_argument("--lang", default="en", choices=["en", "zh"])
    s.add_argument("--json", action="store_true", help="輸出 JSON")
    for name in ("list", "download"):
        s = sub.add_parser(name)
        s.add_argument("--code", required=True, help="股份代號（5 碼，如 02318；4 碼會自動補 0）")
        s.add_argument("--days", type=int, default=1000, help="最多往回幾天（預設 1000）")
        s.add_argument("--annual", type=int, default=2, help="年報份數（預設 2）")
        s.add_argument("--periodic", type=int, default=1, help="中期/季度報告份數（預設 1）")
        s.add_argument("--no-latest", action="store_true", help="不要額外抓「比報告更新的業績公告」")
        s.add_argument("--fye-month", type=int, help="決算月（1-12；預設由標題／刊發月推估）")
        s.add_argument("--lang", default="en", choices=["en", "zh"], help="en（預設，CID 亂碼少）/ zh")
        if name == "download":
            s.add_argument("--out", help="輸出資料夾（預設：repo 內以代號開頭的公司資料夾）")
            s.add_argument("--no-create", action="store_true", help="找不到公司資料夾時報錯，不自動新建")
            s.add_argument("--force", action="store_true", help="已存在也重新下載")
    return ap


def _parse_day(s: str | None, default: date) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date() if s else default


def _cmd_search(a) -> int:
    stock = resolve_stock(a.code)
    t1, t2g, t2 = SEARCH_TYPES[a.type]
    d_to = _parse_day(a.date_to, date.today())
    d_from = _parse_day(a.date_from, d_to - timedelta(days=30))
    rows = search(stock["stockId"], t1, t2g, t2, d_from, d_to, a.lang.upper(), rows=500)
    if a.keyword:
        rx = re.compile(a.keyword, re.I)
        rows = [r for r in rows if rx.search(r["TITLE"]) or rx.search(r["LONG_TEXT"])]
    if a.json:
        print(json.dumps([{"date": f"{r['_date']:%Y-%m-%d %H:%M}", "docno": r["_docno"], "title": r["TITLE"],
                           "category": re.sub(r"^.*?\[|\]$", "", r["LONG_TEXT"]), "type": r.get("FILE_TYPE"),
                           "size": r.get("FILE_INFO"), "url": BASE + r["FILE_LINK"]} for r in rows],
                         ensure_ascii=False, indent=1))
    else:
        print(f"# {stock['code']} {stock['name_zh']} / {stock['name_en']}（stockId {stock['stockId']}）"
              f" {d_from}~{d_to} type={a.type}：{len(rows)} 則")
        for r in rows:
            print(f"{r['_date']:%Y-%m-%d %H:%M}  {r.get('FILE_TYPE', ''):<4} {r.get('FILE_INFO', ''):>6}  "
                  f"{r['TITLE'][:110]}  | {BASE}{r['FILE_LINK']}")
    return 0


def _cmd_fetch(a) -> int:
    dest = Path(a.dest).expanduser().resolve()
    st, note = save_pdf(a.url, dest)
    print(f"[hkexnews] {st}：{dest}（{note}）")
    return 0 if st == "downloaded" else 1


def _cmd_list_download(a) -> int:
    stock = resolve_stock(a.code)
    print(f"[hkexnews] 公司：{stock['code']} {stock['name_zh']} / {stock['name_en']}（stockId {stock['stockId']}）",
          file=sys.stderr)
    t0 = time.time()
    docs, fye, fye_how = collect(stock, a.days, a.lang.upper(), a.fye_month)
    scan_line = (f"近 {a.days} 天 6 類文件；決算月 {fye} 月（{fye_how}）；請求 {STATS['requests']} 次、"
                 f"重試 {STATS['retries']} 次；{time.time() - t0:.0f} 秒")
    print(f"[hkexnews] 掃描：{scan_line}", file=sys.stderr)
    if a.cmd == "list":
        print("\n".join(_row(d) for d in docs) or "此區間 HKEXnews 無年報/中報/業績")
        for o in OBS:
            print(f"LEARN? {o}")
        return 0

    sel = select(docs, a.annual, a.periodic, not a.no_latest)
    out, created = resolve_out(a, stock)
    if created:
        print(f"[hkexnews] 新公司 → 自動建立資料夾 {out.name}（可事後改名，但要保留代號開頭）")
    n_a = sum(d["_cat"] == "40100" for d in sel)
    n_p = sum(d["_cat"] in ("40200", "40300") for d in sel)
    print(f"[hkexnews] 選定 {n_a}/{a.annual} 份年報、{n_p}/{a.periodic} 份中期/季度報告"
          + ("、1 份最新業績公告" if any(d["_cat"] in RESULTS for d in sel) else "") + f" → {out}")
    results, downloaded = [], []
    for d in sel:
        print("  " + _row(d))
        r = download_doc(d, out, a.force)
        r["doc"] = d
        results.append(r)
        print(f"    [{r['status']}] {r['file']}  {r['note']}")
        if r["status"] == "downloaded":
            downloaded.append(str(out / r["file"]))

    gaps = []
    if n_a < a.annual:
        gaps.append(f"年報只找到 {n_a}/{a.annual} 份：{a.days} 天內 HKEXnews 沒有更多（新上市？加大 --days）")
    if n_p < a.periodic:
        gaps.append(f"中期/季度報告只找到 {n_p}/{a.periodic} 份（新上市，或首份中報尚未刊發）")
    if any(r["status"] == "failed" for r in results):
        gaps.append("有檔案下載驗證失敗（見上方 failed），已丟棄未寫入")
    newest_rep = max((d for d in docs if d["_cat"] in REPORTS), key=lambda d: d["_pe"], default=None)
    if newest_rep and not any(d["_cat"] in RESULTS for d in sel):
        gaps.append(f"沒有比 {newest_rep['_base']}（期末 {newest_rep['_pe']}）更新的業績公告")

    rel = out.relative_to(REPO_ROOT) if out.is_relative_to(REPO_ROOT) else out
    L = [f"## {datetime.now():%H:%M:%S} — {stock['code']} {stock['name_zh']} / {stock['name_en']}", "",
         f"- 指令：`hkexnews.py {' '.join(sys.argv[1:])}`", f"- 掃描：{scan_line}",
         f"- 輸出資料夾：`{rel}`" + ("（本次新建）" if created else ""), "- 文件："]
    for r in results:
        d = r["doc"]
        L.append(f"  - {d['_date']:%Y-%m-%d} `{d['_docno']}` {CAT[d['_cat']][2]} 期末 {d['_pe']} 「{d['TITLE'][:80]}」"
                 f" → `{r['file']}`：{r['status']}（{r['note']}）｜{BASE}{d['FILE_LINK']}")
    if not results:
        L.append("  - （無）")
    if gaps:
        L += ["- 缺口與原因："] + [f"  - {g}" for g in gaps]
    L += _obs_lines()
    L.append(f"- 下一步：Convert2md（`<SCOPE>` = `{out}`）→ `hkexnews.py verify --code {stock['code']}`" if downloaded
             else "- 下一步：無新 PDF，免轉檔")
    sp = write_summary(L)
    runs = _load_manifest()  # 每家公司各存一筆：同一輪連續 download 多家後，verify 任一家都找得到
    runs["last"] = stock["code"]
    runs.setdefault("runs", {})[stock["code"]] = {
        "code": stock["code"], "folder": str(out), "stock": stock,
        "items": [{"base": r["doc"]["_base"], "status": r["status"], "cover": r.get("cover"),
                   "url": BASE + r["doc"]["FILE_LINK"]} for r in results if r["status"] in ("downloaded", "skipped")],
        "downloaded": downloaded, "time": datetime.now().isoformat()}
    CACHE.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(runs, ensure_ascii=False, indent=1), encoding="utf-8")
    for g in gaps:
        print(f"[hkexnews] ⚠ {g}")
    for o in OBS:
        print(f"LEARN? {o}")
    print(f"[hkexnews] 執行報告：{sp}")
    if downloaded:
        print("[hkexnews] NEXT → 跑 Convert2md skill，<SCOPE> 用下面這個資料夾，轉完再 `hkexnews.py verify`：")
        print(f"CONVERT2MD_SCOPE={out}")
    return 0


def _load_manifest() -> dict:
    try:
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return m if "runs" in m else {}


def _cmd_verify(a) -> int:
    runs = _load_manifest()
    code = norm_code(a.code) if a.code else runs.get("last")
    m = (runs.get("runs") or {}).get(code or "")
    if not m:
        raise HkexError("NOT_FOUND", f"{MANIFEST} 沒有 {code or '任何公司'} 的 download 紀錄 → 先跑 download --code {code or '{代號}'}")
    out, stock = Path(m["folder"]), m["stock"]
    items = m.get("items") or []
    bad, L = 0, [f"## {datetime.now():%H:%M:%S} — verify {m['code']}（{out.name}）", ""]
    for it in items:
        md = out / Path(it.get("cover") or f"{it['base']}.pdf").with_suffix(".md").name
        if it["status"] == "skipped" and not md.is_file():
            line = f"- ➖ `{it['base']}`：由既有檔 `{it.get('cover')}` 涵蓋（非 .md，本次不驗證）"
        else:
            ok, note = verify_md(md, stock)
            bad += not ok
            line = f"- {'✅' if ok else '❌'} `{md.name}`：{note}" + ("（既有檔）" if it["status"] == "skipped" else "")
            if not ok and it["status"] == "downloaded":
                observe(f"{md.name} 驗證失敗：{note}（來源 {it.get('url')}）")
        L.append(line)
        print(line)
    L += _obs_lines()
    sp = write_summary(L)
    for o in OBS:
        print(f"LEARN? {o}")
    print(f"[hkexnews] verify：{len(items) - bad}/{len(items)} 通過 → {sp}")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    a = parser.parse_args(argv)
    raw = argv if argv is not None else sys.argv[1:]
    try:
        if a.cmd == "lookup":
            s = resolve_stock(a.query)
            print(f"{s['code']}  stockId={s['stockId']}  {s['name_zh']} / {s['name_en']}")
            return 0
        if a.cmd == "selftest":
            return _cmd_selftest(a, parser)
        if a.cmd == "verify":
            return _cmd_verify(a)
        if a.cmd == "learn":
            return _cmd_learn(a)
        if a.cmd == "search":
            return _cmd_search(a)
        if a.cmd == "fetch":
            return _cmd_fetch(a)
        return _cmd_list_download(a)
    except HkexError as e:
        p = log_error(e, raw)
        print(f"[hkexnews] ✗ {e.kind}：{e}" + (f"｜{e.detail[:200]}" if e.detail else ""), file=sys.stderr)
        print(f"[hkexnews] 錯誤報告已寫入：{p}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    except Exception:  # noqa: BLE001 — 腳本 bug：完整 traceback 寫進 log 讓 AI 自我修正
        tb = traceback.format_exc()
        p = log_error(None, raw, kind="SCRIPT_BUG", tb=tb)
        print(tb, file=sys.stderr)
        print(f"[hkexnews] ✗ SCRIPT_BUG → 已寫入 {p}；AI 請依 SKILL.md §9 自我修正", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
