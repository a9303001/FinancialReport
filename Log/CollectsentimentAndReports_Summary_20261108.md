# 任務執行最終報告 - 2026/11/08

- **執行日**：2026-11-08 台北時間（排程觸發 UTC 2026-11-07 20:01；輪替表第 8 日 → 2832 台產）
  - 日期判定沿用前幾次執行慣例（以台北日期為準：UTC 11-05 20:09 → 第 6 日 7203、UTC 11-06 20:07 → 第 7 日 UHS），避免重複執行 UHS。
- **公司資料夾**：`2832台產/`

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生/下載的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| 2832 台產 | 鉅亨 API、MoneyDJ、工商時報、經濟日報、Yahoo股市、CMoney API、PTT、HiStock、yfinance | `2832台產/202611_輿情新聞.md`（新建） | ✅ 補 2026-10-09 ~ 11-07 輿情 |
| 2832 台產 | TWSE 電子書（firecrawl）、官網 IR | 無新財報 | ⭕ 既有 2024/2025 年報 + 2026Q2 季報；Q3 PDF 尚未上傳 |

**本期重點**（每股以 2.5354 億股換算）：
- 10/29 董事會通過 Q3 財報：前三季營收 80.62 億元（每股約 31.80 元）、淨利 11.68 億元（EPS 4.61 元），約為 2025 全年淨利 12.43 億元的 94%；每股淨值約 49.27 元、負債比率約 53%、OPM 約 100%。
- Q3 單季淨利約 3.24 億元（每股約 1.28 元），季減約 24%、年減約 2% → 上半年 +39.8% 的高成長在 Q3 收斂。
- 9 月營收 8.68 億元（每股約 3.42 元）年增僅 0.49%，1~9 月累計增幅降至 5.8%。
- 自結前三季 11.73 億元 / EPS 4.63 元，正式數字小幅下修為 11.68 億元 / 4.61 元。
- 金控產險同業前三季年增 28~32%，台產約 +25%，略落後。
- 10 月入選臺灣璞玉指數；股價一個月跌約 6%，11/06 收 53.6 元（PB 約 1.09、TTM PE 約 9.2、殖利率約 6.5%）。
- 社群（CMoney 4 則、PTT/Dcard/Mobile01 無新文）討論冷清，焦點在「前三季 EPS 已超過去年全年」，沒人提到成長放緩。

## 2. 失敗或被擋網站
- **來源**：[TWSE 電子書 doc.twse.com.tw](https://doc.twse.com.tw/server-java/t57sb01)｜**原因**：`curl` GET/POST 皆回安全性封鎖頁｜**已試過**：curl ×2 → `firecrawl_scrape` 成功取得清單
- **來源**：Bright Data `search_engine`（google）Dcard 查詢｜**原因**：兩次「the search engine answer was not JSON」｜**已試過**：Bright Data ×2 → `WebSearch`（allowed_domains）
- **來源**：`firecrawl_search` `site:dcard.tw`、`site:mobile01.com`｜**原因**：0 筆（`tbs: qdr:m`）｜**已試過**：Bright Data、WebSearch 補查

## 3. 資料缺失說明
- **Q3 2026 財報 PDF**：董事會 10/29 已通過，但 TWSE 電子書清單（firecrawl 讀取）只有 115 Q1/Q2 的 `_AI2`/`_AIB`；官網 `115年第3季財務報告.pdf` 回 404。保險業 Q3 法定申報期限為 11/14 前，屬「已公告重訊、PDF 尚未上傳」，下次執行再下載。
- **2025 前三季淨利 9.34 億元**：來自 WebSearch 結果摘要（旺得富 2025-10 報導），未以原始頁面核實；Q3 年比推算依此數字，待 Q3 正式財報比較期驗證。
- **10 月營收**：依規定 11/10 前公告，抓取時尚未公告。
- PTT / Dcard / Mobile01：冷門低流動性存股標的，長期無新討論（PTT 最新一篇停在 2025-04-18）。

## 4. 異常檔案刪除紀錄
- 無（官網猜測網址 `115年第3季財務報告.pdf` 回 404 HTML，只存在暫存區，未寫入 repo）。

## 5. 本次使用的 MCP
| MCP 服務名稱 | 工具/函式 | 用途 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape` | 讀取 TWSE 電子書清單（確認 Q3 PDF 尚未上傳） |
| Firecrawl | `firecrawl_search` | Dcard / Mobile01 索引（0 筆） |
| Bright Data | `search_engine`（google） | Dcard（兩次失敗）、Mobile01（只回行情站） |
| yfinance | `get_historical_stock_prices` | 2832.TW 近一個月日線 |

其餘使用內建 `curl`（鉅亨 API、MoneyDJ、工商時報、經濟日報、Yahoo股市、CMoney API、PTT、HiStock、台產官網）與 `WebSearch`。無帳號級錯誤。

## 6. Phase 4 Convert2md
- 本次無新下載 PDF，略過。

## 7. Skill 維護
- §4.2 新增一列「TWSE 電子書 `doc.twse.com.tw/server-java/t57sb01`」：`curl` 被安全性封鎖，`firecrawl_scrape`（basic）可讀清單，用來判斷新季報是否已上傳（`_AI2` 個別財報、`_AIB` 英文版）。
- §7.3 台股 ③ 官網 IR 補上台產 2832 的財報 PDF 路徑規則（`tfmi.com.tw/investors-Financial`）。
- `.claude/` 與 `.agents/` 兩份 SKILL.md 已用 `diff` 確認一致。
