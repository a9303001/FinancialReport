# 任務執行最終報告 - 2026/09/17

- **執行來源**：`Routines_CollectsentimentAndReports.md` 每日輪替表 → 當日「日」= 17 → **8117 中央自動車工業（日股・東証スタンダード）**
- **Skill**：`CollectsentimentAndReports`
- **公司資料夾**：`FinancialReport/8117中央自動車工業/`

---

## 1. 成功紀錄

| 股號/名稱 | 資料來源 | 產生的檔案／下載的財報檔名 | 狀態／備註 |
| :--- | :--- | :--- | :--- |
| `8117中央自動車工業` | — | `8117_AnnualReport_2026.md` | **已存在，跳過下載**（2026年3月期／第87期 有価証券報告書，提出日 2026-06-22，EDINET E02642）|
| `8117中央自動車工業` | — | `8117_AnnualReport_2025.md` | **已存在，跳過下載**（2025年3月期 有価証券報告書）|
| `8117中央自動車工業` | — | `8117_Quarter_2027Q1.md` | **已存在，跳過下載**（2027年3月期 第1四半期決算短信，含 2026-08-28 期中審閱完成版）|
| `8117中央自動車工業` | 株探／MINKABU PRESS／フィスコ | `202609_輿情新聞.md` | ✅ 新增（新聞 3 則，含內文逐字引述）|
| `8117中央自動車工業` | TDnet 適時開示原始 PDF | `202609_輿情新聞.md` | ✅ 新增（2026-09-07「売出価格等の決定」全文數據）|
| `8117中央自動車工業` | Yahoo!ファイナンス 掲示板 | `202609_輿情新聞.md` | ✅ 新增（抓到 No.3423~3515，2026/7/3~9/17；整理 4 個主題）|
| `8117中央自動車工業` | X (Twitter) | `202609_輿情新聞.md` | ✅ 新增（@apegogo3 2026-09-03 貼文全文，TOPIX 被動買盤試算）|
| `8117中央自動車工業` | note.com | `202609_輿情新聞.md` | ✅ 新增（1 篇全文 + 2 篇索引摘要）|
| `8117中央自動車工業` | 96ut.com PO 分析 | `202609_輿情新聞.md` | ✅ 新增（8/21~9/17 逐日股價／成交量／逆日歩實績表）|

### Phase 2（財報）結論：**無需下載，現有檔案已是最新**
- 以 **決算プロ（TDnet 適時開示一覧）** 與 **IRBANK** 核對，8117 過去一年 TDnet 開示最新一筆為 **2026-09-07「売出価格等の決定に関するお知らせ」**（非定期報告）。
- 最新定期報告為 **2027年3月期 第1四半期決算短信（2026-08-05 發布、2026-08-28 期中審閱完成版）**，資料夾內 `8117_Quarter_2027Q1.md` 即為此份。
- **2027年3月期 第2四半期（中間期）決算短信尚未發布**（該公司 3 月決算，上期結算日為 2026-09-30，依前期慣例約於 11 月中旬公布；前期對應檔為 2025-11-13 發布）。
- 最新 2 份年報（2026年3月期／2025年3月期 有価証券報告書）皆已在庫。→ **Phase 2 達成「最新 2 年報 + 1 季報」要求。**

---

## 2. 失敗或被擋網站

- **來源**: [moomoo 社區 8117](https://www.moomoo.com/ja/stock/8117-JP/community)
  - **原因**: JS 動態渲染（§2.3 已知）；且本環境 §2.1 四個 MCP 全部不可用或失敗。
  - **已依 §2 換過的 MCP**：
    - `firecrawl_scrape` → ❌ `Insufficient credits`（本環境 Firecrawl 額度用盡，**全程不可用**）
    - Bright Data `scrape_as_markdown` → ❌ 回傳空殼（僅 `Document`）
    - Apify `apify/web-fetch` → ❌ `Monthly usage hard limit exceeded`（本環境 Apify 額度用盡）
    - Playwright `browser_navigate` → ❌ `Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome`（本環境瀏覽器未安裝）
  - **影響評估**：低。moomoo 頁面可見之行情摘要（高値 2,144／安値 2,134／出來高 243.17 萬股）已由 96ut.com 同日資料完整涵蓋。
- **來源**: [note.com 站內搜尋](https://note.com/search?q=中央自動車工業)
  - **原因**: 官方 API `/api/v3/searches` 回 **HTTP 403**；搜尋頁為 JS 渲染，Bright Data 僅取得外框。
  - **替代做法（成功）**：改用 Bright Data `search_engine`（Google）定位文章 URL → 再用 `scrape_as_markdown` 抓內文，成功取得 1 篇全文。
- **來源**: `finance.yahoo.co.jp`（內建 `curl`）
  - **原因**: agent proxy 連線中斷（`ws_closed_mid_exchange`），HTTP 000。
  - **替代做法（成功）**：Bright Data `scrape_as_markdown` 一次取得完整掲示板（80KB／1,559 行）。

---

## 3. 資料缺失說明

1. **2027年3月期 第2四半期決算短信**：尚未發布（結算日 2026-09-30 未到），非抓取失敗。
2. **5ch**：兩次搜尋（含 `site:` 限定）均查無 8117 於過去三個月的相關討論。唯一命中為 2022 年市場重組前的舊帖（仍稱「東証2部」），與本次事件無關。推測原因為 8117 屬中小型股（時價總額約 1,315 億円），日本散戶討論高度集中於 Yahoo!ファイナンス 掲示板。已依 §5 第 7 點在 `202609_輿情新聞.md` 據實記錄「已查過」。
3. **Monex「被動買盤 66.7 日分」試算原始報告**：僅取得 X 貼文中的轉述，未取得原始出處，已於檔案中標註為「市場預期而非事實」。
4. **みんかぶ**：本月 2026-09-12 已收集並經 `ArrangePublicOpinionMd` 併入 `2026_PublicOpinion.md`，本次僅以 IRBANK 同日數據做交叉查核，未重複抓取（遵守 §2.6 請求頻率控制）。

---

## 4. 異常檔案刪除紀錄

- **無刪除**。本次 Phase 2 未下載任何新財報檔（既有檔案已涵蓋最新 2 年報 + 1 季報），故無 <10KB、無公司名稱或 `(cid:` 亂碼之異常檔需處理。
- 暫存檔（`po_price_real.pdf` 等）僅存放於 session scratchpad，未寫入 repo。

---

## 5. 本次執行使用的 MCP

| MCP 服務名稱 | 用到的工具／函式 | 用途說明 |
| :--- | :--- | :--- |
| Bright Data | `scrape_as_markdown` | 抓取 Yahoo!ファイナンス 8117 掲示板全文、X 貼文全文、note.com 文章全文（內建工具失敗後的遞補，**本次最關鍵的抓取工具**）|
| Bright Data | `search_engine`（Google／Bing） | 定位 note.com／X 文章 URL、查證 5ch 是否有相關討論 |
| PyMuPDF4LLM | `convert_pdf_to_markdown` | 將 TDnet「売出価格等の決定に関するお知らせ」PDF 轉為 Markdown 以取得精確數據（2,134 円／折價 3.00% 等）|
| Firecrawl | `firecrawl_scrape` | ❌ 嘗試抓取 kabutan／moomoo，回 `Insufficient credits`，**本環境全程不可用** |
| Apify | `apify/web-fetch` | ❌ 嘗試抓取 moomoo，回 `Monthly usage hard limit exceeded`，**本環境額度已用盡** |
| Playwright | `browser_navigate` | ❌ 嘗試抓取 moomoo，回 Chromium 未安裝，**本環境不可用** |

**同時使用的內建工具**：`Bash`（`curl` 抓取 kabutan 新聞列表與內文、決算プロ TDnet 一覽、IRBANK、96ut.com PO 分析；皆成功且未耗用 MCP 額度）、`WebSearch`（查核 Q2 是否已發布）。

> 📌 **環境註記（供下次執行參考，建議併入 §2.3/§2.4 經驗表）**
> - 本環境 **Firecrawl 與 Apify 額度皆已用盡**、**Playwright 無 Chromium**，§2.1 MCP 鏈實質上僅剩 **Bright Data** 可用 → 遇 JS 渲染站請直接用 Bright Data，不必逐一試其他三個。
> - `kabutan.jp`（列表頁與新聞內文）、`ke.kabupro.jp`、`irbank.net`、`96ut.com` 皆為 **SSR 靜態頁**，一般瀏覽器 UA 的 `curl` 即可完整取得，**不需動用任何 MCP**。
> - `tdnet-pdf.kabutan.jp/{yyyyMMdd}/{文件ID}.pdf` 可直接取得 TDnet 適時開示原始 PDF（需先從 `kabutan.jp/disclosures/pdf/...` 頁面的 `<object data=...>` 取出真實網址）。
> - `finance.yahoo.co.jp` 在本環境對 `curl` 會出現 proxy `ws_closed_mid_exchange`，直接改用 Bright Data 即可。

---

## 6. 本月重點發現（摘要）

| 項目 | 內容 |
| :--- | :--- |
| **最大事件** | 2026-08-28 公告大股東釋股（354.86 萬股 + OA 上限 53.22 萬股，約當扣除庫藏股後發行股數 7.4%），賣出人為あいおいニッセイ同和損保、東京海上日動火災、大同生命保険（政策持股解消）|
| **定價結果** | 2026-09-07 決定 **1 股 2,134 円**（基準價 2,200 円，折價 3.00%），總額 **75.73 億円**（每股約 137.0 円規模換手）；受渡日 9/14 |
| **對沖措施** | 庫藏股買回上限 100 萬股（1.80%）／25 億円（每股約 45.2 円），期間 2026-10-13 ~ 2027-03-31 |
| **股價實績** | PO 公告日收 2,286 → 9/14 最低 **2,047（-10.5%）**，明確「公募割れ」；9/15~9/17 連三日反彈至 **2,190（+1.53%）**，重回賣出價之上 |
| **基本面** | FY2027 Q1 經常利益 34.2 億円（YoY +21.8%，每股約 61.9 円），上半年進度 51.9% > 5 年平均 46.3%；營益率 25.0% → 25.5% |
| **關鍵不確定性** | 新 TOPIX 是否納入（JPX 未公告）；Green Shoe 行使期間至 2026-10-09 仍有追加供給 |
| **估值（2026-09-17, IRBANK）** | PER 12.74 倍（預估）、PBR 1.91 倍、殖利率 2.88%（預估）、ROE 14.99%（預估）、時價總額 1,315 億円 |

---

## 7. Push 說明（與 Skill §7 強制規則的差異）

- Skill §7 要求「強制 push 到 `master`」，惟本 session 之執行環境規範明確指定：**所有開發與推送一律至指定分支 `claude/nice-allen-tctylq`，未經明確許可不得推送至其他分支**。
- 因此本次改以：**推送至 `claude/nice-allen-tctylq` 並開立 Draft PR（base: `master`）**，由 PR 合併途徑進入 master，以同時滿足兩項要求。
