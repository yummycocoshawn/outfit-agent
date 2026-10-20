# Discord Bot 設定(Windows)

> ⚠️ **Bot token 等於 bot 的密碼。絕對不要告訴任何人、不要貼到聊天(包含跟 Claude 的對話)、不要 commit。外洩後別人可以冒用你的 bot,發現外洩請立刻在 Developer Portal 按 Reset Token。**

## 1. 建立 Application 與 Bot
1. 瀏覽器開 https://discord.com/developers/applications 並登入。
2. 右上角 **New Application**,名稱填 `outfit-agent`,勾選同意條款,按 **Create**。
3. 左側選單點 **Bot**(Application 建立時已自動附帶一個 bot)。

## 2. 開啟 Message Content Intent
1. 在 **Bot** 頁面往下捲到 **Privileged Gateway Intents**。
2. 打開 **MESSAGE CONTENT INTENT**,按 **Save Changes**。
3. 為什麼需要:Discord 預設不讓 bot 讀訊息文字。agent 要看懂 `!週報`、`!刪除` 這些指令,必須開啟這項權限。(只傳照片不需要,但指令需要。)

## 3. 取得 Token
1. 在 **Bot** 頁面按 **Reset Token** → 確認(可能要二次驗證)。
2. 按 **Copy**。
3. 在 repo 資料夾建立 `.env`(從 `.env.example` 複製),把 token 貼到 `DISCORD_TOKEN=` 後面。**只貼在這個檔案。**

## 4. 邀請 Bot 進你的 Server
1. 左側選單 **OAuth2** → 往下找 **OAuth2 URL Generator**。
2. **SCOPES** 勾選 `bot`(不要勾 administrator)。
3. **BOT PERMISSIONS** 只勾選:
   - View Channels
   - Send Messages
   - Read Message History
   - Add Reactions
4. 複製頁面最下方產生的 **Generated URL**,貼到瀏覽器。
5. 選擇你的 `outfit-test` Server → **繼續** → **授權**。
6. 回 Discord,成員列表應出現 `outfit-agent`(離線狀態,程式啟動後才會上線)。

## 5. 填 `.env`
```
DISCORD_TOKEN=<貼上 token>
CHANNEL_ID=<頻道 ID>
CLAUDE_MODEL=haiku
DATA_DIR=./data
```
確認 `.env` 已被 `.gitignore` 忽略:在 repo 資料夾執行 `git check-ignore .env`,應印出 `.env`。

## 6. 啟動測試
```
uv run bot.py
```
看到 log 出現「已登入 outfit-agent」,且 bot 在成員列表變成上線,就設定成功。
