import os
import asyncio
from flask import Flask
from threading import Thread

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from pyrogram import Client, filters
from pyrogram.errors import FloodWait

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port)

bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Bhejo link restricted content ka (Public ya Private).")

@bot.on_message(filters.text & filters.regex(r"https?://t\.me/(?:c/(\d+)|([\w_]+))/(\d+)"))
async def handle_links(client, message):
    status_msg = await message.reply_text("🔎 Fetching content...")
    try:
        match = message.matches[0]
        private_id = match.group(1)
        username = match.group(2)
        message_id = int(match.group(3))

        target_chat = int("-100" + private_id) if private_id else username

        try:
            user_msg = await userbot.get_messages(target_chat, message_id)
        except Exception:
            await userbot.get_chat(target_chat)
            user_msg = await userbot.get_messages(target_chat, message_id)

        media = (user_msg.video or user_msg.document or user_msg.photo or 
                 user_msg.audio or user_msg.voice or user_msg.animation)

        if media:
            await status_msg.edit_text("📥 Downloading...")
            file_path = await userbot.download_media(user_msg)
            await status_msg.edit_text("📤 Uploading...")
            
            caption = user_msg.caption if user_msg.caption else ""
            if user_msg.video: await client.send_video(message.chat.id, file_path, caption=caption)
            elif user_msg.photo: await client.send_photo(message.chat.id, file_path, caption=caption)
            elif user_msg.document: await client.send_document(message.chat.id, file_path, caption=caption)
            elif user_msg.audio: await client.send_audio(message.chat.id, file_path, caption=caption)
            elif user_msg.voice: await client.send_voice(message.chat.id, file_path)
            elif user_msg.animation: await client.send_animation(message.chat.id, file_path)
            
            os.remove(file_path)
            await status_msg.delete()
        else:
            await status_msg.edit_text("Koi media nahi mila is message mein.")

    except FloodWait as e:
        await status_msg.edit_text(f"Wait {e.value} seconds (Telegram Limit).")
    except Exception as e:
        await status_msg.edit_text(f"Error: {str(e)}\n\nBhai check kar ki tera account is channel mein joined hai ya nahi.")

async def main():
    await userbot.start()
    await bot.start()
    print("🚀 BOT IS LIVE!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    Thread(target=run_web).start()
    loop.run_until_complete(main())
    
