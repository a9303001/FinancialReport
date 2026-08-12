import re, glob, os

files = glob.glob("StkScreenerResult/*.md")
for rank in range(21, 41):
    pattern = f"StkScreenerResult/{rank:02d}-*.md"
    matches = glob.glob(pattern)
    if not matches:
        pattern = f"StkScreenerResult/{rank}-*.md"
        matches = glob.glob(pattern)
    if matches:
        filepath = matches[0]
        with open(filepath, encoding='utf-8') as f:
            text = f.read()
        # Find block ⑦ or scores
        # e.g. 市場地位 XX.X ... 總分驗算: XX.X + XX.X + XX.X + XX.X + XX.X = XX.X
        m_calc = re.search(r'總分驗算[：:]\s*([\d\.\s\+\=]+)', text)
        if m_calc:
            expr = m_calc.group(1).strip()
            # print(f"Rank {rank} ({os.path.basename(filepath)}): {expr}")
        else:
            print(f"Rank {rank} ({os.path.basename(filepath)}): missing ⑦ 總分驗算")
