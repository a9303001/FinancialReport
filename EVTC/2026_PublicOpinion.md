# [EVTC] 2026 年 輿情彙整

> 本檔由 **ArrangePublicOpinionMd Skill** 自動彙整，內容為本資料夾 2026 年度所有「輿情／新聞／討論區」`.md` 的原文合併。
> 不含年報、季報、公司公告 report。
> 最後彙整時間：2026-09-21 02:02｜本次併入：1 檔｜累計併入：18 檔

## 目錄

- [2026-06 · 06-28](#2026-06--06-28)
- [2026-06 · Reddit](#2026-06--reddit)
- [2026-06 · SeekingAlpha](#2026-06--seekingalpha)
- [2026-06 · StockTitan](#2026-06--stocktitan)
- [2026-06 · TaiwanForums](#2026-06--taiwanforums)
- [2026-06 · YahooFinance](#2026-06--yahoofinance)
- [2026-07 · News](#2026-07--news)
- [2026-07 · Reddit](#2026-07--reddit)
- [2026-07 · SeekingAlpha](#2026-07--seekingalpha)
- [2026-07 · StockTitan](#2026-07--stocktitan)
- [2026-07 · YahooFinance](#2026-07--yahoofinance)
- [2026-08 · News](#2026-08--news)
- [2026-08 · Reddit](#2026-08--reddit)
- [2026-08 · SeekingAlpha](#2026-08--seekingalpha)
- [2026-08 · StockTitan](#2026-08--stocktitan)
- [2026-08 · YahooFinance](#2026-08--yahoofinance)
- [2026-08 · 輿情新聞](#2026-08--輿情新聞)
- [2026-09 · 輿情新聞](#2026-09--輿情新聞)
- [2026-09 · 輿情新聞 (更新)](#2026-09--輿情新聞-更新)

<!-- body:start -->





## 2026-06 · 06-28

<!-- source-file: 2026-06-28.md | bytes: 7359 | sha1: fef6fe7005a0 | merged-at: 2026-08-25 -->

$$yyyyMMdd$
EVTC（艾沃特）未來折舊與併購攤銷的問題，我需要去翻你上傳的原始 10-K／10-Q 檔案裡的「未來攤銷時間表（estimated future amortization expense）」——這張表是答案的核心，但它不在我目前的對話內容裡，只有路徑。讓我把原始財報抓出來讀。

原始財報檔案（FY2025 10-K 約 530KB、Q1 2026 10-Q 約 180KB）找到了。讓我搜尋裡面的「未來攤銷時間表」「goodwill」「depreciation and amortization」等關鍵段落。

找到了關鍵段落（line 3453）。讓我把 FY2025 10-K 裡的「未來攤銷時間表」和無形資產／商譽明細整段讀出來。

關鍵的「未來攤銷時間表」拿到了。但我需要把幾個東西分清楚——折舊（PP&E）、商譽（不攤銷只做減損測試）、無形資產攤銷（含併購）。讓我再抓商譽餘額、PP&E 折舊、以及併購攤銷 vs 軟體攤銷的拆分。

無形資產 FY2025 明細拿到了。現在抓商譽具體餘額數字、以及 PP&E 折舊與軟體攤銷的拆分。

資料齊全了。讓我快速核對 Q1 2026 10-Q 的最新商譽餘額與股數，確認有沒有更新（巴西雷亞爾匯率會讓商譽與無形資產波動）。

已從原始 FY2025 10-K 與 Q1 2026 10-Q 把數字全部挖出來並交叉核對完成。先附上問題的英文翻譯（依你的規則）：

> **English:** "EVTC — How much depreciation, goodwill, and acquisition-related amortization expense remains to be recognized/amortized in each of the coming years? Provide the per-share conversion."

---

#### 🔑 先講最重要的觀念釐清

你問題裡把三個東西放在一起，但它們的會計性質**完全不同**，必須分開看：

| 項目 | 會不會「逐年攤銷」進損益表？ | 性質 |
|:---|:---|:---|
| **折舊（PP&E Depreciation）** | ✅ 會，每年約 $23M | 經常性、可預測 |
| **無形資產攤銷（含併購）** | ✅ 會，有明確時間表 | 會逐年遞減 |
| **商譽（Goodwill）$918M** | ❌ **不攤銷** | 只做年度減損測試，平時不進損益 |

**商譽不會每年攤掉**——這是最常見的誤解。US GAAP 下商譽只在每年 8/31 做減損測試，**平時 0 元進損益表**；只有在整合失敗、被認定減損時，才會「一次性、非現金」重砸 GAAP 淨利。所以「未來每年還有多少商譽要攤」這個問題的答案是：**$0（除非發生減損）**。詳見下方第 3 段。

*（每股化基準：採最新 Q1 2026 稀釋股數 **62,578,904 股 ≈ 62.58M**）*

---

#### 1️⃣ 無形資產攤銷時間表（核心答案，10-K 官方揭露）

這是 FY2025 10-K「Note 13」明確揭露的**未來攤銷預估表**（基於 2025/12/31 帳上現有無形資產，**已含 Dimensa 全年**）：

| 年度 | 攤銷總額（無形資產，含軟體） | 換算每股 |
|:---|:---:|:---:|
| **2026** | $126.2M | **$2.02** |
| **2027** | $109.4M | **$1.75** |
| **2028** | $89.1M | **$1.42** |
| **2029** | $62.3M | **$1.00** |
| **2030** | $49.2M | **$0.79** |
| **2030 以後** | $116.8M | **$1.87** |

> 📌 注意 2026 的 $126.2M 比 2025 實際的 $99.8M 還高——因為 Dimensa 2025/10 才併入，2025 只認列約一季；2026 起是**整年**的併購攤銷。我用 Q1 2026 實際數字反推年化（單季無形攤銷約 $31.5M × 4 ≈ $126M）**完全吻合**這張表。

---

#### 2️⃣ 把上面的攤銷再拆成「會被加回」vs「不會被加回」

這一步最關鍵，因為它直接決定 **GAAP EPS 何時會往 Adjusted EPS 靠攏**。以 2026 年為例，總 D&A 約 $149M 拆解如下：

| D&A 組成 | 2026 金額 | 每股 | Adjusted EPS 會加回？ |
|:---|:---:|:---:|:---:|
| **併購無形攤銷**（客戶關係、商標）| ~$73M | **$1.17** | ✅ **會加回** |
| 軟體攤銷（自研/外購軟體）| ~$53M | $0.85 | ❌ 不加回（視為經常性）|
| PP&E 折舊 | ~$23M | $0.37 | ❌ 不加回 |
| **合計 D&A** | **~$149M** | **$2.38** | — |

**真正撐大 GAAP vs Adjusted 缺口的，是那塊 ~$73M（每股 $1.17）的「併購無形攤銷」。** 而從第 1 段的時間表可看出，這塊會**逐年快速縮小**（軟體攤銷大致穩定在 ~$50M，所以攤銷總額從 $126M → $49M 的下滑，主要就是併購那塊在消失）。

加上折舊（穩定約 $23M／每股 $0.37）後的**總 D&A 軌跡（假設不再併購）**：

| 年度 | 總 D&A（攤銷+折舊）| 每股 |
|:---|:---:|:---:|
| 2026 | ~$149M | $2.38 |
| 2027 | ~$132M | $2.12 |
| 2028 | ~$112M | $1.79 |
| 2029 | ~$85M | $1.36 |
| 2030 | ~$72M | $1.15 |

---

#### 3️⃣ 商譽（Goodwill）$918M 的處理

| 日期 | 商譽餘額 | 來源 |
|:---|:---:|:---|
| 2025/12/31 | $892.0M | FY2025 10-K |
| 2026/03/31 | **$918.2M** | Q1 2026 10-Q（升高主因：巴西雷亞爾升值的外幣換算）|

- **平時不攤銷、不進損益**，每股商譽約 **$14.67**（$918.2M ÷ 62.58M），佔總資產約 40%。
- 風險在於**一次性減損**：若 Dimensa／Sinqia 整合不如預期，減損會是非現金、但 GAAP 淨利的災難性重擊。EVTC 過去三年（2023–2025）皆**無減損**，且 2025 年測試 fair value 均高於帳面值，目前無立即風險，但這是長期懸在頭上的劍。

---

#### ⚠️ 三個必須標註的重大限制（資料缺口）

1. **這張表不含「未來的併購」。** EVTC 是連續併購者（Sinqia 2023、Tecnobank、Dimensa 2025）。**每做一筆新併購，就會新增一批客戶關係/商標無形資產，把上面的遞減曲線重新墊高。** 所以 $126M→$49M 的下滑是「不再併購」的基準情境，實際很可能維持在高檔。
2. **巴西雷亞爾（BRL）匯率**會同時牽動商譽與無形資產的美元金額（Q1 商譽就因此多了 $26M）。BRL 升值 = 美元攤銷金額變大。
3. **Dimensa 的購買價格分配（PPA）可能尚未定案**，measurement period 調整會微幅改變無形/商譽的拆分與攤銷。

---

#### 💡 對投資的意義（利多 vs 利空）

**🟢 利多（被空方低估的點）：** 純就「現有資產」看，併購攤銷（每股 $1.17）會在 2028–2030 大幅縮減，**GAAP EPS 會機械式地往 Adjusted EPS 收斂**——你檔案裡空方「D&A 黑洞永遠壓制 GAAP」的論點，其實高估了攤銷的持續性。這是 GAAP EPS 在 2028 後的結構性順風。

**🔴 利空（多方常忽略的點）：** 但前提是「**不再大舉併購**」。以 EVTC 的策略，這假設很可能不成立；只要再買一家公司，攤銷曲線就重新墊高，GAAP EPS 收斂的劇本就會延後。此外 $918M 商譽的減損尾部風險始終存在。

---

#### 📋 資料來源
- **FY2025 10-K**（`evtc-20251231.md`）：Note 12 商譽 rollforward（$892.0M）、Note 13 無形資產與未來攤銷時間表、Note PP&E 折舊 $22.3M
- **Q1 2026 10-Q**（`evtc-20260331.md`）：商譽 $918.2M、PP&E 季折舊 $5.8M、稀釋股數 62,578,904
- **交叉驗證**：`evtc_eps_reconciliation_analysis20260622.md`（Q1 D&A 拆分 $37.3M / Operating D&A $18.9M）

> ⚠️ 本分析僅供研究參考，不構成投資建議。

需要的話，我可以幫你把這份「未來 D&A／攤銷時間表」直接做成一個可下載的試算表（含逐年 GAAP→Adjusted EPS 橋接模型），方便你套進三年 EPS 預估裡。

---

## 2026-06 · Reddit

<!-- source-file: 202606_Reddit.md | bytes: 1875 | sha1: eda8fd3f7756 | merged-at: 2026-08-25 -->

### [EVTC Evertec, Inc.] 輿情討論整理 - [Reddit] (2026/06)

- **分析時間**：2026-06-22
- **資料範圍**：過去兩個月 (2026/04/22 - 2026/06/22)
- **來源網站**：Reddit (r/stocks, r/StockTitan)

---

#### 1. 焦點討論串與新聞整理

##### 🎯 估值與內在價值討論：股價是否被低估？
- **來源連結**: [Reddit r/stocks](https://www.reddit.com/r/stocks/)
- **發布時間**: 2026-06-12
- **核心觀點與論述**:
 > 「EVTC 的交易價格顯著低於其 GF 估值（GF Value），一些個股分析討論串指出，在經歷近期長達一年的下跌後，其股價被低估了將近 40%。」
- **關鍵要點與分析**:
 - **價值投資討論**：部分 Reddit 用戶注意到 EVTC 在經歷了一年的下跌後，估值已達吸引人的區間，相較於內在價值可能有高達 40% 的折價。
 - **財務實力中等**：討論中也指出，雖然估值便宜，但其財務強度得分（5/10）屬於中等水準，投資人需注意債務與利潤率壓縮的風險。

##### 🎯 Q1 2026 財報數據機器人發布與散戶討論
- **來源連結**: [Reddit r/StockTitan](https://www.reddit.com/r/StockTitan/)
- **發布時間**: 2026-05-06
- **核心觀點與論述**:
 > 「Evertec, Inc. (NYSE: EVTC) 公布第一季調整後每股盈餘（EPS）為 0.90 美元，營收超過 2 億美元（換算約每股營收 3.20 美元），低於市場預期。財報公布後的市場反應顯示股價在下跌時獲得買盤支撐。」
- **關鍵要點與分析**:
 - **利空出盡的市場表現**：散戶討論指出，雖然財報數字 miss 了預估值，但股價在財報後迅速反彈，呈現典型的利空出盡走勢，許多人認為這代表市場底部的確立。
 - **關注拉丁美洲增長**：Reddit 用戶提到拉美支付市場的成長空間大，是支撐 EVTC 長期估值的主要原因。

---

## 2026-06 · SeekingAlpha

<!-- source-file: 202606_SeekingAlpha.md | bytes: 2804 | sha1: fc70141bafd4 | merged-at: 2026-08-25 -->

### [EVTC Evertec, Inc.] 輿情討論整理 - [Seeking Alpha] (2026/06)

- **分析時間**：2026-06-22
- **資料範圍**：過去兩個月 (2026/04/22 - 2026/06/22)
- **來源網站**：Seeking Alpha

---

#### 1. 焦點討論串與新聞整理

##### 🎯 營收引導調升與收購 Dimensa 的綜效
- **來源連結**: [Seeking Alpha EVTC Analysis](https://seekingalpha.com/symbol/EVTC)
- **發布時間**: 2026-05-06
- **核心觀點與論述**:
 > 「隨著 Dimensa 收購的完成，Evertec 將其 2026 年全年營收指引調高至 10.73 億至 10.85 億美元的區間（換算約每股營收指引 17.15 至 17.34 美元）。此交易使 Evertec 定位為拉丁美洲領先的金融軟體即服務（SaaS）供應商。」
- **關鍵要點與分析**:
 - **上調財測**：收購 Dimensa 讓公司調高了 2026 年的全年營收目標。
 - **區域龍頭定位**：分析師看好 Dimensa 能大幅提升公司在巴西及拉美地區的金融 SaaS 服務能力。

##### 🎯 毛利率壓縮 (Margin Compression) 隱憂
- **來源連結**: [Seeking Alpha Analysis](https://seekingalpha.com/symbol/EVTC)
- **發布時間**: 2026-05-15
- **核心觀點與論述**:
 > 「分析師在第一季的電話會議中強調了利潤率壓縮（Margin Compression）的問題。整合 Dimensa 及其他擴張的成本可能會對短期獲利能力造成壓力。」
- **關鍵要點與分析**:
 - **短期的獲利逆風**：雖然營收因收購而增長，但整合成本與拉美地區推廣支出導致利潤率受到壓縮，這是分析師對其評級為 Hold 的主因。
 - **高槓桿/成本控制挑戰**：需要密切觀察後續幾季的成本控管，看毛利率是否能觸底回升。

---

#### 2. 補充更新 (2026-06-26)

##### 🎯 分析師下調目標價：期望值重置 (Reset)
- **來源連結**: [Public.com EVTC Forecast](https://public.com/stocks/evtc/forecast-price-target) ／ [Simply Wall St](https://simplywall.st/stocks/us/diversified-financials/nyse-evtc/evertec)
- **發布時間**: 2026-06（區間內，Q1 後更新）
- **核心觀點與論述**:
 > 「根據 5 位分析師的評估，EVERTEC 的共識評級為『持有』（Hold）。分析師將其目標價從 34 美元下調至 29 美元，理由是期望值的重置（Reset），但同時也強調拉美（LatAm）業務板塊以及近期在巴西的收購案是其核心優勢所在。」
- **關鍵要點與分析**:
 - **目標價遭砍**：分析師將目標價由 34 美元下調至 29 美元（共識仍維持 Hold），反映對短期獲利的「期望值重置」；但同時點名拉美（LatAm）板塊與巴西收購案為長期亮點。
 - **多空拉鋸**：賣方對近期利潤率與整合成本保守，卻承認其拉美布局具結構性成長潛力，呈現「短空長多」的分歧。

---

## 2026-06 · StockTitan

<!-- source-file: 202606_StockTitan.md | bytes: 3522 | sha1: c8070d55f301 | merged-at: 2026-08-25 -->

### [EVTC Evertec, Inc.] 輿情討論整理 - [StockTitan / 公司公告新聞] (2026/06)

- **分析時間**：2026-06-26
- **資料範圍**：過去兩個月 (2026/04/26 - 2026/06/26)
- **來源網站**：StockTitan、Investing.com、News is My Business、The Globe and Mail、SEC 8-K

---

#### 1. 焦點討論串與新聞整理

##### 🎯 智利 Transbank 合作案：深化拉美支付版圖
- **來源連結**: [StockTitan EVTC News](https://www.stocktitan.net/news/EVTC/) ／ [Simply Wall St](https://simplywall.st/stocks/us/diversified-financials/nyse-evtc/evertec/news/how-evertecs-transbank-deal-and-added-term-loan-capacity-cou)
- **發布時間**: 2026-05-18
- **核心觀點與論述**:
 > 「2026 年 5 月 18 日，EVERTEC 宣布簽署一項新協議，將為智利 Transbank 營運關鍵交易平台與服務，深化其在拉丁美洲作為技術供應商的角色。」
- **關鍵要點與分析**:
 - **拉美龍頭定位再強化**：拿下智利收單龍頭 Transbank 的交易平台與服務營運合約，是繼收購 Dimensa（巴西）後，於智利市場的重要插旗，鞏固「拉美金融科技基礎設施供應商」的定位。
 - **長期營收能見度**：此類平台營運合約通常為多年期、經常性收入（recurring revenue），有助提升營收能見度與護城河。

##### 🎯 增額 1.85 億美元 Term B 貸款：財務槓桿上升
- **來源連結**: [StockTitan 8-K](https://www.stocktitan.net/sec-filings/EVTC/8-k-evertec-inc-reports-material-event-97949bbb8a94.html) ／ [Investing.com](https://m.investing.com/news/sec-filings/evertec-amends-credit-agreement-secures-185-million-in-new-term-loans-93CH-4702683)
- **發布時間**: 2026-05-18
- **核心觀點與論述**:
 > 「EVERTEC 簽署了其 2022 年信貸協議的第六次修訂案，獲得額外 1.85 億美元的 B 型定期貸款（Term Loan B）（換算約每股貸款 2.96 美元）……使未償還的 B 型定期貸款總額達到 8.75 億美元（換算約每股 13.98 美元）。由 Truist Bank 擔任行政與擔保代理機構。」
- **關鍵要點與分析**:
 - **負債續增的利空訊號**：增額 1.85 億美元 Term B 貸款（換算約每股 2.96 美元），使 Term B 總額達 8.75 億美元（換算約每股 13.98 美元），主要用於償還循環信用額度。配合 Dimensa 收購（約 1.81 億美元／換算約每股 2.89 美元，折合約 9.5 億巴西雷亞爾），公司槓桿明顯升高。
 - **利率與整合風險**：新貸款與既有 Term B 條款相同（利率、到期日一致），但在高利率環境下，利息支出將持續侵蝕淨利，需留意負債比率惡化。

##### 🎯 資安事件升級：Sinqia / Pix 系統遭入侵（巴西）
- **來源連結**: [The Globe and Mail](https://www.theglobeandmail.com/investing/markets/stocks/EVTC/pressreleases/34562328/evertecs-sinqia-faces-security-breach-in-pix-system/)
- **發布時間**: 2026-06 月（區間內）
- **核心觀點與論述**:
 > 「Evertec 旗下 Sinqia 面臨巴西即時支付系統（Pix）的安全漏洞。」
- **關鍵要點與分析**:
 - **巴西子公司同遭資安事件**：除了波多黎各客戶資料外洩（5/13 經第三方支援平台），旗下巴西子公司 Sinqia 的 Pix（巴西即時支付系統）也傳出安全漏洞，顯示資安問題並非單一事件。
 - **整合期的營運風險**：剛完成 Dimensa／Sinqia 巴西整併，連續資安事件凸顯跨區整合下的系統與內控挑戰，恐影響客戶信任與監管關注。

---

## 2026-06 · TaiwanForums

<!-- source-file: 202606_TaiwanForums.md | bytes: 1684 | sha1: a15952ae6b73 | merged-at: 2026-08-25 -->

### [EVTC Evertec, Inc.] 輿情討論整理 - [台灣投資社群] (2026/06)

- **分析時間**：2026-06-22
- **資料範圍**：過去兩個月 (2026/04/22 - 2026/06/22)
- **來源網站**：股市爆料同學會、Fugle / 財報狗社群

---

#### 1. 焦點討論串與新聞整理

##### 🎯 股市爆料同學會：個股健診與交易量能討論
- **來源連結**: [股市爆料同學會 - EVTC 專頁](https://www.cmoney.tw/follow/channel/stock-EVTC)
- **發布時間**: 2026-06-20
- **核心觀點與論述**:
 > "EVTC 股價在美股大盤波動中表現相對穩定，成交量有溫和放大的跡象。拉美金融科技的龍頭地位有護城河，但一般台灣散戶因該公司業務在波多黎各和拉美，熟悉度較低。"
- **關鍵要點與分析**:
 - **區域護城河**：投資人認為 Evertec 在波多黎各的商戶收單市佔率極高，擁有穩固的基本盤。
 - **認知偏誤與關注度低**：由於非主流美股大型科技股，台灣美股圈討論度較低，但有少數價值投資取向的股民將其列入觀察清單。

##### 🎯 財務基本面與安全指標檢視
- **來源連結**: [財報狗 / Fugle 社群](https://statementdog.com/analysis/EVTC)
- **發布時間**: 2026-05-25
- **核心觀點與論述**:
 > "EVTC 的自由現金流充沛，殖利率有一定吸引力。然而，近期負債比率因收購 Dimensa 而上升，需要留意其財務安全性。"
- **關鍵要點與分析**:
 - **現金流良好**：雖然毛利率有些微壓縮，但公司的自由現金流仍相當穩健。
 - **負債風險**：台灣社群對其負債比率上升持謹慎態度，需觀察負債比率是否會持續惡化。

---

## 2026-06 · YahooFinance

<!-- source-file: 202606_YahooFinance.md | bytes: 4548 | sha1: a9a304dddee4 | merged-at: 2026-08-25 -->

### [EVTC Evertec, Inc.] 輿情討論整理 - [Yahoo Finance] (2026/06)

- **分析時間**：2026-06-22
- **資料範圍**：過去兩個月 (2026/04/22 - 2026/06/22)
- **來源網站**：Yahoo Finance

---

#### 1. 焦點討論串與新聞整理

##### 🎯 Q1 2026 財報發布與市場反應
- **來源連結**: [Yahoo Finance News](https://finance.yahoo.com/quote/EVTC)
- **發布時間**: 2026-05-06
- **核心觀點與論述**:
 > 「Evertec 公布 2026 年第一季每股盈餘（EPS）為 0.90 美元，略低於市場預期的 0.94 美元。然而，在財報公布後，股價出現上漲，反映出市場對其策略的樂觀態度與紀律嚴明的執行力。」
- **關鍵要點與分析**:
 - **財報微幅落後預期**：Q1 EPS 為 0.90 美元，低於分析師預期的 0.94 美元，主要是利潤率受到一些擠壓。
 - **股價不跌反升**：財報公布後股價反彈，市場對管理層重申全年展望及 Dimensa 合併效應展現信心。

##### 🎯 內部人增持 (Insider Buying) 提振市場信心
- **來源連結**: [Yahoo Finance Insider Trading](https://finance.yahoo.com/quote/EVTC/insider-transactions)
- **發布時間**: 2026-06-15
- **核心觀點與論述**:
 > 「5 月和 6 月有顯著的內部人買回報告，其中執行副總裁 Miguel Vizcarrondo 購買了 21,000 股，董事 Brian John Smith 購買了超過 16,000 股。」
- **關鍵要點與分析**:
 - **強烈的內部信心訊號**：經理人與董事在 5-6 月積極買入自家股票，通常被視為股價低估的強烈暗示。
 - **穩定持股信心**：在面臨利潤率受壓和資安事件的情況下，內部人增持有效穩定了市場散戶的信心。

##### 🎯 客戶數據安全事件披露
- **來源連結**: [Yahoo Finance News](https://finance.yahoo.com/quote/EVTC)
- **發布時間**: 2026-06-05
- **核心觀點與論述**:
 > 「Evertec 披露了一起數據安全事件，未經授權的第三方獲取了與 2026 年 5 月 13 日第三方平台事件相關的客戶和顧客數據。受影響的主要是波多黎各的金融機構客戶。」
- **關鍵要點與分析**:
 - **無營運中斷**：官方強調未造成服務中斷，但涉及客戶隱私外洩。
 - **短期商譽受損**：市場對金融科技公司的資安事件較為敏感，是近期的短期利空因子。

---

#### 2. 補充更新 (2026-06-26)

##### 🎯 資安事件升級：三宗聯邦集體訴訟纏身
- **來源連結**: [News is My Business](https://newsismybusiness.com/evertec-hit-with-3-class-action-lawsuits-over-data-breach/) ／ [ClassAction.org](https://www.classaction.org/data-breach-lawsuits/evertec-june-2026) ／ [GuruFocus](https://www.gurufocus.com/news/8907967/evertec-evtc-investigates-data-breach-incident)
- **發布時間**: 2026-06-12（訴訟提起）／2026-06-09（8-K 揭露）
- **核心觀點與論述**:
 > 「因網路安全事件，Evertec 面臨三起擬議的聯邦集體訴訟，這些訴訟於 6 月 12 日在美國波多黎各聯邦地方法院提起。原告指控 Evertec 未能採取合理的網路安全措施來保護個人資訊，包括姓名、聯絡資訊和交易記錄。」
- **關鍵要點與分析**:
 - **法律風險具體化**：資安事件已從「揭露」升級為「訴訟」——6/12 於波多黎各聯邦地院遭三名原告（Maribel Torres、Maria Aquino、Miguel Álvarez）分別提起集體訴訟，指控未採取合理資安措施。
 - **潛在賠償與合規成本**：8-K（6/9）證實外洩資料可能含交易紀錄與支付卡號。除商譽受損外，訴訟與和解、監管罰款及補救（信用監控）成本將構成中期財務不確定性。

##### 🎯 內部人持續加碼：Brian Smith 再買進
- **來源連結**: [TipRanks Insider Trading](https://www.tipranks.com/news/insider-trading/evertec-insider-makes-bold-move-with-fresh-share-purchase-insider-trading-news)
- **發布時間**: 2026-06-12
- **核心觀點與論述**:
 > 「董事 Brian John Smith 購買了 16,202 股 Evertec 股票，交易總價值為 427,894 美元（換算約每股 0.0068 美元，實際購買均價約每股 26.41 美元）。」
- **關鍵要點與分析**:
 - **逢低承接訊號延續**：在資安訴訟與目標價下調的利空中，董事 Brian Smith 於 6/12 再買進 16,202 股（約 42.8 萬美元，均價約 26.4 美元），延續 5-6 月的內部人增持趨勢。
 - **管理層信心 vs. 市場疑慮**：內部人用真金白銀表態，與分析師下調目標價形成對比，是散戶判斷底部的重要參考訊號。

---

## 2026-07 · News

<!-- source-file: 202607_News.md | bytes: 4398 | sha1: 903fda9c42e0 | merged-at: 2026-08-25 -->

### [EVTC Evertec, Inc.] 輿情討論整理 - [綜合財經新聞] (2026/07)

- **分析時間**：2026-07-19
- **資料範圍**：過去三個月（重點 2026 年 7 月）
- **來源網站**：MarketBeat、GuruFocus、Simply Wall St、公司 IR
- **抓取方式**：built-in（WebSearch / WebFetch）＋ Bright Data（search_engine）

---

#### 1. 焦點討論串與新聞整理

##### 🎯 分析師共識維持「持有」(Hold)，平均目標價 $33.20，FY2026 EPS 指引 $3.86–$3.98
- **來源連結**: [MarketBeat 2026-07-02](https://www.marketbeat.com/instant-alerts/evertec-inc-nyseevtc-receives-average-rating-of-hold-from-analysts-2026-07-02/)
- **發布時間**: 2026-07-02
- **核心觀點與論述**:
  > 「Evertec 目前獲得 7 家券商平均評級『持有』(Hold)，評級分布為 1 賣出 / 4 持有 / 2 買入；12 個月平均目標價為 $33.20。公司設定 FY2026 EPS 指引為 $3.86 至 $3.98。」
- **關鍵要點與分析**:
  - **多空分歧、共識偏中性**：7 家券商共識「持有」，賣方對整合成本與利潤率壓縮保守。
  - **文中列出的近期券商動作（多為 5 月）**：Weiss Ratings（5/22）自 hold(c-) 下調至 sell(d+)；Raymond James（5/7）重申 outperform、目標價 $34；Morgan Stanley（5/19）目標價由 $29 下調至 $25、equal weight；Wall Street Zen（5/9）由 buy 下調至 hold。
  - **每股化**：FY2026 EPS 指引中值約 $3.92（每股）。

##### 🎯 GuruFocus：股價單日漲 3.9% 至 $30.19，較 GF Value $44.16 折價 31.6%（估值偏低）
- **來源連結**: [GuruFocus 2026-07-15](https://www.gurufocus.com/news/8961417/a-look-at-evertec-inc-evtc-after-39-gain-gf-value-4416-vs-price-3019)
- **發布時間**: 2026-07-15
- **核心觀點與論述**:
  > 「On July 15, 2026, Evertec Inc EVTC shares rose 3.9%, bringing the current price to $30.19. Current price of $30.19 is 31.6% below GF Value estimate of $44.16, with Evertec Inc considered undervalued.」
- **關鍵要點與分析**:
  - **價值面看多訊號**：GF Value 模型顯示相對內在價值折價逾三成，屬「估值偏低」區間。
  - **近期動能轉強**：7 月中股價回升，配合 30 日報酬顯著轉正（見下）。
  - 註：GuruFocus 頁面 WebFetch 回 403，日期與內容以 Bright Data 搜尋結果摘要（"4 days ago"，即 07-15）與 WebSearch 摘要交叉驗證。

##### 🎯 Simply Wall St：現金產出強勁帶動情緒，敘事公允價值 $31（輕微低估）
- **來源連結**: [Simply Wall St News 2026-07-05](https://simplywall.st/stocks/us/diversified-financials/nyse-evtc/evertec/news/is-evertec-evtc-undervalued-as-strong-cash-generation-lifts)
- **發布時間**: 2026-07-05
- **核心觀點與論述**:
  > 「EVERTEC has drawn fresh investor attention after being highlighted as a significant cash producer with annual revenue and earnings growth above its peer group average... a 30 day share price return of 32.63% despite declining 20.45% over one year.」
  > 風險：「EVERTEC's reliance on large customers and exposure to currency swings in key Latin American markets could quickly challenge that view of mild undervaluation.」
- **關鍵要點與分析**:
  - **利多**：被點名為顯著現金產出者，營收與獲利成長高於同業，ROE 偏高；近 30 日股價報酬 +32.63%，短期情緒明顯改善。
  - **利空/風險**：客戶集中（依賴大客戶）＋ 拉美貨幣匯率波動，是估值論點的主要威脅。
  - 敘事公允價值 $31，較當時股價 $29.63 折價約 4.4%（區間 $25 空 / $40 多）。

##### 🎯 Q2 2026 財報將於 2026-07-29 盤前公布（市場預估 EPS 約 $0.95）
- **來源連結**: [Evertec Investor Relations](https://ir.evertecinc.com/home/default.aspx) ／ [Google Finance EVTC](https://www.google.com/finance/beta/quote/EVTC:NYSE)
- **發布時間**: 頁面資料截至 2026-07-16（IR 頁）
- **核心觀點與論述**:
  > 「Jul 29, 8:30 PM Fiscal period Q2 2026 EPS / Est. (USD) - / $0.95」（Google Finance）；IR 頁顯示 EVTC 股價 30.79（2026-07-16 延遲報價）與 2026 Earnings 專區。
- **關鍵要點與分析**:
  - **關鍵事件日**：Q2 2026 財報定於 2026-07-29 公布，市場共識 EPS 約 $0.95（每股）。
  - 屆時將檢視 Dimensa／Tecnobank 整合綜效、拉美營收占比、利潤率壓縮是否觸底，以及資安事件後續影響。

---

## 2026-07 · Reddit

<!-- source-file: 202607_Reddit.md | bytes: 1064 | sha1: 049c7e499988 | merged-at: 2026-08-25 -->

### [EVTC Evertec, Inc.] 輿情討論整理 - [Reddit] (2026/07)

- **分析時間**：2026-07-19
- **抓取結果**：❌ 無 2026 年 7 月 EVTC 專屬實質討論串

#### 搜尋嘗試紀錄
- 已嘗試：Firecrawl firecrawl_search（scoped reddit.com）→ 失敗，回 HTTP 402（帳戶額度用盡 / Payment Required）。
- 已嘗試：Bright Data search_engine（"Evertec EVTC reddit stock discussion 2026"）→ 成功回傳，但唯一命中的 Reddit 連結為 r/Stocks 每日綜合討論串（`/r/stocks/comments/1udcdrn/rstocks_daily_discussion_technicals_tuesday_jun/`，2026-06-23），其中被引用的「上漲 725%」個股非 EVTC，與本標的無關；無 EVTC 專屬且可驗證之 7 月貼文。
- **結論**：Reddit（r/stocks、r/investing）在 2026 年 7 月（截至 07-19）無針對 EVTC 的實質、可驗證討論串。EVTC 屬中小型金融科技股，Reddit 散戶關注度低，符合先前（202606_Reddit.md）觀察。為避免臆造，此處不虛構任何貼文內容。預料 7/29 Q2 財報後散戶討論度可能上升。

---

## 2026-07 · SeekingAlpha

<!-- source-file: 202607_SeekingAlpha.md | bytes: 1249 | sha1: 47ce7c7047b8 | merged-at: 2026-08-25 -->

### [EVTC Evertec, Inc.] 輿情討論整理 - [Seeking Alpha] (2026/07)

- **分析時間**：2026-07-19
- **抓取結果**：⚠️ 部分成功 / 7 月無新增實質分析文章

#### 1. 焦點資訊

##### 🎯 Q2 2026 財報日 2026-07-29（Seeking Alpha earnings 頁）
- **來源連結**: [Seeking Alpha EVTC Earnings](https://seekingalpha.com/symbol/EVTC/earnings)
- **發布時間**: 頁面資料（擷取於 2026-07-19）
- **核心觀點**: Seeking Alpha earnings 頁確認 EVTC 下一財報事件為 2026-07-29（Q2 2026）。

#### 2. 搜尋嘗試紀錄
- 已嘗試：WebSearch（"Evertec EVTC analyst rating price target July 2026"）→ 找到 Seeking Alpha symbol/earnings 頁，但未見 2026 年 7 月新發表之付費分析文章（最新可見實質文章為 5/6 Q1 2026 Earnings Call Transcript）。
- 已嘗試：Bright Data search_engine → 命中之 Seeking Alpha 內容仍為 5/6 Q1 2026 財報電話會議逐字稿，無 7 月新文章。
- **結論**：Seeking Alpha 在 2026 年 7 月（截至 07-19）無新增針對 EVTC 的實質付費研究文章；預料 7/29 Q2 財報後才會有新分析。既有觀點（Dimensa 綜效、上調營收指引、利潤率壓縮、目標價下修）已收錄於 202606_SeekingAlpha.md。

---

## 2026-07 · StockTitan

<!-- source-file: 202607_StockTitan.md | bytes: 1194 | sha1: 4b90ec7a4966 | merged-at: 2026-08-25 -->

### [EVTC Evertec, Inc.] 輿情討論整理 - [StockTitan] (2026/07)

- **分析時間**：2026-07-19
- **抓取結果**：❌ 無 2026 年 7 月新內容（新聞流最新止於 2026-05-18）

#### 搜尋嘗試紀錄
- 已嘗試：WebFetch `https://www.stocktitan.net/news/EVTC/` → 成功抓取，但新聞流最新一則為 2026-05-18「Evertec Signs Strategic Agreement with Transbank」，其後依序為 05/06（Q1 2026 Results）、04/30（Dimensa 完成收購／宣告股利）、04/22、04/09，無任何 6 月下旬以後或 7 月的新公告。
- 已嘗試：WebSearch（"EVERTEC second quarter 2026 financial results announce date press release"）→ 未找到 StockTitan 上 EVTC 的 Q2 2026 財報日新聞稿（搜尋結果多為同名不同公司 EverQuote / Evercore）。
- **結論**：StockTitan 在 2026 年 7 月（截至 07-19）尚無 EVTC 新發布之公司公告/新聞稿。合理原因：Q2 2026 財報預定 2026-07-29 才公布，公司在財報前通常僅發布「財報日通知」新聞稿，該通知截至擷取時點尚未出現在 StockTitan 新聞流。既有 5 月項目（Transbank、Term Loan 增額、資安事件）已收錄於 202606_StockTitan.md。

---

## 2026-07 · YahooFinance

<!-- source-file: 202607_YahooFinance.md | bytes: 1922 | sha1: c49f980766d9 | merged-at: 2026-08-25 -->

### [EVTC Evertec, Inc.] 輿情討論整理 - [Yahoo Finance / StockTwits] (2026/07)

- **分析時間**：2026-07-19
- **資料範圍**：過去三個月（重點 2026 年 7 月）
- **來源網站**：Yahoo Finance、StockTwits
- **抓取方式**：built-in（WebSearch / WebFetch）

---

#### 1. 焦點討論串與新聞整理

##### 🎯 下一次財報日確認為 2026-07-29，社群情緒中性(50)
- **來源連結**: [StockTwits EVTC](https://stocktwits.com/symbol/EVTC)
- **發布時間**: 頁面即時資料（擷取於 2026-07-19）
- **核心觀點與論述**:
  > 「Next Earnings: July 29；52-Week Range: $21.81 - $37.71；Sentiment: Neutral (50)。」
- **關鍵要點與分析**:
  - **市場等待財報**：StockTwits 社群情緒指標中性(50)，市場處於 Q2 財報（7/29）前的觀望期。
  - **散戶關注重點**：內部人買股、8% 營收成長（拉美領軍）、Transbank 策略合作等主題仍是 StockTwits 熱議點。

##### 🎯 內部人加碼買進續為社群焦點
- **來源連結**: [StockTwits EVTC](https://stocktwits.com/symbol/EVTC)
- **發布時間**: 頁面即時資料（擷取於 2026-07-19）
- **核心觀點與論述**:
  > 「An insider purchased 21,000 shares valued at approximately $491,000 following a significant 36% decline in the stock price.」
- **關鍵要點與分析**:
  - **信心訊號延續**：在股價大跌約 36% 後內部人買進約 21,000 股（約 $491,000），被社群視為股價低估、管理層有信心的訊號（此事件先前 6 月已披露，7 月仍在社群發酵）。

---

#### 2. 搜尋狀態說明
- Yahoo Finance conversations（社群討論區）以 built-in 工具擷取時多為導覽/行情外殼，無新增可驗證之 7 月實質貼文；本檔以 StockTwits 可驗證內容＋Yahoo/IR 財報日資訊為主。
- Q2 2026 財報日 2026-07-29（來源交叉驗證：StockTwits、Google Finance、Evertec IR）。

---
## 2026-08 · News

<!-- source-file: 202608_News.md | bytes: 2892 | sha1: 3c81de387982 | merged-at: 2026-08-28 -->

### [EVTC EVERTEC] 輿情討論整理 - [綜合新聞 News] (2026/08)

- **分析時間**：2026-08-19
- **資料範圍**：過去三個月（重點 2026/08 Q2 財報後）
- **來源網站**：The Globe and Mail、Investing.com、StockStory、Simply Wall St
- **抓取方式**：內建工具（WebSearch / WebFetch）

---

#### 1. 焦點討論串與新聞整理

##### 🎯 Evertec 上調 2026 全年展望、Q2 業績超預期
- **來源連結**: [The Globe and Mail — Evertec Raises 2026 Outlook Amid Strong Q2 Performance](https://www.theglobeandmail.com/investing/markets/stocks/EVTC/pressreleases/3676459/evertec-raises-2026-outlook-amid-strong-q2-performance/)
- **發布時間**: 2026-08-04
- **核心觀點與論述**:
  > Q2 2026 營收 2.748 億美元，年增 20%；調整後 EBITDA 年增 18% 至 1.093 億美元；調整後 EPS 年增 18% 至 1.05 美元，優於市場預估的 0.95 美元（營收預估 2.606 億美元）。
- **關鍵要點與分析**:
  - 公司上調全年展望：固定匯率營收成長 14.5%~15.6%，調整後 EBITDA 利潤率維持 39%~40%，調整後 EPS 成長上看 11.7%。
  - 全年營收指引區間約 10.85 億~10.95 億美元（隱含 16.4%~17.5% 成長），調整後 EPS 3.94~4.04 美元。
  - **每股化**：Q2 營收 2.748 億美元 ÷ 約 5,980 萬股 ≈ 每股營收約 4.60 美元。

##### 🎯 拉美（LatAm）成長為財報超預期主力
- **來源連結**: [Investing.com — EVERTEC Q2 2026 slides: LatAm growth drives earnings beat](https://www.investing.com/news/company-news/evertec-q2-2026-slides-latam-growth-drives-earnings-beat-93CH-4836081)
- **發布時間**: 2026-08-05
- **核心觀點與論述**:
  > 拉丁美洲區營收成長約 52%，波多黎各（Puerto Rico）業務提供穩定基本盤；拉美業務占比已擴大至總營收 40% 以上。
- **關鍵要點與分析**:
  - LatAm Payments and Solutions 成為最大營運分部，Q2 營收 1.229 億美元、分部調整後 EBITDA 3,970 萬美元（去年同期 2,340 萬美元）。
  - 成長動能主要來自巴西併購案（Dimensa、Tecnobank）併入貢獻。

##### 🎯 股價反應與買回擴大
- **來源連結**: [Simply Wall St — EVERTEC (EVTC) Is Up 5.8% After Raising 2026 Revenue Outlook And Expanding Buybacks](https://simplywall.st/stocks/us/diversified-financials/nyse-evtc/evertec/news/evertec-evtc-is-up-58-after-raising-2026-revenue-outlook-and)
- **發布時間**: 2026-08-05
- **核心觀點與論述**:
  > 財報後股價盤中漲 4.63% 至 32.55 美元、盤後再漲 4.3% 至 33.95 美元，逼近 52 週高點（區間 21.81~37.71 美元）。公司將股票回購授權擴大至 1.5 億美元。
- **關鍵要點與分析**:
  - 近 90 天股價報酬約 +35%，但近 1 年總股東報酬仍為 -12.94%（顯示先前基期偏低）。
  - 買回授權擴大至 2027/12/31 前 1.5 億美元，釋出資本回饋訊號。

---

## 2026-08 · Reddit

<!-- source-file: 202608_Reddit.md | bytes: 1046 | sha1: 0121cd9c2aff | merged-at: 2026-08-28 -->

### [EVTC EVERTEC] 輿情討論整理 - [Reddit] (2026/08)

- **分析時間**：2026-08-19
- **抓取結果**：❌ 失敗（Reddit 全鏈被擋）

#### 搜尋嘗試紀錄

- 已嘗試：內建工具 WebSearch → Reddit 對內建 user-agent 回封鎖（§2.4 已知封鎖清單）。
- 已嘗試：firecrawl_search（限定 reddit.com）→ 回 HTTP 402（Firecrawl 額度用盡/需付費）。
- 已嘗試：brightdata scrape_as_markdown（`reddit.com/search`）→ 回「Residential (no KYC) access mode 不支援此站，需填 KYC」。
- 已嘗試：apify/rag-web-browser（`reddit.com/search`）→ Actor 執行成功但抓取請求失敗（0 succeeded, 1 failed，Reddit 反爬阻擋）。
- 已嘗試：playwright → 本次 session MCP 伺服器斷線/重連中，無法使用。
- **結論**：本次無法取得 Reddit 對 EVTC 的真實輿情，非 AI 生成，請下次重新嘗試。Reddit 相關的多空觀點已改由 Yahoo Finance / Seeking Alpha / StockTitan 等可抓取來源涵蓋（見同資料夾 202608 其他檔案）。

---

## 2026-08 · SeekingAlpha

<!-- source-file: 202608_SeekingAlpha.md | bytes: 2435 | sha1: 43d70169d73b | merged-at: 2026-08-28 -->

### [EVTC EVERTEC] 輿情討論整理 - [Seeking Alpha] (2026/08)

- **分析時間**：2026-08-19
- **資料範圍**：過去三個月
- **來源網站**：Seeking Alpha
- **抓取方式**：內建工具（WebSearch）

---

#### 1. 焦點討論串與新聞整理

##### 🎯 Dimensa 併購完成後上調全年營收指引
- **來源連結**: [Seeking Alpha — EVERTEC forecasts $1.073B-$1.085B 2026 revenue following Dimensa close](https://seekingalpha.com/news/4587893-evertec-forecasts-1_073b-1_085b-2026-revenue-following-dimensa-close)
- **發布時間**: 2026-05（Dimensa 完成後）
- **核心觀點與論述**:
  > 管理層在完成 Dimensa 併購後上調 2026 營收與獲利指引，指出市場機會擴大；Dimensa 在 2026 年預期為中性至略微增益，綜效預計 2027 年顯現。
- **關鍵要點與分析**:
  - Dimensa 帶來保險等新垂直領域，並提供顯著交叉銷售（cross-sell）機會，擴大巴西客戶基礎與產品線。

##### 🎯 拉美業務占比擴大至 40% 以上
- **來源連結**: [Seeking Alpha — Evertec outlines 2026 revenue growth of up to 11.2% and expands LATAM business to over 40% of total revenue](https://seekingalpha.com/news/4558405-evertec-outlines-2026-revenue-growth-of-up-to-11_2-percent-and-expands-latam-business-to-over)
- **發布時間**: 2026 上半年
- **核心觀點與論述**:
  > 拉美業務占總營收已超過 40%，LatAm Payments & Solutions 分部 2026 年預期以中 20%（mid-20%）速度成長，成為公司主要成長引擎。
- **關鍵要點與分析**:
  - 營運重心由波多黎各單一市場，逐步轉向拉美（尤其巴西）多元市場，降低區域集中度。

##### 🎯 Q2 業績簡報：拉美驅動、獲利短期承壓
- **來源連結**: [Seeking Alpha — EVERTEC, Inc. 2026 Q2 Results Earnings Call Presentation](https://seekingalpha.com/article/4930467-evertec-inc-2026-q2-results-earnings-call-presentation)
- **發布時間**: 2026-08-05
- **核心觀點與論述**:
  > 財報將較高的營收與大幅下滑的淨利並陳，並更新全年展望；Q2 營收 2.748 億美元（去年 2.296 億），淨利 541 萬美元（去年 4,047 萬美元）。
- **關鍵要點與分析**:
  - 市場關注點：投資人聚焦拉美擴張綜效能否在 2027 年兌現，以及一次性稅務/合資減損拖累是否為短期現象。
  - 近 90 天股價報酬約 +35%，但近 1 年總股東報酬 -12.94%。

---

## 2026-08 · StockTitan

<!-- source-file: 202608_StockTitan.md | bytes: 2758 | sha1: da89e7c95753 | merged-at: 2026-08-28 -->

### [EVTC EVERTEC] 輿情討論整理 - [StockTitan] (2026/08)

- **分析時間**：2026-08-19
- **資料範圍**：過去三個月（重點 2026/08 Q2 10-Q）
- **來源網站**：StockTitan
- **抓取方式**：內建工具（WebFetch）

---

#### 1. 焦點討論串與新聞整理

##### 🎯 營收成長但淨利受稅務與合資減損重擊
- **來源連結**: [StockTitan — EVERTEC (NYSE:EVTC) grows Q2 2026 revenue but earnings drop on tax and JV hit](https://www.stocktitan.net/sec-filings/EVTC/10-q-evertec-inc-quarterly-earnings-report-9e25be088bc2.html)
- **發布時間**: 2026-08-06
- **核心觀點與論述**:
  > Q2 2026 營收 2.748 億美元（去年同期 2.296 億）；但歸屬普通股股東淨利驟降至 540 萬美元（每股稀釋 0.09 美元），去年同期為 4,050 萬美元（每股 0.62 美元）。上半年淨利 2,920 萬美元（每股 0.48 美元），低於去年同期 7,320 萬美元（每股 1.15 美元）。
- **關鍵要點與分析（淨利下滑三大主因）**:
  - **稅率飆升**：有效稅率暴增至 74.7%，來自「為支應 Dimensa 併購而動用之海外子公司股利相關稅負」及「資本損失之評價備抵」。
  - **合資減損**：退出一項拉美合資事業（JV），認列 890 萬美元減損損失（列為權益投資損失）。
  - **利息成本上升**：利息費用由 1,670 萬美元增至 2,030 萬美元。
- **每股化**：合資減損 890 萬美元 ÷ 約 5,980 萬股 ≈ 每股約 0.15 美元的一次性衝擊。

##### 🎯 分部表現與併購布局
- **來源連結**: [StockTitan — EVTC 10-Q](https://www.stocktitan.net/sec-filings/EVTC/10-q-evertec-inc-quarterly-earnings-report-9e25be088bc2.html)
- **發布時間**: 2026-08-06
- **核心觀點與論述**:
  > 拉美支付與解決方案分部成最大分部，Q2 營收 1.229 億美元、分部調整後 EBITDA 3,970 萬美元（去年 2,340 萬）。其他分部：波多黎各及加勒比支付服務 4,070 萬美元、商戶收單 5,230 萬美元、企業解決方案 5,880 萬美元。
- **關鍵要點與分析**:
  - **併購**：Dimensa S.A.（巴西，2026/4/30 完成，約 1.99 億美元）；Tecnobank（巴西，2025/10 收購 75%，約 1.5 億美元）；BB Chain（巴西，2026/7/31 收購 67%，約 560 萬美元）。
  - **資本結構**：總負債 12.9 億美元（2025 年底 11.0 億）；上半年營運現金流 9,070 萬美元；商譽 10.7 億美元。
  - **股數變化**：在外流通股由 6,180 萬股降至 5,980 萬股（因買回）。上半年回購 259 萬股、金額 6,700 萬美元；季配息維持每股 0.05 美元。
  - **客戶集中度改善**：最大客戶 Popular, Inc. 占 Q2 營收比重由去年 31% 降至約 24%，客戶依賴風險下降。

---

## 2026-08 · YahooFinance

<!-- source-file: 202608_YahooFinance.md | bytes: 2344 | sha1: 4d409fe441c1 | merged-at: 2026-08-28 -->

### [EVTC EVERTEC] 輿情討論整理 - [Yahoo Finance] (2026/08)

- **分析時間**：2026-08-19
- **資料範圍**：過去三個月
- **來源網站**：Yahoo Finance
- **抓取方式**：內建工具（WebSearch）

---

#### 1. 焦點討論串與新聞整理

##### 🎯 獲利下滑、指引調高與買回同時發生，投資故事轉變
- **來源連結**: [Yahoo Finance — How EVERTEC's Profit Drop, Higher Guidance And Buybacks Has Changed Its Investment Story](https://finance.yahoo.com/markets/stocks/articles/evertec-profit-drop-higher-guidance-031920120.html)
- **發布時間**: 2026-08
- **核心觀點與論述**:
  > 本季呈現「營收升、淨利大幅降、指引上修、擴大買回」的複雜組合。投資人須權衡：成長來自拉美併購（正面），但短期獲利被稅務與合資減損侵蝕（負面）。
- **關鍵要點與分析**:
  - 利多：拉美擴張帶動營收動能、指引調高、買回授權擴大至 1.5 億美元。
  - 利空：有效稅率 74.7% 異常偏高、890 萬美元合資減損、利息費用上升、總負債升至 12.9 億美元。

##### 🎯 Q2 財報電話會議重點
- **來源連結**: [Yahoo Finance — Evertec Q2 Earnings Call Highlights](https://finance.yahoo.com/markets/stocks/articles/evertec-q2-earnings-call-highlights-060353298.html)
- **發布時間**: 2026-08
- **核心觀點與論述**:
  > 管理層強調拉美（尤其巴西）為成長核心，Dimensa 綜效預計 2027 年顯現；波多黎各業務維持穩定基本盤。
- **關鍵要點與分析**:
  - 分部：拉美 Payments & Solutions Q2 營收 1.229 億美元、分部調整後 EBITDA 3,970 萬美元。
  - 客戶集中度：Popular, Inc. 占比由 31% 降至約 24%。

##### 🎯 分析師評價分歧
- **來源連結**: [Yahoo Finance — Should Value Investors Buy Evertec (EVTC) Stock?](https://finance.yahoo.com/markets/stocks/articles/value-investors-buy-evertec-evtc-134003360.html)
- **發布時間**: 2026-08
- **核心觀點與論述**:
  > 部分分析師維持中性（Hold）評等；TipRanks 的 AI 分析（Spark）給予「Neutral」，指 EVTC 因財報電話會議後上修展望與穩健的基本獲利能力而評分高於平均。
- **關鍵要點與分析**:
  - 多空拉鋸：成長故事（拉美）vs. 短期獲利品質疑慮（稅務、減損、負債）。

---

## 2026-08 · 輿情新聞

<!-- source-file: 202608_輿情新聞.md | bytes: 7734 | sha1: aa27f496542b | merged-at: 2026-09-01 -->

### [EVTC EVERTEC] 輿情與新聞整理 (2026/08)

- **分析月份**：2026/08
- **資料範圍**：過去三個月（2026-06 ~ 2026-08）
- **最後更新**：2026-08-31 00:27

---

#### [Seeking Alpha & 財經媒體]

- **抓取時間**：2026-08-31
- **抓取方式**：search_web + read_url_content
- **抓取結果**：✅ 成功

##### 🎯 Q2 2026 財報發布：拉美營收強勁成長、指引上修，但一次性稅務與合資減損拖累 GAAP 淨利
- **來源連結**: [BusinessWire / Investing.com / Seeking Alpha — EVERTEC Reports Second Quarter 2026 Results](https://www.businesswire.com)
- **發布時間**: 2026-08-04
- **核心觀點與論述**:
  > Evertec 於 2026 年 8 月 4 日公布 2026 Q2 財報：單季營收達 2.748 億美元（年增 20%，按固定匯率計算約年增 16%），Adjusted EBITDA 達 1.093 億美元（年增 18%），Adjusted EPS 達 1.05 美元。然而 GAAP 歸屬於普通股東淨利為 540 萬美元（稀釋 EPS 0.09 美元），較去年同期的 4,050 萬美元（EPS 0.62 美元）大幅下滑。
- **關鍵要點與分析**:
  - **淨利下滑原因**：
    1. **稅率飆升**：為支應 Dimensa 併購案而自海外子公司調撥股利，產生額外稅負，加上資本損失提列評價備抵，導致有效稅率高達 74.7%。
    2. **合資減損**：退出一項拉美合資事業（JV），認列 890 萬美元減損損失（換算約每股衝擊 0.15 美元）。
    3. **利息費用增加**：由去年同期的 1,670 萬美元增至 2,030 萬美元。
  - **營收指引上調**：管理層將 2026 全年營收指引調高至 10.73 億至 10.85 億美元（年增率約 10%~11.2%）。

##### 🎯 Dimensa 併購綜效與拉美市場擴張
- **來源連結**: [GuruFocus / Seeking Alpha — Evertec Strategic Expansion & Dimensa Integration](https://www.gurufocus.com)
- **發布時間**: 2026-08-05
- **核心觀點與論述**:
  > 2026 年 4 月 30 日完成收購巴西金融科技 B2B 服務商 Dimensa（約 1.99 億美元），其 Q2 表現優於管理層原先預期。拉美支付與解決方案（LatAm Payments & Solutions）分部營收年增 52% 達 1.229 億美元，占總營收比例已超過 40%，成為公司最核心的成長引擎。
- **關鍵要點與分析**:
  - **新合約里程碑**：智利 Transbank 簽署多年期合作協議（預計 2027 年底起產生顯著貢獻）；墨西哥 Clip 簽訂新支付處理合約。
  - **收購與整合**：7 月 31 日收購巴西 BBChain 67% 股權；Dimensa 與 Tecnobank 在巴西的交叉銷售（Cross-selling）預計將於 2027 年顯現更強綜效。
  - **客戶集中度下降**：第一大客戶 Popular, Inc. 占營收比重從去年同期的 31% 降至約 24%，業務多元化進展良好。

---

#### [Yahoo Finance & 市場評級]

- **抓取時間**：2026-08-31
- **抓取方式**：search_web + read_url_content
- **抓取結果**：✅ 成功

##### 🎯 股票回購擴大與資本配置
- **來源連結**: [Yahoo Finance — EVERTEC Capital Allocation & Share Repurchases](https://finance.yahoo.com)
- **發布時間**: 2026-08-10
- **核心觀點與論述**:
  > 2026 上半年公司共斥資 6,700 萬美元回購 259 萬股，在外流通股數由 6,180 萬股降至約 5,980 萬股。董事會進一步批准新的股票回購授權，額度提高至 1.5 億美元，並維持每季每股 0.05 美元現金股利。
- **關鍵要點與分析**:
  - **多空觀點**：
    - **利多**：管理層透過積極買回展現對長期價值的信心，拉美營收動能充沛。
    - **利空/風險**：總負債增至約 12.9 億美元，且 6 月曾發生網路資安事件（雖未中斷營運但產生補救費用），需持續關注資安維護與償債成本。

##### 🎯 華爾街法人目標價與評級 (MarketBeat / Investing.com)
- **來源連結**: [MarketBeat / Investing.com — EVTC Analyst Ratings](https://www.marketbeat.com/stocks/NYSE/EVTC/price-target/)
- **發布時間**: 2026-08-25
- **核心觀點與論述**:
  > 截至 2026 年 8 月底，華爾街分析師對 Evertec (EVTC) 共識評級為「持有 (Hold)」，12 個月平均目標價落在 35.00 ~ 35.60 美元之間（目標價區間為 30.00 ~ 40.00 美元），相較於目前約 29~30 美元價位具備約 12%~20% 的潛在上升空間。法人普遍肯定其 Q2 營收超預期與上調全年指引，但對 GAAP 淨利下滑與短期技術面指標偏弱保持審慎態度。

---

#### [SEC 官方申報公告 (Form 8-K & Form 4)]

- **抓取時間**：2026-08-31
- **抓取方式**：sec-edgar-mcp (get_filing_content & analyze_form4_transactions)
- **抓取結果**：✅ 成功

##### 🎯 Form 8-K：5 月網路資安事件後續處理說明
- **來源連結**: [SEC EDGAR — EVTC Form 8-K (2026-06-09)](https://www.sec.gov/edgar/browse/?CIK=0001559865)
- **發布時間**: 2026-06-09
- **核心觀點與論述**:
  > 公司於 2026 年 5 月 13 日發現第三方支援平台發生潛在未授權存取客戶資料事件，主要影響波多黎各金融機構客戶之部分交易紀錄、卡號與客戶聯絡資訊。公司已立即啟動應變與修復措施，封鎖該第三方平台權限，通報執法機關，並聘請外部資安專家調查。該事件未造成營運或客戶服務中斷，但後續將產生調查與修復費用。

##### 🎯 Form 4：2026 年 8 月高層與內部人持股變動
- **來源連結**: [SEC EDGAR — EVTC Form 4 Filings](https://www.sec.gov/edgar/browse/?CIK=0001559865)
- **發布時間**: 2026-08-13 ~ 2026-08-24
- **核心觀點與論述**:
  > 2026 年 8 月公司有多筆高管與董事持股處分申報：
  > 1. **EVP & CIO Diego Viglianco**：於 2026-08-12 減持 27,570 股（均價 $30.32，金額約 83.6 萬美元），持股降至 53,102 股。
  > 2. **EVP Paola Perez-Surillo**：於 2026-08-14 減持 17,486 股（均價 $31.56，金額約 55.2 萬美元），持股降至 46,421 股。
  > 3. **Director Aldo J. Polak**：於 2026-08-11 與 08-21 合計減持 2,000 股（均價 $29.50~$29.80）。
  > 4. **Director Brian John Smith**：先前於 2026-06-12 增持 16,202 股（均價 $26.42，金額約 42.8 萬美元）。

---

#### [Reddit]

- **抓取時間**：2026-08-31
- **抓取方式**：Firecrawl search (site:reddit.com)
- **抓取結果**：✅ 成功

##### 🎯 Q2 財報發布與社群討論 (r/StockTitan & r/Quantisnow)
- **來源連結**: [Reddit r/StockTitan — EVTC Reports Second Quarter 2026 Results](https://www.reddit.com/r/StockTitan/comments/1vfle8z/evtc_evertec_reports_second_quarter_2026_results/)
- **發布時間**: 2026-08-04
- **核心觀點與論述**:
  > 社群轉發 EVTC 2026 Q2 財報發布，散戶關注單季營收達 2.748 億美元優於預期，以及全年營收指引調升至 10.85~10.95 億美元。討論焦點主要落在 Dimensa 併購後在巴西市場的整合綜效，以及波多黎各本土業務（ATH 網絡）的穩定現金流。

---

#### [股市爆料同學會 / 華語社群 (CMoney / Futu / 雪球)]

- **抓取時間**：2026-08-31
- **抓取方式**：search_web
- **抓取結果**：✅ 成功（社群標籤與個股頁面彙整）

##### 🎯 華語投資人對 EVTC 的基本面定位
- **來源連結**: [CMoney 股市爆料同學會 / 富途牛牛 EVTC 個股討論區](https://www.cmoney.tw)
- **發布時間**: 2026-08
- **核心觀點與論述**:
  > 華語社群關注 EVTC 作為波多黎各最大金融科技龍頭（ATH® 網絡運營商）的護城河，以及近年積極透過收購巴西（Dimensa、Tecnobank）、智利、墨西哥等拉美市場標的轉型為泛拉美支付巨頭的成長故事。投資人普遍認為其本益比與現金流具防禦性，但需注意匯率波動與併購商譽資產的後續表現。

---

## 2026-09 · 輿情新聞

<!-- source-file: 202609_輿情新聞.md | bytes: 8922 | sha1: 7577e0402808 | merged-at: 2026-09-17 -->

### [EVTC EVERTEC, Inc.] 輿情與新聞整理 (2026/09)

- **分析月份**：2026/09
- **資料範圍**：過去三個月 (2026-06 ~ 2026-09)
- **最後更新**：2026-09-02 12:35

---

#### [Seeking Alpha / StockTitan 財經媒體]

- **抓取時間**：2026-09-02
- **抓取方式**：search_web + 官方財報新聞交叉驗證
- **抓取結果**：✅ 成功

##### 🎯 Q2 2026 財報發布與全年財測上調 (Top-Line Acceleration & Guidance Raise)
- **來源連結**: [StockTitan EVTC Q2 2026 Earnings](https://www.stocktitan.net/news/EVTC/)
- **發布時間**: 2026-08-04
- **核心觀點與論述**:
  > "EVERTEC, Inc. reported second quarter 2026 revenue of $274.8 million, an increase of 20% compared to $229.6 million in the prior year. Adjusted EBITDA was $109.3 million, up 18%. Adjusted EPS was $1.05 compared to $0.89 in the prior year, beating consensus estimates of $0.95. GAAP net income attributable to common shareholders was $5.4 million or $0.09 per diluted share, impacted by equity investment impairment and higher tax provisions. The company increased its share repurchase authorization to $150 million and raised full year revenue and adjusted EPS guidance."
- **關鍵要點**:
  - 營收達到 2.748 億美元（年增 20%，每股營收貢獻約 4.47 美元），拉美市場擴張（年增 52%）成為主要動能。
  - 調整後 EPS 達到 1.05 美元，擊敗市場共識預估之 0.95 美元（每股超額獲利 +0.10 美元）。
  - 官方上調 2026 全年財測：營收預估 10.85 億至 10.95 億美元，調整後 EPS 預估 3.94 至 4.04 美元（中點 3.99 美元）。
  - 擴大庫藏股授權至 1.5 億美元（可執行至 2027 年底），Q2 單季透過股利與回購回饋股東 5,010 萬美元。

##### 🎯 拉美戰略版圖拓展：智利 Transbank 與墨西哥 Clip 合作協議
- **來源連結**: [StockTitan EVTC Strategic Agreements](https://www.stocktitan.net/news/EVTC/)
- **發布時間**: 2026-08-04
- **核心觀點與論述**:
  > "EVERTEC announced new strategic commercial agreements in Latin America, including partnership expansions with Transbank in Chile and Clip in Mexico, further cementing its role as a premier fintech processing enabler across the region."
- **關鍵要點**:
  - 在智利與最大收單處理商 Transbank 簽署深度戰略協議，強化收單與支付網關基礎設施。
  - 在墨西哥與領先支付獨角獸 Clip 合作，擴大雲端處理與商戶支付服務。

---

#### [X (Twitter)]

- **抓取時間**：2026-09-02
- **抓取方式**：firecrawl_search (搭配 site:x.com 運算子)
- **抓取結果**：✅ 成功

##### 🎯 市場對 Q2 財報評價：「營收加速與財測上調壓過 GAAP 會計雜訊」
- **來源連結**: [https://x.com/Finsee_main/status/2084743346984026503](https://x.com/Finsee_main/status/2084743346984026503)
- **發布時間**: 2026-08-05
- **核心觀點與論述**:
  > "EVTC Q2 2026 earnings: Top-Line Acceleration and Guidance Raise Overshadow GAAP Noise. Evertec delivered a powerful 20% revenue jump in Q2, beating adjusted EPS expectations at $1.05 vs $0.95 consensus..."
- **關鍵要點**:
  - 社群投資人指出 EVTC 核心本業（Adjusted EPS $1.05）成長強勁，拉美佔比已達 48%，正逐步擺脫單一波多黎各島內依賴。
  - 市場普遍理解 Q2 GAAP EPS $0.09 主要受非現金攤銷、一次性減損與極端有效稅率（74.7%）拖累，屬於會計性壓抑。

##### 🎯 官方資安事件後續進展聲明
- **來源連結**: [https://x.com/Evertec_Inc/status/2064327590765068798](https://x.com/Evertec_Inc/status/2064327590765068798)
- **發布時間**: 2026-06-09
- **核心觀點與論述**:
  > "On May 13, 2026, Evertec learned of unauthorized access to data maintained by an external service provider platform that we use to support customer transactions... We have taken immediate remediation steps and engaged leading cybersecurity experts."
- **關鍵要點**:
  - 公司主動說明 5 月發生的第三方支援平台資安事件，重申核心內部主系統未受直接破壞，並已強化供應商安全審查。

---

#### [Reddit 社群討論]

- **抓取時間**：2026-09-02
- **抓取方式**：firecrawl_search (site:reddit.com)
- **抓取結果**：✅ 成功

##### 🎯 波多黎各地方與員工觀點 (r/PuertoRico & r/StockTitan)
- **來源連結**: [https://www.reddit.com/r/PuertoRico/comments/1ig5mkd/](https://www.reddit.com/r/PuertoRico/comments/1ig5mkd/)
- **發布時間**: 2026-07-28
- **核心觀點與論述**:
  > "Discussions regarding Evertec's operational restructuring, moving select software and support operations to Colombia and Brazil to optimize operational expenditure while expanding Latin American footprint."
- **關鍵要點**:
  - 討論指出 EVTC 持續進行跨國營運成本優化（OPEX 整合），將部分支援後台轉移至哥倫比亞與巴西團隊，以降低波多黎各本地薪資支出並支援拉美擴張。

---

#### [雪球 Xueqiu]

- **抓取時間**：2026-09-02
- **抓取方式**：brightdata scrape_as_markdown (https://xueqiu.com/S/EVTC)
- **抓取結果**：✅ 成功

##### 🎯 雪球個股行情與財務估值指標 (2026-09-01 收盤)
- **來源連結**: [https://xueqiu.com/S/EVTC](https://xueqiu.com/S/EVTC)
- **發布時間**: 2026-09-01
- **核心觀點與論述**:
  > "Evertec(NYSE:EVTC) 收盤價 $29.16 (-1.59%)，總市值 17.42 億美元，總股本 5975.25 萬股，市盈率 TTM 約 17.86 倍，市淨率 PB 2.72 倍，每股淨資產 $10.73，股息率 TTM 0.71%，52 週區間 $21.81 - $35.41。"
- **關鍵要點**:
  - 華語圈投資人關注度相對較低（冷門價值股），目前關注球友 79 人。
  - 估值指標顯示以現價 $29.16 計算，若以 2026 預估調整後 EPS $3.99 計算，前瞻調整後市盈率（Forward Adj. PE）僅約 7.3 倍，PB 約 2.7 倍，具備深度價值特性。

---

#### [台灣與華語討論區 (PTT / CMoney)]

- **抓取時間**：2026-09-02
- **抓取方式**：內建工具 search_web
- **抓取結果**：✅ 成功（查無近三個月獨立熱門專文）

##### 🎯 查詢紀錄
- 已搜尋：PTT 股市板、CMoney 股市爆料同學會，搜尋關鍵字 `"EVTC"`、`"Evertec"`。
- 結果：近三個月內台灣散戶討論區無針對 EVTC 的獨立專文貼文（屬於美股冷門中型金融科技股）。歷史多為美股海外收入與中南美金融外包提及。

---

#### [華爾街投行與券商研究報告 (Wall Street Analyst Consensus)]

- **抓取時間**：2026-09-02
- **抓取方式**：search_web + StockAnalysis / MarketBeat 交叉比對
- **抓取結果**：✅ 成功

##### 🎯 華爾街投行評級與目標價最新動態 (2026-08 ~ 2026-09)
- **來源連結**: [https://stockanalysis.com/stocks/evtc/forecast/](https://stockanalysis.com/stocks/evtc/forecast/)
- **發布時間**: 2026-08-20
- **核心觀點與論述**:
  > "Wall Street analysts currently maintain an overall 'Moderate Buy' / 'Buy' consensus rating on EVERTEC, Inc. (NYSE: EVTC), with an average 12-month price target of $35.60 (ranging from $30.00 to $40.00). Raymond James maintains an 'Outperform' rating with a $34.00 price target, while Morgan Stanley maintains an 'Equal-Weight' rating with a $34.00 price target. Key investment theses focus on Latin America digital payments TAM expansion, recurring revenue stability from core processing, and substantial free cash flow yield."
- **關鍵要點**:
  - 平均目標價 $35.60 美元，相對現價 $29.16–$29.98 具備約 +20%~+22% 潛在上升空間。
  - 機構普遍看好拉美分部營收維持 20%+ 高速增長，推升 2027 年調整後 EPS 挑戰 $4.50 美元。

---

#### [Simply Wall St 與市場深度追蹤]

- **抓取時間**：2026-09-12
- **抓取方式**：web_search_exa + 財經新聞查證
- **抓取結果**：✅ 成功

##### 🎯 市場對獲利預期上修與低估值敘事之關注 (Rising Earnings Views & Undervalued Narrative)
- **來源連結**: [Simply Wall St EVTC Analysis](https://simplywall.st/stocks/us/diversified-financials/nyse-evtc/evertec/news/evertec-evtc-draws-fresh-attention-on-rising-earnings-views)
- **發布時間**: 2026-09-02
- **核心觀點與論述**:
  > "EVERTEC (EVTC) has drawn fresh attention on rising earnings views and an undervalued narrative, supported by positive Zacks Rank and low valuation multiples relative to industry peers. Over the past 90 days, the share price rebounded 29.2%, contrasting with a 1-year total shareholder return still down 15.8%, highlighting market reassessment of the Latin America growth trajectory."
- **關鍵要點**:
  - 市場重新定價 EVTC 獲利展望，認為拉美併購動能已從「整合陣痛期」步入「實質獲利回饋期」。
  - 2026 年 8 月 7 日正式完成對巴西區塊鏈與數位資產託管服務商 BBChain 之收購，進一步拓展巴西數位金融與資產代幣化版圖。

---

## 2026-09 · 輿情新聞 (更新)

<!-- source-file: 202609_輿情新聞.md | bytes: 28033 | sha1: 9c5ad571fe9b | merged-at: 2026-09-21 -->

### [EVTC EVERTEC, Inc.] 輿情與新聞整理 (2026/09)

- **分析月份**：2026/09
- **資料範圍**：過去三個月（2026-06-19 ~ 2026-09-19）
- **最後更新**：2026-09-19
- **說明**：本檔為 2026-09-19 排程執行（Routines_CollectsentimentAndReports 第 19 日輪值 = EVTC）之新增收集。2026-09-02 / 09-12 兩次先前收集之內容已由 ArrangePublicOpinionMd 併入 `2026_PublicOpinion.md`，本檔僅記錄本次新抓取結果，重複資訊會標註「延續前次」。

---

#### [雪球 Xueqiu]

- **抓取時間**：2026-09-19
- **抓取方式**：brightdata scrape_as_markdown（`https://xueqiu.com/S/EVTC`）
- **抓取結果**：✅ 成功

##### 🎯 股價回落與估值指標更新（2026-09-18 收盤）
- **來源連結**: [https://xueqiu.com/S/EVTC](https://xueqiu.com/S/EVTC)
- **發布時間**: 2026-09-18（美東時間收盤，雪球顯示 09-18 16:10）
- **核心觀點與論述**:
  > "Evertec(NYSE:EVTC) $27.65 -0.57 -2.02%；最高 28.14、今開 28.04、最低 27.54、昨收 28.22；成交量 125.81 萬股、換手 2.11%、成交額 3482.21 萬；52週最高 34.77、52週最低 21.81；市盈率(TTM) 16.93、市盈率(靜) 11.67、市淨率 2.58、市銷率 1.85；每股收益 1.63、每股淨資產 10.73；股息(TTM) 0.21、股息率(TTM) 0.75%；總市值 16.52 億、總股本 5975.25 萬股；79 球友關注。"
- **關鍵要點**:
  - 股價自前次收集（2026-09-01 收盤 $29.16）回落至 $27.65，約 -5.2%；52 週高點同步自 $35.41 下修為 $34.77，顯示 9 月上旬反彈動能轉弱。
  - 以官方上調後之 2026 全年調整後 EPS 指引中點 $3.99 計算，前瞻調整後本益比約 6.9 倍（$27.65 / $3.99）；GAAP 口徑市盈率(TTM) 16.93 倍、市淨率 2.58 倍。
  - **每股化**：總市值 16.52 億美元 ÷ 5975.25 萬股 ≈ 每股市值 $27.65（與收盤價一致）；每股淨資產 $10.73，故每股商譽與無形資產佔比仍高（延續併購後資產結構）。
  - 華語圈關注度依舊極低（關注球友僅 79 人），**個股討論區內全為 SEC 公告自動轉發（Form 4／144／10-Q），過去三個月無任何雪球用戶原創實質討論貼文**，屬冷門美股常態。

##### 🎯 雪球公告流反映之申報密集度（2026-08 ~ 2026-09）
- **來源連結**: [https://xueqiu.com/S/EVTC/408543806](https://xueqiu.com/S/EVTC/408543806)
- **發布時間**: 2026-09-09（雪球轉發時間）
- **核心觀點與論述**:
  > "持股變動聲明 $Evertec(EVTC)$ 4 Statement of changes in beneficial ownership of securities Accession Number: 0001778473-26-000005 Size: 4 KB"
- **關鍵要點**:
  - 雪球公告流顯示 2026-08-07 至 2026-09-09 期間共轉發 10 筆 SEC 申報，其中 **Form 4（持股變動）5 筆、Form 144（擬出售證券報告）3 筆**，其餘為 10-Q。
  - 內部人申報密度偏高，為本次觀察到的**新增風險訊號**（詳見下方 [SEC 內部人交易] 章節）。

---

#### [StockTitan 官方新聞稿彙整]

- **抓取時間**：2026-09-19
- **抓取方式**：firecrawl_scrape 失敗（額度用盡）→ 依 §2.1 遞補至 brightdata scrape_as_markdown（`https://www.stocktitan.net/news/EVTC/`）成功
- **抓取結果**：✅ 成功

##### 🎯 官方新聞稿自 2026-08-04 起「空窗」：Q2 財報後無新增重大公告
- **來源連結**: [https://www.stocktitan.net/news/EVTC/](https://www.stocktitan.net/news/EVTC/)
- **發布時間**: 頁面擷取日 2026-09-19（最新一則新聞稿為 2026-08-04）
- **核心觀點與論述**:
  > "08/04/2026 04:05 PM — EVERTEC Reports Second Quarter 2026 Results ... 07/23/2026 04:05 PM — EVERTEC Declares Quarterly Dividend on Common Stock ... 07/21/2026 04:05 PM — EVERTEC to Announce Second Quarter 2026 Financial Results on August 4, 2026"
- **關鍵要點**:
  - **StockTitan 第 1 頁最新一則官方新聞稿停在 2026-08-04（Q2 財報）**，2026-08-05 ~ 2026-09-19 共 6 週無任何新聞稿發布，屬於財報空窗期（下一個催化劑為 Q3 2026 財報，依往例約落在 2026-11 初）。
  - 頁面 FAQ 區塊同步顯示「The current stock price of EVERTEC (EVTC) is $27.65 as of September 19, 2026」、「market cap approximately 1.7B」，與雪球資料交叉相符。
  - 頁面另列 Float 58.83M（流通股 5,883 萬股）、產業歸類 Software - Infrastructure。

##### 🎯 Q2 2026 財報重點（官方新聞稿原文，延續前次收集、本次交叉驗證）
- **來源連結**: [https://www.stocktitan.net/news/EVTC/evertec-reports-second-quarter-2026-6km0sjq55g4p.html](https://www.stocktitan.net/news/EVTC/evertec-reports-second-quarter-2026-6km0sjq55g4p.html)
- **發布時間**: 2026-08-04
- **核心觀點與論述**:
  > "EVERTEC (NYSE: EVTC) reported second quarter 2026 revenue of $274.8 million, up 20% year over year, or 16% on a constant currency basis, driven by organic growth across most segments, recent acquisitions and $9.1 million of favorable foreign exchange, primarily in Brazil. GAAP net income attributable to common shareholders declined to $5.4 million, or $0.09 per diluted share, mainly due to impairment charges from exiting an equity method investment, cybersecurity response costs, acquisition-related expenses, higher depreciation and amortization, increased interest expense and higher income taxes. Adjusted EBITDA rose 18% to $109.3 million (39.8% margin) and Adjusted Net Income increased to $64.8 million, with adjusted earnings per share up 18% to $1.05. ... it repurchased 1,907,437 shares for $47.1 million and its board increased the share repurchase authorization to $150 million. Evertec raised its 2026 revenue outlook to $1.085–$1.095 billion and adjusted EPS outlook to $3.94–$4.04."
- **關鍵要點（含每股化換算，基準：總股本 5,975.25 萬股）**:
  - 營收 2.748 億美元 → **每股營收約 $4.60**；匯兌順風貢獻 910 萬美元 → **每股約 $0.15**（其中主要來自巴西幣別，屬非經常性助力）。
  - 調整後 EBITDA 1.093 億美元（利潤率 39.8%）→ **每股調整後 EBITDA 約 $1.83**。
  - 調整後淨利 6,480 萬美元 → 調整後 EPS $1.05；GAAP 淨利僅 540 萬美元 → GAAP EPS $0.09，**GAAP 與調整後每股差距高達 $0.96**，主因權益法投資退出減損、資安事件應變成本、併購費用、折舊攤銷與利息費用增加、稅負提高。
  - 單季回購 1,907,437 股、金額 4,710 萬美元 → **每股回購金額約 $0.79**，回購股數約佔總股本 3.2%（對 EPS 有實質增益）。
  - 2026 全年指引上調至營收 10.85~10.95 億美元（**每股營收約 $18.16~$18.33**）、調整後 EPS $3.94~$4.04。

##### 🎯 StockTitan 標註之股價反應（Sentiment / End-of-Day）
- **來源連結**: [https://www.stocktitan.net/news/EVTC/](https://www.stocktitan.net/news/EVTC/)
- **發布時間**: 各則新聞稿當日
- **核心觀點與論述**:
  > "EVERTEC Reports Second Quarter 2026 Results — End-of-Day -3.81%；EVERTEC Declares Quarterly Dividend — End-of-Day 2.24%；EVERTEC Reports First Quarter 2026 Results (05/06/2026) — End-of-Day -17.05%"
- **關鍵要點**:
  - **利空訊號**：Q2 財報（營收 +20%、調整後 EPS 擊敗預期、指引上調）當日股價仍收黑 -3.81%，顯示市場對「GAAP 獲利大幅萎縮 + 併購攤銷與利息墊高」的疑慮壓過營收成長故事。
  - 對照 Q1 2026 財報當日重挫 -17.05%，連續兩季財報後股價負面反應，反映市場正在重新檢視併購驅動成長的獲利品質。

---

#### [SEC EDGAR 內部人交易 Form 4／144]

- **抓取時間**：2026-09-19
- **抓取方式**：MCP `SEC EDGAR` → `get_insider_summary`、`analyze_form4_transactions`（直接讀取 SEC 原始申報）
- **抓取結果**：✅ 成功

##### 🎯【本次最重要新增訊號】高階主管密集賣股，director 卻在 6 月逆勢買進
- **來源連結**: [https://www.sec.gov/Archives/edgar/data/0001559865/000186721126000004/0001867211-26-000004.txt](https://www.sec.gov/Archives/edgar/data/0001559865/000186721126000004/0001867211-26-000004.txt)（EVP & CIO 賣出申報）
- **發布時間**: 2026-08-13（交易日 2026-08-12）
- **核心觀點與論述**:
  > SEC Form 4 原始資料：Viglianco Diego（EVP & CIO），transaction_date 2026-08-12，code `S`，shares 27,570，price_per_share $30.3217，amount $835,969，shares_owned_after 53,102。
  > Perez-Surillo Paola（Executive Vice President），transaction_date 2026-08-14，code `S`，shares 17,486，price_per_share $31.5617，amount $551,888，shares_owned_after 46,421。
  > Polak Aldo J.（Director），2026-08-11 賣 1,000 股 @ $29.50、2026-08-21 賣 1,000 股 @ $29.80、2026-08-28 賣 1,000 股 @ $30.0904、2026-09-03 賣 1,094 股 @ $30.3727，持股由 18,943 降至 14,849。
  > SMITH BRIAN JOHN（Director），2026-06-12，code `P`（公開市場買進），shares 16,202，price_per_share $26.4164，amount $427,999，shares_owned_after 88,222。
- **關鍵要點**:
  - **利空**：過去 3 個月（2026-06-19 ~ 09-19）Form 4 中**僅有賣出、無任何買進**，合計賣出 49,150 股、金額約 151.0 萬美元；**每股化：相當於每股回收約 $0.025 的內部人持股價值**（相對總股本 5,975 萬股佔比僅 0.08%，金額不大，但「方向一致」值得留意）。
  - 兩位 EVP 為**單筆大額出清**：CIO Viglianco 一次賣出 27,570 股，佔其賣前持股（80,672 股）約 34.2%；EVP Perez-Surillo 賣出 17,486 股，佔賣前持股（63,907 股）約 27.4%。兩人同期（2026-08-10 ~ 08-14）另有對應 Form 144 事前申報（券商皆為 Morgan Stanley Smith Barney），屬**已規劃出售**，但**持股比例砍掉四分之一到三分之一**仍屬偏強的負面訊號。
  - 董事 Polak 為每週固定 1,000 股的規律賣出（疑似 10b5-1 計畫），賣出價區間 $29.50~$30.37，**全部高於 2026-09-18 收盤價 $27.65**。
  - **利多（平衡觀點）**：董事 Brian John Smith 於 2026-06-12 以自有資金於公開市場**買進** 16,202 股（均價 $26.42、總額 42.8 萬美元），持股增至 88,222 股。`P` code 的公開市場買進通常被視為內部人最具訊號價值的行為，且買進價位 $26.42 接近目前股價，代表董事會層級對 $26~27 區間具支撐性看法。
  - 內部人合計僅持有全公司 1.13% 股權（MarketBeat 2026-09-15 數據），機構持股高達 96.8%，故內部人交易對籌碼面的實質衝擊有限，主要作為**訊號**解讀。

---

#### [MarketBeat／美國券商評級彙整]

- **抓取時間**：2026-09-19
- **抓取方式**：MCP `Exa` `web_search_exa`（回傳含原文摘錄之索引內容）
- **抓取結果**：✅ 成功（⚠️ 為搜尋索引之原文摘錄，非逐頁完整抓取）

##### 🎯 分析師共識回落為「Hold」，目標價 $35，與 9 月初報告口徑不同
- **來源連結**: [https://www.marketbeat.com/instant-alerts/consensus-evertec-inc-nyse-evtc-receives-consensus-rating-of-hold-from-analysts-2026-09-15/](https://www.marketbeat.com/instant-alerts/consensus-evertec-inc-nyse-evtc-receives-consensus-rating-of-hold-from-analysts-2026-09-15/)
- **發布時間**: 2026-09-15
- **核心觀點與論述**:
  > "Analysts rate Evertec 'Hold' overall: Four of six analysts recommend holding the stock, while two recommend buying it. The average 12-month price target is $35, versus a recent price of $29.23. ... Insiders sold 20,580 shares worth approximately $644,673 over the past three months, while institutional investors own 96.8% of the stock. ... Evertec stock opened at $29.23 on Tuesday. The company's fifty day moving average price is $30.08 and its two-hundred day moving average price is $28.14. Evertec has a one year low of $21.81 and a one year high of $34.76. The company has a debt-to-equity ratio of 1.89, a current ratio of 1.70 and a quick ratio of 1.70. ... price-to-earnings ratio of 18.98, a PEG ratio of 0.83 and a beta of 0.69."
- **關鍵要點**:
  - **修正前次紀錄**：9 月初收集寫的是「Moderate Buy / Buy 共識、均價 $35.60」，**2026-09-15 MarketBeat 口徑已為「Hold」共識（4 Hold / 2 Buy）、均價 $35.00**。差異來源為統計機構不同（Simply Wall St 敘事 vs MarketBeat 券商調查），閱讀時須註明出處。
  - 評級異動（2026-08）：Morgan Stanley 目標價 $34（08-06）；Wall Street Zen 由 hold 升至 buy（08-08）；**Weiss Ratings 於 08-11 由 hold (c-) 降至 sell (d+)，08-25 又調回 hold (c-)**——評級機構間分歧明顯。
  - **負債結構為主要風險項**：負債權益比（D/E）1.89、流動比率 1.70。依 AGENTS.md 負債比率公式仍需以年報總資產計算，此處僅為市場端口徑。
  - 50 日均線 $30.08、200 日均線 $28.14，**2026-09-18 收盤 $27.65 已同時跌破兩條均線**，短線技術面轉弱。

---

#### [Simply Wall St]

- **抓取時間**：2026-09-19
- **抓取方式**：MCP `Exa` `web_search_exa`（原文摘錄）
- **抓取結果**：✅ 成功

##### 🎯 9 月中旬回檔後「低估敘事」再度浮現，但本益比口徑卻顯示溢價
- **來源連結**: [https://simplywall.st/stocks/us/diversified-financials/nyse-evtc/evertec/news/evertec-evtc-following-a-recent-pullback-has-its-undervalued](https://simplywall.st/stocks/us/diversified-financials/nyse-evtc/evertec/news/evertec-evtc-following-a-recent-pullback-has-its-undervalued)
- **發布時間**: 2026-09-15
- **核心觀點與論述**:
  > "EVERTEC (EVTC) drew investor attention after its recent share move, with the price closing at $29.33. ... The 7 day share price return is down 3.36% and the 30 day move is down 7.10%, while a 90 day share price gain of 7.75% alongside a 1 year total shareholder return decline of 10.77% points to momentum that has picked up in the short run but still trails over longer periods. ... EVERTEC's most followed narrative pegs fair value at $35.60, above the latest $29.33 close. ... A simple P/E check lands in a different place. The share price trades on roughly 18x earnings, slightly above the US Diversified Financial industry at 17.6x and above a fair ratio of 17.1x. That kind of premium hints at less margin for error than the discount story suggests."
- **關鍵要點**:
  - **利多敘事**：拉美與加勒比海電商滲透率提升＋金融普惠政策擴大 TAM，支撐經常性收入成長，敘事公允價 $35.60。
  - **利空面**：同一篇文章自陳另一種算法——GAAP 本益比約 18 倍，**高於**同業 17.6 倍與「合理倍數」17.1 倍，代表以 GAAP 獲利口徑看並不便宜；「便宜」結論高度依賴使用 Adjusted EPS。
  - 風險點重申：**對 Popular, Inc. 的客戶集中度**與拉美匯率波動。
  - 動能數據：30 日 -7.10%、1 年 TSR -10.77%，即使 90 日 +7.75%，中長期仍為負報酬。

---

#### [Zacks（經 Yahoo Finance）]

- **抓取時間**：2026-09-19
- **抓取方式**：MCP `yfinance` `get_yahoo_finance_news` + MCP `Exa` 原文摘錄交叉驗證
- **抓取結果**：✅ 成功

##### 🎯【本次最重要新增利多】Zacks 於 2026-09-17 上調至 Rank #2（Buy）
- **來源連結**: [https://finance.yahoo.com/markets/stocks/articles/makes-evertec-evtc-buy-stock-160003175.html](https://finance.yahoo.com/markets/stocks/articles/makes-evertec-evtc-buy-stock-160003175.html)
- **發布時間**: 2026-09-17
- **核心觀點與論述**:
  > "Evertec (EVTC) appears an attractive pick, as it has been recently upgraded to a Zacks Rank #2 (Buy). This upgrade is essentially a reflection of an upward trend in earnings estimates... This payment processing company is expected to earn $4.00 per share for the fiscal year ending December 2026, which represents no year-over-year change. Analysts have been steadily raising their estimates for Evertec. Over the past three months, the Zacks Consensus Estimate for the company has increased 5.6%."
- **關鍵要點**:
  - **預估 EPS（Forward EPS）**：FY2026 為 $4.00（Zacks 共識），近三個月共識上修 5.6%，與公司上調後指引 $3.94~$4.04 中點一致。
  - 以 2026-09-18 收盤 $27.65 計算，**前瞻本益比約 6.9 倍**（調整後 EPS 口徑），為進入 Zacks 前 20% 估值修正族群的主因。
  - **注意口徑落差**：Zacks 之 $4.00 為 Adjusted EPS；公司同時給的 **GAAP EPS 指引僅 $1.61~$1.73**（Simply Wall St 2026-08-14 引述），兩者差距近 2.3 倍，全部來自併購攤銷、利息與一次性費用。若以 GAAP 指引中點 $1.67 計算，本益比高達約 16.6 倍。
  - Yahoo Finance 同期另有多篇 Zacks 制式價值股比較文（EVTC vs MA、EVTC vs PAYP、「Are Investors Undervaluing Evertec」），屬例行性量產內容，**依 §5.2 規則不另列為獨立輿情記錄**。

---

#### [TipRanks／法說會後續追蹤]

- **抓取時間**：2026-09-19
- **抓取方式**：MCP `Exa` `web_search_exa`（原文摘錄，含頁面 JSON-LD 之 datePublished 佐證）
- **抓取結果**：✅ 成功

##### 🎯 Q2 營運拆解與 2026 全年細項指引（含每股化）
- **來源連結**: [https://www.tipranks.com/news/company-announcements/evertec-raises-2026-outlook-amid-strong-q2-performance](https://www.tipranks.com/news/company-announcements/evertec-raises-2026-outlook-amid-strong-q2-performance)
- **發布時間**: 2026-08-04（頁面 JSON-LD `datePublished: 2026-08-04T21:15:55.000Z`）
- **核心觀點與論述**:
  > "The company returned $50.1 million to shareholders through share repurchases and dividends in the quarter, buying back 1,907,437 shares for $47.1 million at an average price of $24.68. On July 31, 2026, the board increased Evertec's share repurchase authorization to $150 million while keeping the program's expiration at December 31, 2027... Operationally, merchant acquiring benefited from higher sales volumes and improved spreads, [payments] in Puerto Rico were lifted by stronger POS activity and ATH Movil growth, and Latin America [drove] expansion, offsetting a [decline] in Business Solutions revenue... The company maintained expectations for an adjusted EBITDA margin of 39% to 40%, capital expenditures of about $90 million and an adjusted effective tax rate of 11% to 12%."
  > TipRanks AI 分析（Spark）："EVTC is a Neutral. EVTC scores above average primarily due to improved forward outlook from the earnings call... The score is tempered by financial quality risks—especially elevated leverage and weaker cash conversion—and a negative corporate event (data breach investigation)."
- **關鍵要點（每股化基準：5,975.25 萬股）**:
  - 單季股東回饋 5,010 萬美元 → **每股約 $0.84**；其中回購 4,710 萬美元均價 **$24.68**（低於目前股價 $27.65，回購時點抓得不錯，屬利多）。
  - 2026 全年資本支出指引約 9,000 萬美元 → **每股資本支出約 $1.51**，約佔每股營收（$18.16~$18.33）的 8.2%~8.3%。
  - 調整後有效稅率指引僅 11%~12%（波多黎各稅務優惠），但 Q2 GAAP 有效稅率飆升至 74.7%（前次收集紀錄），**稅率波動為 GAAP 獲利品質的重大不確定性**。
  - **分部利空**：Business Solutions 分部營收**衰退**，被商戶收單與拉美成長抵銷；若 Business Solutions（多為 Popular, Inc. 相關業務）續弱，客戶集中度風險會被放大。
  - **風險重申**：TipRanks AI 明列「槓桿偏高、現金轉換轉弱、資料外洩調查（data breach investigation）」三項負面因子，與 5 月資安事件、D/E 1.89 相互印證。

##### 🎯 Simply Wall St 2029 年長期預估（敘事基礎）
- **來源連結**: [https://simplywall.st/stocks/us/diversified-financials/nyse-evtc/evertec/news/evertec-evtc-is-up-58-after-raising-2026-revenue-outlook-and](https://simplywall.st/stocks/us/diversified-financials/nyse-evtc/evertec/news/evertec-evtc-is-up-58-after-raising-2026-revenue-outlook-and)
- **發布時間**: 2026-08-16
- **核心觀點與論述**:
  > "EVERTEC's narrative projects $[1].3 billion revenue and $234.2 [million] earnings by 2029. This requires 10.1% yearly revenue growth and about a $136.6 million earnings increase from $97.6 million today."
- **關鍵要點**:
  - 多方敘事要成立，需 2029 年達成營收 13 億美元（**每股營收約 $21.76**）、淨利 2.342 億美元（**每股盈餘約 $3.92，GAAP 口徑**）。
  - 意即：GAAP 淨利須自目前 9,760 萬美元（**每股約 $1.63**）增加 1.366 億美元，**等同三年內 GAAP 淨利要翻 2.4 倍**——這是「低估敘事」最大的執行風險所在。

---

#### [Reddit]

- **抓取時間**：2026-09-19
- **抓取結果**：❌ 失敗（依 §2.1 四條 MCP 鏈全數失敗後，改用 MCP 搜尋替代路徑取得索引結果）

##### 搜尋嘗試紀錄

- 已嘗試：內建工具 → `reddit.com` 對內建 user-agent 封鎖（§2.4 已知）。
- 已嘗試：`firecrawl`（`firecrawl_scrape` / `firecrawl_search`）→ **帳號額度用盡**，回 `Insufficient credits to perform this request`。
- 已嘗試：`brightdata scrape_as_markdown`（`old.reddit.com/search?q=EVTC`）→ 回 `Residential Failed (bad_endpoint): Requested site is not available for immediate residential (no KYC) access mode`，需完成 KYC。
- 已嘗試：`apify` `trudax/reddit-scraper-lite`（§2.9 SOP）→ 回 `Monthly usage hard limit exceeded`，**Apify 帳號本月用量已達上限**。
- 已嘗試：`playwright` `browser_navigate` → 回 `Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome`，**本環境 Playwright 瀏覽器未安裝**。
- **替代路徑（§2.1 允許）**：`brightdata search_engine`（Google `site:reddit.com Evertec EVTC 2026`）取得索引清單，另以 `Exa web_fetch_exa` 嘗試讀取貼文內文 → 回 `SOURCE_NOT_AVAILABLE`。

##### ⚠️ 索引結果（僅標題與網址為真實搜尋結果，**無法取得發文時間與內文**，依 §5.0 不臆測日期）

- [$EVTC Evertec Boosts 2026 Outlook on LatAm Acquisition Despite Plunging Profits and Cash Flow](https://www.reddit.com/r/SignalBloom/comments/1t5of1b/evtc_evertec_boosts_2026_outlook_on_latam/) — r/SignalBloom
- [EVTC | EVERTEC Reports Second Quarter 2026 Results](https://www.reddit.com/r/StockTitan/comments/1vfle8z/evtc_evertec_reports_second_quarter_2026_results/) — r/StockTitan
- [$EVTC Evertec Beats Q4 Estimates on LatAm Growth, But Declining Cash Flow and Margin Pressure Signal Risk](https://www.reddit.com/r/SignalBloom/comments/1rfmm96/evtc_evertec_beats_q4_estimates_on_latam_growth/) — r/SignalBloom
- **可觀察到的傾向（僅就標題措辭）**：r/SignalBloom 兩則標題均為「營收／展望利多，但獲利與現金流下滑」的對照句型，與本次其他來源（GAAP 獲利萎縮、現金轉換轉弱）方向一致；r/StockTitan 則為新聞稿自動轉發機器人內容，無實質討論。
- **結論**：本次無法取得 Reddit 真實貼文內文與留言，非 AI 生成，請下次重新嘗試（建議先確認 Apify 月用量重置、Firecrawl 額度、或完成 Bright Data KYC）。

---

#### [X (Twitter)]

- **抓取時間**：2026-09-19
- **抓取結果**：❌ 失敗

##### 搜尋嘗試紀錄

- 已嘗試：`firecrawl_search`（§2.4 指定之 `site:x.com` 運算子路徑，為前次 2026-09-02 成功之方法）→ **Firecrawl 額度用盡，本次不可用**。
- 已嘗試：`brightdata search_engine`（Google `site:x.com EVTC Evertec`）→ **60 秒逾時**（依 §2.5 純網路錯誤，零重試、換來源）。
- 已嘗試：`Exa web_search_exa`（查詢 X/Twitter 上 EVTC 討論）→ 回傳結果皆為財經網站（MarketChameleon、MarketBeat、Simply Wall St），**無任何 x.com 貼文**。
- **結論**：本次無法取得 X 平台真實貼文，非 AI 生成。前次（2026-09-02）已取得之 X 內容保留於 `2026_PublicOpinion.md`，本次未能更新。

---

#### [台灣／華語討論區（PTT、CMoney 股市爆料同學會、雪球討論區）]

- **抓取時間**：2026-09-19
- **抓取方式**：CMoney 官方 API（§2.8 SOP，美股端點）＋ 雪球個股頁（brightdata）＋ 搜尋引擎
- **抓取結果**：✅ 已查詢，過去三個月無符合內容

##### 🎯 查詢紀錄（依 §5「找不到也要記錄」規則）
- 雪球 `https://xueqiu.com/S/EVTC`：討論區前 10 則（2026-08-07 ~ 2026-09-09）**全為 SEC 公告自動轉發**，無用戶原創討論；關注人數僅 79 人。
- PTT 股市板 / CMoney 股市爆料同學會：搜尋關鍵字 `EVTC`、`Evertec`、`艾沃特`，**過去三個月無針對本檔之獨立討論串**。
- **推測原因**：EVTC 為市值僅約 16.5~17.5 億美元之美股中小型金融科技股，主要業務在波多黎各與拉美，台灣／中國散戶關注度極低；此情況與前次（2026-09-02）一致，屬長期結構性冷門，非抓取失敗。

---

#### [⚠️ 假訊息／錯誤報導辨識（依 AGENTS.md §6 真假消息判讀）]

- **抓取時間**：2026-09-19
- **抓取方式**：MCP `Exa` 原文摘錄 + SEC EDGAR 原始 Form 4 交叉查核
- **抓取結果**：✅ 成功辨識出 1 則內容錯誤之報導

##### 🎯 ad-hoc-news.de（2026-09-01）數據嚴重失真，切勿引用
- **來源連結**: [https://www.ad-hoc-news.de/boerse/news/nebenwerte/evertec-stock-edges-lower-after-director-share-sale-and-steady-q2-results/70039964](https://www.ad-hoc-news.de/boerse/news/nebenwerte/evertec-stock-edges-lower-after-director-share-sale-and-steady-q2-results/70039964)
- **發布時間**: 2026-09-01
- **核心觀點與論述（原文，僅供比對，內容有誤）**:
  > "Evertec stock ... has seen modest pressure after a director disclosed the sale of shares worth about USD 3,009,000, with the price around USD 29.68 as of August 31, 2026... In that quarter, Evertec generated revenue in the mid-USD 160 million range, up by about mid-single-digit percent... Net income attributable to Evertec shareholders for the second quarter of 2026 came in around the low-USD 40 million range, broadly flat compared with the prior-year quarter."
- **與官方資料比對後的錯誤點（3 項）**:
  1. **內部人賣出金額誇大 100 倍**：該文稱董事賣出約 **USD 3,009,000**；SEC Form 4（accession `0001778473-26-000004`）實為 **1,000 股 × $30.0904 = USD 30,090**。疑為小數點／千分位誤植。
  2. **Q2 營收錯誤**：該文稱「mid-USD 160 million range、年增中個位數」；官方新聞稿與 10-Q 為 **USD 274.8 million、年增 20%**。
  3. **Q2 淨利錯誤**：該文稱「low-USD 40 million range、與去年同期持平」；官方 GAAP 淨利實為 **USD 5.41 million（去年同期 40.47 million，年減 87%）**。該文疑似把「去年同期」數字誤植為本期。
- **判讀建議**：此類自動生成的德語財經聚合站內容（文中另自承插圖為 AI 生成）**不可作為 EVTC 財務數據來源**；本資料夾後續分析一律以 SEC 原始申報與公司新聞稿為準。

---

#### 本次收集小結（2026-09-19）

- **新增利多**：① Zacks 於 09-17 上調至 Rank #2（Buy），近三個月共識 EPS 上修 5.6% 至 $4.00；② 董事 Brian John Smith 於 06-12 以 $26.42 公開市場買進 16,202 股（42.8 萬美元）；③ Q2 回購均價僅 $24.68、授權額度提高至 1.5 億美元。
- **新增利空**：① 08-11 ~ 09-03 內部人**全為賣出**共 49,150 股／約 151 萬美元，兩位 EVP 單筆出清持股 27%~34%；② 股價自 09-01 的 $29.16 跌至 09-18 的 $27.65，同時跌破 50 日（$30.08）與 200 日（$28.14）均線；③ MarketBeat 09-15 共識由 Buy 口徑降為 **Hold**（4 Hold / 2 Buy）；④ Business Solutions 分部營收衰退、GAAP 與 Adjusted EPS 差距達 2.3 倍；⑤ 資安事件（data breach investigation）仍列於第三方風險評分中。
- **資料缺口**：Reddit、X 兩大英文圈社群平台本次因 MCP 工具額度／環境限制全數抓取失敗（詳見各章節嘗試紀錄）。

---
