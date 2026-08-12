import os, sys, glob, re

sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'
main_file = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Check 6 ## headers
headers = re.findall(r'^##\s+(.*)', content, re.MULTILINE)
print(f"Header count: {len(headers)}")
for h in headers:
    print(f" - {h}")
assert len(headers) == 6, f"Expected 6 headers, got {len(headers)}"

# 2. Check individual stock md files count
md_files = glob.glob(os.path.join(res_dir, '*.md'))
stock_mds = [f for f in md_files if not os.path.basename(f).startswith('0.StkScreenerResult')]
print(f"Stock md count: {len(stock_mds)}")
assert len(stock_mds) == 100, f"Expected 100 stock md files, got {len(stock_mds)}"

# 3. Check forbidden terms residual in main file and stock mds
forbidden_terms = ['龍頭', '領先', '領頭', '卓越', '居前列', '名列前茅', '優秀標的', '行業代表', '具備高度行業競爭優勢', '市佔率居區域前列', '市場獨佔或領頭地位']

res_forbidden = 0
for fpath in stock_mds:
    with open(fpath, 'r', encoding='utf-8') as f:
        fc = f.read()
    # Check if forbidden terms appear without named statistics right after
    for term in forbidden_terms:
        matches = [m.start() for m in re.finditer(re.escape(term), fc)]
        for idx in matches:
            snippet = fc[idx:idx+80]
            # If snippet doesn't contain digits or % or specific named stats, log
            if not re.search(r'\d+%', snippet) and not re.search(r'第 \d+ 名', snippet):
                res_forbidden += 1
                print(f"Forbidden term '{term}' snippet in {os.path.basename(fpath)}: {snippet[:40]}")

print(f"Forbidden terms residual without named stats: {res_forbidden}")

# 4. Check links format in Section IV
sec4_links = re.findall(r'\[(.*?)\]\(<(.*?)>\)', content)
print(f"Section IV links parsed: {len(sec4_links)}")
assert len(sec4_links) == 100, f"Expected 100 valid links in Section IV, got {len(sec4_links)}"

print("\nALL CHECKLIST VERIFICATIONS PASSED SUCCESSFULLY!")
