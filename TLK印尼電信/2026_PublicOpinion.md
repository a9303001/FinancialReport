# [TLK印尼電信] 2026 年 輿情彙整

> 本檔由 **ArrangePublicOpinionMd Skill** 自動彙整，內容為本資料夾 2026 年度所有「輿情／新聞／討論區」`.md` 的原文合併。
> 不含年報、季報、公司公告 report。
> 最後彙整時間：2026-10-26 02:11（2026-10-31 補充 3Q 財報與 10/30 市場資料）｜本次併入：1 檔｜累計併入：1 檔

## 目錄

- [2026-10 · 輿情新聞](#2026-10--輿情新聞)

<!-- body:start -->

## 2026-10 · 輿情新聞

<!-- source-file: 202610_輿情新聞.md | bytes: 54905 | sha1: 0de71d8705c9 | merged-at: 2026-10-26 -->

### [TLK 印尼電信 PT Telkom Indonesia] 輿情與新聞整理 (2026/10)

- **分析月份**：2026/10
- **資料範圍**：2026-07-19 ~ 2026-10-19（首次收集，涵蓋近三個月）
- **最後更新**：2026-10-25 01:40 UTC
- **標的**：NYSE `TLK`（ADR，1 ADS = 100 股 B 股）；母股為印尼 IDX `TLKM`
- **每股換算基準**：2026-09-30 臨時股東會公告之有表決權股數 98,580,940,800 股（已扣庫藏股）≒ 9.858 億 ADS 當量

---

#### [SEC EDGAR 6-K 官方公告]

- **抓取時間**：2026-10-19
- **抓取方式**：curl SEC `data.sec.gov/submissions` + 各 6-K 原文（sec-edgar-mcp `get_recent_filings` 交叉核對）
- **抓取結果**：✅ 成功

##### 🎯 2026 上半年（Q2）合併財報（未經查核）
- **來源連結**：[6-K 2026-07-31 Consolidated financial statements as of June 30, 2026](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000052/tmb-20260731x6k.htm)
- **發布時間**：2026-07-31（EDGAR 收件 16:09 UTC）
- **核心觀點**：
  > "REVENUES 75,878 / 73,004 … OPERATING PROFIT 20,133 / 19,281 … PROFIT FOR THE PERIOD 14,206 / 13,624 … Profit per share 107.50 / 105.72"（單位：十億盧比；2026 / 2025）
- **關鍵要點**：
  - 2026H1 營收 75.88 兆盧比（年增 3.9%，換算每股約 770 盧比）；營業利益 20.13 兆盧比（年增 4.4%，每股約 204 盧比）。
  - 歸屬母公司淨利 10.62 兆盧比（年增 1.4%，每股 107.50 盧比；每 ADS 10,750 盧比）。
  - 人事費用 7.72 兆盧比，較去年同期 8.08 兆下降 4.4%；財務成本 2.08 兆盧比，較去年 2.65 兆下降 21%。
  - 營運/維護/電信服務費用 21.47 兆盧比，年增 8.7%，成長快於營收。
  - 完整財報已轉存 `TLK_Quarter_2026Q2.md`。

##### 🎯 批發光纖連網業務第二階段分拆（Spin-off Phase 2）至 PT Telkom Infrastruktur Indonesia（TIF）
- **來源連結**：[6-K 2026-08-07 Spin-off plan](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000058/tmb-20260807x6k.htm)、[6-K 2026-09-08 EGM Notice](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000060/tmb-20260908x6k.htm)、[6-K 2026-09-30 Deed of Spin-Off](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000066/tmb-20260930x6k.htm)
- **發布時間**：2026-08-07 / 2026-09-08 / 2026-09-30
- **核心觀點**：
  > "Phase-2 Spin-Off constitutes a further stage to consolidate a portion of the Wholesale Fiber Connectivity business, including related business, assets, liabilities, and business activities, into TIF in order to establish a more focused operating model …"
- **關鍵要點**：
  - 延續 2025-12-12 臨時股東會通過的 Phase 1；公司稱這符合全球電信業把基礎設施獨立成實體的趨勢，以利效率、透明度與資產價值釋放。
  - 2026-09-30 已簽署分拆契據，TIF 增資預計 2026-10-01 生效；Telkom 持股 TIF 由 99.9999997% 升至 99.9999999%，不影響現有股東持股。

##### 🎯 2026-09-30 臨時股東會（EGMS）：分拆高票通過，但換將案有三成三反對
- **來源連結**：[6-K 2026-10-02 Summary of Minutes of EGMS](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000068/tmb-20261002x6k.htm)、[6-K 2026-09-30 Changes in Management](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000064/tmb-20260930x6k.htm)
- **發布時間**：2026-10-02 / 2026-09-30
- **核心觀點**：
  > "Disagree 28,998,601,148 shares or 33.3632562% … Agree 55,639,383,078 shares or 64.0138117%"（第二議案：經營層異動）
- **關鍵要點**：
  - 出席股數 86,917,778,519 股，佔有表決權股數 98,580,940,800 股的 88.17%。
  - 第一議案（分拆 Phase 2）：同意 99.19%、反對 0.32%、棄權 0.49%。
  - 第二議案（經營層異動）：反對高達 33.36%（約 290 億股），以 66.64% 通過。由於政府（Dwiwarna A 股 + 國家持股）約佔過半，反對票規模接近整個公眾流通股，顯示外部法人對換將有明顯異議（此為依票數推論，公告本身未說明反對者身分）。
  - 總裁 Dian Siswarini 與 IT 數位董事 Faizal Rochmad Djoemadi 去職；原網路董事 Nanang Hendarno 升任總裁（President Director），Budi Satria Dharma Purba 改任網路董事，新增 Radita Ali Putra（批發與國際）、Kharim I. G. Siregar（IT 數位）。
  - 董事會改組依據新的國營企業管理規章 GR 38/2026。

##### 🎯 反對分拆股東之法定股份收買請求權（Share Buyback）
- **來源連結**：[6-K 2026-10-02 Information Disclosure on the Share Buyback](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000072/tmb-20261002x6k.htm)
- **發布時間**：2026-10-02
- **核心觀點**：
  > "The Company will purchase the shares of eligible Shareholders at a price based on the closing price on the date of the Extraordinary General Meeting of Shareholders on 30 September 2026, being Rp2,290,-."
- **關鍵要點**：
  - 只有出席並在第一議案投反對票的股東（最多約 2.78 億股）可申請，申請期至 2026-10-05；以 2,290 盧比收購，上限約 6,362 億盧比（每股約 6.5 盧比），金額不大。（2026-10-20 補註：實際收買 15,956,199 股、金額 365.4 億盧比，付款已於 10/20 完成；來源 Kontan）
  - 公告揭露 2026-09-30 當日 TLKM 收盤 2,290 盧比。

##### 🎯 收購 Telkomsigma 持有之 Telkom Data Ekosistem（TDE）19.19% 股權
- **來源連結**：[6-K 2026-09-18](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000062/tmb-20260918x6k.htm)
- **發布時間**：2026-09-18（交易日 2026-09-17）
- **核心觀點**：
  > "in order to support Telkom's Unlock DC Co through the Strategic Partnership and Telkom Group's streamlining program."
- **關鍵要點**：
  - Telkom 由子公司 Telkomsigma 買下 TDE 19.19% 股權，持股升至 100%；屬集團內交易，公司稱對財務無重大影響。
  - 目的是為資料中心子公司（DC Co）引進策略夥伴鋪路（「Unlock DC Co」）。

##### 🎯 內部稽核主管更迭
- **來源連結**：[6-K 2026-08-07](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000054/tmb-20260807x6k.htm)、[6-K 2026-10-02](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000070/tmb-20261002x6k.htm)
- **發布時間**：2026-08-07 / 2026-10-02
- **關鍵要點**：
  - 8/7 代理稽核主管由 Afdol Muftiasa 換成 Umar Syahid；10/2 正式任命 Deni Ratno Tama。稽核主管兩個月內換了兩次，屬公司治理觀察點。

---

#### [Yahoo Finance 新聞頁]

- **抓取時間**：2026-10-19
- **抓取方式**：WebFetch `finance.yahoo.com/quote/TLK/news/`
- **抓取結果**：⭕ 無新內容
- 頁面僅 2 則標記 TLK 的文章：MT Newswires「Asian Equities Traded in the US as American Depositary Receipts Rise」（約 4 個月前，亞洲 ADR 綜合盤勢）、Yahoo Finance「10-year Treasury yield hits highest level since 2002 as stocks retreat: AlphaCheck」（約 12 天前，主題為美債殖利率）。兩則皆非以 Telkom 為主題，不列入重點。

---

#### [MSCI 官方公告：印尼可能由新興市場降為獨立市場]

- **抓取時間**：2026-10-19
- **抓取方式**：curl MSCI 新聞稿 PDF（`ir.msci.com` 網頁版回 Akamai Access Denied，改抓 `msci.com` PDF 成功）
- **抓取結果**：✅ 成功

##### 🎯 MSCI 啟動諮詢：擬將 MSCI Indonesia 指數由 Emerging Market 改列 Standalone Market
- **來源連結**：[MSCI Launches a Consultation on a Proposal to Reclassify Indonesia from Emerging Market to Standalone Market Status](https://www.msci.com/downloads/documents/press-releases/media-room/Indonesia_PR_Oct_26.pdf)
- **發布時間**：2026-10-15（紐約）
- **核心觀點**：
  > "Despite the announced reforms, significant concerns remain around market dysfunction, including continued suspected coordinated trading behavior and lack of evidence of meaningful enforcement. Accordingly, MSCI considers Indonesia's continued classification as an Emerging Market no longer appropriate …"
  > "MSCI expects to proceed with the proposed reclassification unless the consultation identifies clear evidence of material improvements in market governance and functioning …"
- **關鍵要點**：
  - 理由：持股結構不透明、疑似聯合炒作（coordinated trading）、執法不足；印尼雖已推出 1% 以上股東揭露、HSC（高持股集中）申報、15% 最低自由流通量路線圖，但投資人認為落實不足。
  - 時程：意見收集至 2027-04-30，2027-06-30 前公布決定；預設立場是「除非看到明確改善，否則就降級」。MSCI 認為降為 Frontier 都不足以反映問題深度。
  - 現行對印尼成分股的凍結（不調升 FIF/NOS、不新增 IMI 成分、不向上遷移）持續。
  - **對 TLK 的意義**：Telkom 是 MSCI Indonesia 權重最大的個股之一（股權分散、外資持股高），若降級，追蹤 MSCI EM 的被動資金可能被迫賣出；這是 10 月中股價崩跌的直接主因，與公司基本面無直接關係。

---

#### [CNBC Indonesia / Katadata / JournalArta（印尼財經媒體）]

- **抓取時間**：2026-10-19
- **抓取方式**：WebSearch 找網址 → curl 單篇（JSON-LD `datePublished`）
- **抓取結果**：✅ 成功

##### 🎯 10/16 IHSG 單日重挫 11.57%，TLKM 跌近跌停；10/19 新 ARB 7% 首日再度跌停
- **來源連結**：[Batas Auto Reject Turun, 351 Saham ARB Hari Ini（CNBC Indonesia）](https://www.cnbcindonesia.com/market/20261019174233-17-777615/batas-auto-reject-turun-351-saham-arb-hari-ini)
- **發布時間**：2026-10-19 18:01（WIB）
- **核心觀點**：
  > "PT Telkom Indonesia (Persero) Tbk (TLKM) melemah 6,84% ke Rp1.770 … Langkah ini diambil setelah Indeks Harga Saham Gabungan (IHSG) anjlok 11,57% pada Jumat (16/10/2026). Kejatuhan itu terjadi bersamaan dengan pengumuman MSCI yang membuka kemungkinan Indonesia dipindahkan ke klasifikasi standalone market."
- **關鍵要點**：
  - 10/19 共 351 檔股票（約 36%）鎖在跌停（ARB），TLKM 跌 6.84% 至 1,770 盧比，為市值前幾大的跌停股之一。
  - 印尼證交所（BEI）經 OJK 支持，依 Kep-00157/BEI/10-2026 把跌停限制由 15% 縮為 7%，實施期間 2026-10-19 ~ 12-31。
  - IHSG 10/19 收 4,996.61（−3.64%）。BEI 總裁 Jeffrey Hendrik 稱新規「有效緩和第一盤的恐慌」。

##### 🎯 LQ45 權值股集體觸及新 ARB
- **來源連結**：[Saham LQ45 BBCA, TLKM hingga UNVR Sentuh ARB setelah BEI Ubah Batas Jadi 7%（Katadata）](https://katadata.co.id/finansial/bursa/6ad5be4792a34/saham-lq45-bbca-tlkm-hingga-unvr-sentuh-arb-setelah-bei-ubah-batas-jadi-7)
- **發布時間**：2026-10-19 11:39（WIB）
- **關鍵要點**：
  - BBCA、BBRI、TLKM、UNVR 等 LQ45 成分股同步跌停；BEI 開發董事 Iding Pardi 表示調整是為了「讓投資人有時間消化資訊」。
  - 顯示這波是全市場系統性賣壓，不是 TLKM 個別利空。

##### 🎯 10/15 外資賣超榜首為 TLKM
- **來源連結**：[IHSG Sesi I Net Sell Rp 182,9 Miliar, Investor Asing Jual Saham TLKM, GOTO, ADRO（JournalArta）](https://journalarta.com/news/2026/10/15/ihsg-sesi-i-net-sell-rp-1829-miliar-investor-asing-jual-saham-tlkm-goto-adro/)
- **發布時間**：2026-10-15 16:36（WIB）
- **關鍵要點**：
  - MSCI 公告前一天（雅加達時間 10/15 上午），外資已在第一盤賣超 TLKM 349.3 億盧比，居全市場之首；IHSG 年初至今跌 32.75%。
  - 文章自承資料不足以說明個股被賣的原因。

##### 🎯 臨時股東會換將：Nanang Hendarno 接任總裁
- **來源連結**：[Rombak Direksi, Telkom (TLKM) Angkat Nanang Hendarno jadi Direktur Utama（Katadata）](https://katadata.co.id/finansial/bursa/6abce56180422/rombak-direksi-telkom-tlkm-angkat-nanang-hendarno-jadi-direktur-utama)
- **發布時間**：2026-09-30 17:33（WIB）
- **關鍵要點**：
  - Nanang Hendarno：ITS 電機學士、台夫特理工（TU Delft）太空系統工程碩士；2022–2025 任鐵塔公司 PT Infrastruktur Telekomunikasi Indonesia（Telkom Infra）CEO，2016–2022 任 Telin 技術長。背景偏網路/基礎設施。
  - 與 SEC 6-K 公告的董事名單一致。

---

#### [Selular.ID（印尼電信產業媒體）]

- **抓取時間**：2026-10-19
- **抓取方式**：curl 單篇（SSR，JSON-LD `datePublished`）
- **抓取結果**：✅ 成功

##### 🎯 前總裁任期僅 16 個月，換將前兩週股價跌約 15%
- **來源連結**：[Saham TLKM Anjlok di Era Dian Siswarini, Jadi Alasan Dicopot?](https://selular.id/2026/10/saham-tlkm-anjlok-di-era-dian-siswarini-jadi-alasan-dicopot/)
- **發布時間**：2026-10-01 17:00（WIB）
- **核心觀點**：
  > "Artinya, hanya dalam sekitar dua pekan terakhir masa kepemimpinan Dian, saham TLKM kehilangan sekitar 15% nilainya."
- **關鍵要點**：
  - TLKM 9/14 2,690 → 9/18 2,560 → 9/22 2,470 → 9/29 2,370 → 9/30 2,290 盧比；52 週區間 2,270 ~ 3,990。
  - 作者也提醒「斷言 Dian 因股價下跌被撤換還太早」。

##### 🎯 主權基金 Danantara 要求新總裁加速「瘦身」（streamlining）
- **來源連結**：[Danantara Beri Target Dirut Baru Telkom, Perampingan Anak Usaha Dikebut](https://selular.id/2026/10/danantara-beri-target-dirut-baru-telkom-perampingan-anak-usaha-dikebut/)
- **發布時間**：2026-10-01 18:00（WIB）
- **核心觀點**：
  > "Pertama yang paling penting sesuai dengan instruksi dan arahan dari Danantara yaitu kita harus mempercepat streamlining ini."（Nanang Hendarno，2026-09-30）
- **關鍵要點**：
  - 新經營層延續「TLKM 30」策略四主軸：營運與服務卓越、瘦身（Streamlining）、價值釋放（Unlock Value）、營運模式系統。
  - 子公司整併目標在 2026 年底前開始完成、延續至 2027 年初。

##### 🎯 InfraNexia（TIF）接收約 85.7 兆盧比光纖資產
- **來源連結**：[Aset Rp85,7 Triliun Dipindah, InfraNexia Jadi Raksasa Fiber Telkom](https://selular.id/2026/10/aset-rp857-triliun-dipindah-infranexia-jadi-raksasa-fiber-telkom/)
- **發布時間**：2026-10-05 06:00（WIB）
- **關鍵要點**：
  - 標題稱移轉資產約 85.7 兆盧比（換算每股約 869 盧比；集團內移轉，非現金流入）。依 DCD 報導，Phase 2 本身約 49.9 兆盧比（28 億美元），兩階段合計約 48 億美元，故 85.7 兆應為兩階段累計值；InfraNexia 管理約 11.2 萬公里光纖，含 2.6 萬公里國內海纜，Telkom 原網路基礎設施資產 90% 以上已移入。
  - 市場解讀：先把光纖資產獨立，未來可引進策略投資人或做資產變現（「unlock value」），但目前仍 100% 持有，尚無引資時程。

---

#### [Investortrust / Katadata（Q2 財報解讀與信評）]

- **抓取時間**：2026-10-19
- **抓取方式**：WebSearch 找網址 → curl 單篇（JSON-LD `datePublished`）
- **抓取結果**：✅ 成功

##### 🎯 Q2 單季淨利年增 28%，券商維持買進
- **來源連結**：[Dialing In: How Indonesia's Telkom Engineered a Second-Quarter Comeback（Investortrust）](https://investortrust.id/business/111695/dialing-in-how-indonesias-telkom-engineered-a-second-quarter-comeback)
- **發布時間**：2026-08-04 10:43（GMT+7）
- **核心觀點**：
  > "Analysts at BRI Danareksa Sekuritas reiterated a Buy rating on TLKM shares with a target price of Rp 3,750 … citing disciplined operational expenditure and robust mobile data consumption."
  > "Stronger free cash flow gives Telkom greater latitude either to deleverage its debt profile or to sweeten dividend payouts for shareholders in upcoming periods."（Stockbit Sekuritas）
- **關鍵要點**：
  - Q2 單季營收 38.7 兆盧比（季增 4%，換算每股約 393 盧比）；單季淨利 6.3 兆盧比（年增 28%、季增 45%，每股約 64 盧比），為 2023Q3 以來最佳單季。
  - Q2 EBITDA 利潤率 50.4%（季增 210bp）；上半年 EBITDA 約 37.4 兆盧比（每股約 379 盧比），利潤率 49.4%。
  - 上半年正常化淨利 11.3 兆盧比（年增 6%，每股約 115 盧比），排除出售 AdMedika、Telkomedika 等一次性稅後利益約 4,290 億盧比。
  - Telkomsel 上半年營收約 42.8 兆盧比（年增 5.6%）；Q2 ARPU 46,000 盧比（年增 11.7%），用戶穩定在 1.535 億。
  - **IndiHome 固網寬頻**：上半年營收約 12.8 兆盧比（年減 3.8%），用戶 950 萬（年減 5.4%），公司解釋是清除 12 個月以上零營收的休眠帳戶。
  - 上半年資本支出 9.4 兆盧比（每股約 95 盧比），資本支出占營收 12.5%，遠低於全年目標 17%~19%；分析師認為在等待頻譜拍賣結果。自由現金流年增 12.8%。
  - 全年營收成長指引維持 1%~3%。
  - BRI Danareksa 目標價 3,750 盧比（約為 10/19 收盤 1,770 的 2.1 倍）——此為 8 月初、MSCI 事件前的評估。

##### 🎯 Fitch 維持 BBB／展望負向，但上調獨立信用狀況至 'a'
- **來源連結**：[Fitch Ratings Sorot Telkom (TLKM), Ungkap Prospek Kinerja hingga Margin EBITDA（Katadata）](https://katadata.co.id/finansial/bursa/6ac3593a7b3e8/fitch-ratings-sorot-telkom-tlkm-ungkap-prospek-kinerja-hingga-margin-ebitda)
- **發布時間**：2026-10-05 15:07（WIB）
- **核心觀點**：
  > "Fitch menaikkan Standalone Credit Profile (SCP) Telkom menjadi 'a' dari sebelumnya 'a-' … didukung oleh rasio EBITDA net leverage yang sangat rendah, yakni sekitar 0,4 kali"
- **關鍵要點**：
  - Telkom 長期發行人評等維持 BBB（外幣與本幣），展望負向，與印尼主權評等（2026 年 3 月展望調降為負向）連動。
  - 獨立信用狀況（SCP）由 'a-' 上調至 'a'，淨槓桿約 0.4 倍 EBITDA，Fitch 認為足以支撐 5G 投資。
  - 政府持股 52% 並握有 Dwiwarna A 股否決權（任免董監、增資、修章）。2025 年 B2C 佔營收 72%；行動市占約 48%、固網寬頻約 67%。
  - **解讀**：公司本身信用比國家好，但評等被主權天花板壓住——國家風險是 TLK 的主要折價來源。⚠️ 未取得 Fitch 原始新聞稿，僅此一則媒體轉述。

---

#### [w.media（資料中心產業媒體）]

- **抓取時間**：2026-10-19
- **抓取方式**：WebFetch（curl 只拿到頁框）
- **抓取結果**：✅ 成功

##### 🎯 Telkomsel 擬出售資料中心 NeutraDC 多數股權，進入有約束力報價評估
- **來源連結**：[Telkomsel mulls stake sale of NeutraDC](https://w.media/telkomsel-mulls-stake-sale-of-neutradc/)
- **發布時間**：2026-09-11 15:20（GMT+8），作者 Jan Yong
- **核心觀點**：
  > "We will evaluate the use of the transaction proceeds holistically"（Budi Satria Dharma Purba，時任批發與國際服務董事；文中提及用途包括投資、強化資產負債表與股東回饋）
- **關鍵要點**：
  - 策略夥伴遴選已進入 binding offer 評估階段，目標 2026 年底完成；分析師估出售約 70% 股權。
  - 2 月 Bloomberg 報導目標售價 10 億~15 億美元（約每 ADS 1.0~1.5 美元，以 9.858 億 ADS 當量計）；此為第五度嘗試出售資料中心業務，過去多次未成。
  - 呼應 9/18 6-K 收回 TDE 100% 股權以「Unlock DC Co」。

---

#### [GuruFocus / MarketBeat（美股 ADR 端）]

- **抓取時間**：2026-10-19
- **抓取方式**：curl 單篇（JSON-LD `datePublished`）
- **抓取結果**：✅ 成功（皆為自動化/模板化快訊）

##### 🎯 ADR 10/16 單日跌 13.7%，10/19 再跳空開低
- **來源連結**：[TLK Stock Down 13.7% -- Now Undervalued? GF Score: 72/100（GuruFocus）](https://www.gurufocus.com/news/9128468/pt-telkom-indonesia-persero-tbk-tlk-stock-down-137-now-undervalued-gf-score-72100)、[TLK Shares Gap Down - What's Next?（MarketBeat）](https://www.marketbeat.com/instant-alerts/price-pt-telekomunikasi-indonesia-tbk-nyse-tlk-shares-gap-down-whats-next-2026-10-19/)
- **發布時間**：2026-10-16 22:31 UTC / 2026-10-19 15:00 UTC
- **核心觀點**：
  > "TLK's current price is $11.03, which is 35.9% below the GF Value™ estimate of $17.20."
- **關鍵要點**：
  - GuruFocus：10/16 收 11.03 美元，年初至今 −43.2%、近一年 −33.8%；52 週區間 10.60 ~ 23.52 美元；TTM 本益比 10.6 倍（5 年中位數 16.4 倍）、預估本益比 9.0 倍。
  - MarketBeat：10/19 開 10.20 美元；評級異動為 Weiss 由 D+ 降為 D（7/31）、Wall Street Zen 由 Buy 降 Hold、Zacks 由 Strong Sell 升 Hold（10/8），共識「Reduce」。Lazard 加碼約 480 萬 ADS。
  - yfinance 日線核對：10/15 收 12.78 美元 → 10/16 收 11.03（−13.7%，量 765 萬股，約為平日 7 倍）→ 10/19 收 10.59。9/14 收 15.26，一個月內累跌約 31%。
  - 兩站皆為模板化自動文章，評分與「低估」結論屬量化模型輸出，不代表分析師研究。

---

#### [Seeking Alpha]

- **抓取時間**：2026-10-19
- **抓取方式**：WebSearch（`allowed_domains: seekingalpha.com`）找文章 → Apify `apify/rag-web-browser` 取標題/日期/摘要（WebFetch 403；Firecrawl 額度用盡；Bright Data 需重新授權）
- **抓取結果**：⚠️ 僅標題、日期與摘要（正文付費牆）

##### 🎯 The Value Pendulum：分拆後維持「買進」，預期 Q3 優於共識
- **來源連結**：[Telekomunikasi Indonesia: A 'Buy' After Infrastructure Unit Spinoff And Q3 Preview](https://seekingalpha.com/article/4954723-telekomunikasi-indonesia-a-buy-after-infrastructure-unit-spinoff-and-q3-preview)
- **發布時間**：2026-10-16 07:27 ET（7 則留言）
- **核心觀點**：
  > "The spin-off of TLK's wholesale fiber business into a separate infrastructure-focused entity unlocks value, enhances margins, and preserves cash flows for shareholder returns."
  > "A Q3 beat, driven by price increases and cost controls, could prompt a re-rating from the current 3.5x EV/EBITDA toward peer levels"（SA Quick Insights 摘要）
- **關鍵要點**：
  - 多方論點：TIF 可爭取第三方客戶、未來以較高 EBITDA 倍數部分出售；漲價與產品簡化帶動利潤率；Q3 可能優於預期。
  - 作者自列風險：基礎設施子公司對外成長不如預期、漲價或成本控制執行不佳、**印尼總體情緒轉差引發資金外流**——文章發布同日即發生 MSCI 引發的崩跌，此風險已實現。
  - 作者聲明未持有部位。
- **其他較舊文章（三個月外，僅列標題供參考）**：〈Turning Bullish On Positive Developments (Upgrade)〉（2026 年 7 月，未能取得確切日期）、〈A Mixed View〉（降評，2026 年 5 月前後）。

---

#### [Reddit]

- **抓取時間**：2026-10-19
- **抓取方式**：Apify `trudax/reddit-scraper-lite`（第 1 次：全站 "Telkom Indonesia"、"TLKM"；第 2 次：r/finansial "TLKM"、"Telkom"，觸及 0.1 美元上限中止）
- **抓取結果**：⭕ 無個股新內容（僅印尼大盤崩跌討論）
- **市場層級討論（非 TLK 專屬）**：
  - [BREAKING: Indonesia's stock market crashes to its lowest level since 2020.（r/ZoomexGlobalExchange）](https://www.reddit.com/r/ZoomexGlobalExchange/comments/1x9qsx7/breaking_indonesias_stock_market_crashes_to_its/)｜2026-10-19 07:56 UTC｜原文："Over Rp1,621 trillion ($90B) wiped out in 2 trading sessions as MSCI warns it could remove Indonesia from its indexes"。留言分歧：「opportunity or trap?」／「Opportunity」。⚠️ 該版為加密交易所導流版，且 MSCI 實際是「降為獨立市場」而非「移出指數」，標題用語不精確。
  - [Otw jadi kek Zimbabwe kah?（r/WkwkwkLand）](https://www.reddit.com/r/WkwkwkLand/comments/1x81ztd/otw_jadi_kek_zimbabwe_kah/)｜2026-10-17 05:24 UTC｜印尼網友自嘲盧比會變成辛巴威幣（該版標明多為諷刺/迷因）；有留言擔心「美股 AI 泡沫若破裂會像 2008 年，IHSG 再被撞一次」。屬情緒指標，非基本面資訊。
  - r/finansial 搜尋結果為 2025 年與 Telkom 大學相關的無關貼文，已排除。

---

#### [Stockbit（印尼最大投資社群）]

- **抓取時間**：2026-10-19
- **抓取方式**：Exa `web_search_exa`（索引含單篇貼文全文與發布時間）
- **抓取結果**：⚠️ 為搜尋索引內容，非原始頁面逐字擷取（Stockbit 頁面需 JS 載入）

##### 🎯 Stockbit Snips 研究部：Q2 優於預期（8/3）
- **來源連結**：[📡 TLKM: Pemulihan pada 2Q26, Kinerja 1H26 Lampaui Ekspektasi](https://snips.stockbit.com/snips-terbaru/-tlkm-pemulihan-pada-2q26-kinerja-1h26-lampaui-ekspektasi)
- **發布時間**：2026-08-03（Stockbit Investment Research）
- **核心觀點**：
  > "laba bersih ternormalisasi selama 1H26 mencapai Rp11,3 T (+6% YoY), melampaui ekspektasi karena setara 55% estimasi 2026F konsensus"
- **關鍵要點**：
  - Q1 淨利年減 22%，Q2 強力反彈；上半年營收 +4% 已超過全年指引 1%~3%，但管理層未上修，理由是下半年出售子公司會壓抑營收、待售業務也會暫停新專案。
  - 上半年資本支出占營收 14.2%（與 Investortrust 引述的 12.5% 不同，口徑可能不同），自由現金流 +12.8%。
  - IndiHome ARPU 21.1 萬盧比（年減 2.7%、季增 3.4%）。
  - 管理層稱：光纖 InfraNexia 第二階段在 2H26 完成並找策略夥伴，重要里程碑於 3Q26 末宣布、4Q26 開始執行；資料中心目標 2026 年底前完成價值釋放。
  - 8/3 當天 TLKM 收漲 4.2%。

##### 🎯 散戶輿情（10/16 ~ 10/19，MSCI 衝擊期間）
- **來源連結**：[ReiganDesu](https://stockbit.com/post/36797063)、[Cuan100M](https://stockbit.com/post/36796833)、[AwanDeru](https://stockbit.com/post/36797270)、[Dandyrachmadika](https://stockbit.com/post/36751819)、[skydrugz27](https://stockbit.com/post/36738215)、[TLKM 個股串流](https://stockbit.com/symbol/TLKM)
- **發布時間**：2026-10-16 22:20 ~ 2026-10-19 17:30（WIB，依索引時間）
- **核心觀點**：
  > "$TLKM semoga ntar sore meeting sama MSCI nya dapet hasil bagus. Fundamental masih sangat oke, big player juga udah pada masuk tadi, walupun tetep kalah sama buangan asing."（ReiganDesu，10/19）
  > "$TLKM $BRMS $BRPT yg masih di MSCI kayaknya di hindari dl untuk sementara"（Cuan100M，10/19）
  > "Hati2 meskipun banyak yang bilang mau serok2, tapi selama permasalahan belum dibereskan ya endingnya sama kaya crash yang lalu"（Dandyrachmadika，10/18）
- **關鍵要點**：
  - **偏多**：基本面仍佳、大戶已進場但抵不過外資拋售（ReiganDesu）；年初至今已修正約 49%、「Telkom 不會倒」，打算小量試單（AwanDeru）；有人認為 OJK/BEI 的救市措施是反轉催化劑（iqbal2606，屬喊單語氣）。
  - **偏空**：仍在 MSCI 指數內的權值股應暫時避開，因為被動資金會繼續賣（Cuan100M）；回顧上半年 MSCI 事件，即使大宗商品高檔股市仍走空，只要問題未解決，反彈也只是區間震盪（Dandyrachmadika）；有人抱怨主權基金 Danantara「只會喊話」、BEI 盤後才公告。
  - **事件細節**（skydrugz27 整理，⚠️ 社群整理非官方）：10/13 Danantara 在曼谷辦「Reform, Transparency and Capital」論壇，MSCI、Moody's、S&P、Fitch 與財政部、OJK、央行、BEI 皆出席；BEI 開發董事 Iding Pardi 稱 MSCI 當時「完全沒暗示」會改分類；經濟統籌部長 Airlangga 也質疑 MSCI 為何未在會中提出。10/16 全市場 812 檔下跌、僅 11 檔上漲。
  - YansenDoang（10/19）稱 BEI/OJK 與 MSCI 當天下午有線上會議、結果將於傍晚公布——⚠️ 未查到官方結果，待後續確認。
  - 排除：純謾罵（fafafifu）、研討會廣告（mywahyudi）、Stockbit 標示「Potential Junk」的喊單文。

---

#### [X（Twitter）]

- **抓取時間**：2026-10-19
- **抓取方式**：WebSearch（`allowed_domains: x.com, twitter.com`）取索引；時間由 status ID 換算（UTC）。Firecrawl 額度用盡未使用。
- **抓取結果**：⚠️ 為搜尋索引摘要，非原始頁面逐字引述

##### 🎯 媒體帳號與財經帳號貼文
- [Radio Elshinta](https://x.com/RadioElshinta/status/2110934188149133463)｜2026-10-16 03:21 UTC｜IHSG 開盤重挫 8.01% 至 5,393.92，觸發暫停交易（trading halt），起因為 MSCI 公告。
- [The New York Times](https://x.com/nytimes/status/2111028319177064889)｜2026-10-16 09:35 UTC｜"Indonesian stocks suffered their biggest plunge since 1998, deepening investor fears about Southeast Asia's largest economy."
- [Merapi Uncover](https://x.com/merapi_uncover/status/2112028054461780159)｜2026-10-19 03:48 UTC｜IHSG 10/19 盤中再跌逾 5% 至 4,911，為 2020 年疫情以來低點。
- [NusaBali.com](https://x.com/nusabalicom/status/2110181865571463634)｜2026-10-14 01:32 UTC｜Telkom 截至 2026 上半年已完成 50 個子公司實體中 24 個的整併，其餘 26 個力拚年底前完成。
- [Investor Daily](https://x.com/InvestorID/status/2086396209338765775)｜2026-08-09 10:16 UTC｜「Dividen Telkom Terendus, Potensi Cuan Saham 35%」——媒體標題式推文，正文未取得。
- 背景：[Mirae Asset Sekuritas](https://x.com/MiraeAssetID/status/2054382374519984536) 指出 2026 年 5 月 MSCI 季檢剔除 AMMN、BREN、TPIA、DSSA、CUAN、AMRT 六檔印尼股、無新增；TLKM 未被剔除（三個月外，僅作脈絡）。

---

#### [Simply Wall St]

- **抓取時間**：2026-10-19
- **抓取方式**：Exa `web_search_exa` 索引全文
- **抓取結果**：⚠️ 為搜尋索引內容

##### 🎯 〈3 Indonesian Telecom Stocks After The MSCI Selloff〉
- **來源連結**：[3 Indonesian Telecom Stocks After The MSCI Selloff](https://simplywall.st/stocks/id/telecom/idx-tlkm/perusahaan-perseroan-persero-pt-telekomunikasi-indonesia-shares/news/3-indonesian-telecom-stocks-after-the-msci-selloff)
- **發布時間**：2026-10-19 09:33 UTC
- **核心觀點**：
  > "A large, cash generative telecom group has seen its share price affected by MSCI related selling and short term sentiment rather than a sudden change in its core digital connectivity role."
- **關鍵要點**：
  - 列 TLKM、EXCL（XLSMART）、ISAT 為 MSCI 衝擊下的「價值/逆勢」標的；TLKM 市值 187.3 兆盧比。
  - 屬平台量化篩選 + 社群 narrative 摘錄，非獨立研究。

---

#### [Rikopedia Research]

- **抓取時間**：2026-10-19
- **抓取方式**：curl 單篇（JSON-LD `datePublished`）
- **抓取結果**：✅ 成功（⚠️ 可信度待查）

##### 🎯 〈TLKM Terkoreksi ke 1.900: Peluang Upside 90% Terbuka〉
- **來源連結**：[TLKM Terkoreksi ke 1.900: Peluang Upside 90% Terbuka](https://www.rikopedia.com/2026/10/tlkm-terkoreksi-ke-1900-peluang-upside.html)
- **發布時間**：2026-10-19 15:05（WIB）
- **核心觀點**：
  > "Change Global justru menambah kepemilikan saham, menilai kabar buruk MSCI sudah sepenuhnya priced in."
- **關鍵要點**：
  - 稱基金 Change Global Investment（創辦人 Thea Jamison）逢低加碼 TLKM，估上檔空間約 90%；理由為營業利益率與 ROIC 優於區域同業、資料中心與光纖成長。
  - ⚠️ 本文為部落格式整理、未附原始訪談連結，基金觀點未經其他來源核實；「上檔 90%」屬單一基金觀點，引用時請保守看待。

---

#### [Reuters / Bloomberg]

- **抓取時間**：2026-10-19
- **抓取方式**：Firecrawl → HTTP 402 額度用盡；WebSearch → `reuters.com` 被內建搜尋封鎖；改用 Exa `web_search_exa` 找轉載頁（TradingView、MarketScreener）
- **抓取結果**：⚠️ 僅標題（Reuters 正文未取得；Bloomberg 付費牆，僅經 Katadata 轉述）
- [Telkom Indonesia plans $2.8 billion second-phase fibres business spin-off（Reuters via MarketScreener）](https://www.marketscreener.com/news/telkom-indonesia-plans-2-8-billion-second-phase-fibres-business-spin-off-ce7f50d2dc8ff327)｜2026-08-07 06:42 EDT｜Phase 2 光纖分拆規模約 28 億美元（約每 ADS 2.84 美元，集團內移轉）。MarketScreener 頁面另顯示 23 位分析師平均評等為 BUY。
- [Telkom Indonesia Shareholders Approve Partial Wholesale Fiber Connectivity Spin-Off Plan（Reuters via TradingView）](https://www.tradingview.com/news/reuters.com,2026:newsml_FWN45O097:0-telkom-indonesia-shareholders-approve-partial-wholesale-fiber-connectivity-spin-off-plan/)｜2026-10-02 10:18 UTC｜股東會通過分拆（與 6-K 一致）。
- Bloomberg：2026 年 2 月報導 NeutraDC 多數股權出售目標估值 10 億~15 億美元（經 Katadata 9/7 轉述，見下）。

---

#### [The Jakarta Post / Katadata / DCD / DealStreetAsia（資料中心與重組進度）]

- **抓取時間**：2026-10-19
- **抓取方式**：Exa `web_search_exa` 索引全文
- **抓取結果**：⚠️ 為搜尋索引內容，非原始頁面逐字擷取

##### 🎯 公開說明會（Public Expose 2026，9/7）：NeutraDC 進入 binding offer 評估、可能出售多數股權
- **來源連結**：[Progres Telkom (TLKM) Jual Mayoritas Saham NeutraDC, Target Rampung Akhir 2026（Katadata）](https://katadata.co.id/finansial/bursa/6a9e796d86aba/progres-telkom-tlkm-jual-mayoritas-saham-neutradc-target-rampung-akhir-2026)、[Telkom ramps up data center expansion, seeks strategic partner（The Jakarta Post）](https://www.thejakartapost.com/business/2026/09/10/telkom-ramps-up-data-center-expansion-seeks-strategic-partner)
- **發布時間**：2026-09-07 15:44（WIB）／2026-09-10 11:48（WIB）
- **核心觀點**：
  > "Terkait nilai ataupun porsi kepemilikan yang beredar di pasar, angka tersebut merupakan kajian atau estimasi dari pihak eksternal dan … bukan merupakan angka resmi dari kami"（Budi Satria Dharma Purba）
- **關鍵要點**：
  - 公司不證實市場流傳的 10 億~15 億美元估值與 70% 出售比例。
  - NeutraDC（PT Telkom Data Ekosistem）2026 上半年營收 8,670 億盧比（年增 11%，換算每股約 8.8 盧比，占集團營收約 1.1%）；集團有效資料中心容量 49.9MW，Cikarang 15.5MW、使用率 96%。
  - 出售所得可能用於核心業務、強化資產負債表或股東回饋。

##### 🎯 NeutraDC 擴產目標 300MW（2030）
- **來源連結**：[Data centers emerge as next major growth driver for Indonesian listed companies（Indonesia Business Post）](https://indonesiabusinesspost.com/7217/markets-and-finance/data-centers-emerge-as-next-major-growth-driver-for-indonesian-listed-companies)
- **發布時間**：2026-08-26（GMT+7）
- **關鍵要點**：
  - 引 BRI Danareksa 報告：NeutraDC IT 容量 90.4MW（與 Jakarta Post 的 49.9MW「有效容量」口徑不同），目標 2030 年 300MW；Cikarang 第二園區規劃總容量 120MW；Batam 18MW、新加坡 17.4MW。
  - BRI Danareksa 將 TLKM、ISAT、DSSA、DCII 列為資料中心直接受惠股。

##### 🎯 InfraCo Phase 2 完成，兩階段合計約 48 億美元
- **來源連結**：[Telkom Indonesia finalizes spin-off of $4.8bn InfraCo（DCD）](https://www.datacenterdynamics.com/en/news/telkom-indonesia-finalizes-spin-off-of-48bn-infraco/)、[Fokus 'AI Ready', Telkom Spin-Off Bisnis Fiber Rp85,7 T ke InfraNexia（CNN Indonesia）](https://www.cnnindonesia.com/ekonomi/20261001094733-625-1410327/fokus-ai-ready-telkom-spin-off-bisnis-fiber-rp857-t-ke-infranexia)
- **發布時間**：2026-08-12（DCD）／2026-10-01 09:53（WIB，CNN Indonesia，作者標示「Telkom」＝公司新聞稿）
- **關鍵要點**：
  - Phase 1 於 2026 年 1 月完成（移轉 50% 光纖資產）；Phase 2 約 49.9 兆盧比（28 億美元）。⚠️ DCD 8/12 寫「已完成」，但股東會 9/30 才通過、契據 9/30 才簽，DCD 用語過早，以 6-K 為準。
  - InfraNexia 總裁 Lukman Hakim Abd. Rauf：主打 5G 回傳、批發網路、FTTx、被動基礎設施共享，定位「AI Ready Infrastructure」。

##### 🎯 下半年再出售 6 家子公司
- **來源連結**：[Indonesia's Telkom eyes six more divestments as restructuring gathers pace（DealStreetAsia）](https://www.dealstreetasia.com/stories/indonesia-telkom-restructuring-491278)
- **發布時間**：2026-08-05 14:52 UTC
- **關鍵要點**：
  - 呼應財報說明會：截至 6 月底已完成 2 項出售、2 項合併、8 項關閉；年底前目標再 6 項出售、2 項合併、4 項關閉（正文付費，僅取標題與摘要）。

---

#### [2026-10-22 ~ 10-23 補充（StockAnalysis 例行更新蒐集）]

##### 🎯 IDX 剔除 HSC 股票時程指向 11 月；Danantara 承接國營股
- **來源連結**：[IHSG Hari Ini Meroket ke 5.439!（Merahputih）](https://www.merahputih.com/post/read/ihsg-hari-ini-meroket-ke-5-439-aturan-saham-hsc-bei-dan-manuver-danantara-jadi-penyelamat)、[IHSG menguat di tengah pasar cermati perkembangan regulasi dan MSCI（Antara）](https://www.antaranews.com/berita/5803781/ihsg-menguat-di-tengah-pasar-cermati-perkembangan-regulasi-dan-msci)、[BEI Keluarkan Saham HSC dari IHSG, Bobot 18%（Katadata）](https://katadata.co.id/amp/finansial/bursa/6ad5f8c1dfe35/bei-keluarkan-saham-hsc-dari-perhitungan-ihsg-bobot-18-termasuk-dssa-dan-bren)
- **發布時間**：2026-10-22 ~ 10-23（WIB）
- **關鍵要點**：
  - JCI 10/23 +0.95% 至 5,439.26；Pilarmas 分析師稱 HSC 股票「11 月 2 日起」不計入 JCI（已由 IDX 公告 Peng-00201/BEI.POP/10-2026 證實，見下方 10-24 補充）。
  - HSC 約 80 檔、權重約 18%，含 DSSA、BREN；名單每三個月檢討，不是下市。
  - Danantara 執行長 Rosan 稱國營股估值已很便宜，備約 10 億美元至年底可進場；尚無買進 TLKM 的正式揭露。
  - BI 10/22：BI-Rate 維持 5.75%、存款便利利率升至 5.00%、11–12 月法定準備率 9%→7%（約 190 兆盧比）、DNDF 避險成本最多降 45%。

##### 🎯 Kontan：TLKM 三天反彈是否為多頭陷阱
- **來源連結**：[Diguyur Net Sell Triliunan Rupiah, Apakah Kenaikan Tiga Hari TLKM Cuma Bull Trap?（Kontan Insight）](https://insight.kontan.co.id/news/diguyur-net-sell-triliunan-rupiah-apakah-kenaikan-tiga-hari-tlkm-cuma-bull-trap)
- **發布時間**：2026-10-23 14:00（WIB）
- **關鍵要點**：
  - TLKM 10/22 收 2,200 盧比，較 10/19 的 1,770 盧比 +24.3%，但外資未回流；10/19 外資賣超 3,674.8 億盧比。正文付費，僅取前言。
  - TLKM 10/23 收 2,240 盧比（Yahoo Finance）；TLK ADR 10/23 收 12.13 美元。

##### 🎯 BNY Mellon 持股增至 6.52%；新加坡政府續賣 MTEL
- **來源連結**：[Singapore Government Sells MTEL Shares Again（IDN Financials）](https://www.idnfinancials.com/news/70748/singapore-government-sells-mtel-shares-again)
- **發布時間**：2026-10-24 01:00（WIB；持股異動資料日 10/22）
- **關鍵要點**：
  - ADR 存託銀行 BNY Mellon 增加 5,758 萬股 TLKM，持股 6.52%（推測為 10/19 ADR 溢價時的本地股轉 ADR 套利）。
  - 新加坡政府再出售 111 萬股 Mitratel（MTEL），規模很小。

---

#### [2026-10-24 補充（StockAnalysis 例行更新蒐集）]

##### 🎯 IDX 正式公告：HSC 股票 2026-11-02 起不計入 JCI
- **來源連結**：[BEI: Saham HSC Resmi Keluar dari IHSG Mulai 2 November（Bisnis.com）](https://market.bisnis.com/read/20261022/7/2014729/bei-saham-hsc-resmi-keluar-dari-ihsg-mulai-2-november)、[BEI Kecualikan Saham HSC dari IHSG Mulai 2 November 2026（Media Indonesia）](https://mediaindonesia.com/ekonomi/947430/bei-kecualikan-saham-hsc-dari-ihsg-mulai-2-november-2026)、[Efektif 2 November 2026（Metro TV News）](https://www.metrotvnews.com/read/NG9Cw2RD-efektif-2-november-2026-bei-kecualikan-saham-hsc-dari-perhitungan-ihsg)、[BEI Keluarkan Saham HSC dan Papan Akselerasi dari IHSG, Mampukan Meyakinkan MSCI?（Kontan）](https://investasi.kontan.co.id/news/bei-keluarkan-saham-hsc-dan-papan-akselerasi-dari-ihsg-mampukan-meyakinkan-msci)、[Kuasai 28,8% Kapitalisasi Pasar, BEI Keluarkan HSC dari IHSG（Kontan）](https://investasi.kontan.co.id/news/kuasai-288-kapitalisasi-pasar-bei-keluarkan-hsc-dari-ihsg)
- **發布時間**：2026-10-22（WIB；公告日期 2026-10-21）
- **關鍵要點**：
  - 法源：IDX 公告 No. Peng-00201/BEI.POP/10-2026〈JCI 評估標準調整〉，2026-11-02 生效。
  - 範圍：2026-10-13 名單上的 80 檔 HSC 股票，佔 JCI 權重約 18%（Kontan 稱約佔市值 28.8%）；Papan Akselerasi（加速板）股票一併排除；不是下市，照常交易。
  - JCI 定期檢討月份改為 1／4／7／10 月（原 3／6／9／12 月）；單一股票權重上限 9%（capped free float）不變。
  - Kontan 引述分析師：此舉「可能還不足以說服 MSCI」。MSCI 的 Standalone 諮詢仍在進行。
  - TLKM 不在 HSC 名單；剔除後非 HSC 大型股在 JCI 的相對權重上升。

##### 🎯 反對股東收買價格確認
- **來源連結**：[Telkom Rampungkan Buyback Saham, Serok Rp36,54 Miliar（CNBC Indonesia）](https://cnbcindonesia.com/market/20261023094855-17-778800/telkom-rampungkan-buyback-saham-serok-rp3654-miliar)、[TLKM Eksekusi Buyback 15,95 Juta Saham（Bloomberg Technoz）](https://www.bloombergtechnoz.com/detail-news/125494/tlkm-eksekusi-buyback-15-95-juta-saham-terkait-spin-off-fiber)
- **發布時間**：2026-10-23（WIB）
- **關鍵要點**：
  - 15,956,199 股 × 2,290 盧比 ＝ 365.4 億盧比，10/20 付款完成；與前述一致。

##### 🎯 NeutraDC、Danantara、3Q 財報：本輪查無新進度
- **關鍵要點**：
  - NeutraDC 最新公開資訊仍為 9/7 公開說明會（binding offer 評估，目標年底完成）。
  - Danantara 仍無買進 TLKM 的正式揭露（Katadata 10/20 標題為問句「Sinyal Danantara Masuk?」）。
  - 3Q2026 財報日期仍未見公司公告；歷年為 10 月底（3Q2024 為 2024-10-30）。

---

#### [2026-10-24 晚間補充（CollectsentimentAndReports 例行收集）]

- **抓取時間**：2026-10-24 20:00 UTC
- **抓取方式**：SEC EDGAR submissions JSON（curl）；`WebSearch`（印尼文關鍵字）＋ `curl` 單篇；Exa `web_search_exa`（Stockbit 索引）；`WebFetch` Yahoo Finance 新聞頁
- **抓取結果**：✅ 成功（SEC、periskop 全文）／⚠️ Stockbit 為 Exa 索引全文／⭕ Yahoo Finance 新聞頁無 TLK 新文章（仍為 MT Newswires ADR 盤勢稿與 17 天前的美債殖利率文）

##### 🎯 SEC 6-K（2026-10-22）：反對股東收買結果報告
- **來源連結**：[Form 6-K tmb-20261022x6k.htm（SEC EDGAR）](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000074/tmb-20261022x6k.htm)
- **發布時間**：2026-10-22（申報日）
- **關鍵要點**：
  - 為向 OJK 提交的〈依公司法第 62 條執行之股份買回結果報告〉，交割日 2026-10-20，內容與前述 CNBC Indonesia 報導（15,956,199 股 × 2,290 盧比）一致。
  - 截至 10-24，EDGAR 最新申報仍為此件；**尚無 3Q2026 財報 6-K**。

##### 🎯 Telkom 回覆 BEI 異常波動詢問：買回計畫至 2027-06-08，三個月內無其他公司行動
- **來源連結**：[Telkom (TLKM) Jelaskan ke BEI, Buyback Saham Berjalan sampai Juni 2027（periskop.id）](https://periskop.id/pasar-modal/20261024/telkom-tlkm-jelaskan-bei-buyback-saham)
- **發布時間**：2026-10-24 17:11 WIB（JSON-LD `datePublished` 2026-10-24T10:11Z；公司回覆於 10-22 揭露）
- **核心觀點**：
  > "Telkom menyatakan tidak memiliki rencana tindakan korporasi lain dalam tiga bulan mendatang, termasuk yang berdampak terhadap pencatatan saham Perseroan di Bursa."
- **關鍵要點**：
  - BEI 因股價波動（10/19 跌停後三天 +24%）要求說明；公司稱買回計畫已於 2026-05-01 揭露、2026-06-08 年度股東會通過，期間 2026-06-09 ~ 2027-06-08，執行視市況與財務狀況而定（WebSearch 摘要稱額度上限約 4 兆盧比，約每股 41 盧比，未在本文中核實）。
  - 除已揭露事項外，三個月內無其他公司行動計畫（含影響上市地位者）；正在進行子公司整併簡化。
  - 公司表示不知悉任何未揭露重大資訊，亦不知悉特定股東持股變動（與 BNY Mellon 10/22 增持 5,759 萬股屬存託銀行 ADR 轉換一致，並非特定大股東進場）。

##### 🎯 Stockbit 社群：短線反彈派 vs. MSCI 外資賣壓派、殖利率陷阱警告
- **來源連結**：[stockbit.com/symbol/TLKM 討論流](https://stockbit.com/symbol/TLKM)、[owennath 技術面貼文](https://stockbit.com/post/36915899)
- **發布時間**：2026-10-22 21:50 ~ 2026-10-24 16:14（WIB，Stockbit 顯示時間）
- ⚠️ 為 Exa 搜尋索引全文，非原始頁面逐字擷取；mhilmi2703 貼文被 Stockbit 標為「Potential Junk」，僅作情緒參考
- **關鍵要點**：
  - **多方（技術面）**：owennath（10/22）認為 TLKM 已確認短線多頭反轉、回補 2,170 缺口，量能放大且 YU 券商大量承接；但同日外資仍賣超約 3,320 億盧比。目標 2,220–2,230（MA20），突破後 2,300–2,350 甚至 2,440–2,450（MA50），支撐 2,000–2,050。
  - 另一用戶統計 10/23 TLKM 自圈選買點 2,160 漲至 2,250（+4.17%）；「Pegawai Negeri Saham」10/23 盤後名單把 TLKM 列為 Strong Buy 第 3 名（自營社群名單，非研究報告）。
  - **空方（資金面）**：（Potential Junk 標記）用戶估算至 2027 年 MSCI 決定前約 100 個交易日，若外資每天賣 1 兆盧比，累計約 100 兆盧比，相當於降為 Standalone 時的被動資金流出，質疑「誰來接」。
  - **股利品質警告**（10/24 15:14）：一則推廣影片貼文把 TLKM 列入 8%~15% 高殖利率股，但指出其配息率已 > 100%、部分動用保留盈餘，提醒「股利陷阱」。（該說法未在本文中核實，需對照 FY2025 年報股利政策）
  - 情緒面：散戶貼文多聚焦 10/16 崩跌、ARB 下限改 7%、10/21 Prabowo 演說「嗆 MSCI」造成的焦慮；ISAT（Indosat）AI／資料中心題材被拿來與 TLKM 比較。

##### 🎯 3Q2026 財報日期：第三方網站多指向 10/30
- **來源連結**：[Earnings Whispers TLK](https://beta.earningswhispers.com/go/w/TLK)、[AJ Bell TLK company info](https://www.ajbell.co.uk/market-research/sub/NYSE:TLK/company-info)、[TipRanks](https://www.tipranks.com/stocks/mx:tlkn/earnings)
- ⚠️ 為搜尋索引摘要，非原始頁面逐字引述
- **關鍵要點**：
  - Earnings Whispers、AJ Bell 標 2026-10-30（盤前）；TipRanks 以歷史推估 10-29（TBA）。公司尚未正式公告。

---

#### [2026-10-25 補充（StockAnalysis 例行更新蒐集）]

- **抓取時間**：2026-10-25（台北時間上午，週末休市）
- **抓取方式**：`WebSearch`（印尼文／英文關鍵字）；Yahoo Finance 歷史股價（TLK、TLKM.JK 確認 10/23 後無新報價）
- **抓取結果**：✅ 成功（搜尋摘要，非全文逐字擷取）

##### 🎯 FTSE Russell 10/7 維持印尼 Secondary Emerging、不列觀察名單
- **來源連結**：[Kontan](https://investasi.kontan.co.id/news/ftse-russell-pertahankan-status-indonesia-di-emerging-market-ini-alasannya)、[Bisnis.com](https://market.bisnis.com/read/20261007/7/2010623/ihsg-tak-bergeming-walau-ftse-russell-pertahankan-status-ri)、[Investortrust](https://investortrust.id/market/118752/ftse-keeps-indonesia-in-emerging-market-fold-as-watchdog-hails-global-vote-of-confidence)
- **發布時間**：2026-10-07
- **關鍵要點**：
  - 年度國家分類檢討（10/6 生效）維持印尼 Secondary Emerging，不列入升降級觀察名單；理由為持股揭露、投資人分類、最低自由流通股、市場監理等改革。
  - FTSE 將在 2026 年 12 月指數檢討前更新對印尼股票的處理方式。
  - 對 TLK 的意義：若 MSCI 降級，追蹤 FTSE 新興市場指數的資金（如 VWO）不必跟賣，可作為被動賣壓的緩衝（TLKM 在 FTSE 指數權重未取得，無法量化）。

##### 🎯 10/20 外資淨買超第一名為 TLKM（約 2,550 億盧比）
- **來源連結**：[Kontan 10/20](https://pusatdata.kontan.co.id/news/ihsg-melonjak-565-ke-5278-asing-justru-net-sell-rp-221-triliun-hari-ini-2010)、[Katadata 10/20](https://katadata.co.id/finansial/bursa/6ad716556afdf/ihsg-naik-4-51-saat-net-sell-tembus-rp-1-9-t-asing-borong-saham-tlkm-dan-goto)
- **發布時間**：2026-10-20
- **關鍵要點**：
  - JCI 收 5,278.89（+5.65%），外資全市場淨賣超約 2.21 兆盧比，但 TLKM 為外資淨買超第一（約 2,550 億盧比 ≒ 每股 2.59 盧比 ≒ 每 ADS 0.014 美元）；BBCA、BBRI、BMRI 為主要淨賣超。
  - 與 10/19 TLKM 外資淨賣超 3,674.8 億盧比合看，外資對 TLKM 為「進出反覆」，非單向撤出。

##### 🎯 Moody's：印尼 Baa2、展望負向（2026-02），7 月稱風險再偏負面
- **來源連結**：[Bank Indonesia 新聞稿](https://www.bi.go.id/en/publikasi/ruang-media/news-release/Pages/sp_282726.aspx)、[Bloomberg 2026-07-21](https://www.bloomberg.com/news/articles/2026-07-21/moody-s-flags-rising-risks-in-indonesia-on-policy-uncertainty)
- **關鍵要點**：
  - 2026-02 展望由穩定轉負向，主因政策可預測性下降、支出增加但收入未跟上、Danantara 相關或有負債；7 月表示風險「再偏負面一點」。本輪查無 10 月新動作。
  - TLK 的 Fitch BBB 評等受主權上限壓制，主權若降評，TLK 評等可能連動。

##### 🎯 其他
- **Prabowo 10/21 內閣會議**：稱 MSCI 試圖「恐嚇」印尼、印尼不會被嚇倒（[The Star](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/21/prabowo-vows-indonesia-will-not-be-frightened-by-msci-amid-proposed-market-downgrade)、[DealStreetAsia](https://www.dealstreetasia.com/stories/prabowo-msci-indonesia-498821/)）。
- **AI 資料中心**：網路董事 Budi Satria Dharma Purba 10/20 於 Bali Tech Week 表示將把資料中心建在電源附近，主打印尼電價較鄰國便宜（[Bisnis.com](https://teknologi.bisnis.com/read/20261020/84/2014206/permintaan-data-center-ai-melonjak-telkom-bidik-pembangunan-dekat-sumber-energi)）；未揭露金額。
- **Goldman Sachs**：印尼 underweight 為 2026-01-29 調降、6 月維持；本輪查無 10 月新動作。
- **NeutraDC、3Q 財報**：查無新進度；3Q2025 財報為 2025-10-31 見報、1Q2026 延至 2026-05-29 公布，3Q2026 第三方網站標 10/30。

---

#### [本期小結（2026-07-19 ~ 2026-10-19）]

- **利多**：Q2 獲利強勁反彈（單季淨利 +28% YoY）、Telkomsel ARPU 連續上升、資本支出偏低使自由現金流 +12.8%；光纖分拆 Phase 2 完成、資料中心出售進入 binding offer；Fitch 上調獨立信用狀況至 'a'；淨槓桿僅約 0.4 倍。
- **利空**：MSCI 擬將印尼降為獨立市場（2027-06 前決定），被動資金賣壓是 10 月崩跌主因；ADR 自 9/14 15.26 美元跌至 10/19 10.59 美元（約 −31%）；換將案三成三反對、稽核主管兩個月兩度更換，治理與政策干預疑慮升高；IndiHome 固網持續衰退；評等受主權天花板壓制（BBB／負向）。
- **待觀察**：Q3 財報（Earnings Whispers／AJ Bell 標 2026-10-30 盤前，尚待公司公告確認）、NeutraDC 買家與價格、MSCI 11 月季檢與諮詢進度、BEI 新 ARB 7% 規定（至 12/31）。

---

#### [2026-10-26 補充（StockAnalysis 例行更新蒐集）]

- **抓取時間**：2026-10-26（台北時間上午，雅加達與紐約皆未開盤）
- **抓取方式**：`WebSearch` ＋ Firecrawl 抓 Kontan、Suara.com、Selular.ID 全文；Yahoo Finance 歷史股價（TLK、TLKM.JK 確認 10/23 後無新報價）
- **抓取結果**：✅ 成功（Kontan Insight 專題為付費文章，只取得標題與導言）

##### 🎯 MSCI 降級諮詢歷史：12 次有 10 次成真
- **來源連結**：[Kontan Insight 2026-10-25](https://insight.kontan.co.id/news/dari-12-konsultasi-penurunan-klasifikasi-market-oleh-msci-hanya-dua-yang-selamat)、[KabarBursa（Stockbit 統計）](https://www.kabarbursa.com/market-hari-ini/ri-terancam-downgrade-ke-standalone-market-begini-dampaknya.md)
- **關鍵要點**：
  - Stockbit 研究團隊統計 2006 年以來 MSCI 12 次降級諮詢，10 次最後降級；Kontan 專題標題「12 次只有 2 次逃過」，並指外資在 MSCI 決定前已在調整部位。
  - 兩次未降級的市場名稱未查到。

##### 🎯 BRI Danareksa（10/22 報告）：維持 buy、TP 3,500 盧比；2027 CapEx 可能上修
- **來源連結**：[Kontan 2026-10-25](https://investasi.kontan.co.id/news/telkom-tlkm-ekspansi-pusat-data-ai-bri-danareksa-targetkan-harga-saham-rp-3500)
- **關鍵要點**：
  - NeutraDC Batam 由 3 × 18MW 擴大為總計 118MW：BTM-1 18MW 已全數簽約、首批 6MW 4Q26 上線；BTM-2 100MW 2028 年服務，CapEx 約 13–17 兆盧比（視 NeutraDC 出售而定），已取得 90MW 供電、Medco 為合資夥伴。
  - Telin 海纜容量售出 >85%，Bifrost 預計 1Q27 售罄；2026 EBITDA 目標 2 兆盧比；2030 企業價值目標 40–45 兆；2031 前 CapEx 32 兆。
  - 2027 合併 CapEx 可能由 29 兆升至約 35 兆盧比；淨負債／EBITDA 0.6 倍。風險：5G 投資不足。

##### 🎯 家寬資費月減 2.2%；TLKM 2H 可能再提 6–8 兆減損
- **來源連結**：[Kontan 2026-10-25](https://investasi.kontan.co.id/news/tarif-internet-rumah-turun-22-bagaimana-prospek-saham-telekomunikasi)
- **關鍵要點**：
  - Mirae Asset（10/23）：10 月家寬資費平均月減 2.2%，IndiHome、XL Satu、ICON+、Biznet 調價。
  - 券商估 TLKM 固網 ARPU 約 219,000 盧比（年增 5%）、用戶 9.86 百萬（年減 4%）；2H2026 可能再提 6–8 兆盧比減損，ERP 費用壓 3Q 獲利（公司未證實）。
  - 印尼電信類股 EV/EBITDA 約 4.1 倍，約低於歷史平均 2 個標準差。

##### 🎯 外資整週淨賣 TLKM 6,068 億盧比；Danantara 證實進場
- **來源連結**：[Kontan 2026-10-24](https://investasi.kontan.co.id/news/asing-net-sell-rp-872-triliun-sepekan-cermati-saham-yang-banyak-dijual)、[Suara.com 2026-10-25](https://suara.com/bisnis/2026/10/25/155845/danantara-getol-serok-saham-saat-ihsg-diguncang-msci)
- **關鍵要點**：
  - 10/19–10/23 JCI 漲 4.9% 至 5,439.25，外資全市場淨賣 8.72 兆盧比；TLKM 淨賣 6,068.3 億（第 4 大，次於 BBCA、BBRI、BMRI）。與 10/20 單日淨買超合看，外資整週仍偏賣。
  - Danantara 投資長 Pandu Sjahrir 證實已開始買股，18 兆盧比（10 億美元）分批投入至年底；標的未揭露。Danantara 持 TLKM 52.09%。

##### 🎯 其他
- **CGS International**（[Selular.ID 2026-10-26](https://selular.id/2026/10/dividen-telkom-makin-menggiurkan-usai-kisruh-msci-ai-jadi-andalan/)）：股價下跌推高殖利率；TLKM 30 目標 EBITDA 率 50%、ICT 2030 年佔營收 25%、NeutraDC 2030 年 400MW。媒體自注殖利率上升不代表股利增加。
- **3Q2026 財報日期**：仍未見公司公告；3Q2025 為 2025-10-30 發布（Bisnis.com／Kontan）。

---

#### [2026-10-26 ~ 10-27 補充（StockAnalysis 例行更新蒐集）]

##### 🎯 OJK 推三項措施回應 MSCI
- **來源連結**：[CNBC Indonesia 2026-10-26](https://www.cnbcindonesia.com/market/20261026094013-17-779355/hadapi-msci-ojk-siapkan-3-jurus-ini)
- **關鍵要點**：
  - ①免股東會（RUPS）買回延長至 2027 年 6 月，但不得違反最低自由流通股規定；②要求 IDX 讓 HSC 委員會納入 SRO 以外獨立人士；③強化異常交易與協同交易監控。
  - 2026 年至今 OJK 對 166 方罰款 2.3 兆盧比；OJK 表示指數回穩不代表壓力結束。IDX 已於 10/19 聯繫 MSCI 要求說明諮詢依據，尚未見回覆。

##### 🎯 10/26 外資淨賣 TLKM 3,294 億盧比
- **來源連結**：[Kontan 2026-10-26](https://investasi.kontan.co.id/news/ihsg-terkoreksi-121-ke-5373-cek-saham-net-sell-terbesar-asing-di-awal-pekan)
- **關鍵要點**：
  - JCI 連漲四天後跌 1.21% 至 5,373.09；外資全市場淨賣 1.85 兆盧比；TLKM 淨賣 3,293.9 億（第 2 大，次於 BMRI 4,000.3 億）。
  - TLKM 10/26 收 2,250 盧比；TLK ADR 10/26 收 12.25 美元（+1.0%）。BRI Danareksa 10/27 晨報推薦 TLKM。

##### 🎯 3Q2026 財報日期與券商評等
- **來源連結**：[ad-hoc-news 2026-10-26](https://www.ad-hoc-news.de/boerse/news/corporate-news/bank-of-america-keeps-buy-on-telkom-indonesia-stock/70415087)、[BatamToday](https://batamtoday.com/news/telkom-percepat-buyback-saham-rp-4-triliun-sisa-anggaran-di-atas-rp-3-triliun)
- **關鍵要點**：
  - Quanteia 標 3Q 財報 10/29，Earnings Whispers 標 10/30；公司未正式公告。
  - Bank of America 10/21 維持 Buy（目標價未揭露）。
  - Telkom 宣布加速執行 4 兆盧比買回，至 10/19 尚餘 3 兆以上，未公布時程與金額。

---

#### [2026-10-27 ~ 10-28 補充（StockAnalysis 例行更新蒐集）]

- **抓取時間**：2026-10-28（台北時間上午）
- **抓取方式**：`WebSearch` ＋ Firecrawl 抓 CNBC Indonesia、investor.id、Katadata、StockAnalysis 全文；Yahoo Finance（TLKM、IDR=X、同業）
- **抓取結果**：✅ 成功（Yahoo TLK 10/27 收盤缺值，改用 StockAnalysis）

##### 🎯 10/27 TLKM −4.89%、外資淨賣 2,344 億盧比
- **來源連結**：[investor.id 2026-10-27](https://investor.id/market/459629/tiga-raksasa-bursa-terempas-asing-belum-juga-puas)、[CNBC Indonesia 2026-10-28](https://www.cnbcindonesia.com/market/20261028063818-17-780036/ihsg-ditutup-turun-19-asing-buang-10-saham-ini)、[Katadata 2026-10-27](https://katadata.co.id/finansial/bursa/6ae07b6a97539/ihsg-anjlok-1-99-jelang-rupslb-bei-saham-grup-astra-untr-aali-justru-melesat)
- **關鍵要點**：
  - JCI 收 5,266.13（−1.99%），盤中一度 −3.49% 至 5,185；外資全市場淨賣約 6,512–6,683 億盧比，年初至今累計淨賣 97.3 兆。
  - 外資淨賣前三：BMRI 2,663 億、TLKM 2,344.5 億、BBNI 1,195.7 億；TLKM 收 2,140（−4.89%），IDXBUMN20 −1.86%。
  - Katadata 指跌勢發生在 IDX 10/28 臨時股東會前（市場關注 demutualization，POJK 13/2026 已於 9/21 發布）。
  - TLK ADR 10/27 收 11.76 美元（−4.0%）；USD/IDR 收 18,144。

##### 🎯 BRI Danareksa 外資流出壓力測試
- **來源連結**：[investor.id 2026-10-27](https://investor.id/market/459629/tiga-raksasa-bursa-terempas-asing-belum-juga-puas)
- **關鍵要點**：
  - 若 MSCI 降為 Standalone，最壞情境到 4Q2027 外資累計流出 140–160 億美元（252–288 兆盧比）。
  - 主動型基金賣壓約 40 億美元（72 兆盧比），集中在 4Q2026（front-loaded）；被動型基金在 3Q2027 MSCI 定案後賣出。
  - 賣壓大小取決於執法進展、投資人信心與估值。

##### 🎯 3Q2026 財報日期
- **來源連結**：[ad-hoc-news 2026-10-27](https://www.ad-hoc-news.de/boerse/news/corporate-news/telkom-indonesia-completes-buyback-bri-keeps-target-for-telkom-indonesia-stock/70418463)
- **關鍵要點**：ad-hoc-news 標 10/29，Earnings Whispers 標 10/30；公司 IR 與 IDX 尚未見正式公告。

---

#### [2026-10-28 ~ 10-29 補充（StockAnalysis 例行更新蒐集）]

- **抓取時間**：2026-10-29（台北時間上午）
- **抓取方式**：Firecrawl 抓 Kontan Pusat Data、CNBC Indonesia 全文；`WebSearch`；Yahoo Finance（TLK、TLKM.JK、ISAT.JK、IDR=X）；SEC EDGAR 近期申報
- **抓取結果**：✅ 成功

##### 🎯 10/28 JCI 反彈，但 TLKM 仍是外資第一大淨賣股
- **來源連結**：[Kontan Pusat Data 2026-10-28](https://pusatdata.kontan.co.id/news/ihsg-menguat-031-ada-net-buy-asing-besar-di-saham-saham-ini-rabu-2810)
- **關鍵要點**：
  - JCI 盤中重挫後收 5,282.31（+0.31%）；外資全市場「淨買」6,642 億盧比（BBCA 淨買 1.2 兆）。
  - 外資淨賣前三：TLKM 4,335 億、BMRI 2,765 億、BBNI 859 億；TLKM 收 2,070（−3.27%），基礎建設類股 −2.13%。
  - Indosat（ISAT）−6.82% 至 1,570，為 LQ45 最大跌幅；電信股集體走弱。
  - TLK ADR 10/28 收 11.43 美元（−2.8%），盤後 11.35。

##### 🎯 CNBC Indonesia：WisdomTree 指數調整剔除 TLKM
- **來源連結**：[CNBC Indonesia 2026-10-28](https://www.cnbcindonesia.com/market/20261028081539-17-780048/ihsg-ditutup-turun-19-simak-5-saham-pilihan-hari-ini)
- **關鍵要點**：報導稱 10/27 跌勢「也受 WisdomTree 指數 rebalancing 影響，23 檔被剔除，包括 TLKM、PTBA、PGAS、BREN」；未寫指數名稱與生效日，其他來源查無佐證。

##### 🎯 IDX 臨時股東會通過 demutualization 章程修改
- **來源連結**：[CNBC Indonesia 2026-10-28](https://www.cnbcindonesia.com/market/20261028123721-17-780150/jelang-demutualisasi-bei-bagikan-dividen-tunai-rp156-triliun)、[Bisnis.com 2026-10-28](https://market.bisnis.com/read/20261028/7/2016309/bei-gelar-rupslb-hari-ini-2810-minta-restu-demutualisasi-bursa)
- **關鍵要點**：
  - 股東會通過 demutualization 相關章程修改，須再經 OJK 與法務人權部核准才生效。
  - 另通過特別現金股利 1.564 兆盧比（每股 170 億盧比），2 兆盧比保留盈餘轉營運與發展準備。

##### 🎯 印尼盾創紀錄新低
- **來源連結**：[Kontan Pusat Data 2026-10-28](https://pusatdata.kontan.co.id/news/rupiah-melemah-6-hari-beruntun-kurs-jisdor-cetak-rekor-terlemah-sepanjang-masa)
- **關鍵要點**：即期匯率收 18,184（−0.15%，連 6 天走弱）；JISDOR 18,183，為有紀錄以來最弱。

##### 🎯 3Q2026 財報日期
- **來源連結**：Yahoo Finance TLK 報價頁（earnings 時間戳 2026-10-30 美東、法說 2026-11-01，皆標「預估」）、[AJ Bell](https://www.ajbell.co.uk/market-research/sub/NYSE:TLK/company-info)
- **關鍵要點**：多數來源指向 10/30；SEC EDGAR 至 10/29 台北上午最新 6-K 仍為 10/22，尚未申報 3Q。

---

#### [2026-10-29 ~ 10-30 補充（StockAnalysis 例行更新蒐集）]

- **抓取時間**：2026-10-30（台北時間上午）
- **抓取方式**：Firecrawl 抓 Kontan Pusat Data、CNBC Indonesia 全文；Firecrawl 搜尋；Yahoo Finance（TLK、TLKM.JK、IDR=X）；SEC EDGAR 近期申報
- **抓取結果**：✅ 成功（10/29 外資淨賣 TLKM 精確金額未取得）

##### 🎯 10/29 JCI 崩 3.49%，TLKM −4.35%
- **來源連結**：[Kontan Pusat Data 2026-10-29](https://pusatdata.kontan.co.id/news/ihsg-tumbang-349-diiringi-net-sell-asing-rp-108-triliun-hari-ini-2910)、[CNBC Indonesia 2026-10-30](https://www.cnbcindonesia.com/research/20261029184133-128-780742/jumat-krusial-10-sentimen-panas-ini-bisa-bikin-pasar-ri-bergejolak)、[Emitennews 2026-10-29](https://emitennews.com/news/anjlok-349-persen-ihsg-dekati-level-5000)
- **關鍵要點**：
  - JCI 收 5,098.06（−3.49%），一週 −5.38%、年初至今 −41.04%；LQ45 全數下跌，基礎建設類股 −4.24%（CNBC 口徑 utilities −5.99%）。
  - 外資全市場淨賣 1.08 兆盧比（常規市場 1.52 兆）；淨賣前三：BBCA 5,035 億、BBRI 1,645 億、BMRI 1,559 億。TLKM 不在前三，Kontan 排行圖顯示約第 5 名。
  - TLKM 收 1,980（−4.35%），成交 5,410 億盧比；CNBC 點名 BBCA、ASII、BBRI、TLKM、BMRI 為主要拖累。
  - TLK ADR 10/29 收 11.22 美元（−1.8%），盤後 11.15；以 18,125 換算 ADR 溢價約 +2.7%。

##### 🎯 主權風險指標升溫
- **來源連結**：[CNBC Indonesia 2026-10-30](https://www.cnbcindonesia.com/research/20261029184133-128-780742/jumat-krusial-10-sentimen-panas-ini-bisa-bikin-pasar-ri-bergejolak)
- **關鍵要點**：
  - 印尼 5 年 CDS 10/29 為 103.48bp（10/28 106.34、10/14 91.78）。
  - 10 年公債殖利率 10/28 7.706%（2020 年 5 月以來最高），10/29 回落至 7.643%；公債標售投標金額由 10/13 的 64.86 兆降到 10/27 的 31.09 兆（−52%）。
  - 印尼盾 10/29 收 18,125（Refinitiv，+0.28%），前一日為紀錄最弱收盤。Fed 10/28 維持 3.75%–4.00%；BI 表示 11 月利率決策視數據而定。

##### 🎯 3Q2026 財報仍未發布
- **來源連結**：Yahoo Finance TLK 報價頁（earnings 時間戳美東 2026-10-30 16:00、法說 2026-11-01，皆標「預估」）；SEC EDGAR（最新 6-K 仍為 2026-10-22）
- **關鍵要點**：截至台北 10/30 上午尚無 3Q 6-K 或 IDX 公告；Telkom 官網 10/29 僅有新總裁在 DTIIF 論壇談 AI 基礎建設（連網、資料中心、AI 模型平台）的新聞稿。

##### 🎯 指數成分調整
- **來源連結**：[Kontan Pusat Data 2026-10-29](https://pusatdata.kontan.co.id/news/ini-daftar-lengkap-saham-baru-lq45-untuk-periode-2-november-2026-29-januari-2027)
- **關鍵要點**：LQ45、IDX30、IDX80 新名單 11/2 生效；IDX30 剔除 PGEO、UNVR；TLKM 續留。

---

#### [2026-10-30 ~ 10-31 補充（StockAnalysis 例行更新蒐集）]

- **抓取時間**：2026-10-31（台北時間上午）
- **抓取方式**：SEC EDGAR（sec-edgar-mcp `get_recent_filings` + 6-K 原文 curl）；Firecrawl 抓 investortrust、Kontan 全文；WebSearch；Yahoo Finance（TLK、TLKM.JK、IDR=X、同業）
- **抓取結果**：✅ 成功

##### 🎯 3Q2026（9M）合併財報已發布（6-K）
- **來源連結**：[6-K 2026-10-30 Consolidated financial statements as of September 30, 2026](https://www.sec.gov/Archives/edgar/data/1001807/000100180726000076/0001001807-26-000076-index.htm)（EDGAR 收件 2026-10-30 19:59 UTC，美東收盤前 1 分鐘）
- **核心觀點**：
  > "REVENUES 113,502 / 109,617 … Unrealized loss on changes in fair value of investments (1,663) / (360) … OPERATING PROFIT 27,999 / 28,244 … Owners of the parent company 14,446 / 15,031 … Profit per share 146.31 / 151.73"（單位：十億盧比；9M2026 / 9M2025，比較期已依新會計政策調整）
- **關鍵要點**：
  - 9M 營收 +3.5%，歸屬母公司淨利 −3.9%；推算 3Q 單季淨利 3.82 兆（年減 16.1%），主因投資公允價值損失 3Q 單季 1.33 兆（9M 合計 1.663 兆：Telkomsel 持有 GOTO 0.759 兆、MDI 新創投資 0.794 兆）。
  - 市場傳聞的 6–8 兆減損 **3Q 未認列**。
  - 9/30 庫藏股 594,375,800 股（流通 98,467,840,800 股）；2026 年至 9/30 買回金額 1,749 十億盧比。
  - 員工數 17,442 人（2025 年底 19,082 人，−8.6%），付給員工現金 +22.7%（自願離職金）。
  - Telkomsel 2023 年度補稅（Art.23 預扣稅 12,844 十億＋公司所得稅 1,623 十億，含罰款）異議於 2026-09-15 被稅局全數駁回，將於 2026-12-14 前上訴稅務法院；公司未提列。
  - 期後事項：TIF 光纖分拆適用帳面價值法被稅局拒絕，公司 10/15 提出答辯，等待開庭。

##### 🎯 媒體報導 3Q 財報
- **來源連結**：[investortrust 2026-10-31](https://investortrust.id/market/121081/pendapatan-telkom-tlkm-tumbuh-jadi-rp-113-5-triliun-hingga-kuartal-i-2026)（標題誤植「Kuartal I」，內文為 9M）
- **關鍵要點**：營收 113.50 兆（+3.54%）、淨利 14.45 兆（−3.89%）；點名公允價值損失 1.66 兆拖累獲利。

##### 🎯 10/30 JCI −0.80%，外資淨賣 TLKM 第 2 大
- **來源連結**：[Kontan 2026-10-30](https://investasi.kontan.co.id/news/ihsg-terkoreksi-080-ke-5057-cek-saham-net-sell-terbesar-asing-di-akhir-pekan-ini)、[Kontan Pusat Data 2026-10-30](https://pusatdata.kontan.co.id/news/ihsg-turun-1670-sepanjang-oktober-2026-ditutup-5057-pada-jumat-3010)
- **關鍵要點**：JCI 收 5,057.05（−0.80%），一週 −7.03%，整個 10 月約 −16.2% 到 −16.7%；外資全市場淨賣 1,402.7 億，一週 4.20 兆、一個月 16.50 兆。淨賣前三：BBRI 2,065.4 億、TLKM 1,194.8 億、AMMN 593.3 億。TLKM 收 1,980（平盤，財報在收盤後才公布）。

##### 🎯 Telkom × PLN × Danantara：National AI Data Center Hub MoU
- **來源連結**：[investortrust 2026-10-30](https://www.investortrust.id/business/121017/telkomgroup-gandeng-pln-dan-danantara-kembangkan-hub-data-center-ai-perkuat-infrastruktur-digital-indonesia)
- **關鍵要點**：10/27 在 DTIIF 論壇簽 MoU，合作電力、連網與資料中心；投資金額與商業模式仍在討論。

##### 🎯 同業：Indosat 10/30 跌 6.8%
- **來源連結**：Yahoo Finance ISAT.JK（2026-10-30）
- **關鍵要點**：ISAT 收 1,365（52 週新低），Yahoo 顯示最近一季淨利年減 51%；Forward PE 6.85 倍、殖利率 7.58%。

##### 🎯 OJK 主席回應 MSCI
- **來源連結**：[IDN Financials](https://idnfinancials.com/news/71078/capital-market-faces-msci-threat-ojk-chief-relies-on-retail-investors)
- **關鍵要點**：OJK 主席表示會持續建立市場對改革的信心，並認為本地散戶力量變強可緩衝外資撤出；MSCI 本身無新表態。

---
