#!/usr/bin/env python3
"""EDINET API v2 downloader — 日股有価証券報告書（年報）/ 半期報告書 / 四半期報告書（季報）.

只用 Python 標準函式庫（Windows / Linux / macOS / Claude Code 雲端皆可）。

子指令:
  checkkey                                檢查 API key（不印 key）；失敗寫 Log/edinet_error.md
  lookup   <查詢>                         用證券代碼 / EDINET コード / 公司名找公司
  list     --code 3445                    列出該公司在 EDINET 的年報/季報與預定檔名（不下載）
  download --code 3445 [--annual 2 --periodic 1] [--format pdf] [--out DIR]
  verify   [--code 3445]                  Convert2md 之後驗證 .md（存在、大小、公司名、CID）
  selftest [--offline]                    自我檢查：命名邏輯、SKILL.md 與參數一致、.agents 鏡像同步、API

API key 讀取順序（找到即停，key 永遠不會被印出或寫進 log）:
  1. 環境變數 EDINET_API_KEY
  2. 環境變數 EDINET_API_KEY_FILE 指向的檔案
  3. <skill 資料夾>/.env、<repo>/.claude/skills/edinet/.env、<repo>/.agents/skills/edinet/.env
  4. ~/.config/edinet/.env
  5. 都沒有 → 送佔位值，由 Claude Code 雲端環境的「網路密鑰」代理注入真 key
key 一律用 HTTP header `Ocp-Apim-Subscription-Key` 傳送（不放網址）。

結束碼：0 成功／1 一般錯誤／2 API key（授權）錯誤／3 腳本 bug（會寫 SCRIPT_BUG 到 Log/edinet_error.md）
"""
from __future__ import annotations

import argparse
import csv
import http.client
import io
import json
import os
import re
import sys
import tempfile
import threading
import time
import traceback
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path

VERSION = "2.0.1"

# Windows 主控台（cp950/cp932）印日文會 UnicodeEncodeError → 一律 UTF-8
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

API = "https://api.edinet-fsa.go.jp/api/v2"
CODELIST_URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip"
FUNDLIST_URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Fundcode.zip"
UA = f"Mozilla/5.0 (compatible; edinet-skill/{VERSION})"

SKILL_DIR = Path(__file__).resolve().parent.parent


def _find_repo_root() -> Path:
    env = os.environ.get("EDINET_REPO")
    if env:
        return Path(env).expanduser().resolve()
    for p in SKILL_DIR.parents:
        if (p / ".git").exists() or (p / "AGENTS.md").is_file():
            return p
    return SKILL_DIR.parents[2]  # .claude/skills/edinet -> repo


REPO_ROOT = _find_repo_root()
LOG_DIR = REPO_ROOT / "Log"
ERROR_LOG = LOG_DIR / "edinet_error.md"
CACHE = Path(os.environ.get("EDINET_CACHE_DIR") or (Path.home() / ".cache" / "edinet"))
MANIFEST = CACHE / "last_run.json"

# docTypeCode
ANNUAL = {"120"}                 # 有価証券報告書
ANNUAL_AMEND = {"130"}           # 訂正有価証券報告書
QUARTERLY = {"140"}              # 四半期報告書（2024/4 起廢止，只剩舊資料）
HALF = {"160"}                   # 半期報告書
PERIODIC_AMEND = {"150", "170"}  # 訂正四半期 / 訂正半期
PERIODIC = QUARTERLY | HALF
DOC_NAME = {"120": "有価証券報告書", "130": "訂正有価証券報告書", "140": "四半期報告書",
            "150": "訂正四半期報告書", "160": "半期報告書", "170": "訂正半期報告書"}
FORMAT_TYPE = {"xbrl": (1, "zip"), "pdf": (2, "pdf"), "attach": (3, "zip"),
               "english": (4, "zip"), "csv": (5, "zip")}
FORMAT_FLAG = {"pdf": "pdfFlag", "xbrl": "xbrlFlag", "csv": "csvFlag", "attach": "attachDocFlag",
               "english": "englishDocFlag"}
MON = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
QUARTERLY_LAST_PE = date(2024, 6, 30)  # 四半期報告書廢止：此日之後結束的季度不會再有 140
MIN_PDF_BYTES = 10 * 1024

PROXY_PLACEHOLDER = "proxy-injected-edinet-key"  # 雲端：由網路代理把 header 換成真 key
AUTH_KINDS = {"AUTH_INVALID_KEY", "AUTH_FORBIDDEN"}


class EdinetError(Exception):
    def __init__(self, kind: str, msg: str, *, status: str | int | None = None,
                 api_msg: str | None = None, endpoint: str | None = None):
        super().__init__(msg)
        self.kind, self.status, self.api_msg, self.endpoint = kind, status, api_msg, endpoint


# ---------------------------------------------------------------- API key
def _read_env_file(p: Path) -> str | None:
    try:
        lines = p.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            return line.strip('"').strip("'")  # 檔案只放 key 本身也接受
        k, v = line.split("=", 1)
        if k.strip().removeprefix("export ").strip() == "EDINET_API_KEY":
            return v.strip().strip('"').strip("'") or None
    return None


def get_key() -> tuple[str | None, str]:
    k = os.environ.get("EDINET_API_KEY", "").strip().strip('"').strip("'")
    if k:
        return k, "環境變數 EDINET_API_KEY"
    f = os.environ.get("EDINET_API_KEY_FILE")
    if f and (k := _read_env_file(Path(f).expanduser())):
        return k, f"EDINET_API_KEY_FILE ({f})"
    cands = [SKILL_DIR / ".env", REPO_ROOT / ".claude/skills/edinet/.env",
             REPO_ROOT / ".agents/skills/edinet/.env", Path.home() / ".config/edinet/.env"]
    seen = set()
    for p in cands:
        if p in seen:
            continue
        seen.add(p)
        if p.is_file() and (k := _read_env_file(p)):
            return k, str(p)
    return None, ""


def key_format_note(k: str | None) -> str:
    if not k:
        return "本機未設定（送佔位值，靠雲端代理注入）"
    if re.fullmatch(r"[0-9a-fA-F]{32}", k):
        return f"長度 {len(k)}，格式正常（32 碼英數）"
    return f"⚠ 格式異常：長度 {len(k)}（EDINET key 通常是 32 碼 0-9a-f；檢查是否多了空白、引號或貼錯字串）"


def require_key() -> str:
    k, _ = get_key()
    return k or PROXY_PLACEHOLDER


# ---------------------------------------------------------------- HTTP（含全域限流）
MIN_INTERVAL = float(os.environ.get("EDINET_MIN_INTERVAL", "0.2"))  # 秒/請求（約 5 req/s）
_lock = threading.Lock()
_next_slot = [0.0]
STATS = {"requests": 0, "retry_429": 0, "retry_net": 0}


def _throttle() -> None:
    with _lock:
        now = time.monotonic()
        wait = _next_slot[0] - now
        _next_slot[0] = max(now, _next_slot[0]) + MIN_INTERVAL
        STATS["requests"] += 1
    if wait > 0:
        time.sleep(wait)


def _penalize(sec: float) -> None:
    """被限流時讓所有執行緒一起暫停。"""
    with _lock:
        _next_slot[0] = max(_next_slot[0], time.monotonic() + sec)
        STATS["retry_429"] += 1


def _backoff(i: int, retry_after: str | None = None) -> float:
    try:
        if retry_after:
            return min(120.0, float(retry_after))
    except ValueError:
        pass
    return min(60.0, 5.0 * 2 ** i)


def http_get(url: str, params: dict | None = None, key: str | None = None,
             retries: int = 6) -> tuple[bytes, str]:
    full = url + ("?" + urllib.parse.urlencode(params) if params else "")
    headers = {"User-Agent": UA}
    if key:  # header 傳 key（不會出現在網址／log）
        headers["Ocp-Apim-Subscription-Key"] = key
    endpoint = urllib.parse.urlsplit(url).path
    err, kind = None, "NETWORK"
    for i in range(retries):
        _throttle()
        try:
            req = urllib.request.Request(full, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read(), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            body = e.read()[:500].decode("utf-8", "replace")
            if e.code in (401, 403):
                raise EdinetError("AUTH_INVALID_KEY" if e.code == 401 else "AUTH_FORBIDDEN",
                                  f"HTTP {e.code}", status=e.code, api_msg=body, endpoint=endpoint)
            if e.code == 404:
                raise EdinetError("NOT_FOUND", "HTTP 404", status=404, api_msg=body, endpoint=endpoint)
            if e.code == 429 or e.code >= 500:
                kind, err = ("RATE_LIMIT" if e.code == 429 else "API_ERROR"), f"HTTP {e.code} {body[:200]}"
                _penalize(_backoff(i, e.headers.get("Retry-After")))
                continue
            raise EdinetError("API_ERROR", f"HTTP {e.code}", status=e.code, api_msg=body, endpoint=endpoint)
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException) as e:
            kind, err = "NETWORK", str(e)
            STATS["retry_net"] += 1
            time.sleep(min(30, 2 ** i))
    raise EdinetError(kind, f"已重試 {retries} 次仍失敗：{err}", endpoint=endpoint)


def _status_of(j: dict) -> tuple[str, str]:
    meta = j.get("metadata") or {}
    status = str(j.get("StatusCode") or meta.get("status") or "200")
    return status, str(j.get("message") or meta.get("message") or "")


def _raise_for_status(status: str, msg: str, endpoint: str) -> None:
    if status == "401":
        raise EdinetError("AUTH_INVALID_KEY", f"API status {status}", status=status, api_msg=msg, endpoint=endpoint)
    if status == "403":
        raise EdinetError("AUTH_FORBIDDEN", f"API status {status}", status=status, api_msg=msg, endpoint=endpoint)
    if status == "404":
        raise EdinetError("NOT_FOUND", f"API status {status}", status=status, api_msg=msg, endpoint=endpoint)
    raise EdinetError("API_ERROR", f"API status {status}", status=status, api_msg=msg, endpoint=endpoint)


def api_call(path: str, params: dict, key: str, retries: int = 6) -> tuple[bytes, str, dict | None]:
    """呼叫 API；EDINET 常以 HTTP 200 + JSON 內的 status 回錯（含 429）→ 在這裡統一判斷與重試。"""
    url = f"{API}/{path}"
    for i in range(retries):
        data, ctype = http_get(url, params, key)
        if "json" not in ctype.lower():
            return data, ctype, None
        try:
            j = json.loads(data.decode("utf-8"))
        except ValueError:
            raise EdinetError("API_ERROR", "回應不是合法 JSON", api_msg=data[:200].decode("utf-8", "replace"),
                              endpoint=url) from None
        status, msg = _status_of(j)
        if status == "200":
            return data, ctype, j
        if status == "429" or status.startswith("5"):
            _penalize(_backoff(i))
            continue
        _raise_for_status(status, msg, f"/api/v2/{path}")
    raise EdinetError("RATE_LIMIT", f"API 持續回 429/5xx（已重試 {retries} 次）", endpoint=url)


def api_json(path: str, params: dict, key: str) -> dict:
    _, _, j = api_call(path, params, key)
    if j is None:
        raise EdinetError("API_ERROR", "預期 JSON 卻收到其他格式", endpoint=path)
    return j


# ---------------------------------------------------------------- code list
def _load_csv(url: str, fname: str, refresh_days: int = 7) -> list[dict]:
    CACHE.mkdir(parents=True, exist_ok=True)
    csv_path = CACHE / fname
    fresh = csv_path.is_file() and (time.time() - csv_path.stat().st_mtime) < refresh_days * 86400
    if not fresh:
        try:
            data, _ = http_get(url)
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
                csv_path.write_bytes(z.read(name))
        except Exception as e:  # noqa: BLE001
            if not csv_path.is_file():
                raise EdinetError("NETWORK", f"無法下載 {fname}：{e}", endpoint=url) from e
            print(f"[edinet] {fname} 更新失敗，沿用快取：{e}", file=sys.stderr)
    text = csv_path.read_bytes().decode("cp932", "replace")
    rows = list(csv.reader(io.StringIO(text)))
    hi = next((i for i, r in enumerate(rows[:5]) if any("ＥＤＩＮＥＴコード" in c for c in r)), 1)
    header = rows[hi]
    return [dict(zip(header, r)) for r in rows[hi + 1:] if len(r) == len(header)]


def load_codelist() -> list[dict]:
    """EDINET コードリスト + ファンドコードリスト（J-REIT 投資法人的證券代碼與決算期在後者）。"""
    codes = _load_csv(CODELIST_URL, "EdinetcodeDlInfo.csv")
    try:
        funds = _load_csv(FUNDLIST_URL, "FundcodeDlInfo.csv")
    except EdinetError:
        return codes
    by_code = {c["ＥＤＩＮＥＴコード"]: c for c in codes}
    for f in funds:
        c = by_code.get(f.get("ＥＤＩＮＥＴコード", ""))
        # 只合併「發行者 = 基金本身」的投資法人（J-REIT、インフラファンド），避免把投信代碼掛到投信公司上
        if c and f.get("証券コード") and f.get("ファンド名") == f.get("発行者名") and not c.get("証券コード"):
            c["証券コード"] = f["証券コード"]
            c["決算日"] = c.get("決算日") or "/".join(x for x in (f.get("特定期1"), f.get("特定期2")) if x)
            c["上場区分"] = c.get("上場区分") or "上場(投資法人)"
    return codes


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "").lower().replace(" ", "").replace("　", "")


def lookup(query: str, codes: list[dict]) -> list[dict]:
    q = _norm(query)
    out = []
    for c in codes:
        sec = c.get("証券コード", "").lower()
        if q == c.get("ＥＤＩＮＥＴコード", "").lower() or (
                sec and (q == sec or (len(q) == 4 and sec == q + "0"))):
            return [c]
        if len(q) >= 2 and (q in _norm(c.get("提出者名", "")) or q in _norm(c.get("提出者名（英字）", ""))
                            or q in _norm(c.get("提出者名（ヨミ）", ""))):
            out.append(c)
    out.sort(key=lambda c: (not c.get("上場区分", "").startswith("上場"), c.get("証券コード") == ""))
    return out


def resolve_company(code: str) -> dict:
    hits = lookup(code, load_codelist())
    if not hits:
        raise EdinetError("NOT_FOUND", f"コードリスト找不到「{code}」。先用 lookup 子指令確認（非上場或已下市？）。")
    if len(hits) > 1:
        lines = "\n".join(_fmt_company(c) for c in hits[:15])
        raise EdinetError("AMBIGUOUS", f"「{code}」對到多家公司，請改用證券代碼或 EDINET コード：\n{lines}")
    return hits[0]


def _fmt_company(c: dict) -> str:
    sec = c.get("証券コード", "")
    return (f"{c.get('ＥＤＩＮＥＴコード')}  證券代碼={sec[:4] if sec else '-':<5} "
            f"決算日={c.get('決算日', ''):<9} {c.get('上場区分', '')}  {c.get('提出者名')}"
            + (f" / {c['提出者名（英字）']}" if c.get("提出者名（英字）") else ""))


def is_fund(company: dict) -> bool:
    return "投資法人" in company.get("上場区分", "") or "投資法人" in company.get("提出者名", "")


def company_short_name(company: dict) -> str:
    n = unicodedata.normalize("NFKC", company.get("提出者名", ""))
    for w in ("株式会社", "投資法人", "(株)"):
        n = n.replace(w, "")
    return re.sub(r'[\s<>:"/\\|?*]', "", n)


# ---------------------------------------------------------------- daily lists
def daily_list(d: date, key: str) -> list[dict]:
    p = CACHE / "lists" / f"{d.isoformat()}.json"
    stale_limit = date.today() - timedelta(days=7)  # 一週內的清單可能還在變動 → 每次重抓
    if p.is_file() and d < stale_limit:
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            p.unlink(missing_ok=True)  # 快取壞掉 → 重抓
    j = api_json("documents.json", {"date": d.isoformat(), "type": 2}, key)
    res = j.get("results") or []
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)
    return res


def _month_end(y: int, m: int) -> date:
    y2, m2 = (y + 1, 1) if m == 12 else (y, m + 1)
    return date(y2, m2, 1) - timedelta(days=1)


def period_months(company: dict) -> list[int]:
    ms = [int(x) for x in re.findall(r"(\d{1,2})月", company.get("決算日", ""))]
    return list(dict.fromkeys(m for m in ms if 1 <= m <= 12))


# 法定提出期限：有報 = 期末後 3 個月；半期報 / 四半期報 = 期末後 45 日。窗口放寬兩端吸收早交與假日。
ANNUAL_WINDOW = (30, 105)
PERIODIC_WINDOW = (15, 50)


def filing_windows(company: dict, today: date, days: int, want_periodic: bool) -> set[date] | None:
    months = period_months(company)
    if not months:
        return None
    fund = is_fund(company) or len(months) > 1
    lo = today - timedelta(days=days)
    out: set[date] = set()
    for y in range(lo.year - 1, today.year + 1):
        for m in range(1, 13):
            pe = _month_end(y, m)
            wins = []
            if m in months:
                wins.append(ANNUAL_WINDOW)
            if want_periodic and not fund:
                off = (m - months[0]) % 12
                if off == 6 or (off in (3, 9) and pe <= QUARTERLY_LAST_PE):
                    wins.append(PERIODIC_WINDOW)
            for a, b in wins:
                for k in range(a, b + 1):
                    d = pe + timedelta(days=k)
                    if lo <= d <= today:
                        out.add(d)
    return out


def _wanted_types(include_amend: bool) -> set[str]:
    t = ANNUAL | PERIODIC
    return t | ANNUAL_AMEND | PERIODIC_AMEND if include_amend else t


def scan(company: dict, key: str, days: int, annual_n: int, periodic_n: int,
         include_amend: bool = False, workers: int = 4, full_scan: bool = False) -> tuple[list[dict], dict]:
    """往回掃每日提出書類清單（只掃平日）。預設先掃法定申報窗口，份數不夠才補掃其餘日期。"""
    ecode = company["ＥＤＩＮＥＴコード"]
    types = _wanted_types(include_amend)
    today = date.today()
    weekdays = [d for d in (today - timedelta(days=i) for i in range(days + 1)) if d.weekday() < 5]
    win = None if (full_scan or include_amend) else filing_windows(company, today, days, periodic_n > 0)
    if win:
        first = [d for d in weekdays if d in win]
        phases = [("申報窗口", first), ("補掃窗口外日期", [d for d in weekdays if d not in win])]
    else:
        phases = [("全區間", weekdays)]
    found: dict[str, dict] = {}
    info = {"mode": phases[0][0] if len(phases) == 1 else "申報窗口優先", "scanned_days": 0,
            "phases_used": [], "oldest": None}
    stop_early = not include_amend

    def enough() -> bool:
        n_a = sum(d["docTypeCode"] in ANNUAL for d in found.values())
        n_p = sum(d["docTypeCode"] in PERIODIC for d in found.values())
        return n_a >= annual_n and n_p >= periodic_n

    chunk = 20
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        for label, dates in phases:
            if stop_early and enough():
                break
            if not dates:
                continue
            info["phases_used"].append(f"{label}（{len(dates)} 個平日）")
            print(f"[edinet] {label}：{len(dates)} 個平日待掃", file=sys.stderr)
            for s in range(0, len(dates), chunk):
                batch = dates[s:s + chunk]
                for d, res in zip(batch, ex.map(lambda x: daily_list(x, key), batch)):
                    info["scanned_days"] += 1
                    info["oldest"] = min(info["oldest"] or d, d)
                    for doc in res:
                        if (doc.get("edinetCode") == ecode and doc.get("docTypeCode") in types
                                and doc.get("withdrawalStatus", "0") == "0"
                                and doc.get("disclosureStatus", "0") == "0"):
                            found[doc["docID"]] = doc
                print(f"[edinet]   掃到 {batch[-1].isoformat()}，找到 {len(found)} 份", file=sys.stderr)
                if stop_early and enough():
                    break
    docs = sorted(found.values(), key=lambda d: d.get("submitDateTime") or "", reverse=True)
    return docs, info


# ---------------------------------------------------------------- naming
def _parse(d: str | None) -> date | None:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date() if d else None
    except ValueError:
        return None


def _fye_month(company: dict) -> int | None:
    ms = period_months(company)
    return ms[0] if ms else None


def _fy_of(period_end: date, fye_month: int | None) -> int:
    """財報所屬會計年度 = 期末日之後（含）第一個決算月的年份。"""
    if not fye_month:
        return period_end.year
    return period_end.year if period_end.month <= fye_month else period_end.year + 1


def target_name(doc: dict, ticker: str, company: dict) -> str:
    t = doc["docTypeCode"]
    ps, pe = _parse(doc.get("periodStart")), _parse(doc.get("periodEnd"))
    desc = doc.get("docDescription") or ""
    fye = _fye_month(company)
    amend = "_Amend" + doc["docID"] if t in ANNUAL_AMEND | PERIODIC_AMEND else ""
    if pe is None:
        return f"{ticker}_{DOC_NAME.get(t, t)}_{doc['docID']}"
    short_period = ps is not None and (pe - ps).days < 300  # 6 個月決算（J-REIT 等）
    if t in ANNUAL | ANNUAL_AMEND:
        tag = f"{pe.year}{MON[pe.month]}" if short_period else str(pe.year)
        return f"{ticker}_AnnualReport_{tag}{amend}"
    fy = _fy_of(pe, fye)
    if t in HALF | {"170"}:
        return f"{ticker}_Quarter_{fy}H1{amend}"
    m = re.search(r"第\s*([1-4１-４])\s*四半期", desc)
    if m:
        q = int(m.group(1).translate(str.maketrans("１２３４", "1234")))
    elif fye:
        months_into = (pe.month - fye) % 12 or 12
        q = max(1, min(3, months_into // 3))
    else:
        q = 0
    return f"{ticker}_Quarter_{fy}Q{q}{amend}"


def _aliases(base: str) -> list[str]:
    """同一期別在 repo 裡可能出現的舊檔名（collectStk §7.1）。"""
    out = [base]
    m = re.match(r"^(.+?)_(AnnualReport|Quarter)_(\w+?)(_Amend\w+)?$", base)
    if not m or m.group(4):
        return out
    t, kind, per = m.group(1), m.group(2), m.group(3)
    if kind == "AnnualReport":
        out += [f"{t}_annual_{per}"]
    else:
        out += [f"{t}_quarter_{per}", f"{t}_QuarterlyReport_{per}"]
        if per.endswith("H1"):
            fy = per[:-2]
            out += [f"{t}_Quarter_{fy}Q2", f"{t}_quarter_{fy}Q2", f"{t}_interim_{fy}", f"{t}_QuarterlyReport_{fy}Q2"]
    return out


# 既有 .md 實際是哪種文件：取檔頭「最早出現」的關鍵字。不能只看有沒有出現——
# 決算短信封面固定有「半期報告書提出予定日」，有報目次也會提到其他報告書（2026-11 實測）。
KIND_PATTERNS = [
    ("120", re.compile(r"有価証券報告書|Annual Securities Report")),
    ("140", re.compile(r"四半期報告書|Quarterly Securities Report")),
    ("160", re.compile(r"(?<!四)半期報告書(?!提出)|Semi-Annual Securities Report")),
    ("tanshin", re.compile(r"決算短信|Summary of (?:Consolidated )?Financial Results|FINANCIAL RESULTS", re.I)),
    ("asset", re.compile(r"資産運用報告|Asset Management Report", re.I)),
    ("other", re.compile(r"Annual Report|Integrated Report|統合報告書|決算説明", re.I)),
]


def doc_kind(path: Path, head_chars: int = 6000) -> str | None:
    """'120'/'140'/'160'/'tanshin'/'asset'/'other'；PDF、讀不到或認不出 → None。"""
    if path.suffix.lower() != ".md":
        return None
    try:
        with path.open(encoding="utf-8", errors="replace") as f:
            head = f.read(head_chars)
    except OSError:
        return None
    best = None
    for kind, pat in KIND_PATTERNS:
        m = pat.search(head)
        if m and (best is None or m.start() < best[1]):
            best = (kind, m.start())
    return best[0] if best else None


def _same_doc(doc_type: str, p: Path) -> bool:
    """既有檔是否就是這種 EDINET 文件。PDF／認不出內容 → 視為是（保守：避免重複下載）。"""
    k = doc_kind(p)
    return k is None or k == {"130": "120", "150": "140", "170": "160"}.get(doc_type, doc_type)


def name_taken_by_other(out: Path, base: str, doc: dict) -> Path | None:
    """目標檔名已被「別種文件」佔用（舊流程把決算短信存成 _Quarter_、資産運用報告存成 _AnnualReport_）。"""
    p = out / f"{base}.md"
    return p if p.is_file() and not _same_doc(doc["docTypeCode"], p) else None


def existing_cover(out: Path, base: str, doc: dict, fmt: str) -> Path | None:
    """資料夾內已涵蓋該期別的檔案（新命名、舊命名、日文原檔名如「有価証券報告書－第39期(20250401－20260331)」）。
    .md 要檔頭內容確實是同一種文件才算（決算短信、資産運用報告不能頂替有報／半期報）。"""
    if not out.is_dir():
        return None
    typ, ext = FORMAT_TYPE[fmt]
    suffix = "" if fmt == "pdf" else f"_{fmt}"
    files = {p.name.lower(): p for p in out.iterdir() if p.is_file()}
    for b in _aliases(base):
        for name in (f"{b}{suffix}.{ext}",) + ((f"{b}.md",) if fmt == "pdf" else ()):
            hit = files.get(name.lower())
            if hit and (fmt != "pdf" or _same_doc(doc["docTypeCode"], hit)):
                return hit
    if fmt != "pdf" or "_Amend" in base:
        return None
    pe = _parse(doc.get("periodEnd"))
    kw = {"120": "有価証券報告書", "160": "半期報告書", "140": "四半期報告書"}.get(doc["docTypeCode"])
    if not pe or not kw:
        return None
    pe8 = pe.strftime("%Y%m%d")
    for p in files.values():
        if p.suffix.lower() in (".md", ".pdf") and kw in p.name and "訂正" not in p.name \
                and not (kw == "半期報告書" and "四半期報告書" in p.name) \
                and pe8 in re.sub(r"\D", "", p.name) and _same_doc(doc["docTypeCode"], p):
            return p
    return None


# ---------------------------------------------------------------- folders / download
def find_company_folder(ticker: str) -> list[Path]:
    """repo 根目錄下「代碼開頭、下一字不是數字」的資料夾（3445 → 3445RS；不會誤配 34450xx）。"""
    return [p for p in REPO_ROOT.iterdir() if p.is_dir() and p.name.startswith(ticker)
            and not p.name[len(ticker):len(ticker) + 1].isdigit()]


def resolve_out(a, ticker: str, company: dict) -> tuple[Path, bool]:
    if a.out:
        return Path(a.out).expanduser().resolve(), False
    cands = sorted(set(find_company_folder(ticker)))
    if len(cands) == 1:
        return cands[0], False
    if len(cands) > 1:
        raise EdinetError("AMBIGUOUS", "repo 內有多個以「%s」開頭的資料夾：%s → 用 --out 指定"
                          % (ticker, ", ".join(p.name for p in cands)))
    if a.no_create:
        raise EdinetError("NOT_FOUND", f"repo 內找不到以「{ticker}」開頭的公司資料夾，請用 --out 指定")
    return REPO_ROOT / f"{ticker}{company_short_name(company)}", True


def _valid_payload(data: bytes, ext: str) -> str | None:
    if ext == "pdf":
        if not data.startswith(b"%PDF"):
            return "不是 PDF（檔頭不是 %PDF）"
        if len(data) < MIN_PDF_BYTES:
            return f"PDF 太小（{len(data)} bytes < 10KB）"
    elif not zipfile.is_zipfile(io.BytesIO(data)):
        return "不是合法 ZIP"
    return None


def download_doc(doc: dict, fmt: str, out: Path, base: str, key: str, force: bool) -> dict:
    typ, ext = FORMAT_TYPE[fmt]
    suffix = "" if fmt == "pdf" else f"_{fmt}"
    other = name_taken_by_other(out, base, doc) if fmt == "pdf" else None
    if other is not None:  # 同名檔其實是決算短信／資産運用報告 → 另存，不覆蓋
        base = base + "_EDINET"
    dest = out / f"{base}{suffix}.{ext}"
    r = {"format": fmt, "file": dest.name, "status": "", "note": ""}
    if other is not None:
        r["note"] = f"{other.name} 是別種文件，改存 {dest.name}；"
    if not force and (hit := existing_cover(out, base, doc, fmt)):
        r.update(status="skipped", note=f"已存在 {hit.name}", cover=hit.name)
        return r
    flag = FORMAT_FLAG[fmt]
    if str(doc.get(flag)) != "1":
        r.update(status="unavailable", note=f"EDINET 無此格式（{flag}=0）")
        return r
    data, ctype, _ = api_call(f"documents/{doc['docID']}", {"type": typ}, key)
    if (bad := _valid_payload(data, ext)) is not None:
        r.update(status="failed", note=f"{bad}；content-type={ctype}")
        return r
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=out, delete=False, suffix=".part") as tf:
        tf.write(data)
    umask = os.umask(0)
    os.umask(umask)
    os.chmod(tf.name, 0o666 & ~umask)  # NamedTemporaryFile 預設 0600 → 改回一般檔案權限
    Path(tf.name).replace(dest)
    r.update(status="downloaded", note=r["note"] + f"{len(data) / 1024:.0f} KB", cover=dest.name)
    return r


def select(docs: list[dict], annual_n: int, periodic_n: int, include_amend: bool) -> list[dict]:
    ann = [d for d in docs if d["docTypeCode"] in ANNUAL][:annual_n]
    per = [d for d in docs if d["docTypeCode"] in PERIODIC][:periodic_n]
    sel = ann + per
    if include_amend:
        sel += [d for d in docs if d["docTypeCode"] in ANNUAL_AMEND | PERIODIC_AMEND]
    return sel


def _row(d: dict, ticker: str, company: dict) -> str:
    return (f"{(d.get('submitDateTime') or '')[:10]}  {d['docID']}  {d['docTypeCode']} "
            f"{DOC_NAME.get(d['docTypeCode'], ''):<8} 期間 {d.get('periodStart')}~{d.get('periodEnd')}  "
            f"→ {target_name(d, ticker, company)}  | {d.get('docDescription')}")


# ---------------------------------------------------------------- logs
ERROR_HEADER = """# EDINET 錯誤報告

> 由 `.claude/skills/edinet/scripts/edinet.py` 自動寫入，最新在最上面（最多保留 50 筆）。
> **API key 永遠不會寫進這裡**（只記錄來源與格式檢查）。
> 種類：`AUTH_INVALID_KEY` / `AUTH_FORBIDDEN`（key 錯誤，優先處理）、`RATE_LIMIT`、`NETWORK`、`API_ERROR`、`NOT_FOUND`、`AMBIGUOUS`、`SCRIPT_BUG`（腳本本身有錯 → AI 依 SKILL.md §9 自我修正）、`SELFTEST_FAIL`。

<!-- entries -->
"""

FIX_AUTH = [
    "本機：設環境變數 `EDINET_API_KEY`（Windows `setx EDINET_API_KEY \"你的key\"` 後重開終端機／Claude；"
    "macOS/Linux 寫進 `~/.bashrc`），或把 `.claude/skills/edinet/.env.example` 複製成 `.env` 填 `EDINET_API_KEY=...`。",
    "雲端 Claude Code：claude.ai → 雲端環境設定 → Network secrets → 檢查 host `api.edinet-fsa.go.jp`、"
    "header `Ocp-Apim-Subscription-Key` 那筆；或請 Claude 呼叫 `request_credential` 重新存 key。",
    "key 失效或遺失：EDINET 首頁 →「API」→ API キー発行，重新登入取得（重新發行後舊 key 立即失效）。",
    "修好後執行 `python .claude/skills/edinet/scripts/edinet.py checkkey` 確認。",
    "在修好之前：改走 AGENTS.md §4.2 D/F 替代來源（IR Bank `irbank.net/{代碼}/ir`、Ullet、Futu `{代碼}-JP/announcement`）。",
]


def _auth_causes(src: str, k: str | None) -> list[str]:
    if not k:
        return ["本機沒有設定 key（環境變數與 .env 都沒有），腳本送出佔位值，但：",
                "（a）目前不在 Claude Code 雲端環境（沒有代理幫忙注入 key），或",
                "（b）雲端環境的 Network secret（`api.edinet-fsa.go.jp`）沒設、已刪除、key 已失效，或 header 名稱不是 `Ocp-Apim-Subscription-Key`，或",
                "（c）【最常見】這是排程任務（scheduled task）開的 session，它跑在另一個雲端環境，"
                "而 EDINET key 只存在 `FinancialReport` 環境 → 把排程任務的環境改成 `FinancialReport`，"
                "或在該環境的 Network secrets 也加 `api.edinet-fsa.go.jp` 這筆。"]
    return ["本機 key 被 EDINET 拒絕（來源與格式見上一行；格式異常就先修格式）。",
            "可能：key 打錯／貼到多餘空白或引號、key 已被重新發行（舊 key 失效）、EDINET 帳號被停用，"
            "或環境變數殘留舊值（`setx` 後未重開終端機）。"]


def log_error(e: EdinetError | None, argv: list[str], *, kind: str | None = None,
              detail: str = "", tb: str | None = None) -> Path:
    kind = kind or (e.kind if e else "SCRIPT_BUG")
    k, src = get_key()
    L = [f"## {datetime.now():%Y-%m-%d %H:%M:%S} — {kind}", ""]
    L.append(f"- 指令：`edinet.py {' '.join(argv)}`（script v{VERSION}，Python {sys.version.split()[0]}，{sys.platform}）")
    if e is not None:
        L.append(f"- 錯誤：{e}")
        if e.endpoint:
            L.append(f"- 端點：`{e.endpoint}`")
        if e.status is not None:
            L.append(f"- 狀態碼：{e.status}")
        if e.api_msg:
            L.append(f"- API 回應：`{str(e.api_msg).strip()[:300]}`")
    if detail:
        L.append(f"- 說明：{detail}")
    L.append(f"- key 來源：{src or '無（佔位值 → 雲端代理注入）'}；{key_format_note(k)}")
    if kind in AUTH_KINDS:
        L.append("- 可能原因：")
        L += [f"  - {c}" for c in _auth_causes(src, k)]
        L.append("- 修正步驟：")
        L += [f"  {i}. {s}" for i, s in enumerate(FIX_AUTH, 1)]
    elif kind == "RATE_LIMIT":
        L.append("- 處理：EDINET 限流。稍等 5–10 分鐘再跑（已下載的每日清單有快取，不會重抓）；"
                 "或調低 `--workers`、設 `EDINET_MIN_INTERVAL=0.5`。")
    elif kind == "NETWORK":
        L.append("- 處理：檢查網路／代理；雲端若被代理擋（403 from proxy）見 `/root/.ccr/README.md`。")
    elif kind in ("SCRIPT_BUG", "SELFTEST_FAIL"):
        L.append("- 處理：**AI 必須依 SKILL.md §9 自我修正**：修 `scripts/edinet.py` / `SKILL.md` → "
                 "`edinet.py selftest` 全過 → 同步 `.agents/skills/edinet/` → 在 §10 變更紀錄記一筆 → commit & push。")
    if tb:
        L += ["", "```text", tb.strip()[-3000:], "```"]
    entry = "\n".join(L) + "\n"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    old = ERROR_LOG.read_text(encoding="utf-8") if ERROR_LOG.is_file() else ERROR_HEADER
    if "<!-- entries -->" not in old:
        old = ERROR_HEADER + old
    head, _, rest = old.partition("<!-- entries -->\n")
    entries = re.split(r"(?m)^(?=## \d{4}-\d{2}-\d{2} )", rest)
    entries = [x for x in entries if x.strip()][:49]
    ERROR_LOG.write_text(head + "<!-- entries -->\n" + entry + "\n" + "\n".join(x.rstrip() + "\n" for x in entries),
                         encoding="utf-8")
    return ERROR_LOG


def write_summary(lines: list[str]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    p = LOG_DIR / f"edinet_Summary_{date.today():%Y%m%d}.md"
    head = "" if p.is_file() else f"# EDINET 執行報告 {date.today():%Y-%m-%d}\n\n"
    with p.open("a", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n\n")
    return p


# ---------------------------------------------------------------- verify（Convert2md 之後）
CID_RE = re.compile(r"\(cid:\d+\)")


def verify_md(md: Path, company: dict, ticker: str) -> tuple[bool, str]:
    if not md.is_file():
        return False, "尚未轉成 .md（PDF 還在 → Convert2md 未跑或失敗）"
    size = md.stat().st_size
    if size < MIN_PDF_BYTES:
        return False, f".md 太小（{size} bytes）"
    text = md.read_text(encoding="utf-8", errors="replace")
    cid = len(CID_RE.findall(text))
    if cid >= 50:
        return False, f"CID 亂碼 {cid} 次"
    head = _norm(text[:20000])
    names = [_norm(company_short_name(company)), _norm(company.get("提出者名（英字）", "")).split(",")[0],
             company.get("ＥＤＩＮＥＴコード", "").lower(), ticker.lower()]
    if not any(n and len(n) >= 2 and n in head for n in names):
        return False, "前 2 萬字找不到公司名／EDINET コード／證券代碼 → 檔案可能抓錯"
    return True, f"OK（{size / 1024:.0f} KB，CID {cid}）"


# ---------------------------------------------------------------- selftest
def _cmd_selftest(a, parser: argparse.ArgumentParser) -> int:
    fails: list[str] = []

    def check(name: str, cond: bool, info: str = "") -> None:
        print(f"  {'PASS' if cond else 'FAIL'}  {name}{('  — ' + info) if info and not cond else ''}")
        if not cond:
            fails.append(f"{name}：{info}")

    print("[selftest] 命名與期別邏輯")
    dec = {"決算日": "12月末日", "上場区分": "上場", "提出者名": "テスト株式会社"}
    mar = {"決算日": "3月31日", "上場区分": "上場", "提出者名": "テスト株式会社"}
    reit = {"決算日": "1月末日/7月末日", "上場区分": "上場(投資法人)", "提出者名": "テスト投資法人"}
    cases = [
        ({"docID": "S1", "docTypeCode": "120", "periodStart": "2025-01-01", "periodEnd": "2025-12-31"}, "3445", dec, "3445_AnnualReport_2025"),
        ({"docID": "S2", "docTypeCode": "160", "periodStart": "2026-01-01", "periodEnd": "2026-06-30"}, "3445", dec, "3445_Quarter_2026H1"),
        ({"docID": "S3", "docTypeCode": "160", "periodStart": "2026-04-01", "periodEnd": "2026-09-30"}, "7203", mar, "7203_Quarter_2027H1"),
        # EDINET 實際回傳：半期報告書的 period 是「整個會計年度」（2026-11 實測 S100ZCG0）
        ({"docID": "S3b", "docTypeCode": "160", "periodStart": "2026-04-01", "periodEnd": "2027-03-31"}, "7203", mar, "7203_Quarter_2027H1"),
        ({"docID": "S3c", "docTypeCode": "160", "periodStart": "2026-01-01", "periodEnd": "2026-12-31"}, "3445", dec, "3445_Quarter_2026H1"),
        ({"docID": "S4", "docTypeCode": "140", "periodStart": "2023-10-01", "periodEnd": "2023-12-31",
          "docDescription": "四半期報告書－第120期第3四半期"}, "7203", mar, "7203_Quarter_2024Q3"),
        ({"docID": "S5", "docTypeCode": "140", "periodStart": "2023-04-01", "periodEnd": "2023-06-30"}, "7203", mar, "7203_Quarter_2024Q1"),
        ({"docID": "S6", "docTypeCode": "120", "periodStart": "2026-02-01", "periodEnd": "2026-07-31"}, "2971", reit, "2971_AnnualReport_2026Jul"),
        ({"docID": "S7", "docTypeCode": "130", "periodStart": "2025-04-01", "periodEnd": "2026-03-31"}, "7203", mar, "7203_AnnualReport_2026_AmendS7"),
    ]
    for doc, t, comp, want in cases:
        got = target_name(doc, t, comp)
        check(f"target_name {want}", got == want, f"得到 {got}")

    print("[selftest] 申報窗口")
    w = filing_windows(dec, date(2026, 11, 26), 800, True) or set()
    check("12 月決算：有報 2026-03-27 在窗口內", date(2026, 3, 27) in w)
    check("12 月決算：半期報 2026-08-10 在窗口內", date(2026, 8, 10) in w)
    check("12 月決算：2026-06-15 不在窗口內", date(2026, 6, 15) not in w)
    w = filing_windows(mar, date(2026, 11, 26), 1200, True) or set()
    check("3 月決算：四半期報 2024-02-13 在窗口內（廢止前）", date(2024, 2, 13) in w)
    check("3 月決算：2025-02-13 不在窗口內（四半期報已廢止）", date(2025, 2, 13) not in w)
    w = filing_windows(reit, date(2026, 11, 26), 800, False) or set()
    check("J-REIT：有報 2026-10-28 在窗口內", date(2026, 10, 28) in w)

    print("[selftest] 既有檔判定（舊命名 / 日文原檔名）")
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        for n, body in (("9435_Quarter_2027Q2.md", "EDINET提出書類 株式会社光通信 半期報告書"),
                        ("202606有価証券報告書－第39期(20250401－20260331).md", "【提出書類】 有価証券報告書"),
                        ("3445_annual_2024.md", "x"),
                        # 舊流程：決算短信存成 _Quarter_Q2、資産運用報告存成 _AnnualReport_（2026-11 實際 repo 狀況）
                        ("4979_Quarter_2026Q2.md", "2026年12月期 第２四半期（中間期）決算短信〔日本基準〕（連結）\n半期報告書提出予定日 2026年8月10日"),
                        ("2971_AnnualReport_2026Jul.md", "# 2971 第19期 資産運用報告\n有価証券報告書")):
            (tdp / n).write_text(body, encoding="utf-8")
        toy = tdp / "7203Toyota"  # 期末日與上面 9435 相同 → 放獨立資料夾（實際上每家公司各一個資料夾）
        toy.mkdir()
        (toy / "7203_AnnualReport_2026.md").write_text("# FY2026 FINANCIAL RESULTS", encoding="utf-8")
        d_h1 = {"docID": "A", "docTypeCode": "160", "periodEnd": "2026-09-30"}
        d_an = {"docID": "B", "docTypeCode": "120", "periodEnd": "2026-03-31"}
        d_old = {"docID": "C", "docTypeCode": "120", "periodEnd": "2024-12-31"}
        d_new = {"docID": "D", "docTypeCode": "120", "periodEnd": "2025-03-31"}
        check("H1 認得舊名 Q2", existing_cover(tdp, "9435_Quarter_2027H1", d_h1, "pdf") is not None)
        check("認得日文有報原檔名", existing_cover(tdp, "9435_AnnualReport_2026", d_an, "pdf") is not None)
        check("認得 {ticker}_annual_{FY}", existing_cover(tdp, "3445_AnnualReport_2024", d_old, "pdf") is not None)
        check("不同期別不誤判", existing_cover(tdp, "9435_AnnualReport_2025", d_new, "pdf") is None)
        d_h1b = {"docID": "E", "docTypeCode": "160", "periodEnd": "2026-12-31"}
        d_reit = {"docID": "F", "docTypeCode": "120", "periodEnd": "2026-07-31"}
        d_toy = {"docID": "G", "docTypeCode": "120", "periodEnd": "2026-03-31"}
        check("決算短信 Q2 不可頂替半期報告書", existing_cover(tdp, "4979_Quarter_2026H1", d_h1b, "pdf") is None)
        check("資産運用報告不可頂替有報", existing_cover(tdp, "2971_AnnualReport_2026Jul", d_reit, "pdf") is None)
        check("同名資産運用報告 → 改存 _EDINET", name_taken_by_other(tdp, "2971_AnnualReport_2026Jul", d_reit) is not None)
        check("英文決算資料不可頂替有報", existing_cover(toy, "7203_AnnualReport_2026", d_toy, "pdf") is None)
        check("真的半期報告書 Q2 仍算已有", name_taken_by_other(tdp, "9435_Quarter_2027Q2", d_h1) is None)

    print("[selftest] SKILL.md 與 CLI 參數一致")
    skill_md = SKILL_DIR / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else ""
    check("SKILL.md 存在", bool(text), str(skill_md))
    subs = {}
    for act in parser._actions:  # noqa: SLF001
        if isinstance(act, argparse._SubParsersAction):  # noqa: SLF001
            subs = act.choices
    opts = {o for sp in subs.values() for act in sp._actions for o in act.option_strings}  # noqa: SLF001
    for sc in sorted(set(re.findall(r"edinet\.py\s+([a-z]+)", text))):
        check(f"SKILL.md 提到的子指令 `{sc}` 存在", sc in subs, f"CLI 沒有 {sc}")
    for op in sorted(set(re.findall(r"(?<![\w-])(--[a-z][a-z-]+)", text))):
        check(f"SKILL.md 提到的參數 `{op}` 存在", op in opts, f"CLI 沒有 {op}")
    for sc in subs:
        check(f"子指令 `{sc}` 有寫進 SKILL.md", f"edinet.py {sc}" in text, "SKILL.md 漏寫")

    print("[selftest] .claude / .agents 鏡像同步、.gitignore")
    for rel in ("SKILL.md", "scripts/edinet.py", ".env.example"):
        a1, a2 = REPO_ROOT / ".claude/skills/edinet" / rel, REPO_ROOT / ".agents/skills/edinet" / rel
        same = a1.is_file() and a2.is_file() and a1.read_bytes() == a2.read_bytes()
        check(f"鏡像一致 {rel}", same, f"{a1} 與 {a2} 不同或缺檔 → 複製 .claude 版到 .agents")
    gi = REPO_ROOT / ".gitignore"
    check(".gitignore 排除 .env", gi.is_file() and re.search(r"(?m)^\.env\s*$", gi.read_text(encoding="utf-8")) is not None)

    if not a.offline:
        print("[selftest] 線上：API key、コードリスト")
        try:
            k, src = get_key()
            api_json("documents.json", {"date": (date.today() - timedelta(days=1)).isoformat(), "type": 1},
                     k or PROXY_PLACEHOLDER)
            check("API key 有效", True)
        except EdinetError as e:
            p = log_error(e, sys.argv[1:])
            check("API key 有效", False, f"{e.kind} → 已寫 {p}")
        try:
            hit = lookup("3445", load_codelist())
            check("コードリスト：3445 → E31042", bool(hit) and hit[0]["ＥＤＩＮＥＴコード"] == "E31042",
                  str(hit[:1]))
        except EdinetError as e:
            check("コードリスト下載", False, str(e))

    print(f"[selftest] {'全部通過' if not fails else f'{len(fails)} 項失敗'}")
    if fails:
        p = log_error(None, sys.argv[1:], kind="SELFTEST_FAIL", detail="；".join(fails[:20]))
        print(f"[selftest] 失敗明細已寫入 {p}", file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------- CLI
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=f"EDINET API v2 年報/季報下載器 v{VERSION}")
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lookup", help="找公司")
    s.add_argument("query")
    sub.add_parser("checkkey", help="檢查 API key")
    s = sub.add_parser("selftest", help="自我檢查")
    s.add_argument("--offline", action="store_true", help="不連網（只跑邏輯、文件、鏡像檢查）")
    s = sub.add_parser("verify", help="Convert2md 後驗證 .md")
    s.add_argument("--code", help="只驗證這家公司（預設：上次 download 的公司）")
    for name in ("list", "download"):
        s = sub.add_parser(name)
        s.add_argument("--code", required=True, help="證券代碼(4碼) / EDINET コード(E开头) / 公司名")
        s.add_argument("--days", type=int, default=800, help="最多往回掃幾天（預設 800）")
        s.add_argument("--annual", type=int, help="年報份數（預設 2；J-REIT 3）")
        s.add_argument("--periodic", type=int, help="季報/半期報份數（預設 1；J-REIT 0）")
        s.add_argument("--include-amendments", action="store_true", help="一併納入訂正報告書（會全區間掃描）")
        s.add_argument("--full-scan", action="store_true", help="不用申報窗口，逐日全掃")
        s.add_argument("--workers", type=int, default=4)
        if name == "download":
            s.add_argument("--format", default="pdf",
                           help="pdf / xbrl / csv / english / attach，可逗號分隔（預設 pdf）")
            s.add_argument("--out", help="輸出資料夾（預設：repo 內以證券代碼開頭的公司資料夾）")
            s.add_argument("--no-create", action="store_true", help="找不到公司資料夾時報錯，不自動新建")
            s.add_argument("--ticker", help="檔名用的代碼（預設：證券代碼前 4 碼）")
            s.add_argument("--force", action="store_true", help="已存在也重新下載")
    return ap


def _cmd_checkkey() -> int:
    k, src = get_key()
    api_json("documents.json", {"date": (date.today() - timedelta(days=1)).isoformat(), "type": 1},
             k or PROXY_PLACEHOLDER)
    print(f"[edinet] API key 有效（來源：{src or '雲端網路密鑰（代理注入）'}；{key_format_note(k)}；key 不顯示）")
    return 0


def _cmd_list_download(a) -> int:
    key = require_key()
    company = resolve_company(a.code)
    fund = is_fund(company)
    annual_n = a.annual if a.annual is not None else (3 if fund else 2)
    periodic_n = a.periodic if a.periodic is not None else (0 if fund else 1)
    ecode = company["ＥＤＩＮＥＴコード"]
    ticker = getattr(a, "ticker", None) or (company.get("証券コード") or ecode)[:4]
    print(f"[edinet] 公司：{_fmt_company(company)}", file=sys.stderr)
    print(f"[edinet] 目標：年報 {annual_n} 份、季/半期報 {periodic_n} 份" + ("（J-REIT 預設）" if fund else ""),
          file=sys.stderr)
    t0 = time.time()
    docs, info = scan(company, key, a.days, annual_n, periodic_n, a.include_amendments, a.workers, a.full_scan)
    elapsed = time.time() - t0
    scan_line = (f"{info['mode']}；掃 {info['scanned_days']} 個平日（最舊 {info['oldest']}）；"
                 f"API 請求 {STATS['requests']} 次、429 重試 {STATS['retry_429']} 次；{elapsed:.0f} 秒")
    print(f"[edinet] 掃描：{scan_line}", file=sys.stderr)

    if a.cmd == "list":
        print("\n".join(_row(d, ticker, company) for d in docs) or "此區間 EDINET 無年報/季報")
        return 0

    sel = select(docs, annual_n, periodic_n, a.include_amendments)
    out, created = resolve_out(a, ticker, company)
    if created:
        print(f"[edinet] 新公司 → 自動建立資料夾 {out.name}（可事後改名，但要保留代碼開頭）")
    n_a = sum(d["docTypeCode"] in ANNUAL for d in sel)
    n_p = sum(d["docTypeCode"] in PERIODIC for d in sel)
    print(f"[edinet] 選定 {n_a}/{annual_n} 份年報、{n_p}/{periodic_n} 份季/半期報 → {out}")
    results, downloaded = [], []
    for d in sel:
        base = target_name(d, ticker, company)
        print("  " + _row(d, ticker, company))
        for fmt in [f.strip() for f in a.format.split(",") if f.strip()]:
            if fmt not in FORMAT_TYPE:
                raise EdinetError("API_ERROR", f"未知格式 {fmt}（可用：{', '.join(FORMAT_TYPE)}）")
            r = download_doc(d, fmt, out, base, key, a.force)
            r.update(doc=d, base=base)
            results.append(r)
            print(f"    [{r['status']}] {r['file']}  {r['note']}")
            if r["status"] == "downloaded" and fmt == "pdf":
                downloaded.append(str(out / r["file"]))

    gaps = []
    if n_a < annual_n:
        gaps.append(f"年報只找到 {n_a}/{annual_n} 份：{a.days} 天內 EDINET 沒有更多（新上市？可加大 --days）")
    if n_p < periodic_n:
        gaps.append(f"季/半期報只找到 {n_p}/{periodic_n} 份")
    latest_ann = next((d for d in docs if d["docTypeCode"] in ANNUAL), None)
    if not fund and periodic_n:
        gaps.append("提醒：2024/4 起四半期報告書廢止，第 1／第 3 季只有 TDnet 決算短信（不在 EDINET）→ "
                    "最新單季請另抓 株探／IR Bank／公司 IR（collectStk §7.3）")
    if any(r["status"] == "failed" for r in results):
        gaps.append("有檔案下載驗證失敗（見上方 failed），已丟棄未寫入")

    rel = out.relative_to(REPO_ROOT) if out.is_relative_to(REPO_ROOT) else out
    L = [f"## {datetime.now():%H:%M:%S} — {ticker} {company.get('提出者名')}（{ecode}）", "",
         f"- 指令：`edinet.py {' '.join(sys.argv[1:])}`",
         f"- 掃描：{scan_line}",
         f"- 輸出資料夾：`{rel}`" + ("（本次新建）" if created else ""),
         f"- 年報 {n_a}/{annual_n} 份；季/半期報 {n_p}/{periodic_n} 份",
         "- 文件："]
    for r in results:
        d = r["doc"]
        L.append(f"  - {(d.get('submitDateTime') or '')[:10]} `{d['docID']}` {DOC_NAME.get(d['docTypeCode'])} "
                 f"{d.get('periodStart')}~{d.get('periodEnd')} → `{r['file']}`：{r['status']}（{r['note']}）")
    if not results:
        L.append("  - （無）")
    if latest_ann:
        L.append(f"- 最新有報提出日：{(latest_ann.get('submitDateTime') or '')[:10]}")
    if gaps:
        L.append("- 缺口與原因：")
        L += [f"  - {g}" for g in gaps]
    L.append(f"- 下一步：Convert2md（`<SCOPE>` = `{out}`）→ `edinet.py verify --code {ticker}`" if downloaded
             else "- 下一步：無新 PDF，免轉檔")
    sp = write_summary(L)

    CACHE.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({"code": ticker, "ecode": ecode, "folder": str(out),
                                    "items": [{"base": r["base"], "status": r["status"], "cover": r.get("cover")}
                                              for r in results if r["format"] == "pdf"
                                              and r["status"] in ("downloaded", "skipped")],
                                    "downloaded": downloaded, "time": datetime.now().isoformat()},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    for g in gaps:
        print(f"[edinet] ⚠ {g}")
    print(f"[edinet] 執行報告：{sp}")
    if downloaded:
        print("[edinet] NEXT → 跑 Convert2md skill，<SCOPE> 用下面這個資料夾，轉完再 `edinet.py verify`：")
        print(f"CONVERT2MD_SCOPE={out}")
    return 0


def _cmd_verify(a) -> int:
    if not MANIFEST.is_file():
        raise EdinetError("NOT_FOUND", f"找不到上次 download 的紀錄 {MANIFEST}，請先跑 download")
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if a.code and a.code[:4] != m["code"][:4]:
        raise EdinetError("NOT_FOUND", f"上次 download 的是 {m['code']}，不是 {a.code}；請先 download --code {a.code}")
    company = resolve_company(m["ecode"])
    out = Path(m["folder"])
    items = m.get("items") or []
    bad, L = 0, [f"## {datetime.now():%H:%M:%S} — verify {m['code']}（{out.name}）", ""]
    for it in items:
        # 本次下載的 → 檢查同名 .md；略過的 → 檢查涵蓋它的既有檔（舊命名／日文檔名）
        md = out / Path(it.get("cover") or f"{it['base']}.pdf").with_suffix(".md").name
        if it["status"] == "skipped" and not md.is_file():
            line = f"- ➖ `{it['base']}`：由既有檔 `{it.get('cover')}` 涵蓋（非 .md，本次不驗證）"
        else:
            ok, note = verify_md(md, company, m["code"])
            bad += not ok
            line = f"- {'✅' if ok else '❌'} `{md.name}`：{note}" + ("（既有檔）" if it["status"] == "skipped" else "")
        L.append(line)
        print(line)
    sp = write_summary(L)
    print(f"[edinet] verify：{len(items) - bad}/{len(items)} 通過 → {sp}")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    a = parser.parse_args(argv)
    raw = argv if argv is not None else sys.argv[1:]
    try:
        if a.cmd == "lookup":
            hits = lookup(a.query, load_codelist())
            print("\n".join(_fmt_company(c) for c in hits[:30]) or "找不到")
            return 0
        if a.cmd == "checkkey":
            return _cmd_checkkey()
        if a.cmd == "selftest":
            return _cmd_selftest(a, parser)
        if a.cmd == "verify":
            return _cmd_verify(a)
        return _cmd_list_download(a)
    except EdinetError as e:
        p = log_error(e, raw)
        print(f"[edinet] ✗ {e.kind}：{e}" + (f"｜{e.api_msg}" if e.api_msg else ""), file=sys.stderr)
        if e.kind in AUTH_KINDS:
            print("[edinet] ✗ API key 錯誤 → 修正步驟見錯誤報告；先改走 IR Bank／Ullet／Futu", file=sys.stderr)
        print(f"[edinet] 錯誤報告已寫入：{p}", file=sys.stderr)
        return 2 if e.kind in AUTH_KINDS else 1
    except KeyboardInterrupt:
        return 130
    except Exception:  # noqa: BLE001 — 腳本 bug：完整 traceback 寫進 log 讓 AI 自我修正
        tb = traceback.format_exc()
        p = log_error(None, raw, kind="SCRIPT_BUG", tb=tb)
        print(tb, file=sys.stderr)
        print(f"[edinet] ✗ SCRIPT_BUG → 已寫入 {p}；AI 請依 SKILL.md §9 自我修正", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
