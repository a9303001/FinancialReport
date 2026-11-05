# 任務執行最終報告 - 2026/11/06

- **執行日**：2026-11-06 台北時間（排程觸發於 UTC 2026-11-05 20:01）→ 輪替表第 6 日 → `7203` Toyota
  - 備註：沿用 `_20261101`～`_20261105` 報告「以台北日期對照輪替表」的做法；第 5 日（3445 RS）已於 UTC 11-04 20:01 那次執行完畢（`Log/CollectsentimentAndReports_Summary_20261105.md`），本次不重跑。
- **公司資料夾**：`7203Toyota/`

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| 7203 Toyota | 本機盤點 | — | 年報 FY2025（`7203_FY2025_annual_results.md`）、FY2026（`7203_FY2026_annual_results.md`）已存在 |
| 7203 Toyota | 株探開示清單 → `tdnet-pdf.kabutan.jp` | `7203Toyota/7203_Quarter_2027Q2.md` | 2026-11-05 13:55 發布的 FY2027 Semi-Annual Consolidated Financial Results（英文，14 頁），0 個 `(cid:`；取代 2027Q1 成為最新季報 |
| 7203 Toyota | 株探、日經、Reuters、Yahoo Finance、Seeking Alpha、Yahoo JP 掲示板、X（firecrawl_search）、5ch、Reddit（Apify） | `7203Toyota/202611_輿情新聞.md`（新建） | 資料範圍 2026-10-06 ~ 2026-11-06 |

**本期重點**（每股以 2026-09-30 自己株式除外 11,779,620,513 股換算）：
- 11/5 決算：上期營收 26.96 兆円（+9.5%，每股約 2,289 円）、營業利益 2.19 兆円（+9.2%，每股約 186 円）、淨利 2.24 兆円（+26.1%，每股約 190 円）。通期營業利益 3.4 → 3.9 兆円（每股約 331 円）、淨利 3.25 → 3.57 兆円（每股約 303 円，仍年減 7.2%）。Q2 單季營業利益 +34%，遠超 Reuters 事前預期 +18%。
- 資本政策：回購上限 1 → 1.3 兆円（每股約 110 円）並對四家損保公司 TOB（2,725 円、約 1.09 億股、約 2,963 億円）；註銷 12 億股；Reuters 報導 2031/3 前股東回饋最多 14 兆円（每股約 1,189 円）、R&D＋capex 至少 22 兆円。
- 股價 11/5 +16.68% 收 3,533 円（Reuters：近 40 年最大單日漲幅），出来高 1.05 億股；PER 11.6、PBR 1.11、殖利率 2.83%。同日美國期中選舉民主黨大勝帶動「關稅放寬」預期，但日經指出關稅仍將延續。
- 風險：中國 4~9 月銷量 -25%、中東出口 -26%、資材漲價 9,800 億円（每股約 83 円）、カナダ關稅壓低約 4,000 億円（每股約 34 円）；株探試算下半年淨利年減約 36%。
- 流通股數：2026/3 底約 130.3 億股 → 2026/9 底約 117.8 億股（-9.6%），主要來自 TOB 回購與市場回購。
- 資料校正：日經 11/5 文章寫「7~9 月純利益 +34% 1兆1276億円」，依決算短信計算應為單季**營業利益**（單季淨利為 7,594 億円、-18.5%），已在輿情檔註明。

## 2. 失敗或被擋網站
- **來源**：[日經 決算相關文章](https://www.nikkei.com/article/DGXZQOFD148W60U6A011C2000000/)｜**原因**：付費牆（只取得導言段）｜**已試過**：`curl`
- **來源**：[Seeking Alpha](https://seekingalpha.com/news/4666430-toyota-shares-rally-as-automaker-lifts-annual-profit-forecast)｜**原因**：僅取索引摘要（依 §4.1 不跑 scrape）｜**已試過**：`firecrawl_search`
- 其餘來源皆成功或確認無新內容。

## 3. 資料缺失說明
- Reuters 所提「14 兆円股東回饋／22 兆円投資」出自決算簡報，本次下載的決算短信與自社株買い公告中沒有這兩個數字；簡報 PDF 已確認存在但未逐頁核對、未存檔（非年報／季報）。
- Yahoo JP 掲示板單頁只涵蓋 11/5 22:47 ~ 11/6 04:51（決算後討論量大）。
- Reddit 搜尋結果全部與 Toyota 無關（2025 年 $RDDT 討論串），記為無新內容。
- みんかぶ、note、東洋経済、Yahoo JP 株つぶやき本次未查（時間優先處理決算與主要媒體）。

## 4. 異常檔案刪除紀錄
- 無（`7203_Quarter_2027Q2.pdf` 轉檔成功後依 Convert2md 慣例刪除原始 PDF，保留 `.md`）

## 5. 本次使用的 MCP
| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| pymupdf4llm | `convert_pdf_to_markdown` | Q2 決算短信 PDF 轉 Markdown（`save_path` 必須填完整 `.md` 檔案路徑，填資料夾會回 `Is a directory`） |
| yfinance | `get_historical_stock_prices` | 7203.T 三個月日線（11/5 OHLC 為 null，改用株探） |
| Firecrawl | `firecrawl_search`、`firecrawl_scrape` | Reuters 搜尋與全文、Seeking Alpha 與 X 索引 |
| Apify | `call-actor`（`trudax/reddit-scraper-lite`）、`get-dataset-items` | Reddit r/stocks |

## 6. Phase 4 Convert2md
- 新增 1 個 PDF → `7203_Quarter_2027Q2.md`（51.8KB，0 個 `(cid:`），已移除 `pdf_images` 圖片連結並刪除原始 PDF。

## 7. Skill 維護
- 修改 §4.4 株探列：補充大型股決算日新聞列表每頁只涵蓋數天；列表 `<time>` 可能只顯示 15:30，真實發布時間以單篇內文開頭為準。兩份 SKILL.md 已用 `diff` 確認一致。
