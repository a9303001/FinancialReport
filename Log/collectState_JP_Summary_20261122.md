# collectState 執行報告 — JP — 2026/11/22

- **資料窗口（＝保留期）**：2026-10-22 ~ 2026-11-22
- **資料夾**：`jp_state/`（執行後共 60 個 `.md` 檔，含 `StateAnalysis.md`、`AnalysisResult.md`、`0.Index.md`、`202611_JP_輿情新聞.md` 與 56 篇單篇；本次新增 6、刪除 2）

## 1. 收集成果
| 類別 | 新增檔案數 | 代表檔案 | 備註 |
| :--- | :--- | :--- | :--- |
| A 官方數據／政策 | 3 | `20261116_Data_内閣府_GDP1次速報2026年7-9月期.md`、`20261106_Data_厚労省_毎月勤労統計調査2026年9月速報.md`、`20261029_Policy_国交省_不動産価格指数公表延期.md` | 補齊 GDP、薪資與 MLIT 延期一手官方文件；經產省商業動態統計 9 月僅取得索引 |
| B 研究報告 | 2 | `20261023_Report_JREI_不動産取引市場調査2026上期.md`、`20261113_Report_PRBASE_東日本REINS10月首都圏市況分析.md` | JREI 投資家調査第 55 回尚未發布（最新第 54 回 2026-05-27） |
| C 新聞 | 1 | `20261116_News_住宅新報_東日本REINS10月中古マンション成約単価80万円割れ.md` | 與 PR BASE、YUKU NEWS 三家獨立媒體交叉核對東日本 REINS 10 月速報 |
| D REIT 市場 | 0 | — | 週末休市（11/21~22）無新收盤價與 TDnet 開示；另於 IR 核對 3462/3281/3269/8985/8951 一手數字（非本窗口發布故不入單篇檔） |
| E 輿情 | 0（併入月檔） | `202611_JP_輿情新聞.md` | 補收 5ch J-REIT 総合 #483~#490（11/21~22 週末貼文） |

**本期重點**：
1. **東日本 REINS 10 月首都圈中古公寓轉冷**（11/10 速報，住宅新報 11/16）：成約 3,392 件（YoY -19.7%，連 7 月減）、成約單價 79.44 萬円/㎡（YoY -6.9%，連 6 月跌破 80 萬円）、在庫 53,510 件（+22.5%）、東京都區部單價 -4.0%。
2. **實質薪資連 9 月正成長**（厚勞省 11/06）：9 月現金給與總額 311,409 円（+4.6%）、實質薪資 +2.2%，支撐住宅租金同時強化日銀升息底氣。
3. **7~9 月實質 GDP 小幅轉負**（內閣府 11/16）：季調年率 -0.1%（個人消費 -0.3%、民間住宅 -1.1%、設備投資 +1.6%）。
4. **實物投資交易維持高檔**（JREI 10/23）：2025 年 7.7 兆円創高、2026 上期 3.5 兆円（年化 7 兆円），辦公與住宅交易佔比升。
5. **5 檔大型 REIT 官方 IR 核對**：8985 每口 NAV 修正為 95,334 円（P/NAV 0.88 倍、時價 LTV 34.5%、政策利率 +0.5% 影響 DPU -159 円）；3462 除商譽 NAV 183,239 円（P/NAV 0.68 倍、稼働率 99.0%）；3269 NAV 189,810 円（P/NAV 0.72 倍）；3281 稼働率 99.0%（回購 ≈ 320 円/口）；8951 NAV 125,533 円、稼働率 98.2%。

## 2. 失敗或被擋網站
- **來源**：[東日本 REINS](https://www.reins.or.jp/)｜**原因**：SSL 憑證鏈異常（curl rc=60／Exa CRAWL_SSL_ERROR）｜**已試過**：改由住宅新報、PR BASE、YUKU NEWS 三家獨立媒體交叉核對 10 月速報一致。
- **來源**：[經濟產業省 商業動態統計](https://www.meti.go.jp/statistics/tyo/syoudou/result-2.html)｜**原因**：`result-2.html` curl 403、`h2slt11j.xlsx` 回傳 0 bytes｜**已試過**：以 Exa 與 WebSearch 取得 9 月小賣業販賣額摘要並標示僅索引。
- **來源**：[Yahoo!ファイナンス 掲示板](https://finance.yahoo.co.jp/)｜**原因**：舊 URL 路徑回 404｜**已試過**：週末休市確認無新開盤事件，改補 5ch 週末貼文。

## 3. 資料缺口說明
- **窗口內無新發布（⭕）**：
  - 東京 Kantei 70㎡ 中古公寓價格 2026 年 10 月版（最新一期 2026-10-22，11/22 複核尚未更新）
  - JREI 不動產投資家調査（Cap Rate）（最新一期第 54 回 2026-05-27）
  - 財務省 10 年 JGB 11/20 資料（`jgbcm.csv` 最新仍為 2026-11-19）
  - 國交省不動產價格指數 2026 年 1~7 月（10/29 官方公告因程式異常延期）
- **去重略過 URL**：`state_known_urls.txt` 共 52 筆既收 URL 全數跳過未重複下載。

## 4. Phase 1 清理紀錄
- 依窗口起日 `2026-10-22` 刪除 2 份窗口外檔案：
  - `20261021_REIT_8953_JMF住宅3物件譲渡.md`（2026-10-21）
  - `20261021_REIT_8953_JMF決算短信2026年8月期.md`（2026-10-21）

## 5. Phase 4 轉檔紀錄
- **Convert2md（`jp_state/` 限定範圍）**：掃描 3 份 PDF → 成功 3 份、CID 失敗 0、0 KB 0；原始 PDF 均已自動刪除，詳見 `Log/conversion_summary.md`。
- **state_tools.py convert**：HTML 轉 Markdown 成功 1 份（`20261029_Policy_国交省_不動産価格指数公表延期.md`）、失敗 0；無殘留非 `.md` 檔。

## 6. 本次使用的 MCP
- `pymupdf4llm-mcp`（`convert_pdf_to_markdown`）：PDF 轉 Markdown 3 份均成功。
- `exa`（`web_search_exa`、`web_fetch_exa`）：用於 REINS 三家媒體全文與 5 檔大型 REIT 官方 IR 核對，皆正常。
- 本次未呼叫 Firecrawl／Bright Data／Apify（無需重複抓取已收站點）。

## 7. Skill 維護
- 更新 `collectState/SKILL.md` §4.1（並同步 `.claude/skills/collectState/SKILL.md` 與 `.agents/skills/collectState/SKILL.md`）：
  - `住宅新報 jutaku-s.com` 由 `[未驗證]` 改為 `[2026-11]`（curl 與 Exa 可讀，可作為 REINS 月例速報替代核對來源）。
  - `JREI reinet.or.jp` 註明不動產取引市場調査 PDF（`/wp-content/uploads/{yyyy}/{MM}/Market-Survey_*.pdf`）curl 可下載 `[2026-11]`。
  - 補記 `mhlw.go.jp` 毎月勤労統計 PDF 與 `esri.cao.go.jp` GDP 速報 `gaiyou{yy}{q}1.pdf` curl 可下載 `[2026-11]`、`meti.go.jp/statistics/tyo/syoudou/result-2.html` curl 403 `[2026-11]`。
