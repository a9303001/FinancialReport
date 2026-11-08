# 任務執行最終報告 - 2026/11/08（6279 胡連）

- **執行日**：2026-11-08（使用者手動指定 6279 胡連，非輪替表排程；同日輪替表 2832 台產的報告見 `CollectsentimentAndReports_Summary_20261108.md`，本檔加代號後綴避免覆蓋）
- **公司資料夾**：`6279胡連/`

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| 6279 胡連 | 鉅亨 API、MoneyDJ、經濟日報、中央社、PTT、CMoney、HiStock、Yahoo 股市、Dcard、Mobile01（皆經 Firecrawl） | `6279胡連/202611_輿情新聞.md`（新建，12 個來源章節） | ✅ 涵蓋 2026-08-06 ~ 11-08 |
| 6279 胡連 | TWSE 電子書（firecrawl stealth）、財報狗 e-report | 無（PDF 無法落地，見 §2） | ⚠️ 已確認最新檔名：2025/2024 年報 `2025_6279_20260526F04.pdf`、`2024_6279_20250626F04.pdf`；最新季報 2026Q2 `202602_6279_AI1.pdf`（中文，115/08/13 上傳）與 `202602_6279_AIA.pdf`（英文，115/09/21 上傳）；2026Q3 尚未上傳 |

**本期重點**（每股以 119,015,700 股換算）：
- **Q2 財報（8/06）**：上半年營收 48.70 億元（每股 40.92 元）、營業利益 5.62 億元（每股 4.72 元）、歸母淨利 5.24 億元（EPS 4.4 元）；毛利率 H1 27.4%、Q2 單季 27.9%。負債比率 42.6%，每股淨值 76.12 元；自算 OPM（營業利益率 ÷ 稅前淨利率）85.2%。原公告誤植為單季數字，40 分鐘後更正。
- **月營收放緩**：7 月 +38.2% → 8 月 +29.8% → 9 月 +13.7% → 10 月 +4.0%；10 月 10.31 億元（每股 8.66 元），1~10 月 88.38 億元（每股 74.26 元）年增 13.1%。Q3 營收 29.37 億元（每股 24.68 元）季增 6.9%。
- **首次國際併購**：688 萬歐元（約 2.51 億元，每股 2.11 元）買下義大利超跑線束廠 LA PUNTA 80%；8/06 公告估 EPS +0.29 元（自算交叉驗證吻合），但交割從「2026 年 10 月底」延到 2027-01-15，2026 年無貢獻。標的 2025 年營收 1,590 萬歐元（約 5.8 億元，每股 4.87 元）、淨利 118.3 萬歐元，近三年獲利持平。
- **法人觀點**：MoneyDJ（10/30）稱 Q3 毛利率會比 Q2 再受銅價壓抑、Q4 營收創新高、明年非中國占比衝三成；經濟日報（9/28）分析師估 2026 EPS 10.4 元、營收 112 億元（每股 94.1 元）、毛利率 28.5%，並稱新品 2026H2~2028 放量後毛利率可回 30%。以 H1 EPS 4.4 元推算，下半年需 6.0 元才達標，難度不低。
- **股利**：現金股利 5.5 元（總額 6.55 億元），9/03 除息、10/08 發放；11/06 收 99.7 元，殖利率約 5.5%。
- **籌碼**：借券賣出餘額 2,774 張（約占股本 2.33%）高於融資餘額 2,127 張；近一年股價 −24.4%（大盤 +42.3%）。
- **社群**：PTT 只有 1 篇 7 月營收文（「成也中國 敗也中國」「再發可轉債再說」）；CMoney 以「跟大盤一起跌」、「二代接班後股價一路爛？」為主，看多只有 1 則（中國政策、高頻連接器）；Dcard、Mobile01 無新文。整體關注度低、情緒中性偏空。

## 2. 失敗或被擋網站
- **來源**：[TWSE 電子書 PDF](https://doc.twse.com.tw/server-java/t57sb01)｜**原因**：本雲端環境網路政策未放行 `doc.twse.com.tw`（代理 `connect_rejected`，curl rc=56）；實體 PDF 只能用 `curl` 下載｜**已試過**：curl → 被拒；`firecrawl_scrape` basic → 安全性封鎖頁；`firecrawl_scrape` stealth → 成功取得清單與 step=9 實體連結 `doc.twse.com.tw/pdf/202602_6279_AIA_20261108_182422.pdf`，但無法存成二進位檔。曾提議建立放行台灣財經站的新環境，使用者未同意。
- **來源**：[財報狗 個股頁](https://statementdog.com/analysis/6279)｜**原因**：AWS WAF／逾時｜**已試過**：firecrawl_scrape（全引擎失敗）→ Bright Data（45 秒逾時）→ Apify rag-web-browser（202 + `x-amzn-waf-action: challenge`）
- **來源**：CMoney 官方 API（§5.2）｜**原因**：需 `curl` POST 取 token，環境不放行｜**已試過**：改 firecrawl_scrape 渲染頁面，取得首屏貼文（無法翻頁）

## 3. 資料缺失說明
- **財報 PDF 未下載**：2024、2025 年報與 2026Q2 季報皆已確認存在於 TWSE 電子書，但本環境無法下載。下次在可連 `doc.twse.com.tw` 的環境（例如 Cloud 環境或本機）執行即可補齊：清單 → step=9 取實體連結 → curl 下載 → 存為 `6279_AnnualReport_2025.pdf`、`6279_AnnualReport_2024.pdf`、`6279_Quarter_2026Q2.pdf`（建議用英文版 `_AIA`）。
- **2026Q3 季報**：上櫃公司法定期限 2026-11-14，TWSE 清單尚未出現，屬「尚未公布」。
- **CMoney**：只取到首屏約 8 則，9 月中至 10 月下旬的貼文未涵蓋。
- **CMoney 時間異常**：10 月營收快訊頁 meta 時間 11/05 00:51，早於鉅亨（17:15）與 MoneyDJ（13:59），原因不明，照錄。

## 4. 異常檔案刪除紀錄
無（本次沒有下載任何 PDF）

## 5. 本次使用的 MCP
| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape`（html / markdown / query directQuote；basic 與 stealth proxy） | TWSE 電子書清單與 step=9 連結、財報狗 e-report、鉅亨 API 與單篇、MoneyDJ、經濟日報、PTT、CMoney、HiStock、Yahoo 股市 |
| Firecrawl | `firecrawl_search` | 中央社全文、Dcard／Mobile01 索引 |
| Bright Data | `scrape_as_markdown` | 財報狗個股頁（逾時） |
| Apify | `call-actor`（`apify/rag-web-browser`）、`get-dataset-items` | 財報狗個股頁（AWS WAF challenge），約 0.015 CU |
| Claude Code Remote | `get_environment`、`create_environment` | 確認網路政策；提議新環境被使用者拒絕 |

無帳號級錯誤（Firecrawl 額度正常）。

## 6. Phase 4 Convert2md
略過：本次沒有新下載的 PDF。

## 7. Skill 維護
- §3.4 新增一列：雲端環境代理 `connect_rejected` 時，所有 curl 改走 MCP，新聞頁用 `firecrawl_scrape` + `query`/directQuote 省 token；PDF 無法落地則列出檔名與 step=9 網址。
- §4.2「TWSE 電子書」列改寫：basic proxy 也會被擋 → 改 stealth；補上檔名尾碼對照（`_AI1`/`_AIA`/`_AI2`/`_AIB`、年報 `mtype=F` 的 `F04`）與 step=9 取得實體 PDF 連結的方法。
- §4.2「股市爆料同學會」列：補 curl 不可用時用 firecrawl_scrape（waitFor）讀渲染頁、單篇 meta `publishedTime` 取時間。
- §4.2「財報狗」列：補 Bright Data 逾時、個股首頁全引擎失敗、只有 e-report 穩定。
- §7.3 台股：修正「季報多只有中文」→ 英文版 `_AIA` 常晚 1~1.5 個月上傳，有就優先用。
- `.claude` 與 `.agents` 兩份 SKILL.md 已用 `diff` 確認一致。
