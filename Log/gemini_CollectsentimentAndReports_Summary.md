# Rotation Progress — CollectsentimentAndReports

| 欄位 | 值 |
| :--- | :--- |
| **last_executed_date** | 30 |
| **last_executed_companies** | 8002 丸紅 (Marubeni) |
| **last_executed_time** | 2026-08-30 20:20 (UTC) |
| **next_date** | 31（無/不執行 Skip） |

---

## ⚠️ 輪替邏輯歧異提醒（2026-08-30 記錄）

本追蹤器先前以「**循序補跑**」方式推進（15 → 16 → 17 → 18 → 19，next=20），
但 `Routines_CollectsentimentAndReports.md` 的原始規則為「**取得今日的「日」(Day of the Month)**」。

2026-08-30 該次執行依 **Routines 檔的原始規則**執行 **Day 30 = 8002 丸紅**，故本表更新為 30。

若欲改採循序補跑，下列輪替日尚待確認/補跑：

| 輪替日 | 公司 | 備註 |
| :---: | :--- | :--- |
| 20 | 4979 OAT | `Log/CollectsentimentAndReports_Summary_20260829.md` 顯示已執行 |
| 21 | 5306 桂盟 | 待補 |
| 22 | 03606 福耀玻璃 | 待補 |
| 23 | 01816 中廣核電力 | 待補 |
| 24 | 9503 關西電力 | 待補 |
| 25 | PBR.A 巴西石油 | 待補 |
| 26 | 1264 德麥 | 待補 |
| 27 | 6902 DENSO | 待補 |
| 28 | 6605 帝寶 | 待補 |
| 29 | 00883 中國海洋石油 / 00857 中石油 / 00386 中石化 | 待補 |

> 建議由使用者明確指定採用「日曆日對應」或「循序補跑」其中一種邏輯，以免兩套機制交錯造成重複或遺漏。

---

## 歷史紀錄

| 執行時間 (UTC) | 輪替日 | 公司 | 報告檔 |
| :--- | :---: | :--- | :--- |
| 2026-08-30 20:20 | 30 | 8002 丸紅 (Marubeni) | `CollectsentimentAndReports_Summary_20260830.md`（第二筆，Append） |
| 2026-08-31 00:27 | 19 | EVTC (EVERTEC) | `CollectsentimentAndReports_Summary_20260831.md` |
| — | 18 | CF (CF Industries) | — |
| — | 17 | 1301 極洋 | — |
| — | 16 | 00546 阜豐 | — |
| — | 15 | 87001 匯賢Reit | `CollectsentimentAndReports_Summary_20260830.md`（第一筆） |
| — | 20 | 4979 OAT | `CollectsentimentAndReports_Summary_20260829.md` |
