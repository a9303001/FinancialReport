# CollectsentimentAndReports 任務執行最終報告 - 2026/07

- **執行日期**：2026-07-18
- **目標標的**：`9022 JR東海`（東海旅客鉄道 / Central Japan Railway，東證 Prime，JP）
- **會計年度**：3 月底結算（FY2026.3＝2025/4～2026/3）
- **資料夾**：`FinancialReport/9022JR東海/`（本次新建，原無此公司）

---

## 1. 成功紀錄

| 股號/名稱 | 類別 | 資料來源 | 產生的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- | :--- |
| `9022JR東海` | 年報(最新) | 官方 IR（決算短信 FY2026.3 全年） | `9022_AnnualReport_2026.md` | 下載+轉換成功（36.5KB，CID=0） |
| `9022JR東海` | 年報(次新) | 官方 IR（Integrated Report 2025 / FY2025.3） | `9022_AnnualReport_2025.md` | 下載+轉換成功（408KB，CID=0） |
| `9022JR東海` | 季報(最新) | 官方 IR（決算短信 FY2026.3 第3四半期／截至 2025/12） | `9022_Quarter_2026Q3.md` | 下載+轉換成功（14.4KB，CID=0） |
| `9022JR東海` | 輿情 | 株探 Kabutan | `202607_Kabutan.md` | 成功 |
| `9022JR東海` | 輿情 | みんかぶ Minkabu | `202607_Minkabu.md` | 成功 |
| `9022JR東海` | 輿情/分析 | BigGo ファイナンス（矢部教授リニア風險分析） | `202606_BigGo.md` | 成功 |
| `9022JR東海` | 輿情 | Yahoo!ファイナンス JP（AI値動き解説） | `202607_YahooFinanceJP.md` | 成功 |
| `9022JR東海` | 輿情 | moomoo 中文 | `202607_moomoo_CN.md` | 成功 |
| `9022JR東海` | 輿情 | Reddit(r/transit, r/japan) + Seeking Alpha | `202607_Reddit_SeekingAlpha_EN.md` | 部分成功（見下） |

### 財報來源與搜尋過程
- **命中即止**：日股搜尋順序第 1 站「官方 IR 頁面」即命中，未再往 EDINET / IR Bank / 富途遞補。
- 財報索引：`https://global.jr-central.co.jp/en/company/ir/brief-announcement/{年度}/`（英文版，避免中文版 CID 亂碼）。
- Integrated Report：`https://global.jr-central.co.jp/en/company/ir/annualreport/_pdf/annualreport2025.pdf`。
- **一律優先英文版**：全部 3 檔轉換後 `(cid:` 出現 0 次，內容乾淨。
- 三份 PDF 已依 repo 慣例（各公司資料夾僅存 `.md`）於成功轉換後刪除來源 PDF，僅保留 `.md`。

### 關鍵基本面（供交叉驗證，來源：FY2026.3 決算短信 + Minkabu）
- **FY2026.3 實績（過去最高益）**：営收 2兆62億円（+9.5%）、営業利益 8,301.67億円（+18.1%）、純利益 5,528.71億円（+20.6%）、綜合利益 620,515 百万円（+33.5%）、営業利益率約 41%。
- **FY2027.3 業績預想（減收減益）**：営收 1兆9,930億円（-0.7%）、営業利益 7,020億円（-15.4%）、純利益 4,470億円（-19.1%）。主因：万博增收效果消失＋労務費等成本上升。
- **股東還元**：自社株買（上限 200億円／650万株，5/1–7/31，8/31 消却）；配當年 32 円維持。
- **估值（2026/07/17）**：股價 3,766 円｜PER 8.0 倍｜PBR 0.71 倍｜殖利率 0.85%｜時価総額約 3.77 兆円。
- **下次決算**：2026/07/31（FY2027.3 Q1）。

### 三個月輿情主軸
- **最大題材（利多）**：2026/07/07 静岡縣知事鈴木表明リニア静岡工区「着工容認」，9 年僵局解除，股價由 3,453→3,766 円、出來高暴增；居民訴訟同期結案。
- **核心利空**：リニア總工費膨脹至 11 兆円、開業延至「2036 以降」；公司自估開業翌年度經常利益由 6,000 億級急減至 650 億級（折舊+利息年壓 5,000 億円超）。丹羽社長稱着工/開業時期「どちらも未定」。
- **其他**：東海道新幹線 23 年來首度導入個室、夜行新幹線試運行、鉄道股維權基金題材。

---

## 2. 失敗或被擋網站
- **note.com（`https://note.com/yama_shukatsu/n/nfdfbd1340980`）**：HTTP 404（頁面已刪除/移動），依 §2.5 直接跳過換來源，未重試。
- **Reddit 留言層級**：已用 brightdata `scrape_as_markdown` 抓取 r/transit 貼文頁，僅得貼文標題與分享連結，**留言區未載入（登入牆）**，無法取得逐則留言原文。已於 `202607_Reddit_SeekingAlpha_EN.md` 誠實記錄，未捏造留言。
- **Kabutan 深度內文**：材料ニュース列表可讀，個別內文為プレミアム付費牆，取列表標題/日期即可。

## 3. 資料缺失說明
- **FY2027.3（27年3月期）季報尚未發布**：FY2027 Q1（4–6月）決算預定 2026/07/31 發表，故「最新季報」採目前最新的 FY2026.3 Q3（截至 2025/12）。已確認官方 `brief-announcement/2027/` 為 HTTP 404，屬正常時序。
- **Integrated Report 2026 尚未發布**：官方 `annualreport2026.pdf` 為 HTTP 404（該報通常每年秋季發布），故 FY2026 年報採官方 FY2026.3 全年決算短信替代。
- **英文/中文散戶社群討論稀少**：JR東海為日本內需鐵路股（美股僅 OTC:CJPRY），海外原生多空論戰有限，討論集中於「リニア工程延宕與成本」交通議題。

## 4. 異常檔案刪除紀錄
- 無因 <10KB／無公司名／CID 亂碼過多而刪除之檔案。3 份財報轉換後 CID 均為 0、皆含 "Central Japan Railway"、皆 >10KB。
- 3 份來源 PDF（27.2MB/437KB/417KB）於轉換成功後依 repo 慣例刪除，非異常刪除。

## 5. 本次執行使用的 MCP（強制填寫）

| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_search` | 搜尋官方 IR 財報頁、日文/中文/英文新聞與輿情來源 |
| Firecrawl | `firecrawl_scrape` | 抓取 Kabutan、Minkabu、BigGo、Yahoo Finance JP、moomoo（JS 渲染頁） |
| Bright Data | `scrape_as_markdown` | 抓取 Reddit r/transit 貼文頁（§2.4 Reddit 內建工具被擋） |

### 內建工具
- `WebFetch`：抓取官方 IR 索引頁（brief-announcement、annualreport）。
- `Bash`（`curl`）：下載財報 PDF、解析真實 PDF href、檢查 FY2027/2026 頁存在性。
- `Bash`（`python3` + `pymupdf`）：PDF→Markdown 轉換與 CID 亂碼檢查（本環境無 Windows markitdown.exe，改用等效 pymupdf，Phase 4 意圖已達成：清潔 .md、無 XBRL/CID）。

---

## 6. 完成度
- Phase 1 初始化 ✅｜Phase 2 財報（2 年報+1 季報）✅｜Phase 3 輿情（6 來源）✅｜Phase 4 轉換（3 檔，CID=0）✅｜Phase 5 報告 + Push master ✅
