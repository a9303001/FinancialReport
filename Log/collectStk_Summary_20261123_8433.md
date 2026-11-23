# 任務執行最終報告 - 2026/11/23

- **執行日**：2026-11-23（使用者指定；輪替表第 9 日 → 8433 弘帆）
- **公司資料夾**：`8433弘帆/`

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| 8433 弘帆 | 官網 IR `www.bonfame.com`（113 年度合併報告） | `8433_AnnualReport_2024.md`（FY2024 合併財報，85 頁，0 個 CID） | ✅ 補齊第 2 份年報（原有 `8433_annual_2024.md`／`_2025.md` 實為股東會開會通知，非年報） |
| 8433 弘帆 | 既有檔 | `2025_8433_20260618F04.md`（FY2025 股東會年報）、`202504_8433_AI1_*.md`（FY2025 合併財報） | ✅ 已有，跳過 |
| 8433 弘帆 | 既有檔 | `8433_Quarter_2026Q2.md` | ⚠️ 2026Q3 PDF 未能下載（見 §3），最新完整季報仍為 Q2 |
| 8433 弘帆 | 鉅亨 API、MoneyDJ、CMoney API、Yahoo、PTT、經濟日報、HiStock、yfinance、Exa、Bright Data | `202611_輿情新聞.md`（11-09～11-23 增補） | ✅ |

**本期重點**（每股以 54,506,098 股換算）：
- **Q3 單季（MoneyDJ 轉載 MOPS 綜合損益表，11/13）**：營收 9.14 億元（每股 16.77 元，年增 3.2%）；毛利率 22.29%（年增 1.8 個百分點）；但推銷費用年增 49%、信用減損轉損失，營業利益 7,166 萬元（每股 1.31 元，年減 9.4%）；業外由去年同季 +6,468 萬元縮至 +250 萬元 → 稅後 6,338 萬元，**EPS 1.16 元（去年同季 2.02 元，年減 42%）**。OPM 約 96.7%。
- **前三季**：營收 26.69 億元（每股 48.96 元，年增 9.6%），營業利益年減 10.1%，EPS 3.96 元（去年同期 0.71 元，低基期來自去年匯損）；稀釋 EPS 3.64 元，與基本 EPS 差約 8%，原因待 Q3 附註驗證。近四季 EPS 6.42 元。
- **10 月營收** 2.86 億元（每股 5.24 元），年減 6.71%；1~10 月 29.55 億元（每股 54.21 元），年增 7.92%。
- **股價**：11/20 收 45.00 元（−4.76%，量 102 張，52 週新低）；PB ≈ 1.00、TTM PE ≈ 7.0、以 2025 年度股利 4.20 元計殖利率 ≈ 9.3%（2025 配發率 133%、FCF 為負）。
- **籌碼**：外資 20 日小額買超 18 張、持股 1.22%；融資 176 張；借券賣出餘額 112 張（相對日均量偏高）。
- **社群**：PTT／Dcard／Mobile01／CMoney 11 月無網友實質討論（CMoney 只有營收自動推播）。

## 2. 失敗或被擋網站
- **來源**：[TWSE 電子書 202603_8433_AI1.pdf](https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=8433&year=115&seamon=&mtype=A&)｜**原因**：清單與 step=9 連結用 Apify 成功（11/13 16:43 上傳、1,625,377 bytes），但 PDF 本體：`curl` 第一次傳 360 KB 後逾時、第二次回 947 bytes 封鎖頁；Apify `call-actor` 第一次 120 秒逾時、第二次被 MCP 60 秒上限中止（ABORTED）｜**已試過**：curl ×2、Apify ×2、官網 IR（只到 115Q2）。Firecrawl 預檢停用；Bright Data 依 Skill 不用於 TWSE PDF。
- **來源**：[弘帆官網 https](https://www.bonfame.com/)｜**原因**：`curl` rc=35（SSL）、Bright Data 45 秒逾時｜**已試過**：改 `http://` 直連成功。
- **來源**：鉅亨關鍵字 API｜**原因**：至 11/23 未收錄 11/13 的 Q3 綜合損益表重訊（索引落後）｜**替代**：MoneyDJ。

## 3. 資料缺失說明
- **2026Q3 季報 PDF**：TWSE 已上傳（下載網址 `https://doc.twse.com.tw/pdf/202603_8433_AI1_20261123_134231.pdf`，時效性連結，下次需重取 step=9），本環境無法落地；官網預計數週後上架（官網 115Q2 為 2026-08 後上架）。缺：Q3 資產負債表細項（只有總資產 46.78 億、總負債 22.24 億、權益 24.54 億）、現金流量表、附註（客戶集中、借款、稀釋 EPS 明細）。
- **FY2024 股東會年報（F04）** 未下載：已有 FY2024 經查核合併財報與 FY2025 年報（含 FY2024 比較數），足以涵蓋兩年度；需要 FY2024 年報非財務章節時再補。
- 冷門股：無券商研究、無媒體專文，社群討論近乎零。

## 4. 異常檔案刪除紀錄
- 無（Convert2md 依規則刪除已成功轉檔的來源 `8433_AnnualReport_2024.pdf`；暫存下載檔在 scratchpad，未進 repo）。
- 註：`8433_annual_2024.md`、`8433_annual_2025.md` 內容為股東會開會通知書，檔名誤導，本次未刪（非本 Skill 可刪範圍），建議使用者確認後改名或刪除。

## 5. MCP 預檢與使用紀錄
- **預檢結果**：可用：Bright Data、Apify、Exa、Playwright、yfinance（`8433.TWO`；`8433.TW` 回空）、curl｜停用：Firecrawl（`Insufficient credits for this connected-app request`，每日 MCP 額度 2026-11-23T14:59Z 重置）
- **使用者待辦**：Firecrawl 額度用盡 → 到 Firecrawl 後台加值或等每日額度重置：https://www.firecrawl.dev/billing/mtew3ffk26y4prtb1knxjnam2bew37hk

| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape` | 預檢（額度用盡，停用） |
| Bright Data | `scrape_as_markdown`、`search_engine` | 預檢；官網 https（逾時）；Dcard/Mobile01 索引（0 筆） |
| Apify | `apify--web-fetch`、`call-actor`、`get-actor-run` | TWSE 清單與 step=9 連結（成功）；Q3 PDF 全文（2 次逾時）；官網連結列表（成功） |
| Exa | `web_search_exa` | 預檢；新聞與第三方平台索引（FinLab、toAlpha、領富、富聯網） |
| Playwright | `browser_navigate` | 預檢 |
| yfinance | `get_historical_stock_prices` | 股價（5d、1mo） |
| pymupdf4llm | `convert_pdf_to_markdown` | FY2024 合併財報轉檔 |

## 6. Phase 4 Convert2md
- 掃描範圍 `8433弘帆/`：1 個 PDF → 成功 1（`8433_AnnualReport_2024.md`，0 個 `(cid:`），已移除 43 行 `pdf_images` 圖片連結；報告見 `Log/conversion_summary.md`。

## 7. Skill 維護
- **§4.2 合併重複列（刪除 3 列）**：TWSE 電子書、MOPS 法說會簡報、MoneyDJ 各有新舊兩列 → 保留較新的一列，舊列的獨有內容（不要用 Firecrawl `parsers: pdf`／Bright Data 解析 TWSE PDF、改用 MoneyDJ 轉載）併入新列；刪除已失效的「MOPS 法說帶 cookie 即可下載」舊列。
- **§4.2 TWSE 電子書列修改**：Apify `call-actor` 120 秒上限連 1.6 MB PDF 也可能逾時（原寫 5 MB 以上），失敗 2 次即換路；step=9 連結 `curl` 可能先傳部分資料後逾時、不支援續傳、重抓即被封鎖。
- **§7.3 新增**：弘帆 8433 官網 IR 路徑（需用 `http://`）。
