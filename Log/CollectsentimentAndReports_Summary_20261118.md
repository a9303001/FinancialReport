# 任務執行最終報告 - 2026/11/18

- **執行日**：2026-11-18（輪替表第 18 日 → CF CF Industries Holdings, Inc.）
- **公司資料夾**：`CF/`

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| CF | SEC EDGAR（curl `data.sec.gov` + Archives） | `CF/CF_Quarter_2026Q3.md`（10-Q，期末 2026-09-30，申報 2026-11-05） | ✅ 新增；HTML 轉 md 後刪除原始 HTML，0 個 `(cid:` |
| CF | 既有檔案盤點 | `CF_AnnualReport_2025.md`、`CF_AnnualReport_2024.md` | ✅ 已有，跳過 |
| CF | SEC 8-K Ex-99.1、Yahoo Finance、Benzinga（經 Firecrawl）、Seeking Alpha、X、Reddit、Reuters、Bloomberg | `CF/202611_輿情新聞.md`（新建，涵蓋 2026-10-19 ~ 2026-11-18） | ✅ |

**本期重點**（每股換算以 10-Q 封面流通股 146,284,911 股計）：
- **Q3 財報（11/4）**：營收 18.60 億美元（約每股 12.71 美元，年增 12%）；淨利 4.36 億美元，稀釋 EPS 2.87 美元，略低於共識（Zacks 2.93）；營收優於共識（17.6 億）。財報後股價收跌逾 4%。
- **前九月**：淨利 17.8 億美元（EPS 11.60）、adjusted EBITDA 30.1 億美元（約每股 20.6 美元），含約 1.70 億美元（約每股 1.16 美元）訴訟和解一次性利益。TTM FCF 20.3 億美元（約每股 13.9 美元）。
- **Yazoo City** 停產延至 **2027 上半年**才恢復，AN 銷量年減約 67%；修復成本大部分由保險支付，總額仍在估算中。
- **成本壓力**：年初至今非天然氣可控成本增加約 2 億美元（約每股 1.37 美元）；美加移轉訂價稅務爭議存入 3.06 億美元（約每股 2.09 美元）保證金。
- **資本配置**：Q3 庫藏股 300 萬股／3.67 億美元；20 億美元計畫剩約 11.1 億美元（約每股 7.6 美元）。Q3 加權平均股數年減約 6.1%。
- **成長**：Blue Point One（CF 40%，總成本 37 億美元）8 月開工、2029 年投產；管理層提出 2030 年 mid-cycle EBITDA 33 億美元（約每股 22.6 美元）；Courtright DEF 擴產案 FEED 研究，FID 預計 2027。
- **產業**：管理層稱氮肥供需「constructive into 2027」，原因包括中東尿素出口只恢復約一半、歐洲約 37% 氨產能停機、千里達約 35% 產能永久關閉。
- **分析師**：共識 Hold（20 位，平均目標價 123 美元）。RBC 目標價上調至 125 美元、UBS 下調至 133 美元、JPM Hold 115 美元、Bernstein Outperform 162 美元。
- **偏空輿情**：Frank Curzio（X）與 Trefis 都認為荷姆茲重開、波斯灣出貨恢復後，化肥交易可能反轉，現在約 11.5% 的 FCF 殖利率反映的是獲利高峰。俄烏和談消息也可能降低俄國供給風險溢價。11/18 盤中股價約 114.89 美元（-3.7%），原因未找到對應報導。

## 2. 失敗或被擋網站
- **來源**：[MT Newswires／RBC 報告全文](https://finance.yahoo.com/markets/stocks/articles/cf-industries-poised-see-improving-180206851.html)｜**原因**：Yahoo Finance Plus 付費牆｜**已試過**：WebFetch（評等與目標價改用 Benzinga 標題補上）
- **來源**：Seeking Alpha 分析文章內文｜**原因**：只取得索引摘要（依 §4.1 不跑 scrape 全引擎）｜**已試過**：`firecrawl_search`；新聞稿 4667600 用 `firecrawl_scrape` query 模式取得引述與 metadata
- **來源**：yfinance `get_recommendations`｜**原因**：回錯誤 `'GradeDate'`｜**已試過**：1 次，改用 Firecrawl 回傳的 Benzinga 結構化結果

## 3. 資料缺失說明
- Reddit 近一個月沒有散戶實質討論，只有新聞轉貼機器人與自動彙整文（r/MarketFluxHub 誤把前九月 EBITDA 寫成 Q3，已註明與官方不符）。
- Reuters、Bloomberg 近一個月沒有 CF 專文。
- 11/18 股價下跌 3.7% 的原因沒有找到對應新聞。
- 下一份財報：2026 年 10-K 預計 2027 年 2 月公布。

## 4. 異常檔案刪除紀錄
- 無（`CF_Quarter_2026Q3.html` 轉成 `.md` 後依 §9 刪除原始 HTML，不屬於異常檔）。

## 5. 本次使用的 MCP
| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_search`、`firecrawl_scrape` | Seeking Alpha／X／Reuters／Bloomberg 索引；X 單篇全文（x-com provider）；SA 新聞 query 引述；附帶 Benzinga 評等異動 |
| Apify | `call-actor`（`harshmaur/reddit-scraper`）、`get-dataset-items` | Reddit 搜尋（約 0.0036 CU） |
| yfinance | `get_recommendations` | 評等異動（回錯誤） |
- 內建工具：curl（SEC EDGAR）、WebFetch（Yahoo Finance）、WebSearch。
- 無帳號級錯誤。Bright Data 與 Playwright 本次不需要用到。

## 6. Phase 4 Convert2md
- 本次沒有新的 PDF，所以未呼叫 Convert2md。10-Q 為 SEC HTML，依 §9 自行用 BeautifulSoup + html2text 轉成 `CF_Quarter_2026Q3.md`（移除 ix:header 與 iXBRL 標籤，約 27 萬字元，正文可讀），再刪除原始 HTML。

## 7. Skill 維護
- §4.1「X (Twitter)」列：改寫為 `firecrawl_scrape` 單篇 status 頁自 2026-11 起可經 Firecrawl x-com provider 取得全文、`created_at` 與讚數；刪除舊的「Firecrawl 全引擎失敗」敘述，日期更新為 [2026-11]。
- §4.1「美股分析師評級」列：補上 yfinance 對 CF 回 `'GradeDate'` 錯誤；新增替代路徑：個股 `firecrawl_search` 回應的 `answer` 欄附有 Benzinga 結構化評等異動，日期更新為 [2026-11]。
- `.claude/` 與 `.agents/` 兩份 SKILL.md 已用 diff 確認一致。
