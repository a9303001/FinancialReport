/goal

使用latest OPUS

## 1. 任務目標（Goal）

- 分析為什麼美股 **UHS（Universal Health Services, NYSE: UHS）** 的本益比（PE）長期 **< 8**、為什麼這麼低。
- 深入探討低本益比背後的成因，至少涵蓋：
  - 獲利品質、成長性疑慮、產業與市場情緒
  - 法遵／訴訟、政策風險（Medicaid、加州補充給付等）、資本結構與治理
 - 分析結果 **update 到** `UHS/hourAnalysisResult.md`。


---

## 2. 資料來源（Data Sources · 依序）

1. **前一輪的 `hourAnalysisResult.md`** — 作為延續與比對的基準（每次先讀回）。
2. FinancialReport repo 內的財報與輿情檔。
3. **網路搜尋（web search）** — 取得最新股價、PE、財報、新聞與市場動態，並與本地資料交叉驗證。

---

## 3. 研究深度（Research Depth）

- 進行 **deep research**：盡量搜尋、交叉驗證，資訊要新、要可驗證。
- 資料缺失時，**明確註記缺口與可能原因**（如財報尚未發布、資料庫延遲等）。
- **優先補齊前一輪仍缺的項目**（例如：5 年 ROE 完整年序、最新一季實績），逐輪把缺口補上。

---

## 4. 輸出hourAnalysisResult.md規範(Output · 每次都要 optimize + rearrange）

- **延續而非重寫**：於檔首新增一段「更新紀錄 + 時間戳記」，比對前一輪結論，補新資訊、修正舊觀點。
- **每次更新都要同步「優化與重新編排」內容（optimize & rearrange）**，讓 user 一眼看得懂：
  1. 檔首固定放「**最新結論摘要**」
  2. 相同主題**合併去重**，不要讓同一觀點散落多段、也不要無限堆疊舊內容。
  3. 用**表格／條列**呈現數據與多空對照，段落簡潔、標題清楚。
  4. 過舊或已被推翻的內容**收斂或移除**，只保留「仍有效」與「有變化」的重點。
- 每次都要重新整理 hourAnalysisResult.md 內容，不要有流水帳
- hourAnalysisResult.md要讓user看的懂
### 4.1 **每股化** 
- 所有提到的財務數字都要嘗試**每股化** ，讓我可以做每股分析



---

## 5. 收尾（Finalize）

- 每小時分析完就 **commit + push**，並 **merge 回 `master` 分支**（不必等整個 session 結束）。
