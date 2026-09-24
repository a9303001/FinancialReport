# 任務執行最終報告 - 2026/09

- **執行日期**：2026-09-24（每日輪替表第 24 日）
- **標的**：`4507` 塩野義製薬（鹽野義製藥，日股）
- **資料夾**：`4507鹽野義製藥/`

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `4507鹽野義製藥` | （既有檔案） | `202506有価証券報告書－第160期(20240401－20250331).md`（FY2024 年報） | 已存在，跳過下載 |
| `4507鹽野義製藥` | （既有檔案） | `202606有価証券報告書－第161期(20250401－20260331).md`（FY2025 年報） | 已存在，跳過下載 |
| `4507鹽野義製藥` | （既有檔案） | `20260803_2027年3月期第1四半期決算短信.md`（FY2026 Q1 季報）＋決算補足資料／説明資料／トランスクリプト | 已存在，為最新一季；Q2（2026/7–9）尚未結束，預計 11 月初公布 |
| `4507鹽野義製藥` | Yahoo 掲示板、みんかぶ、株探、Yahoo 株つぶやき（X）、5ch、note、Reddit（索引）、Fierce Pharma／Simply Wall St | `202609_輿情新聞.md` | 新建；9 個來源章節、共 25 則，全部附真實 URL 與發布時間；未重複 `2026_PublicOpinion.md` 已收內容 |

**本次輿情重點（利多／利空）**
- 利多：Xocova 在美國全通路上市（約 160 名業務）；VTAMA 兒童適應症核准當週股價 +5.4%；みずほ維持「買い」評等；分析師共識淨利 2,252.8 億日圓，高於公司財測 2,100 億；9/17–18 出現技術面買進訊號；社長表示正在評估 3 件併購。
- 利空：みずほ目標價 4,000 → 3,800 円、共識目標價 3,388 → 3,350 円；みんかぶ個人投資家預想為「売り」（1,962 円）；note 文章指出 HIV 權利金佔營收過半、核心營業利益僅 +1.5%，且公司已大額借款；Reddit 使用者反映美國 Xocova 保險給付不易取得。

## 2. 失敗或被擋網站
- **來源**：Reddit（reddit.com）
  - **原因**：Apify `Monthly usage hard limit exceeded`（帳號月額度用盡）；Bright Data 對 www.reddit.com 回空白、old.reddit.com 需 KYC；Playwright 被 HTTP 403 js_challenge 擋下
  - **已依 §2 換過的 MCP**：apify / brightdata / playwright；最後改用 `firecrawl_search` 取索引摘要，已標註「⚠️ 搜尋摘要，非原文」
- **來源**：Shared Research — 塩野義不在其研究覆蓋範圍內，頁面無內容（非抓取失敗）
- **來源**：pharmaceutical-technology.com — `curl` 回 403，改用其他英文新聞源

## 3. 資料缺失說明
- 財報：無缺口。FY2026 Q2（2026/7–9）季報尚未公布。
- 輿情：Reddit 只取得搜尋索引摘要；Shared Research 未覆蓋塩野義；雪球、東方財富、LIHKG 對 4507 幾乎沒有討論（前次已記錄），本次未重抓。

## 4. 異常檔案刪除紀錄
- 無（本次未下載新財報、未刪除任何檔案）。Phase 4 Convert2md：資料夾內沒有 PDF/HTML，不需轉換。

## 5. 本次執行使用的 MCP
| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape` ×8 | みんかぶ analyst_consensus／pick 頁、Shared Research、note 搜尋頁、Fierce Pharma 關鍵字頁與 2 篇文章 |
| Firecrawl | `firecrawl_search` ×1 | Reddit 替代路徑（索引摘要） |
| Apify | `call-actor`（trudax/reddit-scraper-lite） | Reddit 抓取，因月額度用盡而失敗 |
| Bright Data | `scrape_as_markdown` ×2 | Reddit 抓取，失敗（回空白／需 KYC） |
| Playwright | `browser_navigate` ×1 | Reddit 抓取，被 403 擋下 |
| yfinance | `get_yahoo_finance_news` ×2 | 4507.T／SGIOY 英文新聞清單 |

內建工具：`Bash`（curl）、`WebSearch`（日期／背景確認）。

## 6. SKILL.md 增補
- 將下列網站的新踩坑與可行解法補入 §2.4：Yahoo 掲示板 `/bbs` 會轉到 `/forum`、みんかぶ子頁 `curl` 回 403、5ch 已改用 `find.5ch.io` 網域且為 Shift_JIS 編碼、note 搜尋頁與 API 無法直接抓、Shared Research 對未覆蓋公司只有空頁、Fierce Pharma 有 Cloudflare 阻擋。
