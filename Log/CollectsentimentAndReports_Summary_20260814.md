# 任務執行最終報告 - 2026/08/14

- **執行 Skill**：CollectsentimentAndReports（每日輪替，Day 14）
- **當日對象（Rotation Table Day 14）**：`6121 新普`（Simplo Technology，台股）、`6781 AES-KY`（Advanced Energy Solution Holding，台股）
- **執行方式**：每公司一個獨立子代理人負責 Phase 2（財報）＋ Phase 3（輿情）；主代理人負責 Phase 1/4/5。

---

## 1. 成功紀錄

| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `6121新普` | MOPS/TWSE | `6121_Quarter_2026Q2.md` | 2026 Q2 季報，下載+轉換成功（中文，193KB，cid=0） |
| `6121新普` | 股市爆料同學會(CMoney API) | `202608_股市爆料同學會.md` | 150 篇區間內貼文，7 則實質討論 |
| `6121新普` | 經濟日報(UDN) | `202608_經濟日報.md` | Q2 財報全文＋AES-KY 相關 |
| `6121新普` | 財訊快報/Yahoo 等 | `202608_News.md` | 綜合新聞全文 |
| `6121新普` | MoneyDJ | `202608_MoneyDJ.md` | 2026-07-06 LEV/BBU 專文全文 |
| `6121新普` | 鉅亨網 | `202608_鉅亨網.md` | cnyes 條目（SERP 標註） |
| `6121新普` | Google News | `202608_GoogleNews.md` | 5 則真實新聞 URL |
| `6121新普` | PTT / Dcard | `202608_PTT.md` / `202608_Dcard.md` | 誠實記錄：三個月內無區間內內容 |
| `6121新普` | 財報狗 | `202608_財報狗.md` | 健檢＋公告 feed（社群需登入，未越牆） |
| `AES-KY` | MOPS/TWSE(doc.twse) | `6781_Quarter_2026Q1.md` | 2026 Q1 季報，下載+轉換成功（中文，151KB，cid=0） |
| `AES-KY` | MOPS/TWSE(doc.twse) | `6781_AnnualReport_2025.pdf` | 114 年度年報 PDF（下載成功，但轉 md 失敗，見第 4 節） |
| `AES-KY` | MOPS/TWSE(doc.twse) | `6781_AnnualReport_2024.pdf` | 113 年度年報 PDF（下載成功，但轉 md 失敗，見第 4 節） |
| `AES-KY` | 股市爆料同學會(CMoney API) | `202608_cmoney.md` | 120 篇貼文，濾出 7 月營收/BBU/發言人等實質貼文 |
| `AES-KY` | 經濟日報(UDN) | `202608_udn.md` | 7 月營收 17.23 億(YoY+28.24%)＋董座展望 |
| `AES-KY` | 鉅亨網 | `202608_anue.md` | 8/7 漲 8.26%、外資買超 |
| `AES-KY` | Google News | `202608_googlenews.md` | 投顧「買進」目標價 1,450／外資 1,680、越南擴產 |
| `AES-KY` | MoneyDJ | `202608_moneydj.md` | 6/30、7/6 兩篇專文（BBU 占比>70%、ASP 下修等利多利空） |
| `AES-KY` | PTT | `202608_ptt.md` | 8/6 Q2 自結 H1 EPS 23.45、毛利率 39.06% |
| `AES-KY` | 財報狗/readmo | `202608_statementdog.md` | 數據頁＋籌碼（外資投信賣超） |
| `AES-KY` | Dcard | `202608_dcard.md` | 誠實記錄：三個月內無符合內容 |

## 2. 失敗或被擋網站

- **Firecrawl（`firecrawl_scrape` / `firecrawl_search`）**：回 **402 Insufficient credits**（額度用盡）。兩個子代理人均遇到，依 §2.1 抓取鏈改用 **Bright Data** 遞補，成功抓取。
- **財報狗社群/亮點頁**：需登入牆，未越牆（誠實標註，只取可見的健檢與公告 feed）。
- **內建 `WebFetch` 抓財報狗 e-report**：回傳空白（JS 渲染），依 §2 換 MCP。

## 3. 資料缺失說明

- **AES-KY 2026 Q2 季報**：TWSE 尚未上架（`202602_6781_AI1` 不存在），最新季報為 2026 Q1，屬正常（申報期限與上架時間差）。
- **6121 新普 PTT / Dcard、AES-KY Dcard**：過去三個月內無符合條件的區間內貼文（命中者多為 2019–2025 舊文），已依 Skill §5 誠實記錄「已搜尋、無區間內新內容」，非略過未查。
- **6121 已存財報**：2024/2025 年報、2026 Q1 季報先前已存在，本次未重複下載，僅新增 2026 Q2。

## 4. 異常檔案刪除紀錄

| 檔案 | 原因 | 處置 |
| :--- | :--- | :--- |
| `AES-KY/6781_AnnualReport_2024.md` | markitdown 轉出 CID 亂碼 800 次（≥50 門檻），字型缺 ToUnicode CMap | 刪除 .md，**保留原始 PDF** 作權威來源 |
| `AES-KY/6781_AnnualReport_2025.md` | markitdown 轉出 CID 亂碼 806 次（≥50 門檻），字型缺 ToUnicode CMap | 刪除 .md，**保留原始 PDF** 作權威來源 |

> AES-KY 年報為 MOPS 中文版且無英文版；`markitdown`／`pypdf` 皆無法正確解出中文（映射到錯誤 Unicode 碼位），屬無法 regex 修復的字型問題。保留 PDF 以供日後以英文版或更佳工具重轉。成功轉換的兩份季報原始 PDF 已依 Convert2md Step 1.4 刪除（僅留 .md）。

## 5. 本次執行使用的 MCP

| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape`、`firecrawl_search` | 嘗試抓財報狗/cnyes/新聞；**額度用盡(402)**，依鏈遞補至 Bright Data |
| Bright Data | `scrape_as_markdown` | 主力抓取：財報狗報表清單、經濟日報、鉅亨網、Yahoo/財訊快報、MoneyDJ、PTT、readmo 等正文 |
| Bright Data | `search_engine` | Google/Bing 定位 6121/6781 相關新聞、PTT、Dcard、MoneyDJ 文章 URL |

> 另使用內建工具：`WebSearch`（公司身分確認、初步探索）、`WebFetch`（部分全文抓取）、`Bash`/`curl`（CMoney 官方 API 取貼文與留言）。未使用 Apify / Playwright（Bright Data 已滿足需求）。全程未從 GitHub `a9303001/FinancialReport` 取任何財報或輿情，未訪問 macrotrends.net。

## 6. 補充：公司身分確認

- **6781 AES-KY = Advanced Energy Solution Holding Co., Ltd.**（鋰電池模組廠，2021/03/22 台股上市，電子零組件業；主軸為 AI 伺服器備援電池模組 BBU），為新普(6121)集團旗下公司。論壇提及之「新盛力(4931)」「順達(3211)」為同族群同業，非 6781 本身。
