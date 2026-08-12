with open('StkScreenerResult/0.StkScreenerResult_gemini.md', encoding='utf-8') as f:
    text = f.read()

sec3 = text.split('## 三、Top 100 排名總覽')[1].split('## 四、個股詳細')[0]
sec4 = text.split('## 四、個股詳細')[1].split('## 五、⚠️ 待查')[0]

sec3_data = [l for l in sec3.splitlines() if l.startswith('|') and l.split('|')[1].strip().isdigit()]
sec4_data = [l for l in sec4.splitlines() if l.startswith('|') and l.split('|')[1].strip().isdigit()]

print("Sec 3 data rows:", len(sec3_data))
print("Sec 4 data rows:", len(sec4_data))
