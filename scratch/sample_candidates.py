import csv, os, glob, re

# Load current Top 100 codes
with open('StkScreenerResult/0.StkScreenerResult_gemini.md', encoding='utf-8') as f:
    main_text = f.read()

top100_codes = set()
for l in main_text.splitlines():
    if l.startswith('|') and len(l.split('|')) >= 12:
        parts = [p.strip() for p in l.split('|')[1:-1]]
        if parts[0].isdigit():
            top100_codes.add(parts[1])

print(f"Loaded {len(top100_codes)} Top 100 stock codes.")

def inspect_csv(filename):
    filepath = os.path.join('StkScreenerResult', filename)
    with open(filepath, encoding='utf-8', errors='ignore') as f:
        reader = list(csv.reader(f))
    header = reader[0]
    rows = reader[1:]
    print(f"\n--- {filename} ({len(rows)} rows) ---")
    print("Header:", header[:8])
    for r in rows[:10]:
        print("  ", r[:6])

inspect_csv('TW.csv')
inspect_csv('US.csv')
inspect_csv('hk.csv')
inspect_csv('jp.csv')
