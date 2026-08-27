/goal
使用latest claude OPUS model 


# 個股分析1
><OUTPUT_FILENAME>` : hourAnalysisResult.md
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
- `COMPANY_NAME`：03606 福耀玻璃（中股: 600660 福耀玻璃）
- `MARKET`：港股/中股
- `COMPANY_FOLDER`：03606福耀玻璃
- `EXTRA_ANALYSIS`：
  1. 未來5年產能規畫，對eps影響
  2. AI 自駕車對玻璃需求影響?對eps影響?
  3. 電動車對玻璃需求影響?對eps影響?
  4. 所有數據要港幣每股化


---
# 個股分析2
><OUTPUT_FILENAME>` : hourAnalysisResult.md
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
- `COMPANY_NAME`：INGR宜瑞安
- `MARKET`：美股
- `COMPANY_FOLDER`：INGR宜瑞安
- `EXTRA_ANALYSIS`：
  1. 有哪些產品，各佔eps比重
  2. 各產品的主要競爭對手，市佔率
  3. 未來三年EPS