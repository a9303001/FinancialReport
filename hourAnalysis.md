/goal

---
# 個股分析1
<OUTPUT_FILENAME>` : hourAnalysisResult.md
> **載入並執行 `StockAnalysis` Skill**（`.agents/skills/StockAnalysis/SKILL.md`），傳入以下參數：
- `COMPANY_NAME`：TLK 印尼電信
- `MARKET`：美股ADR
- `COMPANY_FOLDER`：TLK印尼電信
- `EXTRA_ANALYSIS`：
  1. **每股美元化：所有每股數字以「每 1 ADS（美元 USD）」為主要單位**（依 EXTRA_ANALYSIS 指定）
     - 先查證並寫明 ADR 轉換比例（目前資料顯示 1 ADS = 100 股 TLKM Series B 普通股；以最新 20-F 及 BNY Mellon 存託銀行公告為準）。
     - 財報原幣為印尼盾（IDR）。換算公式：`每 ADS 美元 = 每股普通股 IDR × ADR 比例 ÷ USD/IDR 匯率`；美元在前、IDR 放括號。
     - 適用範圍：EPS、Forward EPS、BPS、DPS、每股營收、每股營業利益、每股 FCF、每股 CapEx 等所有每股金額。
     - 匯率聲明：損益表用期間平均匯率，資產負債表用期末匯率；寫明數值、時點與來源。
     - 匯率敏感度：寫出「IDR 兌 USD 每貶值 1%，每 ADS EPS 減少約 X 美元」。
     - 股價同時列 TLK（NYSE，USD）與 TLKM（IDX，IDR），並算出 ADR 相對本地股的溢價／折價率。
  2. **2026 年為什麼大跌：做量化歸因，不要只列新聞**
     - 先列事實：2026 年初至今 TLK（USD）與 TLKM（IDR）的跌幅、波段最低點與日期。
     - 跟大盤與同業比：JCI（雅加達綜合指數）、MSCI Indonesia 指數、Indosat（ISAT）、XLSmart（EXCL），用來分出「整個市場在跌」還是「公司自己出問題」。
     - 拆出匯率貢獻：`TLK 美元跌幅 ≈ TLKM 本地跌幅 + IDR 貶值幅度`，算出各自佔幾個百分點。
     - 逐類檢查原因並量化：
       - (a) 基本面：營收／EBITDA／淨利年增率、Telkomsel 行動用戶數與 ARPU、IndiHome 固網、價格戰、資料中心與鐵塔資產重組（Mitratel、NeutraDC 等）。
       - (b) 政策／治理：Danantara（印尼主權基金）接管國營企業持股的影響、股利政策變動、管理層更換。
       - (c) 資金面：MSCI 事件、外資賣超金額。
     - 每個原因都要寫：發生日期、對每 ADS 股價或 EPS 的影響（USD）、一次性或常態性、股價是否已反映。
     - 結論：跌幅是否超過基本面惡化幅度？用 PE、PB、殖利率跟各自 5 年中位數比較，判斷是「超跌」還是「合理修正」。
  3. **每 ADS 的存託管理費（depositary fee）與實際持有成本**
     - 查證來源：最新 20-F 的 Item 12.D，以及 BNY Mellon ADR 官網公告。
     - 逐項列出（每 ADS 美元）：
       - 年度存託服務費（depositary service fee）。
       - 現金股利分配費（cash distribution fee）。
       - ADS 發行／註銷費（每 100 ADS 收多少）。
       - 其他費用（如有）。
     - 算實際成本：查近 1–2 次配息實際從股利中扣了多少，換算成佔每 ADS 股利的 % 與佔股價的 %。
     - 併算印尼股利預扣稅（分別寫美國投資人、台灣投資人的稅率，以及是否適用租稅協定）。
     - 用流程寫出：`每 ADS 毛股利 → 扣預扣稅 → 扣存託費 → 淨股利（USD）`，並算出實際淨殖利率。
     - 一句話結論：直接買 IDX 的 TLKM 和買 NYSE 的 TLK，在費用、稅與流動性上差多少、哪個划算。
  4. **MSCI 對印尼降級的影響（市場層面 ＋ TLK 個別衝擊）**
     - 先釐清時間軸與現況：MSCI 對印尼 free float 及股權透明度的疑慮 → 指數調整凍結 → 擬由 Emerging Market 改列 Standalone Market 的諮詢（諮詢截止日、最終決定日都要查證）。明確區分「已發生」與「尚未定案」。
     - 量化被動資金賣壓：TLKM 在 MSCI EM 與 MSCI Indonesia 的權重、追蹤資產規模，估算若被剔除的被動賣出金額（USD），換算每 ADS 金額，並換算約等於 TLKM 幾天的日均成交量。
     - TLK 自身條件：政府／Danantara 持股比例、實際 free float 比例、是否符合 15% 最低 free float 新規、外資持股比例。
     - 情境分析（維持 EM／降為 Frontier／改列 Standalone）：每個情境寫機率判斷，以及對每 ADS 股價、PE、PB 的影響（USD）。
     - 回升條件：若 OJK／IDX 的改革被 MSCI 認可，股價有多少回升空間。
     - 所以呢：對長期持有者來說，這是「跟基本面無關的資金面殺盤 → 撿便宜機會」，還是「估值折價會長期存在」？
  5. **MSCI 為什麼要把印尼踢出新興市場：只講原因，影響留在第 4 題，不重複**
     - 以 MSCI 官方公告與諮詢文件為主要來源，逐條列出 MSCI 點名的問題，例如：free float 計算不可靠、股權結構不透明（隱藏的集中持股）、疑似協同炒作、監管執法不一致。
     - 每條都寫：MSCI 原文重點（英文附白話中文）、具體案例或數據、印尼當局（OJK／IDX）已做的回應。
     - 說明 MSCI 為何認為降到 Frontier 還不夠、要改列 Standalone（寫出 MSCI 公開的理由）。
     - 對照 TLK：上述哪些問題跟 TLK 有關、哪些無關（例如 TLK 是國營大型權值股，股權結構相對透明）。用來判斷 TLK 是「被市場連坐」還是「本身也有問題」。
     - 歷史對照：找過去被 MSCI 降級或改列 Standalone 的市場（如阿根廷、奈及利亞、巴基斯坦等，需查證），寫出當時權值股的跌幅與多久回升，作為 TLK 的參考。








