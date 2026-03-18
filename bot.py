import os
import asyncio
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot is Online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port)

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Bhejo link restricted content ka. Sab nikalunga! 🔥")

@bot.on_message(filters.text & filters.regex(r"https?://t\.me/(?:c/(\d+)|([\w_]+))/(\d+)"))
async def handle_links(client, message):
    status = await message.reply_text("🔎 Analyzing Content...")
    try:
        m = message.matches[0]
        chat = int("-100" + m.group(1)) if m.group(1) else m.group(2)
        msg_id = int(m.group(3))

        try:
            u_msg = await userbot.get_messages(chat, msg_id)
        except:
            await userbot.get_chat(chat)
            u_msg = await userbot.get_messages(chat, msg_id)

        media = None
        for a in ["video", "photo", "document", "audio", "voice", "animation", "video_note"]:
            if getattr(u_msg, a, None):
                media = getattr(u_msg, a)
                break

        if media:
            await status.edit_text("📥 Downloading (Bypassing Restriction)...")
            file = await userbot.download_media(u_msg)
            await status.edit_text("📤 Uploading To You...")
            cap = u_msg.caption or ""
            if u_msg.video: await client.send_video(message.chat.id, file, caption=cap)
            elif u_msg.photo: await client.send_photo(message.chat.id, file, caption=cap)
            elif u_msg.document: await client.send_document(message.chat.id, file, caption=cap)
            elif u_msg.audio: await client.send_audio(message.chat.id, file, caption=cap)
            elif u_msg.voice: await client.send_voice(message.chat.id, file)
            elif u_msg.video_note: await client.send_video_note(message.chat.id, file)
            elif u_msg.animation: await client.send_animation(message.chat.id, file)
            os.remove(file)
            await status.delete()
        else:
            await status.edit_text("❌ Is link mein koi media nahi mila.")
    except FloodWait as e:
        await status.edit_text(f"Telegram Limit: {e.value}s wait.")
    except Exception as e:
        await status.edit_text(f"Error: {str(e)}")

async def main():
    await userbot.start()
    await bot.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    Thread(target=run_web).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
