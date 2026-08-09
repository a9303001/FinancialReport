import datetime

file_path = r'd:\FinancialReport\StkScreenerResult\0.StkScreenerResult_gemini.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update date
now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
content = content.replace('更新日期：2026-08-10 01:59:00', f'更新日期：{now_str}')

# Update Summary
content = content.replace('完成第一百九十輪', '完成第一百九十一輪')
content = content.replace('新入榜 6 檔｜落榜 6 檔｜修正 0 處', '新入榜 0 檔｜落榜 0 檔｜修正 0 處')
content = content.replace('本輪完成 TOP 21~40', '本輪完成 TOP 41~60')
content = content.replace('第 2 / 5 輪循環', '第 3 / 5 輪循環')

# Add new log entry
log_header = """| :-: | :-- | :-- | :-- | :-- | :-- | :-- |
"""

new_log = f"""| 191 | TOP 41~60 稽核與 Round 191 動態替換 | 完成 TOP 41~60 共 20 檔全鏈算術與 md 內容對比驗算（無計算錯誤）；20 檔新抽樣標的 (台5/美5/港5/日5) 全數通過 5 < PE < 15，本輪無新標的超越 Top 100 門檻 (71.2分) | Top 100 門檻維持 71.2分，100 檔 100% 保持獨立 md 分析檔案 | 官方財報與交易所數據 | {datetime.datetime.now().strftime('%Y-%m-%d')} | {datetime.datetime.now().strftime('%Y-%m-%d')} |
"""

# Replace in file (keep only top 5)
parts = content.split('## 二、修正紀錄 (Self-Fix Log) (僅保留最新 5 筆)')
if len(parts) == 2:
    lines = parts[1].split('\n')
    for i, line in enumerate(lines):
        if line.startswith('| 190 |'):
            # Found the first data row
            # We insert the new_log before it, and remove the last row (which should be 186)
            table_lines = [l for l in lines[i:] if l.strip().startswith('|')]
            if len(table_lines) == 5:
                table_lines.pop() # remove last
            
            new_table = new_log + '\n'.join(table_lines)
            parts[1] = '\n'.join(lines[:i]) + '\n' + new_table + '\n' + '\n'.join(lines[i + len(table_lines) + 1:])
            break
    
    content = parts[0] + '## 二、修正紀錄 (Self-Fix Log) (僅保留最新 5 筆)' + parts[1]

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated 0.StkScreenerResult_gemini.md")
