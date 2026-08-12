import sys, os, re

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'
main_md_path = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Parse Section 3 rows
sec3_match = re.search(r'## 三、Top 100 排名總覽.*?\n(\|.*?\n)+', text, re.DOTALL)
if not sec3_match:
    print("Section 3 not found!")
    sys.exit(1)

sec3_text = sec3_match.group(0)
lines = [l.strip() for l in sec3_text.split('\n') if l.strip().startswith('|')]

sec4_rows = []
sec4_header = """## 四、個股詳細
> 本區塊按排名順序收錄 Top 100 的個股分析檔連結與摘要。完整分析內容個別儲存於 `StkScreenerResult\\<排名>-<代號>-<公司>.md`。
> 🔴 **連結寫法（兩條都要遵守）**：
> ① 用**同目錄相對路徑（只寫檔名）**。主結果檔本身就在 `StkScreenerResult\\` 內，加 `StkScreenerResult/` 前綴會變成雙層目錄而失效；也不可用 `file:///d:/...` 絕對路徑。
> ② 目標一律用**角括號包起來** `](<檔名.md>)`。很多檔名含空格或括號（如 `15-TRV-The Travelers.md`、`05-01308-海豐國際 (SITC International).md`），不包角括號的 Markdown 連結會斷掉。

| 排名 | 代號 公司 | 分析檔案連結 | 總分 | 一句話定位 | 本區塊最後更新 |
| :-: | :--- | :--- | :-: | :--- | :--- |"""

sec4_lines = [sec4_header]

for l in lines[2:]:
    cols = [c.strip() for c in l.split('|')[1:-1]]
    if len(cols) < 12 or not cols[0].isdigit():
        continue
    rank = int(cols[0])
    code = cols[1]
    name = cols[2]
    total_score = cols[11]
    
    prefix = f"{rank:02d}-" if rank < 100 else f"{rank:03d}-"
    matches = [f for f in os.listdir(res_dir) if f.startswith(prefix) and f.endswith('.md')]
    if not matches:
        # fallback search
        matches = [f for f in os.listdir(res_dir) if f.endswith('.md') and code in f and not f.startswith('0.')]
    
    if not matches:
        print(f"Missing file for Rank {rank} [{code}] {name}")
        continue
    
    filename = matches[0]
    filepath = os.path.join(res_dir, filename)
    
    one_liner = ""
    update_date = "2026-08-12"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        file_lines = f.readlines()
    
    for fl in file_lines:
        if '- **一句話定位**：' in fl:
            one_liner = fl.split('- **一句話定位**：')[1].strip()
        elif '- **本區塊最後更新**：' in fl:
            update_date = fl.split('- **本區塊最後更新**：')[1].strip()
    
    if not one_liner:
        one_liner = f"{name} ({code}) 個股分析說明"
    
    # clean newlines in one_liner
    one_liner = one_liner.replace('\n', ' ').replace('\r', '').replace('|', '｜')
    
    row_str = f"| {rank} | {code} {name} | [{filename}](<{filename}>) | {total_score} | {one_liner} | {update_date} |"
    sec4_lines.append(row_str)

sec4_new = '\n'.join(sec4_lines)

# Replace Section 4 in main_md
text = re.sub(r'## 四、個股詳細.*?(?=## 五、)', sec4_new + '\n\n', text, flags=re.DOTALL)

with open(main_md_path, 'w', encoding='utf-8') as f:
    f.write(text)

print(f"Rebuilt Section 4 with {len(sec4_lines)-1} rows successfully!")
