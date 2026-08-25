#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ArrangePublicOpinionMd — 把各公司資料夾內零散的輿情 md 依年份合併成
{YYYY}_PublicOpinion.md，驗證後刪除原檔，並產出總結報告。

規則以 ../SKILL.md 為準；本檔是該規則的參考實作，關鍵字／regex 清單以本檔為單一事實來源。

用法：
    python arrange_public_opinion.py [--root D:\\FinancialReport]
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# 常數
# --------------------------------------------------------------------------

SKIP_DIRS = {'.git', '.github', '.claude', '.agents', 'Log', 'Prompt',
             'AnalysisResult', 'StkScreenerResult', 'discard'}

MERGED_RE = re.compile(r'^(\d{4})_PublicOpinion(_part\d+)?\.md$')
LEGACY_RE = re.compile(r'^(\d{4})_輿情彙整(_part\d+)?\.md$')

BODY_MARK = '<!-- body:start -->'
SOURCE_RE = re.compile(r'<!-- source-file: (.+?) \|')
MAX_BYTES = 20 * 1024 * 1024          # 超過就該切 part（見 SKILL.md §7）

# §3.1 黑名單：年報／季報／公告／財報本體／分析產出（命中即完全不動）
BLACK_KEYWORDS = [
    'annual', '年報', 'annualreport', '有価証券報告書', 'interim', '中報', '中期報告',
    '半期報告書', 'quarter', '季報', '四半期', '決算短信', '決算説明', '適時開示',
    '10-k', '10k', '10-q', '10q', '20-f', '6-k', '8-k', 'def 14a',
    '公告', 'announcement', '股東會', '通知書', 'notice', 'official_ir',
    '財務報告', 'financial_report', 'earnings_release',
    '第一季度', '第二季度', '第三季度', '第四季度', '未經審核', '營運統計',
    '業績公告', '中期業績', '年度業績',
]
BLACK_REGEX = [
    r'財報(?!狗)',                          # 「財報狗／StatementDog」是輿情來源，不可誤殺
    r'_H[12](_|\.)',                        # 半年報
    r'^S\d{3}[A-Z0-9]{4}\.md$',             # 日本 EDINET
    r'^[a-z]{2,6}-\d{8}\.md$',              # SEC XBRL
    r'^ltn\d+\.md$',                        # 公開資訊觀測站公告
    r'^\d{8,}\.md$',                        # 純數字公告編號
    r'^\d{8}(?![_\-\d])',                   # 8 碼日期 + 中文標題的港股/台股公告
    r'^\d{2}-[0-9A-Za-z]{2,6}-.*\.md$',     # 選股排名產出
    r'(F04|FE4|FI4)(_|\.)',                 # 台股財報代碼
    r'_AI[0-9A-Z](_|\.)',                   # 台股財報 AI 系列
    r'(?<![A-Za-z])[Qq][1-4](?![A-Za-z])',  # 季度（避免誤中 Xueqiu1 之類）
    r'(?i)analysis|_summary_|conversion_summary|_reconciliation_',
    r'(?i)^(readme|index|prompt|agents|claude|orange)\.md$',
    r'(?i)^Routines_',
    MERGED_RE.pattern,                      # 輸出檔本身（舊版 {YYYY}_輿情彙整.md 見 §4.1 遷移規則）
]
# §3.2 白名單
WHITE_REGEX = [
    r'^\d{4}(0[1-9]|1[0-2])_.+\.md$',                # W1 yyyyMM_來源
    r'^\d{4}_[^\d].*\.md$',                          # W2 yyyy_來源
    r'^\d{4}-\d{2}-\d{2}.*\.md$',                    # W4 單篇抓取存檔
    r'^_SubAgentC_feed_\d{8}_Round\d+\.md$',         # W5
    r'(?i)輿情|新聞|討論|sentiment|news|feed',        # W3
]
SOURCE_NAMES = [  # W6，可持續擴充
    'PTT', 'Dcard', 'Mobile01', 'CMoney', '股市爆料', '財報狗', 'StatementDog',
    'Reddit', 'Twitter', 'SeekingAlpha', 'Motley', 'TipRanks', 'YahooFinance',
    'Yahoo_Finance', 'GoogleNews', 'Xueqiu', '雪球', 'Eastmoney', '東方財富',
    'Guba', 'Sina', '新浪', 'Futu', '富途', 'Moomoo', 'LIHKG', '高登', 'HKEJ',
    'HKET', 'HK01', 'Minkabu', 'Kabutan', '5ch', 'note', 'Reuters', 'Nikkei',
    'Bloomberg', 'Investing', 'MarketBeat', 'StockTitan', 'MoneyDJ', 'Cnyes',
    '鉅亨', '經濟日報', 'udn', 'anue', 'BigGo',
]
# §3.3 內容判定
CONTENT_EXCLUDE = ['合併財務報告', '會計師核閱', '會計師查核', '資產負債表', '綜合損益表',
                   '現金流量表', 'Form 10-K', 'Form 10-Q', 'ITEM 1. BUSINESS',
                   '有価証券報告書', '四半期報告書', '股東常會', '董事會決議']
CONTENT_INCLUDE = ['輿情', '討論', '留言', '網友', '看多', '看空', '情緒', '鄉民', '貼文',
                   'Reddit', 'PTT', '雪球', 'Seeking Alpha', '來源網站', '抓取方式', '新聞']


# --------------------------------------------------------------------------
# 分類
# --------------------------------------------------------------------------

def is_black(name: str) -> str | None:
    """命中黑名單則回傳命中的規則字串，否則 None。"""
    low = name.lower()
    for kw in BLACK_KEYWORDS:
        if kw in low:
            return f'黑名單關鍵字「{kw}」'
    for pat in BLACK_REGEX:
        if re.search(pat, name):
            return f'黑名單樣式 `{pat}`'
    return None


def is_white(name: str) -> str | None:
    for pat in WHITE_REGEX:
        if re.search(pat, name):
            return f'白名單樣式 `{pat}`'
    low = name.lower()
    for src in SOURCE_NAMES:
        if src.lower() in low:
            return f'輿情來源名「{src}」'
    return None


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore')


def sniff_content(path: Path) -> tuple[bool | None, str]:
    """灰色地帶內容判定：前 60 行 + 中段 20 行。回傳 (是否輿情, 理由)；None = 待人工確認。"""
    lines = read_text(path).split('\n')
    mid = len(lines) // 2
    sample = '\n'.join(lines[:60] + lines[mid:mid + 20])
    hit_ex = [k for k in CONTENT_EXCLUDE if k in sample]
    hit_in = [k for k in CONTENT_INCLUDE if k in sample]
    if hit_ex and not hit_in:
        return False, f'內容含財報／公告特徵：{"、".join(hit_ex[:3])}'
    if hit_in and not hit_ex:
        return True, f'內容含輿情特徵：{"、".join(hit_in[:3])}'
    if hit_ex and hit_in:
        return None, f'特徵衝突（財報：{hit_ex[0]}／輿情：{hit_in[0]}）'
    return None, '前 60 行與中段皆無明確特徵'


def year_of(path: Path) -> tuple[int, str]:
    """§3.4 年份判定，回傳 (年份, 來源標記)。"""
    name, this_year = path.name, dt.date.today().year
    for pat, tag in [(r'^(\d{4})(?:0[1-9]|1[0-2])_', 'yyyyMM'),
                     (r'^(\d{4})-\d{2}-\d{2}', 'yyyy-mm-dd'),
                     (r'(20\d{2})\d{4}', 'yyyymmdd'),
                     (r'^(\d{4})_', 'yyyy_')]:
        m = re.search(pat, name)
        if m and 2000 <= int(m.group(1)) <= this_year + 1:
            return int(m.group(1)), tag
    head = '\n'.join(read_text(path).split('\n')[:40])
    m = re.search(r'(20\d{2})[-/年]\d{1,2}', head)
    if m and 2000 <= int(m.group(1)) <= this_year + 1:
        return int(m.group(1)), 'content'
    return dt.date.fromtimestamp(path.stat().st_mtime).year, 'mtime(推定)'


def month_key(name: str) -> str:
    """§4.2 排序用月份；無月份者記 12 排最後。"""
    for pat in (r'^\d{4}(0[1-9]|1[0-2])_', r'^\d{4}-(\d{2})-\d{2}', r'\d{4}(\d{2})\d{2}'):
        m = re.search(pat, name)
        if m and 1 <= int(m.group(1)) <= 12:
            return f'{int(m.group(1)):02d}'
    return '12'


def source_title(name: str) -> str:
    """章節標題：檔名去掉日期前綴與副檔名。"""
    stem = re.sub(r'\.md$', '', name)
    stripped = re.sub(r'^(\d{4}-\d{2}-\d{2}|\d{6}|\d{4})[_\-]', '', stem)
    return stripped or stem


# --------------------------------------------------------------------------
# 合併
# --------------------------------------------------------------------------

def demote_headings(text: str, levels: int = 2) -> str:
    """ATX 標題下降 levels 級；反引號區塊內不動（§4.3）。"""
    out, in_fence = [], False
    for line in text.split('\n'):
        if re.match(r'^\s*(```|~~~)', line):
            in_fence = not in_fence
        elif not in_fence:
            m = re.match(r'^(#{1,6})(\s)', line)
            if m:
                line = '#' * min(6, len(m.group(1)) + levels) + line[len(m.group(1)):]
        out.append(line)
    return '\n'.join(out)


def build_section(src: Path, year: int) -> tuple[str, str]:
    """回傳 (章節文字, 章節標題)。"""
    raw = read_text(src)
    sha = hashlib.sha1(raw.encode('utf-8')).hexdigest()[:12]
    title = f'{year}-{month_key(src.name)} · {source_title(src.name)}'
    meta = (f'<!-- source-file: {src.name} | bytes: {src.stat().st_size} '
            f'| sha1: {sha} | merged-at: {dt.date.today().isoformat()} -->')
    return f'\n## {title}\n\n{meta}\n\n{demote_headings(raw).strip()}\n\n---\n', title


def anchor(title: str) -> str:
    slug = re.sub(r'[^\w\u4e00-\u9fff\- ]', '', title.lower()).strip().replace(' ', '-')
    return f'#{slug}'


def build_header(company: str, year: int, titles: list[str], added: int, total: int) -> str:
    toc = '\n'.join(f'- [{t}]({anchor(t)})' for t in titles) or '- （無章節）'
    return (
        f'# [{company}] {year} 年 輿情彙整\n\n'
        f'> 本檔由 **ArrangePublicOpinionMd Skill** 自動彙整，內容為本資料夾 {year} 年度所有'
        f'「輿情／新聞／討論區」`.md` 的原文合併。\n'
        f'> 不含年報、季報、公司公告 report。\n'
        f'> 最後彙整時間：{dt.datetime.now():%Y-%m-%d %H:%M}'
        f'｜本次併入：{added} 檔｜累計併入：{total} 檔\n\n'
        f'## 目錄\n\n{toc}\n\n{BODY_MARK}\n'
    )


def split_body(merged: Path) -> str:
    """取出既有 body；無 body 標記的舊檔整份保留為 body 前段（§4.4）。"""
    if not merged.exists():
        return ''
    text = read_text(merged)
    return text.split(BODY_MARK, 1)[1] if BODY_MARK in text else '\n' + text.strip() + '\n'


def atomic_write(target: Path, content: str) -> None:
    """§4.5 先寫 .tmp，確認可讀後才取代正式檔。"""
    tmp = target.with_suffix(target.suffix + '.tmp')
    tmp.write_text(content, encoding='utf-8', newline='\n')
    if tmp.stat().st_size == 0 or not read_text(tmp).strip():
        tmp.unlink(missing_ok=True)
        raise IOError(f'暫存檔內容為空：{tmp.name}')
    tmp.replace(target)


# --------------------------------------------------------------------------
# 驗證與刪除
# --------------------------------------------------------------------------

def _norm(text: str) -> str:
    """去空白與 ATX 的 '#'（合併時階層會下降，見 §4.3）。"""
    return re.sub(r'[#\s]+', '', text)


def verify(merged_text: str, src: Path) -> str | None:
    """通過回傳 None，否則回傳未通過的檢查代號。"""
    if f'source-file: {src.name} |' not in merged_text:                 # C2
        return 'C2 缺少 source-file 註記'
    probe = _norm(read_text(src))[:200]                                 # C3
    if not probe or probe not in _norm(merged_text):
        return 'C3 原文內容比對失敗'
    if is_black(src.name):                                              # C5
        return 'C5 命中黑名單'
    return None


def git_ok(root: Path) -> bool:
    return run_git(root, ['rev-parse', '--is-inside-work-tree'])[0]


def run_git(root: Path, args: list[str]) -> tuple[bool, str]:
    try:
        p = subprocess.run(['git', *args], cwd=root, capture_output=True,
                           text=True, encoding='utf-8', errors='ignore')
        return p.returncode == 0, (p.stdout or '') + (p.stderr or '')
    except OSError as exc:
        return False, str(exc)


def delete_file(root: Path, path: Path, use_git: bool) -> tuple[bool, str]:
    """逐檔刪除；優先 git rm，保留可復原性（§5.2）。"""
    rel = path.relative_to(root).as_posix()
    if use_git:
        ok, out = run_git(root, ['rm', '--quiet', '--', rel])
        if ok:
            return True, 'git rm'
        if 'did not match' not in out:                 # 未追蹤的檔案改用檔案系統刪除
            return False, out.strip()[:200]
    try:
        path.unlink()
        return True, 'unlink'
    except OSError as exc:
        return False, str(exc)


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------

class Report:
    def __init__(self) -> None:
        self.companies = 0
        self.scanned = 0
        self.sentiment = 0
        self.excluded_report = 0     # 年報／季報／公告
        self.excluded_system = 0     # 分析報告／系統檔
        self.merged_files: set[str] = set()
        self.detail: list[tuple] = []      # 公司, 年, 彙整檔, 併入, 刪除, 備註
        self.excluded: list[tuple] = []    # 公司, 檔名, 原因, 規則
        self.manual: list[tuple] = []      # 公司, 檔名, 原因, 建議
        self.errors: list[tuple] = []      # 公司, 檔名, 錯誤
        self.deleted = 0
        self.notes: list[str] = []


SYSTEM_RULE_HINT = ('analysis', '_summary_', 'conversion_summary', 'readme',
                    'index', 'prompt', 'agents', 'claude', 'routines', '_reconciliation_',
                    'orange')


def classify(path: Path, company: str, rep: Report) -> tuple[bool, str]:
    """回傳 (是否為輿情檔, 理由)；順帶累計排除統計。"""
    if MERGED_RE.match(path.name):
        rep.excluded.append((company, path.name, '本 Skill 的輸出檔（不併入、不刪除）', '§3.1-D'))
        return False, '輸出檔本身'
    hit = is_black(path.name)
    if hit:
        is_system = any(k in hit.lower() for k in SYSTEM_RULE_HINT)
        rep.excluded_system += is_system
        rep.excluded_report += not is_system
        rep.excluded.append((company, path.name,
                             '分析報告／系統檔' if is_system else '年報／季報／公告／財報',
                             hit))
        return False, hit
    hit = is_white(path.name)
    if hit:
        return True, hit
    verdict, why = sniff_content(path)
    if verdict is True:
        return True, why
    if verdict is False:
        rep.excluded_report += 1
        rep.excluded.append((company, path.name, '內容判定為財報／公告', why))
        return False, why
    rep.manual.append((company, path.name, why, '請人工確認後手動歸檔或刪除'))
    return False, why


def migrate_legacy(company_dir: Path, root: Path, use_git: bool,
                   rep: Report) -> dict[Path, int]:
    """§4.1 舊版檔名遷移：{YYYY}_輿情彙整.md → {YYYY}_PublicOpinion.md。

    回傳「新檔已存在、需當成一般來源併入」的舊檔 → 年份。
    """
    pending: dict[Path, int] = {}
    for old in sorted(company_dir.glob('*.md')):
        m = LEGACY_RE.match(old.name)
        if not m:
            continue
        year = int(m.group(1))
        new = company_dir / f'{m.group(1)}_PublicOpinion{m.group(2) or ""}.md'
        if new.exists():                    # 兩者都在 → 舊檔當來源併入，驗證後刪除
            pending[old] = year
            rep.notes.append(f'{company_dir.name}：`{new.name}` 已存在，舊檔 `{old.name}` '
                             f'改以一般來源併入後刪除')
            continue
        if not (use_git and run_git(root, ['mv', '--',
                                           old.relative_to(root).as_posix(),
                                           new.relative_to(root).as_posix()])[0]):
            old.rename(new)
        rep.notes.append(f'{company_dir.name}：舊檔 `{old.name}` 已改名為 `{new.name}`')
    return pending


def process_company(company_dir: Path, root: Path, use_git: bool, rep: Report) -> None:
    company = company_dir.name
    rep.companies += 1
    pending_legacy = migrate_legacy(company_dir, root, use_git, rep)

    by_year: dict[int, list[Path]] = {}
    for path in sorted(company_dir.glob('*.md')):
        if not path.is_file():
            continue
        rep.scanned += 1
        try:
            if path in pending_legacy:
                keep, year, tag = True, pending_legacy[path], 'legacy'
            else:
                keep, _ = classify(path, company, rep)
                year, tag = (year_of(path) if keep else (0, ''))
        except OSError as exc:
            rep.errors.append((company, path.name, f'讀取失敗：{exc}'))
            continue
        if not keep:
            continue
        if path.stat().st_size == 0:
            rep.errors.append((company, path.name, '空檔（0 bytes）：不併入、不刪除'))
            continue
        rep.sentiment += 1
        by_year.setdefault(year, []).append(path)
        if tag.startswith('mtime'):
            rep.notes.append(f'{company}/{path.name}：年份 {year} 為 mtime 推定')

    for year in sorted(by_year):
        merge_year(company_dir, root, year, by_year[year], use_git, rep)


def merge_year(company_dir: Path, root: Path, year: int,
               sources: list[Path], use_git: bool, rep: Report) -> None:
    company = company_dir.name
    merged = company_dir / f'{year}_PublicOpinion.md'
    sources = sorted(sources, key=lambda p: (month_key(p.name), p.name))

    body = split_body(merged)
    known = set(SOURCE_RE.findall(body))
    added, added_bytes = [], 0
    for src in sources:
        if src.name in known:
            continue
        try:
            section, _ = build_section(src, year)
        except OSError as exc:
            rep.errors.append((company, src.name, f'讀取失敗：{exc}'))
            continue
        body += section
        added.append(src)
        added_bytes += src.stat().st_size

    # 目錄只列本 Skill 產生的章節（帶 source-file 註記者），不動舊檔既有的標題
    titles = re.findall(r'^## (.+)\n\n<!-- source-file:', body, flags=re.M)
    total = len(set(SOURCE_RE.findall(body)))
    try:
        atomic_write(merged, build_header(company, year, titles, len(added), total) + body)
    except (OSError, IOError) as exc:
        rep.errors.append((company, merged.name, f'寫入失敗：{exc}；該年度不刪任何檔'))
        return
    rep.merged_files.add(str(merged))

    merged_text = read_text(merged)
    size = merged.stat().st_size
    if size == 0 or (added_bytes and size < added_bytes * 0.95):        # C1 / C4
        rep.errors.append((company, merged.name, 'C1/C4 未通過：併入可能不完整，該年度不刪任何檔'))
        rep.detail.append((company, year, merged.name, len(added), 0, 'C1/C4 未通過'))
        return
    if size > MAX_BYTES:
        rep.notes.append(f'{company}/{merged.name} 已超過 20 MB，請依 §7 切成 _part{{n}}')

    deleted = 0
    for src in sources:
        fail = verify(merged_text, src)
        if fail:
            rep.errors.append((company, src.name, f'{fail}：不刪除'))
            continue
        ok, how = delete_file(root, src, use_git)
        if ok:
            deleted += 1
            rep.deleted += 1
        else:
            rep.errors.append((company, src.name, f'刪除失敗（{how}）'))
    rep.detail.append((company, year, merged.name, len(added), deleted, '—'))


def write_report(root: Path, rep: Report, git_note: str) -> Path:
    log_dir = root / 'Log'
    log_dir.mkdir(exist_ok=True)
    out = log_dir / f'ArrangePublicOpinionMd_Summary_{dt.date.today():%Y%m%d}.md'

    def table(header: list[str], rows: list[tuple]) -> str:
        if not rows:
            return '（無）\n'
        cell = lambda c: str(c).replace('|', r'\|').replace('\n', ' ')
        head = '| ' + ' | '.join(header) + ' |\n|' + '|'.join([' :--- '] * len(header)) + '|\n'
        return head + '\n'.join('| ' + ' | '.join(cell(c) for c in r) + ' |' for r in rows) + '\n'

    lines = [
        f'# ArrangePublicOpinionMd 執行報告 {dt.datetime.now():%Y-%m-%d %H:%M}\n',
        git_note + '\n',
        '## Section 1 — 統計概覽\n',
        table(['指標', '數量'], [
            ('掃描公司資料夾數', rep.companies),
            ('掃描 `.md` 總數', rep.scanned),
            ('判定為輿情檔', rep.sentiment),
            ('排除：年報／季報／公告', rep.excluded_report),
            ('排除：分析報告／系統檔', rep.excluded_system),
            ('產生／更新的彙整檔數', len(rep.merged_files)),
            ('已刪除的原始檔數', rep.deleted),
            ('待人工確認（灰色地帶）', len(rep.manual)),
        ]),
        '\n## Section 2 — 各公司明細\n',
        table(['公司', '年份', '彙整檔', '本次併入', '已刪除', '備註'], rep.detail),
        '\n## Section 3 — 排除清單\n',
        table(['公司', '檔名', '排除原因', '命中規則'], rep.excluded),
        '\n## Section 4 — 人工確認清單\n',
        table(['公司', '檔名', '判定困難的原因', '建議'], rep.manual),
        '\n## Section 5 — 錯誤與跳過\n',
        table(['公司', '檔名', '錯誤／跳過原因'], rep.errors),
        '\n## 附註\n',
        ('\n'.join(f'- {n}' for n in rep.notes) or '（無）') + '\n',
        '\n## 復原指引\n',
        '```bash\ngit checkout HEAD -- "<公司資料夾>/<被刪檔名>"\n```\n',
    ]
    out.write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description='合併各公司輿情 md 為年度彙整檔')
    ap.add_argument('--root', default=str(Path(__file__).resolve().parents[4]),
                    help='FinancialReport repo 根目錄')
    root = Path(ap.parse_args().root).resolve()

    # Phase 0
    if not (root / 'AGENTS.md').exists():
        print(f'[中止] {root} 底下找不到 AGENTS.md，路徑可能錯誤。', file=sys.stderr)
        return 1
    use_git = git_ok(root)
    git_note = ('> git 可用，刪除以 `git rm` 執行，可復原。' if use_git
                else '> [!WARNING]\n> 無 git 保護，刪除不可復原。')
    if use_git:
        dirty = [l for l in run_git(root, ['status', '--porcelain'])[1].splitlines()
                 if l.strip().endswith('.md')]
        if dirty:
            git_note += f'\n>\n> 執行前工作區有 {len(dirty)} 個未提交的 `.md` 變更。'

    rep = Report()
    for d in sorted(root.iterdir()):
        if d.is_dir() and d.name not in SKIP_DIRS:
            process_company(d, root, use_git, rep)

    out = write_report(root, rep, git_note)
    print(f'公司 {rep.companies}｜掃描 {rep.scanned}｜輿情 {rep.sentiment}｜'
          f'彙整檔 {len(rep.merged_files)}｜刪除 {rep.deleted}｜人工確認 {len(rep.manual)}')
    print(f'報告：{out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
