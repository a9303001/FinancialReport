# MdClean 執行摘要（給下一輪 AI 讀）

- **最後執行時間**：2026-11-01 14:09:34（耗時 3.3 秒）
- **腳本版本**：`gemini/MdClean.py` v1｜規則說明：`gemini/MdClean.md`
- **批次參數**：max_files=20｜max_mb=25.0｜no_join=False
- **整體進度**：共 220 個可清理 md｜CLEAN 20｜NEW 200｜MODIFIED 0｜OLD_VERSION 0｜FAIL 待處理 0
- **排除**：`hourAnalysisResult.md`、非公司資料夾（.agents, .claude, History, HkReitScreenerResult, JpReitScreenerResult, Log, Prompt, StkScreenerResult, gemini）

## 1. 下一輪要處理的 md 檔

> 下一輪直接執行 `python gemini/MdClean.py` 即會依序處理下列檔案（腳本以檔頭標記自動判斷，不需手動指定）。
> 若清單為空 = 全部完成；之後只有新檔或被修改的檔會再次出現。

1. `00941中國移動/202610231417.md`｜NEW｜2 KB｜light
2. `00941中國移動/2026_PublicOpinion.md`｜NEW｜90 KB｜light
3. `01044恒安國際/01044_AnnualReport_2024.md`｜NEW｜714 KB｜report
4. `01044恒安國際/01044_AnnualReport_2025.md`｜NEW｜669 KB｜report
5. `01044恒安國際/01044_Quarter_2026Q2.md`｜NEW｜250 KB｜report
6. `01044恒安國際/202610_輿情新聞.md`｜NEW｜26 KB｜light
7. `01044恒安國際/2026_PublicOpinion.md`｜NEW｜50 KB｜light
8. `01426春泉Reit/01426_InterimReport_2026.md`｜NEW｜190 KB｜report
9. `01426春泉Reit/01426_InterimResults_2026.md`｜NEW｜3 KB｜report
10. `01426春泉Reit/01426_Quarter_2026Q2_OpStats.md`｜NEW｜4 KB｜report
11. `01426春泉Reit/2025042201223.md`｜NEW｜692 KB｜report
12. `01426春泉Reit/20260324以春泉產業信託的基金單位及現金形式向春泉資產管理有限公司支付基本費用及浮動費用.md`｜NEW｜9 KB｜report
13. `01426春泉Reit/2026042200516.md`｜NEW｜545 KB｜report
14. `01426春泉Reit/202606_InvestmentAnalysis.md`｜NEW｜14 KB｜light
15. `01426春泉Reit/2026_PublicOpinion.md`｜NEW｜143 KB｜light
16. `01426春泉Reit/ltn20131205481.md`｜NEW｜897 KB｜report
17. `01816中廣核電力/01816_AnnualReport_2024.md`｜NEW｜1,043 KB｜report
18. `01816中廣核電力/01816_AnnualReport_2025.md`｜NEW｜1,081 KB｜report
19. `01816中廣核電力/01816_Quarter_2026H1.md`｜NEW｜535 KB｜report
20. `01816中廣核電力/01816_Quarter_2026Q1.md`｜NEW｜59 KB｜report

- 下一輪之後尚餘：180 檔

## 2. 本輪處理結果

- [OK] `00546阜豐/00546_2025_annual_report.md`｜report｜627 KB → 572 KB（-9%）｜empty_cols_removed=2201, empty_rows_removed=440, header_cols_aligned=33, page_markers=113, running_header_lines_removed=126, separator_rows_removed=683, single_col_tables_to_text=2, tables_seen=683, wrapped_lines_joined=338
- [OK] `00546阜豐/00546_AnnualReport_2024.md`｜report｜716 KB → 563 KB（-21%）｜empty_cols_removed=2280, empty_rows_removed=416, header_cols_aligned=32, page_markers=108, running_header_lines_removed=119, separator_rows_removed=703, single_col_tables_to_text=4, tables_seen=703, wrapped_lines_joined=326
- [OK] `00546阜豐/00546_Quarter_2026H1.md`｜report｜206 KB → 197 KB（-4%）｜page_markers=65, picture_text_blocks=6, running_header_lines_removed=72, separator_rows_removed=62, tables_seen=62
- [OK] `00546阜豐/00546_Quarter_2026Q2.md`｜report｜111 KB → 111 KB（-0%）｜image_links_removed=2, picture_text_blocks=2, separator_rows_removed=31, tables_seen=31
- [OK] `00546阜豐/2026_PublicOpinion.md`｜light｜198 KB → 199 KB（+0%）｜control_chars_removed=13
- [OK] `00883中國海洋石油/00883_AnnualReport_2024.md`｜report｜558 KB → 480 KB（-14%）｜empty_cols_removed=1063, empty_rows_removed=337, header_cols_aligned=17, separator_rows_removed=357, single_col_tables_to_text=3, tables_seen=357, wrapped_lines_joined=2357
- [OK] `00883中國海洋石油/00883_AnnualReport_2025.md`｜report｜533 KB → 462 KB（-13%）｜empty_cols_removed=982, empty_rows_removed=319, header_cols_aligned=9, separator_rows_removed=334, single_col_tables_to_text=5, tables_seen=334, wrapped_lines_joined=2279
- [OK] `00883中國海洋石油/00883_Quarter_2026Q1.md`｜report｜36 KB → 27 KB（-26%）｜empty_cols_removed=201, header_cols_aligned=2, page_markers=16, separator_rows_removed=68, single_col_tables_to_text=5, tables_seen=68, wrapped_lines_joined=41
- [OK] `00883中國海洋石油/00883_Quarter_2026Q2.md`｜report｜38 KB → 39 KB（+3%）｜image_links_removed=1, page_markers=14, separator_rows_removed=13, tables_seen=13
- [OK] `00883中國海洋石油/202610_輿情新聞.md`｜light｜31 KB → 32 KB（+1%）｜無需變更（僅加導讀）
- [OK] `00883中國海洋石油/2026_PublicOpinion.md`｜light｜74 KB → 74 KB（+1%）｜control_chars_removed=1
- [OK] `00883中國海洋石油/Orange.md`｜report｜0 KB → 1 KB（+1363%）｜無需變更（僅加導讀）
- [OK] `00941中國移動/00941_Quarter_2026Q2.md`｜report｜96 KB → 94 KB（-2%）｜page_markers=47, picture_text_blocks=1, running_header_lines_removed=50, separator_rows_removed=43, tables_seen=43, wrapped_lines_joined=1
- [OK] `00941中國移動/00941_Quarter_2026Q3.md`｜report｜34 KB → 36 KB（+5%）｜separator_rows_removed=23, tables_seen=23
- [OK] `00941中國移動/00941_analysis_report.md`｜light｜10 KB → 10 KB（+4%）｜無需變更（僅加導讀）
- [OK] `00941中國移動/00941_annual_2024.md`｜report｜506 KB → 444 KB（-12%）｜empty_cols_removed=3573, empty_rows_removed=459, header_cols_aligned=72, separator_rows_removed=829, single_col_tables_to_text=70, tables_seen=829, wrapped_lines_joined=1531
- [OK] `00941中國移動/00941_annual_2025.md`｜report｜428 KB → 398 KB（-7%）｜empty_cols_removed=723, empty_rows_removed=218, header_cols_aligned=4, page_markers=147, running_header_lines_removed=228, separator_rows_removed=349, tables_seen=349, wrapped_lines_joined=1785
- [OK] `00941中國移動/00941_interim_2025.md`｜report｜143 KB → 135 KB（-5%）｜empty_cols_removed=299, empty_rows_removed=89, header_cols_aligned=1, page_markers=26, running_header_lines_removed=14, separator_rows_removed=127, single_col_tables_to_text=1, tables_seen=127, wrapped_lines_joined=562
- [OK] `00941中國移動/00941_interim_2026.md`｜report｜55 KB → 51 KB（-7%）｜empty_cols_removed=85, header_cols_aligned=2, separator_rows_removed=62, tables_seen=62, wrapped_lines_joined=185
- [OK] `00941中國移動/00941_quarter_2026Q1.md`｜report｜19 KB → 17 KB（-12%）｜empty_cols_removed=132, empty_rows_removed=25, header_cols_aligned=1, separator_rows_removed=63, tables_seen=63, wrapped_lines_joined=29

## 3. FAIL 清單（未覆寫原檔，需下一輪 AI 處理）

<!-- fail-list:start -->
<!-- fail-list:end -->

- 處理方式：先 `python gemini/MdClean.py --file "<路徑>" --no-join --dry-run` 重試；仍失敗 → 依 `gemini/MdClean.md` Step 4 判斷，必要時把該檔加入 `MdClean.py` 的 `SKIP_FILES` 並在 ai-notes 註明原因。

## 4. 下一輪 AI 必讀重點

- 清理後檔案第一行是 `<!-- MdClean:v1 | sha1:… -->`，第二段是 `<!-- AI-META … -->` 導讀（公司、文件類型、單位、頁碼標記、數字慣例）。**不要手動修改這兩段**；改了內容後 sha1 不符會自動重排入待處理。
- `*_PublicOpinion.md` 由 ArrangePublicOpinionMd 每次 append 並重寫檔頭 → MdClean 標記會消失，該檔自動回到待處理（正常現象）。`<!-- body:start -->`、`<!-- source-file: … -->` 一律原樣保留。
- 安全閘門：數字 token 必須 100% 保留（頁碼、圖片路徑、cid 亂碼除外）；FAIL 的檔不會被覆寫。
- 腳本是確定性規則；AI 不要整份重寫大檔。只允許：(a) 小檔（<100 KB）局部修正；(b) 把觀察寫進下方 ai-notes；(c) 修改 `MdClean.py` 規則並升版（VERSION → v2 後舊檔會變 OLD_VERSION 自動重跑）。

## 5. AI 觀察與待辦（ai-notes，腳本會保留）

<!-- ai-notes:start -->
- 2026-11-01｜v1 首輪（Claude 建立腳本）｜全量 dry-run 220/220 通過安全閘門、220/220 冪等（清兩次結果相同）；正式清理第 1 批 20 檔 OK=20 FAIL=0；抽查 UHS 10-K、00941 年報、3445 有価証券報告書、1264 季報、UHS 輿情彙整皆合格。
- 已知限制（v2 候選規則，非 bug）：PDF 碎表的「單一儲存格被切開」（例：`二|零二三年`）與「多行表頭散在不同列」無法機械還原；部分表格列被 pymupdf 輸出成「項目 數字 數字」純文字行（AI-META 已註明讀法）。若要改善，應在 Convert2md 階段改用表格模式重轉，而不是在 MdClean 硬修。
- 已知限制：pymupdf4llm 新版年報（如 01044）中英對照段落常被並排輸出成同一行，v1 不拆分。
- 待辦：下一輪照常 `python gemini\MdClean.py`；抽查重點放在 01044（新版 pymupdf4llm 格式）與 01816（cid 亂碼檔）。
<!-- ai-notes:end -->

## 6. 歷次執行紀錄（最新在上，保留 30 筆）

<!-- history:start -->
- 2026-11-01 14:09｜v1｜本輪 OK 20｜FAIL 0｜累計 CLEAN 20/220｜待處理 200
<!-- history:end -->
