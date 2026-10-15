# 任務執行最終報告 - 2026/10/14

- **執行日**：2026-10-14（每日輪替表第 27 日 → `3455 醫療保健投資法人`（ヘルスケア＆メディカル投資法人，HCM））
- **公司資料夾**：`3455醫療保健投資法人/`（本次新建，原本不存在）
- **每口換算基準**：最新發行口數 457,000 口（2026-09-29 第三者割當完成後）

## 1. 成功紀錄
| 股號/名稱 | 資料來源 | 產生的檔案/下載的財報檔名 | 狀態/備註 |
| :--- | :--- | :--- | :--- |
| `3455醫療保健投資法人` | 官網英文 IR Library（Semi-annual report 欄） | `3455_AnnualReport_2025Jul.md`（第 21 期，2025 年 7 月期，經審計財報） | 下載成功，0 cid，已轉 md |
| `3455醫療保健投資法人` | 官網英文 IR Library（Semi-annual report 欄） | `3455_AnnualReport_2026Jan.md`（第 22 期，2026 年 1 月期，經審計財報） | 下載成功，0 cid，已轉 md |
| `3455醫療保健投資法人` | 官網英文 IR Library（Summary of accounts 欄） | `3455_Quarter_2026Jul.md`（第 23 期，2026 年 7 月期決算短信英文版，2026-09-14） | 下載成功，0 cid，已轉 md（J-REIT 為半年決算，以最新決算短信作為「季報」） |
| `3455醫療保健投資法人` | 官網日文 IR Library（決算説明資料欄） | `3455_Presentation_2026Jul.md`（第 23 期決算説明資料，72 頁） | 英文版尚未公布，改抓日文版；0 cid，已轉 md |
| `3455醫療保健投資法人` | Yahoo!ファイナンス 掲示板、株探＋TDnet 開示、Yahoo ニュース、5ch、JAPAN-REIT.COM、X、note、みんかぶ、Reddit | `3455醫療保健投資法人/202610_輿情新聞.md`（新建） | 輿情建立成功，涵蓋 2026-07-14 ~ 2026-10-14 |

**本期重點**（皆已對照 TDnet 原文或決算短信）：
- **公募增資＋大量取得物件（2026-08-19 公告）**：公募 92,858 口＋超額配售 4,642 口，發行價 95,160 円、發行價額 91,939 円（公募手取 85.37 億円，約每口 18,681 円）。取得 14 棟，合計 217.36 億円（約每口 47,562 円），其中 **13 棟向資產管理公司的利害關係人 SPC 購入**。
- **發行口數 359,500 → 457,000 口（+27.1%）**：每口數字會被攤薄，這是本期最主要的流通口數變化。
- **第 23 期（2026 年 7 月期）**：每口分配 3,174 円（前期 3,286 円），LTV 52.6%，出租率 100%，57 棟。預估 2027 年 1 月期每口分配 3,440 円（含賣出グッドタイムホーム不動前的利益）、2027 年 7 月期 3,170 円（含超額分配 417 円）。株探標題「經常利益 8 期來最高」主要是物件增加和賣樓利益帶動，**每口分配沒有創新高**。
- **融資**：2026-09-28 向三井住友銀行短期借款 8 億円（約每口 1,751 円），利率 TIBOR+0.25%，2026-12-01 到期，利率重設風險仍在。
- **股價**：7/14 收 111,600 円 → 10/14 收 92,800 円，三個月跌 16.8%（其中約 2.8 個百分點是 7/30 除息 3,174 円）。10/1 跌破公募價 95,160 円，10/8 跌破發行價額 91,939 円（低點 91,400 円）。株探計算的殖利率 7.41%，在 58 檔 J-REIT 中排第 4。
- **法人籌碼**：三井住友DS 集團 8/31 新超過 5%（5.30%），之後 SMBC日興 在 9/15 降到 3.63%（主要是承銷部位出清）；三菱UFJ 9/14 新超過 5%（5.24%）；三井住友トラスト・アセットマネジメント 8~9 月連續 3 次減碼。
- **輿情**：Yahoo 掲示板明顯偏空（升息、REIT 指數 10 年低點、固定租金無法轉嫁通膨、超額分配被批評為「タコ足」），少數人以 7% 殖利率分批承接。note 有作者指出 **增資價格只有每口 NAV 的 0.65 倍**、過去兩檔專業 Healthcare REIT 都被併購下市，但其餘論證在付費區，未能核實。
- **已更正的網友錯誤**：掲示板多人寫「公募價 95,100 円」，正確是 95,160 円；「分配金修正後殖利率降到 5%」與公司預估不符（以 91,500 円計年化約 7.2%）。

## 2. 失敗或被擋網站
- **JAPAN-REIT.COM**：`curl` 回 SSL 憑證鏈不完整（不可關閉 TLS 驗證）、`WebFetch` 回 HTTP 503 → Firecrawl `firecrawl_scrape` 成功。
- **みんかぶ**：`curl` 403 → Firecrawl 額度用盡 → Bright Data 本 session 未授權 → Playwright 403 → **Apify `apify/rag-web-browser` 成功**。
- **note 搜尋頁**：Firecrawl 額度用盡 → Bright Data 未授權 → **Apify `apify/rag-web-browser` 成功**；`takenoko_fund` 增資檢證文後半為付費內容，未取得。
- **X**：Firecrawl `firecrawl_search` 第 1 次成功（3 則），第 2 次回「Insufficient credits」，無法再查；Bright Data 未授權、Apify 未另找 X Actor。X 樣本只有 1 個帳號 3 則。
- **Firecrawl**：本次用了 3 次後額度用盡（帳號級），之後未再呼叫。
- **Bright Data**：本 session 的 MCP 需要授權，無法使用（不是網站封鎖）。

## 3. 資料缺失說明
- **英文第 23 期簡報與資產運用報告**：決算後約 1 個月，英文只出 Summary of accounts；日文「資産運用報告」「有価証券報告書」（預定 2026-10-28 提交）尚未上架。以英文決算短信＋日文簡報補足。
- **5ch、Reddit、Shared Research**：三個月內沒有與本 REIT 相關的內容（Shared Research 回 404，沒有覆蓋此 REIT）。
- **Yahoo 掲示板**：一次只能拿到最新 72 則（2026-09-24 以後），`?page=` 不會翻頁，更早的討論取不到。
- **日本經濟新聞**：付費牆，未抓取；重要事件已由 TDnet 原文涵蓋。

## 4. 異常檔案刪除紀錄
- 無下載檔因 <10KB、沒有公司名稱或 cid 亂碼而刪除（4 份 PDF 下載後都先用 `pdftotext` 確認 0 個 `(cid:`）。
- Convert2md 成功後依規則刪除 4 份來源 PDF。
- 轉檔產生的 `.md` 內有指向暫存圖片的失效連結（年報各 10 個、簡報 253 個），已移除，正文未動。
- Playwright 在 repo 根目錄產生的 `.playwright-mcp/` 暫存資料夾已移出 repo，未提交。

## 5. 本次執行使用的 MCP
| MCP 服務名稱 | 用到的工具/函式 | 用途說明 |
| :--- | :--- | :--- |
| Firecrawl | `firecrawl_scrape` | 抓 JAPAN-REIT.COM 3455 個股頁（curl TLS 錯誤、WebFetch 503 之後） |
| Firecrawl | `firecrawl_search` | 用 `site:x.com` 查 X 貼文（成功 1 次；第 2 次與 note 搜尋頁 scrape 回額度不足） |
| Apify | `call-actor`（`trudax/reddit-scraper-lite`）＋ `get-dataset-items` | Reddit 搜尋，結果只有 1 則無關文章 |
| Apify | `call-actor`（`apify/rag-web-browser`）＋ `get-dataset-items` | 抓みんかぶ個股頁、note 搜尋結果頁 |
| Playwright | `browser_navigate` | 試抓みんかぶ，回 403 |
| pymupdf4llm | `convert_pdf_to_markdown` | Phase 4 把 4 份 PDF 轉成 Markdown |
| （其餘） | — | Yahoo 掲示板／ニュース、株探、TDnet PDF、5ch、公司 IR、note 單篇、Shared Research 都用內建 `Bash`（`curl`、`pdftotext`）；`WebFetch` 用於 JAPAN-REIT（503） |

## 6. Phase 4 Convert2md
- 掃描 8 份 PDF，4 份已轉換跳過（其他公司），本次轉換 4 份，**4 份成功、0 失敗、0 cid 亂碼**。報告見 `Log/conversion_summary.md`。

## 7. Skill 維護
- 本次發現 8 個新的網站／工具行為，已加進 `CollectsentimentAndReports/SKILL.md` §2.4：JAPAN-REIT 的 TLS 憑證鏈錯誤與 WebFetch 503、みんかぶ 連 Playwright 都 403（Apify `rag-web-browser` 可行）、note 搜尋頁可用 Apify、株探新聞 `&page=2`、Shared Research 沒有 J-REIT、Firecrawl 額度用盡、轉檔後的失效圖片連結、HCM 英文 IR 的欄位與更新時差。
