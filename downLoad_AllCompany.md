/goal

# 個股資料更新主任務 (Main Orchestration Goal)
請作為主代理 (Main Agent) 執行以下協調與排程步驟：

1. **掃描公司目錄 (Scan Company Folders)**：
   - 掃描 `FinancialReport` 目錄，辨識所有代表公司的子資料夾（如 `2881富邦金`、`02318中國平安`、`UHS` 等，排除 `.git`、`.agents`、`Prompt`、`.zettel-notes` 等系統資料夾）。

2. **為每家公司建立子代理 (Spawn Sub-Agent per Company)**：
   - 針對辨識出的每個公司資料夾，單獨啟動一個子代理 (Sub-Agent) 處理該公司的更新。
   - 每個子代理必須執行並嚴格遵循 `CollectsentimentAndReports/SKILL.md`。
   - 子任務範圍：針對該特定公司，下載最近 2 期年報、最近 1 期季報，並蒐集整理過去二個月的輿情與新聞


