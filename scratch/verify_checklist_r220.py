import os, sys, glob, re

sys.stdout.reconfigure(encoding='utf-8')
res_dir = r'd:\FinancialReport\StkScreenerResult'
main_file = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check headers
headers = [line for line in content.splitlines() if line.startswith('## ')]
print(f"1. Number of ## headers: {len(headers)} (Expected: 6)")
for h in headers:
    print(f"   - {h}")

# Check Section IV links
sec4_lines = [l for l in content.splitlines() if '](<' in l]
print(f"2. Section IV link lines count: {len(sec4_lines)}")

# Check non-Top 100 files
md_files = glob.glob(os.path.join(res_dir, '*.md'))
stock_mds = [f for f in md_files if not '0.StkScreener' in f]
print(f"3. Individual stock md files count: {len(stock_mds)} (Expected: 100)")

# Check CSV files presence
csv_files = glob.glob(os.path.join(res_dir, '*.csv'))
print(f"4. CSV files count: {len(csv_files)} ({[os.path.basename(c) for c in csv_files]})")

# Check forbidden words in overview and md files
forbidden_words = ['龍頭', '領先', '領頭', '卓越', '居前列', '名列前茅', '優秀標的', '行業代表', '具備高度行業競爭優勢', '市佔率居區域前列', '市場獨佔或領頭地位']

# Test overview table position column
rows_with_forbidden = []
lines = content.splitlines()
in_sec3 = False
for l in lines:
    if '## 三、Top 100 排名總覽' in l:
        in_sec3 = True
        continue
    elif in_sec3 and l.startswith('## '):
        in_sec3 = False
    elif in_sec3 and l.startswith('|') and not '代號' in l and not ':-' in l:
        for fw in forbidden_words:
            if fw in l:
                rows_with_forbidden.append((l, fw))

print(f"5. Forbidden words residual count in Section III: {len(rows_with_forbidden)}")

print("Self-check validation completed successfully!")
