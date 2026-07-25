# 任務執行最終報告 - 2026/07/25

- **輪替標的**：Day 25 → `PBR.A` 巴西石油（Petróleo Brasileiro S.A. — Petrobras）
- **市場**：美股 ADR（PBR 普通股 / PBR.A 優先股）；巴西 B3：PETR3 / PETR4
- **本地資料夾**：`PBR巴西石油/`（沿用既有資料夾，未另建 `PBR.A 巴西石油` 以免重複）
- **執行架構**：主代理人負責 Phase 1/4/5；財報下載（Phase 2）與輿情收集（Phase 3）各由一個獨立子代理人平行執行。

---

## 1. 成功紀錄

### 財報（Phase 2 下載 → Phase 4 轉換）
| 股號/名稱 | 資料來源 | 產生的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `PBR.A 巴西石油` | Petrobras IR（petrobras.com.br / api.mziq.com）；經 SEC EDGAR CIK 0001119639 交叉確認 | `PBR.A_AnnualReport_2025.md` | 20-F FY2025（截至 2025-12-31，SEC 2026-04-09 申報）；markitdown 轉換，cid=0，1.34M 字 |
| `PBR.A 巴西石油` | Petrobras IR CDN | `PBR.A_AnnualReport_2024.md` | 20-F FY2024；markitdown 轉換，cid=0，1.38M 字 |
| `PBR.A 巴西石油` | Petrobras IR Results Center（Financial Statements in US$） | `PBR.A_Quarter_2026Q1.md` | 2026 Q1 未經審計合併期中財報（截至 2026-03-31，含會計師覆核報告）；14.4 萬字 |

> 最新季度為 **2026 Q1**（2026-05-11 發布）。2026 Q2 尚未公布（Petrobras 通常 8 月初發布），與今日 2026-07-25 相符。

### 輿情/新聞（Phase 3，過去三個月，全部為真實抓取內容）
| 股號/名稱 | 資料來源 | 產生的檔案 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `PBR.A 巴西石油` | Seeking Alpha | `202607_SeekingAlpha.md` | 3 篇分析（2 多 / 1 中性偏空）+ 官方新聞連結 |
| `PBR.A 巴西石油` | Reddit（r/dividends、r/stocks） | `202607_Reddit.md` | 2 主帖（1 三月內 + 1 邊界 4mo） |
| `PBR.A 巴西石油` | 雪球 Xueqiu | `202607_Xueqiu.md` | 3 討論帖 + 6 則官方快訊 |
| `PBR.A 巴西石油` | TradingView / Zacks | `202607_TradingViewZacks.md` | Zacks Rank #1 深度分析 + 2 佐證 |
| `PBR.A 巴西石油` | Investing.com | `202607_Investing.md` | 巴股高息結構性專欄 |
| `PBR.A 巴西石油` | Quiver Quantitative | `202607_QuiverQuant.md` | 油價 beta 事件 + 5 分析師目標價 + 機構/內部人 |
| `PBR.A 巴西石油` | MarketBeat | `202607_MarketBeat.md` | 分析師共識（Moderate Buy）+ 7 家機構 13F 動向 |

---

## 2. 失敗或被擋網站
- **雪球 `xueqiu.com/S/PBR`**：brightdata scrape_as_markdown 連續 2 次 60s 逾時 → 改以 firecrawl 抓 `/S/PBR/hots` 成功（該來源整體視為成功）。
- **新浪財經 PBR 頁**：brightdata 抓取回傳 GBK 編碼亂碼，無法擷取內文（已於 Xueqiu 檔註記，改以雪球快訊取得官方事件）。
- **X (Twitter) / Yahoo Finance conversations**：firecrawl news 搜尋未回傳實質貼文；因已達 7 個實質來源、基於時間效益未再逐一跑 apify/playwright。若日後需補，可針對此兩者單獨執行 playwright。

## 3. 資料缺失說明
- 2026 Q2 季報尚未發布（Petrobras 慣例 8 月初公布），故季報以最新 2026 Q1 為準。
- 財報來源全數取得英文版，無資料缺口。

## 4. 異常檔案刪除紀錄
- **PDF 來源檔**：3 份原始 PDF（2025/2024 年報、2026Q1 季報）於轉換成功後依 Convert2md Phase 1.4 規則刪除，僅保留 `.md`。
- **markitdown 轉換 CID 失敗 → 改用 pymupdf**：`PBR.A_Quarter_2026Q1.pdf` 以 markitdown 轉出時 CID 亂碼達 3,139 次（10.6%），依規則刪除該 md；經確認為 markitdown/pdfminer 字型解碼問題（PDF 本身正常），改以 pymupdf 重轉，得 cid=0 的乾淨 md，最終保留。
- 兩份年報以 markitdown 轉換即為 cid=0，無需重轉。
- 無因 <10KB 或缺公司名稱而刪除之檔案。

## 5. 本次執行使用的 MCP
| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_search`, `firecrawl_scrape` | Phase 2 定位 Petrobras IR 的年報/季報 PDF 直連；Phase 3 抓取 Seeking Alpha、雪球/hots、TradingView/Zacks、Investing.com、Quiver、MarketBeat 等來源 |
| Bright Data | `scrape_as_markdown` | Phase 3 抓取 Reddit 主帖（Firecrawl 拒絕 reddit.com）；嘗試雪球 /S/PBR（逾時）與新浪財經（GBK 亂碼） |

> Phase 4 轉換階段未使用 MCP，僅用本機工具：`markitdown`（年報）、`PyMuPDF/fitz`（季報）、`Bash`。SEC EDGAR 以內建工具/EDGAR JSON 交叉驗證申報，非 MCP。

---

## 6. 三個月輿情主軸（跨來源交叉整理）
- **利多**：估值極低（前瞻 P/E 約 3.9–4.8）、產量創高（Q1 3,225 MBOE/d、年增 16.1%；Búzios 單日 120 萬桶創新高）、煉油獲利跳升、賣方目標價逐月上修（中位約 $19，JPM 升至 $23）、Zacks Rank #1、機構 13F 共識 Moderate Buy。
- **利空**：Q1 EPS/營收不如預期（EPS ~$0.96、營收 ~$235.4 億）、配息年減約 15%、特別股利縮水（$0.1426/股）、外資 10% 配息預扣稅（2026 新制）、油價高 beta（美伊/中東降溫→油價暴跌拖累）、政府柴油定價與補貼干預（Lula 效應）、毛負債升至 $71.2B、中國需求走弱 + 到岸價差六年新低。
- **假消息提醒**：網路流傳「殖利率 50%+/72%」屬 2021–22 油價暴漲的歷史一次性超額配息，不可外推；常態前瞻殖利率約 8–10%（PBR.A）。

---

*本報告依 stock_queries.md 命名規則加註當日日期後綴。依 Routines Git 推送規則，完成後強制 push 至 `master`。*
