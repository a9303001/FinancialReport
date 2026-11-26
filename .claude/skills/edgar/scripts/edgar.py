#!/usr/bin/env python3
"""SEC EDGAR downloader — 美股（含 ADR／外國發行人）年報 10-K／20-F／40-F 與季報 10-Q／6-K.

只用 Python 標準函式庫（Windows / Linux / macOS / Claude Code 雲端皆可）。

子指令:
  checkua                                 檢查 User-Agent 與 SEC 連線（被擋會寫 Log/edgar_error.md）
  lookup   <查詢>                         用 ticker / CIK / 公司名找公司
  list     --code UHS                     列出年報/季報與預定檔名、本機是否已有（不下載）
  download --code UHS [--annual 2 --periodic 1] [--out DIR]
  verify   [--code UHS]                   Convert2md 之後驗證 .md（大小、CID、殘留標籤、公司名、表單與期末日）
  lesson   --section sec --key K --text T 把本次學到的經驗寫進 references/lessons.md（.claude/.agents 同步）
  hint     --code UHS --set k=v           設定公司特例（references/company_hints.json，下載時自動套用）
  selftest [--offline]                    自我檢查：命名、FY、6-K 期別判斷、既有檔判定、html2md、SKILL.md↔CLI、鏡像

User-Agent（SEC 規定要宣告聯絡方式；不是密鑰，但含個人 email，不要 commit）:
  1. 環境變數 SEC_EDGAR_USER_AGENT（與 sec-edgar-mcp 共用）
  2. <skill>/.env、<repo>/.claude/skills/edgar/.env、<repo>/.agents/skills/edgar/.env、~/.config/edgar/.env
  3. 預設通用值 DEFAULT_UA（2026-11 實測 SEC 接受）
結束碼：0 成功／1 一般錯誤／2 被 SEC 擋（BLOCKED：未宣告 UA 或超過 10 req/s）／3 腳本 bug（寫 SCRIPT_BUG）
"""
from __future__ import annotations

import argparse
import gzip
import html
import http.client
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import time
import traceback
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zlib
from datetime import date, datetime, timedelta
from pathlib import Path

VERSION = "1.0.0"

for _s in (sys.stdout, sys.stderr):  # Windows 主控台（cp950）→ UTF-8
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

WWW = "https://www.sec.gov"
DATA = "https://data.sec.gov"
TICKERS_URL = f"{WWW}/files/company_tickers.json"
DEFAULT_UA = f"FinancialReport-edgar-skill/{VERSION} (research; contact admin@example.com)"

SKILL_DIR = Path(__file__).resolve().parent.parent


def _find_repo_root() -> Path:
    env = os.environ.get("EDGAR_REPO")
    if env:
        return Path(env).expanduser().resolve()
    for p in SKILL_DIR.parents:
        if (p / ".git").exists() or (p / "AGENTS.md").is_file():
            return p
    return SKILL_DIR.parents[2]


REPO_ROOT = _find_repo_root()
LOG_DIR = REPO_ROOT / "Log"
ERROR_LOG = LOG_DIR / "edgar_error.md"
CACHE = Path(os.environ.get("EDGAR_CACHE_DIR") or (Path.home() / ".cache" / "edgar"))
MANIFEST = CACHE / "last_run.json"
MIRRORS = [REPO_ROOT / ".claude/skills/edgar", REPO_ROOT / ".agents/skills/edgar"]
HINTS_REL = "references/company_hints.json"
LESSONS_REL = "references/lessons.md"

ANNUAL = {"10-K", "10-K405", "10-KT", "20-F", "40-F"}
QUARTER = {"10-Q", "10-QT"}
SIXK = {"6-K"}
AMEND = {f + "/A" for f in ANNUAL | QUARTER}
FAMILY = {"10-K": "10-K", "10-K405": "10-K", "10-KT": "10-K", "10-Q": "10-Q", "10-QT": "10-Q",
          "20-F": "20-F", "40-F": "40-F", "6-K": "6-K"}
MIN_BYTES = 10 * 1024
SIXK_MIN_SIZE = int(os.environ.get("EDGAR_6K_MIN_SIZE", "400000"))  # 含財報的 6-K 整份提交通常 > 1MB
SIXK_MAX_PROBE = 12
SIXK_PROBE_BYTES = 1_500_000
BLOCK_KINDS = {"BLOCKED"}
OBS: list[str] = []  # 本次觀察（寫進執行報告，供 §9 經驗學習）


class EdgarError(Exception):
    def __init__(self, kind: str, msg: str, *, status: int | None = None, api_msg: str | None = None,
                 endpoint: str | None = None):
        super().__init__(msg)
        self.kind, self.status, self.api_msg, self.endpoint = kind, status, api_msg, endpoint


# ---------------------------------------------------------------- User-Agent
def _read_env_file(p: Path) -> str | None:
    try:
        lines = p.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return None
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            if k.strip().removeprefix("export ").strip() == "SEC_EDGAR_USER_AGENT":
                return v.strip().strip('"').strip("'") or None
    return None


def get_ua() -> tuple[str, str]:
    v = os.environ.get("SEC_EDGAR_USER_AGENT", "").strip().strip('"').strip("'")
    if v:
        return v, "環境變數 SEC_EDGAR_USER_AGENT"
    for p in (SKILL_DIR / ".env", *(m / ".env" for m in MIRRORS), Path.home() / ".config/edgar/.env"):
        if p.is_file() and (v := _read_env_file(p)):
            return v, str(p)
    return DEFAULT_UA, "預設通用值"


def ua_note(ua: str) -> str:
    return "格式正常（含聯絡 email）" if re.search(r"\S+@\S+\.\w+", ua) else "⚠ 沒有 email：SEC 可能回 403 Undeclared Automated Tool"


# ---------------------------------------------------------------- HTTP（SEC 上限 10 req/s）
MIN_INTERVAL = float(os.environ.get("EDGAR_MIN_INTERVAL", "0.15"))
_lock = threading.Lock()
_next = [0.0]
STATS = {"requests": 0, "retry": 0}
BLOCK_MARKERS = ("Undeclared Automated Tool", "Request Rate Threshold Exceeded", "Your Request Originates")


def _throttle() -> None:
    with _lock:
        now = time.monotonic()
        wait = _next[0] - now
        _next[0] = max(now, _next[0]) + MIN_INTERVAL
        STATS["requests"] += 1
    if wait > 0:
        time.sleep(wait)


def _decompress(data: bytes, enc: str) -> bytes:
    enc = (enc or "").lower()
    if "gzip" in enc or data[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(data)
        except (OSError, EOFError):  # Range 截斷的 gzip → 盡量解
            return zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(data)
    if "deflate" in enc:
        return zlib.decompress(data)
    return data


def http_get(url: str, *, limit: int | None = None, retries: int = 5) -> tuple[bytes, str]:
    ua, _ = get_ua()
    headers = {"User-Agent": ua, "Accept-Encoding": "gzip, deflate"}
    if limit:
        headers["Range"] = f"bytes=0-{limit - 1}"
        headers["Accept-Encoding"] = "identity"
    endpoint = urllib.parse.urlsplit(url).path
    err = ""
    for i in range(retries):
        _throttle()
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read(limit) if limit else r.read()
                data = _decompress(raw, r.headers.get("Content-Encoding", ""))
                ctype = r.headers.get("Content-Type", "")
            head = data[:3000].decode("latin-1", "replace")
            if any(m in head for m in BLOCK_MARKERS):
                raise EdgarError("BLOCKED", "SEC 回傳封鎖頁", status=200, api_msg=_text_head(head), endpoint=endpoint)
            if "Directory listing is Not Available" in head:
                raise EdgarError("NOT_FOUND", "SEC 目錄尚未公開／accession 錯誤", status=200, endpoint=endpoint)
            return data, ctype
        except urllib.error.HTTPError as e:
            body = _decompress(e.read()[:4000], e.headers.get("Content-Encoding", "")).decode("utf-8", "replace")
            if e.code == 403:
                raise EdgarError("BLOCKED", "HTTP 403", status=403, api_msg=_text_head(body), endpoint=endpoint)
            if e.code == 404:
                raise EdgarError("NOT_FOUND", "HTTP 404", status=404, endpoint=endpoint)
            if e.code == 429 or e.code >= 500:
                err = f"HTTP {e.code}"
                STATS["retry"] += 1
                with _lock:
                    _next[0] = max(_next[0], time.monotonic() + min(60, 5 * 2 ** i))
                continue
            raise EdgarError("API_ERROR", f"HTTP {e.code}", status=e.code, api_msg=_text_head(body), endpoint=endpoint)
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException) as e:
            err = str(e)
            STATS["retry"] += 1
            time.sleep(min(30, 2 ** i))
    raise EdgarError("RATE_LIMIT" if "429" in err else "NETWORK", f"已重試 {retries} 次仍失敗：{err}", endpoint=endpoint)


def _text_head(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()[:300]


def cached_json(url: str, name: str, max_age: float) -> dict:
    p = CACHE / name
    if p.is_file() and time.time() - p.stat().st_mtime < max_age:
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            p.unlink(missing_ok=True)
    data, _ = http_get(url)
    j = json.loads(data.decode("utf-8"))
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(j), encoding="utf-8")
    tmp.replace(p)
    return j


# ---------------------------------------------------------------- hints（公司特例，自動學習）
def load_hints() -> dict:
    p = SKILL_DIR / HINTS_REL
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
    except ValueError as e:
        raise EdgarError("SCRIPT_BUG", f"{p} 不是合法 JSON：{e}") from e


def save_hints(h: dict) -> None:
    text = json.dumps(dict(sorted(h.items())), ensure_ascii=False, indent=1) + "\n"
    for m in {SKILL_DIR, *MIRRORS}:
        if m.is_dir():
            (m / HINTS_REL).parent.mkdir(parents=True, exist_ok=True)
            (m / HINTS_REL).write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- company
def _norm(s: str) -> str:
    return re.sub(r"[^0-9a-z぀-鿿]", "", unicodedata.normalize("NFKC", s or "").lower())


def load_tickers() -> list[dict]:
    j = cached_json(TICKERS_URL, "company_tickers.json", 7 * 86400)
    return [{"cik": int(v["cik_str"]), "ticker": v["ticker"], "title": v["title"]} for v in j.values()]


def lookup(q: str, rows: list[dict]) -> list[dict]:
    qs = q.strip()
    if qs.isdigit() and len(qs) <= 10:
        hit = [r for r in rows if r["cik"] == int(qs)]
        return hit[:1] or [{"cik": int(qs), "ticker": "", "title": f"CIK {int(qs)}"}]
    t = qs.upper().replace(".", "-").replace("/", "-")
    exact = [r for r in rows if r["ticker"].upper() == t]
    if exact:
        return exact[:1]
    n = _norm(qs)
    out, seen = [], set()
    for r in rows:
        if len(n) >= 3 and n in _norm(r["title"]) and r["cik"] not in seen:
            seen.add(r["cik"])
            out.append(r)
    return out


def resolve_company(code: str) -> dict:
    hints = load_hints()
    h = hints.get(code.upper())
    try:
        hits = lookup(code, load_tickers())
    except EdgarError:
        if h and h.get("cik"):  # 代碼表抓不到 → 用上次學到的 CIK
            return {"cik": int(h["cik"]), "ticker": code.upper(), "title": h.get("title", "")}
        raise
    if not hits:
        raise EdgarError("NOT_FOUND", f"SEC 代碼表找不到「{code}」：可能是未在 SEC 註冊的 ADR（unsponsored/OTC，如 HEGIY）、"
                         "已下市或代碼打錯 → 先跑 `edgar.py lookup 公司名`；仍無 → 改走官網 IR／財報狗／富途（collectStk §7.3）")
    if len(hits) > 1:
        lines = "\n".join(f"  CIK {r['cik']:<10} {r['ticker']:<8} {r['title']}" for r in hits[:15])
        raise EdgarError("AMBIGUOUS", f"「{code}」對到多家公司，請改用 ticker 或 CIK：\n{lines}")
    return hits[0]


# ---------------------------------------------------------------- submissions / companyfacts
def load_submissions(cik: int) -> dict:
    return cached_json(f"{DATA}/submissions/CIK{cik:010d}.json", f"subs/CIK{cik:010d}.json", 6 * 3600)


def _rows_from(block: dict) -> list[dict]:
    keys = ("accessionNumber", "filingDate", "reportDate", "form", "primaryDocument",
            "primaryDocDescription", "size", "isXBRL", "isInlineXBRL")
    n = len(block.get("accessionNumber", []))
    return [{k: (block.get(k) or [None] * n)[i] for k in keys} for i in range(n)]


def filings(subs: dict, cutoff: date) -> list[dict]:
    """recent（最近 1000 筆或 1 年）不夠回溯到 cutoff 時，自動補抓 filings.files 的舊分頁。"""
    rows = _rows_from(subs["filings"]["recent"])
    for f in subs["filings"].get("files", []):
        oldest = min((r["filingDate"] for r in rows), default="9999")
        if oldest <= cutoff.isoformat():
            break
        OBS.append(f"submissions recent 只到 {oldest}，補抓舊分頁 {f['name']}（大量申報公司常見，如發大量 424B2 的銀行）")
        j = cached_json(f"{DATA}/submissions/{f['name']}", f"subs/{f['name']}", 7 * 86400)
        rows += _rows_from(j)
    return rows


def load_dei(cik: int) -> tuple[dict, dict | None]:
    """companyfacts → {accession: (fy, fp)}、最新流通股數。沒有 XBRL（舊 6-K、小公司）→ 空。"""
    try:
        j = cached_json(f"{DATA}/api/xbrl/companyfacts/CIK{cik:010d}.json", f"facts/CIK{cik:010d}.json", 86400)
    except EdgarError as e:
        if e.kind == "NOT_FOUND":
            return {}, None
        raise
    m: dict[str, tuple[int, str]] = {}
    for tax in j.get("facts", {}).values():
        for con in tax.values():
            for arr in con.get("units", {}).values():
                for x in arr:
                    if x.get("accn") and x.get("fy") and x.get("fp") and x["accn"] not in m:
                        m[x["accn"]] = (int(x["fy"]), str(x["fp"]))
    so = (j.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding", {})
          .get("units", {}).get("shares", []))
    shares = max(so, key=lambda x: (x.get("end", ""), x.get("filed", ""))) if so else None
    return m, shares


def filer_type(rows: list[dict]) -> str:
    forms = {r["form"] for r in rows}
    if forms & (ANNUAL - {"20-F", "40-F"} | QUARTER):
        return "domestic"
    if forms & {"20-F", "40-F", "6-K"}:
        return "fpi"
    return "unknown"


# ---------------------------------------------------------------- 日期 / FY / 命名
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
MONTHS["sept"] = 9
DATE_US = r"([A-Za-z]{3,9})\.?\s+(\d{1,2})\s*,\s*(\d{4})"
DATE_UK = r"(\d{1,2})\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})"


def _mk(y: str, mon: str, d: str) -> date | None:
    m = MONTHS.get(mon.lower())
    try:
        return date(int(y), m, int(d)) if m else None
    except ValueError:
        return None


def parse_date(s: str) -> date | None:
    s = s.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        try:
            return date.fromisoformat(s)
        except ValueError:
            return None
    if m := re.fullmatch(DATE_US, s):
        return _mk(m.group(3), m.group(1), m.group(2))
    if m := re.fullmatch(DATE_UK, s):
        return _mk(m.group(3), m.group(2), m.group(1))
    return None


def _eff(d: date) -> tuple[int, int]:
    """52/53 週會計年度：期末落在月初 1–7 日視為上個月底（如 2026-01-03 → 2025/12）。"""
    if d.day <= 7:
        return (d.year - 1, 12) if d.month == 1 else (d.year, d.month - 1)
    return d.year, d.month


def fye_month(subs: dict) -> int | None:
    v = str(subs.get("fiscalYearEnd") or "")
    if not re.fullmatch(r"\d{4}", v):
        return None
    m, d = int(v[:2]), int(v[2:])
    if d <= 7:
        m = 12 if m == 1 else m - 1
    return m if 1 <= m <= 12 else None


def fy_of(pe: date, fyem: int | None) -> int:
    y, m = _eff(pe)
    if not fyem:
        return y
    return y if m <= fyem else y + 1


def q_of(pe: date, fyem: int | None) -> int:
    if not fyem:
        return 0
    k = (_eff(pe)[1] - fyem) % 12
    return 4 if k == 0 else max(1, min(4, round(k / 3)))


def target_name(item: dict, ticker: str, fyem: int | None, dei: dict) -> tuple[str, str | None]:
    """回傳 (檔名主幹, 觀察訊息)。年度與季別優先用 XBRL DEI（DocumentFiscalYearFocus/PeriodFocus）。"""
    form = item["form"].removesuffix("/A")
    pe = parse_date(item.get("period") or item.get("reportDate") or "")
    amend = "_Amend" + item["accessionNumber"].replace("-", "") if item["form"].endswith("/A") else ""
    if pe is None:
        return f"{ticker}_{form.replace('-', '')}_{item['accessionNumber']}", "無期末日 → 用 accession 命名"
    d = dei.get(item["accessionNumber"])
    note = None
    if form in ANNUAL:
        fy = fy_of(pe, fyem)
        if d and d[1] == "FY" and d[0] != fy:
            note = f"{item['form']} 期末 {pe}：日期推算 FY{fy}，DEI 標 FY{d[0]} → 採 DEI（公司慣例，如零售業 1 月底結帳）"
            fy = d[0]
        return f"{ticker}_AnnualReport_{fy}{amend}", note
    fy, q = fy_of(pe, fyem), q_of(pe, fyem)
    if d and re.fullmatch(r"Q[1-4]", d[1]) and (d[0], int(d[1][1])) != (fy, q):
        note = f"{item['form']} 期末 {pe}：日期推算 {fy}Q{q}，DEI 標 {d[0]}{d[1]} → 採 DEI"
        fy, q = d[0], int(d[1][1])
    tag = "H1" if item.get("h1") else f"Q{q}"
    return f"{ticker}_Quarter_{fy}{tag}{amend}", note


# ---------------------------------------------------------------- 既有檔判定（看檔名 + 檔頭內容）
FORM_RE = re.compile(r"\bFORM\s*(10-K405|10-KT|10-K|10-QT|10-Q|20-F|40-F|6-K)(\s*/\s*A\b)?", re.I)
PERIOD_RE = re.compile(r"(?:fiscal\s+year|quarterly\s+period|year|period)\s+ended\s*:?\s*" + DATE_US, re.I)
NOT_FILING_RE = re.compile(r"AnalysisResult|PublicOpinion|輿情|Analysis|Orange|IR$|_Presentation_", re.I)


def _head_text(p: Path, n: int = 15000) -> str:
    try:
        with p.open(encoding="utf-8", errors="replace") as f:
            s = f.read(n)
    except OSError:
        return ""
    if p.suffix.lower() in (".htm", ".html"):
        s = re.sub(r"(?is)<ix:header.*?</ix:header>", " ", s)
        s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = re.sub(r"[|#*_>]", " ", s.replace("​", "").replace("\xa0", " "))
    return re.sub(r"\s+", " ", s)


def doc_identity(p: Path) -> tuple[str, date | None, bool] | None:
    """(表單家族, 期末日, 是否修正) — 從檔頭讀；認不出表單 → None。"""
    if p.suffix.lower() not in (".md", ".htm", ".html") or NOT_FILING_RE.search(p.stem):
        return None
    s = _head_text(p)
    m = FORM_RE.search(s, 0, 5000)  # 真正的申報檔封面在最前面；分析檔內文提到 "Form 10-K" 不算
    if not m:
        return None
    fam = FAMILY.get(m.group(1).upper(), m.group(1).upper())
    pm = PERIOD_RE.search(s, m.start(), m.start() + 4000)
    pe = _mk(pm.group(3), pm.group(1), pm.group(2)) if pm else None
    return fam, pe, bool(m.group(2))


def _same(ident, fam: str, pe: date | None, amend: bool) -> bool:
    if ident is None:
        return True  # 認不出內容 → 保守視為同一份（避免重複下載），報告會提示
    f2, pe2, a2 = ident
    if f2 != fam or a2 != amend:
        return False
    return pe is None or pe2 is None or abs((pe - pe2).days) <= 7


def aliases(base: str, item: dict, ticker: str) -> list[str]:
    out = [base]
    pe = parse_date(item.get("period") or item.get("reportDate") or "")
    m = re.match(r"^(.+?)_(AnnualReport|Quarter)_(\d{4})(Q[1-4]|H1)?$", base)
    if m:
        t, kind, fy, q = m.groups()
        if kind == "AnnualReport":
            out.append(f"{t}_annual_{fy}")
        else:
            out += [f"{t}_quarter_{fy}{q}", f"{t}_QuarterlyReport_{fy}{q}"]
            if q in ("Q2", "H1"):
                alt = "H1" if q == "Q2" else "Q2"
                out += [f"{t}_Quarter_{fy}{alt}", f"{t}_interim_{fy}"]
    if pe and not item["form"].endswith("/A"):
        fam = FAMILY.get(item["form"], "").replace("-", "")
        out += [f"{ticker}_{fam}_{pe.isoformat()}", f"{ticker.lower()}-{pe:%Y%m%d}"]
    if item.get("primaryDocument") and item["form"] != "6-K":
        out.append(Path(item["primaryDocument"]).stem)
    return list(dict.fromkeys(out))


def existing_cover(out: Path, base: str, item: dict, ticker: str) -> Path | None:
    if not out.is_dir():
        return None
    fam = FAMILY.get(item["form"].removesuffix("/A"), "")
    pe = parse_date(item.get("period") or item.get("reportDate") or "")
    amend = item["form"].endswith("/A")
    files = {p.name.lower(): p for p in out.iterdir() if p.is_file()}
    for b in aliases(base, item, ticker) + [base + "_EDGAR"]:
        for ext in (".md", ".htm", ".html", ".pdf"):
            hit = files.get((b + ext).lower())
            if hit and (ext == ".pdf" or _same(doc_identity(hit), fam, pe, amend)):
                return hit
    if fam in ("10-K", "10-Q", "20-F", "40-F"):  # 任意檔名：看內容（如 UHS_10K_2025-12-31.md、evtc-20260630.md）
        for p in files.values():
            if p.suffix.lower() == ".md" and (ident := doc_identity(p)) and pe and ident[1] \
                    and _same(ident, fam, pe, amend):
                return p
    return None


def name_taken_by_other(out: Path, base: str, item: dict) -> Path | None:
    p = out / f"{base}.md"
    if not p.is_file():
        return None
    fam = FAMILY.get(item["form"].removesuffix("/A"), "")
    pe = parse_date(item.get("period") or item.get("reportDate") or "")
    ident = doc_identity(p)
    if ident is None:
        s = _head_text(p, 4000).lower()
        if re.search(r"press release|reports? (?:first|second|third|fourth)[- ]quarter|earnings (?:release|call)", s):
            return p  # 新聞稿／法說稿佔了檔名
        return None
    return None if _same(ident, fam, pe, item["form"].endswith("/A")) else p


# ---------------------------------------------------------------- filing index / 6-K 判斷
def acc_dir(cik: int, acc: str) -> str:
    return f"{WWW}/Archives/edgar/data/{cik}/{acc.replace('-', '')}"


def filing_index(cik: int, acc: str) -> list[dict]:
    """解析 {acc}-index.htm 的文件表：Seq / Description / Document / Type / Size。"""
    p = CACHE / "index" / f"{acc}.json"
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    data, _ = http_get(f"{acc_dir(cik, acc)}/{acc}-index.htm")
    t = data.decode("utf-8", "replace")
    docs = []
    for row in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", t):
        cells = re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)
        if len(cells) < 4:
            continue
        txt = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in cells]
        href = re.search(r'href="([^"]+)"', cells[2])
        name = Path(urllib.parse.urlsplit(href.group(1)).path).name if href else txt[2].split()[0] if txt[2] else ""
        if name.startswith("ix?doc="):
            name = Path(name).name
        docs.append({"seq": txt[0], "desc": txt[1], "doc": name, "type": txt[3],
                     "size": int(re.sub(r"\D", "", txt[4]) or 0) if len(txt) > 4 else 0})
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")
    return docs


FS_KW = [r"statements? of financial position", r"balance sheets?", r"statements? of (?:profit or loss|income|operations)",
         r"income statements?", r"statements? of comprehensive income", r"statements? of cash flows?",
         r"changes in (?:shareholders'?|stockholders'?)?\s*equity", r"notes to the (?:interim )?(?:condensed )?consolidated",
         r"interim (?:condensed )?(?:consolidated )?financial", r"unaudited"]
# (regex, 日期格式, 期間詞所在 group)；期間詞決定是否「只有半年」(H1)
PERIOD_PATS = [
    (re.compile(r"(three|six|nine|twelve|3|6|9|12)[- ]months?\s+(?:period\s+)?ended\s+" + DATE_US, re.I), "us", 1),
    (re.compile(r"(three|six|nine|twelve|3|6|9|12)[- ]months?\s+(?:period\s+)?ended\s+" + DATE_UK, re.I), "uk", 1),
    (re.compile(r"(first|second|third|fourth)\s+(half|quarter)\b[^.]{0,40}?ended\s+" + DATE_US, re.I), "us", 2),
    (re.compile(r"(?:ended|through)\s+" + DATE_US, re.I), "us", 0),
    (re.compile(r"(?:ended|through)\s+" + DATE_UK, re.I), "uk", 0),
    (re.compile(r"as\s+(?:of|at)\s+" + DATE_US, re.I), "us", 0),
    (re.compile(r"as\s+(?:of|at)\s+" + DATE_UK, re.I), "uk", 0),
]
HALF_TOK = {"six", "6", "half"}


def html_text(raw: bytes) -> str:
    t = raw.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style|ix:header)[^>]*>.*?</\1>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).replace("\u200b", "")


def score_6k_text(s: str, filed: date | None = None) -> dict:
    """6-K 文件是否為財報、期末日、是否只有半年（H1）。
    期末日 = 出現次數 ≥ max(2, 最高次數 × 25%) 的日期中「最新且不晚於提交日」者——
    比較期（去年同期、去年底）出現次數常和本期一樣多，不能取最常出現的（TM 2026-08 實測）。"""
    score = sum(1 for k in FS_KW if re.search(k, s, re.I))
    count: dict[date, int] = {}
    toks: dict[date, set] = {}
    for pat, fmt, tg in PERIOD_PATS:
        for m in pat.finditer(s):
            g = m.groups()[-3:]
            dd = _mk(g[2], g[0], g[1]) if fmt == "us" else _mk(g[2], g[1], g[0])
            if not dd or (filed is not None and dd > filed):
                continue  # 財測（如 FY 結束日）晚於提交日 → 不是本期
            count[dd] = count.get(dd, 0) + 1
            if tg:
                toks.setdefault(dd, set()).add(m.group(tg).lower())
    pe = None
    if count:
        floor = max(2, max(count.values()) * 0.25)
        ok = [d for d, n in count.items() if n >= floor] or [max(count, key=count.get)]
        pe = max(ok)
    ts = toks.get(pe, set()) if pe else set()
    h1 = bool(ts & HALF_TOK) and not (ts - HALF_TOK)
    return {"score": score, "period": pe.isoformat() if pe else None, "h1": h1}


def probe_6k(cik: int, row: dict, prefer_type: str | None) -> dict | None:
    cache = CACHE / "probe6k.json"
    allc = json.loads(cache.read_text(encoding="utf-8")) if cache.is_file() else {}
    acc = row["accessionNumber"]
    if acc in allc:
        return allc[acc] or None
    filed = parse_date(row["filingDate"])
    best = None
    for d in filing_index(cik, acc):
        ext = Path(d["doc"]).suffix.lower()
        if ext not in (".htm", ".html") or not (d["type"] == "6-K" or d["type"].startswith("EX-99")
                                                 or d["type"].startswith("EX-13")):
            continue
        raw, _ = http_get(f"{acc_dir(cik, acc)}/{d['doc']}", limit=SIXK_PROBE_BYTES)
        r = score_6k_text(html_text(raw), filed)
        r.update(doc=d["doc"], type=d["type"], desc=d["desc"], size=d["size"])
        bonus = 2 if prefer_type and d["type"] == prefer_type else 0
        if r["period"] and r["score"] + bonus >= 3 and (
                best is None or (r["score"] + bonus, d["size"]) > (best["score"], best["size"])):
            r["score"] += bonus
            best = r
    allc[acc] = best or {}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(allc, ensure_ascii=False), encoding="utf-8")
    return best


def select_6k(cik: int, rows: list[dict], n: int, hint: dict) -> list[dict]:
    if n <= 0:
        return []
    min_size = int(hint.get("sixk_min_size") or SIXK_MIN_SIZE)
    cands = sorted((r for r in rows if r["form"] == "6-K" and (r["size"] or 0) >= min_size),
                   key=lambda r: r["filingDate"], reverse=True)
    if not cands:
        OBS.append(f"沒有 ≥ {min_size} bytes 的 6-K（季報可能只放新聞稿或 PDF）→ 可用 `hint --set sixk_min_size=…` 調低")
        return []
    newest = parse_date(cands[0]["filingDate"])
    cands = [r for r in cands if newest and (newest - parse_date(r["filingDate"])).days <= 200][:SIXK_MAX_PROBE]
    print(f"[edgar] 6-K：檢查 {len(cands)} 份大型 6-K 的附件找財報", file=sys.stderr)
    found = []
    for r in cands:
        b = probe_6k(cik, r, hint.get("sixk_doc_type"))
        if b:
            found.append(dict(r, period=b["period"], h1=b["h1"], doc=b["doc"], doc_type=b["type"],
                              doc_desc=b["desc"], score=b["score"]))
    found.sort(key=lambda r: (r["period"], r["score"], r["filingDate"]), reverse=True)
    out, seen = [], set()
    for r in found:
        if r["period"] not in seen:
            seen.add(r["period"])
            out.append(r)
    if out and out[0]["accessionNumber"] != cands[0]["accessionNumber"]:
        OBS.append(f"最新提交的 6-K（{cands[0]['filingDate']}）不是最新一期財報；依期末日改選 "
                   f"{out[0]['filingDate']}（期末 {out[0]['period']}）。同一期財報可能重送（如 TLK 2026-11-25 重送 H1）")
    if not out:
        OBS.append("大型 6-K 都沒找到財報期末日／財報關鍵字 → 可能是 PDF 附件或新格式，請人工確認後用 hint 記下")
    return out[:n]


# ---------------------------------------------------------------- 資料夾 / 下載
def find_company_folder(ticker: str) -> list[Path]:
    """美股資料夾 = ticker 本身（UHS/），或 ticker 後接非 ASCII（TLK印尼電信/）；不誤配 AES-KY、CFG。"""
    return [p for p in REPO_ROOT.iterdir() if p.is_dir() and (
        p.name == ticker or (p.name.startswith(ticker) and len(p.name) > len(ticker)
                             and not p.name[len(ticker)].isascii()))]


def resolve_out(a, ticker: str, hint: dict) -> tuple[Path, bool]:
    if a.out:
        return Path(a.out).expanduser().resolve(), False
    if hint.get("folder") and (REPO_ROOT / hint["folder"]).is_dir():
        return REPO_ROOT / hint["folder"], False
    c = sorted(set(find_company_folder(ticker)))
    if len(c) == 1:
        return c[0], False
    if len(c) > 1:
        raise EdgarError("AMBIGUOUS", f"repo 內有多個「{ticker}」資料夾：{', '.join(p.name for p in c)} → 用 --out 指定")
    if getattr(a, "no_create", False) or a.cmd == "list":  # list 只看不建資料夾
        raise EdgarError("NOT_FOUND", f"repo 內找不到「{ticker}」資料夾，請用 --out 指定")
    return REPO_ROOT / ticker, True


def _valid(data: bytes, ext: str) -> str | None:
    if len(data) < MIN_BYTES:
        return f"檔案太小（{len(data)} bytes < 10KB）"
    if ext == ".pdf":
        return None if data.startswith(b"%PDF") else "不是 PDF（檔頭不是 %PDF）"
    head = data[:5000].decode("latin-1", "replace").lower()
    return None if ("<html" in head or "<?xml" in head or "<document" in head or "<body" in head) \
        else "不是 HTML"


def _write(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False, suffix=".part") as tf:
        tf.write(data)
    um = os.umask(0)
    os.umask(um)
    os.chmod(tf.name, 0o666 & ~um)
    Path(tf.name).replace(dest)


def download_item(cik: int, item: dict, out: Path, base: str, ticker: str, force: bool) -> list[dict]:
    res = []
    doc = item.get("doc") or item["primaryDocument"]
    ext = Path(doc).suffix.lower()
    if ext not in (".htm", ".html", ".pdf"):
        return [{"file": doc, "status": "unavailable", "note": f"主文件是 {ext}（多為 2001 年前純文字申報），不處理"}]
    other = name_taken_by_other(out, base, item)
    if other is not None:
        base += "_EDGAR"
        OBS.append(f"{other.name} 不是 {item['form']}（新聞稿或別期），新檔改存 {base}")
    r = {"file": f"{base}{'.pdf' if ext == '.pdf' else '.htm'}", "status": "", "note": "", "base": base}
    if other is not None:
        r["note"] = f"{other.name} 是別種文件；"
    if not force and (hit := existing_cover(out, base, item, ticker)):
        pending = hit.suffix.lower() in (".htm", ".html", ".pdf")
        if doc_identity(hit) is None and hit.suffix.lower() == ".md":
            OBS.append(f"既有檔 {hit.name} 檔頭認不出表單，保守視為已有；若其實不是 {item['form']}，請改名或用 --force")
        r.update(status="pending-convert" if pending else "skipped", note=f"已存在 {hit.name}", cover=hit.name)
        res.append(r)
    else:
        data, _ = http_get(f"{acc_dir(cik, item['accessionNumber'])}/{doc}")
        if (bad := _valid(data, ext)) is not None:
            r.update(status="failed", note=bad)
            res.append(r)
            return res
        _write(out / r["file"], data)
        r.update(status="downloaded", note=r["note"] + f"{len(data) / 1024:.0f} KB", cover=r["file"])
        if len(data) < 200_000 and FAMILY.get(item["form"].removesuffix("/A")) in ("10-K", "20-F", "40-F"):
            OBS.append(f"{item['form']} {item['accessionNumber']} 主文件只有 {len(data) // 1024} KB → 財報可能在附件"
                       "（EX-13 年報、20-F 的 EX-15/99）；請看 filing index 確認並寫入 lessons")
        res.append(r)
    # 10-K 把財報放在 EX-13（給股東的年報）的公司：一併下載
    if FAMILY.get(item["form"].removesuffix("/A")) == "10-K":
        for d in filing_index(cik, item["accessionNumber"]):
            if d["type"].startswith("EX-13") and Path(d["doc"]).suffix.lower() in (".htm", ".html"):
                b13 = f"{base}_EX13"
                r13 = {"file": f"{b13}.htm", "base": b13, "status": "", "note": ""}
                hit = next((out / f"{b13}{e}" for e in (".md", ".htm") if (out / f"{b13}{e}").is_file()), None)
                if hit and not force:
                    r13.update(status="skipped" if hit.suffix == ".md" else "pending-convert",
                               note=f"已存在 {hit.name}", cover=hit.name)
                else:
                    data, _ = http_get(f"{acc_dir(cik, item['accessionNumber'])}/{d['doc']}")
                    _write(out / r13["file"], data)
                    r13.update(status="downloaded", note=f"EX-13 {d['desc']} {len(data) / 1024:.0f} KB", cover=r13["file"])
                    OBS.append(f"{ticker} 10-K 的財報在 EX-13（{d['desc']}）→ 已一併下載 {b13}")
                res.append(r13)
                break
    return res


# ---------------------------------------------------------------- 選件
def plan(code: str, a) -> dict:
    company = resolve_company(code)
    cik = company["cik"]
    hints = load_hints()
    ticker = (getattr(a, "ticker", None) or company["ticker"] or str(cik)).upper()
    hint = hints.get(ticker, {})
    subs = load_submissions(cik)
    cutoff = date.today() - timedelta(days=a.days)
    rows = filings(subs, cutoff)
    ftype = filer_type(rows)
    fyem = fye_month(subs)
    dei, shares = load_dei(cik)
    n_a = a.annual if a.annual is not None else 2
    n_p = a.periodic if a.periodic is not None else 1
    inwin = [r for r in rows if (r["filingDate"] or "") >= cutoff.isoformat()]

    def latest(forms: set, n: int) -> list[dict]:
        c = sorted((r for r in inwin if r["form"] in forms), key=lambda r: (r["reportDate"] or "", r["filingDate"]),
                   reverse=True)
        out, seen = [], set()
        for r in c:
            if r["reportDate"] not in seen:  # 同期多份（重送）只取最新提交
                seen.add(r["reportDate"])
                out.append(r)
        return out[:n]

    sel = latest(ANNUAL, n_a)
    if ftype == "fpi":
        sel += select_6k(cik, [r for r in rows if (r["filingDate"] or "") >= (date.today() - timedelta(days=400)).isoformat()],
                         n_p, hint)
    else:
        sel += latest(QUARTER, n_p)
    if a.include_amendments:
        sel += [r for r in inwin if r["form"] in AMEND]
    items = []
    for r in sel:
        base, note = target_name(r, ticker, fyem, dei)
        if note:
            OBS.append(note)
        items.append(dict(r, base=base))
    return {"company": company, "cik": cik, "ticker": ticker, "hint": hint, "subs": subs, "ftype": ftype,
            "fyem": fyem, "shares": shares, "items": items, "n_a": n_a, "n_p": n_p,
            "got_a": sum(r["form"] in ANNUAL for r in sel),
            "got_p": sum(r["form"] in QUARTER | SIXK for r in sel)}


def _row(r: dict) -> str:
    extra = f" doc={r['doc']}({r['doc_type']})" if r.get("doc") else ""
    return (f"{r['filingDate']}  {r['form']:<6} 期末 {r.get('period') or r['reportDate'] or '?':<10}  "
            f"{r['accessionNumber']}  → {r['base']}{extra}")


# ---------------------------------------------------------------- logs
ERROR_HEADER = """# SEC EDGAR 錯誤報告

> 由 `.claude/skills/edgar/scripts/edgar.py` 自動寫入，最新在最上面（最多保留 50 筆）。
> 種類：`BLOCKED`（SEC 擋 UA／超過 10 req/s，優先處理）、`RATE_LIMIT`、`NETWORK`、`API_ERROR`、`NOT_FOUND`、`AMBIGUOUS`、`SCRIPT_BUG`（AI 依 SKILL.md §9 自我修正）、`SELFTEST_FAIL`。

<!-- entries -->
"""

FIX_BLOCKED = [
    "SEC 規定自動程式要宣告 User-Agent（`名稱 email`），且全站 ≤ 10 req/s；超過會被封鎖約 10 分鐘。",
    "設環境變數 `SEC_EDGAR_USER_AGENT=\"YourName your@email\"`（Windows `setx`；macOS/Linux 寫進 `~/.bashrc`），"
    "或把 `.claude/skills/edgar/.env.example` 複製成 `.env` 填入（`.env` 不會被 commit）。",
    "被限流：等 10 分鐘再跑；或設 `EDGAR_MIN_INTERVAL=0.3` 放慢。",
    "雲端：代理若回 403（不是 SEC 頁面），見 `/root/.ccr/README.md`；`www.sec.gov`、`data.sec.gov` 需在允許清單。",
    "在修好之前：改走 collectStk §7.3 美股的其他來源（官網 IR、財報狗、富途），報告寫明。",
]


def log_error(e: EdgarError | None, argv: list[str], *, kind: str | None = None, detail: str = "",
              tb: str | None = None) -> Path:
    kind = kind or (e.kind if e else "SCRIPT_BUG")
    ua, src = get_ua()
    L = [f"## {datetime.now():%Y-%m-%d %H:%M:%S} — {kind}", "",
         f"- 指令：`edgar.py {' '.join(argv)}`（script v{VERSION}，Python {sys.version.split()[0]}，{sys.platform}）"]
    if e is not None:
        L.append(f"- 錯誤：{e}")
        if e.endpoint:
            L.append(f"- 端點：`{e.endpoint}`")
        if e.status is not None:
            L.append(f"- 狀態碼：{e.status}")
        if e.api_msg:
            L.append(f"- 回應：`{str(e.api_msg)[:300]}`")
    if detail:
        L.append(f"- 說明：{detail}")
    L.append(f"- User-Agent 來源：{src}；{ua_note(ua)}")
    if kind == "BLOCKED":
        L.append("- 修正步驟：")
        L += [f"  {i}. {s}" for i, s in enumerate(FIX_BLOCKED, 1)]
    elif kind in ("RATE_LIMIT", "NETWORK"):
        L.append("- 處理：重跑一次（清單有快取）；仍失敗 → 改走官網 IR／財報狗／富途，報告寫明。")
    elif kind in ("SCRIPT_BUG", "SELFTEST_FAIL"):
        L.append("- 處理：**AI 必須依 SKILL.md §9 自我修正**：修 `scripts/edgar.py` / `SKILL.md` → `edgar.py selftest` 全過 → "
                 "同步 `.agents/skills/edgar/` → §10 變更紀錄 → commit & push。")
    if tb:
        L += ["", "```text", tb.strip()[-3000:], "```"]
    entry = "\n".join(L) + "\n"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    old = ERROR_LOG.read_text(encoding="utf-8") if ERROR_LOG.is_file() else ERROR_HEADER
    if "<!-- entries -->" not in old:
        old = ERROR_HEADER + old
    head, _, rest = old.partition("<!-- entries -->\n")
    ent = [x for x in re.split(r"(?m)^(?=## \d{4}-\d{2}-\d{2} )", rest) if x.strip()][:49]
    ERROR_LOG.write_text(head + "<!-- entries -->\n" + entry + "\n" + "\n".join(x.rstrip() + "\n" for x in ent),
                         encoding="utf-8")
    return ERROR_LOG


def write_summary(lines: list[str]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    p = LOG_DIR / f"edgar_Summary_{date.today():%Y%m%d}.md"
    head = "" if p.is_file() else f"# SEC EDGAR 執行報告 {date.today():%Y-%m-%d}\n\n"
    with p.open("a", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n\n")
    return p


def _obs_lines() -> list[str]:
    obs = list(dict.fromkeys(OBS))
    if not obs:
        return []
    return ["- 本次觀察（AI 依 SKILL.md §9 判斷：通用規律 → `edgar.py lesson`；公司特例 → `edgar.py hint`；腳本錯 → 修腳本）："] + \
        [f"  - {o}" for o in obs]


# ---------------------------------------------------------------- commands
def _cmd_list_download(a) -> int:
    P = plan(a.code, a)
    c, ticker = P["company"], P["ticker"]
    print(f"[edgar] 公司：CIK {P['cik']}  {ticker}  {c['title']}（{P['ftype']}，FYE 月 {P['fyem']}）", file=sys.stderr)
    print(f"[edgar] 選定 年報 {P['got_a']}/{P['n_a']}、季報 {P['got_p']}/{P['n_p']}；"
          f"SEC 請求 {STATS['requests']} 次", file=sys.stderr)
    if a.cmd == "list":
        out = None
        try:
            out, _ = resolve_out(a, ticker, P["hint"]) if hasattr(a, "out") else (None, False)
        except EdgarError:
            pass
        for r in P["items"]:
            hit = existing_cover(out, r["base"], r, ticker) if out else None
            print(_row(r) + (f"   [本機已有 {hit.name}]" if hit else ""))
        if not P["items"]:
            print("此區間 SEC 無年報/季報")
        for o in dict.fromkeys(OBS):
            print(f"LEARN: {o}")
        return 0

    out, created = resolve_out(a, ticker, P["hint"])
    if created:
        print(f"[edgar] 新公司 → 自動建立資料夾 {out.name}")
    results, new_files = [], []
    for it in P["items"]:
        print("  " + _row(it))
        for r in download_item(P["cik"], it, out, it["base"], ticker, a.force):
            r["item"] = it
            results.append(r)
            print(f"    [{r['status']}] {r['file']}  {r['note']}")
            if r["status"] in ("downloaded", "pending-convert"):
                new_files.append(r.get("cover") or r["file"])
    gaps = []
    if P["got_a"] < P["n_a"]:
        gaps.append(f"年報只找到 {P['got_a']}/{P['n_a']} 份（{a.days} 天內；新上市？加大 --days）")
    if P["got_p"] < P["n_p"]:
        gaps.append(f"季報只找到 {P['got_p']}/{P['n_p']} 份" + ("（外國發行人：6-K 判斷見觀察）" if P["ftype"] == "fpi" else ""))
    if any(r["status"] == "failed" for r in results):
        gaps.append("有檔案下載驗證失敗（見 failed），未寫入")
    sh = P["shares"]
    rel = out.relative_to(REPO_ROOT) if out.is_relative_to(REPO_ROOT) else out
    L = [f"## {datetime.now():%H:%M:%S} — {ticker} {c['title']}（CIK {P['cik']}，{P['ftype']}）", "",
         f"- 指令：`edgar.py {' '.join(sys.argv[1:])}`",
         f"- SEC 請求 {STATS['requests']} 次、重試 {STATS['retry']} 次",
         f"- 輸出資料夾：`{rel}`" + ("（本次新建）" if created else ""),
         f"- 年報 {P['got_a']}/{P['n_a']} 份；季報 {P['got_p']}/{P['n_p']} 份",
         (f"- 最新流通股數（XBRL dei:EntityCommonStockSharesOutstanding）：{sh['val']:,} 股（{sh['end']}，{sh.get('form')} "
          f"{sh['accn']}）→ 每股換算用" if sh else "- 流通股數：companyfacts 無 dei 值（多類股或無 XBRL）→ 看 10-K/10-Q 封面"),
         "- 文件："]
    for r in results:
        it = r["item"]
        L.append(f"  - {it['filingDate']} {it['form']} 期末 {it.get('period') or it['reportDate']} `{it['accessionNumber']}`"
                 f" → `{r['file']}`：{r['status']}（{r['note']}）")
    if not results:
        L.append("  - （無）")
    if gaps:
        L += ["- 缺口與原因："] + [f"  - {g}" for g in gaps]
    L += _obs_lines()
    L.append(f"- 下一步：Convert2md `--html`（`<SCOPE>` = `{out}`）→ `edgar.py verify --code {ticker}`" if new_files
             else "- 下一步：無新檔，免轉檔")
    sp = write_summary(L)
    CACHE.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({
        "code": ticker, "cik": P["cik"], "title": c["title"], "folder": str(out), "ftype": P["ftype"],
        "fyem": P["fyem"], "time": datetime.now().isoformat(),
        "items": [{"base": r["base"], "status": r["status"], "cover": r.get("cover"), "form": r["item"]["form"]
                   if not r["base"].endswith("_EX13") else "EX-13",
                   "period": r["item"].get("period") or r["item"]["reportDate"], "acc": r["item"]["accessionNumber"],
                   "filed": r["item"]["filingDate"], "doc_type": r["item"].get("doc_type"),
                   "url": f"{acc_dir(P['cik'], r['item']['accessionNumber'])}/{r['item'].get('doc') or r['item']['primaryDocument']}"}
                  for r in results if r["status"] in ("downloaded", "skipped", "pending-convert")]},
        ensure_ascii=False, indent=1), encoding="utf-8")
    for g in gaps:
        print(f"[edgar] ⚠ {g}")
    for o in dict.fromkeys(OBS):
        print(f"LEARN: {o}")
    print(f"[edgar] 執行報告：{sp}")
    if new_files:
        print("[edgar] NEXT → 跑 Convert2md skill（scan_pending 加 --html），<SCOPE> 用下面這個資料夾，轉完再 `edgar.py verify`：")
        print(f"CONVERT2MD_SCOPE={out}")
        if any(f.lower().endswith((".htm", ".html")) for f in new_files):
            print("CONVERT2MD_HTML=1")
    return 0


RESIDUE_RE = re.compile(r"<(?:div|span|td|tr|table|font|p)\b|ix:non|xbrli:", re.I)
CID_RE = re.compile(r"\(cid:\d+\)")
TITLE_STOP = {"inc", "corp", "corporation", "co", "ltd", "plc", "sa", "nv", "ag", "the", "holdings", "group", "tbk",
              "company", "limited", "llc", "lp"}


def title_key(title: str) -> str:
    words = [w for w in re.findall(r"[A-Za-z0-9]+", title) if w.lower() not in TITLE_STOP]
    return _norm(" ".join(words[:3]))


def verify_md(md: Path, it: dict, m: dict) -> tuple[bool, str]:
    if not md.is_file():
        return False, "尚未轉成 .md（來源檔還在 → Convert2md 未跑或失敗）"
    size = md.stat().st_size
    if size < MIN_BYTES:
        return False, f".md 太小（{size} bytes）"
    text = md.read_text(encoding="utf-8", errors="replace")
    if (cid := len(CID_RE.findall(text))) >= 50:
        return False, f"CID 亂碼 {cid} 次"
    if (res := len(RESIDUE_RE.findall(text))) >= 50:
        return False, f"殘留 HTML/XBRL 標籤 {res} 處 → html2md 沒處理到（§9 修 html2md.py）"
    head = _norm(text[:20000])
    keys = [title_key(m.get("title", "")), str(m.get("cik", "")), m.get("code", "").lower()]
    if not any(k and len(k) >= 3 and k in head for k in keys):
        return False, "前 2 萬字找不到公司名／CIK／ticker → 檔案可能抓錯"
    note = ""
    fam = FAMILY.get((it.get("form") or "").removesuffix("/A"))
    if fam in ("10-K", "10-Q", "20-F", "40-F"):
        ident = doc_identity(md)
        pe = parse_date(it.get("period") or "")
        if ident is None:
            note = "；⚠ 檔頭認不出 FORM"
        elif not _same(ident, fam, pe, (it.get("form") or "").endswith("/A")):
            return False, f"檔頭是 {ident[0]} 期末 {ident[1]}，預期 {fam} 期末 {pe} → 抓錯檔"
    return True, f"OK（{size / 1024:.0f} KB，CID {cid}）{note}"


def add_source_header(md: Path, it: dict, m: dict) -> bool:
    text = md.read_text(encoding="utf-8", errors="replace")
    if text.startswith("> 來源：SEC EDGAR"):
        return False
    hdr = (f"> 來源：SEC EDGAR {it.get('form')}｜{m.get('title')}（CIK {m.get('cik')}）｜accession {it.get('acc')}｜"
           f"期末 {it.get('period')}｜提交 {it.get('filed')}｜{it.get('url')}\n\n")
    md.write_text(hdr + text, encoding="utf-8")
    return True


def _cmd_verify(a) -> int:
    if not MANIFEST.is_file():
        raise EdgarError("NOT_FOUND", f"找不到上次 download 的紀錄 {MANIFEST}，請先跑 download")
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if a.code and a.code.upper() != m["code"]:
        raise EdgarError("NOT_FOUND", f"上次 download 的是 {m['code']}，不是 {a.code}；請先 download --code {a.code}")
    out = Path(m["folder"])
    bad, L = 0, [f"## {datetime.now():%H:%M:%S} — verify {m['code']}（{out.name}）", ""]
    for it in m["items"]:
        md = out / Path(it.get("cover") or f"{it['base']}.htm").with_suffix(".md").name
        if it["status"] == "skipped" and not md.is_file():
            line = f"- ➖ `{it['base']}`：由既有檔 `{it.get('cover')}` 涵蓋（非 .md）"
        else:
            ok, note = verify_md(md, it, m)
            bad += not ok
            if ok and it["status"] != "skipped" and add_source_header(md, it, m):
                note += "；已補來源標頭"
            line = f"- {'✅' if ok else '❌'} `{md.name}`：{note}" + ("（既有檔）" if it["status"] == "skipped" else "")
        L.append(line)
        print(line)
    if not bad:  # 成功 → 把這家公司的資訊記進 company_hints.json（下次直接用）
        h = load_hints()
        e = h.setdefault(m["code"], {})
        e.update(cik=m["cik"], title=m["title"], folder=out.name if out.parent == REPO_ROOT else e.get("folder"),
                 filer=m.get("ftype"), last_ok=date.today().isoformat())
        six = [it for it in m["items"] if it.get("doc_type")]
        if six and six[0]["doc_type"] != "6-K":
            e["sixk_doc_type"] = six[0]["doc_type"]
        h[m["code"]] = {k: v for k, v in e.items() if v is not None}
        save_hints(h)
        L.append(f"- 已更新 `references/company_hints.json` 的 {m['code']}")
    sp = write_summary(L)
    print(f"[edgar] verify：{len(m['items']) - bad}/{len(m['items'])} 通過 → {sp}")
    return 1 if bad else 0


LESSON_SECTIONS = {"sec": "## A. SEC／EDGAR 行為", "company": "## B. 公司特例",
                   "naming": "## C. 命名與會計年度", "convert": "## D. HTML 轉檔與驗證"}


def _cmd_lesson(a) -> int:
    key = a.key.strip().replace("：", ":")
    line = f"- [{date.today():%Y-%m}] **{key}**：{a.text.strip()}"
    targets = [p / LESSONS_REL for p in {SKILL_DIR, *MIRRORS} if (p / LESSONS_REL).is_file()]
    if not targets:
        raise EdgarError("NOT_FOUND", f"找不到 {LESSONS_REL}")
    for p in targets:
        t = p.read_text(encoding="utf-8")
        sec = LESSON_SECTIONS[a.section]
        if sec not in t:
            t = t.rstrip() + f"\n\n{sec}\n"
        pat = re.compile(r"(?m)^- \[\d{4}-\d{2}\] \*\*" + re.escape(key) + r"\*\*：.*$")
        if pat.search(t):
            t = pat.sub(lambda _: line, t, count=1)  # 同一 key → 改寫（合併不追加）
            act = "更新"
        else:
            i = t.index(sec) + len(sec)
            nxt = t.find("\n## ", i)
            nxt = len(t) if nxt < 0 else nxt
            t = t[:nxt].rstrip() + "\n" + line + "\n" + t[nxt:]
            act = "新增"
        p.write_text(t, encoding="utf-8")
    print(f"[edgar] lessons {act}：{line}（{len(targets)} 份）")
    return 0


def _cmd_hint(a) -> int:
    h = load_hints()
    e = h.setdefault(a.code.upper(), {})
    for kv in a.set or []:
        k, _, v = kv.partition("=")
        if not k:
            continue
        if v == "":
            e.pop(k, None)
        else:
            e[k] = int(v) if v.isdigit() and k != "folder" else v
    if a.note:
        e.setdefault("notes", [])
        e["notes"] = [n for n in e["notes"] if not n.startswith(a.note[:20])] + [f"[{date.today():%Y-%m}] {a.note}"]
    save_hints(h)
    print(json.dumps({a.code.upper(): e}, ensure_ascii=False, indent=1))
    return 0


def _cmd_checkua() -> int:
    ua, src = get_ua()
    data, _ = http_get(f"{DATA}/submissions/CIK0000320193.json")
    ok = json.loads(data).get("name", "")
    print(f"[edgar] SEC 連線正常（測試 CIK 320193 = {ok}）；User-Agent 來源：{src}；{ua_note(ua)}")
    return 0


# ---------------------------------------------------------------- selftest
def _load_html2md():
    p = SKILL_DIR.parent / "Convert2md" / "scripts" / "html2md.py"
    spec = importlib.util.spec_from_file_location("html2md", p)
    if not spec or not p.is_file():
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _cmd_selftest(a, parser: argparse.ArgumentParser) -> int:
    fails: list[str] = []

    def check(name: str, cond: bool, info: str = "") -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {name}{('  — ' + info) if info and not cond else ''}")
        if not cond:
            fails.append(f"{name}：{info}")

    print("[selftest] 會計年度與命名")
    R = lambda form, pe, acc="0000000000-26-000001", **k: dict(form=form, reportDate=pe, accessionNumber=acc,
                                                               primaryDocument="x.htm", **k)  # noqa: E731
    cases = [
        (R("10-K", "2025-12-31"), "UHS", 12, {}, "UHS_AnnualReport_2025"),
        (R("10-Q", "2026-09-30"), "UHS", 12, {}, "UHS_Quarter_2026Q3"),
        # Target：FYE 0201，期末 2026-01-31 → DEI 標 FY2025（日期推算會得 2026）
        (R("10-K", "2026-01-31", "A1"), "TGT", 1, {"A1": (2025, "FY")}, "TGT_AnnualReport_2025"),
        (R("10-Q", "2026-10-31", "A2"), "TGT", 1, {"A2": (2026, "Q3")}, "TGT_Quarter_2026Q3"),
        # Apple 52/53 週：FYE 9 月，Q1 期末 2025-12-27 → FY2026Q1
        (R("10-Q", "2025-12-27"), "AAPL", 9, {}, "AAPL_Quarter_2026Q1"),
        # 期末 2026-01-03（52/53 週，FYE 0103 → 視為 12 月）→ FY2025
        (R("10-K", "2026-01-03"), "XYZ", fye_month({"fiscalYearEnd": "0103"}), {}, "XYZ_AnnualReport_2025"),
        (R("20-F", "2026-03-31"), "TM", 3, {}, "TM_AnnualReport_2026"),
        (R("6-K", "2026-10-30", period="2026-09-30"), "TLK", 12, {}, "TLK_Quarter_2026Q3"),
        (R("6-K", "2026-08-07", period="2026-06-30", h1=True), "XX", 12, {}, "XX_Quarter_2026H1"),
        (R("6-K", "2026-11-05", period="2026-09-30"), "TM", 3, {}, "TM_Quarter_2027Q2"),
        (R("10-K/A", "2025-12-31", "0000950170-26-000009"), "UHS", 12, {}, "UHS_AnnualReport_2025_Amend000095017026000009"),
    ]
    for item, t, fyem, dei, want in cases:
        got = target_name(item, t, fyem, dei)[0]
        check(f"target_name {want}", got == want, f"得到 {got}")
    check("fye_month 0103 → 12", fye_month({"fiscalYearEnd": "0103"}) == 12)
    check("fye_month 0201 → 1", fye_month({"fiscalYearEnd": "0201"}) == 1)

    print("[selftest] 6-K 期別判斷")
    s1 = ("Consolidated Statements of Financial Position as of September 30, 2026 and December 31, 2025 and for the "
          "nine months period ended September 30, 2026. Consolidated statements of profit or loss for the nine months "
          "period ended September 30, 2026 and 2025. Statements of cash flows. Notes to the interim consolidated "
          "financial statements. As of September 30, 2026. Unaudited.")
    r1 = score_6k_text(s1, date(2026, 10, 30))
    check("TLK 型 9 月季報 → 2026-09-30、非 H1", r1["period"] == "2026-09-30" and not r1["h1"] and r1["score"] >= 3, str(r1))
    s2 = ("Unaudited interim condensed consolidated financial statements for the six months ended 30 June 2026. "
          "Balance sheet as at 30 June 2026. Income statement for the six months ended 30 June 2026. "
          "Statement of cash flows six months ended 30 June 2026.")
    r2 = score_6k_text(s2, date(2026, 8, 7))
    check("英式日期半年報 → 2026-06-30、H1", r2["period"] == "2026-06-30" and r2["h1"], str(r2))
    # TM 2026-11 實測：日本企業英譯決算短信，比較期與本期一樣多次、財測日 2027-03-31 晚於提交日
    s4 = ("FY2027 Semi-Annual (April 1, 2026 through September 30, 2026). Consolidated Statement of Financial Position "
          "As of March 31, 2026 As of September 30, 2026. Consolidated Statement of Income For the first half ended "
          "September 30, 2025 For the first half ended September 30, 2026. Statement of Comprehensive Income. "
          "Statement of Cash Flows For the first half ended September 30, 2025 For the first half ended September 30, "
          "2026. Forecast for FY2027 (April 1, 2026 through March 31, 2027). Unaudited.")
    r4 = score_6k_text(s4, date(2026, 11, 5))
    check("TM 型半年報 → 2026-09-30、H1（排除財測日、不取比較期）", r4["period"] == "2026-09-30" and r4["h1"], str(r4))
    s5 = ("FY2027 First Quarter (April 1, 2026 through June 30, 2026). Statement of Income For the three months ended "
          "June 30, 2025 For the three months ended June 30, 2026. Statement of Financial Position As of March 31, 2026 "
          "As of June 30, 2026. Statements of cash flows. Unaudited.")
    r5 = score_6k_text(s5, date(2026, 8, 4))
    check("TM 型第 1 季 → 2026-06-30、非 H1", r5["period"] == "2026-06-30" and not r5["h1"], str(r5))
    r3 = score_6k_text("Press release: Changes to organizational structure, November 5, 2026.", date(2026, 11, 5))
    check("人事新聞稿 → 不是財報", r3["score"] < 3, str(r3))

    print("[selftest] 既有檔判定（檔名 + 檔頭內容）")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "UHS_10K_2025-12-31.md").write_text("UNITED STATES SECURITIES AND EXCHANGE COMMISSION FORM 10-K "
                                                 "For the fiscal year ended December 31, 2025", encoding="utf-8")
        (d / "evtc-20260630.md").write_text("FORM 10-Q For the quarterly period ended June 30, 2026 EVERTEC", encoding="utf-8")
        # 舊流程把 CF 的季報 HTML 轉檔時表格拆行
        (d / "CF_AnnualReport_2025.md").write_text("| FORM | 10-K |\n For the fiscal year ended\nDecember 31\n, 2025",
                                                   encoding="utf-8")
        (d / "ZZ_Quarter_2026Q3.md").write_text("ZZ Corp Reports Third Quarter 2026 Results — press release",
                                                encoding="utf-8")
        (d / "AA_Quarter_2026Q2.md").write_text("FORM 10-Q For the quarterly period ended June 30, 2026", encoding="utf-8")
        it = lambda f, pe: R(f, pe)  # noqa: E731
        check("認得 {T}_10K_{期末日}", existing_cover(d, "UHS_AnnualReport_2025", it("10-K", "2025-12-31"), "UHS") is not None)
        check("不同期別不誤判", existing_cover(d, "UHS_AnnualReport_2024", it("10-K", "2024-12-31"), "UHS") is None)
        check("認得 EDGAR 原檔名 evtc-YYYYMMDD", existing_cover(d, "EVTC_Quarter_2026Q2", it("10-Q", "2026-06-30"), "EVTC") is not None)
        check("檔頭拆行的日期也認得", existing_cover(d, "CF_AnnualReport_2025", it("10-K", "2025-12-31"), "CF") is not None)
        check("新聞稿佔用檔名 → 改存 _EDGAR", name_taken_by_other(d, "ZZ_Quarter_2026Q3", it("10-Q", "2026-09-30")) is not None)
        check("10-Q 不頂替 10-K", existing_cover(d, "AA_AnnualReport_2026", it("10-K", "2026-06-30"), "AA") is None)
        check("Q2 與 H1 互認", existing_cover(d, "AA_Quarter_2026H1", it("10-Q", "2026-06-30"), "AA") is not None)
        di = doc_identity(d / "CF_AnnualReport_2025.md")
        check("doc_identity 拆行日期", di == ("10-K", date(2025, 12, 31), False), str(di))

    print("[selftest] html2md（Convert2md/scripts/html2md.py）")
    h2m = _load_html2md()
    check("html2md.py 存在且可載入", h2m is not None)
    if h2m:
        sample = ("<html><body><div style='display:none'><ix:header><ix:hidden>SECRETCONTEXT</ix:hidden></ix:header></div>"
                  "<p style='font-weight:bold'>Item 2. Management's Discussion</p><p>Revenue grew.&#160;Fine.</p>"
                  "<table><tr><td></td><td colspan='2'>2026</td><td></td></tr>"
                  "<tr><td>Net revenues</td><td>$</td><td>4,733,352</td><td></td></tr>"
                  "<tr><td>Other</td><td></td><td>(15,738</td><td>)</td></tr></table></body></html>")
        p = h2m.H2M()
        p.feed(sample)
        md = p.result()
        check("html2md 丟掉 ix:header／display:none", "SECRETCONTEXT" not in md, md[:200])
        check("html2md 合併 $ 與 )", "$4,733,352" in md and "(15,738)" in md, md)
        check("html2md 粗體段落 → ### 標題", "### Item 2. Management's Discussion" in md, md[:200])
        check("html2md 刪全空欄", "| Net revenues | $4,733,352 |" in md, md)

    print("[selftest] SKILL.md 與 CLI 參數一致")
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8") if (SKILL_DIR / "SKILL.md").is_file() else ""
    check("SKILL.md 存在", bool(text))
    subs = next(act.choices for act in parser._actions if isinstance(act, argparse._SubParsersAction))  # noqa: SLF001
    opts = {o for sp in subs.values() for act in sp._actions for o in act.option_strings}  # noqa: SLF001
    for sc in sorted(set(re.findall(r"edgar\.py\s+([a-z]+)", text))):
        check(f"SKILL.md 提到的子指令 `{sc}` 存在", sc in subs, f"CLI 沒有 {sc}")
    for op in sorted(set(re.findall(r"(?<![\w-])(--[a-z][a-z-]+)", text)) - {"--html"}):
        check(f"SKILL.md 提到的參數 `{op}` 存在", op in opts, f"CLI 沒有 {op}")
    for sc in subs:
        check(f"子指令 `{sc}` 有寫進 SKILL.md", f"edgar.py {sc}" in text, "SKILL.md 漏寫")

    print("[selftest] 經驗庫、hints、鏡像、.gitignore")
    try:
        load_hints()
        check("company_hints.json 是合法 JSON", True)
    except EdgarError as e:
        check("company_hints.json 是合法 JSON", False, str(e))
    lt = (SKILL_DIR / LESSONS_REL).read_text(encoding="utf-8") if (SKILL_DIR / LESSONS_REL).is_file() else ""
    check("lessons.md 存在且有 A–D 四節", all(s in lt for s in LESSON_SECTIONS.values()))
    for rel in ("SKILL.md", "scripts/edgar.py", ".env.example", HINTS_REL, LESSONS_REL):
        a1, a2 = MIRRORS[0] / rel, MIRRORS[1] / rel
        check(f"鏡像一致 edgar/{rel}", a1.is_file() and a2.is_file() and a1.read_bytes() == a2.read_bytes(),
              "→ 把 .claude/skills/edgar 複製到 .agents/skills/edgar")
    c1 = REPO_ROOT / ".claude/skills/Convert2md/scripts/html2md.py"
    c2 = REPO_ROOT / ".agents/skills/Convert2md/scripts/html2md.py"
    check("鏡像一致 Convert2md/scripts/html2md.py", c1.is_file() and c2.is_file() and c1.read_bytes() == c2.read_bytes())
    gi = REPO_ROOT / ".gitignore"
    check(".gitignore 排除 .env", gi.is_file() and re.search(r"(?m)^\.env\s*$", gi.read_text(encoding="utf-8")) is not None)

    if not a.offline:
        print("[selftest] 線上：SEC 連線、代碼表、submissions")
        try:
            rows = load_tickers()
            check("代碼表：AAPL → CIK 320193", lookup("AAPL", rows)[0]["cik"] == 320193)
            s = load_submissions(352915)
            check("submissions：UHS 有 10-K", any(f == "10-K" for f in s["filings"]["recent"]["form"]))
        except EdgarError as e:
            p = log_error(e, sys.argv[1:])
            check("SEC 連線", False, f"{e.kind} → 已寫 {p}")

    print(f"[selftest] {'全部通過' if not fails else f'{len(fails)} 項失敗'}")
    if fails:
        p = log_error(None, sys.argv[1:], kind="SELFTEST_FAIL", detail="；".join(fails[:20]))
        print(f"[selftest] 失敗明細已寫入 {p}", file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------- CLI
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=f"SEC EDGAR 美股年報/季報下載器 v{VERSION}")
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lookup", help="找公司")
    s.add_argument("query")
    sub.add_parser("checkua", help="檢查 User-Agent 與 SEC 連線")
    s = sub.add_parser("selftest", help="自我檢查")
    s.add_argument("--offline", action="store_true", help="不連網")
    s = sub.add_parser("verify", help="Convert2md 後驗證 .md")
    s.add_argument("--code", help="只驗證這家（預設：上次 download 的公司）")
    s = sub.add_parser("lesson", help="寫一條經驗到 references/lessons.md")
    s.add_argument("--section", required=True, choices=sorted(LESSON_SECTIONS))
    s.add_argument("--key", required=True, help="短標題；同 key 會改寫舊的那條")
    s.add_argument("--text", required=True)
    s = sub.add_parser("hint", help="設定公司特例（references/company_hints.json）")
    s.add_argument("--code", required=True)
    s.add_argument("--set", action="append", help="key=value；value 留空 = 刪除該 key")
    s.add_argument("--note", help="一句話備註")
    for name in ("list", "download"):
        s = sub.add_parser(name)
        s.add_argument("--code", required=True, help="ticker / CIK / 公司名")
        s.add_argument("--days", type=int, default=800, help="年報/10-Q 往回幾天（預設 800）")
        s.add_argument("--annual", type=int, help="年報份數（預設 2）")
        s.add_argument("--periodic", type=int, help="季報份數（預設 1）")
        s.add_argument("--include-amendments", action="store_true", help="一併下載 10-K/A、10-Q/A、20-F/A")
        s.add_argument("--ticker", help="檔名用的代碼（預設：SEC ticker）")
        s.add_argument("--out", help="輸出資料夾（預設：repo 內 ticker 資料夾）")
        if name == "download":
            s.add_argument("--no-create", action="store_true", help="找不到公司資料夾時報錯，不自動新建")
            s.add_argument("--force", action="store_true", help="已存在也重新下載")
    return ap


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    a = parser.parse_args(argv)
    raw = argv if argv is not None else sys.argv[1:]
    try:
        if a.cmd == "lookup":
            hits = lookup(a.query, load_tickers())
            print("\n".join(f"CIK {r['cik']:<10} {r['ticker']:<8} {r['title']}" for r in hits[:30]) or "找不到")
            return 0
        if a.cmd == "checkua":
            return _cmd_checkua()
        if a.cmd == "selftest":
            return _cmd_selftest(a, parser)
        if a.cmd == "verify":
            return _cmd_verify(a)
        if a.cmd == "lesson":
            return _cmd_lesson(a)
        if a.cmd == "hint":
            return _cmd_hint(a)
        return _cmd_list_download(a)
    except EdgarError as e:
        if e.kind == "SCRIPT_BUG":
            p = log_error(e, raw, tb=traceback.format_exc())
            print(f"[edgar] ✗ SCRIPT_BUG：{e} → 已寫入 {p}；AI 請依 SKILL.md §9 自我修正", file=sys.stderr)
            return 3
        p = log_error(e, raw)
        print(f"[edgar] ✗ {e.kind}：{e}" + (f"｜{e.api_msg}" if e.api_msg else ""), file=sys.stderr)
        if e.kind in BLOCK_KINDS:
            print("[edgar] ✗ 被 SEC 擋 → 修正步驟見錯誤報告（設 SEC_EDGAR_USER_AGENT、放慢速度）", file=sys.stderr)
        print(f"[edgar] 錯誤報告已寫入：{p}", file=sys.stderr)
        return 2 if e.kind in BLOCK_KINDS else 1
    except KeyboardInterrupt:
        return 130
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc()
        p = log_error(None, raw, kind="SCRIPT_BUG", tb=tb)
        print(tb, file=sys.stderr)
        print(f"[edgar] ✗ SCRIPT_BUG → 已寫入 {p}；AI 請依 SKILL.md §9 自我修正", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
