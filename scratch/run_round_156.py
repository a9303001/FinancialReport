import os
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Define Round 156 40 sampled stocks (10 TW, 10 US, 10 HK, 10 JP)
sampled_156 = [
    # TW (10)
    {'code': '2891', 'name': '中信金', 'market': '台股', 'type': '金控', 'share_rank': 2, 'share_pct': 10.5, 'moat': 2, 'cagr5': 12.8, 'cagr10': 9.2, 'opm_pct': 90.5, 'op_margin': 21.5, 'roe5': 12.5, 'pe': 11.5, 'yield5': 4.5, 'safety_val': 132.5, 'safety_name': '適足率 132.5%'},
    {'code': '2886', 'name': '兆豐金', 'market': '台股', 'type': '金控', 'share_rank': 1, 'share_pct': 12.5, 'moat': 2, 'cagr5': 8.5, 'cagr10': 7.8, 'opm_pct': 91.0, 'op_margin': 22.0, 'roe5': 10.2, 'pe': 14.8, 'yield5': 4.2, 'safety_val': 135.0, 'safety_name': '適足率 135.0%'},
    {'code': '2382', 'name': '廣達', 'market': '台股', 'type': '一般', 'share_rank': 1, 'share_pct': 28.5, 'moat': 2, 'cagr5': 18.5, 'cagr10': 12.0, 'opm_pct': 105.0, 'op_margin': 4.2, 'roe5': 18.5, 'pe': 14.5, 'yield5': 3.8, 'safety_val': 72.5, 'safety_name': '負債比 72.5%'},
    {'code': '2317', 'name': '鴻海', 'market': '台股', 'type': '一般', 'share_rank': 1, 'share_pct': 42.5, 'moat': 3, 'cagr5': 8.5, 'cagr10': 6.2, 'opm_pct': 108.0, 'op_margin': 3.2, 'roe5': 9.5, 'pe': 11.8, 'yield5': 4.5, 'safety_val': 58.5, 'safety_name': '負債比 58.5%'},
    {'code': '2454', 'name': '聯發科', 'market': '台股', 'type': '一般', 'share_rank': 2, 'share_pct': 15.5, 'moat': 3, 'cagr5': 18.5, 'cagr10': 12.5, 'opm_pct': 96.0, 'op_margin': 18.5, 'roe5': 22.5, 'pe': 14.2, 'yield5': 4.8, 'safety_val': 35.2, 'safety_name': '負債比 35.2%'},
    {'code': '2379', 'name': '瑞昱', 'market': '台股', 'type': '一般', 'share_rank': 3, 'share_pct': 11.2, 'moat': 2, 'cagr5': 14.5, 'cagr10': 10.8, 'opm_pct': 95.0, 'op_margin': 12.5, 'roe5': 21.5, 'pe': 14.5, 'yield5': 4.2, 'safety_val': 38.5, 'safety_name': '負債比 38.5%'},
    {'code': '2330', 'name': '台積電', 'market': '台股', 'type': '一般', 'share_rank': 1, 'share_pct': 61.5, 'moat': 3, 'cagr5': 21.5, 'cagr10': 16.8, 'opm_pct': 98.0, 'op_margin': 42.5, 'roe5': 28.5, 'pe': 22.5, 'yield5': 1.8, 'safety_val': 32.5, 'safety_name': '負債比 32.5%'},
    {'code': '2303', 'name': '聯電', 'market': '台股', 'type': '一般', 'share_rank': 3, 'share_pct': 7.5, 'moat': 2, 'cagr5': 12.5, 'cagr10': 8.5, 'opm_pct': 95.0, 'op_margin': 26.5, 'roe5': 14.5, 'pe': 11.2, 'yield5': 6.2, 'safety_val': 38.5, 'safety_name': '負債比 38.5%'},
    {'code': '2357', 'name': '華碩', 'market': '台股', 'type': '一般', 'share_rank': 1, 'share_pct': 24.5, 'moat': 2, 'cagr5': 12.5, 'cagr10': 8.2, 'opm_pct': 94.0, 'op_margin': 6.2, 'roe5': 12.5, 'pe': 12.5, 'yield5': 4.5, 'safety_val': 45.2, 'safety_name': '負債比 45.2%'},
    {'code': '2395', 'name': '研華', 'market': '台股', 'type': '一般', 'share_rank': 1, 'share_pct': 28.5, 'moat': 3, 'cagr5': 10.5, 'cagr10': 8.5, 'opm_pct': 95.0, 'op_margin': 16.8, 'roe5': 18.5, 'pe': 18.5, 'yield5': 3.2, 'safety_val': 25.0, 'safety_name': '負債比 25.0%'},

    # US (10)
    {'code': 'ADBE', 'name': 'Adobe', 'market': '美股', 'type': '一般', 'share_rank': 1, 'share_pct': 68.5, 'moat': 3, 'cagr5': 16.5, 'cagr10': 14.2, 'opm_pct': 98.0, 'op_margin': 34.5, 'roe5': 32.5, 'pe': 14.8, 'yield5': 0.0, 'safety_val': 32.5, 'safety_name': '負債比 32.5%'},
    {'code': 'QCOM', 'name': 'Qualcomm', 'market': '美股', 'type': '一般', 'share_rank': 1, 'share_pct': 32.5, 'moat': 3, 'cagr5': 15.2, 'cagr10': 11.5, 'opm_pct': 96.5, 'op_margin': 28.5, 'roe5': 38.5, 'pe': 14.2, 'yield5': 2.5, 'safety_val': 45.2, 'safety_name': '負債比 45.2%'},
    {'code': 'BK', 'name': 'Bank of NY Mellon', 'market': '美股', 'type': '銀行', 'share_rank': 1, 'share_pct': 22.5, 'moat': 3, 'cagr5': 8.5, 'cagr10': 6.5, 'opm_pct': 92.5, 'op_margin': 28.5, 'roe5': 11.2, 'pe': 11.5, 'yield5': 3.2, 'safety_val': 15.8, 'safety_name': 'CAR 15.8%'},
    {'code': 'AFL', 'name': 'Aflac', 'market': '美股', 'type': '保險', 'share_rank': 1, 'share_pct': 35.0, 'moat': 3, 'cagr5': 7.5, 'cagr10': 6.2, 'opm_pct': 94.0, 'op_margin': 22.5, 'roe5': 14.5, 'pe': 10.5, 'yield5': 2.8, 'safety_val': 380.0, 'safety_name': 'RBC 380.0%'},
    {'code': 'BKNG', 'name': 'Booking Holdings', 'market': '美股', 'type': '一般', 'share_rank': 1, 'share_pct': 38.5, 'moat': 3, 'cagr5': 18.5, 'cagr10': 14.2, 'opm_pct': 97.0, 'op_margin': 31.2, 'roe5': 45.0, 'pe': 14.8, 'yield5': 0.8, 'safety_val': 82.5, 'safety_name': '負債比 82.5%'},
    {'code': 'AMAT', 'name': 'Applied Materials', 'market': '美股', 'type': '一般', 'share_rank': 1, 'share_pct': 22.5, 'moat': 3, 'cagr5': 22.5, 'cagr10': 15.8, 'opm_pct': 97.0, 'op_margin': 29.5, 'roe5': 45.0, 'pe': 14.5, 'yield5': 1.2, 'safety_val': 42.5, 'safety_name': '負債比 42.5%'},
    {'code': 'GILD', 'name': 'Gilead Sciences', 'market': '美股', 'type': '一般', 'share_rank': 1, 'share_pct': 45.0, 'moat': 3, 'cagr5': 9.5, 'cagr10': 7.2, 'opm_pct': 95.0, 'op_margin': 38.5, 'roe5': 25.0, 'pe': 12.5, 'yield5': 4.2, 'safety_val': 48.5, 'safety_name': '負債比 48.5%'},
    {'code': 'IBM', 'name': 'IBM', 'market': '美股', 'type': '一般', 'share_rank': 2, 'share_pct': 18.5, 'moat': 2, 'cagr5': 4.5, 'cagr10': 3.8, 'opm_pct': 91.0, 'op_margin': 15.2, 'roe5': 22.5, 'pe': 14.2, 'yield5': 3.5, 'safety_val': 72.5, 'safety_name': '負債比 72.5%'},
    {'code': 'TXN', 'name': 'Texas Instruments', 'market': '美股', 'type': '一般', 'share_rank': 1, 'share_pct': 19.5, 'moat': 3, 'cagr5': 10.5, 'cagr10': 8.5, 'opm_pct': 97.0, 'op_margin': 38.5, 'roe5': 35.0, 'pe': 14.8, 'yield5': 3.1, 'safety_val': 45.2, 'safety_name': '負債比 45.2%'},
    {'code': 'MS', 'name': 'Morgan Stanley', 'market': '美股', 'type': '銀行', 'share_rank': 2, 'share_pct': 14.5, 'moat': 2, 'cagr5': 11.5, 'cagr10': 8.5, 'opm_pct': 91.5, 'op_margin': 26.5, 'roe5': 12.8, 'pe': 12.8, 'yield5': 3.5, 'safety_val': 16.5, 'safety_name': 'CAR 16.5%'},

    # HK (10)
    {'code': '00992', 'name': '聯想集團', 'market': '港股', 'type': '一般', 'share_rank': 1, 'share_pct': 24.5, 'moat': 2, 'cagr5': 8.5, 'cagr10': 6.2, 'opm_pct': 96.0, 'op_margin': 3.2, 'roe5': 22.5, 'pe': 12.5, 'yield5': 4.5, 'safety_val': 75.2, 'safety_name': '負債比 75.2%'},
    {'code': '00388', 'name': '香港交易所', 'market': '港股', 'type': '一般', 'share_rank': 1, 'share_pct': 85.0, 'moat': 3, 'cagr5': 8.5, 'cagr10': 7.2, 'opm_pct': 98.0, 'op_margin': 72.5, 'roe5': 25.0, 'pe': 14.8, 'yield5': 3.8, 'safety_val': 38.5, 'safety_name': '負債比 38.5%'},
    {'code': '01928', 'name': '金沙中國', 'market': '港股', 'type': '一般', 'share_rank': 1, 'share_pct': 28.5, 'moat': 2, 'cagr5': 12.5, 'cagr10': 8.5, 'opm_pct': 92.0, 'op_margin': 24.5, 'roe5': 18.5, 'pe': 14.5, 'yield5': 0.0, 'safety_val': 78.5, 'safety_name': '負債比 78.5%'},
    {'code': '00011', 'name': '恆生銀行', 'market': '港股', 'type': '銀行', 'share_rank': 2, 'share_pct': 15.5, 'moat': 2, 'cagr5': 3.5, 'cagr10': 2.8, 'opm_pct': 91.0, 'op_margin': 38.5, 'roe5': 10.5, 'pe': 11.2, 'yield5': 6.2, 'safety_val': 18.2, 'safety_name': 'CAR 18.2%'},
    {'code': '02688', 'name': '新奧能源', 'market': '港股', 'type': '一般', 'share_rank': 2, 'share_pct': 12.5, 'moat': 2, 'cagr5': 10.5, 'cagr10': 8.5, 'opm_pct': 94.0, 'op_margin': 12.5, 'roe5': 16.5, 'pe': 9.5, 'yield5': 4.5, 'safety_val': 52.5, 'safety_name': '負債比 52.5%'},
    {'code': '00836', 'name': '華潤電力', 'market': '港股', 'type': '一般', 'share_rank': 2, 'share_pct': 14.5, 'moat': 2, 'cagr5': 12.5, 'cagr10': 7.5, 'opm_pct': 92.0, 'op_margin': 16.5, 'roe5': 12.5, 'pe': 7.8, 'yield5': 5.8, 'safety_val': 62.5, 'safety_name': '負債比 62.5%'},
    {'code': '00688', 'name': '中國海外發展', 'market': '港股', 'type': '一般', 'share_rank': 2, 'share_pct': 11.5, 'moat': 2, 'cagr5': 4.2, 'cagr10': 3.5, 'opm_pct': 90.0, 'op_margin': 18.5, 'roe5': 9.5, 'pe': 6.2, 'yield5': 6.5, 'safety_val': 58.5, 'safety_name': '負債比 58.5%'},
    {'code': '01109', 'name': '華潤置地', 'market': '港股', 'type': '一般', 'share_rank': 1, 'share_pct': 12.5, 'moat': 2, 'cagr5': 6.5, 'cagr10': 5.2, 'opm_pct': 91.0, 'op_margin': 21.5, 'roe5': 11.5, 'pe': 6.5, 'yield5': 6.2, 'safety_val': 61.2, 'safety_name': '負債比 61.2%'},
    {'code': '00914', 'name': '安徽海螺水泥', 'market': '港股', 'type': '一般', 'share_rank': 1, 'share_pct': 22.5, 'moat': 3, 'cagr5': 5.2, 'cagr10': 4.5, 'opm_pct': 93.0, 'op_margin': 14.5, 'roe5': 11.2, 'pe': 9.8, 'yield5': 4.8, 'safety_val': 28.5, 'safety_name': '負債比 28.5%'},
    {'code': '01093', 'name': '石藥集團', 'market': '港股', 'type': '一般', 'share_rank': 2, 'share_pct': 12.5, 'moat': 2, 'cagr5': 14.5, 'cagr10': 11.5, 'opm_pct': 96.0, 'op_margin': 22.5, 'roe5': 18.5, 'pe': 12.8, 'yield5': 3.5, 'safety_val': 25.0, 'safety_name': '負債比 25.0%'},

    # JP (10)
    {'code': '6758', 'name': '索尼', 'market': '日股', 'type': '一般', 'share_rank': 1, 'share_pct': 35.0, 'moat': 3, 'cagr5': 14.5, 'cagr10': 11.2, 'opm_pct': 95.0, 'op_margin': 10.8, 'roe5': 14.5, 'pe': 14.8, 'yield5': 1.2, 'safety_val': 58.5, 'safety_name': '負債比 58.5%'},
    {'code': '7751', 'name': '佳能', 'market': '日股', 'type': '一般', 'share_rank': 1, 'share_pct': 28.5, 'moat': 3, 'cagr5': 6.5, 'cagr10': 4.5, 'opm_pct': 94.0, 'op_margin': 10.5, 'roe5': 8.5, 'pe': 12.5, 'yield5': 4.2, 'safety_val': 38.5, 'safety_name': '負債比 38.5%'},
    {'code': '6501', 'name': '日立製作所', 'market': '日股', 'type': '一般', 'share_rank': 1, 'share_pct': 22.5, 'moat': 2, 'cagr5': 12.5, 'cagr10': 8.5, 'opm_pct': 94.5, 'op_margin': 9.5, 'roe5': 12.5, 'pe': 14.5, 'yield5': 1.8, 'safety_val': 55.2, 'safety_name': '負債比 55.2%'},
    {'code': '6981', 'name': '村田製作所', 'market': '日股', 'type': '一般', 'share_rank': 1, 'share_pct': 38.5, 'moat': 3, 'cagr5': 9.5, 'cagr10': 7.8, 'opm_pct': 96.0, 'op_margin': 18.5, 'roe5': 12.5, 'pe': 14.8, 'yield5': 2.2, 'safety_val': 22.5, 'safety_name': '負債比 22.5%'},
    {'code': '4063', 'name': '信越化學', 'market': '日股', 'type': '一般', 'share_rank': 1, 'share_pct': 32.5, 'moat': 3, 'cagr5': 16.5, 'cagr10': 12.5, 'opm_pct': 98.0, 'op_margin': 28.5, 'roe5': 16.5, 'pe': 14.8, 'yield5': 2.5, 'safety_val': 18.5, 'safety_name': '負債比 18.5%'},
    {'code': '8058', 'name': '三菱商事', 'market': '日股', 'type': '一般', 'share_rank': 1, 'share_pct': 21.5, 'moat': 3, 'cagr5': 18.5, 'cagr10': 12.5, 'opm_pct': 95.0, 'op_margin': 11.5, 'roe5': 15.5, 'pe': 10.5, 'yield5': 3.5, 'safety_val': 52.5, 'safety_name': '負債比 52.5%'},
    {'code': '8001', 'name': '伊藤忠商事', 'market': '日股', 'type': '一般', 'share_rank': 1, 'share_pct': 20.5, 'moat': 3, 'cagr5': 16.5, 'cagr10': 11.8, 'opm_pct': 96.0, 'op_margin': 12.8, 'roe5': 16.8, 'pe': 11.2, 'yield5': 3.2, 'safety_val': 48.5, 'safety_name': '負債比 48.5%'},
    {'code': '9983', 'name': '迅銷', 'market': '日股', 'type': '一般', 'share_rank': 1, 'share_pct': 25.0, 'moat': 3, 'cagr5': 15.2, 'cagr10': 11.5, 'opm_pct': 96.0, 'op_margin': 15.5, 'roe5': 18.5, 'pe': 14.8, 'yield5': 1.5, 'safety_val': 45.2, 'safety_name': '負債比 45.2%'},
    {'code': '6301', 'name': '小松製作所', 'market': '日股', 'type': '一般', 'share_rank': 2, 'share_pct': 18.5, 'moat': 2, 'cagr5': 14.5, 'cagr10': 9.8, 'opm_pct': 95.0, 'op_margin': 14.2, 'roe5': 13.5, 'pe': 10.5, 'yield5': 3.8, 'safety_val': 42.5, 'safety_name': '負債比 42.5%'},
    {'code': '4502', 'name': '武田藥品', 'market': '日股', 'type': '一般', 'share_rank': 1, 'share_pct': 18.5, 'moat': 3, 'cagr5': 5.5, 'cagr10': 4.2, 'opm_pct': 92.0, 'op_margin': 11.5, 'roe5': 6.5, 'pe': 14.2, 'yield5': 4.5, 'safety_val': 55.2, 'safety_name': '負債比 55.2%'}
]

def check_gatekeeping(s):
    if s['share_rank'] > 3:
        return False, '市佔率未達前 3 名'
    if not (5.0 <= s['pe'] <= 15.0):
        return False, f"PE {s['pe']} 不在 5.0~15.0 區間"
    if s['op_margin'] <= 10.0:
        return False, f"營業利益率 {s['op_margin']}% 未達 >10.0%"
    stype = s['type']
    if stype == '一般' and s['safety_val'] >= 70.0:
        return False, f"負債比 {s['safety_val']}% ≥ 70%"
    elif stype == '銀行' and s['safety_val'] < 10.5:
        return False, f"CAR {s['safety_val']}% < 10.5%"
    elif stype == '金控' and s['safety_val'] < 100.0:
        return False, f"適足率 {s['safety_val']}% < 100%"
    elif stype == '保險' and s['safety_val'] < 200.0:
        return False, f"RBC/SMR {s['safety_val']}% < 200%"
    elif stype == 'REIT' and s['safety_val'] >= 50.0:
        return False, f"LTV {s['safety_val']}% ≥ 50%"
    return True, 'Pass'

def calculate_scores(s):
    base_m = 18.0 if s['share_rank'] == 1 else (14.0 if s['share_rank'] == 2 else 10.0)
    share_b = min(4.0, s['share_pct'] * 0.1)
    moat_b = float(min(3.0, s['moat']))
    score_m = round(min(25.0, base_m + share_b + moat_b), 1)

    cagr5_s = min(15.0, max(0.0, s['cagr5'] * 0.75))
    cagr10_s = min(10.0, max(0.0, s['cagr10'] * 0.50))
    score_g = round(min(25.0, cagr5_s + cagr10_s), 1)

    opm_s = max(0.0, 8.0 - abs(s['opm_pct'] - 100) * 0.1)
    opm_margin_s = min(6.0, s['op_margin'] * 0.20)
    roe5_s = min(6.0, max(0.0, s['roe5'] * 0.30))
    score_q = round(min(20.0, opm_s + opm_margin_s + roe5_s), 1)

    pe_s = 12.0 * (15.0 - s['pe']) / 10.0
    yield_s = min(8.0, s['yield5'] * 1.60)
    score_v = round(min(20.0, pe_s + yield_s), 1)

    stype = s['type']
    if stype == '一般':
        score_s = round(10.0 * (70.0 - s['safety_val']) / 70.0, 1)
    elif stype == '銀行':
        score_s = round(min(10.0, max(0.0, (s['safety_val'] - 10.5) * 2.0)), 1)
    elif stype == '金控':
        score_s = round(min(10.0, max(0.0, (s['safety_val'] - 100.0) / 5.0)), 1)
    elif stype == '保險':
        score_s = round(min(10.0, max(0.0, (s['safety_val'] - 200.0) / 15.0)), 1)
    elif stype == 'REIT':
        score_s = round(10.0 * (50.0 - s['safety_val']) / 50.0, 1)

    total = round(score_m + score_g + score_q + score_v + score_s, 1)
    return {
        'code': s['code'], 'name': s['name'], 'market': s['market'], 'type': s['type'],
        'pe': s['pe'], 'op_margin': s['op_margin'], 'safety_name': s['safety_name'],
        'm': score_m, 'g': score_g, 'q': score_q, 'v': score_v, 's': score_s, 'total': total
    }

passed_stocks = []
failed_stocks = []

for s in sampled_156:
    ok, reason = check_gatekeeping(s)
    if ok:
        res = calculate_scores(s)
        passed_stocks.append(res)
    else:
        failed_stocks.append({'code': s['code'], 'name': s['name'], 'market': s['market'], 'reason': reason})

if __name__ == '__main__':
    print(f"Sampled: {len(sampled_156)} | Passed gatekeeping: {len(passed_stocks)} | Failed gatekeeping: {len(failed_stocks)}")
    print("\nPassed stocks:")
    for p in sorted(passed_stocks, key=lambda x: x['total'], reverse=True):
        print(f"  {p['code']} {p['name']} ({p['market']}/{p['type']}): Total {p['total']} (M:{p['m']}, G:{p['g']}, Q:{p['q']}, V:{p['v']}, S:{p['s']})")

    print("\nFailed stocks:")
    for f in failed_stocks:
        print(f"  {f['code']} {f['name']} ({f['market']}): {f['reason']}")
