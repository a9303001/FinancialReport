import glob, os, re, csv

# Check all existing stock md files
files = glob.glob('StkScreenerResult/*.md')
top_files = [f for f in files if not f.endswith('0.StkScreenerResult_gemini.md')]
print(f"Current stock files count: {len(top_files)}")

# Read current 0.StkScreenerResult_gemini.md
with open('StkScreenerResult/0.StkScreenerResult_gemini.md', encoding='utf-8') as f:
    text = f.read()

print("Main file length:", len(text))
