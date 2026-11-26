# edgar 經驗庫（每次執行前先讀；執行後依 SKILL.md §9 更新）

> 一條一事實：`- [yyyy-mm] **key**：內容（證據）`。用 `edgar.py lesson --section {sec|company|naming|convert} --key … --text …` 寫入：同 key 會改寫舊條目，並自動同步 `.claude` / `.agents` 兩份。
> 過時或被腳本處理掉、不再需要人注意的條目直接刪除。

## A. SEC／EDGAR 行為

- [2026-11] **User-Agent**：SEC 接受通用 UA（`FinancialReport-edgar-skill/… (research; contact admin@example.com)`），雲端與本機直連 www.sec.gov、data.sec.gov 都 200；被擋時回 403 或內容含「Undeclared Automated Tool／Request Rate Threshold Exceeded」的 HTML 頁。
- [2026-11] **submissions 分頁**：`filings.recent` 只放最近 1000 筆或 1 年；UHS 1000 筆可回溯到 2010，但發大量 424B2 的銀行可能不到 1 年 → 腳本自動補抓 `filings.files`。
- [2026-11] **filing index**：`{accession}/index.json` 只有檔名沒有附件類型；要類型（EX-99.1、EX-13）讀 `{accession}-index.htm` 的表格。accession 打錯時 SEC 回 HTTP 200 + 「Directory listing is Not Available」頁，不是 404。
- [2026-11] **6-K 與 XBRL**：外國發行人的 6-K 財報多半 `isXBRL=0`（TLK），不能靠 XBRL 旗標找季報；整份提交大小（submissions 的 `size`）≥ 數 MB 是可靠的第一道篩選。
- [2026-11] **Range**：Archives 文件支援 `Range: bytes=0-N`，6-K 判斷只讀前 1.5MB。

## B. 公司特例

- [2026-11] **TLK 6-K**：季報財報在 6-K 主文件本身（`tmb-YYYYMMDDx6k.htm`，7–8MB），沒有 EX-99；2026-11-25 的 6-K 是 2026-06-30 半年報重送，最新一期是 2026-10-30 提交的 9 月季報 → 一定要依期末日挑，不能取最新提交。
- [2026-11] **TM（Toyota ADR）**：20-F 每年 6 月提交（FYE 3/31）；6-K 主文件只是封面，財報在附件：Q1＝EX-99.1「FY2027 FIRST QUARTER FINANCIAL SUMMARY」、半年＝EX-99.2「FY2027 SEMI-ANNUAL FINANCIAL SUMMARY」（2026-11-05，accession 0001193125-26-448368）→ 檔名 TM_Quarter_2027H1，與 edinet 的 7203_Quarter_2027H1 同一期。日文詳細版由 edinet 抓到 7203Toyota/；要 SEC 英文版才用 --out 7203Toyota --ticker TM。
- [2026-11] **UHS 股數**：多類股（Class A/B/C/D），companyfacts 沒有 dei:EntityCommonStockSharesOutstanding → 流通股數看 10-Q/10-K 封面。
- [2026-11] **HEGIY（恒安國際 ADR）**：unsponsored OTC ADR，不在 SEC 代碼表 → 走港股 HKEX。

## C. 命名與會計年度

- [2026-11] **1 月底結帳**：Target（FYE 0201）期末 2026-01-31 的 10-K，DEI 標 FY2025；同類零售業（Walmart 則自稱 FY2026）各自不同 → 一律以 DEI 為準，腳本已自動採用並在報告列出。
- [2026-11] **repo 舊檔名**：UHS 用 `UHS_10K_{期末日}`／`UHS_10Q_{期末日}`；EVTC 同時有 `EVTC_Quarter_…` 與 SEC 原名 `evtc-YYYYMMDD`（同一份重複）；CF 舊轉檔把封面日期拆成「December 31\n, 2025」→ 都已由檔名 alias + 檔頭判定認得。
- [2026-11] **6-K 期末日挑法**：日本企業英譯決算短信把比較期（2025-09-30）與本期（2026-09-30）並列、次數一樣多，還有財測日（2027-03-31）→ 不可取「最常出現」的日期；腳本改為：次數 ≥ max(2, 最高×25%) 的日期中取最新且不晚於提交日者（TM 2026-08 實測曾誤判成 2025-06-30，已修並加 selftest）。

## D. HTML 轉檔與驗證

- [2026-11] **html2md 實測**：UHS 10-Q iXBRL 5.8MB → 342KB、0.7 秒；TLK 6-K 7.5MB → 366KB。`$`、`)`、`%` 獨立儲存格要合併，否則每列多 2–3 個空欄。舊轉檔工具會在 md 開頭留下 `xml version=…` 雜訊，html2md 不會。
- [2026-11] **表頭跨欄對齊**：SEC 表頭「2026」常 colspan 跨在「$ 欄＋數字欄」上；把 $ 併到數字後表頭會錯位一欄 → html2md 改為把跨欄表頭移到跨距內第一個有資料的欄（UHS 10-Q 損益表實測對齊，檔案 342KB→333KB）。
