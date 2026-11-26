---
name: collectState
description: 國家層級 REIT 情報收集 — 指令如 `jp /collectState`、`hk /collectState`（或 `/collectState jp`）。只收最近 1 個月：先刪 {cc}_state/ 內發布日超過 1 個月的資料，再收集該國最近 1 個月發布的總經／房地產／REIT 官方數據、研究報告、新聞、REIT 公告與多平台輿情（hk 加中國房地產），已收過的不重抓；全部轉 Markdown、重建 0.Index.md 並 push。只負責收集，不做分析（分析交給 stateAnalysis，產出 AnalysisResult.md）。
argument-hint: "<國家代碼：jp | hk | tw | us | sg …>"
---
/goal
# collectState — 國家層級 REIT 情報收集（只收最近 1 個月）

**任務**：替指定國家 ① 刪掉窗口外舊資料 ② 只收最近 1 個月發布的原始資料（官方數據、研究報告、新聞、REIT 公告、輿情）③ 全部轉 Markdown ④ 寫執行報告並 push。
**分工**：本 Skill 只「收」，不寫任何分析或結論；判斷由 `stateAnalysis` 讀這些檔後寫 `{cc}_state/AnalysisResult.md`。
**抓取技術**沿用 `collectStk`（§3 抓取規則、§4 站點知識庫、§5 API/SOP、§8.3 過濾、§8.5 失敗寫法；§4／§5 依市場放在 `collectStk/references/sites_*.md`）；本檔只寫國家層級差異。
**參數**：`$ARGUMENTS`（空白或不像國家代碼 → 從使用者訊息解析；仍沒有 → 詢問，不可猜）。

## 0. 底線（違反任一＝任務失敗）

1. **窗口**：只收「原文發布日」落在 `WINDOW_START ～ TODAY` 的內容（`WINDOW_START`＝TODAY − 1 個月，由 `window` 子命令算）。發布日查不到＝窗口外，不收。
2. **防幻覺**：只記錄真實抓到的內容，附真實 URL 與發布日；抓不到就誠實寫失敗原因，不用訓練記憶補。
3. **先清後收、不重抓**：先跑 `window` → `purge`；`state_known_urls.txt` 裡的 URL 不再下載。
4. **全轉 Markdown**：結束時 `{cc}_state/` 只剩 `.md`；轉不了的原檔保留並寫進報告。
5. **即時存檔**：每抓完一份就寫檔並記 manifest。
6. **檔案隔離**：只能寫 `{cc}_state/`（`AnalysisResult.md` 除外，只讀）、`Log/collectState_*`、`Log/conversion_summary.md`、本 Skill。其他目錄一律只讀。

## 1. 參數與路徑

- `cc`：2～3 個小寫字母（`jp`、`hk`、`tw`…；別名 japan→jp、hong kong→hk、taiwan→tw）。`hk`（或「hk and china」）加跑 §5 中國房地產。資料夾用小寫 `{cc}`，檔名與標題用大寫 `{CC}`。
- `<REPO>`：repo 根目錄｜`<SCRATCH>`：暫存目錄（不可在 repo 內）｜`<FOLDER>`＝`<REPO>/{cc}_state`（不存在就建立）
- `<TOOLS>`＝`<REPO>/.claude/skills/collectState/scripts/state_tools.py`（Gemini 用 `.agents/` 同名檔）
- 窗口長度只在 `state_tools.py` 的 `WINDOW_MONTHS = 1` 設定。

### `{cc}_state/` 內容
- **單篇資料**：`{yyyyMMdd}_{類型}_{來源}_{短標題}.md`，`yyyyMMdd`＝原文發布日。類型：`Data`（官方統計）、`Policy`（政策／央行）、`Report`（研究報告）、`News`、`REIT`（個別 REIT 公告）、`Sentiment`（長文輿情）。短標題 ≤ 30 字，不含空白與 `\/:*?"<>|`，不建子資料夾。
- **月度彙整**：`{yyyyMM}_{CC}_輿情新聞.md`（§3.3）。
- **`0.Index.md`**：`finalize` 自動產生，勿手改。
- **`AnalysisResult.md`**：`stateAnalysis` 的輸出，受保護，本 Skill 不讀寫。
- 同一內容只下載一種格式（PDF ＞ HTML ＞ 其他）；MCP 直接回 Markdown 正文可直接存 `.md`。

### manifest
每存一檔追加一筆到 `<SCRATCH>/state_manifest.jsonl`（子代理人各寫 `state_manifest_{A|B|C}.jsonl`）：
`{"file": "20261115_Report_CBRE_JapanOfficeQ3.pdf", "url": "https://...", "title": "...", "publisher": "CBRE Japan", "published": "2026-11-15", "type": "Report", "note": "付費牆僅摘要"}`
`file`＝存檔時原始檔名；`published` 必填且等於檔名日期前綴。

## 2. 流程

1. **準備**：解析 `cc`、建 `<FOLDER>`、`git fetch origin master && git merge --no-edit FETCH_HEAD`（失敗記錄後繼續）。
2. **窗口與清理**（一定在收集前）：
   - `python <TOOLS> window --folder <FOLDER> --scratch <SCRATCH>` → 印窗口、月檔名，輸出 `<SCRATCH>/state_known_urls.txt`
   - `python <TOOLS> purge --folder <FOLDER>`（dry-run）→ 確認後加 `--apply`。依檔名日期前綴判斷（不看 mtime）；`0.Index.md`、`AnalysisResult.md` 受保護；舊版遺留的 `StateAnalysis.md` 會被刪除。
3. **盤點**（決定這次補什麼）：已收 URL 清單；`AnalysisResult.md` 第十四章「資料缺口、待辦與行事曆」（優先補）；當月（或上月）月檔中每個來源最後收到的日期；標的池見 §4。
4. **收集**（§3、§4、§5）：可分 2～3 個子代理人平行（A 官方＋報告、B 新聞＋REIT、C 輿情），各寫自己的單篇檔、manifest 與 `<SCRATCH>/digest_{A|B|C}.md`；月檔只由主代理人寫。
5. **轉 Markdown**：
   - PDF → 呼叫 `Convert2md` Skill，掃描**必須帶第 3 個參數 `<FOLDER>`**：`python <SCRATCH>/scan_pending.py <REPO> <SCRATCH> <FOLDER>`（不帶會轉掉 repo 其他 PDF）。CID 亂碼 → 換英文版／HTML 版或換來源，都沒有就保留 PDF。
   - 其他格式 → `python <TOOLS> convert --folder <FOLDER> --scratch <SCRATCH>`（markitdown → pandoc → BeautifulSoup；封鎖頁／過短／CID 判失敗並保留原檔；圖片要把數字寫進 `.md` 後手動刪）。缺套件：`pip install "markitdown[all]" beautifulsoup4 markdownify`。
   - `python <TOOLS> finalize --folder <FOLDER> --manifest "<SCRATCH>/state_manifest*.json*"` → 補來源標頭、重建 `0.Index.md`。⚠️ 要處理完：沒 manifest 紀錄 → 補記重跑；發布日在窗口外 → 刪檔；前綴 ≠ 發布日 → 改檔名。
6. **自檢**：`python <TOOLS> check --folder <FOLDER>` 必須通過（只剩 .md、日期在窗口內、有來源標頭、非空檔、無封鎖頁／CID、當月月檔存在）。
7. **報告與 push**（§6）。

## 3. 收集規則

### 3.1 先驗日期再下載
- 依 §4／§5「慣例發布」只抓本窗口應有新一期的指標；季報／年度指標本期沒出 → 月檔記 `⭕ 窗口內無新發布（最新一期 YYYY-MM-DD）`，不下載舊期。
- 下載前用列表日期、URL 內日期、`curl -sI` 的 `Last-Modified` 或搜尋結果 `publishedDate` 確認在窗口內。
- 搜尋加時間限制：Firecrawl `tbs: "qdr:m"`；WebSearch／Exa 查詢字加「{YYYY}年{M}月」並以發布日過濾；論壇只取窗口內貼文。
- 去重：已收 URL 跳過；同事件多家轉載只存最完整一篇，其餘只在月檔列連結。
- MCP 回「requires approval」＝視同未連線，改用 Exa `web_search_exa`／`web_fetch_exa` 補位並標「索引」。

### 3.2 每類目標（達不到寫原因，不灌水）
- **A 官方數據／政策**：§4 清單逐項確認，有新一期就存單篇（`Data`／`Policy`）。
- **B 研究報告**：≥ 3 份公開報告（PDF 優先），存單篇（`Report`）。
- **C 新聞**：≥ 10 則房地產／利率／REIT 相關，摘要進月檔，重要 3～5 則存全文（`News`）。
- **D REIT 市場**：REIT 指數、平均殖利率；標的池每一檔查窗口內公告（決算、增資、收購、配息、評級），公告存單篇（`REIT`）。
- **E 輿情**：§4 平台每個都試，成功 ≥ 5 個，進月檔。每則標 🟢 利多／🔴 利空／⚪ 中性；與官方數據矛盾標「⚠️ 與 {來源} 不符」；內容農場／AI 稿標明或排除；轉載數字互相矛盾標 `⚠️ 未經證實`。
- **F 中國房地產**（僅 hk）：§5 逐項。

### 3.3 月度彙整檔 `{yyyyMM}_{CC}_輿情新聞.md`
- 標題 `# [{CC} 國家層級] REIT／房地產輿情與新聞整理 ({YYYY}/{MM})`，下一行 `> 資料窗口：WINDOW_START ～ TODAY`。
- 章節固定：`## 一、官方數據與政策` → `## 二、研究報告摘要` → `## 三、新聞` → `## 四、REIT 市場與個別 REIT` → `## 五、中國房地產`（僅 hk）→ `## 六、輿情（依平台）`。
- 每個來源一個 `### [來源名稱]`：抓取時間、方式、結果（✅／⚠️ 僅索引／❌／⭕）。每則：連結、發布日、核心內容摘錄、🟢🔴⚪。只記錄事實與原文觀點，不寫自己的投資結論。
- Append 模式：已存在的章節只補在末尾。REIT 相關金額附每單位金額（÷ 最新已發行單位數，註明日期）。

## 4. 各國來源清單

> 標 `[未驗證]` 的站點首次使用後依結果改成 `[yyyy-mm]`。`collectStk` §4 已有的站點（日經、株探、Yahoo JP、5ch、note、JAPAN-REIT.COM、HKEXnews、AAStocks、新浪、雪球、股吧、LIHKG、moomoo…）照該處做法。括號內為慣例發布時點。

### 4.1 日本（jp）

**A 官方／政策**
- 日銀 `boj.or.jp`：金融政策會合（年 8 次）、短觀（4/7/10/12 月）
- 10 年 JGB：財務省 `mof.go.jp/jgbs/reference/interest_rate/jgbcm.csv`（當月）、`…/data/jgbcm_all.csv`（歷史），cp932（每營業日）[2026-11]
- CPI（含民営家賃）：`stat.go.jp/data/cpi/sokuhou/tsuki/pdf/zenkoku.pdf` 固定網址每月覆寫（20 日前後）[2026-11]
- 國交省 `mlit.go.jp`：不動產價格指數（月底）、地價公示／基準地價（3/9 月）、建築著工 `mlit.go.jp/report/press/content/kencha{令和年}{月2碼}.pdf`（月底）[2026-11]
- 不動產經濟研究所新築公寓：列表 `fudousankeizai.co.jp/mansion`，PDF 在 `/share/mansion/{id}/…pdf`（中旬）[2026-11]
- 東日本 REINS 月例速報：`reins.or.jp` curl/Exa/Firecrawl 皆失敗（憑證鏈不完整，不可關 TLS 驗證）→ 用 `jutaku-s.com`＋`prbase-realestate.com` 交叉核對（10 日前後）[2026-11]
- 毎月勤労統計 `mhlw.go.jp/toukei/itiran/roudou/monthly/…/houdou*.pdf`（上旬）、內閣府 GDP `esri.cao.go.jp/…/gaiyou*.pdf`（季後中旬）；經產省商業動態 curl 403 → 改 e-Stat/Exa [2026-11]
- 東京 Kantei：`kantei.ne.jp/report/`，租金 `report/rent/{id}/`（月中）、70㎡ 價格 `report/70m2/{id}/`（下旬）[2026-11]
- 三鬼商事都心 5 區辦公室 ⭐：`e-miki.com/rent/assets/prt/21_{yyyyMM}.pdf`（號數月＝內容前月；月初）[2026-11]
- JNTO 訪日外客：curl 403，Exa `web_fetch_exa` 讀 `jnto.go.jp/news/press/{yyyyMMdd}_monthly.html`（中旬）[2026-11]
- 稅制大綱（12 月）、金融廳法規（不定期）

**B 研究報告**：可 curl [2026-11]：ARES 月報 `ares.or.jp/action/monthly/pdf/ares_monthly_report_{yyyyMM}.pdf`、ニッセイアセット J-REIT 月報 `nam.co.jp/news/mpdf/{yyMMdd}_tjj.pdf`、JPX 東證 REIT 指數 factsheet `jpx.co.jp/markets/indices/factsheets/files/102_fac2_REIT.pdf`（看 `Last-Modified`）、Cushman & Wakefield 東京 MarketBeat、第一生命經研 `dlri.co.jp`、信金中金 `scbri.jp`、JREI `reinet.or.jp`。大和AM 英文月報只能 Exa 索引。[未驗證]：Nissay 基礎研 `nli-research.co.jp`、三井住友信託基礎研 `smtri.jp`、大和總研、CBRE、JLL、Savills、Colliers。券商報告只收公開摘要。

**C 新聞**：日經、Reuters／Bloomberg、東洋経済、住宅新報 `jutaku-s.com`、株探 J-REIT 市況、Yahoo JP ニュース。

**D REIT 市場**：東證 REIT 指數與平均殖利率、增資／新上市／合併／TOB（TDnet 經株探、JAPAN-REIT.COM）。標的池＝`references/jp.md`（stateAnalysis）本機追蹤組＋板塊代表組＋`JpReitScreenerResult/` 前 10。
- 指數日次：日經頁為 JS → Exa 搜「東証REIT指数 {日期} 終値」取 `stock-marketdata.com/reit.html` 並交叉核對 [2026-11]。
- 個別：株探 `kabutan.jp/stock/?code={代碼}`；開示列表 `stock/news?code={代碼}&nmode=3`，真實發布日看連結路徑 `/disclosures/pdf/{yyyymmdd}/` [2026-11]。

**E 輿情**：5ch（`mao.5ch.io/test/read.cgi/stockb/` 的「J-REIT総合」串，cp932，以討論串 ID＝Unix 秒過濾窗口）、X、Yahoo JP 掲示板、note、みんかぶ、Reddit（r/JapanFinance，經 Apify）、PTT／Dcard／Mobile01。PTT 日本 REIT 文停在 2024；X 經 Exa site 限制無結果 [2026-11]。

### 4.2 香港（hk）— 另跑 §5

**A 官方／政策**
- HKMA：每日隔夜／1M HIBOR、基本利率 `api.hkma.gov.hk/…/daily-monetary-statistics/daily-figures-interbank-liquidity`；3M 在 `monthly-statistical-bulletin/er-ir/hk-interbank-ir-daily`（有延遲）；貨幣與按揭統計（每月）[2026-11]
- 差估署 RVD Excel：`rvd.gov.hk/doc/en/statistics/his_data_{n}.xls`（3 住宅租金、4 住宅售價、8 寫字樓租金、9 寫字樓售價、12 零售；「所有類別」第 29 欄；`Last-Modified`＝發布日；需 `xlrd`）（月底）[2026-11]
- 土地註冊處、統計處（零售、失業、GDP、CPI）新聞稿：經 `info.gov.hk/gia/general/{yyyyMM}/{dd}.htm` 按日索引找（只掃窗口內約 30 頁，最省請求）[2026-11]
- 中原 CCL：`hk.centanet.com/CCI/index`，漲跌號解析 `window.__NUXT__`（每週五）[2026-11]
- 美國 FOMC：`federalreserve.gov/newsevents/pressreleases/monetary{yyyyMMdd}a.htm`（年 8 次）[2026-11]
- 旅發局訪港旅客：官方數字常找不到，只有媒體摘要（月中）[2026-11]
- 施政報告、預算案、印花稅／樓市措施：`info.gov.hk`（不定期）

**B 研究報告**：可 curl [2026-11]：萊坊 `content.knightfrank.com`、Savills `pdf.savills.asia`、JLL 新聞稿 `jll.com.hk`。CBRE、高力回 403 只能取索引；戴德梁行、美聯／中原研究 [未驗證]；評級機構對港 REIT 的公開評論。

**C 新聞**：香港經濟日報、信報、明報、AAStocks、新浪港股、Reuters／Bloomberg、智通財經、KPMG 稅務快訊。AAStocks 冷門 REIT 列表常停在數月前 → 改 Exa [2026-11]。

**D REIT 市場**：全部港股 REIT 的窗口內 HKEXnews 公告（`collectStk` §5.4，起日填 `WINDOW_START`）。上市 REIT 11 檔 [2026-11-20 核對]：00823 領展、02778 冠君、00778 置富、00435 陽光、00808 泓富、00405 越秀、01881 富豪、87001 匯賢（RMB）、01426 春泉、01503 招商局商業、02191 順豐（2026-10-29 公布出售全部物業後清盤除牌，完成後刪除）。每次核對新上市／除牌並改寫本列。
- 名單＋收盤＋殖利率＋市值：curl `hkex.com.hk/market-data/securities-prices/real-estate-investment-trusts`，grep `return "evL…"` 取 token → `www1.hkex.com.hk/hkexwidget/data/getreitfilter?lang=eng&token={token}&sort=5&order=0&all=1&qid=1&callback=cb`（Referer `hkex.com.hk`）[2026-11]
- 單位數：HKEXnews「單位變動月報表」，pdftotext 後找 `Balance at close of the month` [2026-11]
- 恒生 REIT 指數無免授權來源，以 HKEX 殖利率表代替 [2026-11]

**E 輿情**：LIHKG（地產台、財經台）、香港討論區 `discuss.com.hk`、高登、雪球、東方財富股吧（`hk00823` 等）、moomoo／長橋社區、X、Reddit（r/HongKong，經 Apify）、Mobile01。需授權時 Exa 可取 `discuss.com.hk/archiver/?tid-{id}.html`、LIHKG `lihkg.com/category/37` 標題快照、雪球 `/S/{代號}/news`。港 REIT 討論基本不在 PTT [2026-11]。

### 4.3 其他國家（首次執行時新增 `### 4.N {國家}` 小節）
- A 官方：央行（政策利率、房貸）、統計局（CPI 房租、營建）、住房主管機關（房價、交易量）、10 年公債
- B 報告：當地 REIT 協會（Nareit、REITAS、證交所 REITs 專區）、四大顧問行季報
- C 新聞：當地主流財經媒體 2～3 家｜D REIT：交易所全名單與窗口內公告｜E 輿情：`AGENTS.md` §6 該國平台

## 5. 中國房地產（hk 必跑；cn 亦適用）

優先序：官方 ＞ 國際投行／評級 ＞ 專業機構 ＞ 媒體 ＞ 論壇。同樣只收窗口內發布。
- **房價**：NBS 70 城新建／二手（逐城）`stats.gov.cn/sj/zxfb/{yyyyMM}/t{yyyyMMdd}_{id}.html`，解讀頁 `/sj/sjjd/`（每月 15～17 日）[2026-11]
- **銷售／開發**：NBS 銷售面積與金額、開發投資、新開工、到位資金、待售面積（同上）
- **民間價格與租金 ⭐**：中指 `cih-index.com/news/…`：百城價格、50 城租金（月初）；NBS CPI 房租（9～10 日）[2026-11]
- **房企**：克而瑞百強（月底）[未驗證]；萬科、碧桂園、恒大、融創等展期／重組（HKEXnews、財新、Reuters）
- **信貸**：PBOC 居民中長期貸款（月中）、LPR（20 日）
- **政策**：收儲、白名單、限購、城中村改造、土地制度（`gov.cn`、`mohurd.gov.cn`、`mnr.gov.cn`）
- **財政**：財政部土地出讓收入 `gks.mof.gov.cn/tongjishuju/…`（每月 19～20 日）[2026-11]
- **一線商辦**：萊坊各城季報 PDF、JLL、高力、戴德梁行、CBRE（季後 2～4 週）
- **機構預測**：Fitch、S&P、Moody's、UBS、GS、MS、Reuters Poll
- **輿情**：雪球、東方財富股吧房地產板塊、淘股吧、新浪股吧、X、Reddit

## 6. 執行報告與 push

報告寫到 `<REPO>/Log/collectState_{CC}_Summary_{yyyyMMdd}.md`，包含：
1. 窗口、資料夾檔數（新增 N／刪除 N）
2. 各類（A～F）新增檔數與代表檔；本期重要新資料 3～5 點（只列事實與數字，附發布日）
3. 失敗或被擋網站（來源、原因、已試過什麼）
4. 資料缺口（窗口內無新發布的來源及最新一期日期、去重略過數）
5. purge 刪除清單
6. 轉檔統計（Convert2md＋convert＋保留的原檔）
7. 使用的 MCP 與帳號級錯誤
8. 本次 Skill 維護（沒有寫「無」）

commit `{cc}_state/`（含刪除）、`Log/collectState_*`、`Log/conversion_summary.md`、本 Skill 修改；push 前 `git diff --cached --name-only` 確認沒動到 §0-6 禁止的檔。雲端／feature 分支 → push 該分支並開 PR；本機直跑 → push `master`。

## 7. Skill 維護

1. 站點新行為（封鎖、新 API、網址改變、發布日改變）→ 改寫 §4／§5 對應那行並更新 `[yyyy-mm]`；合併不追加，失效做法直接刪。個股站點寫回 `collectStk` §4（`collectStk/references/` 對應市場檔）。
2. `.claude/skills/collectState/` 與 `.agents/skills/collectState/` 必須完全相同（`diff -r` 確認）。
3. `AnalysisResult.md` 列在 `state_tools.py` 的 `PROTECTED`；`stateAnalysis` 改輸出檔名時同步改。
4. `stateAnalysis` 讀當月與上月月檔，窗口不可短於 1 個月。
5. 依賴 `Convert2md` 的 `scan_pending.py` 第 3 個參數（掃描範圍）。
6. `*_state` 是非公司資料夾，會掃描根目錄的 Skill／Routine 要排除它。
