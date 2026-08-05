/goal
使用latest claude OPUS model 

## 全域參數 (Global Parameters)
<OUTPUT_FILENAME>` : hourAnalysisResult.md

#  個股分析1
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
  - `COMPANY_NAME`：`00883`  `中國海洋石油` 
- `MARKET`：港股
- `COMPANY_FOLDER`： `00883中國海洋石油`
- `EXTRA_ANALYSIS`：
  1. 油價對eps的影響
  2. 油價損益平衡點
  3. 未來三年EPS預估


---

#  個股分析2
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
  - `COMPANY_NAME`：`03606`  `福耀玻璃` 
- `MARKET`：港股
- `COMPANY_FOLDER`： `03606福耀玻璃`
- `EXTRA_ANALYSIS`：
