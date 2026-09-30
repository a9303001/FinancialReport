#!/usr/bin/env python3
"""LatestNewsResult.md 機械驗收（規則見 gemini/LatestNews.md Step 7）。

用法（在 REPO_ROOT 執行）：
    python gemini/LatestNews_check.py --today 2026-09-30 --prev "2026/09/30 23:41:07"
    --today 省略 = 取台北今天；--prev 省略 = 不檢查「晚於上一版」；--file 可指定其他檔。
輸出最後一行「問題 0 個」才算通過；有問題時 exit code = 1。
"""
import argparse
import datetime as dt
import os
import re
import sys

NON_COMPANY = {"History", "Log", "Prompt", "gemini", "StkScreenerResult",
               "HkReitScreenerResult", "JpReitScreenerResult"}
ZONES = "一二三四五六七八"
NEED = {"HIGH": "①②③④⑤⑥⑦⑧⑨⑩", "MEDIUM": "①②④⑤⑧⑩", "LOW": "①⑤⑩"}
RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
ITEM = re.compile(r"^- (?:🔴|🟢|⚪)")                     # 排行榜條目的標題行
FIELD = re.compile(r"^\s+- \*\*([①-⑩])")                  # W3 欄位行
P_ITEM = re.compile(r"^- \*\*(P[012])｜")                  # 下一輪項目


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=os.path.join(here, "LatestNewsResult.md"))
    ap.add_argument("--root", default=os.path.dirname(here))
    ap.add_argument("--today")
    ap.add_argument("--prev")
    a = ap.parse_args()

    taipei = dt.timezone(dt.timedelta(hours=8))
    today = dt.date.fromisoformat(a.today) if a.today else dt.datetime.now(taipei).date()
    cutoff = today - dt.timedelta(days=7)
    lines = open(a.file, encoding="utf-8").read().splitlines()
    err = []

    def news_date(mmdd):
        """[MM-DD] 補年份：晚於 TODAY 就視為去年（處理跨年）。"""
        m, d = map(int, mmdd.split("-"))
        x = dt.date(today.year, m, d)
        return x if x <= today else dt.date(today.year - 1, m, d)

    # 1. 時間戳與表頭
    ts = re.fullmatch(r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \(UTC\+8\)", lines[0].strip()) if lines else None
    if not ts:
        err.append("第一行不是 `YYYY/MM/DD HH:MM:SS (UTC+8)`")
    elif a.prev and ts.group(1) <= a.prev.strip():
        err.append(f"時間戳 {ts.group(1)} 沒有晚於上一版 {a.prev}")
    if not any("上一版：" in l and "整份重寫" in l for l in lines[:15]):
        err.append("表頭缺「上一版：PREV_TS｜本版：整份重寫」")

    # 2. 八大區各 1 次、順序固定
    heads = "".join(l[3] for l in lines if re.match(r"^## [一二三四五六七八]、", l))
    if heads != ZONES:
        err.append(f"大區應為「{ZONES}」各 1 次且依序，實際為「{heads}」")

    # 3. 逐行掃描
    zone, cur, items, top5, rumors, plans = None, None, [], [], [], []
    zone_text = {z: [] for z in ZONES}
    for i, line in enumerate(lines, 1):
        if re.match(r"^\s*\|.*\|\s*$", line) or re.search(r"\|\s*:?-{3,}", line):
            err.append(f"第 {i} 行疑似 Markdown 表格")
        if line.startswith("## "):
            zone = line[3] if line[3] in ZONES else None
            cur = None
            continue
        if zone:
            zone_text[zone].append(line)
        if zone == "一" and ITEM.match(line):
            n = re.search(r"\*\*N(\d+)｜", line)
            top5.append(f"N{n.group(1)}" if n else "?")
        elif zone == "二":
            if line.startswith("#"):
                cur = None
            elif ITEM.match(line):
                n = re.search(r"\*\*N(\d+)｜\[(\d{2}-\d{2})\]", line)
                lv = re.search(r"重要性：(HIGH|MEDIUM|LOW)", line)
                sc = re.search(r"分數：(\d+)（幅(\d)\s*廣(\d)\s*急(\d)\s*險(\d)\s*注(\d)）", line)
                cur = {"t": line.strip()[:50], "i": i, "n": n, "lv": lv, "sc": sc, "has": set(), "src": ""}
                items.append(cur)
            elif cur and (m := FIELD.match(line)):
                cur["has"].add(m.group(1))
                if m.group(1) == "⑩":
                    cur["src"] = line
        elif zone == "五" and (m := P_ITEM.match(line)):
            cur = {"t": line.strip()[:50], "has": set()}
            plans.append(cur)
        elif zone == "五" and cur and (m := re.match(r"^\s+- \*\*(觸發|交給|要回答|建立日)\*\*：(.*)", line)):
            cur["has"].add(m.group(1))
            if m.group(1) == "建立日":
                cur["built"] = m.group(2).strip()
        elif zone == "六" and line.startswith("- ⚠️"):
            rumors.append((i, line))

    # 4. 排行榜：編號、日期、分級、分數、欄位、來源、排序
    if not items:
        err.append("第二區排行榜 0 則：可能沒用新骨架（標題行要以 🔴/🟢/⚪ 開頭），或真的沒新聞（要在第八區寫明原因）")
    for k, it in enumerate(items, 1):
        t = it["t"]
        if not it["n"]:
            err.append(f"第 {it['i']} 行標題缺「N#｜[MM-DD]」（單一日期）：{t}")
        else:
            if int(it["n"].group(1)) != k:
                err.append(f"編號應為 N{k}：{t}")
            if news_date(it["n"].group(2)) < cutoff:
                err.append(f"日期 {it['n'].group(2)} 早於 CUTOFF {cutoff}：{t}")
        if not it["lv"] or not it["sc"]:
            err.append(f"缺「重要性」或「分數（幅廣急險注）」：{t}")
            continue
        total, parts = int(it["sc"].group(1)), [int(x) for x in it["sc"].groups()[1:]]
        if total != sum(parts):
            err.append(f"分數 {total} ≠ 分項加總 {sum(parts)}：{t}")
        lv = it["lv"].group(1)
        if (lv == "HIGH" and total <= 3) or (lv == "LOW" and total >= 7):
            err.append(f"{lv} 卻 {total} 分，分級或分數有一個錯：{t}")
        it["key"] = (RANK[lv], -total)
        miss = "".join(c for c in NEED[lv] if c not in it["has"])
        if miss:
            err.append(f"缺欄位 {miss}：{t}")
        if "⑩" in it["has"] and "http" not in it["src"] and "`" not in it["src"]:
            err.append(f"⑩ 來源沒有 URL 或本地路徑：{t}")
    ranked = [it for it in items if "key" in it]
    for x, y in zip(ranked, ranked[1:]):
        if x["key"] > y["key"]:
            err.append(f"排序錯：{y['t']} 應排在 {x['t']} 之前")
    want = [f"N{k}" for k in range(1, min(5, len(items)) + 1)]
    if top5 != want:
        err.append(f"1.2 應依序為 {want}，實際為 {top5}")

    # 5. 傳聞區日期
    for i, line in rumors:
        d = re.search(r"\[(\d{2}-\d{2})\]", line)
        if not d:
            err.append(f"第 {i} 行傳聞缺 [MM-DD]")
        elif news_date(d.group(1)) < cutoff:
            err.append(f"第 {i} 行傳聞日期 {d.group(1)} 早於 CUTOFF {cutoff}")

    # 6. 下一輪項目
    if len(plans) < 5:
        err.append(f"下一輪待分析項目只有 {len(plans)} 條（至少 5 條）")
    for p in plans:
        miss = {"觸發", "交給", "要回答", "建立日"} - p["has"]
        if miss:
            err.append(f"下一輪項目缺 {'／'.join(sorted(miss))}：{p['t']}")
        elif p["built"][:10] < cutoff.isoformat():
            err.append(f"建立日 {p['built']} 早於 CUTOFF（無新證據應刪除，有新證據應更新建立日）：{p['t']}")

    # 7. 每間公司都要出現在第四區
    idx = "\n".join(zone_text["四"])
    for name in sorted(os.listdir(a.root)):
        if name.startswith(".") or name in NON_COMPANY or not os.path.isdir(os.path.join(a.root, name)):
            continue
        code = re.match(r"^\d+", name)
        code = code.group(0) if code else name
        if not re.search(rf"(?<![A-Za-z0-9]){re.escape(code)}(?![A-Za-z0-9])", idx):
            err.append(f"第四區沒有列出持股 {name}")

    lv_count = {k: sum(1 for it in ranked if RANK[k] == it["key"][0]) for k in RANK}
    print(f"TODAY {today}｜CUTOFF {cutoff}")
    print(f"二區 {len(items)} 則（HIGH {lv_count['HIGH']}／MEDIUM {lv_count['MEDIUM']}／LOW {lv_count['LOW']}）"
          f"｜六區傳聞 {len(rumors)} 則｜五區項目 {len(plans)} 條")
    for e in err:
        print(" -", e)
    print(f"問題 {len(err)} 個")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
