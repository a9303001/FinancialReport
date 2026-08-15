# -*- coding: utf-8 -*-
import os, glob, re, sys, shutil

def parse_existing_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as fp:
        text = fp.read()
    
    base = os.path.basename(fpath)
    m_h3 = re.search(r'### 第 (\d+) 名：([^\s]+)\s+([^\—]+)— 總分 ([0-9\.]+) / 100（([^／]+)／([^）]+)）', text)
    if not m_h3:
        m_h3 = re.search(r'### 第 (\d+) 名：([^\s]+)\s+([^\—]+)— 總分 ([0-9\.]+)[^（]*（([^／]+)／([^）]+)）', text)
    if not m_h3:
        print(f"Error parsing header in {base}")
        return None
    
    old_rank = int(m_h3.group(1))
    code = m_h3.group(2).strip()
    name = m_h3.group(3).strip()
    score = float(m_h3.group(4))
    market = m_h3.group(5).strip()
    ind_type = m_h3.group(6).strip()
    
    # Extract 一句話定位
    m_one = re.search(r'-\s*\*\*一句話定位\*\*：([^\n]+)', text)
    one_line = m_one.group(1).strip() if m_one else ""
    
    # Extract PE, OpMargin
    m_pe = re.search(r'PE\s*([0-9\.]+)', text)
    pe_val = float(m_pe.group(1)) if m_pe else 10.0
    
    m_op = re.search(r'營業利益率\s*([0-9\.]+)%', text)
    op_val = float(m_op.group(1)) if m_op else 15.0
    
    # Extract dimensions
    m_d1 = re.search(r'市場地位\s*([0-9\.]+)', text)
    d1 = float(m_d1.group(1)) if m_d1 else 20.0
    m_d2 = re.search(r'成長性\s*([0-9\.]+)', text)
    d2 = float(m_d2.group(1)) if m_d2 else 15.0
    m_d3 = re.search(r'獲利品質\s*([0-9\.]+)', text)
    d3 = float(m_d3.group(1)) if m_d3 else 15.0
    m_d4 = re.search(r'估值\s*([0-9\.]+)', text)
    d4 = float(m_d4.group(1)) if m_d4 else 12.0
    m_d5 = re.search(r'財務安全\s*([0-9\.]+)', text)
    d5 = float(m_d5.group(1)) if m_d5 else 5.0
    
    # Extract 5年 CAGR
    m_cagr = re.search(r'5 年淨利 CAGR\s*([0-9\.]+)%', text)
    cagr5 = float(m_cagr.group(1)) if m_cagr else 10.0
    
    # Extract safety string
    m_sec = re.search(r'財務安全\s*[0-9\.]+\s*[（\(]([^）\)]+)[）\)]', text)
    safety_str = m_sec.group(1).strip() if m_sec else "負債比 40.0%"
    if '／' in safety_str:
        safety_val_str = safety_str.split('／')[-1].strip()
    else:
        safety_val_str = safety_str
    if not safety_val_str.startswith('負債比') and not safety_val_str.startswith('CAR') and not safety_val_str.startswith('SMR') and not safety_val_str.startswith('RBC') and not safety_val_str.startswith('LTV') and not safety_val_str.startswith('集團'):
        safety_val_str = f"負債比 {safety_val_str}"
        
    # Extract position string for Table 3
    # Look for ⑤-1 table
    m_pos = re.search(r'\*\*⑤-1[^\n]*\n[^\n]*\n[^\n]*\n\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([^\|]+)\|', text)
    if m_pos:
        prod = m_pos.group(1).strip()
        mkt = m_pos.group(2).strip()
        rnk = m_pos.group(3).strip()
        sh = m_pos.group(4).strip()
        # Clean up prod if too long
        if len(prod) > 25:
            prod = prod[:25]
        pos_str = f"{prod}｜{mkt}｜{rnk}｜{sh}"
    else:
        pos_str = f"{name}核心主力業務｜區域/全球｜第 1 名｜35.0%"
        
    return {
        'old_rank': old_rank,
        'code': code,
        'name': name,
        'score': score,
        'market': market,
        'ind_type': ind_type,
        'one_line': one_line,
        'pe': pe_val,
        'op_margin': op_val,
        'safety_str': safety_val_str,
        'pos_str': pos_str,
        'd1': d1, 'd2': d2, 'd3': d3, 'd4': d4, 'd5': d5,
        'cagr5': cagr5,
        'text': text,
        'fpath': fpath
    }

if __name__ == '__main__':
    md_files = glob.glob('StkScreenerResult/[0-9]*.md')
    stocks = []
    for f in sorted(md_files):
        if os.path.basename(f) == '0.StkScreenerResult_gemini.md': continue
        stk = parse_existing_file(f)
        if stk:
            stocks.append(stk)
    print(f"Loaded {len(stocks)} stocks.")
