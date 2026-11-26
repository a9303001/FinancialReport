#!/usr/bin/env python3
"""MOPS / TWSE 電子書（doc.twse.com.tw）台股年報（股東會年報）與季報（財務報告書）下載器。

只用 Python 標準函式庫（Windows / Linux / macOS / Claude Code 雲端皆可）。

子指令:
  lookup   <查詢>                    用代號 / 公司簡稱 / 英文簡稱找公司（TWSE、TPEx OpenAPI：上市/上櫃/興櫃）
  plan     --code 6279 [--html F…]   取清單 → 選最新 2 份年報 + 1 份季報 → 比對公司資料夾 → 存計畫
  download --code 6279               依計畫下載（本機直連 → Apify REST）；做不到 → 印 MCP 步驟，結束碼 4
  ingest   --code 6279 --file 202603_6279_AI1.pdf --from <Apify 結果檔/PDF/MD>
                                     把 MCP 拿到的檔案（Apify raw base64、markdown、PDF）落地成正確檔名
  verify   [--code 6279]             Convert2md 之後驗證 .md（大小、CID、公司名、期別）
  learn    --route pdf.apify_raw_mcp --ok|--fail [--note …]   記錄路徑成敗（下次自動排序）
  learn    --code 6279 --note "…"    記錄公司專屬經驗（IR 網址、上架時差…）
  lessons  [--code 6279]             顯示累積經驗與建議路徑順序
  selftest [--offline]               自我檢查：解析、命名、既有檔判定、SKILL.md↔CLI、鏡像、learned.json

結束碼：0 成功／1 一般錯誤／3 腳本 bug（寫 SCRIPT_BUG 到 Log/mops_error.md）／4 需要 AI 走 MCP 路徑
經驗庫：<skill>/learned.json（.claude 與 .agents 兩份同時寫入，內容永遠相同）
"""
from __future__ import annotations

import argparse
import base64
import html as htmllib
import http.client
import http.cookiejar
import json
import os
import re
import sys
import tempfile
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

VERSION = "1.0.0"

for _s in (sys.stdout, sys.stderr):  # Windows 主控台 cp950 印不出部分字 → 一律 UTF-8
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
DOC = "https://doc.twse.com.tw/server-java/t57sb01"
PDF_URL_RE = re.compile(r"https?://doc\.twse\.com\.tw/pdf/[\w.-]+?\.pdf", re.I)
OPENAPI = [  # (url, 市場, 欄位對照)
    ("https://openapi.twse.com.tw/v1/opendata/t187ap03_L", "上市",
     {"code": "公司代號", "name": "公司名稱", "abbr": "公司簡稱", "en": "英文簡稱",
      "shares": "已發行普通股數或TDR原股發行股數", "web": "網址", "listed": "上市日期", "industry": "產業別"}),
    ("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O", "上櫃",
     {"code": "SecuritiesCompanyCode", "name": "CompanyName", "abbr": "CompanyAbbreviation", "en": "Symbol",
      "shares": "IssueShares", "web": "WebAddress", "listed": "DateOfListing", "industry": "SecuritiesIndustryCode"}),
    ("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_R", "興櫃",
     {"code": "SecuritiesCompanyCode", "name": "CompanyName", "abbr": "CompanyAbbreviation", "en": "Symbol",
      "shares": "IssueShares", "web": "WebAddress", "listed": "DateOfListing", "industry": "SecuritiesIndustryCode"}),
]
APIFY_RUN = "https://api.apify.com/v2/acts/apify~web-fetch/run-sync-get-dataset-items"
MIN_REPORT_BYTES = 10 * 1024
STRONG_MD_BYTES = 30 * 1024
CID_RE = re.compile(r"\(cid:\d+\)")

SKILL_DIR = Path(__file__).resolve().parent.parent


def _find_repo_root() -> Path:
    env = os.environ.get("MOPS_REPO")
    if env:
        return Path(env).expanduser().resolve()
    for p in SKILL_DIR.parents:
        if (p / ".git").exists() or (p / "AGENTS.md").is_file():
            return p
    return SKILL_DIR.parents[2]


REPO_ROOT = _find_repo_root()
LOG_DIR = REPO_ROOT / "Log"
ERROR_LOG = LOG_DIR / "mops_error.md"
CACHE = Path(os.environ.get("MOPS_CACHE_DIR") or (Path.home() / ".cache" / "mops"))
LEARNED_FILES = [REPO_ROOT / ".claude/skills/mops/learned.json", REPO_ROOT / ".agents/skills/mops/learned.json"]

# 路徑（route）：<階段>.<做法>。script 能自己執行的是 direct、apify_rest；其餘由 AI 用 MCP 執行後回報。
DEFAULT_ROUTES = {
    "list": ["direct", "apify_rest", "firecrawl_stealth", "apify_webfetch_mcp"],
    "link": ["direct", "apify_rest", "firecrawl_stealth", "apify_webfetch_mcp"],
    "pdf": ["direct", "apify_rest", "apify_raw_mcp", "apify_markdown_mcp", "company_ir"],
}
SCRIPT_ROUTES = {"direct", "apify_rest"}
ROUTE_KEY_RE = re.compile(r"^(list|link|pdf)\.[a-z][a-z0-9_]*$")
ENVS = ("blocked_ip", "open_ip")


class MopsError(Exception):
    def __init__(self, kind: str, msg: str, *, url: str | None = None):
        super().__init__(msg)
        self.kind, self.url = kind, url


# ---------------------------------------------------------------- HTTP
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))
STATS = {"requests": 0}
_last = [0.0]


def http_req(url: str, *, data: bytes | None = None, headers: dict | None = None,
             timeout: int = 60, retries: int = 2, min_gap: float = 1.5) -> tuple[int, bytes, str]:
    """回傳 (HTTP 狀態, 內容, Content-Type)。同站請求間隔 ≥ min_gap 秒；網路錯誤重試 retries 次。"""
    h = {"User-Agent": UA, "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8"}
    h.update(headers or {})
    err = ""
    for i in range(retries + 1):
        gap = _last[0] + min_gap - time.monotonic()
        if gap > 0:
            time.sleep(gap)
        _last[0] = time.monotonic()
        STATS["requests"] += 1
        try:
            req = urllib.request.Request(url, data=data, headers=h)
            with _OPENER.open(req, timeout=timeout) as r:
                return r.status, r.read(), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            body = e.read() or b""
            if e.code >= 500 and i < retries:
                err = f"HTTP {e.code}"
                time.sleep(3 * (i + 1))
                continue
            return e.code, body, e.headers.get("Content-Type", "") if e.headers else ""
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException, OSError) as e:
            err = str(e)
            if i < retries:
                time.sleep(3 * (i + 1))
    raise MopsError("NETWORK", f"連線失敗（重試 {retries} 次）：{err}", url=url)


def is_block_page(data: bytes) -> bool:
    """TWSE／MOPS 依來源 IP 封鎖時回 947 bytes「因為安全性考量…FOR SECURITY REASONS」頁。"""
    head = data[:3000]
    return b"FOR SECURITY REASONS" in head or (len(data) < 3000 and "安全性考量".encode("utf-8") in head)


def decode_html(data: bytes, ctype: str = "") -> str:
    m = re.search(r"charset=([\w-]+)", ctype or "", re.I) or re.search(rb"charset=([\w-]+)", data[:2000], re.I)
    cs = (m.group(1).decode() if isinstance(m.group(1), bytes) else m.group(1)).lower() if m else "utf-8"
    if cs in ("big5", "big5-hkscs", "ms950", "x-windows-950"):
        cs = "cp950"
    try:
        return data.decode(cs, errors="replace")
    except LookupError:
        return data.decode("utf-8", errors="replace")


# ---------------------------------------------------------------- 公司資料（OpenAPI）
def load_companies(refresh_days: int = 7) -> list[dict]:
    CACHE.mkdir(parents=True, exist_ok=True)
    out: list[dict] = []
    for url, market, f in OPENAPI:
        cp = CACHE / f"companies_{market}.json"
        rows = None
        if cp.is_file() and time.time() - cp.stat().st_mtime < refresh_days * 86400:
            rows = json.loads(cp.read_text(encoding="utf-8"))
        else:
            try:
                st, body, _ = http_req(url, timeout=60, min_gap=0.2)
                if st == 200 and body.lstrip()[:1] == b"[":
                    raw = json.loads(body.decode("utf-8"))
                    rows = [{k: str(r.get(v, "")).strip() for k, v in f.items()} | {"market": market} for r in raw]
                    cp.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
            except MopsError:
                pass
            if rows is None and cp.is_file():  # 抓不到 → 用舊快取
                rows = json.loads(cp.read_text(encoding="utf-8"))
        out += rows or []
    return out


def _norm(s: str) -> str:
    return re.sub(r"[\s*＊()（）股份有限公司]", "", (s or "")).lower()


def lookup(q: str, comps: list[dict]) -> list[dict]:
    q0 = q.strip()
    exact = [c for c in comps if c["code"] == q0]
    if exact:
        return exact
    n = _norm(q0)
    return [c for c in comps if n and (n == _norm(c["abbr"]) or n == _norm(c["en"]))] or \
           [c for c in comps if n and (n in _norm(c["abbr"]) or n in _norm(c["name"]) or n in _norm(c["en"]))]


def resolve_company(code: str, name_hint: str | None = None) -> dict:
    hits = lookup(code, load_companies())
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        raise MopsError("AMBIGUOUS", "對到多家：" + "、".join(f"{c['code']} {c['abbr']}({c['market']})" for c in hits[:10]))
    if re.fullmatch(r"\d{4,6}[A-Z]?", code):  # OpenAPI 抓不到（下市、創新板、網路問題）→ 最小資料繼續
        return {"code": code, "name": name_hint or code, "abbr": name_hint or code, "en": "", "shares": "",
                "web": "", "listed": "", "industry": "", "market": "?"}
    raise MopsError("NOT_FOUND", f"找不到公司：{code}（用 `mops.py lookup` 查代號）")


def fmt_company(c: dict) -> str:
    sh = f"{int(c['shares']):,} 股" if (c.get("shares") or "").isdigit() else "股數未知"
    return f"{c['code']} {c['abbr']}（{c['name']}；{c['market']}；英文 {c.get('en') or '-'}；已發行 {sh}；官網 {c.get('web') or '-'}）"


# ---------------------------------------------------------------- 清單解析（t57sb01 step=1）
FIN_RE = re.compile(r"^(\d{4})(0[1-4])_([0-9A-Za-z]+)_(AI[1-3A-C])\.pdf$", re.I)
AGM_RE = re.compile(r"^(\d{4})_([0-9A-Za-z]+)_(\d{8})(F[0-9A-Z]{2})\.pdf$", re.I)
ROW_RE = re.compile(r"(\d{4,6}_[0-9A-Za-z]+_[0-9A-Za-z]+\.pdf)\s*\|?\s*([\d,]{3,})\s*\|?\s*"
                    r"(\d{2,3}/\d{1,2}/\d{1,2})(?:\s+(\d{1,2}:\d{2}:\d{2}))?", re.I)
FIN_SCOPE = {"AI1": ("zh", "合併"), "AI2": ("zh", "個別"), "AI3": ("zh", "個體"),
             "AIA": ("en", "合併"), "AIB": ("en", "個別"), "AIC": ("en", "個體")}
SCOPE_RANK = {"合併": 0, "個體": 1, "個別": 2}
ANNUAL_CODES = {"F04": "zh", "FE4": "en", "FE6": "en"}  # FE6：KY 公司英文年報（6781 實例）；有說明欄時以說明為準


def roc_date(s: str) -> str:
    m = re.match(r"(\d{2,3})/(\d{1,2})/(\d{1,2})", s or "")
    if not m:
        return ""
    y = int(m.group(1)) + 1911
    return f"{y:04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"


def _strip_tags(s: str) -> str:
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", htmllib.unescape(s))


def load_list_source(path: Path) -> str:
    """接受：原始 HTML（UTF-8 或 Big5）、Firecrawl／Apify 回傳的 JSON（含 html/markdown/text 欄位）、純文字。"""
    data = path.read_bytes()
    t = data.lstrip()[:1]
    if t in (b"{", b"["):
        try:
            j = json.loads(data.decode("utf-8", errors="replace"))
            texts: list[str] = []

            def walk(o):
                if isinstance(o, dict):
                    for k, v in o.items():
                        if k in ("html", "markdown", "text", "rawHtml") and isinstance(v, str):
                            texts.append(v)
                        else:
                            walk(v)
                elif isinstance(o, list):
                    for v in o:
                        walk(v)
            walk(j)
            if texts:
                return "\n".join(texts)
        except json.JSONDecodeError:
            pass
    return decode_html(data)


def parse_list(text: str, code: str | None = None) -> list[dict]:
    flat = _strip_tags(text) if "<" in text else re.sub(r"[ \t]+", " ", text)
    rows, prev_end = [], 0
    for m in ROW_RE.finditer(flat):
        fn, size, up = m.group(1), m.group(2), m.group(3)
        desc = flat[prev_end:m.start()][-160:]
        prev_end = m.end()
        r = classify_file(fn, desc)
        if not r or (code and r["co"] != code):
            continue
        r.update(size=int(size.replace(",", "")), uploaded=roc_date(up), desc=desc.strip()[-60:])
        rows.append(r)
    seen, out = set(), []
    for r in rows:  # 同檔名去重（多份清單合併時）
        if r["file"] not in seen:
            seen.add(r["file"])
            out.append(r)
    return out


def classify_file(fn: str, desc: str = "") -> dict | None:
    m = FIN_RE.match(fn)
    if m:
        lang, scope = FIN_SCOPE[m.group(4).upper()]
        return {"file": fn, "kind": "fin", "fy": int(m.group(1)), "q": int(m.group(2)), "co": m.group(3),
                "code": m.group(4).upper(), "lang": lang, "scope": scope}
    m = AGM_RE.match(fn)
    if m:
        c = m.group(4).upper()
        good_desc = "股東會年報" in desc and "前十大" not in desc
        if good_desc:
            lang = "en" if "英文" in desc.split("股東會年報")[0][-12:] else "zh"
        elif c in ANNUAL_CODES and "年報" not in desc:  # 沒有說明欄（Apify text 亂碼）→ 用代碼推定
            lang = ANNUAL_CODES[c]
        else:
            return {"file": fn, "kind": "agm_other", "fy": int(m.group(1)), "co": m.group(2), "code": c}
        return {"file": fn, "kind": "annual", "fy": int(m.group(1)), "co": m.group(2), "code": c,
                "lang": lang, "agm": m.group(3)}
    return None


def list_urls(code: str, today: date) -> list[tuple[str, str]]:
    """要抓的清單頁：財報（mtype=A，year=資料年度）今年＋去年；股東會（mtype=F，year=開會年度）今年起往回 3 年。"""
    r = today.year - 1911
    out = [(f"A{y}", f"{DOC}?step=1&colorchg=1&co_id={code}&year={y}&seamon=&mtype=A&") for y in (r, r - 1)]
    out += [(f"F{y}", f"{DOC}?step=1&colorchg=1&co_id={code}&year={y}&seamon=&mtype=F&") for y in (r, r - 1, r - 2)]
    return out


def step9_url(code: str, row: dict) -> str:
    kind = "A" if row["kind"] == "fin" else "F"
    return f"{DOC}?step=9&kind={kind}&co_id={code}&filename={urllib.parse.quote(row['file'])}&colorchg=1"


# ---------------------------------------------------------------- 選檔與命名
def target_name(row: dict, ticker: str, market: str) -> str:
    if row["kind"] == "annual":
        return f"{ticker}_AnnualReport_{row['fy']}"
    if market == "興櫃" and row["q"] == 2:
        return f"{ticker}_Quarter_{row['fy']}H1"
    return f"{ticker}_Quarter_{row['fy']}Q{row['q']}"


def select(rows: list[dict], annual_n: int, quarter_n: int, lang: str) -> list[dict]:
    pick: list[dict] = []
    ann = [r for r in rows if r["kind"] == "annual"]
    for fy in sorted({r["fy"] for r in ann}, reverse=True)[:annual_n]:
        cands = sorted((r for r in ann if r["fy"] == fy), key=lambda r: (r["lang"] != lang, r["file"]))
        best = dict(cands[0])
        best["alternates"] = [c["file"] for c in cands[1:]]
        pick.append(best)
    fin = [r for r in rows if r["kind"] == "fin"]
    for fy, q in sorted({(r["fy"], r["q"]) for r in fin}, reverse=True)[:quarter_n]:
        cands = sorted((r for r in fin if (r["fy"], r["q"]) == (fy, q)),
                       key=lambda r: (r["lang"] != lang, SCOPE_RANK[r["scope"]], r["file"]))
        best = dict(cands[0])
        best["alternates"] = [c["file"] for c in cands[1:] if c["scope"] == best["scope"]]
        pick.append(best)
    return pick


def en_lag_days(rows: list[dict]) -> list[int]:
    """同期別中文版與英文版上傳日相差幾天（給「英文版何時會出」的判斷用）。"""
    out = []
    zh = {(r["kind"], r["fy"], r.get("q"), r.get("scope")): r for r in rows if r.get("lang") == "zh"}
    for r in rows:
        if r.get("lang") == "en":
            z = zh.get((r["kind"], r["fy"], r.get("q"), r.get("scope")))
            if z and z["uploaded"] and r["uploaded"]:
                out.append((date.fromisoformat(r["uploaded"]) - date.fromisoformat(z["uploaded"])).days)
    return out


# ---------------------------------------------------------------- 既有檔判定
def alias_patterns(row: dict, ticker: str, market: str) -> list[str]:
    t, fy = re.escape(ticker), row["fy"]
    if row["kind"] == "annual":
        return [rf"^{t}_AnnualReport_{fy}(?:_MOPS)?$", rf"^{t}_annual_{fy}$", rf"^{t}_{fy}_annual_report$",
                rf"(?:^|[^\d]){fy}_{t}_\d{{8}}F(?:04|E4|E6)(?:_\d{{8}}_\d{{6}})?$"]
    q = row["q"]
    pats = [rf"^{t}_Quarter_{fy}Q{q}(?:_MOPS)?$", rf"^{t}_(?:quarter|QuarterlyReport)_{fy}Q{q}$",
            rf"^{t}_{fy}Q{q}_quarterly_report$", rf"^{fy}0{q}_{t}_AI[1-3A-C](?:_\d{{8}}_\d{{6}})?$"]
    if q == 2:
        pats += [rf"^{t}_Quarter_{fy}H1(?:_MOPS)?$", rf"^{t}_interim_{fy}$"]
    return pats


def is_strong_md(p: Path) -> bool:
    """md 夠大且檔頭像完整報告（避免把新聞摘要、MoneyDJ 損益表轉載當成財報）。"""
    try:
        if p.stat().st_size < STRONG_MD_BYTES:
            return False
        with p.open(encoding="utf-8", errors="replace") as f:
            head = re.sub(r"[`*#\s]", "", f.read(20000))
    except OSError:
        return False
    return re.search(r"財務報告|財務報表|股東會年報|年報|FinancialStatements|FinancialReport|AnnualReport",
                     head, re.I) is not None


def existing_cover(folder: Path, row: dict, ticker: str, market: str) -> tuple[Path | None, Path | None]:
    """回傳 (涵蓋本期的既有檔, 佔用目標檔名但內容不合格的檔)。"""
    if not folder.is_dir():
        return None, None
    pats = [re.compile(p, re.I) for p in alias_patterns(row, ticker, market)]
    weak = None
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.suffix.lower() not in (".md", ".pdf"):
            continue
        if any(rx.search(p.stem) for rx in pats):
            if p.suffix.lower() == ".pdf" and p.stat().st_size >= MIN_REPORT_BYTES:
                return p, None
            if p.suffix.lower() == ".md" and is_strong_md(p):
                return p, None
            weak = weak or p
    return None, weak


def find_company_folder(c: dict) -> list[Path]:
    code, abbr = c["code"], re.sub(r"[*＊]", "", c.get("abbr") or "")
    out = []
    for p in REPO_ROOT.iterdir():
        if not p.is_dir() or p.name.startswith("."):
            continue
        if (p.name.startswith(code) and not p.name[len(code):len(code) + 1].isdigit()) or (abbr and p.name == abbr):
            out.append(p)
    return sorted(set(out))


def resolve_folder(c: dict, out: str | None) -> tuple[Path, bool]:
    if out:
        return Path(out).expanduser().resolve(), False
    cands = find_company_folder(c)
    if len(cands) == 1:
        return cands[0], False
    if len(cands) > 1:
        raise MopsError("AMBIGUOUS", "多個候選資料夾：" + "、".join(p.name for p in cands) + " → 用 --out 指定")
    safe = re.sub(r"[*＊/\\:]", "", c["abbr"])
    return REPO_ROOT / f"{c['code']}{safe}", True


# ---------------------------------------------------------------- 經驗庫 learned.json
def load_learned() -> dict:
    for p in [SKILL_DIR / "learned.json"] + LEARNED_FILES:
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                raise MopsError("LEARNED_CORRUPT", f"{p} 不是合法 JSON：{e}（照 SKILL.md §9 修）")
    return {"routes": {e: {} for e in ENVS}, "companies": {}}


def save_learned(d: dict) -> None:
    d["updated"] = date.today().isoformat()
    txt = json.dumps(d, ensure_ascii=False, indent=1) + "\n"
    for p in {SKILL_DIR / "learned.json", *LEARNED_FILES}:
        if p.parent.is_dir():
            p.write_text(txt, encoding="utf-8")


def record_route(key: str, ok: bool | None, env: str, note: str = "", *, manual: bool = False) -> None:
    """自動記錄（script）只寫 last_msg；人工經驗（learn --note）才寫 note，避免好的經驗被短訊息蓋掉。"""
    if not ROUTE_KEY_RE.match(key):
        raise MopsError("BAD_ARGS", f"route 名稱要像 pdf.apify_raw_mcp（<list|link|pdf>.<小寫底線>）：{key}")
    d = load_learned()
    r = d.setdefault("routes", {}).setdefault(env, {}).setdefault(key, {"ok": 0, "fail": 0, "streak_fail": 0})
    if ok is not None:  # ok=None：只更新經驗說明，不計數（成敗已由 plan／ingest 自動記過）
        r["ok" if ok else "fail"] += 1
        r["streak_fail"] = 0 if ok else r.get("streak_fail", 0) + 1
        r["last_ok" if ok else "last_fail"] = date.today().isoformat()
    if note:
        r["note" if manual else "last_msg"] = note[:300]
    save_learned(d)


def record_company(code: str, note: str = "", **fields) -> None:
    d = load_learned()
    c = d.setdefault("companies", {}).setdefault(code, {})
    before = json.dumps(c, ensure_ascii=False, sort_keys=True)
    for k, v in fields.items():
        if v not in (None, "", []):
            c[k] = v
    if not note and json.dumps(c, ensure_ascii=False, sort_keys=True) == before:
        return
    if note:
        notes = [n for n in c.get("notes", []) if n[11:] != note]  # 同內容只留最新一筆
        c["notes"] = ([f"{date.today().isoformat()} {note}"] + notes)[:8]
    save_learned(d)


def route_order(stage: str, env: str, learned: dict | None = None) -> list[str]:
    """預設順序 + 經驗：連續失敗 ≥ 2 次的路徑往後排，成功率高的往前；新學到的路徑排在預設之後。"""
    learned = learned or load_learned()
    stats = learned.get("routes", {}).get(env, {})
    names = list(DEFAULT_ROUTES[stage])
    names += sorted(k.split(".", 1)[1] for k in stats if k.startswith(stage + ".") and k.split(".", 1)[1] not in names)

    def score(n: str):
        s = stats.get(f"{stage}.{n}", {})
        ok, fail, streak = s.get("ok", 0), s.get("fail", 0), s.get("streak_fail", 0)
        return (streak >= 2, -(ok / (ok + fail)) if ok + fail else -0.5, names.index(n))
    return sorted(names, key=score)


# ---------------------------------------------------------------- Apify REST（有 token 時由 script 自己跑）
def apify_token() -> str | None:
    t = os.environ.get("APIFY_TOKEN", "").strip()
    if t:
        return t
    for p in (SKILL_DIR / ".env", REPO_ROOT / ".claude/skills/mops/.env", Path.home() / ".config/mops/.env"):
        if p.is_file():
            for line in p.read_text(encoding="utf-8-sig").splitlines():
                k, _, v = line.partition("=")
                if k.strip().removeprefix("export ").strip() == "APIFY_TOKEN" and v.strip():
                    return v.strip().strip('"').strip("'")
    if os.environ.get("MOPS_APIFY_PROXY_AUTH") == "1":
        return "proxy-injected-apify-token"  # 雲端 network secret（api.apify.com）由代理注入
    return None


def apify_fetch(url: str, fmt: str, token: str) -> tuple[bytes | str, dict]:
    body = json.dumps({"url": url, "formats": [fmt]}).encode()
    st, data, _ = http_req(f"{APIFY_RUN}?timeout=280", data=body, timeout=320, retries=0, min_gap=0,
                           headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    if st in (401, 403):
        raise MopsError("APIFY_AUTH", f"Apify 拒絕（HTTP {st}）：{data[:200].decode('utf-8', 'replace')}")
    if st >= 400:
        raise MopsError("APIFY_ERROR", f"Apify HTTP {st}：{data[:200].decode('utf-8', 'replace')}")
    items = json.loads(data.decode("utf-8"))
    it = items[0] if isinstance(items, list) and items else {}
    meta = {k: it.get(k) for k in ("fetch",) if k in it}
    v = it.get(fmt)
    if fmt == "raw" and isinstance(v, str):
        return base64.b64decode(v), meta
    return v or "", meta


# ---------------------------------------------------------------- 計畫檔
def plan_path(code: str) -> Path:
    return CACHE / f"plan_{code}.json"


def load_plan(code: str | None) -> dict:
    if not code:
        lp = CACHE / "last_plan.txt"
        code = lp.read_text(encoding="utf-8").strip() if lp.is_file() else ""
    p = plan_path(code)
    if not code or not p.is_file():
        raise MopsError("NO_PLAN", f"找不到 {code or '(上次)'} 的計畫檔 → 先跑 `mops.py plan --code {code or '代號'}`")
    return json.loads(p.read_text(encoding="utf-8"))


def save_plan(plan: dict) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    plan_path(plan["code"]).write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    (CACHE / "last_plan.txt").write_text(plan["code"], encoding="utf-8")


def refresh_cover(plan: dict) -> None:
    folder = Path(plan["folder"])
    for it in plan["selected"]:
        cov, weak = existing_cover(folder, it, plan["code"], plan["company"]["market"])
        it["cover"] = cov.name if cov else None
        it["weak"] = weak.name if weak else None
        if it.get("saved"):  # 本次 download／ingest 落地的檔 → 保留 downloaded／ingested 狀態
            continue
        it["status"] = "covered" if cov else "pending"


# ---------------------------------------------------------------- Log
ERROR_HEADER = """# MOPS 錯誤報告

> 由 `.claude/skills/mops/scripts/mops.py` 自動寫入，最新在最上面（最多 50 筆）。不含任何 token。
> 種類：`NETWORK`、`NOT_FOUND`、`AMBIGUOUS`、`PARSE_ERROR`（清單解析不到檔案）、`SIZE_MISMATCH`（落地檔大小與清單不同）、
> `APIFY_AUTH`／`APIFY_ERROR`、`NO_PLAN`、`LEARNED_CORRUPT`、`SCRIPT_BUG`／`SELFTEST_FAIL`（→ AI 依 SKILL.md §9 自我修正）。

<!-- entries -->
"""


def log_error(kind: str, msg: str, argv: list[str], tb: str | None = None, url: str | None = None) -> Path:
    L = [f"## {datetime.now():%Y-%m-%d %H:%M:%S} — {kind}", "",
         f"- 指令：`mops.py {' '.join(argv)}`（script v{VERSION}，Python {sys.version.split()[0]}，{sys.platform}）",
         f"- 錯誤：{msg}"]
    if url:
        L.append(f"- 網址：`{url}`")
    if kind in ("SCRIPT_BUG", "SELFTEST_FAIL", "PARSE_ERROR", "LEARNED_CORRUPT"):
        L.append("- 處理：**AI 必須依 SKILL.md §9 自我修正**（修 script／SKILL.md → selftest 全過 → 同步 .agents → §10 變更紀錄）")
    if tb:
        L += ["", "```text", tb.strip()[-3000:], "```"]
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    old = ERROR_LOG.read_text(encoding="utf-8") if ERROR_LOG.is_file() else ERROR_HEADER
    if "<!-- entries -->" not in old:
        old = ERROR_HEADER + old
    head, _, rest = old.partition("<!-- entries -->\n")
    entries = [x for x in re.split(r"(?m)^(?=## \d{4}-\d{2}-\d{2} )", rest) if x.strip()][:49]
    ERROR_LOG.write_text(head + "<!-- entries -->\n" + "\n".join(L) + "\n\n" + "\n".join(x.rstrip() + "\n" for x in entries),
                         encoding="utf-8")
    return ERROR_LOG


def write_summary(lines: list[str]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    p = LOG_DIR / f"mops_Summary_{date.today():%Y%m%d}.md"
    head = "" if p.is_file() else f"# MOPS 執行報告 {date.today():%Y-%m-%d}\n\n"
    with p.open("a", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n\n")
    return p


# ---------------------------------------------------------------- plan
def _detect_env(code: str, force: str | None) -> tuple[str, bytes | None, str]:
    if force:
        return force, None, ""
    url = list_urls(code, date.today())[0][1]
    try:
        st, data, ct = http_req(url, timeout=30, retries=0)
    except MopsError:
        return "blocked_ip", None, ""
    if st != 200 or is_block_page(data):
        return "blocked_ip", None, ""
    return "open_ip", data, ct


def _cmd_plan(a) -> int:
    c = resolve_company(a.code, a.name)
    code = c["code"]
    folder, will_create = resolve_folder(c, a.out)
    learned = load_learned()
    print(f"[mops] 公司：{fmt_company(c)}")
    print(f"[mops] 資料夾：{folder}" + ("（不存在，download/ingest 時自動建立）" if will_create else ""))
    texts, used = [], ""
    if a.html:
        env = a.env or "blocked_ip"
        for f in a.html:
            texts.append(load_list_source(Path(f)))
        used = f"AI 提供的清單檔（{a.route}）"
    else:
        env, first, ct = _detect_env(code, a.env)
        if env == "open_ip":
            for i, (tag, url) in enumerate(list_urls(code, date.today())):
                if i == 0 and first is not None:
                    data, ctype = first, ct
                else:
                    st, data, ctype = http_req(url, timeout=45)
                    if st != 200 or is_block_page(data):
                        env = "blocked_ip"
                        break
                texts.append(decode_html(data, ctype))
            used = "直連 doc.twse.com.tw"
        if env == "open_ip":
            record_route("list.direct", True, env)
        else:
            texts = []
            tok = apify_token()
            if tok:
                try:
                    for _, url in list_urls(code, date.today()):
                        v, _ = apify_fetch(url, "html", tok)
                        texts.append(str(v))
                    used = "Apify REST（script）"
                    record_route("list.apify_rest", True, env)
                except MopsError as e:
                    record_route("list.apify_rest", False, env, str(e))
                    texts = []
            if not texts:
                record_route("list.direct", False, env, "947 bytes 安全性封鎖頁（依來源 IP）")
                order = [r for r in route_order("list", env, learned) if r not in SCRIPT_ROUTES]
                print(f"[mops] ⚠ 本機 IP 被 TWSE 封鎖（{env}），script 無法直接取得清單。")
                print(f"[mops] 建議 MCP 順序：{' → '.join(order)}（詳見 SKILL.md §4）")
                print("[mops] 請用 MCP 依序抓下列網址（firecrawl_scrape：formats [\"html\"]、proxy \"stealth\"、maxAge 0、onlyMainContent false），")
                print("       每頁 HTML 存成一個檔（工具結果若被自動存檔，直接用該檔路徑），再執行：")
                files = []
                urls = list_urls(code, date.today())
                for tag, url in urls:
                    opt = tag == urls[-1][0]
                    print(f"  {tag}: {url}" + ("  ← 選抓：前 2 頁 F 不足 2 份「股東會年報」時才需要（1～5 月常見）" if opt else ""))
                    if not opt:
                        files.append(f"<SCRATCH>/mops_{code}_{tag}.html")
                print(f"  python {_self_rel()} plan --code {code} --html {' '.join(files)}")
                print("NEED_MCP=list")
                return 4
    rows = []
    for t in texts:
        rows += parse_list(t, code)
    rows = list({r["file"]: r for r in rows}.values())
    if not rows:
        if a.html:
            record_route(a.route, False, env, "清單檔解析不到任何檔名")
        raise MopsError("PARSE_ERROR", "清單裡解析不到任何財報／年報檔名（頁面是空表單、封鎖頁或格式改了？）")
    if a.html:
        record_route(a.route, True, env)
    sel = select(rows, a.annual, a.quarter, a.lang)
    plan = {"code": code, "company": c, "folder": str(folder), "env": env, "lang": a.lang, "source": used,
            "time": datetime.now().isoformat(timespec="seconds"), "rows": rows, "selected": []}
    for r in sel:
        r["target"] = target_name(r, code, c["market"])
        r["step9"] = step9_url(code, r)
        plan["selected"].append(r)
    refresh_cover(plan)
    lags = en_lag_days(rows)
    if lags:
        record_company(code, name=c["abbr"], market=c["market"], en_lag_days=sorted(lags)[len(lags) // 2])
    save_plan(plan)

    n_a = sum(r["kind"] == "annual" for r in sel)
    n_q = sum(r["kind"] == "fin" for r in sel)
    L = [f"## {datetime.now():%H:%M:%S} — plan {code} {c['abbr']}（{c['market']}）", "",
         f"- 指令：`mops.py {' '.join(sys.argv[1:])}`", f"- 清單來源：{used}；環境：{env}；解析 {len(rows)} 個檔",
         f"- 年報 {n_a}/{a.annual}、季報 {n_q}/{a.quarter}；語言偏好 {a.lang}", "- 選定："]
    print(f"[mops] 清單來源：{used}；解析 {len(rows)} 個檔；環境 {env}")
    for r in plan["selected"]:
        state = f"已有 {r['cover']}" if r["cover"] else "待下載" + (f"（{r['weak']} 佔名但內容不合格 → 存成 _MOPS）" if r["weak"] else "")
        line = (f"{r['target']:<28} ← {r['file']}（{r['size']:,} bytes，上傳 {r['uploaded']}，"
                f"{r['lang']}{'／' + r['scope'] if r.get('scope') else ''}）：{state}")
        print("  " + line)
        L.append("  - " + line)
    gaps = []
    if n_a < a.annual:
        gaps.append(f"年報只有 {n_a}/{a.annual} 份（新上市、或今年股東會年報尚未上傳）")
    if n_q < a.quarter:
        gaps.append(f"季報只有 {n_q}/{a.quarter} 份")
    if c["market"] == "興櫃":
        gaps.append("興櫃公司只申報半年報（H1）與年度財報，沒有 Q1／Q3")
    lag = load_learned().get("companies", {}).get(code, {}).get("en_lag_days")
    for r in plan["selected"]:
        has_en = any((classify_file(x) or {}).get("lang") == "en" for x in r.get("alternates", []))
        if r["kind"] == "fin" and r["lang"] == "zh" and not has_en and lag is not None:
            gaps.append(f"{r['target']} 英文版尚未上傳（此公司英文版通常晚約 {lag} 天）")
    comp_notes = load_learned().get("companies", {}).get(code, {}).get("notes", [])
    if comp_notes:
        print("[mops] 這家公司的過往經驗：")
        for n in comp_notes:
            print("   - " + n)
    if (c.get("shares") or "").isdigit():
        print(f"[mops] 每股化用股數（OpenAPI 已發行普通股）：{int(c['shares']):,} 股")
    for g in gaps:
        print(f"[mops] ⚠ {g}")
    if gaps:
        L.append("- 缺口：" + "；".join(gaps))
    pend = [r for r in plan["selected"] if not r["cover"]]
    L.append(f"- 下一步：{'download' if pend else '全部已有，免下載'}")
    write_summary(L)
    print(f"[mops] 計畫已存：{plan_path(code)}")
    print(f"[mops] NEXT → `mops.py download --code {code}`" if pend else "[mops] 全部已有，免下載")
    return 0


def _self_rel() -> str:
    try:
        return str(Path(__file__).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(Path(__file__).resolve())


# ---------------------------------------------------------------- download
def _write_atomic(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dest.parent, prefix=".mops_", suffix=".part")
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    os.chmod(tmp, 0o644)
    os.replace(tmp, dest)


def validate_pdf(data: bytes, expect: int | None) -> str | None:
    if is_block_page(data):
        return "拿到的是 TWSE 安全性封鎖頁（依 IP 封鎖）"
    if not data.startswith(b"%PDF"):
        return f"不是 PDF（檔頭 {data[:8]!r}）"
    if len(data) < MIN_REPORT_BYTES:
        return f"PDF 太小（{len(data)} bytes）"
    if expect and len(data) != expect:
        return f"大小 {len(data):,} ≠ 清單 {expect:,} bytes（下載不完整或不同檔）"
    return None


def dest_for(plan: dict, it: dict, ext: str) -> Path:
    base = it["target"] + ("_MOPS" if it.get("weak") and Path(it["weak"]).stem == it["target"] else "")
    return Path(plan["folder"]) / f"{base}.{ext}"


def _try_direct(plan: dict, it: dict) -> bytes:
    st, page, ct = http_req(it["step9"], timeout=45)
    if st != 200 or is_block_page(page):
        raise MopsError("BLOCKED", "step=9 被封鎖")
    m = PDF_URL_RE.search(decode_html(page, ct))
    if not m:
        raise MopsError("PARSE_ERROR", "step=9 頁面找不到 doc.twse.com.tw/pdf/ 連結", url=it["step9"])
    it["pdf_url"] = m.group(0)
    st, data, _ = http_req(m.group(0), headers={"Referer": DOC}, timeout=180)
    return data


def _try_apify_rest(plan: dict, it: dict, tok: str) -> bytes:
    page, _ = apify_fetch(it["step9"], "html", tok)
    m = PDF_URL_RE.search(str(page))
    if not m:
        raise MopsError("PARSE_ERROR", "Apify 取回的 step=9 頁面沒有 PDF 連結", url=it["step9"])
    it["pdf_url"] = m.group(0)
    data, _ = apify_fetch(m.group(0), "raw", tok)
    return data if isinstance(data, bytes) else b""


def _cmd_download(a) -> int:
    plan = load_plan(a.code)
    folder = Path(plan["folder"])
    if not folder.is_dir():
        if a.no_create:
            raise MopsError("NOT_FOUND", f"公司資料夾不存在：{folder}（拿掉 --no-create 會自動建立）")
        folder.mkdir(parents=True)
        print(f"[mops] 新公司 → 建立資料夾 {folder.name}")
    refresh_cover(plan)
    env = plan["env"]
    tok = apify_token()
    done, need = [], []
    for it in plan["selected"]:
        if it["status"] == "covered" and not a.force:
            print(f"  [skip] {it['target']}：已有 {it['cover']}")
            continue
        ok = False
        for route in route_order("pdf", env):
            if route == "direct" and (env == "open_ip" or a.try_direct):
                fn = lambda: _try_direct(plan, it)  # noqa: E731
            elif route == "apify_rest" and tok:
                fn = lambda: _try_apify_rest(plan, it, tok)  # noqa: E731
            else:
                continue
            try:
                data = fn()
                bad = validate_pdf(data, it["size"])
            except MopsError as e:
                data, bad = b"", f"{e.kind}：{e}"
            if bad:
                record_route(f"pdf.{route}", False, env, bad)
                print(f"  [fail] {it['target']} via {route}：{bad}")
                if "封鎖" in bad:
                    env = "blocked_ip"
                continue
            dest = dest_for(plan, it, "pdf")
            _write_atomic(dest, data)
            record_route(f"pdf.{route}", True, env)
            it.update(status="downloaded", saved=dest.name, route=route)
            done.append(dest)
            print(f"  [ok]   {it['target']} → {dest.name}（{len(data):,} bytes，{route}）")
            ok = True
            break
        if not ok:
            need.append(it)
    plan["env"] = env
    save_plan(plan)
    L = [f"## {datetime.now():%H:%M:%S} — download {plan['code']} {plan['company']['abbr']}", ""]
    L += [f"- ✅ `{p.name}`" for p in done] or ["- （script 沒有下載到新檔）"]
    if need:
        L.append("- 需 MCP：" + "、".join(f"`{it['file']}` → `{it['target']}`" for it in need))
        order = [r for r in route_order("pdf", env) if r not in SCRIPT_ROUTES]
        lorder = [r for r in route_order("link", env) if r not in SCRIPT_ROUTES]
        print(f"\n[mops] ⚠ {len(need)} 份需要 AI 走 MCP（環境 {env}）。連結順序：{' → '.join(lorder)}；PDF 順序：{' → '.join(order)}")
        for it in need:
            print(f"\n  ● {it['target']} ← {it['file']}（清單大小 {it['size']:,} bytes）")
            print(f"    ① 取下載連結：firecrawl_scrape {it['step9']}  (formats [\"html\"], proxy \"stealth\", maxAge 0)")
            print("       → 回傳頁含 https://doc.twse.com.tw/pdf/<檔名>_<yyyyMMdd_HHmmss>.pdf（連結有時效，拿到就馬上做 ②）")
            print("    ② 取 PDF：Apify call-actor actor \"apify/web-fetch\"，input {\"url\": \"<①的連結>\", \"formats\": [\"raw\"]}，"
                  "waitSecs 45、callOptions.timeout 300 → get-actor-run 等到 SUCCEEDED")
            print("       → get-dataset-items（datasetId、fields \"raw,fetch.contentLengthBytes\"、limit 1）"
                  "：結果太大會被自動存成檔案，記下該檔路徑")
            print(f"    ③ 落地：python {_self_rel()} ingest --code {plan['code']} --file {it['file']} --from <②的檔案路徑> --link <①的連結>")
        print("\nNEED_MCP=pdf")
    sp = write_summary(L)
    print(f"[mops] 執行報告：{sp}")
    if done:
        print("[mops] NEXT → 跑 Convert2md skill，<SCOPE> 用下面這個資料夾，轉完再 `mops.py verify`：")
        print(f"CONVERT2MD_SCOPE={folder}")
    return 4 if need else 0


# ---------------------------------------------------------------- ingest
def read_payload(src: Path) -> tuple[str, bytes | str, dict]:
    """回傳 (類型 pdf|md, 內容, 中繼資料)。支援 Apify 結果 JSON（raw base64 / markdown）、PDF、Markdown。"""
    data = src.read_bytes()
    if data.startswith(b"%PDF"):
        return "pdf", data, {}
    if data.lstrip()[:1] in (b"{", b"["):
        j = json.loads(data.decode("utf-8", errors="replace"))
        items = j.get("items", j) if isinstance(j, dict) else j
        if isinstance(items, dict):
            items = [items]
        for it in items or []:
            if not isinstance(it, dict):
                continue
            meta = {"contentLength": it.get("fetch.contentLengthBytes") or (it.get("fetch") or {}).get("contentLengthBytes"),
                    "url": it.get("url") or it.get("fetch.loadedUrl")}
            if isinstance(it.get("raw"), str) and it["raw"]:
                return "pdf", base64.b64decode(it["raw"]), meta
            if isinstance(it.get("markdown"), str) and it["markdown"].strip():
                return "md", it["markdown"], meta
        raise MopsError("PARSE_ERROR", f"{src} 是 JSON，但沒有 raw 或 markdown 欄位")
    return "md", data.decode("utf-8", errors="replace"), {}


def _cmd_ingest(a) -> int:
    plan = load_plan(a.code)
    it = None
    if a.file:
        it = next((x for x in plan["selected"] if x["file"] == a.file), None) or \
             next((dict(r, target=target_name(r, plan["code"], plan["company"]["market"]))
                   for r in plan["rows"] if r["file"] == a.file), None)
        if it is None:
            raise MopsError("NOT_FOUND", f"{a.file} 不在 {plan['code']} 的清單裡（先重跑 plan，或改用 --target）")
    elif a.target:
        it = {"target": a.target, "file": "", "size": None}
    else:
        raise MopsError("BAD_ARGS", "要給 --file（清單上的原始檔名）或 --target（自訂目標檔名，如官網 IR 下載）")
    folder = Path(plan["folder"])
    folder.mkdir(parents=True, exist_ok=True)
    cov, weak = existing_cover(folder, it, plan["code"], plan["company"]["market"]) if it.get("fy") else (None, None)
    it["weak"] = weak.name if weak else None
    if cov and not a.force:
        print(f"[mops] {it['target']} 已有 {cov.name}，不覆蓋（要覆蓋加 --force）")
        return 0
    kind, payload, meta = read_payload(Path(a.src))
    env = plan.get("env", "blocked_ip")
    route = a.route or ("pdf.apify_raw_mcp" if kind == "pdf" and Path(a.src).suffix.lower() != ".pdf" else
                        "pdf.apify_markdown_mcp" if kind == "md" else
                        "pdf.company_ir" if a.target else "pdf.manual")
    src_url = a.link or meta.get("url") or it.get("pdf_url") or ""
    if a.link and a.file:
        record_route(a.link_route, True, env)
    if kind == "pdf":
        bad = validate_pdf(payload, it.get("size") if a.file else None)
        if bad:
            record_route(route, False, env, bad)
            raise MopsError("SIZE_MISMATCH" if "≠" in bad else "PARSE_ERROR", bad)
        dest = dest_for(plan, it, "pdf")
        _write_atomic(dest, payload)
        note = f"{len(payload):,} bytes"
    else:
        text = str(payload)
        if len(text.encode("utf-8")) < MIN_REPORT_BYTES:
            record_route(route, False, env, "markdown 太小")
            raise MopsError("PARSE_ERROR", f"markdown 只有 {len(text)} 字，不像完整財報")
        dest = dest_for(plan, it, "md")
        header = (f"<!-- 來源：TWSE 電子書 {src_url or it.get('file')}（{it.get('file')}，清單 {it.get('size') or '?'} bytes）；"
                  f"{route} 直接轉 Markdown，{date.today().isoformat()} 擷取 -->\n\n")
        _write_atomic(dest, (header + text).encode("utf-8"))
        note = f"markdown {len(text):,} 字"
    record_route(route, True, env)
    for x in plan["selected"]:
        if x["target"] == it["target"]:
            x.update(status="ingested", saved=dest.name, route=route, pdf_url=src_url or x.get("pdf_url"))
    save_plan(plan)
    write_summary([f"## {datetime.now():%H:%M:%S} — ingest {plan['code']}", "",
                   f"- ✅ `{dest.name}` ← `{a.src}`（{note}；{route}）"])
    print(f"[mops] ✅ {dest.name}（{note}；route {route}）")
    if kind == "pdf":
        print("[mops] NEXT → 全部落地後跑 Convert2md skill，<SCOPE>：")
        print(f"CONVERT2MD_SCOPE={folder}")
    else:
        print(f"[mops] 已是 Markdown（不經 Convert2md）→ 直接 `mops.py verify --code {plan['code']}`")
    return 0


# ---------------------------------------------------------------- verify
ZH_NUM = "〇一二三四五六七八九"


def verify_md(md: Path, c: dict, it: dict) -> tuple[bool, str]:
    if not md.is_file():
        return False, "尚未轉成 .md（PDF 還在 → Convert2md 未跑或失敗）"
    size = md.stat().st_size
    if size < MIN_REPORT_BYTES:
        return False, f".md 太小（{size} bytes）"
    text = md.read_text(encoding="utf-8", errors="replace")
    cid = len(CID_RE.findall(text))
    if cid >= 50:
        return False, f"CID 亂碼 {cid} 次 → 改抓英文版（plan --lang en）或官網 IR"
    head = re.sub(r"[`*#\s|]", "", re.sub(r"<[^>]{1,40}>", "", text[:30000])).lower()
    names = [_norm(c.get("abbr", "")), _norm(c.get("name", "")), _norm(c.get("en", "")), c["code"]]
    if not any(n and len(n) >= 2 and n in head for n in names):
        return False, "前 3 萬字找不到公司名／代號 → 可能抓錯公司"
    warn = ""
    if it.get("kind") == "fin" and it.get("q") in (1, 2, 3):
        roc = it["fy"] - 1911
        pats = [f"第{it['q']}季", f"第{ZH_NUM[it['q']]}季", f"q{it['q']}", "quarter", "sixmonths", "ninemonths",
                "threemonths"]
        if (str(roc) not in head and str(it["fy"]) not in head) or not any(p in head for p in pats):
            warn = f"；⚠ 前 3 萬字沒看到「{roc}年第{it['q']}季」字樣，請人工確認期別"
    return True, f"OK（{size / 1024:.0f} KB，CID {cid}）{warn}"


def add_source_header(md: Path, it: dict) -> bool:
    """Convert2md 產出的 .md 沒有來源 → 在檔頭補一行（已有「來源」註解就不動）。"""
    text = md.read_text(encoding="utf-8", errors="replace")
    if text[:400].lstrip().startswith("<!-- 來源"):
        return False
    url = it.get("pdf_url") or f"doc.twse.com.tw/pdf/{it['file']}"
    hdr = (f"<!-- 來源：TWSE 電子書 {url}（{it['file']}，{it.get('size') or '?':,} bytes，"
           f"{it.get('uploaded') or '?'} 上傳）；mops skill 下載（{it.get('route') or '既有檔'}），"
           f"{date.today().isoformat()} 驗證 -->\n\n") if isinstance(it.get("size"), int) else \
          f"<!-- 來源：TWSE 電子書 {url}（{it['file']}）；mops skill，{date.today().isoformat()} 驗證 -->\n\n"
    _write_atomic(md, (hdr + text).encode("utf-8"))
    return True


def _cmd_verify(a) -> int:
    plan = load_plan(a.code)
    refresh_cover(plan)
    folder, c = Path(plan["folder"]), plan["company"]
    bad, L = 0, [f"## {datetime.now():%H:%M:%S} — verify {plan['code']}（{folder.name}）", ""]
    for it in plan["selected"]:
        name = it.get("saved") or it.get("cover") or f"{it['target']}.pdf"
        md = folder / (Path(name).stem + ".md")
        if it["status"] == "covered" and not md.is_file():
            line = f"- ➖ `{it['target']}`：由既有檔 `{it['cover']}` 涵蓋（非 .md，本次不驗證）"
        else:
            ok, note = verify_md(md, c, it)
            if ok and it.get("file") and it["status"] in ("downloaded", "ingested") and add_source_header(md, it):
                note += "；已補來源標頭"
            bad += not ok
            line = f"- {'✅' if ok else '❌'} `{md.name}`：{note}" + ("（既有檔）" if it["status"] == "covered" else "")
        L.append(line)
        print(line)
    sp = write_summary(L)
    print(f"[mops] verify：{len(plan['selected']) - bad}/{len(plan['selected'])} 通過 → {sp}")
    return 1 if bad else 0


# ---------------------------------------------------------------- learn / lessons
def _cmd_learn(a) -> int:
    if a.route:
        if not (a.ok or a.fail or a.note):
            raise MopsError("BAD_ARGS", "--route 要搭配 --ok、--fail 或 --note（只寫說明不計數）")
        result = True if a.ok else False if a.fail else None
        record_route(a.route, result, a.env, a.note or "", manual=True)
        print(f"[mops] 已記錄 {a.route} {'成功' if result else '失敗' if result is False else '說明'}（{a.env}）")
    if a.code:
        if not (a.note or a.ir):
            raise MopsError("BAD_ARGS", "--code 要搭配 --note 或 --ir")
        info = {}
        try:
            hit = lookup(a.code, load_companies())
            info = {"name": hit[0]["abbr"], "market": hit[0]["market"]} if len(hit) == 1 else {}
        except MopsError:
            pass
        record_company(a.code, a.note or "", ir=a.ir, **info)
        print(f"[mops] 已記錄 {a.code} 的公司經驗")
    if not a.route and not a.code:
        raise MopsError("BAD_ARGS", "learn 需要 --route 或 --code")
    return 0


def _cmd_lessons(a) -> int:
    d = load_learned()
    for env in ENVS:
        stats = d.get("routes", {}).get(env, {})
        print(f"## 環境 {env}" + ("（雲端／海外 IP：TWSE 依 IP 封鎖）" if env == "blocked_ip" else "（台灣 IP：可直連）"))
        for stage in DEFAULT_ROUTES:
            print(f"  {stage:<4} 建議順序：{' → '.join(route_order(stage, env, d))}")
        for k in sorted(stats):
            s = stats[k]
            print(f"    {k:<26} ok {s.get('ok', 0)} / fail {s.get('fail', 0)}（連敗 {s.get('streak_fail', 0)}；"
                  f"最後成功 {s.get('last_ok', '-')}；最後失敗 {s.get('last_fail', '-')}）{('：' + s['note']) if s.get('note') else ''}"
                  f"{('｜最近訊息：' + s['last_msg']) if s.get('last_msg') else ''}")
    comps = d.get("companies", {})
    for code in sorted(comps):
        if a.code and code != a.code:
            continue
        c = comps[code]
        print(f"## {code} {c.get('name', '')}（{c.get('market', '')}）IR：{c.get('ir', '-')}；英文版晚 {c.get('en_lag_days', '?')} 天")
        for n in c.get("notes", []):
            print(f"  - {n}")
    return 0


# ---------------------------------------------------------------- selftest
FIXTURE_A = """<table><tr><th>證券代號</th><th>資料年度</th><th>資料細節說明</th><th>電子檔案</th><th>檔案大小</th><th>上傳日期</th></tr>
<tr><td>6279</td><td>115 年 第一季</td><td>財務報告書</td><td>IFRSs合併財報</td><td><a>202601_6279_AI1.pdf</a></td><td align="right">  1,448,753</td><td>115/05/11 16:53:46</td></tr>
<tr><td>6279</td><td>115 年 第一季</td><td>財務報告書</td><td>IFRSs英文版-合併財報</td><td><a>202601_6279_AIA.pdf</a></td><td align="right">  1,938,361</td><td>115/06/16 16:38:51</td></tr>
<tr><td>6279</td><td>115 年 第二季</td><td>財務報告書</td><td>IFRSs合併財報</td><td><a>202602_6279_AI1.pdf</a></td><td align="right">  1,503,120</td><td>115/08/13 15:54:35</td></tr>
<tr><td>6279</td><td>115 年 第三季</td><td>財務報告書</td><td>IFRSs合併財報</td><td><a>202603_6279_AI1.pdf</a></td><td align="right">  1,586,330</td><td>115/11/11 15:04:10</td></tr>
</table>"""
FIXTURE_F = """<table><tr><td>6279</td><td>114 年</td><td>開會通知</td><td><a>2025_6279_20250626F01.pdf</a></td><td>1,009,248</td><td>114/05/23 10:12:51</td></tr>
<tr><td>6279</td><td>113 年</td><td>股東會年報(尚未適用永續揭露準則)</td><td><a>2024_6279_20250626F04.pdf</a></td><td>3,706,420</td><td>114/05/23 10:13:32</td></tr>
<tr><td>6279</td><td>114 年</td><td>年報前十大股東相互間關係表</td><td><a>2025_6279_20250626F17.pdf</a></td><td>411,009</td><td>114/05/23 10:14:16</td></tr>
<tr><td>6279</td><td>113 年</td><td>英文版-股東會年報(尚未適用永續揭露準則)</td><td><a>2024_6279_20250626FE4.pdf</a></td><td>3,811,598</td><td>114/05/23 10:15:07</td></tr>
<tr><td>6279</td><td>114 年</td><td>股東會年報(尚未適用永續揭露準則)</td><td><a>2025_6279_20260624F04.pdf</a></td><td>3,900,000</td><td>115/05/22 10:13:32</td></tr>
</table>"""
# Apify formats:["text"] 取 Big5 頁面時中文全變亂碼，只剩 ASCII（檔名、大小、日期）可用
FIXTURE_TEXT = "6279 ??? ??? 202603_6279_AI1.pdf 1,586,330 115/11/11 15:04:10 ?? 2024_6279_20250626FE4.pdf 3,811,598 114/05/23"


def _cmd_selftest(a, parser: argparse.ArgumentParser) -> int:
    fails: list[str] = []

    def check(name: str, cond: bool, info: str = "") -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {name}{('  — ' + info) if info and not cond else ''}")
        if not cond:
            fails.append(f"{name}：{info}")

    print("[selftest] 清單解析")
    rows = parse_list(FIXTURE_A, "6279") + parse_list(FIXTURE_F, "6279")
    check("解析出 9 個檔（含 2 個非年報股東會檔）", len(rows) == 9, str([r["file"] for r in rows]))
    by = {r["file"]: r for r in rows}
    check("AI1 = 中文合併", by.get("202603_6279_AI1.pdf", {}).get("scope") == "合併")
    check("上傳日 115/11/11 → 2026-11-11", by.get("202603_6279_AI1.pdf", {}).get("uploaded") == "2026-11-11")
    check("大小 1,586,330", by.get("202603_6279_AI1.pdf", {}).get("size") == 1586330)
    check("F04 + 說明「股東會年報」= 中文年報", by.get("2024_6279_20250626F04.pdf", {}).get("kind") == "annual")
    check("FE4 + 說明「英文版-股東會年報」= 英文年報", by.get("2024_6279_20250626FE4.pdf", {}).get("lang") == "en")
    check("F17「年報前十大股東」不是年報", by.get("2025_6279_20250626F17.pdf", {}).get("kind") == "agm_other")
    tr = parse_list(FIXTURE_TEXT, "6279")
    check("亂碼文字版仍可解析檔名／大小／日期", len(tr) == 2 and tr[1]["kind"] == "annual" and tr[1]["lang"] == "en",
          str(tr))
    check("FE6（KY 英文年報）代碼推定", (classify_file("2024_6781_20250528FE6.pdf") or {}).get("lang") == "en")
    check("封鎖頁偵測", is_block_page("因為安全性考量，您所執行的頁面無法呈現。FOR SECURITY REASONS".encode("utf-8")))
    check("Big5 解碼", "胡連" in decode_html("公司名稱：胡連".encode("cp950"), "text/html;charset=big5"))

    print("[selftest] 選檔與命名")
    sel = select(rows, 2, 1, "zh")
    names = [target_name(r, "6279", "上櫃") for r in sel]
    check("最新 2 年報 + 1 季報", names == ["6279_AnnualReport_2025", "6279_AnnualReport_2024", "6279_Quarter_2026Q3"],
          str(names))
    check("中文優先、英文列為備援", sel[1]["file"].endswith("F04.pdf") and sel[1]["alternates"] == ["2024_6279_20250626FE4.pdf"])
    sel_en = select(rows, 2, 1, "en")
    check("--lang en 選英文年報", sel_en[1]["file"].endswith("FE4.pdf"))
    h1 = {"kind": "fin", "fy": 2026, "q": 2}
    check("興櫃 Q2 → H1", target_name(h1, "2245", "興櫃") == "2245_Quarter_2026H1")
    check("上櫃 Q2 → Q2", target_name(h1, "2249", "上櫃") == "2249_Quarter_2026Q2")
    check("合併優於個體", select([dict(by["202603_6279_AI1.pdf"], code="AI3", scope="個體", file="x_AI3.pdf"),
                                 by["202603_6279_AI1.pdf"]], 0, 1, "zh")[0]["scope"] == "合併")
    check("英文版時差", en_lag_days(rows) == [36, 0], str(en_lag_days(rows)))
    check("step=9 網址", step9_url("6279", by["202603_6279_AI1.pdf"]).endswith(
        "step=9&kind=A&co_id=6279&filename=202603_6279_AI1.pdf&colorchg=1"))

    print("[selftest] 既有檔判定（repo 實際出現過的舊檔名）")
    big = "股票代碼 合併財務報告暨會計師核閱報告 財務報告\n" + "x" * STRONG_MD_BYTES
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        for n in ("2022年報2022_2245_20230613F04_20260420_120806.md", "202504_8433_AI1_20260522_011705.md",
                  "4417_2026Q1_quarterly_report.md", "1521_QuarterlyReport_2026Q2.md", "2249_quarter_2026Q1.md",
                  "2245_Quarter_2026H1.md", "2024_6279_20250626F04.md", "8433_annual_2025.md",
                  "4417_2025_annual_report.md", "202601_2881_AI1.md"):
            (tdp / n).write_text(big, encoding="utf-8")
        (tdp / "1264_Quarter_2026Q3.md").write_text("MoneyDJ 第3季損益表轉載", encoding="utf-8")  # 太小 = 不合格
        cases = [("2245", {"kind": "annual", "fy": 2022}, "興櫃", True),
                 ("8433", {"kind": "fin", "fy": 2025, "q": 4}, "上櫃", True),
                 ("8433", {"kind": "annual", "fy": 2025}, "上櫃", True),
                 ("4417", {"kind": "fin", "fy": 2026, "q": 1}, "上市", True),
                 ("4417", {"kind": "annual", "fy": 2025}, "上市", True),
                 ("1521", {"kind": "fin", "fy": 2026, "q": 2}, "上市", True),
                 ("2249", {"kind": "fin", "fy": 2026, "q": 1}, "上櫃", True),
                 ("2245", {"kind": "fin", "fy": 2026, "q": 2}, "興櫃", True),
                 ("6279", {"kind": "annual", "fy": 2024}, "上櫃", True),
                 ("2881", {"kind": "fin", "fy": 2026, "q": 1}, "上市", True),
                 ("6279", {"kind": "annual", "fy": 2025}, "上櫃", False),
                 ("4417", {"kind": "fin", "fy": 2026, "q": 2}, "上市", False),
                 ("1264", {"kind": "fin", "fy": 2026, "q": 3}, "上櫃", False)]
        for t, r, mk, want in cases:
            cov, _ = existing_cover(tdp, r, t, mk)
            check(f"{t} {r} → {'已有' if want else '沒有'}", (cov is not None) == want, str(cov))
        _, weak = existing_cover(tdp, {"kind": "fin", "fy": 2026, "q": 3}, "1264", "上櫃")
        check("小檔佔名 → 新檔另存 _MOPS", weak is not None and weak.stem == "1264_Quarter_2026Q3")

    print("[selftest] ingest 解析 Apify 結果檔")
    with tempfile.TemporaryDirectory() as td:
        pdf = b"%PDF-1.5\n" + b"0" * 20000
        jp = Path(td) / "r.json"
        jp.write_text(json.dumps({"items": [{"raw": base64.b64encode(pdf).decode(), "fetch.contentLengthBytes": len(pdf)}]}),
                      encoding="utf-8")
        k, payload, meta = read_payload(jp)
        check("raw base64 → PDF", k == "pdf" and payload == pdf and meta["contentLength"] == len(pdf))
        jp.write_text(json.dumps([{"markdown": "# 胡連 合併財務報告", "url": "u"}]), encoding="utf-8")
        check("markdown 欄位 → md", read_payload(jp)[0] == "md")
        check("validate_pdf 大小不符會擋", validate_pdf(pdf, len(pdf) + 1) is not None and validate_pdf(pdf, len(pdf)) is None)

    print("[selftest] 路徑排序（經驗庫）")
    fake = {"routes": {"blocked_ip": {"pdf.apify_raw_mcp": {"ok": 0, "fail": 3, "streak_fail": 3},
                                      "pdf.new_way": {"ok": 2, "fail": 0, "streak_fail": 0}}}}
    order = route_order("pdf", "blocked_ip", fake)
    check("連敗 ≥2 次往後排、新路徑會被納入", order[-1] == "apify_raw_mcp" and "new_way" in order, str(order))
    learned = None
    try:
        learned = load_learned()
        bad = [k for e in learned.get("routes", {}).values() for k in e if not ROUTE_KEY_RE.match(k)]
        check("learned.json 合法、route 名稱格式正確", not bad, str(bad))
    except MopsError as e:
        check("learned.json 可讀", False, str(e))

    print("[selftest] SKILL.md 與 CLI 參數一致")
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8") if (SKILL_DIR / "SKILL.md").is_file() else ""
    check("SKILL.md 存在", bool(text))
    subs = {}
    for act in parser._actions:  # noqa: SLF001
        if isinstance(act, argparse._SubParsersAction):  # noqa: SLF001
            subs = act.choices
    opts = {o for sp in subs.values() for act in sp._actions for o in act.option_strings}  # noqa: SLF001
    for sc in sorted(set(re.findall(r"mops\.py\s+([a-z]+)", text))):
        check(f"SKILL.md 提到的子指令 `{sc}` 存在", sc in subs, f"CLI 沒有 {sc}")
    own = "\n".join(l for l in text.splitlines() if not re.search(r"selfcheck\.py|check_md\.py|edinet\.py|inventory\.py", l))
    for op in sorted(set(re.findall(r"(?<![\w-])(--[a-z][a-z-]+)", own))):
        check(f"SKILL.md 提到的參數 `{op}` 存在", op in opts, f"CLI 沒有 {op}")
    for sc in subs:
        check(f"子指令 `{sc}` 有寫進 SKILL.md", f"mops.py {sc}" in text, "SKILL.md 漏寫")
    for r in sorted({f"{s}.{n}" for s, ns in DEFAULT_ROUTES.items() for n in ns}):
        check(f"路徑 `{r}` 有寫進 SKILL.md", f"`{r}`" in text, "SKILL.md §4 漏寫")

    print("[selftest] .claude / .agents 鏡像同步、.gitignore")
    base_c, base_a = REPO_ROOT / ".claude/skills/mops", REPO_ROOT / ".agents/skills/mops"
    rels = sorted({str(p.relative_to(base_c)) for p in base_c.rglob("*") if p.is_file()
                   and "__pycache__" not in p.parts and p.name != ".env"}) if base_c.is_dir() else []
    for rel in rels:
        a1, a2 = base_c / rel, base_a / rel
        check(f"鏡像一致 {rel}", a2.is_file() and a1.read_bytes() == a2.read_bytes(),
              "不同或缺檔 → 跑 collectStk selfcheck.py --fix 或手動複製 .claude 版")
    gi = REPO_ROOT / ".gitignore"
    check(".gitignore 排除 .env", gi.is_file() and re.search(r"(?m)^\.env\s*$", gi.read_text(encoding="utf-8")) is not None)

    if not a.offline:
        print("[selftest] 線上：OpenAPI 公司資料、doc.twse 直連")
        try:
            hit = lookup("6279", load_companies())
            check("OpenAPI：6279 → 胡連", bool(hit) and hit[0]["abbr"] == "胡連", str(hit[:1]))
        except MopsError as e:
            check("OpenAPI 公司資料", False, str(e))
        env, _, _ = _detect_env("6279", None)
        print(f"  INFO  doc.twse 直連：{'可（台灣 IP）' if env == 'open_ip' else '被 IP 封鎖 → 走 MCP 路徑（雲端正常現象）'}")
        print(f"  INFO  Apify token：{'有（script 可自己跑 apify_rest）' if apify_token() else '無（apify 改由 AI 用 MCP 跑）'}")

    print(f"[selftest] {'全部通過' if not fails else f'{len(fails)} 項失敗'}")
    if fails:
        p = log_error("SELFTEST_FAIL", "；".join(fails[:20]), sys.argv[1:])
        print(f"[selftest] 失敗明細已寫入 {p}", file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------- CLI
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=f"MOPS／TWSE 電子書 台股年報・季報下載器 v{VERSION}")
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lookup", help="找公司")
    s.add_argument("query")
    s = sub.add_parser("plan", help="取清單、選檔、比對資料夾")
    s.add_argument("--code", required=True, help="股票代號（如 6279）或公司簡稱")
    s.add_argument("--name", help="OpenAPI 查不到時的公司簡稱")
    s.add_argument("--html", nargs="+", help="MCP 抓回的清單頁檔案（HTML／JSON／文字），可多個")
    s.add_argument("--annual", type=int, default=2, help="年報份數（預設 2）")
    s.add_argument("--quarter", type=int, default=1, help="季報份數（預設 1）")
    s.add_argument("--lang", choices=("zh", "en"), default="zh", help="語言偏好（預設 zh；CID 亂碼時改 en）")
    s.add_argument("--out", help="公司資料夾（預設：repo 內以代號開頭或名稱相同的資料夾）")
    s.add_argument("--env", choices=ENVS, help="強制指定環境（略過直連偵測）")
    s.add_argument("--route", default="list.firecrawl_stealth", help="搭配 --html：清單是用哪條路徑抓的（記入經驗庫）")
    s = sub.add_parser("download", help="依計畫下載")
    s.add_argument("--code", help="代號（預設：上次 plan）")
    s.add_argument("--force", action="store_true", help="已存在也重抓")
    s.add_argument("--try-direct", action="store_true", help="環境被判定封鎖時仍試一次直連")
    s.add_argument("--no-create", action="store_true", help="公司資料夾不存在時報錯，不自動建立")
    s = sub.add_parser("ingest", help="落地 MCP 取得的檔案")
    s.add_argument("--code", help="代號（預設：上次 plan）")
    s.add_argument("--file", help="清單上的原始檔名，如 202603_6279_AI1.pdf")
    s.add_argument("--target", help="自訂目標檔名（不在清單的來源，如官網 IR），如 6279_Quarter_2026Q3")
    s.add_argument("--from", dest="src", required=True, help="Apify 結果 JSON／PDF／Markdown 檔路徑")
    s.add_argument("--route", help="這份檔是用哪條路徑拿到的（如 pdf.company_ir），記入經驗庫")
    s.add_argument("--link", help="原始 PDF 網址（寫進 md 來源標頭；有給就記一筆取連結成功）")
    s.add_argument("--link-route", default="link.firecrawl_stealth", help="取得 --link 的路徑（預設 link.firecrawl_stealth）")
    s.add_argument("--force", action="store_true", help="已有也覆蓋")
    s = sub.add_parser("verify", help="Convert2md 後驗證")
    s.add_argument("--code", help="代號（預設：上次 plan）")
    s = sub.add_parser("learn", help="記錄經驗")
    s.add_argument("--route", help="路徑名，如 pdf.apify_raw_mcp、link.firecrawl_stealth")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--ok", action="store_true")
    g.add_argument("--fail", action="store_true")
    s.add_argument("--env", choices=ENVS, default="blocked_ip", help="環境（預設 blocked_ip = 雲端）")
    s.add_argument("--code", help="公司代號（記公司專屬經驗）")
    s.add_argument("--note", help="一句話經驗（含證據）")
    s.add_argument("--ir", help="公司官網 IR 財報頁網址")
    s = sub.add_parser("lessons", help="顯示經驗庫")
    s.add_argument("--code", help="只看這家公司")
    s = sub.add_parser("selftest", help="自我檢查")
    s.add_argument("--offline", action="store_true", help="不連網")
    return ap


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    a = parser.parse_args(argv)
    raw = argv if argv is not None else sys.argv[1:]
    try:
        if a.cmd == "lookup":
            hits = lookup(a.query, load_companies())
            print("\n".join(fmt_company(c) for c in hits[:30]) or "找不到")
            return 0
        return {"plan": _cmd_plan, "download": _cmd_download, "ingest": _cmd_ingest, "verify": _cmd_verify,
                "learn": _cmd_learn, "lessons": _cmd_lessons}.get(a.cmd, lambda x: _cmd_selftest(x, parser))(a)
    except MopsError as e:
        p = log_error(e.kind, str(e), raw, url=e.url)
        print(f"[mops] ✗ {e.kind}：{e}\n[mops] 錯誤報告已寫入：{p}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc()
        p = log_error("SCRIPT_BUG", "未預期例外", raw, tb=tb)
        print(tb, file=sys.stderr)
        print(f"[mops] ✗ SCRIPT_BUG → 已寫入 {p}；AI 請依 SKILL.md §9 自我修正", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
