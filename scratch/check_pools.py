import os
import sys
import glob
import re

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

dir_path = r'd:\FinancialReport\StkScreenerResult'
main_file = os.path.join(dir_path, '0.StkScreenerResult_gemini.md')

with open(main_file, 'r', encoding='utf-8') as f:
    main_text = f.read()

# Get existing Top 100 codes
top100_codes = set(re.findall(r'^\| \d+ \| ([^|]+) \|', main_text, re.MULTILINE))
top100_codes = {c.strip() for c in top100_codes}
print('Top 100 count:', len(top100_codes))

csv_files = {
    'TW': os.path.join(dir_path, 'TW.csv'),
    'US': os.path.join(dir_path, 'US.csv'),
    'HK': os.path.join(dir_path, 'hk.csv'),
    'JP': os.path.join(dir_path, 'jp.csv'),
}

for mkt, cpath in csv_files.items():
    with open(cpath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    header = lines[0]
    data_lines = lines[1:]
    print(f'=== {mkt} csv ({os.path.basename(cpath)}): total rows = {len(data_lines)} ===')
    in_top100 = 0
    not_in_top100 = 0
    in_top100_list = []
    not_in_top100_list = []
    for line in data_lines:
        code = line.split(',')[0].strip('"\'' )
        if code in top100_codes:
            in_top100 += 1
            in_top100_list.append(code)
        else:
            not_in_top100 += 1
            not_in_top100_list.append(code)
    print(f'  In Top 100: {in_top100}, Not in Top 100: {not_in_top100}')
    print(f'  First 5 in Top 100: {in_top100_list[:5]}')
    print(f'  First 5 not in Top 100: {not_in_top100_list[:5]}')
