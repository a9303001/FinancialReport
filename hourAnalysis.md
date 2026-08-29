/goal
使用latest claude OPUS model 


# 個股分析1
<OUTPUT_FILENAME>` : hourAnalysisResult.md
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
- `COMPANY_NAME`：03606 福耀玻璃（中股: 600660 福耀玻璃）
- `MARKET`：港股/中股
- `COMPANY_FOLDER`：03606福耀玻璃
- `EXTRA_ANALYSIS`：
  1. 未來5年產能規畫，對eps影響
  2. AI 自駕車對玻璃需求影響?對eps影響?
  3. 電動車對玻璃需求影響?對eps影響?
  4. 所有數據要每股化


---
# 個股分析2
<OUTPUT_FILENAME>` : hourAnalysisResult.md
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
- `COMPANY_NAME`：4979 OAT
- `MARKET`：日股
- `COMPANY_FOLDER`：4979OAT
- `EXTRA_ANALYSIS`：
各產品市占率?
各產品各提供 多少eps
競爭對手
國際和日本市占率
產品銷往哪些國家?比重?
綠色商品是指什麼?
有什麼投資風險嗎？