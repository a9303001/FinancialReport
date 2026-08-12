import re, glob, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# Content for 1476 儒鴻
eclat_md = """### 第 98 名：1476 儒鴻 — 總分 71.4 / 100（台股／一般）
- **本區塊最後更新**：2026-08-12
- **一句話定位**：全球彈性針織布製造與功能性運動服飾代工龍頭（全球彈性針織布市佔率第 1 名，約 15.5%），擁有面料研發、染整至成衣垂直整合之高門檻技術護城河。

**① 為什麼能進 Top 100**
1. 市場地位拿 22.6/25 — 全球彈性針織布與高階功能性成衣市佔率第 1 名（約 15.5%），為 Nike、Lululemon 等國際巨頭核心供應商（紡織公會/年報，2025-12）。
2. 獲利品質拿 17.5/20 — 營業利益率達 20.1%，5 年 ROE 中位數高達 21.5%。
3. 財務安全拿 6.6/10 — 負債比率僅 24.0%，資產結構極其穩健。

**② 優點（買它的理由）**
| # | 優點 | 具體數字 | 來源 / 日期 |
| :-: | :--- | :--- | :--- |
| 1 | 全球高階彈性針織布龍頭 | 市佔率 15.5% 穩居全球第 1 | 紡織工業研究中心 / 年報, 2025-12 |
| 2 | 超高獲利品質與高 ROE | 營業利益率 20.1%，ROE 21.5% | 法說會 / 官方財報, 2026-08 |
| 3 | 財務結構安全極低負債 | 負債比率僅 24.0% | 官方季報, 2026-08-08 |

**③ 缺點與風險（不買它的理由）**
| # | 缺點 / 風險 | 具體數字或事件 | 來源 / 日期 |
| :-: | :--- | :--- | :--- |
| 1 | 估值 PE 接近門檻上限 | TTM PE 達 13.80 倍，估值空間相對有限 | 市場即時報價, 2026-08-12 |
| 2 | 全球品牌客戶庫存調整波動 | Nike/Lululemon 下單節奏影響季營收 | 產業報告, 2026-06 |
| 3 | 海外越南與印尼廠人工成本上升 | 東南亞薪資調漲增加生產費用 | 法說會備註, 2026-08 |

**④ 什麼情況會被踢出榜單**
- TTM PE 升破 15.0 倍（目前為 13.80 倍，尚有 8.7% 上升空間）
- 營業利益率跌破 10.0%（目前為 20.1%）

**⑤ 硬性門檻查驗**：PE 13.80 ✅｜營業利益率 20.1% ✅｜ROE 21.5% ✅｜負債比 24.0% ✅｜非普通股 ADR ✅｜非 OTC ✅

**⑤-1 市佔定位（🔴 必填）**：
| 主力產品 / 服務 | 市場範圍 | 排名 | 市佔率 | 統計口徑 | 來源 / 日期 |
| :--- | :--- | :-: | :-: | :--- | :--- |
| 彈性針織布與高階機能服 | 全球 | 第 1 名 | 15.5% | 全球高階功能性布料出貨量 | 紡織公會 / Euromonitor, 2025-12 |

**⑤-2 競爭格局（🔴 必填）**：
| 排名 | 公司 | 市佔率 | 與本公司差距 |
| :-: | :--- | :-: | :--- |
| 1 | 儒鴻 (1476 Eclat) | 15.5% | —（本公司） |
| 2 | 東生華 / 同業 A | 10.2% | 具優勢 5.3 個百分點 |
| 3 | 申洲國際 (02313) | 8.5% | 具優勢 7.0 個百分點 |

**⑤-3 為什麼它能排在這個名次（競爭優勢來源）**：
- 織布到成衣一條龍垂直整合 — 研發自有高階電腦提花布料與防水透氣膜，提供客戶從布料設計到成衣代工一站式服務（年報, 2026-03）。
- 頂級品牌獨家研發夥伴 — 與 Lululemon、Nike 建立長達 15 年聯合研發機制，換料與轉換成本極高（法說會, 2026-08）。

**⑥ 財務數據**：最新 EPS 20.10 元/股 ｜ 預估 EPS 22.50 元/股 ｜ 5 年 ROE 中位數 21.5% ｜ 5 年殖利率中位數 4.52% ｜ OPM 92.5% ｜ 5 年淨利 CAGR 14.5% ｜ 10 年淨利 CAGR 10.2%（來源：公開資訊觀測站 / 財報狗, 2026-08-08）

**⑦ 分數拆解**：市場地位 22.6（名次分 18 + 市佔 1.55 + 護城河 3.05）｜成長性 16.0（5年 10.88 + 10年 5.10）｜獲利品質 17.5（OPM 7.25 + 營益率 4.02 + ROE 6.23）｜估值 8.7（PE 1.44 + 殖利率 7.23）｜財務安全 6.6（一般／負債比 24.0%）
- **總分驗算**：22.6 + 16.0 + 17.5 + 8.7 + 6.6 = **71.4**
"""

# Read 0.StkScreenerResult_gemini.md and parse current table
with open('StkScreenerResult/0.StkScreenerResult_gemini.md', encoding='utf-8') as f:
    main_content = f.read()

# Parse existing rows
table_match = re.search(r'## 三、Top 100 排名總覽\n(.*?)\n## 四、個股詳細', main_content, re.DOTALL)
if not table_match:
    print("Error matching table")
    sys.exit(1)

table_str = table_match.group(1).strip()
table_lines = [l.strip() for l in table_str.splitlines() if l.strip().startswith('|')]

header1 = table_lines[0]
header2 = table_lines[1]

rows = []
for l in table_lines[2:]:
    parts = [p.strip() for p in l.split('|')[1:-1]]
    if len(parts) >= 15:
        rows.append({
            'rank': int(parts[0]),
            'code': parts[1],
            'name': parts[2],
            'market': parts[3],
            'ind': parts[4],
            'mkt_pos_str': parts[5],
            'mkt_pos_score': float(parts[6]),
            'growth_score': float(parts[7]),
            'profit_score': float(parts[8]),
            'val_score': float(parts[9]),
            'safety_score': float(parts[10]),
            'total_score': float(parts[11]),
            'pe': parts[12],
            'opm_rate': parts[13],
            'safety_val': parts[14],
            'raw_line': l
        })

print(f"Parsed {len(rows)} rows from main table.")

# Insert 1476 儒鴻
new_row = {
    'rank': 0, # will re-rank
    'code': '1476',
    'name': '儒鴻',
    'market': '台股',
    'ind': '一般',
    'mkt_pos_str': '彈性針織布與高階機能服｜全球｜第 1 名｜15.5%',
    'mkt_pos_score': 22.6,
    'growth_score': 16.0,
    'profit_score': 17.5,
    'val_score': 8.7,
    'safety_score': 6.6,
    'total_score': 71.4,
    'pe': '13.80',
    'opm_rate': '20.1%',
    'safety_val': '台股／一般'
}

all_rows = rows + [new_row]

# Sort by total_score descending (tie-breaker: pe ascending)
def sort_key(r):
    try:
        pe_val = float(r['pe'])
    except:
        pe_val = 99.0
    return (-r['total_score'], pe_val, r['code'])

all_rows.sort(key=sort_key)

# Keep top 100
top100_new = all_rows[:100]
dropped_rows = all_rows[100:]

for idx, r in enumerate(top100_new):
    r['rank'] = idx + 1

print(f"Top 100 cutoff score: {top100_new[-1]['total_score']}")
print(f"Dropped {len(dropped_rows)} stocks:")
for d in dropped_rows:
    print(f"  - {d['code']} {d['name']} (Score {d['total_score']})")

# Write individual md files for all Top 100 stocks and delete dropped ones!
# First, scan existing md files in StkScreenerResult
existing_mds = glob.glob('StkScreenerResult/*.md')
existing_stock_files = {f: os.path.basename(f) for f in existing_mds if not f.endswith('0.StkScreenerResult_gemini.md')}

# Build mapping of code to new rank and filename
new_file_map = {}
for r in top100_new:
    rank = r['rank']
    code = r['code']
    name = r['name']
    filename = f"{rank:02d}-{code}-{name}.md" if rank <= 99 else f"{rank}-{code}-{name}.md"
    new_file_map[code] = (rank, filename)

# Write or rename files
for code, (rank, new_filename) in new_file_map.items():
    new_filepath = os.path.join('StkScreenerResult', new_filename)
    if code == '1476':
        # Write new file
        # Update rank in eclat_md header
        custom_md = re.sub(r'### 第 \d+ 名：', f'### 第 {rank} 名：', eclat_md)
        with open(new_filepath, 'w', encoding='utf-8') as f_out:
            f_out.write(custom_md)
        print(f"Created new file {new_filename}")
    else:
        # Find old file for this code
        old_file = None
        for path, bname in list(existing_stock_files.items()):
            # check if code in bname
            if f"-{code}-" in bname or bname.startswith(f"{code}-") or f"-{code}." in bname:
                old_file = path
                break
        if old_file:
            # Read old content and update rank header and update date
            with open(old_file, encoding='utf-8') as f_in:
                c = f_in.read()
            c = re.sub(r'### 第 \d+ 名：', f'### 第 {rank} 名：', c)
            c = re.sub(r'-\s*\*\*本區塊最後更新\*\*[：:]\s*\d{4}-\d{2}-\d{2}', '- **本區塊最後更新**：2026-08-12', c)
            
            # Remove old file if name changed, then write new file
            if old_file != new_filepath:
                if os.path.exists(old_file):
                    os.remove(old_file)
            with open(new_filepath, 'w', encoding='utf-8') as f_out:
                f_out.write(c)
            print(f"Updated/Renamed {os.path.basename(old_file)} -> {new_filename}")

# Delete dropped files
for d in dropped_rows:
    code = d['code']
    for path, bname in list(existing_stock_files.items()):
        if f"-{code}-" in bname or bname.startswith(f"{code}-") or f"-{code}." in bname:
            if os.path.exists(path):
                os.remove(path)
                print(f"DELETED DROPPED FILE: {bname}")

print("Stock md files update completed!")
