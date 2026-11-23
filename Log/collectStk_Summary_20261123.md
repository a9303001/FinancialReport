# 任務執行最終報告 - 2026/11/23

- **執行日**：2026-11-23（輪替表第 23 日 → 01816 中廣核電力）
- **公司資料夾**：`01816中廣核電力/`
- **觸發**：排程 `/goal Run Routines_CollectsentimentAndReports.md`（舊檔名，2026-11-21 已改名為 `Routines_collectStk.md`）

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| 01816 中廣核電力 | HKEXnews JSON API（英文版 `2026102800466.pdf`） | `01816_Quarter_2026Q3.md`（18 頁，0 個 `(cid:`，原 PDF 405KB 轉檔後已刪） | ✅ 新增 2026 Q3 季報 |
| 01816 中廣核電力 | 既有檔案盤點 | `01816_AnnualReport_2024.md`、`01816_AnnualReport_2025.md` | ✅ 已有 2 份年報，跳過 |
| 01816 中廣核電力 | HKEX、深交所公告 API、AAStocks、新浪、富途、HKEX 權益披露、雪球、東方財富股吧、LIHKG、HKET | `202611_輿情新聞.md`（資料範圍 2026-10-23 ~ 2026-11-23） | ✅ 新建 |

**本期重點**（每股換算基準：總股本 50,531,816,547 股，2026-10-31）：
- 利多
  - 2026 Q3 歸母淨利 34.98 億元人民幣（每股約 0.069 元），年增 36.08%；前三季 96.03 億（每股約 0.190 元），年增 12.75%；前三季營收 510.98 億（每股約 1.011 元），年增 3.98%。主因：惠州 1、2 號及蒼南 1 號商運。美銀（目標價 4 港元）、摩通指業績勝預期。
  - 國信上調 2026~2028 淨利預估至 106.0／126.9／135.8 億（預估 EPS 0.21／0.25／0.27 元）；花旗重申買入（目標價 3.8 港元），廣東電價每 +10 元/MWh → 2027 淨利 +2.55 億（每股約 0.005 元）。
  - 廣東 10、11 月月度電價 0.457／0.474 元/度；雪球流傳廣東 2027 方案初稿取消核電單向差價合約（尚待官方確認，公司 11-10 稱方案未出台）。
  - 蒼南 4 號（華龍一號，1,215MW）11-10 開工；在建 19 台。
  - 廣核轉債（49 億，每股約 0.097 元）10-29 ~ 11-13 已有 10 日達強贖價 4.654 元，預計觸發強贖 → 減債。
- 利空
  - 負債比率 68.08%（較 2025 年底 +2.50pct）；前三季資本開支 377.23 億（每股約 0.747 元）> 經營現金流 265.67 億（每股約 0.526 元）；短借 +35.6%、應付債券 +93.6%。
  - Q4 大修天數將略多於去年同期；新機組首爐燃料便宜與免稅期屬階段性紅利。
  - 新機組計畫電價 0.4153 元入市後均價有下行壓力；2027 廣東核電市場化電量可能由 312 億擴大至 850~900 億度（網友依初稿估算）。
  - 中信證券資管系一個月減持約 1.3 億股 H 股（3.40~3.45 港元）；可轉債轉股潛在稀釋約 2.7%。
- 必備指標（Q3 季報）：負債比率 68.08%；OPM（營業利潤 176.95 億 / 利潤總額 176.61 億）約 100.2%；Q3 EPS 0.0693 元，前三季 EPS 0.1902 元。

## 2. 失敗或被擋網站
- **來源**：[moomoo 社區](https://www.moomoo.com/hant/stock/01816-HK/community)｜**原因**：導向 `moomoo.com/403`「Operations too frequent」｜**已試過**：Playwright ×2 → 403；`firecrawl_scrape` → 403 頁；Apify `apify--web-fetch` → MCP 60 秒逾時
- **來源**：[雪球個股頁](https://xueqiu.com/S/SZ003816)｜**原因**：Bright Data 45 秒逾時｜**已試過**：Bright Data → 逾時；`firecrawl_scrape`（stealth）→ ✅ 成功（單篇改用 Exa 索引）
- **來源**：新浪 `cj.sina.cn`、`/stock/relnews/` 單篇｜**原因**：curl rc=35｜**已試過**：curl → `firecrawl_scrape` directQuote ✅

## 3. 資料缺失說明
- 年報：2025 年報為最新（2026 年報預計 2027 年 3 月公布）。季報：2026 Q3 為最新（Q4 併入年報）。
- LIHKG、香港經濟日報：查得到站但三個月內無 01816 新內容（⭕）。
- 廣東 2027 年電力市場化交易方案尚未正式出台；廣核轉債強贖尚待公司正式公告。

## 4. 異常檔案刪除紀錄
- 無（`01816_Quarter_2026Q3.pdf` 為轉檔成功後依規刪除的來源 PDF，非異常檔）

## 5. MCP 預檢與使用紀錄
- **預檢結果**：可用：Firecrawl、Bright Data、Apify、Exa、Playwright、yfinance、curl｜停用：無
- **使用者待辦**：無（本次排程執行所有連接器皆未出現 `requires approval`）

| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape` | 預檢；新浪 rc=35 單篇（問董秘、格隆匯、證券之星）；雪球個股頁（stealth）；moomoo（失敗） |
| Bright Data | `scrape_as_markdown` | 預檢；雪球個股頁（逾時） |
| Apify | `apify--web-fetch` | 預檢；moomoo（逾時） |
| Exa | `web_search_exa` | 預檢；雪球單篇索引 |
| Playwright | `browser_navigate`、`browser_network_requests`、`browser_network_request` | 預檢；富途新聞；moomoo（403）；LIHKG 搜尋 API |
| yfinance | `get_historical_stock_prices` | 預檢（1816.HK 11-20 收 3.41 港元） |
| pymupdf4llm-mcp | `convert_pdf_to_markdown` | Q3 季報轉 Markdown |

## 6. Phase 4 Convert2md
- `01816中廣核電力/01816_Quarter_2026Q3.pdf` → `01816_Quarter_2026Q3.md`（43.6KB，0 個 `(cid:`，含公司名與資產負債表數字），已移除 `pdf_images` 圖片連結並刪除來源 PDF。
- 首次呼叫 `save_path` 填資料夾回 `[Errno 21] Is a directory`，改填完整檔案路徑後成功。

## 7. Skill 維護
- §4.3 moomoo 列：改寫——同 session 先開富途後 moomoo 會被 403「Operations too frequent」（Playwright、Firecrawl 皆同），要排在富途之前開；Apify web-fetch 逾時；刪除過時的「Firecrawl 需額度」敘述。
- §4.3 HKEX 權益披露列：新增「A 股類別大股東減持附 CNY 代價＋第 27 欄寫可交换公司债券进入换股期 = 可交換債換股，非市場拋售」判讀。
- §5.6 雪球：Bright Data 對個股頁 2026-11 逾時；Firecrawl stealth + directQuote 可取個股頁討論流。
- §9：`convert_pdf_to_markdown` 的 `save_path` 必須是完整 `.md` 檔案路徑。
- `.claude/skills/collectStk/SKILL.md` 與 `.agents/skills/collectStk/SKILL.md` 已同步（`diff` 無差異）。
