# [02318 中國平安] 輿情抓取失敗記錄 - [東方財富股吧] (2026/07)

- **分析時間**：2026-08-01
- **目標網址**：https://guba.eastmoney.com/list,601318.html
- **狀態**：❌ 抓取失敗（未取得任何真實貼文內容）

## 已嘗試的工具鏈（依序）
1. **內建 WebSearch**：可搜到股吧入口頁，但無法取得吧內個別貼文內容。
2. **mcp__brightdata__scrape_as_markdown**：回傳亂碼（`身�`），頁面為 JS 動態載入，無有效內容。
3. **mcp__firecrawl-mcp__firecrawl_scrape**（onlyMainContent）：HTTP 200，但貼文列表為前端 JS 動態渲染，抓到的僅為頁面骨架與導航，貼文區顯示「找到關於"的結果共 0 條」，無實際貼文。

## 可能原因
- 東方財富股吧貼文列表由 JavaScript 前端動態載入（非 SSR），一般 scraper 只取得空殼頁面。
- 該站對非瀏覽器 User-Agent 有反爬機制。

## 備註
- 本月 A 股/H 股散戶輿情已由**雪球 SH601318**（202607_Xueqiu.md）充分覆蓋，內容更豐富且可驗證，故未再以 playwright 進一步嘗試東方財富股吧，以節省資源。
