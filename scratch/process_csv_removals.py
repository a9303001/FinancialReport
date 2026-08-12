import csv, sys, os
sys.stdout.reconfigure(encoding='utf-8')

# Remove 2109, 1108 from TW.csv
tw_path = 'StkScreenerResult/TW.csv'
with open(tw_path, encoding='utf-8-sig') as f:
    tw_rows = list(csv.reader(f))

tw_header = tw_rows[0]
tw_data = tw_rows[1:]
tw_remove_codes = {'2109', '1108'}

new_tw_data = [r for r in tw_data if r[0] not in tw_remove_codes]
print(f"TW.csv: before={len(tw_data)}, after={len(new_tw_data)}, removed={len(tw_data)-len(new_tw_data)}")

with open(tw_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(tw_header)
    writer.writerows(new_tw_data)

# Remove ADRs from US.csv
us_path = 'StkScreenerResult/US.csv'
with open(us_path, encoding='utf-8-sig') as f:
    us_rows = list(csv.reader(f))

us_header = us_rows[0]
us_data = us_rows[1:]
us_remove_codes = {'PHI', 'TIMB', 'TLK', 'RYAAY', 'DRD', 'GFI', 'HMY', 'UL'}

new_us_data = [r for r in us_data if r[0] not in us_remove_codes]
print(f"US.csv: before={len(us_data)}, after={len(new_us_data)}, removed={len(us_data)-len(new_us_data)}")

with open(us_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(us_header)
    writer.writerows(new_us_data)
