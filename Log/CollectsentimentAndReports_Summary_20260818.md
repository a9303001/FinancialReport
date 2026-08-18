# 任務執行最終報告 — CollectsentimentAndReports

- **執行日期**：2026-08-18（每日輪替表 Day 18）
- **目標公司**：`1333` Umios Corporation（前身 マルハニチロ / Maruha Nichiro，日股 TSE Prime，會計年度結束 3/31）
- **本地資料夾**：`1333Umios/`
- **執行分支**：`claude/cool-cannon-0ukzdq`（自動合併至 `master`）

> 說明：`1333` 於 FY2026 起將公司英文名由 Maruha Nichiro 改為 **Umios Corporation**（決算短信抬頭已顯示 Umios），代表人由池見賢（Masaru Ikemi）換為 **安田大介（Daisuke Yasuda）**。散戶輿情中「更名」為當月主要爭議點之一。

---

## 1. 成功紀錄

| 股號/名稱 | 資料來源 | 產生的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `1333Umios` | 官網 IR（umios.com/en）| `1333_Quarter_2027Q1.md` | ✅ 下載成功。FY 至 2027/3 之 **Q1**（季末 2026/6/30），英文決算短信（2026/08/04 公布），pdfminer 轉檔 0 個 `(cid:)` 亂碼 |
| `1333Umios` | Yahoo!ファイナンス掲示板 | `202608_yahoo_finance.md` | ✅ 更新成功。No.13100–13175（8/4–8/18）真實貼文 |
| `1333Umios` | 株探（kabutan）| `202608_kabutan.md` | ✅ 更新成功。個股新聞列表 + 8/4 決算速報全文 |
| `1333Umios` | みんかぶ（minkabu）| `202608_minkabu.md` | ✅ 更新成功。目標株価/個人予想/株価診断 彙總 |
| `1333Umios` | 日経会社情報（Nikkei）| `202608_nikkei.md` | ✅ 更新成功。8/4 決算、7/27 会社分割、漲價、黑鮪配額 |
| `1333Umios` | 時事/食品新聞/data-max | `202608_general_media.md` | ✅ 更新成功。價格調整報導 |
| `1333Umios` | note.com | `202608_note.md` | ⚠️ 部分。文章列表以 WebSearch 取得，日期未逐一驗證（誠實標註）|
| `1333Umios` | 5ch/2ch | `202608_5ch.md` | ✅ 真實擷取，但無專用個股 thread，內容稀少（誠實標註）|
| `1333Umios` | X(Twitter) | `202608_twitter.md` | ❌ 抓取失敗（§5.4 誠實記錄，非 AI 生成）|

### 財報覆蓋狀態
- 資料夾原已含：`report2024_en.md`、`report2025_en.md`（年報）、`20260511_FY2026_annual_results.md`（FY2026 全年）、`20260209_3Q_en_results.md`（FY2026 Q3）。
- 本次補齊唯一缺口 **Q1 FY2027**（季末 2026/6/30，2026/08/04 公布）。最新 2 份年報 + 最新 1 份季報要求已達成。

---

## 2. 失敗或被擋網站

- **來源**：X (Twitter)
  - **原因**：X 自 2023 年起限制未登入/第三方抓取；公開檢索頁需 JS 登入態。第三方 2ch/twitter 集計頁（kabu-sokuhou.com）僅回傳 **2023 年舊快取**，與 2026-08 窗口無關，不予採計。
  - **已依 §2 換過的工具**：內建 WebFetch → WebSearch → Bright Data（scrape_as_markdown）。整條可用鏈已試，均無法取得窗口內可驗證推文。
- **來源**：note.com 站內搜尋
  - **原因**：Bright Data 抓 note 站內搜尋遭 KYC 阻擋；改以 WebSearch 取得文章列表，但發布日期無法逐篇驗證，多屬更名期舊文，未確認窗口內 Q1 決算專文。
- **來源**：Firecrawl（MCP）
  - **原因**：本次額度用盡（"Insufficient credits"），Phase 3 起首選即失效，依 §2.1 順序改用 Bright Data，均成功。

---

## 3. 資料缺失說明

- **X / note 窗口內內容有限**：Umios 為日股中相對冷門之食品股，散戶即時討論主要集中在 **Yahoo!ファイナンス掲示板**（已充分涵蓋），X/5ch/note 端補充有限，屬正常現象而非抓取遺漏。
- 無其他財報缺口：Q1 FY2027 為當前最新季報，官網 IR 與 EDINET 均未有更新的期別。

---

## 4. 異常檔案刪除紀錄

- 無因 <10KB / 缺公司名稱 / `(cid:)` 亂碼而刪除之檔案。
- `1333_Quarter_2027Q1.pdf`（原始下載 234KB）於轉為乾淨 markdown（0 個 `(cid:)`）後移除原始 PDF，比照資料夾既有慣例（僅保留 `.md`）。

---

## 5. 本次執行使用的 MCP

| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| Bright Data | `scrape_as_markdown` | Phase 3 主力：kabutan 新聞列表與 8/4 決算全文、Yahoo 掲示板、minkabu、Nikkei、kabu-sokuhou 2ch/twitter 集計頁 |
| Firecrawl | `firecrawl_scrape` | Phase 3 首選嘗試（kabutan/Yahoo），**額度用盡**後依 §2 遞補至 Bright Data |
| GitHub | `create_pull_request` / 推送 | 將各階段成果推送分支（自動合併至 master）|

- 內建工具：`WebFetch`、`WebSearch`（Phase 2 官網 IR 抓取與 Nikkei/general-media/note 補充）、`Bash`（curl 下載、pdfminer 轉檔、git）。
- 註：Apify、Playwright 本次未觸發（Bright Data 已成功，無需再往下遞補）。

---

## 6. 當月重點摘要（Key Findings）

> 每股化基準：流通在外股數 **151,736 千股（≈1.517 億股）**（來源 minkabu）。

### 核心事件 — 2026/08/04 Q1 FY2027 決算（利空主導）
- **增收減益**：売上 2,775 億円（+5.3%，每股約 1,829 円）；営業利益 -29.4%；経常利益 64.2 億円（-31.3%，每股約 42 円）；純利益 34 億円（-47.3%，每股約 22 円）。
- **進捗率偏低**：通期進捗率 21.4%，低於 5 年平均 31.7%。
- **淨利大跌主因**：Nikkei 指出 -47% 淨利跌幅被**子公司出售（連動 7/27 会社分割揭露）一次性稅負**放大，本業惡化程度小於帳面淨利數字。

### 輿情利多 / 利空
- **利多**：配當 45 円 + 三年限定株主優待（散戶續抱誘因）；**消費税減税題材 → 常温保存食品/罐頭**受惠敘事；H2 調價與新品為獲利回升槓桿（沙丁魚罐 24 品 +15–30%、鯖魚 32 品、冷凍品約 60 品 9 月漲、新品 27 品 9/1 上市）。
- **利空**：**Umios 更名爭議**（成本、品牌辨識度流失）；相對 ニッスイ、極洋 表現落後；minkabu 綜合偏空 → **目標株価 984 円（約 -24%）、個人予想「売り」、株価診断「割高」**。

---

## 7. 結論

- Phase 1~5 全數完成。財報缺口（Q1 FY2027）已補齊並轉為乾淨 markdown；8 個來源之 8 月輿情已建檔（含 2 筆誠實失敗/受限記錄）。
- 全程未從 GitHub `a9303001/FinancialReport` 抓取任何財報或輿情（符合 Skill 禁令）；未訪問 macrotrends.net。
- 所有輿情內容均為實際抓取之真實貼文/新聞，無 AI 生成之模擬內容。
