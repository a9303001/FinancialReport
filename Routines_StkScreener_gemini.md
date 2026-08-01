# Search 台股，日股，港股，美股符合下面條件股票
- 市占率前3名
- 有產品市占率前3名
- pe 5~15
- 營業利益率>10%
- 負債比率<70%
- 排除美國ADR
- 排除美國OTC

# 分析rule
- 每次都要讀取上一次的Routines_StkScreenerResult_gemini.md
- 根據上述條件及五年/10年淨利cagr,opm,等等財務指標做排名，選出前50名的股票，從第一名排到第50名
- 排名要說明為什麼這樣挑
- update to Routines_StkScreenerResult_gemini.md
- 如果這次沒法一次分析完所有股票，可以註記留待下次分析
- 本md會不斷輪迴執行，每次執行都要自動fix Routines_StkScreenerResult_gemini.md錯誤的地方. 不用每次要分享完所有資料，可以留待下次分析

# Routines_StkScreenerResult_gemini.md 內容
- 本次分析結果
- top50股票排名及分析
- 本次來不及分析，需要留待下次分析的部分
- 下次想要分析的部分
- 下次想要分析的股票or市場