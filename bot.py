import os
import sys
import importlib
from datetime import datetime
from pytz import timezone
from pyrogram import Client, filters, __version__
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw.all import layer
from aiohttp import web
from config import Config
from route import web_server

user_modes = {}

class ComboBot(Client):
    def __init__(self):
        super().__init__(
            name="combo_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=300,
            plugins=dict(root="plugins_default"),  # fallback empty folder
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        self.uptime = Config.BOT_UPTIME

        if Config.WEBHOOK:
            app = web.AppRunner(await web_server())
            await app.setup()
            PORT = int(os.environ.get("PORT", 8000))
            await web.TCPSite(app, "0.0.0.0", PORT).start()

        print(f"✅ Bot {me.first_name} started.")

        for admin_id in Config.ADMIN:
            try:
                await self.send_message(admin_id, f"**{me.first_name} is online!**")
            except Exception as e:
                print(f"Error notifying admin {admin_id}: {e}")

        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time_ = curr.strftime('%I:%M:%S %p')
                await self.send_message(
                    Config.LOG_CHANNEL,
                    f"**Bot Restarted**\n\n📅 Date: `{date}`\n⏰ Time: `{time_}`\n🌐 Timezone: `Asia/Kolkata`\n\n"
                    f"🧪 Pyrogram v{__version__} (Layer {layer})"
                )
            except Exception as e:
                print(f"Error logging to LOG_CHANNEL: {e}")

    async def stop(self):
        await super().stop()
        print("Bot stopped.")

bot = ComboBot()

# Update helper import path based on mode
def set_helper_path(mode):
    # Remove old helper paths
    sys.path = [p for p in sys.path if not p.endswith("helper_rename") and not p.endswith("helper_merge")]

    # Add new helper path
    helper_folder = "helper_rename" if mode == "rename" else "helper_merge"
    sys.path.insert(0, os.path.abspath(helper_folder))

    # Clear previously cached modules under helpers.*
    for key in list(sys.modules):
        if key.startswith("helpers."):
            del sys.modules[key]

# /start command
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await message.reply_text(
        f"Hello **{message.from_user.first_name}**!\n\n"
        "I'm a multifunctional bot:\n"
        "🔹 Rename Files\n"
        "🔹 Merge Videos & Audios\n\n"
        "Use /mode to choose your mode."
    )

# /mode command
@bot.on_message(filters.command("mode") & filters.private)
async def mode_command(client, message):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Rename", callback_data="set_mode_rename"),
            InlineKeyboardButton("🎬 Merge", callback_data="set_mode_merge")
        ]
    ])
    await message.reply_text("Choose your working mode:", reply_markup=keyboard)

# Button handler
@bot.on_callback_query(filters.regex(r"set_mode_(rename|merge)"))
async def set_mode(client, callback_query):
    mode = callback_query.data.split("_")[-1]
    user_id = callback_query.from_user.id
    user_modes[user_id] = mode

    # Set helper path
    set_helper_path(mode)

    # Load correct plugin folder
    try:
        if mode == "rename":
            client.plugins.clear()
            client.plugins.load("plugins_rename")
        elif mode == "merge":
            client.plugins.clear()
            client.plugins.load("plugins_merge")

        await callback_query.answer(f"Mode set to {mode.capitalize()}")
        await callback_query.message.edit_text(f"✅ Mode set to **{mode.capitalize()}**.\nNow send your files.")
    except Exception as e:
        await callback_query.message.edit_text("❌ Failed to load mode.")
        print(f"[Plugin load error]: {e}")

# Fallback if user forgets to choose mode
@bot.on_message((filters.document | filters.video | filters.audio) & filters.private)
async def warn_if_no_mode(client, message):
    user_id = message.from_user.id
    if user_id not in user_modes:
        await message.reply_text("❗ Please select a mode first using /mode.")

bot.run()
