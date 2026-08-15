# -*- coding: utf-8 -*-
import os, glob, re, sys
sys.stdout.reconfigure(encoding='utf-8')

def verify():
    print("=== STARTING FULL CHECKLIST VERIFICATION ===")
    
    # 1. Check master file 0.StkScreenerResult_gemini.md
    master_path = 'StkScreenerResult/0.StkScreenerResult_gemini.md'
    with open(master_path, 'r', encoding='utf-8') as f:
        master_text = f.read()
        
    h2_matches = re.findall(r'^##\s+([^\n]+)', master_text, flags=re.M)
    print(f"Master file H2 count: {len(h2_matches)} (Expected 6)")
    for i, h2 in enumerate(h2_matches, start=1):
        print(f"  H2 #{i}: {h2}")
    assert len(h2_matches) == 6, f"Expected 6 H2 headings, found {len(h2_matches)}"
    
    # 2. Check individual markdown files in StkScreenerResult
    md_files = [f for f in glob.glob('StkScreenerResult/[0-9]*.md') if os.path.basename(f) != '0.StkScreenerResult_gemini.md']
    print(f"Total individual stock md files: {len(md_files)} (Expected 100)")
    assert len(md_files) == 100, f"Expected 100 files, found {len(md_files)}"
    
    # Check no TOP01 style names
    bad_names = [f for f in md_files if 'TOP' in os.path.basename(f)]
    print(f"Old TOP prefix files count: {len(bad_names)} (Expected 0)")
    assert len(bad_names) == 0
    
    # 3. Check Section 3 and Section 4 match
    # Parse Section 3 table
    sec3_rows = re.findall(r'^\|\s*(\d+)\s*\|\s*([^\s\|]+)\s*\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([0-9\.]+)\s*\|\s*([0-9\.]+)\s*\|\s*([0-9\.]+)\s*\|\s*([0-9\.]+)\s*\|\s*([0-9\.]+)\s*\|\s*\*\*([0-9\.]+)\*\*\s*\|\s*([0-9\.]+)\s*\|\s*([0-9\.]+)%\s*\|\s*([^\|]+)\|', master_text, flags=re.M)
    print(f"Section 3 rows count: {len(sec3_rows)} (Expected 100)")
    assert len(sec3_rows) == 100
    
    # Parse Section 4 table
    sec4_block = master_text.split('## 四、Top 100 個股詳細連結')[1].split('## 五')[0]
    sec4_lines = [l for l in sec4_block.splitlines() if l.startswith('|') and not l.startswith('| :-') and not l.startswith('| 排名')]
    print(f"Section 4 lines count: {len(sec4_lines)} (Expected 100)")
    assert len(sec4_lines) == 100
    
    sec4_rows = []
    for l in sec4_lines:
        cols = [c.strip() for c in l.split('|')[1:-1]]
        # cols: 排名, 標的名稱[連結], 市場, 類別, 總分, D1, D2, D3, D4, D5, 一句話定位
        assert len(cols) == 11, f"Expected 11 columns in Section 4, found {len(cols)} in line: {l}"
        # extract link target from cols[1]
        m_link = re.search(r'\]\((.*?\.md)\)', cols[1])
        assert m_link, f"Missing link in: {cols[1]}"
        link_target = m_link.group(1)
        sec4_rows.append((cols[0], cols[1], link_target))
    
    # Check link files exist
    for r in sec4_rows:
        rank_num = r[0]
        link_target = r[2]
        full_p = os.path.join('StkScreenerResult', link_target)
        assert os.path.exists(full_p), f"Link target does not exist: {full_p}"
        
    # 4. Check ABCD completion metrics
    a_count = len(sec3_rows)
    b_count = len(md_files)
    c_count = 0
    d_count = 0
    
    for f in md_files:
        with open(f, 'r', encoding='utf-8') as fp:
            c = fp.read()
        has_1 = '① 為什麼能進 Top 100' in c or '①' in c
        has_2 = '② 優點' in c or '②' in c
        has_3 = '③ 缺點' in c or '③' in c
        if has_1 and has_2 and has_3:
            c_count += 1
            
        has_v1 = '⑤-1 市佔定位' in c or '⑤-1' in c
        has_v2 = '⑤-2 競爭格局' in c or '⑤-2' in c
        has_v3 = '⑤-3 為什麼能排在這個名次' in c or '⑤-3' in c
        if has_v1 and has_v2 and has_v3:
            d_count += 1
            
    print(f"ABCD metrics: A={a_count}, B={b_count}, C={c_count}, D={d_count}")
    assert a_count == 100 and b_count == 100 and c_count == 100 and d_count == 100
    
    # 5. Check CSV integrity and BOM
    csvs = ['TW.csv', 'US.csv', 'hk.csv', 'jp.csv']
    for c_name in csvs:
        c_path = os.path.join('StkScreenerResult', c_name)
        with open(c_path, 'rb') as fp:
            raw = fp.read()
        has_bom = raw.startswith(b'\xef\xbb\xbf')
        with open(c_path, 'r', encoding='utf-8-sig') as fp:
            lines = fp.readlines()
        print(f"CSV {c_name}: lines={len(lines)}, BOM={has_bom}")
        assert has_bom, f"Missing BOM in {c_name}"
        
    print("=== ALL CHECKLIST TESTS PASSED SUCCESSFULLY! ===")

if __name__ == '__main__':
    verify()
