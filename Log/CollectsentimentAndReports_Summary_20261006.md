# 任務執行最終報告 - 2026/10（2026-10-06 輪值：7203 Toyota）

- **觸發**：`Routines_CollectsentimentAndReports.md` 每日輪替表，執行日 6 → `7203` / `Toyota` / 資料夾 `7203Toyota`
- **執行時間**：2026-10-06 20:10 ~ 20:45 (UTC)

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `7203Toyota` | 盤點既有檔案 | `7203_FY2025_annual_results.md`、`7203_FY2026_annual_results.md`、`7203_Quarter_2027Q1.md` | 2 年報＋1 季報**皆已存在**，**本次不需下載** |
| `7203Toyota` | 株探開示一覧（nmode=3） | — | 最新開示為 2026-10-05 自社株買回進度（9 月買回 3,555 萬股／1,085 億日圓，累計 1,950 億日圓＝上限的 19.5%）；FY2027 Q2 決算預計 11 月初公布，目前 Q1 即為最新季報 |
| `7203Toyota` | 株探、Yahoo JP 掲示板／株つぶやき、みんかぶ、yfinance、Reddit、Reuters、新聞綜合、Seeking Alpha、雪球、5ch | `7203Toyota/202610_輿情新聞.md`（新建，約 41.6KB，`(cid:` 0） | 輿情增量更新成功（範圍 2026-09-21 ~ 10-06，更早內容已在 `2026_PublicOpinion.md`），12 個來源加上多空總結 |

## 2. 失敗或被擋網站
- **來源**：Seeking Alpha 文章頁
  - **原因**：Firecrawl 回 `All scraping engines failed`（含 stealth）
  - **已依 §2 換過的 MCP**：Firecrawl ❌ → Bright Data `scrape_as_markdown` ✅（只取得 Summary，正文有付費牆）
- **來源**：雪球 TM
  - **原因**：Bright Data 只回外殼，沒有討論流
  - **已依 §2 換過的 MCP**：Bright Data ❌ → Firecrawl `firecrawl_scrape` + stealth ✅
- **來源**：Reddit（r/investing）
  - **原因**：Apify `call-actor` 60 秒逾時，沒有回傳 datasetId；r/stocks 只有 6 月舊文，本期無新內容
- **來源**：Yahoo JP 掲示板
  - **原因**：`?page=N` 不會翻頁，只取得最新約 60 則（大約 11 小時）；9/21 ~ 10/5 的貼文無法取得，已在輿情檔註明
- **來源**：yfinance 新聞
  - **原因**：7203.T 與 TM 都回「No news found」（不是封鎖）

## 3. 資料缺失說明
- **財報**：不缺。最新季報為 FY2027 Q1（2026-08-04 公布），Q2 尚未到發布時間。
- **年報說明**：資料夾內的「年報」是決算短信（Financial Summary）英文版，不是有価証券報告書或 20-F 全文，與前幾次執行的做法一致。
- **輿情注意事項**：
  - 株つぶやき 20 則中約 12 則是模板化垃圾帖。「全固態電池已實現」屬炒作，已標註。
  - 中國「一汽豐田退出／大降價」傳聞已經官方否認。
  - icartea「Toyota Sales Drop 21% in September」是 2024 年的舊聞，已排除。

## 4. 異常檔案刪除紀錄
- 無（本次沒有下載新財報；2026-10-05 買回通知 PDF 只存在 scratchpad 中查閱，沒有放進 repo）。

## 5. 本次執行使用的 MCP
| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape` | みんかぶ 7203 ✅、Reuters 公司頁與 2 篇文章 ✅、雪球 TM 與單篇（stealth）✅、Seeking Alpha 2 篇 ❌ |
| Firecrawl | `firecrawl_search` | Seeking Alpha 站內近一個月文章搜尋 |
| Bright Data | `scrape_as_markdown` | 雪球 TM（只有外殼）❌、Seeking Alpha 2 篇（Summary）✅ |
| Apify | `call-actor`（`trudax/reddit-scraper-lite`）、`get-dataset-items`、`abort-actor-run` | Reddit r/stocks 與 r/investing 搜尋 Toyota／TM |
| yfinance | `get_yahoo_finance_news`、`get_recommendations`、`get_historical_stock_prices` | 新聞（無資料）、TM 評等（無資料）、7203.T 日線 |
| （內建工具） | `Bash`（`curl`）、`WebSearch` | 株探、Yahoo JP、5ch（SSR 直接抓取）；新聞搜尋與原文驗證 |

- **未使用**：Playwright（不需要）。這次沒有帳號層級的錯誤（402／hard limit）。

## 6. 經驗補充（已增補到 SKILL.md §2.4）
- `find.5ch.net` 會 301 轉到 `find.5ch.io`，`curl` 要加 `-L`。
- Yahoo JP 掲示板 `?page=N` 不會翻頁，大型股只涵蓋約半天。
- 用 Firecrawl 抓雪球時，渲染瀏覽器的時區是美東，要以單篇頁的北京時間校準。
- Reuters 文章頁用 Firecrawl basic 就能取得全文。
- Seeking Alpha：用 Firecrawl search 找文章，再用 Bright Data 取 Summary；WebSearch 結果會混入仿冒的 SEO 垃圾頁。
- yfinance 新聞連大型股都回空結果，不可依賴。
