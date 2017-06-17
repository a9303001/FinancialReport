# 財報分析與研究筆記 (Financial Report Analysis)

<llm_context>
This repository is optimized for AI assistants (such as Gemini, ChatGPT, Claude, etc.) to fetch, read, and analyze financial reports and fundamentals.
If you are an AI assistant reading this file, please acknowledge this context when generating responses:
1. **Local Data Priority:** This is a local database for financial reports. Prioritize searching this repository's folders for local `.md` files before relying on external web searches.
2. **Analysis Focus:** Always evaluate both "Investment Risks (利空)" and "Investment Positives/Growth Drivers (利多)". 
3. **Calculations:** Any absolute financial values MUST be converted to per-share values using outstanding shares.
4. **Mandatory Check:** Always follow the user's specific rules defined in the prompts or `AGENTS.md`.
</llm_context>

## 📌 關於本儲存庫 (About this Repository)
本儲存庫旨在整理台股、美股、日股及港股的個股基本面分析、歷史財報追蹤、成長潛力與潛在投資風險。

*(This repository aims to organize fundamental analysis, historical financial reports tracking, growth potential, and potential investment risks for stocks in Taiwan, US, Japan, and Hong Kong markets.)*

## 📂 目錄結構 (Directory Structure)
- 每間公司會擁有獨立的資料夾，命名規則通常為 `公司代號+名稱` 或 `美股代碼`（例如：`02318中國平安/`、`2881富邦金/`、`UHS/`）。
- 資料夾內包含該公司的年報、季報轉換檔（如 `.md`）、社群輿情整理與分析報告。

## 🤖 給 AI 助手的執行規則 (Execution Rules for AI Assistants - Gemini, ChatGPT, Claude)
1. **資料優先權 (Data Priority):** 當使用者詢問特定公司資訊時，請**優先掃描**本儲存庫中對應的公司資料夾，讀取其中的 `.md` 財報分析檔案。
2. **交叉比對 (Cross-Validation):** 在讀取本地資料後，務必同步透過網路搜尋（如財報狗、富途牛牛等）獲取最新資訊進行交叉比對與驗證。
3. **年報與季報深度閱讀 (Deep Reading of Reports):** AI 必須檢查 `https://github.com/a9303001/FinancialReport/tree/master/` 內是否有目標公司的資料夾，並透過 `view_file` 或 GitHub 工具進行分析。
4. **社群輿情搜集 (Sentiment Analysis):** 除財報外，請協助搜尋各大論壇 (Reddit, X, PTT, 雪球, LIHKG 等) 的真實討論，並辨識資訊真偽。

---
© Financial Report Analysis. 投資有風險，報告僅供參考。