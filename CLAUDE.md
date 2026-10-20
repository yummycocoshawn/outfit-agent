# CLAUDE.md

本專案是在本機執行的 Discord 穿搭紀錄 agent:頻道內上傳穿搭照片,用 `claude -p` 辨識後記錄到 Excel 並回覆。

開始任何工作前,先讀 `docs/architecture.md`。

## 四道防護
程式中以 `防護 n 開始` / `防護 n 結束` 註解包住,目前全部啟用:
1. 隔離範圍(`claude_client.py`):獨立暫存資料夾 + 只允許 Read 工具。
2. 資料與指令分離(`claude_client.py`):使用者文字不進 prompt。
3. 檔名清洗(`core.py` 的 `safe_filename`)。
4. Excel 公式防護(`core.py` 的 `clean_text`)。

## 規則
- `.env`、`DATA_DIR` 內的照片與 Excel 檔絕對不可 commit。
- 修改防護區段前先與使用者確認。
