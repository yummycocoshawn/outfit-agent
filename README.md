# 每日穿搭紀錄 Discord Agent

在自己電腦上執行的 Discord bot。在指定頻道上傳穿搭照片,agent 用 `claude -p` 辨識單品、顏色、風格與適合氣溫,寫入 Excel、存照片,並回覆結果。

## 功能

1. **辨識回覆**:上傳照片 → 回覆穿搭名稱、單品、顏色、風格、適合氣溫(非穿搭照片也會回覆並建檔)。
2. **計算**:自動計算「你本月第幾套穿搭」,`!週報` 統計近 7 天套數、最常穿的單品 Top 3、最常見風格。
3. **參考過去結果**:新穿搭會與你近 7 天紀錄比對單品重疊度(Jaccard ≥ 60%),相似時提醒「跟 10/18 的某某穿搭很像」。
4. **多使用者區分**:所有紀錄、統計、重複提醒都以 Discord 使用者 ID 分開計算(同名或改暱稱也不會混在一起)。
5. **其他**:`!刪除` 刪除自己最後一筆紀錄(編輯過去紀錄)、`!週報` 報表、Excel 持續累加、照片以「日期時間_穿搭簡稱」命名、上傳排隊逐張處理。

## 防護機制

- 暫存資料夾:每張照片複製到獨立 temp 資料夾後才給 `claude -p`,用完刪除。
- 工具限制:`--allowedTools "Read(./**)" --permission-mode dontAsk`,模型只能讀暫存資料夾內的檔案(實測絕對路徑也讀不到資料夾外)。
- 資料與指令分離:prompt 明示照片是不可信資料;程式不信任模型輸出。
- 輸出驗證:`core.parse_model_output` 嚴格檢查 JSON 結構、型別、溫度範圍,並清掉 Excel 公式開頭字元與控制字元。
- Token 只放 `.env`(已 gitignore)。

### 防護區段位置(各以 `防護 n 開始/結束` 註解包住,目前全部啟用)
| 防護 | 檔案 | 起始行 |
|---|---|---|
| 1 隔離範圍 | `claude_client.py` | 18 |
| 2 使用者文字只當資料 | `claude_client.py` | 22 |
| 3 檔名清洗 | `core.py` | 21 |
| 4 Excel 公式防護 | `core.py` | 14 |

## 執行

```
uv sync
cp .env.example .env   # 填入 DISCORD_TOKEN、CHANNEL_ID
uv run bot.py
```
需在 Discord Developer Portal 開啟 Message Content Intent。測試:`uv run pytest`。

詳見 `docs/requirements.md`、`docs/architecture.md`。
