# 任務執行最終報告 - 2026/08

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `6121 新普` | 本地已具備完整財報 | `2024_6121_20250529FE4_20260623_014337.md`<br>`2025_6121_20260529FE4_20260623_014508.md`<br>`6121_Quarter_2026Q2.md` | 2 年報 + 1 季報均已齊備，跳過重複下載 |
| `6121 新普` | CMoney、PTT、鉅亨網/經濟日報/MoneyDJ | `202608_輿情新聞.md` | 輿情收集完成，涵蓋蘋果摺疊機雙電芯趨勢、輝達 800VDC BBU 機架商機、Q2 財報後技術面及 ETF 換股與母以子貴討論 |
| `6781 AES-KY` | 財報狗 / TWSE MOPS | `6781_Quarter_2026Q2.md` | 2026 Q2 季報 PDF 下載成功並完成 Markdown 轉換；2024、2025 年報均已齊備 |
| `6781 AES-KY` | CMoney、PTT、鉅亨網/經濟日報/MoneyDJ | `202608_輿情新聞.md` | 輿情收集完成，涵蓋輝達 800VDC 白皮書 HVDC 高壓 BBU 爆發、Q2 獲利破 10 億元創歷史新高、7 月營收新高及千金股籌碼討論 |

## 2. 失敗或被擋網站
- **來源**: [Reddit](https://www.reddit.com/)
- **原因**: 搜尋 `6121`、`Simplo Technology`、`AES-KY` 無個股投資專題討論，多為一般筆電換電池硬體維修發問。
- **已依 §2 換過的 MCP**: apify（帳號達 monthly usage hard limit）→ firecrawl（`firecrawl_search`）

- **來源**: [雪球 Xueqiu](https://xueqiu.com/)
- **原因**: 平台主要覆蓋陸港美股，台股代號 `6121` 及 `6781` 過去三個月內無投資人深度分析專題。
- **已依 §2 換過的 MCP**: 搜尋與內容爬取檢索確認

## 3. 資料缺失說明
- `6121 新普` 與 `6781 AES-KY` 之最新 2 份年報（2024、2025）及最新季報（2026 Q2）均已完整齊備，無財報缺失。
- 社群輿情主要活躍於台股主流平台（CMoney 股市爆料同學會、PTT 股市板、台股財經新聞媒體），雪球與 Reddit 因非台股主要討論板塊故無實質分析專題。

## 4. 異常檔案刪除紀錄
- `d:\FinancialReport\AES-KY781_Quarter_2026Q2.pdf` 於轉換為乾淨 Markdown（`6781_Quarter_2026Q2.md`）並通過 0 個 CID 檢查後，依 Convert2md 規範刪除來源 PDF。

## 5. 本次執行使用的 MCP（強制填寫）
| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| `pymupdf4llm-mcp` | `convert_pdf_to_markdown` | 將 `AES-KY` 2026 Q2 季報 PDF 轉換為 Markdown 文件 |
| `firecrawl-mcp` | `firecrawl_search` | 檢索 Reddit 英文社群對於 AES-KY 與新普之討論 |
| `apify` | `call-actor` | 嘗試呼叫 `trudax/reddit-scraper-lite`（因帳號額度上限轉由 Firecrawl 替代） |
