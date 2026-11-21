# collectState 執行報告 — HK — 2026/11/21

- **資料窗口**：2026-10-21 ~ 2026-11-21｜**保留截止日**：2026-08-21
- **資料夾**：`hk_state/`（執行後共 63 個檔：60 份單篇 `.md`＋`202611_HK_輿情新聞.md`＋`StateAnalysis.md`＋`0.Index.md`）
- **執行方式**：子代理人 HK-A（官方＋報告＋中國房地產）、HK-B（新聞＋REIT＋輿情）平行收集；兩者 05:41 UTC 因帳號 5 小時額度上限（HTTP 429）中斷，06:20 額度重置後由主代理人恢復續跑完成。HK-B 一度卡在 Bash 權限確認，使用者核准後繼續。主代理人負責月檔合併、轉檔、分析與 push。

## 1. 收集成果
| 類別 | 新增檔案數 | 代表檔案 | 備註 |
| :--- | :--- | :--- | :--- |
| A 官方 | Data 約 16＋Policy 1 | `20261028_Data_RVD_私人住宅售價指數9月.md`、`20261120_Data_HKMA_HIBOR隔夜1M每日.md` | HKMA、RVD、統計處、土地註冊處、中原 CCL、Fed；旅發局 10 月 ❌ |
| B 報告 | 香港 4（萊坊、第一太平戴維斯、JLL；高力／CBRE 僅索引） | `20261028_Report_KnightFrank_香港市場報告2026Q3.md` | 評級機構評論未查 |
| C 新聞 | 7 篇全文＋月檔 12 則 | `20261116_News_KPMG_港府擬豁免新上市REIT印花稅.md` | AAStocks、KPMG、智通、The Standard、Now 財經 |
| D REIT | 11 份公告＋報價 1 | `20261112_REIT_HKEX_00823中期業績.md`、`20261029_REIT_HKEX_02191非常重大出售聯合公告.md` | 11 檔逐檔查 HKEXnews；名單無變動 |
| E 輿情 | 月檔 10 平台 | （無單篇長文） | ✅ 東方財富股吧；⚠️ 雪球、LIHKG、香港討論區、長橋、X（索引）；❌ 高登、Reddit；⭕ PTT、Mobile01 |
| F 中國 | 23（Data 7、Report 8、News 5、Policy 2，另 NBS 解讀 1） | `20261116_Data_NBS_CN房地產市場1至10月.md`、`20261102_Report_KnightFrank_CN北京甲級寫字樓2026Q3.md` | NBS、中指、克而瑞、人行、財政部、萊坊／JLL 一線寫字樓、華發／萬科債務 |

**本期重點**：
1. 港元利率：1M HIBOR 2.712%（11/20）、基本利率 4.25%；FOMC 10/28 維持 3.75%~4.00%，2 票主張再升息。
2. 香港住宅：RVD 售價 YoY +9.34%、租金 +6.15%（9 月）；CCL 月跌 1.47%（11/20）；10 月合約 YoY -21.0%。
3. 領展：中期 DPU 127.25 仙（+0.3%）、香港續租 -7.5%；出售彌敦道 700 號 HK$23 億（每單位 0.888，較估值折讓 8.6%）；下半年回購 HK$10~20 億（每單位 0.39~0.77）。
4. 順豐房託：每單位現金 3.28 私有化（較 11/20 收盤 +2.5%）；招商局商業完成收購紅磡學生公寓（每單位 0.468）。
5. 中國：1~10 月開發投資 -21.6%、到位資金 -21.9%、土地出讓 -25.8%；一線寫字樓四城租金全數季跌 0.5%~3.1%；華發集團評級遭降但無公開債違約證據。

## 2. 失敗或被擋網站
- **來源**：旅發局 10 月訪港旅客｜**原因**：查無官方數字｜**已試過**：WebSearch（只有 9 月媒體摘要）
- **來源**：CBRE 亞太 PDF、高力新聞稿｜**原因**：HTTP 403｜**已試過**：curl（殘檔已刪）→ 只取搜尋索引
- **來源**：惠譽評論頁｜**原因**：JS 外殼｜**已試過**：curl
- **來源**：中信建投受託報告 PDF｜**原因**：curl 網路錯誤（rc=000）｜**已試過**：curl（依 collectStk §3.3 零重試）
- **來源**：高登、Reddit、moomoo｜**原因**：Firecrawl／Bright Data／Apify／Playwright 需人工授權｜**已試過**：Exa（moomoo 改用長橋社區索引）
- **來源**：恒生 REIT 指數｜**原因**：無免授權來源｜**已試過**：—（以 HKEX 殖利率表代替）
- **來源**：證券日報（中國經濟網）LPR 文｜**原因**：`state_tools convert` 三種轉換器都判「內容過短 0 字」｜**已試過**：主代理人以 regex 萃取正文 955 字另存 `.md`，原 `.shtml` 刪除

## 3. 資料缺口說明
- 10 月訪港旅客（官方未取得；`Analysis/HkStateResult.md` 的「460 萬、+12%」與 2025 年 10 月數字相同，疑誤植）、香港 10 年期政府債殖利率、恒生 REIT 指數、各 REIT 浮息借款比例與 NOI yield、10 月單月住戶中長期貸款、華發 MTN006（11/17 到期）兌付、越秀中期分派正確數字（RMB 0.0265 vs 0.0271）、評級機構對港 REIT 評論。

## 4. Phase 1 清理紀錄
- 首次執行（`hk_state/` 新建），dry-run 與實刪皆 0 檔：無。

## 5. Phase 4 轉檔紀錄
- **Convert2md**（掃描範圍限定 `/home/user/FinancialReport/hk_state`）：總 PDF 19｜成功 19｜CID 失敗 0｜未產生 0；成功後刪除原 PDF 19 份（`Log/conversion_summary.md` 已合併 JP／HK 兩段）。
- **state_tools convert**：Excel（.xls，經 LibreOffice）、JSON、HTML 等 41 份 → 成功 40、失敗 1（證券日報 `.shtml`，已人工萃取正文補成 `.md`）。
- **finalize**：manifest 2 份 60 筆 → 補來源標頭 60 份、索引 61 筆；無「沒有 manifest」檔。
- **check**：✅ 全部通過（StateAnalysis 199 行，含第五章中國房地產）。
- 失敗保留的原檔：無。

## 6. 本次使用的 MCP
| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| Exa | `web_search_exa`、`web_fetch_exa` | 新聞、香港討論區／LIHKG／雪球／長橋輿情索引、券商目標價 |
| pymupdf4llm | `convert_pdf_to_markdown` | 19 份 PDF 轉 Markdown |
| yfinance | `get_historical_stock_prices`（HKDTWD=X） | 港元／台幣匯率 |
| Firecrawl、Bright Data、Apify、Playwright | — | ❌ 呼叫回「MCP tool call requires approval」，本次全程未用 |
| 內建 | `curl`、`WebSearch` | HKMA API、RVD Excel、info.gov.hk 新聞稿、HKEXnews API／PDF、NBS、中指、財政部、萊坊／第一太平戴維斯 PDF、東方財富股吧、PTT |

## 7. Skill 維護
- `collectState` §4.2 A 表：改寫 HKMA（每日 API 與 3M 月度公報路徑）、RVD（`his_data_{n}.xls` 編號對照、第 29 欄、Last-Modified）、土地註冊處與統計處（經 `info.gov.hk` 逐日索引）、旅發局（10 月查無）、中原 CCL（新網址與 `__NUXT__`）、Fed（聲明網址）並標 `[2026-11]`。
- §4.2 B：萊坊／第一太平戴維斯 PDF 可直接下載、CBRE／高力 403、惠譽 JS 外殼。
- §4.2 C：AAStocks 冷門 REIT 列表停更 → 改 Exa；KPMG 稅務快訊可讀。
- §4.2 D：名單核對改用 HKEX widget API（token 取得法）、單位變動月報表口徑、恒生 REIT 指數無免授權來源；02191 標註私有化除牌。
- §4.2 E：Exa 作為香港論壇輿情備援（香討 archiver、LIHKG 分類頁、長橋、雪球 news 流）；PTT 無港 REIT 討論。
- §5 中國表：NBS 70 城頁結構、中指云、財政部、萊坊各城 PDF 來源。
- `.claude/skills/collectState/` 與 `.agents/skills/collectState/` 同步（`diff -r` 無差異）。日本部分的維護見 `Log/collectState_JP_Summary_20261121.md` §7。
