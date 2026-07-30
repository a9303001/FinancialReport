/goal
使用latest claude OPUS model 
#  個股分析1
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
  - `COMPANY_NAME`：01426 春泉產業信託 REIT
- `MARKET`：港股
- `COMPANY_FOLDER`：01426春泉Reit
- `EXTRA_ANALYSIS`：
  1. 每股營業現金流量、每股營運現金流（FFO）、每股調整後營運現金流（AFFO）
  2. 所有財務數據都要換算成每股多少港幣
  3. 每年收的管理費用是怎麼算的，佔淨值百分比是多少?
  4. 北京華貿中心（China Central Place）土地使用權2053到期,到時續期要每股多少錢?有什麼風險
  
  
 ---
 #  個股分析2
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
  
  - `COMPANY_NAME`：87001 匯賢產業信託 REIT
- `MARKET`：港股
- `COMPANY_FOLDER`：87001匯賢Reit
- `EXTRA_ANALYSIS`：
  1. 最新一期配息（人民幣）換算出來的年殖利率是多少
  2. 人民幣負債佔總負債比重（%）
  3. 港幣負債佔總負債比重（%）
  4. 港幣債務轉置成人民幣債務計劃，對配息影響
  5. 港幣債務還剩多少（單位: 人民幣）？多久可還完
  6. 所有財務數據都要換算成每股多少人民幣（e.g. 債務每股多少人民幣）
  7. 每年收的管理費用是怎麼算的，佔淨值百分比是多少?
  9. 土地使用權到期後,到時續期要每股多少錢?有什麼風險?
