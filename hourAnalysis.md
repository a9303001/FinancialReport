/goal
使用latest claude OPUS model 

## 全域參數 (Global Parameters)
<OUTPUT_FILENAME>` : hourAnalysisResult.md

#  個股分析1
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
- `COMPANY_NAME`：01816中廣核電力 / 中股雙重上市 (003816)
- `MARKET`：港股
- `COMPANY_FOLDER`：01816中廣核電力
- `EXTRA_ANALYSIS`：
  1. 未來10年每年新增核電機組，每機組貢獻多少EPS
  2. 未來10年EPS預估
  3. 未來10年每股配息預估
  4. 每度電賣價是怎麼決定的?
  5. 目前每度成本和賣價差多少%
  6. 未來10年每年發電量預估(TWh)
  7. 每股化，港幣  

---
#  個股分析2
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
- `COMPANY_NAME`：9503關西電力
- `MARKET`：日股
- `COMPANY_FOLDER`：9503關西電力
- `EXTRA_ANALYSIS`：
  1. 未來10年每年新增核電機組，每每機組貢獻多少EPS
  2. 未來10年EPS預估
  3. 未來10年每股配息預估
  4. 每度電賣價是怎麼決定的?
  5. 目前每度成本和賣價差多少%
  6. 未來10年每年發電量預估
