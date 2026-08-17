/goal
使用latest claude OPUS model 

# Routines — 日美港股電力公司比較

> 每次執行本 Routine 時，依序執行下列步驟，進行 Deep Research，並將完整分析結果重寫/更新至 `AnalysisResult/PowerAnalysisResult.md`。

## 全域參數 (Global Parameters)

- `INPUT_FILENAME`: AnalysisResult/PowerAnalysisResult.md
- `OUTPUT_FILENAME`: AnalysisResult/PowerAnalysisResult.md
- `TARGET_AUDIENCE`: 初級股票分析師 (用語白話易懂，專有名詞首次出現附英文全名)

---

## 執行步驟 (Execution Steps)

### Step 1：載入既有報告與歷史 Context
- **動作**：讀取 PowerAnalysisResult.md。
- **重點**：確認上一輪報告之更新時間、核心結論、以及上一輪所標註之「下一輪要分析/追蹤的項目」，作為本輪 Deep Research 之基底與比較對照。

### Step 2：日美港股電力公司比較
- 比較關西電力（9503.T）,九州電力（9508.T）,hk 中廣核,00836.HK, 00902.HK哪個比較適合投資
- 過去五年平均roe,pe,負債比率，股息率，營業利益率 比較
- 哪個長期投資報酬率比較高???
- 00836.HK為什麼PE這麼低

- 日美港股電力公司 pe，負債比，roe，股息率比較



### Step 6：提煉下一輪追蹤項目（Next Iteration Topics）
- **動作**：梳理當前分析中尚未明朗的關鍵變數。
- **重點內容**：
  1. 列出關鍵催化劑（Catalysts）、重大政策變數與黑天鵝/灰天鵝風險。
  2. 標註作為下一次輪替分析時需優先驗證的追蹤項目。

### Step 7：報告撰寫與寫入 (`WRITE TO PowerAnalysisResult.md`)
- **動作**：將上述分析結果彙整並重新撰寫寫入 [PowerAnalysisResult.md]
- **格式規範**：
  1. **目標讀者**：讓「初級股票分析師」看得懂（白話解讀、專業術語首次出現附英文全名）。
  2. **執行摘要表格**：包含主題、結論一句話、信心度評價。
  3. **數據換算與來源驗證**：明確標註數據發布時間與來源，如有具體金額需說明計價單位，數據不足處須明確註記限制與原因。