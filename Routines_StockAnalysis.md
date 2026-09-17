/goal

# Routines — StockAnalysis 每日輪替執行排程

> **一句話任務**：依「今天是幾號」從輪替表取出當日公司，執行「深度分析 → 驗收 → 交付」。
>
> **唯一輸出檔**：`<COMPANY_FOLDER>/hourAnalysisResult.md`（Claude、Gemini 或任何執行者共用同一份，不再依模型分檔）。
>
> **只有 Step 1 命中才有後續動作**：輪替表當日無對應公司 → 直接 skip 結束。
>
> **執行模式**：`/goal` 全自動，不中途停下向使用者提問；遇錯記錄後繼續，走完 Step 0 → Step 5。

---

## 🚨 不可違反規則（Invariants）

| # | 規則 | 違反後果 |
|:-:|:-----|:---------|
| 1 | **單輪單日**：每次啟動只做**今天這一個執行日期**的所有公司（同一日期可能有多間，全部做完才收工） | 跨日會導致進度混亂 |
| 2 | **零阻塞**：遇到任何錯誤（逾時、被擋、API 額度用盡）→ 記錄後繼續，不停下等人 | 停下 = 任務失敗 |
| 3 | **繁體中文**輸出（專有名詞首次出現附英文，如「每股盈餘（EPS）」） | — |
| 4 | **防幻覺**：所有財務數據必須有來源佐證，**嚴禁用訓練資料捏造** | 捏造 = 任務失敗 |
| 5 | **本地優先**：財報／輿情直接讀 `<REPO_ROOT>/<COMPANY_FOLDER>/`，不重複從線上倉庫下載 | — |
| 6 | **整份重寫**：交付前必須對輸出檔執行 SKILL.md §7 Final Rewrite，且第一行為**真實系統時間戳** | 流水帳 = 任務失敗 |

> `<REPO_ROOT>` = FinancialReport repo 根目錄（Windows 本機通常為 `d:\FinancialReport`）。

---

## 全域參數 (Global Parameters)

| 參數 | 值 | 說明 |
|:-----|:---|:-----|
| `SKILL_PATH` | `.claude/skills/StockAnalysis/SKILL.md` | 內容同 `.agents/skills/StockAnalysis/SKILL.md` |
| `ROTATION_TABLE` | 本檔「## 每日輪替表」 | 唯一真實依據（Single Source of Truth） |
| `TIMEZONE` | `Asia/Taipei (UTC+8)` | 取日期與時間戳一律用此時區 |

> **輸出檔固定為 `<COMPANY_FOLDER>/hourAnalysisResult.md`**，不接受其他檔名；SKILL.md 中的 `<OUTPUT_FILENAME>` 一律代入此固定值。

---

## 執行流程 (Execution Flow)

```
Step 0  取今日日期（UTC+8）＋ git pull 同步
  ↓
Step 1  讀輪替表 → 鎖定今日對應公司（可能多間）
  ↓
Step 2  無對應公司 → skip 結束；有對應 → 前置盤點
  ↓
Step 3  逐間執行 StockAnalysis Skill（深度分析 → Final Rewrite）
  ↓
Step 4  驗收：交付檢查（不過 → 就地修正後重跑本步）
  ↓
Step 5  交付：commit & push（依當前環境的分支規範）
  ↓
  ✅ 輸出精簡摘要 + 在對話中回覆分析報告
```

### Step 0 — 取日期與同步

1. 取得今日的「日」（Day of Month，1~31），必須**實際執行指令**取系統時間，嚴禁憑印象：
   ```bash
   TZ=Asia/Taipei date "+%Y/%m/%d %H:%M:%S"      # Linux / macOS
   ```
   ```powershell
   Get-Date -Format "yyyy/MM/dd HH:mm:ss"        # Windows PowerShell
   ```
2. `git pull` 同步最新資料；衝突則 `git stash` → `pull` → `stash pop`；網路失敗重試最多 3 次（間隔 2s / 4s / 8s），仍失敗則記錄後**繼續**。

### Step 1 — 鎖定今日公司

- 對照「## 每日輪替表」的 `執行日期`，取出所有符合今日日期的列（**同一日期可能有多間公司，必須全部做完**）。
- 輪替表只涵蓋 1~30；日期 31 無對應公司。

### Step 2 — 判斷 + 前置盤點（Pre-flight）

- **無對應公司** → 直接 skip 結束（不寫檔、不 commit）。
- **有對應公司** → 每間做一次 30 秒快速盤點：

| # | 檢查 | 做法 | 缺了怎麼辦（零阻塞） |
|:-:|:-----|:-----|:---------------------|
| 1 | 公司資料夾存在？ | 列出 `<REPO_ROOT>/<COMPANY_FOLDER>/` | 不存在 → 建立空資料夾，記「本地無資料，全靠 deep research」 |
| 2 | 年報／季報 md 齊全？ | 找 `*_AnnualReport_*.md`、`*_Quarter_*.md` | 缺 → 照樣分析，並在輸出檔附錄寫明缺哪一期與可能原因 |
| 3 | 輿情檔存在？ | 找 `{yyyy}_PublicOpinion.md`、`{yyyyMM}_輿情新聞.md` | 缺 → 改用 web search 補足並記錄 |
| 4 | 上一版報告存在？ | 找 `hourAnalysisResult.md` | 不存在 → 視為**首輪**全新產出 |

### Step 3 — 執行 StockAnalysis Skill

從輪替表取出參數，搭配全域參數，**載入並執行 `StockAnalysis` Skill**（`SKILL_PATH`）。

#### Step 3 參數對照 (Parameter Mapping)

| StockAnalysis 參數 | 值的來源 | 範例 |
|:---|:---|:---|
| `COMPANY_NAME` | 輪替表 `COMPANY_NAME` | `02318 中國平安` |
| `MARKET` | 輪替表 `MARKET` | `港股/中股` |
| `COMPANY_FOLDER` | 輪替表 `COMPANY_FOLDER` | `02318中國平安` |
| `EXTRA_ANALYSIS` | 輪替表 `EXTRA_ANALYSIS`（值為「無」時留空） | `房地產曝險分析，每股化…` |

> 輸出寫入路徑固定為 `<REPO_ROOT>/<COMPANY_FOLDER>/hourAnalysisResult.md`（直接覆寫，不加日期後綴）。

#### 全程核心要求（細節見 SKILL.md 對應章節）

| 要求 | 依據 |
|:-----|:-----|
| 頭部優先（最重要 × 最新放最前面） | §4.1、§4.5 |
| 七大基本面支柱全覆蓋 | §3.1.1 |
| 所有金額**每股化** + 每股化總表 | §4.3、§7.2 |
| 主要幣別正確（港股／中股用 HKD） | §4.6 |
| 同步套用 @AGENTS.md 的「個股分析規則」（REIT 另加「REIT分析規則」） | §1 |
| 寫給初級分析師看（說人話、術語寫英文、不做 Glossary） | §5 |
| 表格只給純數據；檔頭資訊卡／多空對照／extra 問題／輿情用 key-value 條列 | §4.7 |
| 交付前**整份重寫**（Final Rewrite） | §7 |
| 第一行為**真實系統時間戳** `yyyy/MM/dd HH:mm:ss (UTC+8)` | §4.2 第 0 項 |

### Step 4 — 驗收（Acceptance · 不過就修，修完重跑本步）

#### 交付檢查（Definition of Done）

- [ ] `<COMPANY_FOLDER>/hourAnalysisResult.md` 已更新，且**第一行**是本輪真實系統時間戳（`yyyy/MM/dd HH:mm:ss (UTC+8)`）
- [ ] 已完成 SKILL.md §7 Final Rewrite（整份重寫，非局部補丁、非新舊堆疊）
- [ ] 通過 §7.6 Final Rewrite Checklist（A 結構／B 每股化／C 汰除／D 基本面與幣別）
- [ ] 通過 §5.5 可讀性 checklist 與 §4.5.4 頭部檢查三題
- [ ] `EXTRA_ANALYSIS` 每一項都有對應段落與數字（查不到的要寫明原因）
- [ ] 版面符合 §4.7：**表格只用在純數據**；檔頭資訊卡、多空對照（詳細版）、`EXTRA_ANALYSIS` 問題、跨國輿情彙整都是 **key-value 條列**
- [ ] 今日每間公司都做完（多公司日期不可漏）

> 任一項不過 → **就地修正後重跑 Step 4**，通過才進 Step 5。

### Step 5 — 交付（Commit & Push）

```bash
git add -A
git commit -m "StockAnalysis: 執行日期 {今日} - {公司清單}"
```

- **推送分支依當前環境規範**：Claude Code 於指定 feature 分支開發時 push 該分支並開 PR；本機直跑時 push `master`。
- 被拒絕（non-fast-forward）：`git pull --rebase` 後重推；網路失敗重試最多 4 次（間隔 2s / 4s / 8s / 16s）。
- （選配）寫執行日誌 `Log/hourAnalysis_Summary_{yyyyMMdd}.md`：本輪公司、成功／失敗、資料缺口。

---

## 錯誤處理（零阻塞 Playbook）

| 狀況 | 處置 |
|:-----|:-----|
| 網路搜尋被擋／逾時 | 換來源或升級工具鏈（內建 → Firecrawl → Bright Data → Apify → Playwright），全失敗就誠實寫「查無」 |
| MCP API 額度用盡 | 記錄後改用原生工具，繼續 |
| 本地無年報／季報 | 照樣分析，缺口寫進輸出檔附錄 |
| 某公司整段失敗 | 標 ❌ 記錄原因，**繼續下一間**，不可中斷全輪 |
| git pull／push 失敗 | 依 Step 0 / Step 5 的重試規則，仍失敗則記錄錯誤並在摘要標 ❌ |

---

## 最終 Chat 回覆格式

Step 0 ~ 5 完成後，先輸出精簡摘要，再附上本輪分析報告重點：

```
✅ StockAnalysis — YYYY-MM-DD HH:MM
- 本輪：執行日期 {N}（{公司名稱}）
- 分析：✅ 成功（hourAnalysisResult.md）
- Git：✅ 已 push {分支}
- 下一輪：執行日期 {N+1}（{下輪公司}）
```

---

## 每日輪替表 (Rotation Table)

- 執行日期: 1
- `COMPANY_NAME`：02318 中國平安（中股: 601318 中國平安）
- `MARKET`：港股/中股
- `COMPANY_FOLDER`：02318中國平安
- `EXTRA_ANALYSIS`：
  1. 市佔率、競爭對手
  2. 房地產曝險分析，每股化
  3. 中國平安各獲利來源佔 EPS 的比重
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
  3. 每年收的管理費用是怎麼算的，佔淨值百分比是多少？
  4. 土地使用權到期後，到時續期要每股多少錢？有什麼風險？如果無法續期，每股可拿回多少錢？
  5. 預期何時 EPS 可以回正？

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
- `COMPANY_NAME`：3445 RS科技 及其中國子公司有研硅（688432.SH）
- `MARKET`：日股/中股
- `COMPANY_FOLDER`：3445RS
- `EXTRA_ANALYSIS`：
  1. 未來三年總產能規畫，總產能增加百分比(%)
  2. 金額需換算日幣，每股化
  3. 3445 RS科技 AND 中國子公司有研硅（688432.SH）基本面分析
  4. 中國子公司有研硅（688432.SH）近況，佔 RS EPS 比重？中國市占率，競爭對手分析及市占率
  5. 每股化

---

- 執行日期: 6
- `COMPANY_NAME`：7203 Toyota（美股 ADR: TM）
- `MARKET`：日股/美股
- `COMPANY_FOLDER`：7203Toyota
- `EXTRA_ANALYSIS`：
  1. 自駕車計劃？中國與特斯拉自駕車對 TM 未來 EPS 的影響？TM 有無因應計劃？
  2. 美國關稅對 EPS 影響？關稅稅率是多少？
  3. 每股日元化
  4. 未來 2 年 EPS 預估

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
  1. 台北火車站前館前路都更完會貢獻多少eps
  2. 承德路新總部進度
  3. 未來 3 年 EPS 預估

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
  8. 自有品牌（Daylite 等）占比與毛利率 vs OEM 業務差異？
  9. 越南廠什麼時候蓋的？每股折舊多少？預估何時折舊結束？
  10. 越南廠獲利為每股多少？

---

- 執行日期: 10
- `COMPANY_NAME`：4417 金洲
- `MARKET`：台股
- `COMPANY_FOLDER`：4417金洲
- `EXTRA_ANALYSIS`：
  1. 未來三年魚網訂單預估對 EPS 影響
  2. 挪威未來 3 年訂單展望對 EPS 影響

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
  4. 每股化
  5. 為什麼 202606 營收減少 40%
  6. 未來三年 EPS 預估
  7. 上市櫃進度？市場評價

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
  3. AES-KY 佔 EPS 比重？

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
  7. 每年收的管理費用是怎麼算的，佔淨值百分比是多少？
  8. 土地使用權到期後，到時續期要每股多少錢？有什麼風險？如果無法續期，每股可拿回多少錢？
  9. 預期何時 EPS 可以回正？

---

- 執行日期: 16
- `COMPANY_NAME`：00546 阜豐
- `MARKET`：港股
- `COMPANY_FOLDER`：00546阜豐
- `EXTRA_ANALYSIS`：
  1. 有哪些產品，各佔 EPS 比重
  2. 各產品的主要競爭對手，市佔率

---

- 執行日期: 17
- `COMPANY_NAME`：8117 中央自動車工業
- `MARKET`：日股
- `COMPANY_FOLDER`：8117中央自動車工業
- `EXTRA_ANALYSIS`：
N/A

---

- 執行日期: 18
- `COMPANY_NAME`：CF
- `MARKET`：美股
- `COMPANY_FOLDER`：CF
- `EXTRA_ANALYSIS`：無

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
- `COMPANY_NAME`：4979 OAT
- `MARKET`：日股
- `COMPANY_FOLDER`：4979OAT
- `EXTRA_ANALYSIS`：
  1. 各產品市占率？
  2. 各產品各提供多少 EPS
  3. 競爭對手
  4. 國際和日本市占率
  5. 產品銷往哪些國家？比重？
  6. 各國市占率？
  7. 前五大客戶？都是哪些國家
  8. 綠色商品是指什麼？
  9. 有什麼投資風險嗎？
  10. 輿情對 4979 OAT 產品的評價，優缺點

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
  1. 未來 5 年產能規畫，對 EPS 影響
  2. AI 自駕車對玻璃需求影響？對 EPS 影響？
  3. 每股化，港幣

---

- 執行日期: 23
- `COMPANY_NAME`：01816 中廣核電力 / 中股雙重上市 (003816)
- `MARKET`：港股
- `COMPANY_FOLDER`：01816中廣核電力
- `EXTRA_ANALYSIS`：
  1. 未來 10 年每年新增核電機組，每機組貢獻多少 EPS
  2. 未來 10 年 EPS 預估
  3. 未來 10 年每股配息預估
  4. 每股化，港幣

---

- 執行日期: 24
- `COMPANY_NAME`：02232晶苑國際
- `MARKET`：港股
- `COMPANY_FOLDER`：02232晶苑國際
- `EXTRA_ANALYSIS`：n/a

---

- 執行日期: 25
- `COMPANY_NAME`：01866中國心連心化肥
- `MARKET`：港股
- `COMPANY_FOLDER`：01866中國心連心化肥
- `EXTRA_ANALYSIS`：

---

- 執行日期: 26
- `COMPANY_NAME`：1264 德麥
- `MARKET`：台股
- `COMPANY_FOLDER`：1264德麥
- `EXTRA_ANALYSIS`：無

---

- 執行日期: 27
- `COMPANY_NAME`：8435 鉅邁
- `MARKET`：台股
- `COMPANY_FOLDER`：8435鉅邁
- `EXTRA_ANALYSIS`：

---

- 執行日期: 28
- `COMPANY_NAME`：01044 恒安國際 /美國adr HEGIY
- `MARKET`港股
- `COMPANY_FOLDER`：01044恒安國際
- `EXTRA_ANALYSIS`：
1. 七度空间：卫生巾評價，有什麼缺評嗎？
2. 心相印：生活用纸評價，有什麼缺評嗎？
3. 安儿乐/Q·MO：婴儿纸尿裤品評價，有什麼缺評嗎？
4. 

---

- 執行日期: 29
- `COMPANY_NAME`：`00883` `中國海洋石油`
- `MARKET`：港股/中股雙重上市 (600938)
- `COMPANY_FOLDER`：`00883中國海洋石油`
- `EXTRA_ANALYSIS`：
  1. 油價對 EPS 的影響
  2. 油價 50 美元，預估 EPS 多少
  3. 油價損益平衡點
  4. 未來油價預估
  5. 未來三年 EPS 預估
  6. 與 00857 中石油、00386 中石化兩家公司比較投資價值

---

- 執行日期: 30
- `COMPANY_NAME`：`02633` `雅各臣科研製藥`
- `MARKET`：港股
- `COMPANY_FOLDER`：`02633雅各臣科研製藥`
- `EXTRA_ANALYSIS`：
1. 為什麼pe這麼低
2. 競爭對手有誰???市佔率???
3. 提供學名藥嗎???為什麼香港市佔率這麼高???沒人跟他搶市場嗎????
4. 香港有健保嗎????是怎麼跟雅各臣科研製藥買藥????為什麼只跟他買

---
