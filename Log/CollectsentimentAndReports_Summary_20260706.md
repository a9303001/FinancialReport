# 任務執行最終報告 - 2026/07/06

- **執行公司**：`7203` Toyota Motor Corporation（トヨタ自動車, 日股 TSE 7203 / 美股 NYSE:TM 雙重上市）
- **輪替日對照**：每月 6 日 → Toyota（本日 2026-07-06 命中）
- **資料夾**：`FinancialReport/7203Toyota/`

---

## 1. 成功紀錄

| 股號/名稱 | 資料來源 | 產生的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `7203Toyota` | Yahoo!ファイナンス JP 掲示板 | `202607_YahooFinanceJP.md` | ✅ 新增，72 則真實貼文（2026/7/6 盤中）整理成 5 主題 |
| `7203Toyota` | 雪球 Xueqiu (S/TM) | `202607_Xueqiu.md` | ✅ 新增，4 則真實貼文/公告（2026/7/2–7/5） |
| `7203Toyota` | Google News | `202607_GoogleNews.md` | ✅ 新增，4 篇真實新聞 |
| `7203Toyota` | Seeking Alpha | `202607_SeekingAlpha.md` | ✅ 新增，4 篇真實文章標題＋官方描述（正文付費牆） |
| `7203Toyota` | Reuters | `202607_Reuters.md` | ⚠️ 部分，2 則窗口內真實標題/日期/摘要（全文被封鎖） |
| `7203Toyota` | Minkabu | `202607_Minkabu.md` | ✅ 新增，估值指標＋決算 AI 要約 |
| `7203Toyota` | Reddit | `202607_Reddit.md` | ⚠️ 窗口內查無實質新串；誠實標註 apify 抓到之串為 2025-07（窗口外） |

### 財報狀態（Phase 2）
- **本次未下載任何新財報**，因既有檔案已涵蓋最新可得報告：
  - `7203_FY2025_annual_results.md`（年報，2025-05-08 公布）✅
  - `7203_FY2026_annual_results.md`（年報，2026-05-08 公布，最新年報）✅
  - `7203_FY2026_Q3_results.md`（季報，2026-02-06 公布，最新可得季報）✅
- 符合「最新 2 年報 + 1 季報」要求。下一份季報 FY2027 Q1（2026 年 4–6 月）依 Toyota 慣例約於 **2026-08 上旬** 公布，本日（2026-07-06）尚未發布，故無新季報可下載。

---

## 2. 失敗或被擋網站
- **Reuters（全文）**：內建 WebFetch 反爬被擋；`firecrawl_search` 只回 sitemap 空殼；`brightdata scrape_as_markdown` 回「reuters.com 被封鎖，7 天後再試」。→ 依 §2 已跑 MCP 鏈，最終以 Bright Data 搜尋引擎取得真實標題/日期/摘要，全文無法取得（反爬 + DataDome）。
- **Reddit**：`firecrawl_scrape` 明確拒絕 reddit.com；`brightdata` 對最新串回空；`apify（reddit-scraper-lite）` 成功抓取但唯一有實質留言之串為 2025-07-29（超出 3 個月窗口）。已依 §5.4 誠實記錄。
- **Seeking Alpha**：文章正文為付費牆，僅能取得標題與官方描述（非封鎖，屬付費牆限制）。

---

## 3. 資料缺失說明
- **FY2027 Q1 季報**：尚未公布（預計 2026-08 上旬），非缺失，屬時序未到。
- **Reddit 窗口內輿情**：2026-04~07 期間 r/ValueInvesting、r/stocks、r/wallstreetbets 無新的、可抓取實質留言的 Toyota 專串，多為舊帖延續；已誠實標註，非 AI 生成填充。
- **Reuters / Seeking Alpha 全文**：反爬與付費牆限制，僅取得標題/摘要層級資訊。

---

## 4. 異常檔案刪除紀錄
- 無。本次未下載任何財報 PDF/HTML，故無因 <10KB、缺公司名稱或 `(cid:` 亂碼而刪除之檔案。
- Phase 4 Convert2md：資料夾內無待轉換之 PDF/HTML（全為 `.md`），本次不需轉換。

---

## 5. 本次執行使用的 MCP（強制填寫）

| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape` | 抓 minkabu.jp/stock/7203、Yahoo JP 7203 掲示板（成功）；嘗試 Reddit 串（被拒） |
| Firecrawl | `firecrawl_search` | 搜 Toyota 財報/關稅新聞（qdr:m）、Reuters/Seeking Alpha/Reddit 網域討論串 |
| Bright Data | `scrape_as_markdown` | 抓 xueqiu.com/S/TM（成功）；Reddit 串（1 空 1 部分）；Reuters 文章（被封鎖） |
| Bright Data | `search_engine`（google） | 取得 Reuters Toyota 真實標題/日期/摘要 |
| Apify | `call-actor`（trudax/reddit-scraper-lite） | 抓 Reddit「Why isn't anyone talking about Toyota」串（成功 26 項） |
| Apify | `get-dataset-items` | 讀取上述 Reddit dataset（1 貼文＋25 留言） |

- 內建工具亦使用：`WebFetch`（Yahoo Finance 兩篇文章全文摘要）、`WebSearch`、`Bash`、子代理（general-purpose）讀取過大暫存檔抽取貼文。
- 未使用 Playwright（前面 MCP 已取得足量內容，未觸發鏈末工具）。

---

## 6. 內容重點摘要（跨來源交叉一致）
- **空方主軸**：關稅衝擊（FY26 直接衝擊約 $88.1 億、北美轉營業虧損）、伊朗/中東戰爭致原物料成本上升（約 6,700 億日圓 / 43 億美元）、FY27 營業利益指引大降至約 3 兆日圓（年減約 20%）、連四季獲利下滑、BYD/中國 EV 競爭、豐田家族治理疑慮。
- **多方主軸**：估值便宜（P/E ~9.5–9.7、P/B ~0.92–1.05）、殖利率 3.44–3.47% 且連續增配、約 $810 億現金、BEV FY26 銷量 +68%、分析師目標價 3,489–3,658 円（約 +30–34% 上檔）、Joby eVTOL 新題材。日股散戶當日情緒偏多（約 59% 買 vs 25% 賣），關注 2,900 / 3,000 円關卡。

---

*本報告由 CollectsentimentAndReports skill 自動產生（每日輪替排程，2026-07-06 對應 Toyota 7203）。*
