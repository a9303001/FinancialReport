#!/usr/bin/env python3
"""HKEXnews（披露易）downloader — 港股年報 / 中期報告 / 季度與全年業績，英文版優先。

只用 Python 標準函式庫（Windows / Linux / macOS / Claude Code 雲端皆可）。不需要 API key。

子指令:
  lookup   <查詢>                          股份代號 / 英文名 / 中文名 → stockId（港交所完整股票清單，含 GEM、已除牌）
  list     --code 02318                    列出年報/中報/業績、推算的期別、語言與「download 會怎麼做」（不下載）
  download --code 02318 [--annual 2 --periodic 1] [--out DIR] [--accept-zh]
  verify   [--code 02318] [--prune-zh]     Convert2md 之後驗證 .md（大小、CID、公司名、語言）；可刪掉已被英文版取代的中文檔
  search   --code 01426 --from 2026-10-26 [--type all] [--keyword X] [--json]   任意公告清單（collectState 用）
  fetch    --url /listedco/.../xxx.pdf --dest <檔案路徑>                        下載單一公告 PDF（驗證檔頭）
  learn    --note "..."                    把本次學到的經驗寫進 SKILL.md §8 經驗庫並同步 .agents 鏡像
  selftest [--offline]                     自我檢查

英文優先規則（v2）:
  1. 一律先用英文（lang=EN）搜尋並下載英文版 PDF（中文版是另一個編號、檔名 *_c.pdf）。
  2. 資料夾裡已有同期別檔，但內容是中文 → 自動補抓英文版（--accept-zh 可關閉）；英文 .md 驗證通過後
     `verify --prune-zh` 刪掉被取代的中文檔。
  3. 英文搜尋湊不滿份數時，才用中文搜尋補「英文沒有的期別」；英文完全沒有報告 → 整份改用中文。

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

VERSION = "2.0.0"

for _s in (sys.stdout, sys.stderr):  # Windows 主控台（cp950）印中文 → 一律 UTF-8
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BASE = "https://www1.hkexnews.hk"
PREFIX_URL = BASE + "/search/prefix.do"
SEARCH_URL = BASE + "/search/titleSearchServlet.do"  # 大小寫敏感：全小寫會 404
STOCK_LIST_URL = BASE + "/ncms/script/eds/{}.json"  # activestock_sehk_e / _c、inactivestock_sehk_e / _c（含 GEM）
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
STOCK_CACHE = CACHE / "stocks_v2.json"
LIST_MAX_AGE = 7 * 86400  # 股票清單快取 7 天
MIN_PDF_BYTES = 10 * 1024

# 文件分類（https://www1.hkexnews.hk/ncms/script/eds/tiertwo_e.json，2026-11 實測）
#   代碼: (t1code, 英文名, 中文標籤, LONG_TEXT 裡的英文分類名, LONG_TEXT 裡的中文分類名)
CAT = {
    "40100": ("40000", "Annual Report", "年報", "annual report", "年報"),
    "40200": ("40000", "Interim/Half-Year Report", "中期報告", "interim/half-year report", "中期/半年度報告"),
    "40300": ("40000", "Quarterly Report", "季度報告", "quarterly report", "季度報告"),
    "13300": ("10000", "Final Results", "全年業績公告", "final results", "末期業績"),
    "13400": ("10000", "Interim Results", "中期業績公告", "interim results", "中期業績"),
    "13600": ("10000", "Quarterly Results", "季度業績公告", "quarterly results", "季度業績"),
}
REPORTS = ("40100", "40200", "40300")
RESULTS = ("13300", "13400", "13600")
CAT_BY_NAME = {n: k for k, v in CAT.items() for n in (v[3], v[4])}
# 2 次群組搜尋取代 6 次分類搜尋：(t1code, t2Gcode, 該群組內本 skill 要的分類)
GROUPS = (("40000", "-2", REPORTS), ("10000", "3", RESULTS))
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
LANG_LABEL = {"en": "英文", "zh": "中文", "bi": "中英雙語", None: "未知"}
OBS: list[str] = []  # 本次執行觀察到、值得寫回 skill 的現象（LEARN? 候選）


class HkexError(Exception):
    def __init__(self, kind: str, msg: str, *, status: int | None = None, endpoint: str | None = None,
                 detail: str | None = None):
        super().__init__(msg)
        self.kind, self.status, self.endpoint, self.detail = kind, status, endpoint, detail


def observe(msg: str) -> None:
    if msg not in OBS:
        OBS.append(msg)


# ---------------------------------------------------------------- HTTP（含重試、節流、串流下載）
MIN_INTERVAL = float(os.environ.get("HKEXNEWS_MIN_INTERVAL", "0.8"))  # 秒/請求（禮貌節流）
_last = [0.0]
STATS = {"requests": 0, "retries": 0}


def _with_retry(url: str, params: dict | None, handler, *, retries: int = 4, timeout: int = 60,
                referer: str | None = None):
    """開連線並把 response 交給 handler；403/429/5xx、斷線自動退避重試。"""
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
                return handler(r)
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


def http_get(url: str, params: dict | None = None, timeout: int = 60) -> bytes:
    return _with_retry(url, params, lambda r: r.read(), timeout=timeout)


# ---------------------------------------------------------------- 股份代號 → stockId
def norm_code(code: str) -> str:
    c = code.strip().upper().removesuffix(".HK").removesuffix("-HK")
    return c.zfill(5) if c.isdigit() else c


def _nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "").casefold()


def _stock_list(name: str) -> list[dict]:
    """港交所完整股票清單 [{i: stockId, c: 代號, n: 名稱}]；快取 7 天，網路失敗時用過期快取。"""
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{name}.json"
    fresh = p.is_file() and time.time() - p.stat().st_mtime < LIST_MAX_AGE
    if not fresh:
        try:
            data = http_get(STOCK_LIST_URL.format(name))
            json.loads(data.decode("utf-8-sig"))  # 先驗證再寫快取
            p.write_bytes(data)
        except (HkexError, ValueError) as e:
            if not p.is_file():
                raise HkexError("API_ERROR", f"股票清單 {name}.json 取得失敗：{e}", endpoint=f"/ncms/script/eds/{name}.json") \
                    from None
            observe(f"股票清單 {name}.json 更新失敗，改用舊快取（{e}）")
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except ValueError:
        p.unlink(missing_ok=True)
        raise HkexError("API_ERROR", f"股票清單 {name}.json 不是 JSON（已刪快取，重跑一次）") from None


def _prefix(name: str, lang: str = "EN", typ: str = "A") -> list[dict]:
    data = http_get(PREFIX_URL, {"callback": "c", "lang": lang, "type": typ, "name": name, "market": "SEHK"})
    t = data.decode("utf-8", "replace")
    try:
        return json.loads(t[t.index("(") + 1:t.rindex(")")]).get("stockInfo") or []
    except ValueError:
        raise HkexError("API_ERROR", "prefix.do 回應不是 JSONP", endpoint="/search/prefix.do", detail=t[:200]) from None


def _match_list(q: str, status: str, lists=None) -> list[dict]:
    """在 active / inactive 清單找代號或名稱；回傳 [{stockId, code, name_en, name_zh, status}]。"""
    lists = lists or _stock_list
    en = lists(f"{status}stock_sehk_e")
    zh = {x["i"]: x["n"] for x in lists(f"{status}stock_sehk_c")}
    if q.isdigit():
        hits = [x for x in en if x["c"] == q]
    else:
        nq = _nfkc(q)
        exact = [x for x in en if _nfkc(x["n"]) == nq or _nfkc(zh.get(x["i"], "")) == nq]
        hits = exact or [x for x in en if nq in _nfkc(x["n"]) or nq in _nfkc(zh.get(x["i"], ""))]
    return [{"stockId": x["i"], "code": x["c"], "name_en": x["n"], "name_zh": zh.get(x["i"], ""), "status": status}
            for x in hits]


def resolve_stock(query: str, lists=None) -> dict:
    """回傳 {stockId, code, name_en, name_zh, status}。先查快取 → 上市清單 → 已除牌清單 → prefix.do（備援）。"""
    q = norm_code(query) if query.strip().isdigit() else query.strip()
    cache: dict = {}
    if lists is None:
        try:
            cache = json.loads(STOCK_CACHE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cache = {}
        if q in cache:
            return cache[q]
    hits: list[dict] = []
    try:
        for status in ("active", "inactive"):
            hits = _match_list(q, status, lists)
            if hits:
                if status == "inactive":
                    observe(f"{q} 不在上市清單，在已除牌清單找到（{len(hits)} 筆）")
                break
    except HkexError as e:
        if lists is not None or e.kind == "PROXY_BLOCKED":
            raise
        observe(f"股票清單不可用（{e}）→ 改用 prefix.do")
        hits = [{"stockId": x["stockId"], "code": x["code"], "name_en": x["name"], "name_zh": "", "status": "prefix"}
                for x in _prefix(q, "EN") if not q.isdigit() or x.get("code") == q]
    if len(hits) > 1:
        same_code = len({h["code"] for h in hits}) == 1
        if same_code:  # 已除牌代號被重用：取最新的 stockId（最近一家）
            hits.sort(key=lambda h: h["stockId"], reverse=True)
            observe(f"代號 {hits[0]['code']} 對到 {len(hits)} 家已除牌公司，取最新一家 {hits[0]['name_en']}"
                    f"（其他：{', '.join(h['name_en'] for h in hits[1:4])}）")
        else:
            lines = "\n".join(f"  {h['code']}  {h['name_zh']} / {h['name_en']}" for h in hits[:15])
            raise HkexError("AMBIGUOUS", f"「{query}」對到多檔，請改用 5 碼股份代號：\n{lines}")
    if not hits:
        raise HkexError("NOT_FOUND", f"HKEXnews 找不到「{query}」（港股請用 5 碼代號，如 02318）")
    info = hits[0]
    if not info["name_zh"] and info["status"] == "prefix":
        info["name_zh"] = next((x["name"] for x in _prefix(info["code"], "ZH") if x.get("code") == info["code"]), "")
    if lists is None:
        cache[q] = cache[info["code"]] = info
        CACHE.mkdir(parents=True, exist_ok=True)
        STOCK_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


# ---------------------------------------------------------------- 搜尋
def search(stock_id: int, t1: str, t2g: str, t2: str, d_from: date, d_to: date, lang: str = "EN",
           rows: int = 200) -> tuple[list[dict], bool]:
    """回傳 (文件清單, 是否被 rowRange 截斷)。"""
    params = {"sortDir": "0", "sortByOptions": "DateTime", "category": "0", "market": "SEHK",
              "stockId": str(stock_id), "documentType": "-1", "fromDate": d_from.strftime("%Y%m%d"),
              "toDate": d_to.strftime("%Y%m%d"), "lang": lang, "searchType": "1", "rowRange": str(rows),
              "t1code": t1, "t2Gcode": t2g, "t2code": t2}
    data = http_get(SEARCH_URL, params)
    try:
        j = json.loads(data.decode("utf-8"))
        res = j.get("result")
        out = json.loads(res) if res and res != "null" else []  # result 是「JSON 字串裡的 JSON」
    except (ValueError, AttributeError):
        raise HkexError("API_ERROR", "titleSearchServlet 回應不是預期 JSON", endpoint="/search/titleSearchServlet.do",
                        detail=data[:200].decode("utf-8", "replace")) from None
    for x in out:
        x["TITLE"] = html.unescape(x.get("TITLE") or "").replace("\n", " ").strip()
        x["LONG_TEXT"] = html.unescape(x.get("LONG_TEXT") or "")
        x["_date"] = datetime.strptime(x["DATE_TIME"], "%d/%m/%Y %H:%M")
        x["_docno"] = Path(x.get("FILE_LINK") or "").stem
        x["_lang"] = link_lang(x.get("FILE_LINK") or "")
    return out, bool(j.get("hasNextRow"))


def link_lang(link: str) -> str:
    """HKEXnews 中文版 PDF 檔名以 _c.pdf 結尾；其餘視為英文（或雙語）版。"""
    return "zh" if re.search(r"_c\.pdf$", link, re.I) else "en"


def cats_of(long_text: str) -> list[str]:
    """LONG_TEXT「Announcements and Notices - [Interim Results / Dividend or Distribution]」→ ['13400']。"""
    found = []
    for br in re.findall(r"\[([^\]]+)\]", long_text or ""):
        for part in br.split(" / "):
            c = CAT_BY_NAME.get(_nfkc(part.strip()))
            if c and c not in found:
                found.append(c)
    return sorted(found, key=list(CAT).index)


def gather(stock: dict, d_from: date, d_to: date, lang: str, groups=GROUPS) -> list[dict]:
    """群組搜尋（2 次請求）；被 rowRange 截斷的群組改回逐分類搜尋。"""
    docs: list[dict] = []
    for t1, t2g, cats in groups:
        rows, cut = search(stock["stockId"], t1, t2g, "-2", d_from, d_to, lang)
        if cut:
            observe(f"群組 {t1}/{t2g} 超過 rowRange（{len(rows)} 筆）→ 改逐分類搜尋")
            rows = []
            for c in cats:
                r, cut2 = search(stock["stockId"], t1, "-2", c, d_from, d_to, lang)
                if cut2:
                    observe(f"{CAT[c][1]} 仍超過 rowRange → 縮短 --days")
                for x in r:
                    x["LONG_TEXT"] = x["LONG_TEXT"] or f"[{CAT[c][3]}]"
                rows += r
        seen = set()
        for r in rows:
            cs = [c for c in cats_of(r["LONG_TEXT"]) if c in cats]
            if not cs or r["_docno"] in seen:
                continue
            seen.add(r["_docno"])
            if (r.get("FILE_TYPE") or "").upper() != "PDF":
                observe(f"{cs[0]} 有非 PDF 文件（{r.get('FILE_TYPE')}）：「{r['TITLE'][:60]}」→ 略過")
                continue
            r["_cat"], r["_ticker"] = cs[0], stock["code"]
            docs.append(r)
    return docs


# ---------------------------------------------------------------- 標題解析與期別（英文與中文標題）
CN_DIGITS = str.maketrans("〇零一二三四五六七八九", "00123456789")
_DATE_RES = [
    re.compile(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\.?,?\s+(20\d\d)"),   # 31 December 2025
    re.compile(r"([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d\d)"),   # December 31, 2025
    re.compile(r"(20\d\d)\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日"),               # 2026年9月30日
]


def _cn_num(title: str) -> str:
    """「二零二五年」→「2025年」（只轉 4 個連續中文數字，免得把「九個月」也轉掉）。"""
    return re.sub(r"[〇零一二三四五六七八九]{4}", lambda m: m.group().translate(CN_DIGITS), title)


def _mk(y: int, m: int, d: int) -> date | None:
    try:
        return date(y, m, d)
    except ValueError:
        return None


def title_dates(title: str) -> list[date]:
    title = _cn_num(title)
    found: list[tuple[int, date]] = []
    for i, rx in enumerate(_DATE_RES):
        for m in rx.finditer(title):
            if i == 2:
                dt = _mk(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            else:
                d, mon, y = (m.group(1), m.group(2), m.group(3)) if i == 0 else (m.group(2), m.group(1), m.group(3))
                mm = MONTHS.get(mon.lower())
                dt = _mk(int(y), mm, int(d)) if mm else None
            if dt:
                found.append((m.start(), dt))
    return [d for _, d in sorted(found)]


def title_part(title: str) -> str | None:
    """Q1 / Q3 / H1 / FY；認不出 → None。順序重要：「FIRST THREE QUARTERS」要先於「FIRST QUARTER」。"""
    t = title.lower()
    if re.search(r"nine months|three quarters|third quarter|第三季|前三季|(?<!\d)[9九]\s*個月|(?<!\d)[9九]\s*个月", t):
        return "Q3"
    if re.search(r"six months|interim|half[- ]year|中期|半年|(?<!\d)[6六]\s*個月|(?<!\d)[6六]\s*个月", t):
        return "H1"
    if re.search(r"three months|first quarter|第一季|(?<!\d)[3三]\s*個月|(?<!\d)[3三]\s*个月", t):
        return "Q1"
    if re.search(r"second quarter|第二季", t):
        return "H1"
    if re.search(r"year ended|annual|final results|全年|年度|年報|年报|末期", t):
        return "FY"
    return None


def title_years(title: str) -> list[int]:
    t = _cn_num(title)
    t = re.sub(r"\d{1,2}\s+[A-Za-z]+\s+20\d\d|[A-Za-z]+\s+\d{1,2},?\s+20\d\d|20\d\d年\d{1,2}月\d{1,2}日", " ", t)
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
    for d in (x for x in docs if x["_cat"] == "40100"):
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
    elif cat == "13300" or (cat not in REPORTS and part == "FY"):
        base = f"{t}_AnnualReport_{fy}_Results"
    elif cat == "40200":
        base = f"{t}_Quarter_{fy}H1"
    elif part == "H1":
        base = f"{t}_Quarter_{fy}H1_Results"
    else:
        base = f"{t}_Quarter_{fy}{part}"
    doc.update(_pe=pe, _part=part, _fy=fy, _fye=fye, _base=base, _how=how)
    return doc


# 同一期別多份候選時，排除附屬文件（債券版、簡報、更正、股息表格…）
_PENALTY = re.compile(r"debt|bond|presentation|\bora\b|supplement|clarification|correction|corrigend|erratum|"
                      r"revised|dividend|announcement form|monthly return|summary|abstract|esg|sustainab|"
                      r"債券|债券|簡報|简报|補充|补充|澄清|更正|修訂|修订|股息|摘要|環境、社會|可持續", re.I)


def _score(doc: dict) -> tuple:
    return (bool(_PENALTY.search(doc["TITLE"])), doc["_lang"] != "en", doc["_date"])


def pick(docs: list[dict]) -> list[dict]:
    """同一 (分類, 期末) 只留一份：附屬文件最後、英文優先、再取最早刊發（原始版）。"""
    by: dict[tuple, list[dict]] = {}
    for d in docs:
        by.setdefault((d["_cat"], d["_pe"]), []).append(d)
    out = []
    for k, ds in by.items():
        ds.sort(key=_score)
        if len(ds) > 1 and _score(ds[0])[:2] == _score(ds[1])[:2]:  # 附屬文件／語言規則分不出來才值得記
            observe(f"{CAT[k[0]][1]} 期末 {k[1]} 有 {len(ds)} 份：選「{ds[0]['TITLE'][:60]}」，略過 "
                    + "；".join(f"「{x['TITLE'][:50]}」" for x in ds[1:3]))
        out.append(ds[0])
    return sorted(out, key=lambda d: (d["_pe"], d["_date"]), reverse=True)


def select(docs: list[dict], annual_n: int, periodic_n: int, latest: bool) -> list[dict]:
    ann = [d for d in docs if d["_cat"] == "40100"][:annual_n]
    per = [d for d in docs if d["_cat"] in ("40200", "40300")][:periodic_n]
    sel = ann + per
    if latest:
        newest_pe = max((d["_pe"] for d in docs if d["_cat"] in REPORTS), default=date.min)
        newer = [d for d in docs if d["_cat"] in RESULTS and d["_pe"] > newest_pe]
        if newer:  # 期末比所有報告都新的最新一份業績（Q3、或報告還沒出的中期／全年業績）
            sel.append(newer[0])
    return sel


def collect(stock: dict, days: int, lang: str, fye_month: int | None, annual_n: int = 2,
            periodic_n: int = 1) -> tuple[list[dict], int, str]:
    """英文優先：EN 群組搜尋 → 份數不夠才用 ZH 補「英文沒有的期別」→ EN 完全沒有報告才整份改 ZH。"""
    today = date.today()
    d_from = today - timedelta(days=days)
    docs = gather(stock, d_from, today, lang)
    note = ""
    if lang == "EN" and not any(d["_cat"] in REPORTS for d in docs):
        observe(f"{stock['code']} 英文搜尋沒有任何年報/中報 → 整份改用中文（lang=ZH）")
        docs, lang, note = gather(stock, d_from, today, "ZH"), "ZH", "；英文無報告，改用中文版"
    elif lang == "ZH":
        for d in docs:
            d["_zh_requested"] = True
        note = "；依 --lang zh 用中文版"
    fye, how = (fye_month, "--fye-month") if fye_month else infer_fye(docs)
    for d in docs:
        classify(d, fye)
    docs = pick(docs)
    if lang == "EN":
        n_a = sum(d["_cat"] == "40100" for d in docs)
        n_p = sum(d["_cat"] in ("40200", "40300") for d in docs)
        if n_a < annual_n or n_p < periodic_n:  # 英文湊不滿 → 看中文版有沒有英文沒有的期別
            have = {(d["_cat"], d["_pe"]) for d in docs} | {(d["_cat"], d["DATE_TIME"]) for d in docs}
            extra = [classify(d, fye) for d in gather(stock, d_from, today, "ZH", GROUPS[:1])]
            extra = [d for d in extra if (d["_cat"], d["_pe"]) not in have and (d["_cat"], d["DATE_TIME"]) not in have]
            if extra:
                observe(f"{stock['code']} 英文版缺 {len(extra)} 份報告，用中文版補："
                        + "、".join(f"{d['_base']}（{d['_docno']}）" for d in extra[:4]))
                docs = pick(docs + extra)
                note = "；中文版補缺"
    return docs, fye, how + note


# ---------------------------------------------------------------- 既有檔：種類、語言、別名
DISCLAIMER = re.compile(r"contents of this announcement|本公告的?內容|对本公告的内容|對本公告的內容", re.I)
KIND_PATTERNS = [
    ("annual", re.compile(r"annual report|年報|年度報告|年度报告", re.I)),
    ("interim", re.compile(r"interim report|中期報告|中期报告|半年度報告|半年度报告", re.I)),
    ("quarterly", re.compile(r"quarterly report|季度報告|季度报告", re.I)),
]
ACCEPT = {"40100": {"annual"}, "40200": {"interim"}, "40300": {"quarterly", "results"},
          "13300": {"results", "annual"}, "13400": {"results", "interim"}, "13600": {"results", "quarterly"}}
_CJK = re.compile(r"[㐀-鿿豈-﫿]")
_LATIN = re.compile(r"[A-Za-z]")


def _head(path: Path, n: int) -> str:
    try:
        with path.open(encoding="utf-8", errors="replace") as f:
            return f.read(n)
    except OSError:
        return ""


def text_lang(text: str) -> str | None:
    """中文字占（中文字 + 英文字母）的比例：≥0.5 中文、0.15～0.5 中英雙語、<0.15 英文。
    實測（2026-11）：中文年報 0.93～0.99、英文 0.00～0.02、恒安英文年報（夾中文表格）0.19。"""
    cjk, lat = len(_CJK.findall(text)), len(_LATIN.findall(text))
    if cjk + lat < 200:
        return None
    r = cjk / (cjk + lat)
    return "zh" if r >= 0.5 else ("bi" if r >= 0.15 else "en")


def file_lang(path: Path) -> str | None:
    """.md 看內容（前 4 萬字）；.pdf 只能看檔名：*_c.pdf 或檔名有中文 → zh，否則未知（None）。
    注意：中文檔名不代表中文內容（87001「二零二五年中期報告.md」其實是英文版）。"""
    if path.suffix.lower() == ".md":
        return text_lang(_head(path, 40000))
    return "zh" if re.search(r"_c$", path.stem, re.I) or _CJK.search(path.stem) else None


def doc_kind(path: Path, head_chars: int = 8000) -> str | None:
    """.md 實際是哪種文件：'results'（公告：前 4000 字有港交所免責聲明）/'annual'/'interim'/'quarterly'；PDF 或認不出 → None。"""
    if path.suffix.lower() != ".md":
        return None
    head = _head(path, head_chars)
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


SUFFIXES = ("", "_EN", "_HKEX")  # _EN：同名檔是中文版時英文版另存；_HKEX：同名檔是別種文件時另存


def aliases(base: str) -> list[str]:
    """同一期別在 repo 裡可能出現的檔名（新命名、collectStk 舊命名、手動命名，各加 _EN／_HKEX）。"""
    m = re.match(r"^(.+?)_(AnnualReport|Quarter)_(\d{4})(H1|Q[1-4])?(_Results)?(?:_EN|_HKEX)?$", base)
    if not m:
        return [base]
    t, kind, fy, part, res = m.group(1), m.group(2), m.group(3), m.group(4) or "", m.group(5) or ""
    names = [f"{t}_{kind}_{fy}{part}{res}"]
    if kind == "AnnualReport":
        names += [f"{t}_AnnualReport_{fy}", f"{t}_annual_{fy}", f"{t}_Annual_{fy}"]
        names += [f"{t}_AnnualResults_{fy}", f"{t}_FinalResults_{fy}"] if res else []
    elif part == "H1":
        names += [f"{t}_Quarter_{fy}H1", f"{t}_Quarter_{fy}Q2", f"{t}_quarter_{fy}Q2", f"{t}_QuarterlyReport_{fy}Q2",
                  f"{t}_interim_{fy}", f"{t}_Interim_{fy}", f"{t}_InterimReport_{fy}"]
        names += [f"{t}_InterimResults_{fy}"] if res else []
    else:
        names += [f"{t}_Quarter_{fy}{part}", f"{t}_quarter_{fy}{part}", f"{t}_QuarterlyReport_{fy}{part}"]
    return list(dict.fromkeys(n + s for n in names for s in SUFFIXES))


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


def existing_covers(out: Path, doc: dict) -> list[Path]:
    """資料夾內已涵蓋該期別的所有檔：①同名或別名（.md 要內容種類相符）②HKEX 原始編號檔名
    ③中文原檔名（如 20260423_2025年年報.md、20250828二零二五年中期報告.md）。"""
    if not out.is_dir():
        return []
    cat = doc["_cat"]
    files = {p.name.lower(): p for p in out.iterdir() if p.is_file() and p.suffix.lower() in (".md", ".pdf")}
    hits: list[Path] = []
    for b in aliases(doc["_base"]):
        for ext in (".md", ".pdf"):
            p = files.get((b + ext).lower())
            if p and _same_doc(cat, p):
                hits.append(p)
    for p in files.values():
        if p.stem == doc["_docno"] or p.stem.startswith(doc["_docno"] + "_"):
            hits.append(p)
    # 非 12 月決算的會計年度跨兩個年曆年（「2025/2026 Annual Report」）→ 前一年也算
    fy_labels = {doc["_fy"]} | ({doc["_fy"] - 1} if doc.get("_fye", 12) != 12 else set())
    for p in files.values():
        st = p.stem
        if re.match(r"^\d{5}_", st) or not _ORIG_KW[cat].search(st):
            continue
        if cat in ("40100", "13300") and re.search(r"中期|interim|季度|quarter", st, re.I):
            continue
        if cat in REPORTS and re.search(r"業績|results|公告", st, re.I):
            continue  # 業績公告不能頂替完整報告
        if _years_in_name(st) & fy_labels and _same_doc(cat, p):
            hits.append(p)
    return list(dict.fromkeys(hits))


def existing_cover(out: Path, doc: dict) -> Path | None:
    hits = existing_covers(out, doc)
    return hits[0] if hits else None


def plan(doc: dict, out: Path, force: bool = False, accept_zh: bool = False) -> dict:
    """決定 download 對這份文件要做什麼：
    skip（已有英文／雙語版，或 HKEX 本身只有中文）、download（沒有）、upgrade（只有中文版 → 補抓英文版）。"""
    base = doc["_base"]
    hits = [] if force else existing_covers(out, doc)
    langs = {h: file_lang(h) for h in hits}
    p = {"action": "download", "base": base, "cover": None, "zh_dups": [], "note": ""}
    if hits:
        non_zh = [h for h in hits if langs[h] != "zh"]
        if non_zh or doc["_lang"] != "en" or accept_zh:
            h = (non_zh or hits)[0]
            p.update(action="skip", cover=h.name, note=f"已存在 {h.name}（{LANG_LABEL[langs[h]]}）")
            return p
        p.update(action="upgrade", zh_dups=[h.name for h in hits],
                 note=f"既有 {'、'.join(h.name for h in hits)} 是中文版 → 補抓英文版；")
    taken = [out / f"{base}{e}" for e in (".md", ".pdf")]
    taken = [t for t in taken if t.is_file()]
    if taken and not force:
        t = taken[0]
        if not _same_doc(doc["_cat"], t):  # 同名檔其實是別種文件（如業績公告存成報告名）→ 另存，不覆蓋
            p["base"] = base + "_HKEX"
            p["note"] += f"{t.name} 是別種文件（{doc_kind(t)}），改存 {p['base']}.pdf；"
            observe(f"{t.name} 內容種類與檔名不符（{doc_kind(t)}），新檔另存 {p['base']}.pdf")
        elif file_lang(t) == "zh":  # 同名檔是中文版 → 英文版另存 _EN
            p["base"] = base + "_EN"
    if doc["_lang"] != "en":
        p["note"] += "依 --lang zh 下載中文版；" if doc.get("_zh_requested") else "HKEXnews 無英文版，下載中文版；"
    return p


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


def save_pdf(link: str, dest: Path) -> tuple[str, str]:
    """串流下載到同資料夾暫存檔 → 驗證 %PDF 檔頭與 ≥10KB → 原子改名。"""
    url = link if link.startswith("http") else BASE + link
    if urllib.parse.urlsplit(url).hostname not in ("www1.hkexnews.hk", "www.hkexnews.hk"):
        return "failed", f"只接受 hkexnews.hk 網址：{url}"
    dest.parent.mkdir(parents=True, exist_ok=True)

    def handler(r):
        ctype = r.headers.get("Content-Type", "")
        head = r.read(1024)
        if not head.startswith(b"%PDF"):
            h = head[:200].decode("utf-8", "replace").lower()
            return None, "不是 PDF（" + ("HTML 封鎖頁" if "<html" in h else "檔頭不是 %PDF") + f"）；content-type={ctype}"
        fd, tmp = tempfile.mkstemp(dir=dest.parent, suffix=".part")
        n = len(head)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(head)
                while chunk := r.read(1 << 20):
                    f.write(chunk)
                    n += len(chunk)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise
        return tmp, n

    tmp, info = _with_retry(url, None, handler, timeout=300, referer=BASE + "/search/titlesearch.xhtml")
    if tmp is None:
        return "failed", info
    if info < MIN_PDF_BYTES:
        Path(tmp).unlink(missing_ok=True)
        return "failed", f"PDF 太小（{info} bytes < 10KB）"
    umask = os.umask(0)
    os.umask(umask)
    os.chmod(tmp, 0o666 & ~umask)
    Path(tmp).replace(dest)
    return "downloaded", f"{info / 1024:.0f} KB"


def download_doc(doc: dict, out: Path, force: bool, accept_zh: bool = False) -> dict:
    p = plan(doc, out, force, accept_zh)
    r = {"file": f"{p['base']}.pdf", "status": "skipped", "note": p["note"], "cover": p["cover"],
         "zh_dups": p["zh_dups"], "lang": doc["_lang"], "action": p["action"]}
    if p["action"] == "skip":
        return r
    st, note = save_pdf(doc["FILE_LINK"], out / r["file"])
    r.update(status=st, note=p["note"] + note, cover=r["file"] if st == "downloaded" else None)
    if st == "failed":
        observe(f"下載驗證失敗 {doc['FILE_LINK']}：{note}")
    return r


def _row(d: dict) -> str:
    return (f"{d['_date']:%Y-%m-%d}  {d['_docno']}  {d['_cat']} {CAT[d['_cat']][2]:<6} {LANG_LABEL[d['_lang']]} "
            f"期末 {d['_pe']}（{d['_how']}）→ {d['_base']}  | {d['TITLE'][:90]}")


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


def verify_md(md: Path, stock: dict, expect_lang: str | None = None) -> tuple[bool, str]:
    if not md.is_file():
        return False, "尚未轉成 .md（PDF 還在 → Convert2md 未跑或失敗）"
    size = md.stat().st_size
    if size < MIN_PDF_BYTES:
        return False, f".md 太小（{size} bytes）"
    text = md.read_text(encoding="utf-8", errors="replace")
    cid = len(CID_RE.findall(text))
    if cid >= 50:
        return False, f"CID 亂碼 {cid} 次 → 改抓另一語言版（--lang）"
    head = _nfkc(text[:30000])
    en = _nfkc(stock["name_en"])
    names = [en, en.split(" ")[0] if len(en.split(" ")[0]) >= 4 else "", _nfkc(stock["name_zh"]),
             stock["code"].lstrip("0"), stock["code"]]
    if not any(n and len(n) >= 2 and n in head for n in names):
        return False, "前 3 萬字找不到公司名／股份代號 → 檔案可能抓錯"
    lang = text_lang(text[:40000])
    if expect_lang == "en" and lang == "zh":
        return False, "應是英文版，內容卻是中文 → 檢查 FILE_LINK（_c.pdf？）"
    return True, f"OK（{size / 1024:.0f} KB，CID {cid}，{LANG_LABEL[lang]}）"


def prune_zh(out: Path, names: list[str], keep: Path) -> list[str]:
    """刪掉已被英文版取代的中文檔（同 stem 的 .md 與 .pdf）。只刪內容／檔名確認是中文、且不是 keep 的檔。"""
    removed = []
    for n in names:
        for p in {out / n, (out / n).with_suffix(".md"), (out / n).with_suffix(".pdf")}:
            if p.is_file() and p.resolve() != keep.resolve() and file_lang(p) in ("zh", None) \
                    and (p.suffix.lower() == ".pdf" or file_lang(p) == "zh"):
                p.unlink()
                removed.append(p.name)
    return removed


def drop_en_suffix(md: Path) -> Path:
    """X_EN.md（及同名 .pdf）→ X.md：只在 X.md／X.pdf 都不存在時改名，回傳新的 .md 路徑（沒改就回原路徑）。"""
    if not md.stem.endswith("_EN"):
        return md
    new = md.with_name(md.stem[:-3] + md.suffix)
    if new.exists() or new.with_suffix(".pdf").exists():
        return md
    for src in (md, md.with_suffix(".pdf")):
        if src.is_file():
            src.replace(src.with_name(new.stem + src.suffix))
    return new


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
        print("[hkexnews] 經驗庫已有同樣內容，未重複寫入")
        return 0
    line = f"- [{date.today():%Y-%m}] {note}\n"
    p.write_text(head + LEARN_START + "\n" + body + line + LEARN_END + tail, encoding="utf-8")
    m = sync_mirror()
    print(f"[hkexnews] 已寫入 {p.relative_to(REPO_ROOT)} §8：{line.strip()}")
    if m:
        print(f"[hkexnews] 已同步鏡像 {m.relative_to(REPO_ROOT)}")
    return 0


# ---------------------------------------------------------------- selftest
ZH_SAMPLE = "中國平安保險（集團）股份有限公司二零二五年年度報告，本集團營運收入與淨利潤穩健增長。" * 20
EN_SAMPLE = "Ping An Insurance (Group) Company of China, Ltd. Annual Report 2025. Operating profit grew. " * 20


def _cmd_selftest(a, parser: argparse.ArgumentParser) -> int:
    fails: list[str] = []

    def check(name: str, cond: bool, info: str = "") -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {name}{('  — ' + info) if info and not cond else ''}")
        if not cond:
            fails.append(f"{name}：{info}")

    def mk(cat: str, title: str, dt: str, t: str = "02318", no: str = "2026000000001", lang: str = "en") -> dict:
        return {"_cat": cat, "TITLE": title, "_date": datetime.strptime(dt, "%Y-%m-%d %H:%M"), "_ticker": t,
                "_docno": no, "_lang": lang, "DATE_TIME": dt, "FILE_LINK": f"/listedco/listconews/sehk/x/{no}.pdf"}

    print("[selftest] 標題解析（2026-11 實際英文／中文標題）")
    check("title_dates 31 DECEMBER 2025", title_dates("ANNUAL RESULTS ANNOUNCEMENT FOR THE YEAR ENDED 31 DECEMBER 2025")
          == [date(2025, 12, 31)])
    check("title_dates June 30, 2026", title_dates("ANNOUNCEMENT OF INTERIM RESULTS FOR THE SIX MONTHS ENDED JUNE 30, 2026")
          == [date(2026, 6, 30)])
    check("title_dates FROM…TO 取最後", title_dates("INTERIM RESULTS ANNOUNCEMENT FOR THE PERIOD FROM 1 JANUARY 2026 "
                                                 "TO 30 JUNE 2026")[-1] == date(2026, 6, 30))
    check("title_dates 中文 2026年9月30日", title_dates("截至2026年9月30日止九個月的未經審計業績公告") == [date(2026, 9, 30)])
    check("title_dates 中文 起迄取最後", title_dates("2026年1月1日至2026年6月30日止期間中期業績公告")[-1] == date(2026, 6, 30))
    for t, want in (("RESULTS FOR THE FIRST THREE QUARTERS OF 2026", "Q3"), ("RESULTS FOR THE FIRST QUARTER OF 2026", "Q1"),
                    ("INSIDE INFORMATION - THIRD QUARTERLY REPORT OF 2026", "Q3"),
                    ("Announcement of Unaudited Results for the Three Months Ended March 31, 2026", "Q1"),
                    ("Announcement of Unaudited Results for the Nine Months Ended September 30, 2026", "Q3"),
                    ("2026 FIRST QUARTERLY REPORT", "Q1"), ("2026 INTERIM RESULTS", "H1"),
                    ("截至2026年9月30日止九個月的未經審計業績公告", "Q3"), ("截至2026年3月31日止三個月的未經審計業績公告", "Q1"),
                    ("截至2026年6月30日止6個月的未經審計業績公告", "H1"), ("二零二五年年報", "FY")):
        check(f"title_part {want}：{t[:40]}", title_part(t) == want, f"得到 {title_part(t)}")
    check("title_years 2025/2026", title_years("2025/2026 Annual Report") == [2025, 2026])
    check("title_years 二零二五年年報", title_years("二零二五年年報") == [2025])

    print("[selftest] LONG_TEXT 分類（2 次群組搜尋用）")
    for lt, want in (("Financial Statements/ESG Information - [Annual Report]", ["40100"]),
                     ("Financial Statements/ESG Information - [Interim/Half-Year Report]", ["40200"]),
                     ("Financial Statements/ESG Information - [Environmental, Social and Governance Information/Report]", []),
                     ("Announcements and Notices - [Interim Results / Dividend or Distribution / Closure of Books]", ["13400"]),
                     ("Announcements and Notices - [Quarterly Results / Inside Information]", ["13600"]),
                     ("Announcements and Notices - [Final Results / Dividend or Distribution]", ["13300"]),
                     ("Announcements and Notices - [Dividend or Distribution (Announcement Form)]", []),
                     ("財務報表/環境、社會及管治資料 - [中期/半年度報告]", ["40200"]),
                     ("財務報表/環境、社會及管治資料 - [年報]", ["40100"]),
                     ("公告及通告 - [末期業績 / 股息或分派]", ["13300"]), ("公告及通告 - [季度業績 / 內幕消息]", ["13600"])):
        check(f"cats_of {lt[-40:]}", cats_of(lt) == want, f"得到 {cats_of(lt)}")
    check("link_lang _c.pdf → zh", link_lang("/listedco/listconews/sehk/2026/0428/2026042803046_c.pdf") == "zh")
    check("link_lang .pdf → en", link_lang("/listedco/listconews/sehk/2026/0428/2026042803045.pdf") == "en")

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
        (mk("40100", "二零二五年年報", "2026-04-28 18:40", lang="zh"), 12, "02318_AnnualReport_2025"),
        (mk("13600", "截至2026年9月30日止九個月的未經審計業績公告", "2026-10-28 16:51", lang="zh"), 12, "02318_Quarter_2026Q3"),
    ]
    for doc, fye, want in cases:
        got = classify(doc, fye)["_base"]
        check(f"classify → {want}（{doc['TITLE'][:24]}）", got == want, f"得到 {got}")

    print("[selftest] 選檔（2 年報 + 1 中報 + 比報告更新的最新業績；英文優先）")
    sel_docs = [classify(d, 12) for d in (
        mk("40100", "Annual Report 2025", "2026-04-28 18:40", no="A25"), mk("40100", "Annual Report 2024", "2025-04-16 17:06", no="A24"),
        mk("40100", "Annual Report 2023", "2024-04-26 17:29", no="A23"), mk("40200", "Interim Report 2026", "2026-09-10 06:08", no="I26"),
        mk("40200", "二零二六年中期報告", "2026-09-10 06:08", no="I26C", lang="zh"),
        mk("13400", "2026 INTERIM RESULTS", "2026-08-13 16:30", no="R26"),
        mk("13600", "Announcement of Unaudited Results for the Nine Months Ended September 30, 2026", "2026-10-28 16:51", no="Q3"),
        mk("13600", "Announcement of Unaudited Results for the Nine Months Ended September 30, 2026 (for 5131 debt stock)",
           "2026-10-28 22:29", no="Q3D"),
        mk("13600", "截至2026年3月31日止三個月的未經審計業績公告(致5131債券持有人)", "2026-04-28 22:29", no="Q1D", lang="zh"))]
    sel = select(pick(sel_docs), 2, 1, True)
    check("選到 A25、A24、I26、Q3（英文版、不含債券版、不含舊中期業績）", [d["_docno"] for d in sel] == ["A25", "A24", "I26", "Q3"],
          str([d["_docno"] for d in sel]))
    check("中文標題「致5131債券持有人」算附屬文件", _score(sel_docs[-1])[0])

    print("[selftest] 語言判定")
    check("text_lang 中文", text_lang(ZH_SAMPLE) == "zh", str(text_lang(ZH_SAMPLE)))
    check("text_lang 英文", text_lang(EN_SAMPLE) == "en", str(text_lang(EN_SAMPLE)))
    check("text_lang 雙語", text_lang(EN_SAMPLE + ZH_SAMPLE[:400]) == "bi", str(text_lang(EN_SAMPLE + ZH_SAMPLE[:400])))
    check("text_lang 太短 → None", text_lang("年報 2025") is None)

    print("[selftest] 既有檔判定與英文優先（repo 2026-11 實際檔名／內容）")
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        disc = "Hong Kong Exchanges and Clearing Limited ... take no responsibility for the contents of this announcement\n"
        files = {
            "02318_Interim_2026.md": disc + "ANNOUNCEMENT OF UNAUDITED RESULTS FOR THE SIX MONTHS ENDED JUNE 30, 2026\n" + EN_SAMPLE,
            "02318_annual_2025.md": ZH_SAMPLE,  # 實際是中文年報
            "02318_annual_2024.md": EN_SAMPLE,
            "02318_Quarter_2026Q3.md": "# 中國平安 2026 前三季\n" + disc + EN_SAMPLE,
            "2026042200516.md": "Spring REIT 2025 Annual Report " + EN_SAMPLE,
            "01426_InterimReport_2026.md": "ABOUT SPRING REIT ... 2026 Interim Report " + EN_SAMPLE,
            "20260423_2025年年報.md": "匯賢產業信託 2025 年報 " + ZH_SAMPLE,
            "20250828二零二五年中期報告.md": "HUI XIAN REIT INTERIM REPORT 2025 " + EN_SAMPLE,
            "20260811_2026年中期業績公告.md": disc,
            "02633_Quarter_2026Q2.md": "JACOBSON PHARMA Interim Report 2025/2026 " + EN_SAMPLE,
            "00941_AnnualReport_2025.md": ZH_SAMPLE,
        }
        for n, body in files.items():
            (tdp / n).write_text(body, encoding="utf-8")

        def doc(cat, title, dt, t, no="X", fye=12, lang="en"):
            return classify(mk(cat, title, dt, t, no, lang), fye)

        def cov(*args, **kw):
            return existing_cover(tdp, doc(*args, **kw))

        check("業績公告（02318_Interim_2026）不可頂替中期報告", cov("40200", "Interim Report 2026", "2026-09-10 06:08", "02318") is None)
        check("02318_annual_2024 涵蓋年報 2024", cov("40100", "Annual Report 2024", "2025-04-16 17:06", "02318") is not None)
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
        d = doc("40200", "Interim Report 2026", "2026-09-10 06:08", "02318")
        (tdp / "02318_Quarter_2026H1.md").write_text(disc + EN_SAMPLE, encoding="utf-8")
        p = plan(d, tdp)
        check("同名檔是業績公告 → 改存 _HKEX", p["action"] == "download" and p["base"] == "02318_Quarter_2026H1_HKEX", str(p))
        # 英文優先
        a25 = doc("40100", "Annual Report 2025", "2026-04-28 18:40", "02318")
        p = plan(a25, tdp)
        check("既有中文年報 02318_annual_2025 → upgrade 補抓英文 02318_AnnualReport_2025",
              p["action"] == "upgrade" and p["base"] == "02318_AnnualReport_2025" and "02318_annual_2025.md" in p["zh_dups"],
              str(p))
        check("--accept-zh → 中文版視為已有", plan(a25, tdp, accept_zh=True)["action"] == "skip")
        check("HKEX 只有中文版 → 不 upgrade", plan(dict(a25, _lang="zh"), tdp)["action"] == "skip")
        check("既有英文 02318_annual_2024 → skip", plan(doc("40100", "Annual Report 2024", "2025-04-16 17:06", "02318"),
                                                       tdp)["action"] == "skip")
        p = plan(doc("40100", "Annual Report 2025", "2026-03-30 18:40", "00941"), tdp)
        check("同名檔 00941_AnnualReport_2025.md 是中文 → 英文另存 _EN", p["action"] == "upgrade"
              and p["base"] == "00941_AnnualReport_2025_EN", str(p))
        check("中文原檔名中文年報 → upgrade", plan(doc("40100", "ANNUAL REPORT 2025", "2026-04-23 17:28", "87001"),
                                              tdp)["action"] == "upgrade")
        check("中文檔名但英文內容（二零二五年中期報告.md）→ skip",
              plan(doc("40200", "2025 INTERIM REPORT", "2025-08-28 17:59", "87001"), tdp)["action"] == "skip")
        (tdp / "02318_AnnualReport_2025.md").write_text(EN_SAMPLE * 10, encoding="utf-8")
        check("英文版到位後 → skip（不重複下載）", plan(a25, tdp)["action"] == "skip")
        check("aliases 含 _EN", "00941_AnnualReport_2025_EN" in aliases("00941_AnnualReport_2025"))
        # verify 與 prune
        stock = {"code": "02318", "name_en": "PING AN", "name_zh": "中國平安", "stockId": 7641}
        check("verify 英文 .md OK", verify_md(tdp / "02318_AnnualReport_2025.md", stock, "en")[0])
        bad = tdp / "zh_as_en.md"
        bad.write_text(ZH_SAMPLE * 10, encoding="utf-8")
        check("verify 預期英文但內容中文 → ❌", not verify_md(bad, stock, "en")[0])
        (tdp / "02318_annual_2025.pdf").write_bytes(b"%PDF-1.4")
        rm = prune_zh(tdp, ["02318_annual_2025.md"], tdp / "02318_AnnualReport_2025.md")
        check("prune_zh 刪中文 .md 與同名 .pdf", sorted(rm) == ["02318_annual_2025.md", "02318_annual_2025.pdf"], str(rm))
        check("prune_zh 不刪英文檔", prune_zh(tdp, ["02318_annual_2024.md"], tdp / "x.md") == [])
        (tdp / "00941_Quarter_2026Q3_EN.md").write_text(EN_SAMPLE, encoding="utf-8")
        (tdp / "00941_Quarter_2026Q3_EN.pdf").write_bytes(b"%PDF-1.4")
        check("drop_en_suffix：原名空出 → _EN 改回標準檔名",
              drop_en_suffix(tdp / "00941_Quarter_2026Q3_EN.md").name == "00941_Quarter_2026Q3.md"
              and (tdp / "00941_Quarter_2026Q3.pdf").is_file() and not (tdp / "00941_Quarter_2026Q3_EN.md").exists())
        check("drop_en_suffix：原名被佔 → 不改", drop_en_suffix(tdp / "00941_AnnualReport_2025_EN.md").name
              == "00941_AnnualReport_2025_EN.md")

    print("[selftest] 股份代號解析（模擬港交所股票清單）")
    fake = {"activestock_sehk_e": [{"i": 7641, "c": "02318", "n": "PING AN"}, {"i": 61711, "c": "87001", "n": "HUI XIAN REIT"},
                                   {"i": 1000194656, "c": "80016", "n": "SHK PPT-R"}],
            "activestock_sehk_c": [{"i": 7641, "c": "02318", "n": "中國平安"}, {"i": 61711, "c": "87001", "n": "匯賢產業信託"},
                                   {"i": 1000194656, "c": "80016", "n": "新鴻基地產－Ｒ"}],
            "inactivestock_sehk_e": [{"i": 76829, "c": "08001", "n": "ORIENTSEC INT"}, {"i": 5205, "c": "08001", "n": "TOM GROUP"}],
            "inactivestock_sehk_c": [{"i": 76829, "c": "08001", "n": "東方證券國際"}]}
    lists = fake.__getitem__
    check("2318 → 02318 stockId 7641 中國平安", (lambda s: (s["stockId"], s["name_zh"]))(resolve_stock("2318", lists))
          == (7641, "中國平安"))
    check("中文名 匯賢 → 87001", resolve_stock("匯賢", lists)["code"] == "87001")
    check("08001 不會誤配 80016（prefix.do 的坑）；已除牌取最新", resolve_stock("08001", lists)["stockId"] == 76829)
    try:
        resolve_stock("99999", lists)
        check("找不到 → NOT_FOUND", False)
    except HkexError as e:
        check("找不到 → NOT_FOUND", e.kind == "NOT_FOUND", e.kind)

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
    check(f"SKILL.md 版本 v{VERSION} 有寫進 §10", f"v{VERSION}" in text, "§10 變更紀錄漏寫本版")

    print("[selftest] .claude / .agents 鏡像同步")
    if (REPO_ROOT / ".agents").is_dir():
        for rel in ("SKILL.md", "scripts/hkexnews.py"):
            a1, a2 = REPO_ROOT / ".claude/skills/hkexnews" / rel, REPO_ROOT / ".agents/skills/hkexnews" / rel
            same = a1.is_file() and a2.is_file() and a1.read_bytes() == a2.read_bytes()
            check(f"鏡像一致 {rel}", same, "複製 .claude 版到 .agents（或跑 collectStk selfcheck.py --fix）")

    if not a.offline:
        print("[selftest] 線上：股票清單、群組搜尋、英文版連結")
        try:
            s = resolve_stock("02318")
            check("02318 → stockId 7641", s["stockId"] == 7641, str(s))
            docs = gather(s, date.today() - timedelta(days=800), date.today(), "EN")
            ann = [d for d in docs if d["_cat"] == "40100"]
            check("02318 近 800 天年報 ≥ 2 份", len(ann) >= 2, f"{len(ann)} 份")
            check("02318 有季度業績（13600）", any(d["_cat"] == "13600" for d in docs))
            check("英文搜尋的 FILE_LINK 是英文版（非 _c.pdf）", bool(ann) and all(d["_lang"] == "en" for d in ann),
                  str([d["FILE_LINK"] for d in ann]))
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
    ap = argparse.ArgumentParser(description=f"HKEXnews 港股年報/中報/季度業績下載器 v{VERSION}（英文版優先）")
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lookup", help="找 stockId")
    s.add_argument("query")
    s = sub.add_parser("selftest", help="自我檢查")
    s.add_argument("--offline", action="store_true", help="不連網（只跑邏輯、文件、鏡像檢查）")
    s = sub.add_parser("verify", help="Convert2md 後驗證 .md")
    s.add_argument("--code", help="只驗證這家公司（預設：上次 download 的公司）")
    s.add_argument("--prune-zh", action="store_true", help="英文版驗證通過後，刪掉被它取代的中文檔")
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
        s.add_argument("--lang", default="en", choices=["en", "zh"], help="en（預設，英文版優先）/ zh（只在英文版 CID 亂碼時用）")
        s.add_argument("--accept-zh", action="store_true", help="既有中文版視為已涵蓋，不補抓英文版")
        s.add_argument("--out", help="輸出資料夾（預設：repo 內以代號開頭的公司資料夾）")
        if name == "download":
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
    rows, cut = search(stock["stockId"], t1, t2g, t2, d_from, d_to, a.lang.upper(), rows=500)
    if cut:
        print(f"[hkexnews] ⚠ 超過 500 筆被截斷 → 縮短 --from／--to 區間", file=sys.stderr)
    if a.keyword:
        rx = re.compile(a.keyword, re.I)
        rows = [r for r in rows if rx.search(r["TITLE"]) or rx.search(r["LONG_TEXT"])]
    if a.json:
        print(json.dumps([{"date": f"{r['_date']:%Y-%m-%d %H:%M}", "docno": r["_docno"], "title": r["TITLE"],
                           "category": re.sub(r"^.*?\[|\]$", "", r["LONG_TEXT"]), "type": r.get("FILE_TYPE"),
                           "size": r.get("FILE_INFO"), "lang": r["_lang"], "url": BASE + r["FILE_LINK"]} for r in rows],
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


ACTION_LABEL = {"skip": "略過", "download": "下載", "upgrade": "補抓英文版"}


def _cmd_list_download(a) -> int:
    stock = resolve_stock(a.code)
    print(f"[hkexnews] 公司：{stock['code']} {stock['name_zh']} / {stock['name_en']}（stockId {stock['stockId']}"
          + ("，已除牌" if stock.get("status") == "inactive" else "") + "）", file=sys.stderr)
    t0 = time.time()
    docs, fye, fye_how = collect(stock, a.days, a.lang.upper(), a.fye_month, a.annual, a.periodic)
    scan_line = (f"近 {a.days} 天；決算月 {fye} 月（{fye_how}）；請求 {STATS['requests']} 次、"
                 f"重試 {STATS['retries']} 次；{time.time() - t0:.0f} 秒")
    print(f"[hkexnews] 掃描：{scan_line}", file=sys.stderr)
    sel = select(docs, a.annual, a.periodic, not a.no_latest)

    if a.cmd == "list":
        print("\n".join(_row(d) for d in docs) or "此區間 HKEXnews 無年報/中報/業績")
        try:
            out, created = resolve_out(argparse.Namespace(out=a.out, no_create=False), stock)
        except HkexError as e:
            print(f"\n[hkexnews] 無法決定輸出資料夾：{e}")
            out, created = None, True
        print(f"\n# download 預定動作（→ {out.name if out else '?'}{'，新資料夾' if created else ''}）")
        for d in sel:
            p = plan(d, out, accept_zh=a.accept_zh) if out and not created else \
                {"action": "download", "base": d["_base"], "note": ""}
            print(f"  {ACTION_LABEL[p['action']]:<6} {d['_base']} ← {d['_docno']}（{LANG_LABEL[d['_lang']]}）"
                  + (f" → {p['base']}.pdf" if p["action"] != "skip" else "") + (f"｜{p['note']}" if p["note"] else ""))
        for o in OBS:
            print(f"LEARN? {o}")
        return 0

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
        r = download_doc(d, out, a.force, a.accept_zh)
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
    zh_only = [r["doc"]["_base"] for r in results if r["lang"] != "en" and not r["doc"].get("_zh_requested")]
    if zh_only:
        gaps.append(f"HKEXnews 沒有英文版、改用中文版：{'、'.join(zh_only)}")
    n_up = sum(r["action"] == "upgrade" and r["status"] == "downloaded" for r in results)

    rel = out.relative_to(REPO_ROOT) if out.is_relative_to(REPO_ROOT) else out
    L = [f"## {datetime.now():%H:%M:%S} — {stock['code']} {stock['name_zh']} / {stock['name_en']}", "",
         f"- 指令：`hkexnews.py {' '.join(sys.argv[1:])}`", f"- 掃描：{scan_line}",
         f"- 輸出資料夾：`{rel}`" + ("（本次新建）" if created else ""), "- 文件："]
    for r in results:
        d = r["doc"]
        L.append(f"  - {d['_date']:%Y-%m-%d} `{d['_docno']}` {CAT[d['_cat']][2]}（{LANG_LABEL[r['lang']]}）期末 {d['_pe']}"
                 f" 「{d['TITLE'][:80]}」 → `{r['file']}`：{r['status']}（{r['note']}）｜{BASE}{d['FILE_LINK']}")
    if not results:
        L.append("  - （無）")
    if n_up:
        L.append(f"- 英文優先：{n_up} 份既有中文版已補抓英文版；verify 通過後用 `--prune-zh` 刪中文重複檔")
    if gaps:
        L += ["- 缺口與原因："] + [f"  - {g}" for g in gaps]
    L += _obs_lines()
    L.append(f"- 下一步：Convert2md（`<SCOPE>` = `{out}`）→ `hkexnews.py verify --code {stock['code']} --prune-zh`"
             if downloaded else "- 下一步：無新 PDF，免轉檔")
    sp = write_summary(L)
    runs = _load_manifest()  # 每家公司各存一筆：同一輪連續 download 多家後，verify 任一家都找得到
    runs["last"] = stock["code"]
    runs.setdefault("runs", {})[stock["code"]] = {
        "code": stock["code"], "folder": str(out), "stock": stock,
        "items": [{"base": r["file"][:-4], "status": r["status"], "cover": r.get("cover"), "lang": r["lang"],
                   "zh_dups": r["zh_dups"] if r["status"] == "downloaded" else [],
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
        print("[hkexnews] NEXT → 跑 Convert2md skill，<SCOPE> 用下面這個資料夾，轉完再 "
              f"`hkexnews.py verify --code {stock['code']} --prune-zh`：")
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
    bad, pending, changed = 0, [], False
    L = [f"## {datetime.now():%H:%M:%S} — verify {m['code']}（{out.name}）", ""]
    for it in items:
        md = out / Path(it.get("cover") or f"{it['base']}.pdf").with_suffix(".md").name
        if it["status"] == "skipped" and not md.is_file():
            line = f"- ➖ `{it['base']}`：由既有檔 `{it.get('cover')}` 涵蓋（非 .md，本次不驗證）"
        else:
            ok, note = verify_md(md, stock, it.get("lang") if it["status"] == "downloaded" else None)
            bad += not ok
            line = f"- {'✅' if ok else '❌'} `{md.name}`：{note}" + ("（既有檔）" if it["status"] == "skipped" else "")
            if not ok and it["status"] == "downloaded":
                observe(f"{md.name} 驗證失敗：{note}（來源 {it.get('url')}）")
            dups = [n for n in it.get("zh_dups") or [] if (out / n).is_file()]
            if ok and dups:
                if a.prune_zh:
                    rm = prune_zh(out, dups, md)
                    line += f"；已刪被取代的中文檔 {'、'.join(rm) or '（無）'}"
                    if (new := drop_en_suffix(md)) != md:  # 中文檔刪掉後原名空出 → _EN 改回標準檔名
                        line += f"；{md.name} 改名為 {new.name}"
                        it["cover"], it["base"] = new.with_suffix(".pdf").name, new.stem
                        it["zh_dups"] = []
                        changed = True
                else:
                    pending += dups
                    line += f"；中文重複檔 {'、'.join(dups)} 可刪（加 --prune-zh）"
        L.append(line)
        print(line)
    if changed:
        MANIFEST.write_text(json.dumps(runs, ensure_ascii=False, indent=1), encoding="utf-8")
    L += _obs_lines()
    sp = write_summary(L)
    for o in OBS:
        print(f"LEARN? {o}")
    print(f"[hkexnews] verify：{len(items) - bad}/{len(items)} 通過 → {sp}")
    if pending:
        print(f"PRUNE? 英文版已就緒、可刪的中文檔：{'、'.join(pending)} → `hkexnews.py verify --code {m['code']} --prune-zh`")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    a = parser.parse_args(argv)
    raw = argv if argv is not None else sys.argv[1:]
    try:
        if a.cmd == "lookup":
            s = resolve_stock(a.query)
            print(f"{s['code']}  stockId={s['stockId']}  {s['name_zh']} / {s['name_en']}"
                  + ("（已除牌）" if s.get("status") == "inactive" else ""))
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
