# FinancialReport (財報資料庫)

> **🤖 給 AI 助手（ChatGPT, Claude, Gemini, Copilot, Grok 等）的專屬讀取指南：**
> 請勿嘗試使用網頁爬蟲解析標準 GitHub 頁面（會有 HTML 雜訊干擾）。
> 請直接從下方的「最新財報快速直達區」複製 `https://raw.githubusercontent.com...` 的網址，並使用您的連網工具直接讀取該純文字檔。
> 
> **最佳實踐建議**：若需瀏覽某公司完整財報清單，請先使用 GitHub API 或工具獲取資料夾內檔案列表，再逐一讀取最新檔案。
> **原始 Repo**：https://github.com/a9303001/FinancialReport

## 📂 專案簡介
本資料庫專門存放各大美股、台股、日股、港股及 REITs 的歷年財報備份（包含 10-K, 10-Q, 年報, 季報等）。
所有檔案皆盡可能優化為純文字（TXT）或易讀格式，旨在提供給大語言模型（LLM）進行基本面與財報分析使用。
支援市場：美國（US）、台灣（TW）、日本（JP）、香港（HK）、不動產投資信託（REITs）
**預設分支**：`master`
---

## 🚀 最新財報快速直達區 (AI 讀取用 Raw URLs)

**⚠️ 重要說明（給 AI 與維護者）**：
- 每個資料夾內可能有多個年度/季度的財報檔案。
- **AI 使用方式**：直接複製下方 Raw URL，**將 `[最新檔案名稱]` 替換為資料夾內實際最新檔案**（建議先列出資料夾內容確認）。
- **維護者更新指南**：新增或更新財報後，請在此區同步更新各公司「最新檔案 Raw URL」，並更新日期。
- 完整目錄結構建議使用：`https://uithub.com/a9303001/FinancialReport`（可取得純文字樹狀結構）

### 🇺🇸 美股 (US Stocks) 範例
- **UHS** (Universal Health Services)
  - 資料夾名稱：`UHS`
  - 財報 Raw URL 範例：`https://raw.githubusercontent.com/a9303001/FinancialReport/master/UHS/*`

### 🇹🇼 台股 (TW Stocks) 範例
- **2245 詠勝昌** (Yong Sheng Chang)
  - 資料夾名稱：`2245詠勝昌`
  - 財報 Raw URL 範例：`https://raw.githubusercontent.com/a9303001/FinancialReport/master/2245詠勝昌/*`

- **2249 湧盛** (Yung Sheng)
  - 資料夾名稱：`2249湧盛`
  - 財報 Raw URL 範例：`https://raw.githubusercontent.com/a9303001/FinancialReport/master/2249湧盛/*`

- **2637 慧洋-KY** (Hui Yang)
  - 資料夾名稱：`2637慧洋-KY`
  - 財報 Raw URL 範例：`https://raw.githubusercontent.com/a9303001/FinancialReport/master/2637慧洋-KY/*`


### 🇯🇵 日股 (JP Stocks) 範例

- **7203 Toyota** (豐田汽車)
  - 資料夾名稱：`7203Toyota`
  - 財報 Raw URL 範例：`https://raw.githubusercontent.com/a9303001/FinancialReport/master/7203Toyota/*`

### 🏢 REITs (不動產投資信託)

- **01426 春泉Reit** (Spring REIT / 春泉產業信託)
  - 資料夾名稱：`01426春泉Reit`
  - 財報 Raw URL 範例：`https://raw.githubusercontent.com/a9303001/FinancialReport/master/01426春泉Reit/*`

- **87001 匯賢Reit** (Hui Xian REIT / 匯賢產業信託)
  - 資料夾名稱：`87001匯賢Reit`
  - 財報 Raw URL 範例：`https://raw.githubusercontent.com/a9303001/FinancialReport/master/87001匯賢Reit/*`

---

## 🛠️ 目錄結構查詢與進階使用
若上方清單未包含目標公司，或需取得完整檔案列表：
1. **推薦工具**：使用 `https://uithub.com/a9303001/FinancialReport` 取得結構化純文字目錄。
2. **GitHub 原生**：直接訪問 https://github.com/a9303001/FinancialReport/tree/master 瀏覽資料夾。
3. **AI 進階技巧**：使用 GitHub API (`https://api.github.com/repos/a9303001/FinancialReport/contents/資料夾名稱`) 獲取 JSON 格式檔案列表，再讀取 raw URL。
---