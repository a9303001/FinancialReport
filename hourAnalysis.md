/goal
使用latest claude OPUS model 

## 全域參數 (Global Parameters)
<OUTPUT_FILENAME>` : hourAnalysisResult.md

#  個股分析1
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
- `COMPANY_NAME`：03606 福耀玻璃（中股: 600660 福耀玻璃）
- `MARKET`：港股/中股
- `COMPANY_FOLDER`：03606福耀玻璃
- `EXTRA_ANALYSIS`：
  1. 中美貿易戰影響及對 EPS 影響
  2. AI 自駕車對玻璃需求影響?對eps影響?
  3. 電動車對玻璃需求影響?對eps影響?
  4. 所有數據要每股化
