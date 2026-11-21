---
name: collectState
description: 國家層級 REIT 投資情報收集 — 指令如 `jp /collectState`、`hk /collectState`（或 `/collectState jp`）。先刪除 {cc}_state/ 內三個月前的資料，再收集該國過去 1 個月的總經／房地產／REIT 新聞、研究報告與多平台輿情（hk 同步分析中國房地產），所有 PDF／HTML／Word／Excel 一律轉成 Markdown（PDF 走 Convert2md），最後重寫 {cc}_state/StateAnalysis.md 作為 REIT 投資分析依據並 push。
argument-hint: "<國家代碼：jp | hk | tw | us | sg …>"
---
/goal
# collectState — 國家層級 REIT 情報收集與分析

> **任務**：對指定國家（市場）① 清掉三個月前的舊資料 ② 收集過去 1 個月的新聞、研究報告、官方數據與輿情 ③ 全部轉 Markdown ④ 重寫 REIT 投資分析 `StateAnalysis.md` ⑤ 寫執行報告並 push。
> 本指南適用所有 AI（Claude / Gemini，含輕量模型），請一步一步照做。抓取技術細節**一律沿用** `CollectsentimentAndReports` Skill，本檔不重寫。

## 0. 五條底線（違反任一 = 任務失敗）

1. **防幻覺**：只記錄真實抓到的內容，附真實 URL 與真實發布日。抓不到就照 `CollectsentimentAndReports` §8.5 誠實記錄；**嚴禁**用訓練資料補數字、捏造連結或分配日期。自算數字附公式或標 `(估)`。
2. **先清後收**：Phase 1 清理三個月前資料**一定先跑**，清完才收集。
3. **全部轉 Markdown**：任務結束時 `{cc}_state/` 只能有 `.md`（`check` 子命令通過）。轉不了的原檔保留並寫進報告，不可硬刪。
4. **即時存檔**：每抓完一份報告、一個來源，立刻寫檔並記 manifest，不要等全部做完。
5. **檔案隔離**：只能寫入 `{cc}_state/`、`Log/collectState_*`、本 Skill（維護用）。`Analysis/*`、`*ScreenerResult/`、公司資料夾**只讀**。

---

## 1. 參數與路徑

### 1.1 指令解析

| 使用者輸入 | 解析結果 |
| :--- | :--- |
| `jp /collectState`、`/collectState jp`、`/collectState JP` | `CC=jp` |
| `hk /collectState`、`/collectState hk` | `CC=hk`（**加跑 §5 中國房地產**） |
| `tw /collectState`、`us /collectState`、`sg /collectState`… | `CC=tw` 等（走 §4.3 通用清單） |
| 沒有國家代碼 | 立刻詢問，不可自行猜 |

- `CC` 一律轉小寫，只接受 2~3 個英文字母（ISO 3166 國碼慣例：`jp` 日本、`hk` 香港、`tw` 台灣、`us` 美國、`sg` 新加坡、`cn` 中國）。
- 別名：`japan`→`jp`、`hongkong`/`hong kong`→`hk`、`taiwan`→`tw`。

### 1.2 名詞

| 名詞 | 值 |
| :--- | :--- |
| `<REPO>` | 儲存庫根目錄絕對路徑（雲端 `/home/user/FinancialReport`；Windows 本機如 `D:\FinancialReport`） |
| `<SCRATCH>` | 暫存目錄絕對路徑（有 scratchpad 就用 scratchpad；不可放在 repo 內） |
| `<FOLDER>` | `<REPO>/{cc}_state`（例：`jp_state`、`hk_state`），不存在就建立 |
| `<TOOLS>` | `<REPO>/.claude/skills/collectState/scripts/state_tools.py`（Gemini 用 `.agents/...` 同名檔） |
| `TODAY` | 執行當日（UTC+8） |
| `WINDOW` | 收集窗口：`TODAY − 1 個月` ～ `TODAY` |
| `CUTOFF` | 保留截止日：`TODAY − 3 個月`（早於此日的資料在 Phase 1 刪除） |

### 1.3 `{cc}_state/` 檔案規格

| 檔案 | 命名 | 說明 |
| :--- | :--- | :--- |
| 單篇資料 | `{yyyyMMdd}_{類型}_{來源}_{短標題}.md` | `yyyyMMdd` = **原文發布日**（不是下載日）；保留期依此判斷 |
| 月度輿情新聞彙整 | `{yyyyMM}_{CC}_輿情新聞.md` | `yyyyMM` = 執行當月；Append 模式（§3.5） |
| REIT 投資分析 | `StateAnalysis.md` | 每次整份重寫，受保護不被清理（§6） |
| 資料索引 | `0.Index.md` | `finalize` 自動產生，**勿手改**；下次收集用它去重 |

- `{類型}` 只能用：`News`（新聞）、`Report`（研究／顧問行／券商報告）、`Data`（官方統計、指數）、`Policy`（政策、法規、央行）、`REIT`（個別 REIT 公告／決算／IR）、`Sentiment`（單篇長文輿情，如 note、雪球長文）。
- `{來源}` 用英文或原文簡稱（`BOJ`、`MLIT`、`CBRE`、`JLL`、`Nikkei`、`HKMA`、`RVD`、`NBS`、`中指`…）；`{短標題}` ≤ 30 字。
- 檔名不可含空白與 `\ / : * ? " < > |`；不要建子資料夾。
- 下載時保留原始副檔名（`.pdf` / `.html` / `.docx` / `.xlsx` …），Phase 4 再統一轉 `.md`。用 MCP 直接拿到 Markdown 正文的網頁，可直接存成 `.md`（仍要記 manifest）。

### 1.4 manifest（每存一份檔就追加一筆）

存在 `<SCRATCH>/state_manifest.json`（JSON 陣列），Phase 4 `finalize` 用它幫每份 `.md` 補來源標頭：

```json
[{"file": "20261115_Report_CBRE_JapanOfficeQ3.pdf", "url": "https://...", "title": "Japan Office MarketView Q3 2026",
  "publisher": "CBRE Japan", "published": "2026-11-15", "type": "Report", "note": "付費牆僅摘要"}]
```

---

## 2. 流程總覽

| Phase | 內容 | 執行者 |
| :--- | :--- | :--- |
| 0 | 解析 `CC`、建立 `<FOLDER>`、同步 repo（`git fetch origin master && git merge --no-edit FETCH_HEAD`） | 主代理人 |
| 1 | **清理三個月前資料**（§3.1） | 主代理人 |
| 2 | 盤點既有資料、決定本次缺口（§3.2） | 主代理人 |
| 3 | 收集：官方數據／政策 → 研究報告 → 新聞 → REIT 市場與個別 REIT → 輿情；`hk` 另加中國房地產（§3.3、§4、§5） | 可分 2~3 個子代理人平行（如：A 官方＋報告、B 新聞＋REIT、C 輿情），各自寫不同檔案 |
| 4 | 轉 Markdown：`Convert2md` Skill（PDF）→ `convert`（其他格式）→ `finalize`（§3.4） | 主代理人 |
| 5 | 重寫 `StateAnalysis.md`（§6） | 主代理人 |
| 6 | `check` 自檢 → 執行報告 → Skill 維護 → commit / push（§7、§8） | 主代理人 |

---

## 3. 各 Phase 細節

### 3.1 Phase 1 — 清理三個月前資料（每次 collect 前必做）

```bash
python <TOOLS> purge --folder <FOLDER>            # 先 dry-run，看清單
python <TOOLS> purge --folder <FOLDER> --apply    # 確認無誤才真的刪
```

- 判斷依據：檔名 `yyyyMMdd_` 前綴（月檔 `yyyyMM_` 以該月最後一天計）；**不看 mtime**（git clone 會把 mtime 重設成今天）。
- 沒有日期前綴的檔案：以 git 首次加入日判斷，並在報告列為「待改名」；本次收集的新檔一律要有前綴。
- `StateAnalysis.md`、`0.Index.md` 受保護，不會被刪（每次重寫）。
- 刪除清單原樣貼進執行報告 §4。

### 3.2 Phase 2 — 盤點

依序讀（只讀不改）：

1. `<FOLDER>/0.Index.md`：已收過的原文 URL → 本次**不重複下載**。
2. `<FOLDER>/StateAnalysis.md`：上次結論、資料缺口、下次待辦 → 本次優先補。
3. 當月 `{yyyyMM}_{CC}_輿情新聞.md`：每個來源上次收到哪一天，只補新內容。
4. 既有分析（存在才讀）：`jp` → `Analysis/JpStateResult.md`、`JpReitScreenerResult/0.JpReitScreenerResult.md`；`hk` → `Analysis/HkStateResult.md`、`HkReitScreenerResult/0.HkReitScreenerResult.md`。用來對齊 REIT 標的池與上次燈號，**不得修改**。
5. 本機 REIT 公司資料夾（如 `2971ES-CON日本REIT/`、`01426春泉Reit/`）的 `AnalysisResult.md`：取最新 DPU、NAV、LTV 等數字的基準與股數口徑。

### 3.3 Phase 3 — 收集規則

**抓取技術**：完全依 `CollectsentimentAndReports` Skill：§0 底線、§3 通用抓取規則（固定順序、次數上限、失敗定義、網路錯誤零重試、帳號級錯誤停用、請求頻率、搜尋摘要使用條件）、§4 站點知識庫、§5 已驗證 API/SOP、§8.3 過濾規則、§8.5 失敗寫法。新發現的**國家層級**站點行為寫進本檔 §4／§5；**個股**站點行為寫回 `CollectsentimentAndReports` §4。

**窗口**：只收 `WINDOW` 內發布的內容。例外：月報／季報類指標或顧問行季報若「最新一期」發布在窗口外，仍可收，`note` 寫「最新一期，發布於窗口外」。

**每類最低目標**（達不到要在報告寫原因，不可灌水）：

| 類別 | 目標 | 存法 |
| :--- | :--- | :--- |
| A 官方數據／政策 | §4 清單逐項確認是否有新發布；有新發布就存原檔（PDF／Excel／HTML） | 單篇檔（`Data`／`Policy`） |
| B 研究報告 | ≥ 3 份顧問行／智庫／券商公開報告（PDF 優先） | 單篇檔（`Report`） |
| C 新聞 | ≥ 10 則與房地產／利率／REIT 直接相關的新聞，重要的 3~5 則存全文 | 摘要進月檔；全文存單篇檔（`News`） |
| D REIT 市場 | REIT 指數、平均殖利率、利差；§4 標的池**每一檔**查窗口內公告（決算、增發、收購、配息、評級） | 指數進月檔；公告存單篇檔（`REIT`） |
| E 輿情 | §4 列出的平台**每個都要嘗試**，成功 ≥ 5 個平台 | 進月檔（重要長文另存 `Sentiment`） |
| F 中國房地產（僅 `hk`） | §5 清單逐項 | 單篇檔＋月檔章節 |

**輿情判讀**：每則標明 🟢 利多／🔴 利空／⚪ 中性；明顯誇大或與官方數據矛盾標「⚠️ 與 {官方來源} 不符」；內容農場、AI 自動稿、導流帳號要標明或排除；同一事件不同轉載數字矛盾 → `⚠️ 未經證實（不可採信）`，不得進入 §6 結論。

### 3.4 Phase 4 — 全部轉 Markdown

依序：

1. **PDF** → 呼叫 **`Convert2md` Skill**（它會掃到 `<FOLDER>` 內的 PDF；成功刪 PDF、CID 亂碼刪 `.md` 留 PDF）。CID 失敗的 PDF：改抓英文版／HTML 版或換來源；都沒有就保留 PDF 並寫進報告。150 頁以上的報告依 `CollectsentimentAndReports` §9 處理逾時。
2. **其他格式**（HTML、Word `.docx/.doc`、Excel `.xlsx/.xls`、PowerPoint `.pptx/.ppt`、RTF、ODT、CSV、TXT、JSON、XML、EPUB）：
   ```bash
   python <TOOLS> convert --folder <FOLDER> --scratch <SCRATCH>
   ```
   轉換鏈 markitdown → pandoc → BeautifulSoup+markdownify；舊版 Office 先經 LibreOffice 轉 OOXML。正文 < 200 字、JS 外殼／封鎖頁、CID 亂碼一律判失敗並**保留原檔**。圖片（`.png/.jpg`）不能轉文字：把圖表上的數字寫進對應 `.md` 後手動刪圖。
   - 本機缺套件時：`pip install "markitdown[all]" beautifulsoup4 markdownify`；pandoc／LibreOffice 為選配。
3. **補標頭＋索引**：
   ```bash
   python <TOOLS> finalize --folder <FOLDER> --manifest <SCRATCH>/state_manifest.json
   ```
   幫每份 `.md` 加來源標頭（標題、來源、原文 URL、發布日、收集日、類型），移除失效的 `pdf_images`／base64 圖片連結，重建 `0.Index.md`。

### 3.5 月度輿情新聞彙整檔（`{yyyyMM}_{CC}_輿情新聞.md`）

- 範本與失敗寫法沿用 `CollectsentimentAndReports` §8.4／§8.5，標題改為 `# [{CC} 國家層級] REIT／房地產輿情與新聞整理 ({YYYY}/{MM})`。
- 章節順序固定：`## 一、官方數據與政策` → `## 二、研究報告摘要` → `## 三、新聞` → `## 四、REIT 市場與個別 REIT` → `## 五、中國房地產`（僅 `hk`）→ `## 六、輿情（依平台）`；每個平台／來源是一個 `### [來源名稱]` 子章節，含抓取時間、抓取方式、抓取結果（✅／⚠️ 僅索引／❌／⭕ 無新內容）。
- **Append 模式**：已存在的章節只補在末尾，不可覆蓋舊內容；每抓完一個來源立刻寫入。
- 每則：來源連結、真實發布時間、核心觀點引述、關鍵要點、🟢／🔴／⚪ 標記。提到金額時，與 REIT 相關的換算**每單位金額**（金額 ÷ 最新已發行單位數，註明口徑與日期）。

---

## 4. 各國資料來源清單

> 起始清單（2026-11 建檔）。標 `[未驗證]` 的站點第一次使用時照 `CollectsentimentAndReports` §3 抓取，結果依 §8 寫回本表並改成 `[yyyy-mm]`。已在 `CollectsentimentAndReports` §4 記載的站點（日經、株探、Yahoo JP、5ch、note、JAPAN-REIT.COM、HKEXnews、AAStocks、新浪、雪球、股吧、LIHKG、moomoo、香港經濟日報…）照該處做法。

### 4.1 日本（`jp`）

**A 官方數據／政策**

| 指標 | 來源 | 慣例發布 |
| :--- | :--- | :--- |
| 金融政策決定会合（聲明、展望報告、總裁記者會）、短觀 | 日本銀行 `boj.or.jp` | 年 8 次會議；短觀 4/7/10/12 月 |
| 10 年期 JGB 殖利率 | 財務省 `mof.go.jp` 國債金利情報（CSV） | 每營業日 |
| CPI（含家賃） | 總務省統計局 `stat.go.jp` | 每月 20 日前後 |
| 不動產價格指數、地價公示／基準地價、建築著工 | 國土交通省 `mlit.go.jp` | 月底；3 月／9 月；月底 |
| 首都圈／近畿圈新築公寓動向 | 不動產經濟研究所 `fudousankeizai.co.jp` [未驗證] | 每月中旬 |
| 中古公寓成約（月例速報 PDF） | 東日本 REINS `reins.or.jp`（憑證鏈常不完整，失敗即依 §3 換 MCP） | 每月中旬 |
| 中古公寓價格／租金 | 東京 Kantei `kantei.ne.jp` [未驗證] | 每月下旬 |
| 東京都心 5 區辦公室空室率／租金 ⭐ | 三鬼商事 `e-miki.com` [未驗證] | 每月第 2 個週四 |
| 訪日外客數 | JNTO `jnto.go.jp` | 每月中旬 |
| 不動產相關稅制、法規（12 月稅制大綱） | 財務省、國會、金融廳 | 不定期 |

**B 研究報告**（公開免費 PDF 為主）：ARES 不動產證券化協會 `ares.or.jp`（J-REIT 月次市場資料）、日本不動產研究所 JREI `reinet.or.jp`（不動產投資家調查）、Nissay 基礎研究所 `nli-research.co.jp`（不動產投資報告）、三井住友信託基礎研究所 `smtri.jp`、大和總研 `dir.co.jp`、CBRE `cbre.co.jp`、JLL `jll.co.jp`、Cushman & Wakefield、Savills `savills.co.jp`、Colliers [均未驗證]。券商（野村、大和、SMBC 日興、みずほ）報告多為客戶限定，只收公開摘要並註明。

**C 新聞**：日經（不動產、J-REIT、日銀）、Reuters／Bloomberg 日本房地產、東洋経済、住宅新報 `jutaku-s.com` [未驗證]、株探 J-REIT 市況、Yahoo JP ニュース。

**D REIT 市場**：東證 REIT 指數水位與平均殖利率、對 10 年 JGB 利差（JAPAN-REIT.COM 首頁有彙總）；增資（公募增資）、新上市、合併、TOB 公告（TDnet，經株探／JAPAN-REIT.COM）。**標的池** = `Analysis/gemini_JPState.md` §4.1 標的池（8951、8952、3281、3269、8985、8953、3462、8954）＋本機 J-REIT 資料夾（2971、3455、2989、3492、3451）＋ `JpReitScreenerResult/` 最新榜單前 10。

**E 輿情**：5ch（株式板 J-REIT スレ，`find.5ch.io` 搜「REIT」「リート」）、X（`J-REIT`、`Jリート`、個別投資法人名）、Yahoo JP 掲示板（標的池各檔）、note（「Jリート」新着）、みんかぶ、PTT Stock（`日本REIT`、`J-REIT`）、Reddit（r/JapanFinance、r/JapanFIRE，經 Apify）、Dcard／Mobile01（日本房地產、J-REIT）。

### 4.2 香港（`hk`）— 另必跑 §5 中國房地產

**A 官方數據／政策**

| 指標 | 來源 | 慣例發布 |
| :--- | :--- | :--- |
| HIBOR、基本利率、貨幣統計、按揭統計 | 金管局 HKMA `hkma.gov.hk` | 每日；每月 |
| 私人住宅售價／租金指數、寫字樓／商舖租金與售價指數（Excel） | 差餉物業估價署 RVD `rvd.gov.hk` | 每月底（前月值） |
| 買賣合約登記宗數與金額 | 土地註冊處 `landreg.gov.hk` | 每月初 |
| 零售業總銷貨、失業率、GDP | 統計處 `censtatd.gov.hk` | 每月初／季 |
| 訪港旅客 | 旅發局 `partnernet.hktb.com` [未驗證] | 每月中 |
| 中原城市領先指數 CCL | 中原地產 `centadata.com` [未驗證] | 每週五 |
| 美國 FOMC（港元聯繫匯率傳導） | Fed `federalreserve.gov` | 年 8 次 |
| 施政報告、財政預算案、印花稅／樓市措施 | 香港政府新聞公報 `info.gov.hk` | 不定期 |

**B 研究報告**：JLL `jll.com.hk`、CBRE `cbre.com.hk`、高力 Colliers、萊坊 Knight Frank（住宅／寫字樓月報 PDF）、第一太平戴維斯 Savills、戴德梁行 Cushman & Wakefield、美聯／中原研究部 [均未驗證]；評級機構（Fitch、S&P、Moody's）對港 REIT 的公開評論。

**C 新聞**：香港經濟日報、信報、明報財經、AAStocks、新浪港股、Reuters／Bloomberg 香港地產、智通財經（照 `CollectsentimentAndReports` §4.3）。

**D REIT 市場**：全部港股 REIT 窗口內 HKEXnews 公告（照 `CollectsentimentAndReports` §5.4）：`00823` 領展、`00405` 越秀、`01426` 春泉、`87001` 匯賢、`01503` 招商局商業、`02191` 順豐、`00778` 置富、`00435` 陽光、`02778` 冠君、`00808` 泓富、`01275` 開元（已停牌者註明）[清單未驗證，以 HKEX 上市 REIT 名單為準]；`HkReitScreenerResult/` 最新榜單對照。

**E 輿情**：LIHKG（地產台、財經台）、香港討論區 `discuss.com.hk`（地產版）、高登財經台、雪球（領展／越秀等 REIT 頁與「香港REIT」話題）、東方財富股吧（`hk00823` 等）、moomoo 社區、X、Reddit（r/HongKong、r/HKinvesting，經 Apify）、PTT Stock（`港股REIT`、`領展`）、Mobile01。

### 4.3 其他國家（`tw`、`us`、`sg`、`cn` …）通用清單

照同樣六類收集，第一次執行時先決定來源並寫進本檔新增的 `### 4.N {國家}` 小節：

| 類別 | 必找來源類型 |
| :--- | :--- |
| A 官方 | 央行（政策利率、房貸統計）、統計局（CPI 房租、營建）、住房／國土主管機關（房價指數、交易量）、10 年公債殖利率 |
| B 報告 | 當地 REIT 協會（如 Nareit、REITAS、台灣證交所 REITs 專區）、四大顧問行（CBRE、JLL、Cushman、Colliers）當地季報 |
| C 新聞 | 當地主流財經媒體 2~3 家 |
| D REIT | 當地交易所上市 REIT 全名單與窗口內公告；本機資料夾中該國的 REIT |
| E 輿情 | `AGENTS.md` §6 列出的該國平台 |

---

## 5. 中國房地產（`hk` 必跑；`cn` 亦適用）

> 對齊 `Analysis/gemini_HkState.md` §2.2／§5／§6 的指標，讓兩邊可交叉驗證。優先序：官方 ＞ 國際投行／評級 ＞ 專業機構 ＞ 主流媒體 ＞ 論壇。

| 面向 | 指標 | 來源 | 慣例發布 |
| :--- | :--- | :--- | :--- |
| 房價 | 70 城新建／二手住宅價格指數（環比、同比，一線逐城） | 國家統計局 NBS `stats.gov.cn` | 每月 15~17 日 |
| 銷售／開發 | 商品房銷售面積與金額、開發投資、新開工、**到位資金**、待售面積 | NBS | 同上 |
| 民間價格 | 百城新建／二手均價、漲跌城市家數 | 中指研究院 [未驗證] | 月初 |
| 租金 ⭐ | 50 城住宅租金（含一線逐城）；CPI 租賃房房租 | 中指；NBS | 月初；每月 9~10 日 |
| 房企 | 百強房企銷售榜；萬科、碧桂園、恒大、融創等債務展期／重組／清盤 | 克而瑞 CRIC [未驗證]；HKEXnews；財新、Reuters | 月底；不定期 |
| 信貸 | 居民中長期貸款、LPR、房貸利率下限 | 人民銀行 PBOC `pbc.gov.cn` | 月中；每月 20 日 |
| 政策 | 收儲、白名單融資、限購鬆綁、城中村改造、土地制度 | 國務院 `gov.cn`、住建部 `mohurd.gov.cn`、自然資源部 `mnr.gov.cn`、各地房管局 | 不定期 |
| 財政 | 國有土地使用權出讓收入年增率 | 財政部 `mof.gov.cn` | 每月中 |
| 一線商辦 | 京滬穗深甲級寫字樓空置率、租金、續租調整率 | 高力、JLL、戴德梁行、CBRE | 季後 2~4 週 |
| 機構預測 | Fitch、S&P、Moody's、UBS、GS、MS、Reuters Poll | 各機構新聞稿 | 不定期 |
| 輿情 | 雪球（地產話題）、東方財富股吧房地產板塊、淘股吧、新浪財經股吧、X、Reddit（r/China_irl 等） | §3.3 E 類規則 | — |

- 判讀原則：環比看轉折、同比看趨勢；新房受結構效應影響，**以二手為準**；NBS 70 城與中指百城口徑不同，兩者都列。
- 輸出到 `StateAnalysis.md` §5，並寫出「中國房市 → 香港 REIT」傳導（`87001`、`01426`、`00405`、`01503` 中國曝險高；`00823` 作對照組）。

---

## 6. Phase 5 — `StateAnalysis.md`（REIT 投資分析，每次整份重寫）

### 6.1 寫作規則

1. 第一行固定：`> 最後更新：YYYY-MM-DD HH:MM (UTC+8)｜資料窗口：YYYY-MM-DD ~ YYYY-MM-DD｜collectState {CC}`。
2. 只引用 `<FOLDER>` 內已存檔的資料或本次實際抓到的一手來源；每個數字附「來源＋發布日」，查不到寫 `N/A（原因）`。
3. **利多與利空並陳**（`AGENTS.md` §1），每項寫「具體事件 → 對 DPU／NAV／殖利率的潛在影響」。
4. 金額**每單位化**：金額 ÷ 最新已發行單位數（註明口徑、日期）。
5. **不分析 REIT ETF**（`AGENTS.md` REIT 規則 §1）；REIT 指數只當市場溫度計。
6. 個別 REIT 只做 §6.2 第四章的核心數字；完整個股規則（EPS、五年 ROE、CAGR、年報季報深度分析）交給 `StockAnalysis` Skill，本檔只引用其 `AnalysisResult.md` 結論。
7. 全檔 ≤ 600 行；超過就刪「不影響買賣判斷」的段落。

### 6.2 骨架（照抄標題逐次填寫）

````markdown
> 最後更新：…｜資料窗口：…｜collectState {CC}

# {國家} 房地產景氣 × REIT 投資分析

## 〇、一句話結論與進場建議
- 一句話結論：（現在該 加碼／分批／觀望／減碼 該國 REIT，理由一句）
- 景氣階段：① 下行 ／ ② 築底 ／ ③ 復甦初期 ／ ④ 擴張 ／ ⑤ 過熱（附判定依據）
- 進場時點推估：（季度＋信心度%）
- 跟上次比，變了什麼：（3 點以內，附數字）

## 一、總經與利率
- 政策利率／下次會議日／市場預期：
- 10 年公債殖利率：
- REIT 平均殖利率 − 10 年公債 = 利差（bps）：
- 通膨（含房租項目）、薪資：
- 匯率（對 TWD）：

## 二、本國房地產市場（分板塊）
- 住宅（價格、租金、成交量）：
- 辦公室（空置率、租金、新供給）：
- 商場／零售（銷貨、客流、租金）：
- 物流：
- 飯店（旅客、RevPAR）：

## 三、REIT 市場總覽
- REIT 指數水位與 1 個月／3 個月漲跌：
- 平均殖利率、平均股價淨值比（P/NAV）、平均負債比率（LTV）：
- 資金動向（增資、新上市、收購、私有化、外資買賣）：

## 四、標的池逐檔核心數字（每檔一段，key-value 條列）
### {代號} {名稱}
- 股價（日期）：
- 股價淨值比（P/NAV）：
- 殖利率（近 12 個月 DPU ÷ 股價）：
- 租金報酬率（NOI yield 或 cap rate，註明口徑）：
- 空租率（＝ 1 − 出租率）：
- 負債比率（＝ 負債 ÷ 總資產 × 100%）：
- 本月重要公告（附每單位金額）：
- 燈號：🟢 可買／🟡 觀望／🔴 避開 ＋ 一句話理由

## 五、中國房地產（僅 hk；其他國家刪除本章）
- 房價（NBS 70 城／中指百城，一線逐城）：
- 銷售、開發投資、到位資金、庫存：
- 租金（50 城／一線）：
- 房企債務與政策：
- 三年情境（樂觀／基準／保守 機率）：
- 傳導到香港 REIT：

## 六、核心利多（成長動能）
1. 事件 → 對 DPU／NAV／殖利率的影響（附數字、來源日）

## 七、核心風險（潛在隱憂）
1. 起因與對象 → 對 REIT 財務或估值的具體損害程度

## 八、輿情總結
- 🟢 多方主要論點（平台、日期）：
- 🔴 空方主要論點：
- ⚠️ 已辨識的假消息／誇大／內容農場：
- 輿情 vs 基本面是否背離：

## 九、接下來看這 3 件事（會改變看法的條件與日期）

## 十、資料缺口與下次待辦
- 缺什麼／原因（① 未發布 ② 來源被擋 ③ 預算不足 ④ 需更多期數）／下次怎麼補

## 附錄：本次引用來源（連到 `{cc}_state/` 內檔案或原文 URL）
````

---

## 7. Phase 6 — 自檢、執行報告、push

### 7.1 自檢

```bash
python <TOOLS> check --folder <FOLDER>
```

必須全部通過（只剩「轉換失敗而保留的原檔」可例外，並寫進報告）。另外人工確認：`StateAnalysis.md` 第一行時間戳已更新、§〇～§十 都有內容、利多與利空都有、`hk` 有第五章。

### 7.2 執行報告

寫到 `<REPO>/Log/collectState_{CC}_Summary_{yyyyMMdd}.md`：

````markdown
# collectState 執行報告 — {CC} — YYYY/MM/DD

- **資料窗口**：YYYY-MM-DD ~ YYYY-MM-DD｜**保留截止日**：YYYY-MM-DD
- **資料夾**：`{cc}_state/`（執行後共 N 個檔）

## 1. 收集成果
| 類別 | 新增檔案數 | 代表檔案 | 備註 |
| :--- | :--- | :--- | :--- |
（A 官方／B 報告／C 新聞／D REIT／E 輿情／F 中國房地產）

**本期重點**：（3~5 點，附數字與每單位金額）

## 2. 失敗或被擋網站
- **來源**：[網站](URL)｜**原因**：…｜**已試過**：…

## 3. 資料缺口說明
## 4. Phase 1 清理紀錄（刪除了哪些三個月前的檔案；沒有就寫「無」）
## 5. Phase 4 轉檔紀錄（Convert2md 統計＋convert 統計＋失敗保留的原檔）
## 6. 本次使用的 MCP（人類可讀名稱；帳號級錯誤也寫這裡）
## 7. Skill 維護（本次新增、修改、刪除了本檔哪些內容；沒有就寫「無」）
````

### 7.3 push

> [!IMPORTANT]
> 報告寫完後，把 `{cc}_state/`（含刪除）、`Log/collectState_*`、`Log/conversion_summary.md`、本 Skill 的修改一起 commit 並 push，任務才算完成。推送分支規則同 `CollectsentimentAndReports` §10：雲端／指定 feature 分支 → push 該分支並開 PR（auto-merge workflow 會合併進 `master`）；本機直跑 → push `master`。push 前 `git diff --cached --name-only` 確認沒有動到 §0-5 禁止的檔案。

---

## 8. Skill 維護規則

1. 國家層級站點的新行為（新封鎖、新 API、新捷徑、舊做法失效）→ 改寫 §4 對應國家表格的那一列（`[未驗證]` 改成 `[yyyy-mm]`）；多步驟用法加到 §5 或新增 `### 4.N` 小節。**合併而不是追加**，失效做法直接刪。
2. 個股站點的新行為 → 寫回 `CollectsentimentAndReports` §4（照它的 §11 規則），本檔不重複。
3. 第一次跑新國家 → 新增 `### 4.N {國家}` 小節。
4. 兩份同步：`.claude/skills/collectState/`（`SKILL.md`＋`scripts/state_tools.py`）與 `.agents/skills/collectState/` 必須完全相同（改完 `diff -r` 確認）。
5. `*_state` 資料夾是**非公司資料夾**：`Routines_Move2History.md`、`ArrangePublicOpinionMd`、`Analysis/LatestNews_check.py` 已排除；新增會掃描根目錄的 Skill／Routine 時也要排除 `*_state`。
6. 在 §7.2 報告的「Skill 維護」寫明本次改了什麼。
