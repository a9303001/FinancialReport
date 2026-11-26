#!/usr/bin/env python3
"""collectStk §10 自我檢查：每次執行完（push 前）必跑；改過 skill 後再跑一次直到 0 個 ERROR。

用法：
  python .claude/skills/collectStk/scripts/selfcheck.py          # 只檢查
  python .claude/skills/collectStk/scripts/selfcheck.py --fix    # 檢查 + 自動修可機械修正的項目

檢查項目（ERROR 會讓結束碼 = 1）：
  E1 SKILL.md / references 提到的 references/*.md、scripts/*.py、其他 skill 腳本路徑都存在
  E2 collectStk 內文的 §編號引用都對得到章節；其他 skill 引用「collectStk §X」也對得到
  E3 collectStk、edinet 的 Python 腳本都能編譯
  E4 .claude/skills 與 .agents/skills 每個 skill 資料夾內容相同（--fix：以 .claude 為準複製過去）
  E5 git 追蹤了 .env（API key 外洩風險）
  E6 edinet.py selftest --offline 失敗（edinet 自己的命名／去重／參數／鏡像檢查）
  W1 `[yyyy-mm]` 驗證標記超過 6 個月 → 下次用到該站要重新驗證
  W2 SKILL.md 超過 450 行、references 單檔超過 150 行 → 依 §10 刪減過時內容
  W3 repo 根目錄留有 .playwright-mcp/（--fix：刪除）
只用 Python 標準函式庫。
"""
from __future__ import annotations

import argparse
import filecmp
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve()
SKILL = HERE.parent.parent                 # .../skills/collectStk
SKILLS = SKILL.parent                      # .../skills
REPO = SKILLS.parent.parent                # repo root
MASTER = REPO / ".claude" / "skills"       # 唯一編輯來源
MIRROR = REPO / ".agents" / "skills"       # Gemini 用的鏡像
IGNORE = {".env", "__pycache__"}

errors: list[str] = []
warns: list[str] = []
fixed: list[str] = []


def md_files() -> list[Path]:
    return [SKILL / "SKILL.md"] + sorted((SKILL / "references").glob("*.md"))


# ---------------------------------------------------------------- E1 paths
def check_paths() -> None:
    pat = re.compile(r"`((?:\.claude/skills/[\w-]+/)?(?:references|scripts)/[\w.-]+\.(?:md|py))`")
    for f in md_files():
        for m in pat.finditer(f.read_text(encoding="utf-8")):
            rel = m.group(1)
            target = REPO / rel if rel.startswith(".claude/") else SKILL / rel
            if not target.exists():
                errors.append(f"E1 {f.relative_to(REPO)} 提到 `{rel}`，但檔案不存在")


# ---------------------------------------------------------------- E2 § refs
HEAD_SKILL = re.compile(r"^#{2,4}\s+(\d+(?:\.\d+)*)[.\s]", re.M)
HEAD_REF = re.compile(r"^#{2,4}\s+§(\d+(?:\.\d+)*)", re.M)
REF = re.compile(r"§(\d+(?:\.\d+)*)")
FOREIGN = re.compile(r"(AGENTS\.md|edinet|Convert2md|collectState|stateAnalysis|StockAnalysis)[^§\n]{0,12}$")


def _unfenced(text: str) -> str:
    """去掉 ``` / ```` 圍起來的範本區塊（報告範本裡的「## 1.」不是本 Skill 的章節）。"""
    return re.sub(r"^(`{3,})[^\n]*\n.*?^\1\s*$", "", text, flags=re.M | re.S)


def defined_sections() -> set[str]:
    ids = set(HEAD_SKILL.findall(_unfenced((SKILL / "SKILL.md").read_text(encoding="utf-8"))))
    for f in md_files()[1:]:
        ids |= set(HEAD_REF.findall(_unfenced(f.read_text(encoding="utf-8"))))
    return ids


def _ok(ref: str, ids: set[str]) -> bool:
    # 已定義的節，或「章」本身（如 §4 對到 4.1~4.5）
    return ref in ids or any(i.startswith(ref + ".") for i in ids)


def check_refs() -> None:
    ids = defined_sections()
    for f in md_files():
        for ln, line in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
            for m in REF.finditer(line):
                if FOREIGN.search(line[:m.start()]):
                    continue  # 引用的是別的檔案／skill 的章節
                if not _ok(m.group(1), ids):
                    errors.append(f"E2 {f.relative_to(REPO)}:{ln} 引用 §{m.group(1)}，但沒有這個章節")
    # 其他 skill 對 collectStk 的引用（只檢查「collectStk」之後同一句內的 §）
    for f in sorted(MASTER.glob("*/SKILL.md")):
        if f.parent == SKILL:
            continue
        for ln, line in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
            for m in re.finditer(r"collectStk`?[（(]?([^。；\n]{0,80})", line):
                seg = m.group(1)
                cut = re.search(r"collectState|stateAnalysis|本檔|本 Skill", seg)
                seg = seg[:cut.start()] if cut else seg
                for r in REF.findall(seg):
                    if not _ok(r, ids):
                        errors.append(f"E2 {f.relative_to(REPO)}:{ln} 引用 collectStk §{r}，但 collectStk 沒有這個章節")


# ---------------------------------------------------------------- E3 compile
def check_compile() -> None:
    for d in (SKILL, SKILLS / "edinet"):
        for py in sorted(d.glob("scripts/*.py")):
            try:  # 只編譯不寫 .pyc
                compile(py.read_text(encoding="utf-8"), str(py), "exec")
            except SyntaxError as e:
                errors.append(f"E3 {py.relative_to(REPO)}:{e.lineno} 語法錯誤：{e.msg}")


# ---------------------------------------------------------------- E4 mirror sync
def _diff(a: Path, b: Path) -> list[str]:
    out = []
    names = {p.name for p in a.iterdir() if p.name not in IGNORE} if a.is_dir() else set()
    names |= {p.name for p in b.iterdir() if p.name not in IGNORE} if b.is_dir() else set()
    for n in sorted(names):
        pa, pb = a / n, b / n
        if pa.is_dir() or pb.is_dir():
            out += _diff(pa, pb)
        elif not pa.exists() or not pb.exists() or not filecmp.cmp(pa, pb, shallow=False):
            out.append(str(pa.relative_to(MASTER)))
    return out


def check_mirror(fix: bool) -> None:
    if not MIRROR.is_dir():
        return
    for d in sorted(p for p in MASTER.iterdir() if p.is_dir()):
        diff = _diff(d, MIRROR / d.name)
        if not diff:
            continue
        if fix:
            dst = MIRROR / d.name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(d, dst, ignore=shutil.ignore_patterns(*IGNORE, "*.pyc"))
            fixed.append(f"E4 已把 .claude/skills/{d.name} 同步到 .agents/skills/{d.name}（{len(diff)} 個檔不同）")
        else:
            errors.append(f"E4 .agents/skills/{d.name} 與 .claude 不同：{', '.join(diff[:5])}（用 --fix 同步）")


# ---------------------------------------------------------------- E5 secrets
def check_secrets() -> None:
    try:
        out = subprocess.run(["git", "-C", str(REPO), "ls-files"], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired):
        return
    leaked = [l for l in out.splitlines() if Path(l).name == ".env"]  # .env.example 不算
    if leaked:
        errors.append("E5 git 追蹤了 .env：" + ", ".join(leaked) + "（立即 git rm --cached 並換 key）")


# ---------------------------------------------------------------- E6 edinet selftest
def check_edinet() -> None:
    py = SKILLS / "edinet" / "scripts" / "edinet.py"
    if not py.is_file():
        return
    try:
        r = subprocess.run([sys.executable, str(py), "selftest", "--offline"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        errors.append(f"E6 edinet selftest 無法執行：{e}")
        return
    if r.returncode != 0:
        fails = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
        errors.append("E6 edinet selftest 失敗：" + ("；".join(fails[:5]) or r.stderr.strip()[-300:])
                      + "（照 edinet SKILL.md §9 修；鏡像不一致可先 --fix）")


# ---------------------------------------------------------------- W1-W3
def check_warnings(fix: bool) -> None:
    today = date.today()
    limit = today.year * 12 + today.month - 6
    stale = []
    for f in md_files():
        for ln, line in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
            tags = re.findall(r"\[(20\d\d)-(\d\d)\]", line)
            if tags and max(int(y) * 12 + int(m) for y, m in tags) < limit:
                stale.append(f"{f.name}:{ln}")
    if stale:
        warns.append(f"W1 {len(stale)} 列驗證標記超過 6 個月：{', '.join(stale[:10])}")
    n = len((SKILL / "SKILL.md").read_text(encoding="utf-8").split("\n"))
    if n > 450:
        warns.append(f"W2 SKILL.md 有 {n} 行（> 450），依 §10 刪減過時或重複內容")
    for f in md_files()[1:]:
        k = len(f.read_text(encoding="utf-8").split("\n"))
        if k > 150:
            warns.append(f"W2 {f.name} 有 {k} 行（> 150），依 §10 合併／刪減")
    pw = REPO / ".playwright-mcp"
    if pw.exists():
        if fix:
            shutil.rmtree(pw, ignore_errors=True)
            fixed.append("W3 已刪除 .playwright-mcp/")
        else:
            warns.append("W3 repo 根目錄有 .playwright-mcp/，push 前要刪（--fix 會刪）")


def main() -> None:
    ap = argparse.ArgumentParser(description="collectStk skill 自我檢查")
    ap.add_argument("--fix", action="store_true", help="自動修正可機械修正的項目（鏡像同步、刪 .playwright-mcp）")
    a = ap.parse_args()
    check_paths()
    check_refs()
    check_compile()
    check_mirror(a.fix)
    check_secrets()
    check_edinet()  # 放在鏡像同步之後：selftest 也會檢查 .agents 鏡像
    check_warnings(a.fix)
    for x in fixed:
        print("FIXED ", x)
    for x in errors:
        print("ERROR ", x)
    for x in warns:
        print("WARN  ", x)
    print(f"[selfcheck] {len(errors)} error, {len(warns)} warning, {len(fixed)} fixed")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
