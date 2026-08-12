import glob, re

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
        
        updated = False
        # Fix "為什麼能進 Top 50" to "為什麼能進 Top 100"
        if "為什麼能進 Top 50" in text:
            text = text.replace("為什麼能進 Top 50", "為什麼能進 Top 100")
            updated = True
        
        # Verify ⑦ sum
        m_sum = re.search(r'總分驗算.*?[：:]\s*([\d\.\s\+\=]+)', text)
        if m_sum:
            expr_str = m_sum.group(1)
            # e.g. "23.5 + 19.5 + 16.2 + 13.8 + 5.1 = **78.1**"
            m_nums = re.findall(r'(\d+\.\d+)', expr_str)
            if len(m_nums) >= 6:
                sum_parts = [float(x) for x in m_nums[:5]]
                declared_total = float(m_nums[5])
                calc_total = round(sum(sum_parts), 1)
                if abs(calc_total - declared_total) > 0.05:
                    print(f"MISMATCH in {filepath}: parts={sum_parts}, calc={calc_total}, declared={declared_total}")
        
        if updated:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Updated header in {filepath}")

print("TOP 21-40 deep audit completed.")
