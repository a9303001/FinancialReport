---
name: ArrangePublicOpinionMd
description: 掃描 FinancialReport 內所有公司資料夾，將「輿情／新聞／討論區」.md 依年份合併成單一 {YYYY}_PublicOpinion.md，驗證內容完整併入後自動刪除原始零散 md。年報、季報、公司公告 report 一律不納入、不刪除。
---
/goal
# ArrangePublicOpinionMd Skill — 執行指南 (Execution Guide)

> **[Role & Objective]**
> 你是一個檔案整理 Agent。當此 Skill 啟動時，你的任務是：
> 1. 掃描每個**公司資料夾**內零散的「輿情／新聞／討論區」`.md` 檔。
> 2. 依**年份**分組，合併成同一份 `{YYYY}_PublicOpinion.md`（放在該公司資料夾內）。
> 3. **驗證**原檔內容確實已寫入彙整檔後，**刪除原始的零散 `.md`**。
> 4. 產出總結報告。
>
> **三條不可妥協的底線（The 3 Hard Rules）**
> - **① 只動輿情檔**：**年報、季報、公司公告 report 一律不納入合併、不刪除、不改名。**（見 §3 黑名單）
> - **② 先驗證再刪除**：任何原檔在「內容已確認出現在彙整檔中」之前，**絕對不可刪除**（見 §5）。
> - **③ 原文照抄**：合併時**不摘要、不改寫、不刪節**原檔內容，只做標題階層下降與加上來源註記（見 §4）。

---

## 0. 執行範圍（固定，無參數）

**本 Skill 沒有任何執行參數，也不接受切換。每次執行都是同一套行為，不要反問使用者：**

| 項目 | 固定行為 |
| :--- | :--- |
| 處理範圍 | **全部**公司資料夾 |
| `discard/` | **完全不處理**（底下的公司資料夾一律跳過） |
| 年份 | **全部**年份，一年一份彙整檔 |
| 是否實際動檔 | **實際寫檔與刪檔**（沒有 dry-run 模式） |

> 文中的 `ROOT` 一律指 FinancialReport repo 根目錄（本機 clone，Windows 通常是 `d:\FinancialReport`），不是可調整的參數。

---

## 1. 執行流程概覽 (Workflow)

| Phase | 任務 | 是否每次執行 |
| :--- | :--- | :--- |
| **Phase 0** | 前置檢查（目錄、git 狀態） | **是** |
| **Phase 1** | 掃描公司資料夾，列出所有 `.md` 候選 | **是** |
| **Phase 2** | 分類：輿情檔 / 排除檔（年報季報公告等） | **是** |
| **Phase 3** | 依年份分組 → 合併寫入 `{YYYY}_PublicOpinion.md` | 有輿情檔時 |
| **Phase 4** | 完整性驗證（逐檔比對） | **是** |
| **Phase 5** | 驗證通過才刪除原檔 | **是**（§5.1 檢查全過即刪） |
| **Phase 6** | 產生總結報告 `Log/ArrangePublicOpinionMd_Summary_{yyyyMMdd}.md` | **是** |

---

## 2. Phase 0 — 前置檢查

| 檢查項 | 通過條件 | 未通過時 |
| :--- | :--- | :--- |
| 目錄正確 | `ROOT` 底下看得到 `AGENTS.md` 與多個公司資料夾 | 立刻中止並回報路徑錯誤 |
| git 可用 | `git status` 可執行 | 仍可執行，但報告中註明「無 git 保護，刪除不可復原」 |
| 工作區乾淨 | `git status --porcelain` 無未提交的 `.md` 變更 | **先提醒使用者**：本 Skill 會刪檔，建議先提交或 stash；使用者堅持則繼續 |

### 2.1 公司資料夾判定

「公司資料夾」= `ROOT` 底下的第一層目錄，但**排除**以下非公司目錄：

```
.git  .github  .claude  .agents  Log  Prompt  AnalysisResult  StkScreenerResult  discard
```

- **`discard/` 完全不處理**：底下的公司資料夾（已淘汰的股票）一律跳過，不合併、不刪檔、不改名。
- 每個公司資料夾只掃**第一層**，不再往下遞迴。

---

## 3. Phase 2 — 檔案分類（本 Skill 的核心）

判定順序：**先黑名單 → 再白名單 → 都不中就內容判定**。**黑名單優先權最高。**

### 3.1 黑名單（命中即排除；不合併、不刪除、不改名）

#### A. 年報 / 季報 / 公司公告 report（使用者明令排除）

| 類別 | 檔名關鍵字（不分大小寫） |
| :--- | :--- |
| 年報 | `annual`、`年報`、`AnnualReport`、`有価証券報告書`、`FY20xx` |
| 半年報 / 中報 | `interim`、`中報`、`中期報告`、`半期報告書`、`_H1`、`_H2` |
| 季報 | `quarter`、`季報`、`四半期`、`Q1`/`Q2`/`Q3`/`Q4`、`10-Q`、`10Q`、`第一/二/三/四季度`、`未經審核`、`營運統計` |
| 美股申報 | `10-K`、`10K`、`20-F`、`6-K`、`8-K`、`DEF 14A` |
| 日股公告 | `決算短信`、`決算説明`、`適時開示` |
| 台股財報檔 | 檔名含 `F04`、`FE4`、`FI4`、`AI1`~`AI9`、`AIA`~`AIZ`（公開資訊觀測站財報代碼） |
| 公司公告 | `公告`、`announcement`、`股東會`、`通知書`、`notice`、`Official_IR`（IR 官方公告）、`業績公告`、`中期業績`、`年度業績` |
| 財報本體 | `財務報告`、`財報`（**但 `財報狗`／`StatementDog` 是輿情來源，不算財報**）、`financial_report`、`earnings_release`（公司自行發布的原始稿） |

#### B. 制式檔名（非輿情的機器檔）

| Regex | 說明 |
| :--- | :--- |
| `^S\d{3}[A-Z0-9]{4}\.md$` | 日本 EDINET 報告代碼檔（如 `S100T8BV.md`） |
| `^[a-z]{2,6}-\d{8}\.md$` | SEC XBRL 檔（如 `evtc-20241231.md`） |
| `^ltn\d+\.md$` | 台灣公開資訊觀測站公告檔 |
| `^\d{8,}\.md$` | 純數字公告編號（如 `2025042201223.md`） |
| `^\d{2}-[0-9A-Za-z]{2,6}-.*\.md$` | 選股排名產出檔（如 `12-5306-桂盟.md`） |
| `^\d{8}(?![_\-\d])` | 港股／台股公告檔（8 碼日期 + 中文標題，如 `20260428二零二六年第一季度未經審核營運統計.md`） |
| `(F04\|FE4\|FI4)(_\|\.)` 與 `_AI[0-9A-Z](_\|\.)` | 台股公開資訊觀測站財報代碼（如 `2025_2881_20260612F04.md`、`202601_2881_AI1.md`） |

#### C. 分析報告與系統檔（是「產出」不是「輿情」）

```
hourAnalysis*.md        *Analysis*.md          *_analysis*.md
Analysis-stock-report_*.md                     *_Summary_*.md
conversion_summary.md   README.md  index.md    prompt.md
AGENTS.md  CLAUDE.md    Routines_*.md          *_reconciliation_*.md
```

#### D. 彙整檔本身

`{YYYY}_PublicOpinion.md` 是**輸出檔**，不是輸入檔：不可被併入自己，也不可被刪除（重跑時當作 merge 目標，見 §4.4）。

舊版命名 `{YYYY}_輿情彙整.md`（本 Skill 早期版本的輸出檔）同樣視為輸出檔：**不可併入、不可刪除**，改依 §4.1 的遷移規則改名。

### 3.2 白名單（未命中黑名單，且符合任一即視為輿情檔）

| # | Regex / 條件 | 範例 |
| :--- | :--- | :--- |
| W1 | `^\d{4}(0[1-9]\|1[0-2])_.+\.md$`（`yyyyMM_來源`） | `202607_Xueqiu.md`、`202608_輿情新聞.md`、`202606_PTT.md` |
| W2 | `^\d{4}_[^\d].*\.md$`（`yyyy_來源`） | `2026_reddit.md`、`2026_news.md` |
| W3 | 檔名含 `輿情`、`新聞`、`討論`、`sentiment`、`news`、`feed` | `輿情_20260725.md`、`202607_綜合輿情_中文.md` |
| W4 | `^\d{4}-\d{2}-\d{2}.*\.md$`（單篇抓取存檔，含日期異常者） | `2026-07-04.md`、`2026-07-14_1_zh_20260715.md`、`2026-56-10.md` |
| W5 | `^_SubAgentC_feed_\d{8}_Round\d+\.md$` | `_SubAgentC_feed_20260622_Round1.md` |
| W6 | 檔名含已知輿情來源名 | `PTT`、`Dcard`、`Mobile01`、`CMoney`、`股市爆料同學會`、`財報狗`、`StatementDog`、`Reddit`、`X(Twitter)`、`SeekingAlpha`、`Motley`、`TipRanks`、`YahooFinance`、`GoogleNews`、`Xueqiu`/`雪球`、`Eastmoney`/`東方財富`、`Sina`/`新浪`、`Futu`/`富途`、`Moomoo`、`LIHKG`、`高登`、`Minkabu`、`Kabutan`、`5ch`、`Note_JP`、`Reuters`、`Nikkei`、`鉅亨`、`經濟日報`、`udn` |

> [!CAUTION]
> W1 會誤中台股財報檔（如 `202601_2881_AI1.md`、`202504_6121_AIA.md`）——這就是 §3.1-A「台股財報檔」黑名單存在的理由。**黑名單一定要先跑。**

### 3.3 灰色地帶 → 內容判定（強制）

黑白名單都沒中的檔案，**必須**讀取檔案**前 60 行 + 檔案中段 20 行**再判定：

| 判定 | 特徵字串（出現任一） |
| :--- | :--- |
| **排除**（財報/公告） | `合併財務報告`、`會計師核閱`、`會計師查核`、`資產負債表`、`綜合損益表`、`現金流量表`、`目 錄` + `頁 次`、`Form 10-K`、`Form 10-Q`、`ITEM 1. BUSINESS`、`有価証券報告書`、`四半期報告書`、`股東常會`、`董事會決議` |
| **納入**（輿情） | `輿情`、`討論`、`留言`、`網友`、`看多`、`看空`、`情緒`、`鄉民`、`貼文`、`Reddit`、`PTT`、`雪球`、`Seeking Alpha`、`來源網站`、`抓取方式`、`新聞`、`分析時間` + `資料範圍` |
| **兩者都無 / 兩者都有** | **保守處理：不納入、不刪除**，並在報告的「人工確認清單」列出檔名與判定理由 |

> 寧可漏整理，也不可誤刪財報。灰色地帶一律偏向「不動」。

### 3.4 年份判定（決定併入哪一份彙整檔）

依序嘗試，**取第一個成功者**：

| 優先序 | 來源 | Regex / 方法 | 範例 → 年份 |
| :--- | :--- | :--- | :--- |
| 1 | 檔名 `yyyyMM_` 前綴 | `^(\d{4})(?:0[1-9]\|1[0-2])_` | `202607_Xueqiu.md` → 2026 |
| 2 | 檔名 `YYYY-MM-DD` 前綴 | `^(\d{4})-\d{2}-\d{2}` | `2026-07-04.md` → 2026（日期異常如 `2026-56-10` 也取 2026） |
| 3 | 檔名內 8 碼日期 | `(20\d{2})(?:\d{4})` | `輿情_20260725.md` → 2026 |
| 4 | 檔名 `YYYY_` 前綴 | `^(\d{4})_` | `2026_reddit.md` → 2026 |
| 5 | 內容首個日期 | 內文前 40 行中的 `20\d{2}[-/年]\d{1,2}` | → 該年 |
| 6 | 檔案 mtime | 修改時間的年份 | → 該年（**必須在報告中標記「年份為推定」**） |

- 年份必須落在 `2000`–`當年+1` 之間，否則退回下一優先序。
- **不合併跨年**：2025 的輿情絕不寫進 `2026_PublicOpinion.md`。

---

## 4. Phase 3 — 合併寫入 `{YYYY}_PublicOpinion.md`

### 4.1 輸出路徑與檔名

```
{ROOT}/{公司資料夾}/{YYYY}_PublicOpinion.md
```

- 每個公司、每個年份**一份**。
- 檔名一律用**英文**：`{YYYY}_PublicOpinion.md`（超過 20 MB 才切成 `{YYYY}_PublicOpinion_part{n}.md`）。
- 該年只有 1 個輿情檔時**照樣合併**（等於正規化檔名），不要跳過。

**舊版檔名遷移（每次執行時先做）**：若資料夾內存在舊版命名 `{YYYY}_輿情彙整.md`，
1. `{YYYY}_PublicOpinion.md` **不存在** → 直接改名（`git mv "{YYYY}_輿情彙整.md" "{YYYY}_PublicOpinion.md"`），內容原封不動，之後以它為 merge 目標。
2. 兩者**都存在** → 把舊檔當成一般來源檔併入新檔（保留其 `source-file` 註記），通過 §5 驗證後才刪除舊檔。
3. 遷移結果要寫進 Phase 6 報告。

### 4.2 排序規則

同一年份內的來源檔，依「時間 → 檔名」升冪排序：
1. 先比檔名解析出的 `yyyyMM`（無月份者用 `12` 排最後，避免蓋掉月份明確的內容）。
2. 月份相同再比完整檔名（字典序）。

### 4.3 檔案結構（強制模版）

````markdown
# [{公司資料夾名稱}] {YYYY} 年 輿情彙整

> 本檔由 **ArrangePublicOpinionMd Skill** 自動彙整，內容為本資料夾 {YYYY} 年度所有「輿情／新聞／討論區」`.md` 的原文合併。
> 不含年報、季報、公司公告 report。
> 最後彙整時間：{YYYY-MM-DD HH:mm}
> 本次併入：{N} 檔｜累計併入：{M} 檔

## 目錄

- [{YYYY}-{MM} · {來源標題}](#錨點)
- ...

---

## {YYYY}-{MM} · {來源標題}

<!-- source-file: 202607_Xueqiu.md | bytes: 12345 | sha1: 8f14e45f… | merged-at: 2026-08-25 -->

{原檔內容，原文照抄}

---
````

**規則：**

| 項目 | 規則 |
| :--- | :--- |
| 章節標題 | `## {YYYY}-{MM} · {來源標題}`；`{來源標題}` 取檔名去掉日期前綴與 `.md`（如 `202607_Xueqiu.md` → `Xueqiu`）；無法解析就用完整檔名 |
| 來源註記 | 每章節第一行**必須**是 `<!-- source-file: … -->` HTML 註解，含原檔名、bytes、sha1、併入日期 —— 這是重跑去重與驗證的依據，**不可省略** |
| 標題階層 | 原檔內所有 ATX 標題（`#`…）一律**下降 2 級**（`#`→`###`、`##`→`####`…），最深不超過 `######`；**內容文字一字不改** |
| 程式碼區塊內 | 反引號區塊（``` / ~~~）**內部**的 `#` 不可當標題處理，不做階層調整 |
| 分隔線 | 每個章節結尾補一條 `---` |
| 編碼 | 一律 `utf-8`，換行統一 `\n`，檔尾保留一個換行 |

### 4.4 重跑（冪等）

彙整檔已存在時：
1. 讀出檔內所有 `<!-- source-file: {name} … -->` 的 `{name}` 集合。
2. 已在集合內的原檔 → **不重複併入**（但仍可進入 Phase 5 刪除，前提是通過 §5 驗證）。
3. 新的原檔 → **append 到檔尾**，再更新頂部的目錄與統計數字。
4. **禁止**整檔重寫覆蓋既有內容；只允許 append + 更新頭部區塊。

### 4.5 寫入安全

- 先寫暫存檔（`{YYYY}_PublicOpinion.md.tmp`）→ 確認大小 > 0 且內容可讀 → 才原子性取代正式檔 → 刪暫存檔。
- 寫入失敗 → 保留原檔、記錄錯誤、**跳過該公司的刪除步驟**，繼續下一家。

---

## 5. Phase 4/5 — 驗證與刪除（安全閘門）

### 5.1 刪除前必須全數通過的檢查

| # | 檢查項 | 不通過的動作 |
| :--- | :--- | :--- |
| C1 | 彙整檔存在且 size > 0 | 不刪任何檔 |
| C2 | 彙整檔內找得到該原檔的 `<!-- source-file: {原檔名} … -->` 註記 | 不刪該檔 |
| C3 | 原檔內容**去除所有空白與 `#` 後的前 200 個字元**，能在同樣正規化的彙整檔內容中找到（`#` 要去掉，因為 §4.3 會下降標題階層） | 不刪該檔 |
| C4 | 彙整檔 size ≥ 本次所有已併入原檔 size 總和 × 0.95 | 不刪任何檔（表示併入不完整） |
| C5 | 該檔未命中 §3.1 黑名單 | 不刪該檔（雙重保險） |

### 5.2 刪除規則（嚴格執行）

| 規則 | 說明 |
| :--- | :--- |
| ❌ 禁止萬用字元 | 刪除指令**不可**出現 `*`、`?`、`rm -rf`、`Remove-Item -Recurse`；一次一個**明確單一路徑**（相對 `ROOT` 或絕對路徑皆可） |
| ✅ 優先使用 git | repo 內用 `git rm --cached` + 檔案刪除，或直接 `git rm "<path>"`，保留可復原性 |
| ❌ 禁止刪除目錄 | 只刪 `.md` 檔，永不刪資料夾 |
| ❌ 禁止刪除非輿情檔 | 年報、季報、公告、分析報告、彙整檔本身，一律不刪 |
| ✅ 逐檔記錄 | 每刪一檔就記錄（公司、檔名、bytes、併入的彙整檔），供 Phase 6 報告 |

### 5.3 復原指引（寫進報告）

```
git checkout HEAD -- "<公司資料夾>/<被刪檔名>"
```

---

## 6. Phase 6 — 總結報告

輸出至 `{ROOT}/Log/ArrangePublicOpinionMd_Summary_{yyyyMMdd}.md`（`Log` 不存在就建立），並在最終回覆中以 Markdown 呈現摘要。

### Section 1 — 統計概覽

| 指標 | 數量 |
| :--- | :--- |
| 掃描公司資料夾數 | |
| 掃描 `.md` 總數 | |
| 判定為輿情檔 | |
| 排除：年報／季報／公告 | |
| 排除：分析報告／系統檔 | |
| 產生／更新的彙整檔數 | |
| 已刪除的原始檔數 | |
| 待人工確認（灰色地帶） | |

### Section 2 — 各公司明細

| 公司 | 年份 | 彙整檔 | 本次併入 | 已刪除 | 備註 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `2881富邦金` | 2026 | `2026_PublicOpinion.md` | 8 | 8 | — |

### Section 3 — 排除清單（要看得出「為什麼沒動它」）

| 公司 | 檔名 | 排除原因 | 命中規則 |
| :--- | :--- | :--- | :--- |
| `UHS` | `UHS_10K_2025-12-31.md` | 年報（10-K） | §3.1-A |

### Section 4 — 人工確認清單（灰色地帶）

| 公司 | 檔名 | 判定困難的原因 | 建議 |
| :--- | :--- | :--- | :--- |

### Section 5 — 錯誤與跳過

| 公司 | 檔名 | 錯誤 / 跳過原因 |
| :--- | :--- | :--- |

---

## 7. Python 參考實作（建議做法）

> 中文路徑在 Windows PowerShell/CMD 用 `python -c "…"` inline 會亂碼 —— **請寫成暫存 `.py` 檔再執行**，並全程 `encoding='utf-8'`。

````python
import hashlib, re, os, datetime
from pathlib import Path

SKIP_DIRS = {'.git', '.github', '.claude', '.agents', 'Log', 'Prompt',
             'AnalysisResult', 'StkScreenerResult', 'discard'}

def company_dirs(root: Path) -> list[Path]:
    """ROOT 底下的公司資料夾（不含 discard/，不遞迴）。"""
    return [d for d in sorted(root.iterdir())
            if d.is_dir() and d.name not in SKIP_DIRS]

BLACK_KEYWORDS = [
    'annual', '年報', 'annualreport', '有価証券報告書', 'interim', '中報', '中期報告',
    '半期報告書', 'quarter', '季報', '四半期', '決算短信', '決算説明', '適時開示',
    '10-k', '10k', '10-q', '10q', '20-f', '6-k', '8-k', '公告', 'announcement',
    '股東會', '通知書', 'notice', 'official_ir', '財務報告', 'earnings_release',
    '第一季度', '第二季度', '第三季度', '第四季度', '未經審核', '營運統計',
    '業績公告', '中期業績', '年度業績',
]
BLACK_REGEX = [
    r'財報(?!狗)',                        # 「財報狗 / StatementDog」是輿情來源，不可誤殺
    r'_H[12](_|\.)',                     # 半年報
    r'^S\d{3}[A-Z0-9]{4}\.md$',          # EDINET
    r'^[a-z]{2,6}-\d{8}\.md$',           # SEC XBRL
    r'^ltn\d+\.md$',                     # 公開資訊觀測站公告
    r'^\d{8,}\.md$',                     # 純數字公告編號
    r'^\d{8}(?![_\-\d])',                # 8 碼日期 + 中文標題的港股/台股公告
    r'^\d{2}-[0-9A-Za-z]{2,6}-.*\.md$',  # 選股排名產出
    r'(F04|FE4|FI4)(_|\.)',              # 台股財報代碼
    r'_AI[0-9A-Z](_|\.)',                # 台股財報 AI 系列
    r'[Qq][1-4]',                        # 季度
    r'(?i)houranalysis|analysis|_summary_|conversion_summary',
    r'^\d{4}_PublicOpinion(_part\d+)?\.md$',   # 輸出檔本身
    r'^\d{4}_輿情彙整(_part\d+)?\.md$',        # 舊版輸出檔（見 §4.1 遷移規則）
]
WHITE_REGEX = [
    r'^\d{4}(0[1-9]|1[0-2])_.+\.md$',
    r'^\d{4}_[^\d].*\.md$',
    r'^\d{4}-\d{2}-\d{2}.*\.md$',
    r'^_SubAgentC_feed_\d{8}_Round\d+\.md$',
    r'(?i)輿情|新聞|討論|sentiment|news|feed',
]
SOURCE_NAMES = [  # §3.2 W6，可持續擴充
    'PTT', 'Dcard', 'Mobile01', 'CMoney', '股市爆料', '財報狗', 'StatementDog',
    'Reddit', 'Twitter', 'SeekingAlpha', 'Motley', 'TipRanks', 'YahooFinance',
    'Yahoo_Finance', 'GoogleNews', 'Xueqiu', '雪球', 'Eastmoney', '東方財富',
    'Guba', 'Sina', '新浪', 'Futu', '富途', 'Moomoo', 'LIHKG', '高登', 'HKEJ',
    'HKET', 'HK01', 'Minkabu', 'Kabutan', '5ch', 'note', 'Reuters', 'Nikkei',
    'Bloomberg', 'Investing', 'MarketBeat', 'StockTitan', 'MoneyDJ', 'Cnyes',
    '鉅亨', '經濟日報', 'udn', 'anue', 'BigGo',
]

def is_black(name: str) -> bool:
    low = name.lower()
    if any(k in low for k in BLACK_KEYWORDS):
        return True
    return any(re.search(p, name) for p in BLACK_REGEX)

def is_white(name: str) -> bool:
    if any(re.search(p, name) for p in WHITE_REGEX):
        return True
    low = name.lower()
    return any(s.lower() in low for s in SOURCE_NAMES)

def year_of(path: Path) -> tuple[int | None, str]:
    n = path.name
    for pat, tag in [(r'^(\d{4})(?:0[1-9]|1[0-2])_', 'yyyyMM'),
                     (r'^(\d{4})-\d{2}-\d{2}', 'yyyy-mm-dd'),
                     (r'(20\d{2})\d{4}', 'yyyymmdd'),
                     (r'^(\d{4})_', 'yyyy_')]:
        m = re.search(pat, n)
        if m and 2000 <= int(m.group(1)) <= datetime.date.today().year + 1:
            return int(m.group(1)), tag
    head = path.read_text(encoding='utf-8', errors='ignore')[:4000]
    m = re.search(r'(20\d{2})[-/年]\d{1,2}', head)
    if m:
        return int(m.group(1)), 'content'
    return datetime.date.fromtimestamp(path.stat().st_mtime).year, 'mtime(推定)'

def demote_headings(text: str, levels: int = 2) -> str:
    out, in_fence = [], False
    for line in text.split('\n'):
        if re.match(r'^\s*(```|~~~)', line):
            in_fence = not in_fence
        if not in_fence:
            m = re.match(r'^(#{1,6})(\s)', line)
            if m:
                line = '#' * min(6, len(m.group(1)) + levels) + line[len(m.group(1)):]
        out.append(line)
    return '\n'.join(out)

def section(src: Path, ym: str, title: str) -> str:
    raw = src.read_text(encoding='utf-8', errors='ignore')
    sha = hashlib.sha1(raw.encode('utf-8')).hexdigest()[:12]
    today = datetime.date.today().isoformat()
    meta = (f'<!-- source-file: {src.name} | bytes: {src.stat().st_size} '
            f'| sha1: {sha} | merged-at: {today} -->')
    return f'\n## {ym} · {title}\n\n{meta}\n\n{demote_headings(raw).strip()}\n\n---\n'

def already_merged(merged: Path) -> set[str]:
    if not merged.exists():
        return set()
    body = merged.read_text(encoding='utf-8', errors='ignore')
    return set(re.findall(r'<!-- source-file: (.+?) \|', body))

def _norm(t: str) -> str:
    # 去掉空白與 ATX 標題的 '#'，因為合併時標題階層會下降（§4.3）
    return re.sub(r'[#\s]+', '', t)

def verify(merged_text: str, src_text: str, src_name: str) -> bool:
    if f'source-file: {src_name} |' not in merged_text:      # C2
        return False
    probe = _norm(src_text)[:200]                            # C3
    return bool(probe) and probe in _norm(merged_text)
````

刪除（通過 §5.1 全部檢查後，逐檔執行，路徑寫全）：

```bash
git rm "2881富邦金/202607_PTT.md"
```

```powershell
git rm "d:\FinancialReport\2881富邦金\202607_PTT.md"
```

---

## 8. 異常處理

| 情況 | 動作 |
| :--- | :--- |
| 單一檔案讀取失敗（編碼、權限） | 記錄 → **跳過該檔**（不刪）→ 繼續下一檔 |
| 彙整檔寫入失敗 | 記錄 → **該公司該年度完全不刪檔** → 繼續下一家 |
| 年份無法判定 | 用 mtime 推定並標記；若 mtime 也異常 → 列入人工確認清單，不動該檔 |
| 檔案內容為空（0 bytes） | 不併入；列入報告的「空檔清單」，**不自動刪除** |
| 同年份輿情檔 > 200 個 | 照樣合併；若彙整檔超過 20 MB，改切成 `{YYYY}_PublicOpinion_part{n}.md`，並在 part1 頂部列出所有 part |
| 使用者中途中斷 | 已寫入的彙整檔保留；未驗證的原檔一律不刪 |

---

## 9. 完成後

1. 在最終回覆中呈現 §6 的統計概覽與各公司明細（中文）。
2. 明確回報：**產生幾份彙整檔、刪了幾個原檔、哪些被排除（年報／季報／公告）、哪些需要人工確認**。
3. 若在 git repo 內，提交變更（訊息如 `chore: 合併各公司輿情 md 為年度彙整檔`），**推送分支依使用者指示**，不要自行推 `master`。
