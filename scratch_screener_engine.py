# -*- coding: utf-8 -*-
import os, glob, re, sys, shutil

def parse_stock_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    base = os.path.basename(fpath)
    m_head = re.search(r'### 第 (\d+) 名：([^\s]+)\s+([^\—]+)— 總分 ([0-9\.]+) / 100（([^／]+)／([^）]+)）', text)
    if not m_head:
        m_head = re.search(r'### 第 (\d+) 名：([^\s]+)\s+([^\—]+)— 總分 ([0-9\.]+)[^（]*（([^／]+)／([^）]+)）', text)
    if not m_head:
        print(f'Failed to parse header in {base}')
        return None
    
    rank = int(m_head.group(1))
    code = m_head.group(2).strip()
    name = m_head.group(3).strip()
    score = float(m_head.group(4))
    market = m_head.group(5).strip()
    ind_type = m_head.group(6).strip()
    
    # Extract 一句話定位
    m_one = re.search(r'- \*\*一句話定位\*\*：([^
]+)', text)
    one_line = m_one.group(1).strip() if m_one else ''
    
    # Extract metrics from table / text
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
    
    return {
        'old_rank': rank,
        'code': code,
        'name': name,
        'score': score,
        'market': market,
        'ind_type': ind_type,
        'one_line': one_line,
        'pe': pe_val,
        'op_margin': op_val,
        'd1': d1, 'd2': d2, 'd3': d3, 'd4': d4, 'd5': d5,
        'cagr5': cagr5,
        'text': text,
        'fpath': fpath
    }

print('Parser function defined.')
