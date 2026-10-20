# 架構

```
Discord 頻道 ──► bot.py (on_message) ──► asyncio.Queue ──► worker
                                                         │
                          claude_client.analyze (temp 資料夾 + claude -p, 只允許 Read)
                                                         │
                          core.parse_model_output (驗證/清洗) ──► storage.Store (xlsx + photos)
                                                         │
                                    core.find_repeat / summarize ──► 回覆
```

- `core.py`:無副作用的純函式(驗證、清洗、相似度、統計),有單元測試。
- `storage.py`:Excel/照片;以上傳者欄區分使用者。
- `claude_client.py`:呼叫 `claude -p`,隔離與限權。
- `bot.py`:事件處理、佇列、指令。單一 worker 保證多人同時上傳時逐張處理。
