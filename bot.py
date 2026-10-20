"""Discord 每日穿搭紀錄 agent。啟動:uv run bot.py"""
import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

import discord
from dotenv import load_dotenv

import claude_client
from core import find_repeat, safe_filename, summarize
from storage import Store

load_dotenv()
TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
MODEL = os.environ.get("CLAUDE_MODEL", "sonnet")
store = Store(os.environ.get("DATA_DIR", "./data"))
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 8 * 1024 * 1024

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
queue: asyncio.Queue = asyncio.Queue()
worker_started = False

HELP = "📸 上傳穿搭照片,我會記錄單品、風格與適合氣溫。\n指令:`!週報` 近 7 天統計、`!刪除` 刪掉你最後一筆紀錄、`!說明`"


@client.event
async def on_ready():
    global worker_started
    logging.info("已登入 %s", client.user)
    if not worker_started:
        worker_started = True
        client.loop.create_task(worker())


@client.event
async def on_message(msg: discord.Message):
    if msg.author.bot or msg.channel.id != CHANNEL_ID:
        return
    text = msg.content.strip()
    user = msg.author.display_name
    if text == "!說明":
        await msg.reply(HELP)
    elif text == "!週報":
        await msg.reply(await asyncio.to_thread(report, msg.author.id, user))
    elif text == "!刪除":
        name = await asyncio.to_thread(store.delete_last, msg.author.id)
        await msg.reply(f"🗑️ 已刪除你的最後一筆:{name}" if name else "你還沒有任何紀錄。")
    for att in msg.attachments:
        ext = Path(att.filename).suffix.lower()
        if ext in IMAGE_EXT and att.size <= MAX_BYTES:
            await msg.add_reaction("⏳")
            await msg.reply("處理中…")
            await queue.put((msg, att, ext))


def report(uid, user):
    now = datetime.now()
    recs = [r for r in store.records(uid) if (now - r["time"]).days < 7]
    if not recs:
        return "近 7 天沒有穿搭紀錄,快上傳一張吧!"
    s = summarize(recs)
    top = "、".join(f"{n}×{c}" for n, c in s["top_items"])
    style, cnt = s["top_style"]
    return f"📊 {user} 近 7 天:共 {s['count']} 套穿搭\n最常穿單品:{top}\n最常見風格:{style}({cnt} 次)"


async def worker():
    while True:
        msg, att, ext = await queue.get()
        try:
            await handle(msg, att, ext)
        except Exception:  # 單張失敗不應讓 worker 死掉
            logging.exception("處理失敗")
            await msg.reply("分析失敗，請再傳一次")
        finally:
            queue.task_done()


async def handle(msg, att, ext):
    user = msg.author.display_name
    now = datetime.now()
    tmp_photo = store.photos / f"_{msg.id}{ext}"
    await att.save(tmp_photo)
    try:
        result = await asyncio.to_thread(claude_client.analyze, tmp_photo, MODEL)
    except Exception:
        tmp_photo.unlink(missing_ok=True)
        raise
    base = f"{now:%Y-%m-%d %H-%M-%S} {safe_filename(result['name'])}"
    final = store.photos / f"{base}{ext}"
    n = 2
    while final.exists():  # 同一秒同名:加 -2、-3
        final = store.photos / f"{base}-{n}{ext}"
        n += 1
    tmp_photo.rename(final)
    rec = {**result, "time": now}
    history = await asyncio.to_thread(store.records, msg.author.id)
    await asyncio.to_thread(store.add, msg.author.id, user, rec, final)
    if not result["is_outfit"]:
        await msg.reply(f"🤔 這看起來不是穿搭:{result['note']}(已存檔)")
        return
    month_count = sum(1 for r in history if r["time"].strftime("%Y-%m") == f"{now:%Y-%m}") + 1
    lines = [f"👗 **{result['name']}**({result['style']})",
             f"單品:{'、'.join(result['items'])}",
             f"顏色:{'、'.join(result['colors'])}",
             f"適合氣溫:{result['temp_min']}~{result['temp_max']}°C",
             f"📅 {user} 本月第 {month_count} 套穿搭"]
    rep = find_repeat(result["items"], history, now=now)
    if rep:
        s, old = rep
        lines.append(f"♻️ 跟 {old['time']:%m/%d} 的「{old['name']}」相似度 {s:.0%},換套新的吧!")
    await msg.reply("\n".join(lines))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client.run(TOKEN)
