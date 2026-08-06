# 任務執行最終報告 - 2026/08（CollectsentimentAndReports）

- **執行日期**：2026-08-06（每日輪替表 Day 6 → `7203` Toyota，日股/美股雙重上市 TM）
- **公司**：Toyota Motor Corporation（7203.T / NYSE: TM）
- **資料夾**：`7203Toyota/`

---

## 0. 執行摘要
- **財報**：兩份最新年報（FY2025、FY2026）已存在→跳過；新下載並轉換**最新季報 FY2027 Q1（2026/4–6，8/4 發布）**。
- **輿情**：完成 2026/08 共 7 個來源的收集（GoogleNews、Reuters、SeekingAlpha、YahooFinanceJP、Minkabu、Xueqiu、Reddit），僅記錄真實爬取內容，失敗來源依 §5.4 誠實記錄。
- **本業隱憂**：Q1 淨利 +75.6% 主要靠一次性利益（Toyota Industries 處分、Hino 解除合併），**本業營益 -8.8%**；關稅與中東/伊朗情勢為主要利空。

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生的檔案 / 下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `7203Toyota` | Toyota 官方 IR（global.toyota） | `7203_Quarter_2027Q1.md` | 下載 PDF→轉 md 成功，CID=0，來源 PDF 已刪 |
| `7203Toyota` | （既存） | `7203_FY2025_annual_results.md` | 已存在，跳過 |
| `7203Toyota` | （既存） | `7203_FY2026_annual_results.md` | 已存在，跳過 |
| `7203Toyota` | Google News 綜合 | `202608_GoogleNews.md` | 更新成功（qz/just-auto/TechTimes/Nippon/Yahoo/Investing） |
| `7203Toyota` | Reuters | `202608_Reuters.md` | 更新成功（firecrawl_search 取導言逐字） |
| `7203Toyota` | Seeking Alpha | `202608_SeekingAlpha.md` | 更新成功（firecrawl_scrape，作者 Mike Zaccardi 8/4） |
| `7203Toyota` | Yahoo Finance JP | `202608_YahooFinanceJP.md` | 更新成功（掲示板買い~83%、股價 ¥2,983.5） |
| `7203Toyota` | みんかぶ Minkabu | `202608_Minkabu.md` | 更新成功（firecrawl_scrape，目標 ¥3,169、割高、個人売り、分析師買い） |
| `7203Toyota` | 雪球 Xueqiu | `202608_Xueqiu.md` | 部分成功（取得估值：PE 7.82、PB 0.94、殖利率 3.44%；討論串 JS 未渲染） |
| `7203Toyota` | Reddit | `202608_Reddit.md` | 部分成功（僅搜尋摘要，正文/日期未驗證，§5.4 記錄） |

## 2. 失敗或被擋網站
- **Reddit**（`reddit.com`）：內建 WebSearch 回 `400 not accessible`；firecrawl_scrape「we do not support this site」；brightdata 需 KYC（robots.txt）；apify rag-browser 0 成功；playwright 本次連線中斷。→ 依 §2.1 已跑完可用 MCP 鏈，改用 firecrawl_search 取得真實討論串 URL/摘要當替代。
- **雪球討論串**（`xueqiu.com`）：行情頁 firecrawl 取得成功，但「討論/熱帖」為 JS 動態載入未渲染；brightdata 逾時。→ 僅記錄頁面真實估值數據，未虛構貼文。
- **Minkabu / Seeking Alpha 文章頁**：內建 WebFetch 回 403 → 依 §2 換 firecrawl_scrape 成功。

## 3. 資料缺失說明
- 財報無缺：最新季報（FY2027 Q1）已補齊，年報 FY2025/FY2026 已在庫。
- Reddit 逐字輿情缺失，係該站封鎖爬蟲（非公司冷門），已誠實記錄並保留真實討論串連結供後續重試。
- 雪球逐字討論缺失，係 JS 動態渲染 + brightdata 逾時。

## 4. 異常檔案刪除紀錄
- `7203_Quarter_2027Q1.pdf`：轉換成功（CID=0）後依 Convert2md Step 1.4 刪除來源 PDF，保留 `.md`。
- 無因 <10KB / 無公司名 / CID 亂碼過多而刪除的檔案。

## 5. 本次執行使用的 MCP（強制填寫）
| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape` | 抓取 Seeking Alpha、Minkabu、雪球 TM 行情頁（內建 WebFetch 403 後遞補） |
| Firecrawl | `firecrawl_search` | 搜尋 Reuters 導言逐字、Reddit 真實討論串 URL（替代路徑） |
| Bright Data | `scrape_as_markdown` | 嘗試抓雪球討論、Reddit（雪球逾時、Reddit 需 KYC） |
| Apify | `apify/rag-web-browser` | 嘗試以真實瀏覽器抓 Reddit DD 貼文（失敗，0 succeeded） |
| Playwright | （navigate/snapshot） | 嘗試作為 Reddit 最後手段，本次 MCP 連線中斷未成 |
| GitHub | （Phase 5 推送/PR） | 推送變更並建立 Draft PR |

> 內建工具：`WebSearch`、`WebFetch`、`Bash`（curl 下載財報、markitdown/pdfminer 轉換）亦有使用。

---

## 附：本季重點（供後續分析參考）
- **Q1 FY2027（2026/4–6，發布 2026/08/04）**：營收 ¥13,525.4 億×10=¥13.525 兆（+10.4%）、營益 ¥1.06 兆（**-8.8%**）、母公司淨利 ¥1,477.0 億×10=¥1.477 兆（**+75.6%**）、EPS ¥120.69（前年 ¥64.56）、銷量 239 萬輛（-0.7%）。
- **全年 FY2027 財測上修**：營收 ¥54 兆、營益 ¥3.4 兆、淨利 ¥3.25 兆；匯率假設 1USD≈¥160。
- **資本政策**：庫藏股上限 ¥1 兆（約 $6.3B），最多 5 億股，執行至 2027/8。
- **利多**：財測上修、庫藏股、HV 需求、弱勢日圓、估值低（PE~7.8、PB<1、殖利率 3.4%）。
- **利空**：本業營益衰退、淨利靠一次性利益、美國關稅（FY2026 衝擊 ¥1,450bn）、中東/伊朗情勢干擾出口、中國 EV 競爭、股價對利多反跌。
