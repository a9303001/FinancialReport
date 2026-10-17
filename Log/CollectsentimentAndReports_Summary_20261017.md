# 任務執行最終報告 - 2026/10/17

- **執行日**：2026-10-17（輪替表第 17 日 → `1521` 大億、`7276` 小糸製作所）
- **公司資料夾**：`1521大億/`、`7276小糸製作所/`（後者本次新建）

## 1. 成功紀錄

| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| 1521 大億 | 既有財報盤點 + 鉅亨 API 核對 | 無新財報 | ✅ 已有 2024、2025 年報與 2026Q2 季報；2026Q3 尚未公布（通常 11 月中） |
| 1521 大億 | 鉅亨網 API、MoneyDJ、經濟日報、Yahoo 股市、CMoney API、HiStock、其他媒體（Exa 找網址 → curl 原文） | `1521大億/202610_輿情新聞.md` | ✅ 11 個來源章節；PTT / Dcard / Mobile01 ⭕ 無新內容；財報狗 ❌ |
| 7276 小糸製作所 | 官網 IR（E-IR，`ssl4.eir-parts.net`） | `7276_AnnualReport_2025.md`（有価証券報告書 第126期，2025/4–2026/3） | ✅ 129 頁、cid 0 |
| 7276 小糸製作所 | 官網 IR（E-IR） | `7276_AnnualReport_2024.md`（有価証券報告書 第125期，2024/4–2025/3） | ✅ 124 頁、cid 0 |
| 7276 小糸製作所 | 官網 IR / 株探 TDnet | `7276_Quarter_2026Q1.md`（英文 Consolidated Earnings Report 1Q Fiscal 2026，2026-07-29） | ✅ 13 頁、cid 0；Q2 預定 2026-10-28 公布 |
| 7276 小糸製作所 | Yahoo JP 掲示板、株つぶやき（X）、株探、5ch、みんかぶ、日経、note、Shared Research、東洋経済 | `7276小糸製作所/202610_輿情新聞.md` | ✅ 10 個來源章節 |

> FY 命名：小糸英文資料稱 2026/3 結束之年度為「Fiscal 2025」，故 `AnnualReport_2025` = 2025/4–2026/3、`Quarter_2026Q1` = 2026/4–6。

**本期重點**

- **1521 大億**（在外股數 76,230,000 股）
  - 2026Q2 營收 9.997 億元（每股 13.11 元），年增 15.9%；毛利率 14.47%（去年同期 15.38%）。上半年營業利益 5,983 萬元（每股 0.78 元），年減 5.7%；上半年 EPS 0.94 元，主要來自去年低基期與所得稅利益，非本業改善。
  - Q3 營收轉弱：7–9 月合計約 8.29 億元（每股 10.87 元），年減約 8.2%；1–9 月累計 28.32 億元（每股 37.16 元），年增 6.71%，增幅收斂。
  - 經營權交棒：吳俊億 09-21 辭董事長，持股 32.5% 的大股東小糸（Koito）代表人岩邊惠 10-01 接任；副董事長懸缺。市場觀點分歧，利多是匯率風險可在集團內消化，利空是利潤可能被鎖定，公司性質從成長股轉為收息股。
  - 08-05 審計委員會更名為「審計暨風險管理委員會」；總經理莊智清獲解除競業禁止，公告未說明兼職何處，需留意利益衝突。
  - 散戶輿情冷清，CMoney 中性偏多。10-16 股價 25.65 元、PE 16.13、PB 1.04、殖利率 2.92%（HiStock）。
- **7276 小糸製作所**（2026-06-30 在外股數約 2.624 億股）
  - 1Q FY2026 純益 146.6 億日圓（EPS ¥55.77），年增 44.8%，大幅優於 QUICK 共識 102 億日圓；營業利益 165.6 億日圓（每股約 ¥63）。全年純益預估 395 億日圓（EPS ¥150.53）、股利 ¥58 維持不變，市場預期 10-28 公布 Q2 時可能上修。
  - FY2025（2026/3）純益年減 64%，為 165 億日圓（EPS ¥60.23），主因 LiDAR 與中國相關減損 215.5 億日圓（每股約 ¥82）；日經報導乘用車 LiDAR 開發已凍結。
  - 大型庫藏股：上限 2,500 萬股 / 500 億日圓（每股約 ¥190.5），執行期間 2026/6–2027/5；截至 9/30 已買回 631 萬股、169.9 億日圓（每股約 ¥64.7）。
  - 券商轉趨正面：SMBC 日興 9/8 調升評等；瑞穗（Mizuho）9/29 調升為「買進」，目標價從 ¥2,600 上調至 ¥3,400。みんかぶ目標價則為 ¥2,324，判斷為「割高」。10/16 收盤 ¥2,766（PER 17.9×、PBR 1.13×）。
  - 風險：中東局勢、美國關稅。5ch 有匿名爆料（勞動問題）、掲示板傳出 JAXA 合約說法，均未獲證實，且與 IR 資料無法對應。

## 2. 失敗或被擋網站

- **來源**：[Dcard](https://www.dcard.tw)｜**原因**：403 Cloudflare｜**已試過**：curl API → Firecrawl（402 額度用盡）→ Bright Data（未連線）→ Apify `rag-web-browser`（只找到 2017/2019 舊文，抓取 500）→ Playwright 403；Exa / WebSearch 索引無期間內新文
- **來源**：[Mobile01](https://www.mobile01.com)｜**原因**：Akamai 403｜**已試過**：curl → Firecrawl 402 → Bright Data 未連線 → Apify 搜尋模式（200 但僅舊串）→ Playwright 403
- **來源**：[財報狗](https://statementdog.com/analysis/1521)｜**原因**：AWS WAF｜**已試過**：curl 202 空內容 → Firecrawl 402 → Bright Data 未連線 → Apify 202 challenge → Playwright 403
- **來源**：[みんかぶ](https://minkabu.jp/stock/7276)｜**原因**：405 / 403 真人驗證｜**已試過**：curl 405 → Firecrawl 402 → Bright Data 未連線 → Apify `rag-web-browser` 405 → Playwright 403 → **Apify `apify/web-fetch` 成功**
- **來源**：X（7276，2026-07-17 ~ 09-17）｜**原因**：株つぶやき只涵蓋約一個月；`firecrawl_search` 無額度、Bright Data 未連線｜**已試過**：株つぶやき（curl）
- **來源**：東洋経済 `/search/?q=` 404、四季報 JS 外殼加付費牆｜已改用 `list/search?fulltext=` 全文搜尋

## 3. 資料缺失說明

- 1521 2026Q3 季報尚未公布（台股 Q3 財報期限 11/14）。
- 7276 2026Q2 決算預定 2026-10-28 公布，本次最新季報為 1Q。
- 7276 無英文版有価証券報告書 / 整合報告書，年報改用日文完整版（cid 0）；英文年度決算短信（Fiscal 2025：`ssl4.eir-parts.net/doc/7276/tdnet/2805938/00.pdf`）已驗證可用，未存檔。
- 1521 在 PTT、Dcard、Mobile01 期間內無討論（冷門股）。

## 4. 異常檔案刪除紀錄

無。依 Convert2md 規則，轉換成功的 3 份 PDF 已刪除，只保留 `.md`；PDF 轉檔後的圖片連結行已移除。

## 5. 本次使用的 MCP

| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_search`、`firecrawl_scrape` | ❌ **帳號級錯誤**：Insufficient credits（402），本次全程停用 |
| Bright Data | — | ❌ 未連線（MCP 需重新授權） |
| Apify | `rag-web-browser`、`apify/web-fetch`、`get-dataset-items` | Mobile01 搜尋、みんかぶ、note 搜尋（合計約 0.1 CU，無額度錯誤） |
| Playwright | `browser_navigate`、`browser_evaluate` | 小糸 IR 頁取得 E-IR PDF 連結、Shared Research；Dcard / Mobile01 / 財報狗 / みんかぶ 皆 403 |
| Exa | `web_search_exa` | 1521 輿情的索引替代（商周全文、自由財經線索） |
| pymupdf4llm | `convert_pdf_to_markdown` | Phase 4 PDF 轉 Markdown |

## 6. Phase 4 Convert2md

- 掃描 7 份 PDF，跳過 4 份已轉換，本次轉換 3 份（7276），**3 份成功**、0 份 CID 失敗、0 份空檔。
- 報告：`Log/conversion_summary.md`

## 7. Skill 維護

修改 `CollectsentimentAndReports/SKILL.md` §4（`.claude` 與 `.agents` 兩份已同步，`diff` 無差異）：

- §4.2 Yahoo 股市：發布時間改取單篇 JSON-LD `datePublished`，因 `pubtime` 在 HTML 中的順序不固定。
- §4.2 MoneyDJ：正文改取 JSON-LD `articleBody`；搜尋結果會混入同名公司，需逐則核對。
- §4.2 Dcard / Mobile01 / Goodinfo：Firecrawl 無額度時改用 Exa `web_search_exa` 作索引；Mobile01 補充 Apify 搜尋模式曾成功（200）。
- §4.2 財報狗：註明 Exa 索引的 e-report 版本落後，不可用來判斷是否有新財報。
- §4.4 株探：開示連結改為 HTML 包裝頁，PDF 實體網址要從包裝頁取出。
- §4.4 みんかぶ：curl 與 Apify `rag-web-browser` 回 405，改用 Apify `apify/web-fetch` 可讀。
- §4.4 note：Firecrawl 不可用時的備援改為 Apify `apify/web-fetch`，加 `formats: ["links"]` 取文章網址。
- §4.4 Yahoo JP 掲示板：冷門股一頁可涵蓋數月；株つぶやき需排除「爆上げ」導流垃圾帳號。
- §4.4 東洋経済：加入全文搜尋路徑 `toyokeizai.net/list/search?fulltext=`；四季報為付費 JS 外殼。
- §4.4 新增 2 列：日経個股新聞列表（SSR，`curl` 可讀）、E-IR 代管官網 IR（Playwright 取連結，`ssl4.eir-parts.net` 直接下載）。
