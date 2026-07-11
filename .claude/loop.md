# loop.md — UHS PE 低估分析循環任務

## 執行指令
- 使用 `/goal`

## 執行頻率
- 每一小時執行一次（hourly）

## 任務目標（Goal）
- 分析為什麼美股 **UHS（Universal Health Services）** 的本益比（PE）< 8，為什麼這麼低？
- 深入探討低本益比背後的原因（例如：獲利品質、產業風險、市場情緒、成長性疑慮、法遵/訴訟、政策風險、資本結構等）。

## 輸出（Output）
- 將分析結果 **update 到** `UHS/hourAnalysis.md`
- 每次執行需比對並延續前一次的分析結論，補充新資訊、修正舊觀點，並標註更新時間戳記。

## 分析資料來源（Data Sources）
1. **前一次的 `UHS/hourAnalysis.md`** 分析結果（作為延續與比對基礎）
2. **`UHS/` 資料夾**內的財報與輿情檔案（10-K、10-Q、GoogleNews、Reddit、SeekingAlpha、X、Xueqiu、Official_IR 等）
3. **網路搜尋（web search）**：取得最新股價、PE、財報、新聞與市場動態

## 研究深度（Research Depth）
- 進行 **deep research**：盡可能搜尋、交叉驗證，資訊要新、要可驗證
- 若資料缺失，需明確註記缺口與可能原因

## 收尾（Finalize）
- 分析完成後 **merge into master branch**（合併回 master 分支）
