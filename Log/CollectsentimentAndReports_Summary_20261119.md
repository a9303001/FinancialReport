# 任務執行最終報告 - 2026/11/19

- **執行日**：2026-11-19（輪替表第 19 日 → EVTC EVERTEC）
- **公司資料夾**：`EVTC/`

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| EVTC EVERTEC | SEC EDGAR（sec-edgar-mcp 取清單 + `curl` 下載 10-Q HTML） | `EVTC/EVTC_Quarter_2026Q3.md` | ✅ 新增 2026 Q3 10-Q（2026-11-04 申報，期末 2026-09-30），HTML 已轉 Markdown 並刪除原檔 |
| EVTC EVERTEC | 既有檔案盤點 | `EVTC_AnnualReport_2025.md`、`EVTC_AnnualReport_2024.md` | ✅ 兩份年報已存在，跳過 |
| EVTC EVERTEC | SEC 8-K／Form 4／144／3／13G/A、Yahoo Finance、Seeking Alpha、分析師評等（Exa）、Reddit（Apify）、X、Reuters／Bloomberg | `EVTC/202611_輿情新聞.md`（新建） | ✅ 補 2026-10-19 之後的新內容 |

**本期重點**（每股換算基準：2026-10-28 流通股 59,252,142 股）：
- **Q3 2026 財報（11/03）**：營收 2.830 億美元（約每股 4.78 美元），+24%（固定匯率 +21%）；GAAP 淨利 2,990 萬美元（約每股 0.50 美元，稀釋 EPS 0.49），低於去年同期的 0.51（去年有 600 萬美元一次性稅額抵減，今年利息與稅率較高）；Adj. EBITDA 1.105 億美元（約每股 1.86 美元），+19%，但 margin 由 40.5% 降至 39.0%；Adj. EPS 1.07 美元，優於共識 0.98。
- **財測上修**：2026 年營收 10.88~10.96 億美元，Adj. EPS 4.00~4.08 美元。
- **利多**：Popular 10% 合約折扣已於 2026 年 10 月滿一年，不再造成年減；拉美分部營收 +59%；信用額度再融資（11/05）：Term Loan A 約 3.88 億美元（約每股 6.55 美元）展延最長 5 年、降 25bp，循環額度提高到 3 億美元（約每股 5.06 美元）；KBW 目標價 38 → 42 美元（Outperform）；Argus 11/11 上調至 BUY；Zacks Rank #2、Forward P/E 8.26。
- **利空**：CEO Mac Schuessler 於 11/04 賣出 145,000 股（約 504 萬美元，均價約 34.5~35.1 美元），持股減少約 32%；Business Solutions 營收 -5%、EBITDA -18%；淨負債約 10 億美元（約每股 16.9 美元），淨槓桿 2.46x；Popular／EBT 續約定價將壓抑 2027 年成長；巴西匯率波動。Morgan Stanley、Susquehanna 維持 Hold。
- **股價**：11/18 收 30.81 美元；分析師平均目標價約 35.5~37 美元。
- **其他**：季息 0.05 美元（12/04 發放）；American Century 持股 7.9%（13G/A）；12/08 出席 Raymond James TMT 會議。

## 2. 失敗或被擋網站
- **來源**：[Seeking Alpha](https://seekingalpha.com/symbol/EVTC)｜**原因**：`firecrawl_search` 只回同業 symbol 頁｜**已試過**：firecrawl_search → WebSearch（allowed_domains），只取得索引摘要
- **來源**：X (Twitter)｜**原因**：搜尋結果全為無關貼文｜**已試過**：firecrawl_search `site:x.com`、WebSearch（allowed_domains x.com/twitter.com）
- **來源**：yfinance 分析師評等｜**原因**：`get_recommendations` 回錯誤 `'GradeDate'`｜**已試過**：yfinance → Exa `web_search_exa`（成功取得索引）

## 3. 資料缺失說明
- 2026 年報（10-K）預計 2027 年 2 月底才申報，目前最新為 2025 年報與 2026 Q3 10-Q，資料已齊全。
- Reddit、X 近一個月無實質投資討論（EVTC 為小型股，討論量低，只有機器人轉貼新聞稿）。
- Reuters／Bloomberg 近一個月沒有 EVTC 專題報導。
- 分析師報告全文（Argus、KBW）需付費，只取得標題與自動稿摘要。

## 4. 異常檔案刪除紀錄
- 無（`EVTC_Quarter_2026Q3.html` 原始檔已轉 `.md` 後依規則刪除，非異常檔案）。

## 5. 本次使用的 MCP
| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| SEC EDGAR MCP | `get_recent_filings` | 列出 EVTC 近 45 天申報（10-Q、8-K、Form 4/144/3、13G/A） |
| yfinance | `get_recommendations` | 分析師評等（回錯誤 `'GradeDate'`） |
| Firecrawl | `firecrawl_search` | Seeking Alpha、X、Reuters、Bloomberg 索引搜尋 |
| Exa | `web_search_exa` | 分析師目標價／共識預估（MarketBeat、TipRanks、Yahoo Research、TradingView、Finabase） |
| Apify | `call-actor`（`harshmaur/reddit-scraper`）、`get-dataset-items` | Reddit 搜尋 |

- 無帳號級錯誤。另用內建 `curl`（EDGAR Archives）、`WebFetch`（Yahoo Finance）、`WebSearch`。

## 6. Phase 4 Convert2md
- 本次沒有新下載 PDF，未呼叫 `Convert2md`。
- 新下載的 SEC 10-Q 為 HTML，自行以 BeautifulSoup + markdownify 轉為 `EVTC/EVTC_Quarter_2026Q3.md`（移除 iXBRL 標籤／隱藏區塊，確認損益表、流通股數、期後事件等正文可讀，0 個 `ix:` 殘留），再刪除原始 HTML。

## 7. Skill 維護
- 修改 §4.1「美股分析師評級」列：`'GradeDate'` 錯誤補記 EVTC；Exa 可取得的來源補上 TipRanks blurbs、Yahoo `research/stock-forecast/{代號}/` Argus 評等列表、Finabase 共識預估。`.claude/` 與 `.agents/` 兩份 SKILL.md 已用 `diff` 確認一致。
