# 任務執行最終報告 - 2026/10/19

- **執行日**：2026-10-19（使用者指定輪替表第 24 日 → TLK 印尼電信 PT Telkom Indonesia，美股 ADR）
- **公司資料夾**：`TLK印尼電信/`（本次新建）

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| TLK | SEC EDGAR 20-F（FY2025，2026-05-15 申報，accession 0001104659-26-062051） | `TLK_AnnualReport_2025.md` | ✅ HTML 下載後轉 Markdown，原 HTML 已刪 |
| TLK | SEC EDGAR 20-F（FY2024，2025-04-28 申報，accession 0001558370-25-005643） | `TLK_AnnualReport_2024.md` | ✅ 同上 |
| TLK | SEC EDGAR 6-K（2026-07-31，2026/6/30 合併財報，未經查核） | `TLK_Quarter_2026Q2.md` | ✅ 同上；Q3 財報尚未發布 |
| TLK | SEC 6-K、MSCI 新聞稿、CNBC Indonesia、Katadata、JournalArta、Selular.ID、Investortrust、w.media、GuruFocus、MarketBeat、Seeking Alpha、Reddit、Stockbit、X、Simply Wall St、Rikopedia、Reuters 轉載、Jakarta Post、DCD、DealStreetAsia、yfinance 日線 | `TLK印尼電信/202610_輿情新聞.md`（新建） | 首次收集，涵蓋 2026-07-19 ~ 10-19 |

**本期重點**（每股換算以 2026-09-30 有表決權股數 98,580,940,800 股為基準；1 ADS = 100 股）：
- **MSCI 降級衝擊**：MSCI 10/15 啟動諮詢，擬將印尼由新興市場降為獨立市場（2027-06-30 前決定，預設會降）。IHSG 10/16 單日 −11.57%（1998 年以來最大跌幅），BEI 10/19 起把跌停幅度由 15% 縮為 7%。TLKM 10/19 跌停至 1,770 盧比；ADR 10/16 −13.7% 至 11.03 美元、10/19 收 10.59 美元，較 9/14 的 15.26 美元累跌約 31%。
- **Q2 財報**：2026H1 營收 75.88 兆盧比（年增 3.9%，每股約 770 盧比）、歸母淨利 10.62 兆盧比（每股 107.50 盧比）；Q2 單季淨利約 6.3 兆盧比（年增 28%，每股約 64 盧比）；正常化淨利 11.3 兆盧比（每股約 115 盧比）。Telkomsel ARPU 年增 11.7%；IndiHome 營收年減 3.8%。上半年資本支出 9.4 兆盧比（每股約 95 盧比），自由現金流年增 12.8%。
- **經營層更換**：9/30 臨時股東會通過光纖分拆 Phase 2（同意 99.19%），但經營層異動案有 33.36% 反對；總裁由 Dian Siswarini 換成 Nanang Hendarno。主權基金 Danantara 要求加速整併子公司。
- **資產變現**：光纖資產併入 InfraNexia（Phase 2 約 49.9 兆盧比，兩階段累計約 85.7 兆盧比，集團內移轉）；資料中心 NeutraDC 多數股權出售進入 binding offer，市傳估值 10 億~15 億美元（約每 ADS 1.0~1.5 美元，公司不證實）。
- **信評**：Fitch 維持 BBB／負向（受主權評等壓制），獨立信用狀況上調至 'a'，淨槓桿約 0.4 倍 EBITDA。
- **輿情**：Stockbit 散戶多空分歧，偏多者認為基本面未變、年初至今已跌約 49%，偏空者認為被動資金賣壓未完；SA 作者 The Value Pendulum 10/16 維持買進（EV/EBITDA 約 3.5 倍）。

## 2. 失敗或被擋網站
- **來源**：[Reuters](https://www.reuters.com)｜**原因**：Firecrawl HTTP 402 額度用盡；內建 WebSearch 對 reuters.com 回 400｜**已試過**：firecrawl_search、WebSearch（allowed_domains）；改用 Exa 找到 TradingView/MarketScreener 轉載標題
- **來源**：[Seeking Alpha 正文](https://seekingalpha.com)｜**原因**：付費牆；WebFetch 403｜**已試過**：WebSearch、WebFetch、Bright Data（需重新授權）、Apify rag-web-browser（取得日期與摘要）
- **來源**：[MSCI IR 網頁](https://ir.msci.com)｜**原因**：Akamai Access Denied｜**已試過**：curl；改抓 msci.com PDF 成功
- **來源**：[IDN Financials](https://www.idnfinancials.com)｜**原因**：Cloudflare「Just a moment...」｜**已試過**：curl；內容已由其他來源涵蓋，未再跑 MCP 鏈
- **來源**：Bloomberg｜**原因**：付費牆｜**已試過**：僅經 Katadata 轉述
- **來源**：Stockbit、X｜**原因**：JS 載入／登入牆｜**已試過**：Exa、WebSearch 取索引（已標註）

## 3. 資料缺失說明
- 2026 Q3 財報尚未發布（彙整站稱 2026-10-29 公布，未取得公司正式公告），最新季報為 2026 Q2（6-K 2026-07-31）。
- FY2025 20-F 曾於 2026-04-30 申報 NT 20-F（延遲申報通知），於 2026-05-15 補交；本次未細究延遲原因，建議分析時查閱 NT 20-F 內容。
- yfinance `upgrades_downgrades` 對 TLK 回空陣列；分析師評級改由 MarketBeat、Investortrust、MarketScreener 轉述。
- YansenDoang（Stockbit）稱 10/19 傍晚 BEI/OJK 與 MSCI 會議結果將公布，本次未查到官方結果。

## 4. 異常檔案刪除紀錄
- 3 個原始 SEC HTML（`TLK_AnnualReport_2024.htm`、`TLK_AnnualReport_2025.htm`、`TLK_Quarter_2026Q2.htm`）轉為 Markdown 後依 §9 刪除，非異常檔。無 < 10KB 或亂碼檔。

## 5. 本次使用的 MCP
| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| SEC EDGAR | get_recent_filings | 列出 TLK 20-F／6-K 申報（之後改用 curl `data.sec.gov` 取完整清單與檔案） |
| yfinance | get_historical_stock_prices、get_recommendations | TLK、TLKM.JK 日線/週線；評級異動（回空） |
| Apify | apify/rag-web-browser（2 次）、trudax/reddit-scraper-lite（2 次，第 2 次觸及 0.1 美元上限中止）、get-dataset-items | Seeking Alpha 日期與摘要、Reddit 搜尋 |
| Exa | web_search_exa | Stockbit 貼文、Reuters 轉載、Jakarta Post／DCD 等索引 |
| Firecrawl | firecrawl_search | **Insufficient credits → 本次全程停用** |
| Bright Data | scrape_as_markdown | **MCP 需重新授權（needs you to sign in again）→ 本次全程停用，請使用者至 MCP 設定重新登入** |

## 6. Phase 4 Convert2md
- 本次下載的是 SEC HTML（非 PDF），未呼叫 `Convert2md`。依 §9 自行轉檔：以 BeautifulSoup 移除 `ix:header`、隱藏元素與圖片，表格轉 Markdown 表格，確認無 XBRL 殘留與 base64 後刪除原 HTML。

## 7. Skill 維護
- §3.4 新增「Bright Data `needs you to sign in again`」列：本次停用、改走 Apify／Exa。
- §4.1 Reuters 列：補充內建 WebSearch 對 reuters.com 回 400；Firecrawl 沒額度時用 Exa 找 TradingView/MarketScreener 轉載。
- §4.1 Seeking Alpha 列：新增 Apify `rag-web-browser` 可取得發布時間/摘要/Quick Insights。
- §4.1 X 列：新增 Firecrawl 沒額度時用 WebSearch `allowed_domains: x.com` 取索引。
- §4.1 新增「MSCI 新聞稿」列：ir.msci.com 被擋，改抓 msci.com PDF。
- 新增 §4.5「印尼（ADR 母股）」：CNBC Indonesia／Katadata／Selular.ID 為 SSR；Stockbit 用 Exa 取索引；Reddit 印尼版效益低。
- §7.3 美股：補外國發行人 20-F／6-K 的 EDGAR submissions JSON 與 index.json 查法。
- §8.2 美股來源：補 ADR 母股市場來源指引。
- `.claude/` 與 `.agents/` 兩份 SKILL.md 已同步（diff 相同）。`gemini/gemini_CollectsentimentAndReports.md` 無 § 引用需更新。
