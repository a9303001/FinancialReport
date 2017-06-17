---
trigger: always_on
---

# 股票問題本地資料優先載入規則 (Stock Queries Local Data Priority Rule)

## 1. 觸發條件 (Triggers)
- 每當使用者詢問任何關於特定公司、股票基本面、財報分析、或輿情討論的問題時。

## 2. 執行流程與限制 (Execution Workflow & Constraints)
- **步驟一：檢查本地目錄 (Check Local Directory)**
  - AI 必須先使用目錄清單工具，檢查專案工作區下的 `FinancialReport/` 資料夾中是否已存在該公司名稱或股票代碼的專屬資料夾（例如：`02318中國平安`、`2881富邦金` 或 `UHS`）。
  
- **步驟二：優先載入本地數據 (Load Local Data First)**
  - 若該公司的專屬資料夾存在，AI 必須優先使用檔案讀取工具（如 `view_file`）讀取資料夾內的財報 Markdown 檔案（如 `.md` 轉換檔）或輿情整理檔。
  - 將本地讀取的數據載入為主要分析依據，進行整理與回答。

- **步驟三：強制外部搜尋與補充 (Mandatory External Search & Supplement)**
  - 除了讀取本地資料外，AI **必須且一定要**同步使用網路搜尋或外部平台（如財報狗、富途牛牛等）獲取該公司的最新資訊與近期動態。
  - 將最新的網路搜尋結果與本地資料進行交叉比對與統整後，再回答使用者提出的問題。
