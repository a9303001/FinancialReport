import os, glob, re, sys
sys.stdout.reconfigure(encoding='utf-8')

res_dir = r'd:\FinancialReport\StkScreenerResult'
main_file = os.path.join(res_dir, '0.StkScreenerResult_gemini.md')

with open(main_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Check 6 ## section headers
h2_headers = re.findall(r'^##\s+(.*)', content, re.MULTILINE)
print("H2 headers count:", len(h2_headers))
print("H2 headers:", h2_headers)

# 2. Check individual files
md_files = glob.glob(os.path.join(res_dir, '*.md'))
top100_mds = [f for f in md_files if not os.path.basename(f).startswith('0.StkScreenerResult')]

print("Total Top 100 md files:", len(top100_mds))

# Check link format in Section IV
sec4_links = re.findall(r'\[(.*?)\]\(\<(.*?)\>\)', content)
print("Section 4 link count:", len(sec4_links))

# Check forbidden words
forbidden_words = ['龍頭', '領先', '領頭', '卓越', '居前列', '名列前茅', '優秀標的', '行業代表', '具備高度行業競爭優勢', '市佔率居區域前列', '市場獨佔或領頭地位']

found_forbidden = []
for fpath in top100_mds:
    with open(fpath, 'r', encoding='utf-8') as f:
        txt = f.read()
    for w in forbidden_words:
        # Check if forbidden word is used without detailed named stats following
        if w in txt:
            found_forbidden.append((os.path.basename(fpath), w))

print("Forbidden words standalone audit count:", len(found_forbidden))
