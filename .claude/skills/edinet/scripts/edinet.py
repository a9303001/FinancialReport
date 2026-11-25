#!/usr/bin/env python3
"""EDINET API v2 downloader — 日股有価証券報告書（年報）/ 半期報告書 / 四半期報告書（季報）.

只用 Python 標準函式庫（Windows / Linux / macOS 皆可）。

子指令:
  lookup   <查詢>                       用證券代碼 / EDINET コード / 公司名找公司
  list     --code 3445 [--days 800]     列出該公司在 EDINET 的年報/季報（不下載）
  download --code 3445 [--annual 2 --periodic 1] [--format pdf] [--out DIR]
  checkkey                              檢查 API key 是否設定且有效（不印出 key）

API key 讀取順序（找到即停，key 永遠不會被印出）:
  1. 環境變數 EDINET_API_KEY
  2. 環境變數 EDINET_API_KEY_FILE 指向的檔案
  3. <本 skill 資料夾>/.env            （已列入 .gitignore，內容一行 EDINET_API_KEY=xxxx）
  4. ~/.config/edinet/.env             （同上格式，放在使用者家目錄，跨 repo 共用）
  5. 都沒有 → 送佔位值，由 Claude Code 雲端環境的「網路密鑰」代理注入真 key
key 一律用 HTTP header `Ocp-Apim-Subscription-Key` 傳送（不放網址）。
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path

API = "https://api.edinet-fsa.go.jp/api/v2"
CODELIST_URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip"
FUNDLIST_URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Fundcode.zip"
UA = "Mozilla/5.0 (compatible; edinet-skill/1.0)"

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parent.parent.parent  # .claude/skills/edinet -> repo
CACHE = Path(os.environ.get("EDINET_CACHE_DIR") or (Path.home() / ".cache" / "edinet"))

# docTypeCode
ANNUAL = {"120"}                 # 有価証券報告書
ANNUAL_AMEND = {"130"}           # 訂正有価証券報告書
QUARTERLY = {"140"}              # 四半期報告書（2024/4 起廢止，只剩舊資料）
HALF = {"160"}                   # 半期報告書
PERIODIC_AMEND = {"150", "170"}  # 訂正四半期 / 訂正半期
DOC_NAME = {"120": "有価証券報告書", "130": "訂正有価証券報告書", "140": "四半期報告書",
            "150": "訂正四半期報告書", "160": "半期報告書", "170": "訂正半期報告書"}
FORMAT_TYPE = {"xbrl": (1, "zip"), "pdf": (2, "pdf"), "attach": (3, "zip"),
               "english": (4, "zip"), "csv": (5, "zip")}
MON = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---------------------------------------------------------------- API key
def _read_env_file(p: Path) -> str | None:
    try:
        for line in p.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                if line and not line.startswith("#") and "=" not in line:
                    return line  # 檔案只放 key 本身也接受
                continue
            k, v = line.split("=", 1)
            if k.strip() == "EDINET_API_KEY":
                return v.strip().strip('"').strip("'")
    except OSError:
        return None
    return None


def get_key() -> tuple[str | None, str]:
    k = os.environ.get("EDINET_API_KEY", "").strip()
    if k:
        return k, "環境變數 EDINET_API_KEY"
    f = os.environ.get("EDINET_API_KEY_FILE")
    if f and (k := _read_env_file(Path(f).expanduser())):
        return k, f"EDINET_API_KEY_FILE ({f})"
    for p in (SKILL_DIR / ".env", Path.home() / ".config" / "edinet" / ".env"):
        if p.is_file() and (k := _read_env_file(p)):
            return k, str(p)
    return None, ""


PROXY_PLACEHOLDER = "proxy-injected-edinet-key"  # 雲端：由網路代理把 header 換成真 key


def require_key() -> str:
    k, _ = get_key()
    # 本機找不到 key 時送佔位值：Claude Code 雲端環境若已存「網路密鑰」，代理會把 header 換成真 key
    return k or PROXY_PLACEHOLDER


NO_KEY_HELP = ("找不到有效 API key。本機：設環境變數 EDINET_API_KEY 或建立 "
               f"{SKILL_DIR / '.env'}；雲端：在環境的網路密鑰存 api.edinet-fsa.go.jp 的 "
               "Ocp-Apim-Subscription-Key。詳見 SKILL.md §2。")


# ---------------------------------------------------------------- HTTP
def http_get(url: str, params: dict | None = None, key: str | None = None,
             retries: int = 4) -> tuple[bytes, str]:
    q = dict(params or {})
    full = url + ("?" + urllib.parse.urlencode(q) if q else "")
    headers = {"User-Agent": UA}
    if key:  # 用 header 傳 key（不會出現在網址／log），EDINET 實測接受
        headers["Ocp-Apim-Subscription-Key"] = key
    err = None
    for i in range(retries):
        try:
            req = urllib.request.Request(full, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read(), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            body = e.read()[:300].decode("utf-8", "replace")
            if e.code in (401, 403):
                sys.exit(f"[edinet] HTTP {e.code}：{NO_KEY_HELP} 回應：{body}")
            if e.code == 404:
                raise
            err = f"HTTP {e.code} {body}"
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            err = str(e)
        time.sleep(2 ** i)
    raise RuntimeError(f"[edinet] 連線失敗（已重試 {retries} 次）：{err}")


def api_json(path: str, params: dict, key: str) -> dict:
    data, _ = http_get(f"{API}/{path}", params, key)
    j = json.loads(data.decode("utf-8"))
    meta = j.get("metadata", {})
    status = str(j.get("StatusCode") or meta.get("status") or "200")
    if status == "401":
        sys.exit(f"[edinet] {NO_KEY_HELP} 回應：{j.get('message') or meta.get('message')}")
    if status != "200":
        raise RuntimeError(f"[edinet] API 回應異常 {status}: {meta.get('message') or j}")
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
                sys.exit(f"[edinet] 無法下載 {fname}：{e}")
            print(f"[edinet] {fname} 更新失敗，沿用快取：{e}", file=sys.stderr)
    text = csv_path.read_bytes().decode("cp932", "replace")
    rows = list(csv.reader(io.StringIO(text)))
    header = rows[1]
    return [dict(zip(header, r)) for r in rows[2:] if len(r) == len(header)]


def load_codelist() -> list[dict]:
    """EDINET コードリスト + ファンドコードリスト（J-REIT 投資法人的證券代碼與決算期在後者）。"""
    codes = _load_csv(CODELIST_URL, "EdinetcodeDlInfo.csv")
    try:
        funds = _load_csv(FUNDLIST_URL, "FundcodeDlInfo.csv")
    except SystemExit:
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
    import unicodedata
    return unicodedata.normalize("NFKC", s or "").lower().replace(" ", "")


def lookup(query: str, codes: list[dict]) -> list[dict]:
    q = _norm(query)
    out = []
    for c in codes:
        sec = c.get("証券コード", "")
        if q.upper() == c.get("ＥＤＩＮＥＴコード", "").upper() or (
                sec and (q == sec.lower() or (len(q) == 4 and sec.lower() == q + "0"))):
            return [c]
        if len(q) >= 2 and (q in _norm(c.get("提出者名", "")) or q in _norm(c.get("提出者名（英字）", ""))
                            or q in _norm(c.get("提出者名（ヨミ）", ""))):
            out.append(c)
    out.sort(key=lambda c: (c.get("上場区分") != "上場", c.get("証券コード") == ""))
    return out


def resolve_company(code: str) -> dict:
    hits = lookup(code, load_codelist())
    if not hits:
        sys.exit(f"[edinet] コードリスト找不到「{code}」。先用 lookup 子指令確認。")
    if len(hits) > 1:
        lines = "\n".join(_fmt_company(c) for c in hits[:15])
        sys.exit(f"[edinet] 「{code}」對到多家公司，請改用證券代碼或 EDINET コード：\n{lines}")
    return hits[0]


def _fmt_company(c: dict) -> str:
    sec = c.get("証券コード", "")
    return (f"{c.get('ＥＤＩＮＥＴコード')}  證券代碼={sec[:4] if sec else '-':<5} "
            f"決算日={c.get('決算日', ''):<7} {c.get('上場区分', '')}  {c.get('提出者名')} "
            f"/ {c.get('提出者名（英字）', '')}")


# ---------------------------------------------------------------- daily lists
def daily_list(d: date, key: str) -> list[dict]:
    p = CACHE / "lists" / f"{d.isoformat()}.json"
    stale_limit = date.today() - timedelta(days=7)  # 一週內的清單可能還在變動 → 每次重抓
    if p.is_file() and d < stale_limit:
        return json.loads(p.read_text(encoding="utf-8"))
    j = api_json("documents.json", {"date": d.isoformat(), "type": 2}, key)
    res = j.get("results") or []
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    return res


def _wanted_types(include_amend: bool) -> set[str]:
    t = ANNUAL | QUARTERLY | HALF
    return t | ANNUAL_AMEND | PERIODIC_AMEND if include_amend else t


def scan(edinet_code: str, key: str, days: int, annual_n: int | None, periodic_n: int | None,
         include_amend: bool = False, workers: int = 4) -> list[dict]:
    """由今天往回掃每日提出書類清單；收集夠 annual_n 份年報 + periodic_n 份季/半期報即提早停止。"""
    types = _wanted_types(include_amend)
    today = date.today()
    dates = [today - timedelta(days=i) for i in range(days + 1)]
    found: list[dict] = []
    chunk = 28
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for s in range(0, len(dates), chunk):
            batch = dates[s:s + chunk]
            for d, res in zip(batch, ex.map(lambda x: daily_list(x, key), batch)):
                for doc in res:
                    if (doc.get("edinetCode") == edinet_code and doc.get("docTypeCode") in types
                            and doc.get("withdrawalStatus", "0") == "0"
                            and doc.get("disclosureStatus", "0") == "0"):
                        found.append(doc)
            print(f"[edinet] 已掃到 {batch[-1].isoformat()}，找到 {len(found)} 份", file=sys.stderr)
            n_a = sum(d["docTypeCode"] in ANNUAL for d in found)
            n_p = sum(d["docTypeCode"] in (QUARTERLY | HALF) for d in found)
            if annual_n is not None and periodic_n is not None and n_a >= annual_n and n_p >= periodic_n:
                break
    found.sort(key=lambda d: d.get("submitDateTime") or "", reverse=True)
    return found


# ---------------------------------------------------------------- naming
def _parse(d: str | None) -> date | None:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date() if d else None
    except ValueError:
        return None


def _fye_month(company: dict) -> int | None:
    m = re.match(r"(\d+)月", company.get("決算日", ""))
    return int(m.group(1)) if m else None


def _fy_of(period_end: date, fye_month: int | None) -> int:
    """財報所屬會計年度 = 期末日之後（含）第一個決算月的年份。"""
    if not fye_month:
        return period_end.year
    y = period_end.year if period_end.month <= fye_month else period_end.year + 1
    return y


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


# ---------------------------------------------------------------- download
def find_company_folder(ticker: str) -> Path | None:
    cands = [p for p in REPO_ROOT.iterdir() if p.is_dir() and p.name.startswith(ticker)
             and not p.name[len(ticker):len(ticker) + 1].isdigit()]
    return cands[0] if len(cands) == 1 else None


def download_doc(doc: dict, fmt: str, out: Path, base: str, key: str, force: bool) -> str:
    typ, ext = FORMAT_TYPE[fmt]
    suffix = "" if fmt == "pdf" else f"_{fmt}"
    dest = out / f"{base}{suffix}.{ext}"
    if not force:
        # 半期報 H1 = 舊命名的 Q2；.md 代表已轉檔過 → 都視為已下載
        alts = [base] + ([base[:-2] + "Q2"] if base.endswith("H1") else [])
        hit = [p for b in alts for p in (out / f"{b}{suffix}.{ext}", out / f"{b}.md")
               if p.exists() and (fmt == "pdf" or p.suffix != ".md")]
        if hit:
            return f"略過（已存在）{hit[0].name}"
    flag = {"pdf": "pdfFlag", "xbrl": "xbrlFlag", "csv": "csvFlag", "attach": "attachDocFlag",
            "english": "englishDocFlag"}[fmt]
    if doc.get(flag) not in ("1", 1):
        return f"無此格式（{flag}=0）{dest.name}"
    data, ctype = http_get(f"{API}/documents/{doc['docID']}", {"type": typ}, key)
    if "json" in ctype:  # API 以 JSON 回錯誤
        return f"失敗 {dest.name}: {data[:200].decode('utf-8', 'replace')}"
    out.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return f"已下載 {dest}  ({len(data) / 1024:.0f} KB)"


def select(docs: list[dict], annual_n: int, periodic_n: int, include_amend: bool) -> list[dict]:
    ann = [d for d in docs if d["docTypeCode"] in ANNUAL][:annual_n]
    per = [d for d in docs if d["docTypeCode"] in QUARTERLY | HALF][:periodic_n]
    sel = ann + per
    if include_amend:
        sel += [d for d in docs if d["docTypeCode"] in ANNUAL_AMEND | PERIODIC_AMEND]
    return sel


def _row(d: dict, ticker: str, company: dict) -> str:
    return (f"{(d.get('submitDateTime') or '')[:10]}  {d['docID']}  {d['docTypeCode']} "
            f"{DOC_NAME.get(d['docTypeCode'], ''):<8} 期間 {d.get('periodStart')}~{d.get('periodEnd')}  "
            f"→ {target_name(d, ticker, company)}  | {d.get('docDescription')}")


# ---------------------------------------------------------------- CLI
def main() -> None:
    ap = argparse.ArgumentParser(description="EDINET API v2 年報/季報下載器")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lookup"); s.add_argument("query")
    sub.add_parser("checkkey")
    for name in ("list", "download"):
        s = sub.add_parser(name)
        s.add_argument("--code", required=True, help="證券代碼(4碼) / EDINET コード(E开头) / 公司名")
        s.add_argument("--days", type=int, default=800, help="最多往回掃幾天（預設 800）")
        s.add_argument("--annual", type=int, default=2, help="年報份數（預設 2）")
        s.add_argument("--periodic", type=int, default=1, help="季報/半期報份數（預設 1）")
        s.add_argument("--include-amendments", action="store_true", help="一併納入訂正報告書")
        s.add_argument("--workers", type=int, default=4)
        if name == "download":
            s.add_argument("--format", default="pdf",
                           help="pdf / xbrl / csv / english / attach，可逗號分隔（預設 pdf）")
            s.add_argument("--out", help="輸出資料夾（預設：repo 內以證券代碼開頭的公司資料夾）")
            s.add_argument("--ticker", help="檔名用的代碼（預設：證券代碼前 4 碼）")
            s.add_argument("--force", action="store_true", help="已存在也重新下載")
    a = ap.parse_args()

    if a.cmd == "lookup":
        hits = lookup(a.query, load_codelist())
        print("\n".join(_fmt_company(c) for c in hits[:30]) or "找不到")
        return
    if a.cmd == "checkkey":
        k, src = get_key()
        api_json("documents.json", {"date": (date.today() - timedelta(days=1)).isoformat(), "type": 1},
                 k or PROXY_PLACEHOLDER)
        print(f"[edinet] API key 有效（來源：{src or '雲端網路密鑰（代理注入）'}，key 不顯示）")
        return

    key = require_key()
    company = resolve_company(a.code)
    ecode = company["ＥＤＩＮＥＴコード"]
    ticker = getattr(a, "ticker", None) or (company.get("証券コード") or ecode)[:4]
    print(f"[edinet] 公司：{_fmt_company(company)}", file=sys.stderr)
    docs = scan(ecode, key, a.days, a.annual, a.periodic, a.include_amendments, a.workers)

    if a.cmd == "list":
        print("\n".join(_row(d, ticker, company) for d in docs) or "此區間 EDINET 無年報/季報")
        return

    sel = select(docs, a.annual, a.periodic, a.include_amendments)
    out = Path(a.out) if a.out else find_company_folder(ticker)
    if out is None:
        sys.exit(f"[edinet] repo 內找不到唯一以「{ticker}」開頭的公司資料夾，請用 --out 指定"
                 f"（新公司慣例：{ticker}{company.get('提出者名', '').replace('株式会社', '')}）")
    n_a = sum(d["docTypeCode"] in ANNUAL for d in sel)
    n_p = sum(d["docTypeCode"] in QUARTERLY | HALF for d in sel)
    print(f"[edinet] 選定 {n_a}/{a.annual} 份年報、{n_p}/{a.periodic} 份季/半期報 → {out}")
    for d in sel:
        base = target_name(d, ticker, company)
        print("  " + _row(d, ticker, company))
        for fmt in [f.strip() for f in a.format.split(",") if f.strip()]:
            print("    " + download_doc(d, fmt, out, base, key, a.force))
    if n_a < a.annual or n_p < a.periodic:
        print(f"[edinet] ⚠ 份數不足：{a.days} 天內 EDINET 只有上列文件（可加大 --days；"
              "第1/第3四半期的決算短信在 TDnet，不在 EDINET）")


if __name__ == "__main__":
    main()
