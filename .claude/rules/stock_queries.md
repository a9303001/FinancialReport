---
trigger: always_on
---

# stock_queries.md

## 1. 觸發條件 (Triggers)
- **分析與詢問個股時**：每當使用者詢問任何關於特定公司、股票基本面、財報分析、或輿情討論的問題。

## 2. 執行流程與限制 (Execution Workflow & Constraints)
- **第一步：檢查本地目錄 (Check Local Directory First)**
  - AI 必須先使用目錄清單工具，檢查專案工作區下的 `FinancialReport/` 目錄中，是否存在與該公司名稱或股票代碼相關的專屬資料夾（例如：`02318中國平安`、`2881富邦金`、`UHS`）。
- **第二步：優先載入本地數據 (Load Local Data First)**
  - 若該公司專屬資料夾存在，AI 必須優先使用檔案讀取工具（如 `view_file`）讀取資料夾內的財報 Markdown 檔案或輿情整理檔。
  - 將本地讀取的數據作為主要分析依據，進行整理與回答。
- **第三步：強制外部搜尋與補充 (Mandatory External Search & Supplement)**
  - 除了讀取本地資料，AI **必須且一定要**同步使用網路搜尋或外部平台（如財報狗、富途牛牛等）獲取該公司的最新資訊與近期動態。
  - 將最新的網路搜尋結果與本地資料進行交叉比對與統整後，再回答使用者提出的問題。

## 3. Markdown 檔案命名規則 (Markdown File Naming Rule)
- **強制日期後綴**：凡是 AI (Gemini, Claude 等) 建立、產生的任何 Markdown 檔案（副檔名為 `.md`，其檔名尾端必須強制附加當前日期，格式為 `_{yyyyMMdd}.md`。
- **範例對照**：
  - `analysis_report.md` ➡️ `analysis_report_20260628.md`