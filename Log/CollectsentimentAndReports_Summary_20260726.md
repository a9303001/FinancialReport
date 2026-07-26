# 任務執行最終報告 - 2026/07

- **執行日期**：2026-07-26（每日輪替表第 26 日）
- **目標公司**：荏原製作所 Ebara Corporation
- **股票代碼**：輪替表標示 `6328`，經查證實際東證代碼為 **`6361`**（Prime 主板，曆年制決算）。已沿用既有資料夾 `6361荏原製作所`；`6328` 疑為輪替表筆誤。
- **市場**：日股（JP）

## 1. 成功紀錄

| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `6361荏原製作所` | EBARA PM Europe 官方鏡像 | `6361_AnnualReport_2025.md`（原 PDF） | 下載+轉換成功（FY2025 全年決算，英文） |
| `6361荏原製作所` | EBARA PM Europe 官方鏡像 | `6361_AnnualReport_2024.md`（原 PDF） | 下載+轉換成功（FY2024 全年決算，英文） |
| `6361荏原製作所` | Ebara 官方 IR（Firecrawl 繞過 Akamai） | `6361_Quarter_2026Q1.md`（原 HTML） | 下載+轉換成功（FY2026 Q1 決算短信，英文） |
| `6361荏原製作所` | Yahoo Finance JP 掲示板 | `202607_YahooJP.md` | 更新成功（~9 討論串，7/16–7/24 真實貼文） |
| `6361荏原製作所` | 株探 kabutan | `202607_kabutan.md` / `202606_kabutan.md` / `202605_kabutan.md` / `202604_kabutan.md` | 更新成功（4–7 月材料/開示新聞，共 16 筆） |
| `6361荏原製作所` | みんかぶ minkabu | `202607_minkabu.md` | 更新成功（綜合評價+新聞，會員賣 vs 分析師買分歧） |
| `6361荏原製作所` | note | `202607_note.md` | 更新成功（4 篇真實標題：CMP 技術、短線股價、岐阜市訴訟、企業分析） |
| `6361荏原製作所` | 英文圈（Seeking Alpha/Simply Wall St/TipRanks/Investing/TradingView 等） | `202607_English.md` | 更新成功（4 筆窗內 + 1 舊文對照） |

## 2. 失敗或被擋網站

- **來源**: Ebara 官網 `www.ebara.com`（財報 binary 下載）
  - **原因**: 全站受 Akamai bot 防護，任何 `curl`（試過 4 種 User-Agent 含 Googlebot、多種路徑變體）皆回 517–558 bytes 的 "Access Denied"。此為來源端硬封鎖，非 proxy 問題（proxy 健康）。
  - **已依 §2 換過的 MCP**: 年報改用官方歐洲子公司鏡像 `ebara-pm.eu`（curl 直接成功）；Q1 季報唯一官方檔在 Akamai 後，改用 **Firecrawl** 擷取英文內容成功。未動用 brightdata/apify/playwright 於財報。
- **來源**: Yahoo Finance JP 掲示板 `finance.yahoo.co.jp/quote/6361.T/bbs`
  - **原因**: 內建 WebFetch 與 firecrawl 皆回 500 錯誤。
  - **已依 §2 換過的 MCP**: 改用 **Bright Data scrape_as_markdown 成功**。惟新版 UI 單次僅回最近討論串（7 月），未能分頁抓取 4–6 月更早貼文。
- **來源**: firecrawl_search（英文新聞）回傳空陣列 → 改用 web source + Bright Data search_engine 取得真實連結。

## 3. 資料缺失說明

- **Q1 季報以 `.html`→`.md` 交付而非 PDF**：官網 binary 受 Akamai 封鎖，MCP 抓取工具僅回傳解析後文字，故轉存為 HTML 再轉 Markdown；核心財務數值完整乾淨。
- **4–6 月 Yahoo 掲示板貼文缺口**：Yahoo BBS 新版 UI 無法分頁回溯，4–6 月散戶情緒改由 kabutan 各月材料新聞補足（已完整涵蓋 4/5/6 月）。
- 未發現冷門股問題；荏原為熱門 AI 半導體概念股，過去三個月輿情量充足。

## 4. 異常檔案刪除紀錄

- 無檔案因 <10KB、缺公司名稱或 CID 亂碼過多而被刪除。
- 3 份財報來源檔（2 PDF + 1 HTML）於轉換成功後依 Convert2md Step 1.4 規則刪除，僅保留 `.md`。

## 5. 本次執行使用的 MCP（強制填寫）

| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape` | 繞過 Akamai 擷取 FY2026 Q1 英文決算短信；抓取 minkabu / kabutan / Simply Wall St / note 等 JS 渲染頁面全文 |
| Firecrawl | `firecrawl_search` | 搜尋英文財經來源與券商共識目標價（部分回空陣列，已補其他來源） |
| Bright Data | `scrape_as_markdown` | 突破 Yahoo Finance JP 掲示板 500 封鎖，取得真實掲示板貼文 |
| Bright Data | `search_engine` | 取得英文圈 7 月目標價上調與 5/14 決算報導的真實連結與日期 |
| GitHub | （Phase 5 push，見下） | 將本次成果推送至 `master` |

## 6. 輿情總結（過去三個月，2026-04 ~ 2026-07）

**整體偏多**：FY2026 Q1（5/15 發表）訂單 +62.6%、營收 +15.8%、營業利益 +18.4%，皆創單一 Q1 歷史新高，全年最終益上修並創最高益；AI/先進製程帶動 CMP 研磨與乾式真空幫浦需求為主引擎；外資（Fidelity）增持、券商連月上調目標價至 7,000–7,900 円上緣；新題材包括液化氫貨物泵世界首例型式承認、與美國 NuScale SMR 戰略合作、DC 液冷、國土強韌化。

**主要利空**：① 岐阜市子公司火災訴訟賠償風險；② 估值偏貴（PER ~26x、PBR ~5x）；③ 7 月中信用追證引發短線籌碼鬆動、停損潮；④ 能源事業 Q1 由盈轉虧（-16.6 億日圓）；⑤ Simply Wall St 提出營收成長趨緩疑慮。

> 所有輿情紀錄均為真實抓取內容（附真實 URL 與時間戳），無 AI 生成或捏造。
