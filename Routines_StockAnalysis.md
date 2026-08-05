/goal
使用 latest claude OPUS model

# Routines — 每日輪替執行排程 (Daily Rotation Schedule)

> 每次觸發時，依下列步驟執行；**只有 Step 3 命中才有後續動作**。

## 全域參數 (Global Parameters)

OUTPUT_FILENAME: hourAnalysisResult.md

## 執行流程 (Execution Flow)

- **Step 1**：取得今日的「日」（Day of Month，1~31）。
- **Step 2**：對照下方 `## 每日輪替表` 的 `執行日期`，鎖定今日對應的公司。
- **Step 3**：**無對應公司**→ 直接 skip 結束；**有對應公司** → 進入 Step 4。
- **Step 4**：從輪替表取出參數，搭配全域參數 `OUTPUT_FILENAME`，**載入並執行 `StockAnalysis` Skill**（`.claude/skills/StockAnalysis/SKILL.md`，內容同 `.agents/skills/StockAnalysis/SKILL.md`）。
- **Step 5**：確認 `<COMPANY_FOLDER>/<OUTPUT_FILENAME>` 已更新 → 在對話中回覆分析報告。

## Step 4 參數對照 (Parameter Mapping)

- `COMPANY_NAME` ← 輪替表 `COMPANY_NAME`
- `MARKET` ← 輪替表 `MARKET`
- `COMPANY_FOLDER` ← 輪替表 `COMPANY_FOLDER`
- `OUTPUT_FILENAME` ← 全域參數 `OUTPUT_FILENAME`（上方已設定，輪替表不重複列出）
- `EXTRA_ANALYSIS` ← 輪替表 `EXTRA_ANALYSIS`（值為「無」時留空）

---

## 每日輪替表 (Rotation Table)

- 執行日期: 1
- `COMPANY_NAME`：02318 中國平安（中股: 601318 中國平安）
- `MARKET`：港股/中股
- `COMPANY_FOLDER`：02318中國平安
- `EXTRA_ANALYSIS`：
  1. 市佔率、競爭對手
  2. 房地產曝險分析，每股化
  3. 中國平安各獲利來源佔eps的比重
  4. 如果財務數據單位是人民幣時，要轉成港幣

---

- 執行日期: 2
- `COMPANY_NAME`：00941 中國移動（中股: 600941 中國移動）
- `MARKET`：港股/中股
- `COMPANY_FOLDER`：00941中國移動
- `EXTRA_ANALYSIS`：
  1. 如果財務數據單位是人民幣時，要轉成港幣

---

- 執行日期: 3
- `COMPANY_NAME`：01426 春泉產業信託 REIT
- `MARKET`：港股
- `COMPANY_FOLDER`：01426春泉Reit
- `EXTRA_ANALYSIS`：
  1. 每股營業現金流量、每股營運現金流（FFO）、每股調整後營運現金流（AFFO）
  2. 所有財務數據都要換算成每股多少港幣
  3. 每年收的管理費用是怎麼算的，佔淨值百分比是多少?
  4. 土地使用權到期後,到時續期要每股多少錢?有什麼風險?如果無法續期，每股可拿回多少錢?

---

- 執行日期: 4
- `COMPANY_NAME`：9435 光通訊
- `MARKET`：日股
- `COMPANY_FOLDER`：9435光通訊
- `EXTRA_ANALYSIS`：
  1. 如果財報單位是美元，要換算成日元
  2. 新增/減少哪些投資標的
  3. **SBI・光 高品質價值股基金** 進度，對公司影響
  4. 業務改善處分/建議（業務改善勧告）對 EPS 影響

---

- 執行日期: 5
- `COMPANY_NAME`：3445 RS科技 及其中國子公司有研硅（688432.SH)
- `MARKET`：日股/中股
- `COMPANY_FOLDER`：3445RS
- `EXTRA_ANALYSIS`：
  1. 未來三年總產能規畫，總產能增加百分比(%)
  2. 金額需換算日幣,每股化
  3. 3445 RS科技 AND 中國子公司有研硅（688432.SH)基本面分析
  4. 中國子公司有研硅（688432.SH)近況，佔RS eps比重? 中國市占率，競爭對手分析及市占率
  5. 每股化
---

- 執行日期: 6
- `COMPANY_NAME`：7203 Toyota（美股 ADR: TM）
- `MARKET`：日股/美股
- `COMPANY_FOLDER`：7203Toyota
- `EXTRA_ANALYSIS`：
  1. 自駕車計劃？中國與特斯拉自駕車對 TM 未來 EPS 的影響？TM 有無因應計劃？
  2. 如果財務數據單位是美元時，要轉成日元
  3. 未來 2 年 EPS 預估

---

- 執行日期: 7
- `COMPANY_NAME`：UHS Universal Health Services
- `MARKET`：美股
- `COMPANY_FOLDER`：UHS
- `EXTRA_ANALYSIS`：
  1. 大而美法案（One Big Beautiful Bill Act）對 UHS 影響，EPS 會掉多少？
  2. 未來 3 年 EPS 預估

---
- 執行日期: 8
- `COMPANY_NAME`：2832 台產
- `MARKET`：台股
- `COMPANY_FOLDER`：2832台產
- `EXTRA_ANALYSIS`：
  1. 台北火車站前都更進度
  2. 承德路新總部進度
  3. IFRS 17 對 EPS 影響
  4. 未來 2~3 年 EPS 預估

---

- 執行日期: 9
- `COMPANY_NAME`：8433 弘帆
- `MARKET`：台股
- `COMPANY_FOLDER`：8433弘帆
- `EXTRA_ANALYSIS`：
  1. 未來 3 年 EPS 預估
  2. US 關稅對 EPS 影響
  3. 產線轉移到東南亞進度？效益？
  4. 越南輸美關稅對 EPS 影響
  5. 弘帆前 5 大客戶是誰？營收集中度多少？
  6. 髮飾配件 vs 小家電/電子代工之營收占比與毛利率差異？
  7. 新台幣每升值 1% 對 EPS 影響多少？（匯率敏感度）
  8. 全球髮飾/美妝配件 OEM 前 5 大競爭者市佔？弘帆護城河在哪？
  9. 自有品牌（Daylite 等）占比與毛利率 vs OEM 業務差異？
  10. 越南廠什麼時候蓋的?每股折舊多少?預估何時折舊結束?
  11. 越南廠獲利為每股多少?

---

- 執行日期: 10
- `COMPANY_NAME`：4417 金洲
- `MARKET`：台股
- `COMPANY_FOLDER`：4417金洲
- `EXTRA_ANALYSIS`：
  1. 未來三年魚網訂單預估對 EPS 影響
  2. 挪威未來 3 年訂單展望對 EPS 影響
  3. 全球前五大漁網公司市佔率
  4. 金洲前五大客戶佔營婦比重

---

- 執行日期: 11
- `COMPANY_NAME`：2881 富邦金
- `MARKET`：台股
- `COMPANY_FOLDER`：2881富邦金
- `EXTRA_ANALYSIS`：
  1. 未來 2 年 EPS 預估
  2. 最新累積 EPS

---

- 執行日期: 12
- `COMPANY_NAME`：2249 湧盛
- `MARKET`：台股
- `COMPANY_FOLDER`：2249湧盛
- `EXTRA_ANALYSIS`：
  1. 湧盛前 5 大客戶是誰？
  2. 出口比重多少？
  3. 世界市佔率多少？
  4. 全世界前五大汽車壓縮機公司市佔率？
  5. 每股化
  6. 為什麼202606營收減少40%
  7. 未來三年eps預估
  8. 上市櫃進度?市場評價


---

- 執行日期: 13
- `COMPANY_NAME`：2245 詠勝昌
- `MARKET`：台股
- `COMPANY_FOLDER`：2245詠勝昌
- `EXTRA_ANALYSIS`：
  1. 上市櫃進度

---

- 執行日期: 14
- `COMPANY_NAME`：6121 新普
- `MARKET`：台股
- `COMPANY_FOLDER`：6121新普
- `EXTRA_ANALYSIS`：
  1. 未來三年 EPS 預估
  2. 未來三年世界筆電預估銷售量
  3. AES-KY佔EPS比重?


---

- 執行日期: 15
- `COMPANY_NAME`：87001 匯賢產業信託 REIT
- `MARKET`：港股
- `COMPANY_FOLDER`：87001匯賢Reit
- `EXTRA_ANALYSIS`：
  1. 最新一期配息（人民幣）換算出來的年殖利率是多少
  2. 人民幣負債佔總負債比重（%）
  3. 港幣負債佔總負債比重（%）
  4. 港幣債務轉置成人民幣債務計劃，對配息影響
  5. 港幣債務還剩多少（單位: 人民幣）？多久可還完
  6. 所有財務數據都要換算成每股多少人民幣（e.g. 債務每股多少人民幣）
  7. 每年收的管理費用是怎麼算的，佔淨值百分比是多少?
  9. 土地使用權到期後,到時續期要每股多少錢?有什麼風險?如果無法續期，每股可拿回多少錢?

---

- 執行日期: 16
- `COMPANY_NAME`：00546 阜豐
- `MARKET`：港股
- `COMPANY_FOLDER`：00546阜豐
- `EXTRA_ANALYSIS`：
  1. 味精、蘇氨酸、賴氨酸等主要產品價格趨勢對營收與毛利率的影響
  2. 味精、蘇氨酸、賴氨酸在中國有健康疑慮嗎？有越來越少人使用嗎？

---

- 執行日期: 17
- `COMPANY_NAME`：1301 極洋
- `MARKET`：日股
- `COMPANY_FOLDER`：1301極洋
- `EXTRA_ANALYSIS`：
  1. 日圓匯率變動對水產進口採購成本與毛利率的敏感度分析
  2. 負債比率、利息支出及對淨利潤的潛在影響

---

- 執行日期: 18
- `COMPANY_NAME`：1333 Umios
- `MARKET`：日股
- `COMPANY_FOLDER`：1333Umios
- `EXTRA_ANALYSIS`：
  1. 營業利益率偏低（約 2-3%）的主因分析與改善計畫
  2. 負債比率、利息支出及對淨利潤的潛在影響

---

- 執行日期: 19
- `COMPANY_NAME`：EVTC Evertec
- `MARKET`：美股
- `COMPANY_FOLDER`：EVTC
- `EXTRA_ANALYSIS`：
  1. 收購 Sinqia 與 Dimensa 帶來的 D&A 攤銷、債務與整合成本對 GAAP EPS 的衝擊
  2. 主要客戶 Popular 續約折扣與 2026 年資安集體訴訟事件對 GAAP EPS 的影響


---

- 執行日期: 20
- `COMPANY_NAME`：1878 大東建托
- `MARKET`：日股
- `COMPANY_FOLDER`：1878大東建托
- `EXTRA_ANALYSIS`：
  1. 日本少子化與空屋率上升對公司代管業務的長期威脅及對 EPS 影響？
  2. 建築成本上漲與高負債率（約 63.6%）對利潤率及財務安全性的影響

---

- 執行日期: 21
- `COMPANY_NAME`：5306 桂盟
- `MARKET`：台股
- `COMPANY_FOLDER`：5306桂盟
- `EXTRA_ANALYSIS`：
  1. 自行車產業庫存去化進度與訂單回溫狀況對營收及毛利率的影響
  2. ECFA 早收清單若取消對 EPS 影響？中國佔 EPS 比重？

---

- 執行日期: 22
- `COMPANY_NAME`：03606 福耀玻璃（中股: 600660 福耀玻璃）
- `MARKET`：港股/中股
- `COMPANY_FOLDER`：03606福耀玻璃
- `EXTRA_ANALYSIS`：
  1. 中美貿易戰影響及對 EPS 影響
  2. AI 對玻璃需求影響

---

- 執行日期: 23
- `COMPANY_NAME`：9022 JR 東海
- `MARKET`：日股
- `COMPANY_FOLDER`：9022JR東海
- `EXTRA_ANALYSIS`：
  1. 磁浮列車（リニア中央新幹線）對未來 10 年 EPS 影響

---

- 執行日期: 24
- `COMPANY_NAME`：01378 中國宏橋
- `MARKET`：港股
- `COMPANY_FOLDER`：01378中國宏橋
- `EXTRA_ANALYSIS`：
  1. 煤炭/鋁土礦價格對毛利率影響，以及對沖情況
  2. 過去 10 年 ROE 長期偏低的原因與未來改善空間

---

- 執行日期: 25
- `COMPANY_NAME`：PBR.A 巴西石油（aka PBR；巴西 PETR3/PETR4）
- `MARKET`：美股
- `COMPANY_FOLDER`：PBR巴西石油
- `EXTRA_ANALYSIS`：
  1. PBR.A 和 PBR 價差有多少百分比？哪個比較便宜
  2. 台灣複委託買 PBR.A，配息 US 和巴西各要預扣多少 % 的稅

---

- 執行日期: 26
- `COMPANY_NAME`：6361 荏原製作所（Ebara Corp）
- `MARKET`：日股
- `COMPANY_FOLDER`：6361荏原製作所
- `EXTRA_ANALYSIS`：
  1. 半導體事業對未來 EPS 影響？
  2. 與同業比較毛利率偏低原因？
  3. 公司有什麼應對策略嗎？

---

- 執行日期: 27
- `COMPANY_NAME`：6902 Denso
- `MARKET`：日股
- `COMPANY_FOLDER`：6902Denso
- `EXTRA_ANALYSIS`：無

---

- 執行日期: 28
- `COMPANY_NAME`：6605 帝寶
- `MARKET`：台股
- `COMPANY_FOLDER`：6605帝寶
- `EXTRA_ANALYSIS`：
  1. 侵權官司進度

---

- 執行日期: 29
- `COMPANY_NAME`： `00883`  `中國海洋石油`
- `MARKET`： 港股/中股雙重上市 (600938)
- `COMPANY_FOLDER`： `00883中國海洋石油`
- `EXTRA_ANALYSIS`：
   1. 油價對eps的影響
  2. 油價損益平衡點
  3. 未来油價預估
  4. 未來三年EPS預估


---

