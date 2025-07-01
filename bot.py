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

# --------------------------
# Global State
# --------------------------
user_modes = {}          # stores user_id → mode
banned_users = set()     # stores banned user_ids

# --------------------------
# Combo Bot Class
# --------------------------
class ComboBot(Client):
    def __init__(self):
        super().__init__(
            name="combo_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=300,
            plugins=dict(root="plugins_default"),  # default fallback
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

# --------------------------
# Helper Path Switching
# --------------------------
def set_helper_path(mode):
    # Remove previous helper dirs
    sys.path = [
        p for p in sys.path if not p.endswith("helper_rename") and not p.endswith("helper_merge")
    ]

    helper_dir = "helper_rename" if mode == "rename" else "helper_merge"
    abs_helper = os.path.abspath(helper_dir)
    sys.path.insert(0, abs_helper)

    # Clear any cached helpers.* modules
    for modname in list(sys.modules.keys()):
        if modname.startswith("helpers."):
            del sys.modules[modname]

# --------------------------
# Mode Switching
# --------------------------
async def switch_mode(client, message, mode):
    user_id = message.from_user.id

    # Check ban
    if user_id in banned_users:
        await message.reply_text("🚫 You are banned from using this bot.")
        return

    user_modes[user_id] = mode
    set_helper_path(mode)

    try:
        client.plugins.clear()
        client.plugins.load("plugins_" + mode)
        await message.reply_text(f"✅ Mode set to **{mode.capitalize()}**.\nNow send your files!")

        # Send log to LOG_CHANNEL
        if Config.LOG_CHANNEL:
            await client.send_message(
                Config.LOG_CHANNEL,
                f"👤 User [{message.from_user.first_name}](tg://user?id={user_id}) set mode to **{mode}**."
            )
    except Exception as e:
        await message.reply_text("❌ Failed to load mode.")
        print(f"[Plugin load error]: {e}")
        if Config.LOG_CHANNEL:
            await client.send_message(
                Config.LOG_CHANNEL,
                f"⚠️ Error loading plugins for mode `{mode}`:\n`{e}`"
            )

# --------------------------
# Commands
# --------------------------

# /start
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await message.reply_text(
        f"Hello **{message.from_user.first_name}**!\n\n"
        "I'm a multifunction bot:\n"
        "📝 Rename Files\n"
        "🎬 Merge Videos, Audio, etc.\n\n"
        "Use /rename_on or /merge_on to choose your mode."
    )

# /rename_on
@bot.on_message(filters.command("rename_on") & filters.private)
async def rename_on(client, message):
    await switch_mode(client, message, "rename")

# /merge_on
@bot.on_message(filters.command("merge_on") & filters.private)
async def merge_on(client, message):
    await switch_mode(client, message, "merge")

# /ban
@bot.on_message(filters.command("ban") & filters.user(Config.ADMIN))
async def ban_user(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage:\n/ban user_id")
        return

    user_id = int(message.command[1])
    banned_users.add(user_id)
    await message.reply_text(f"🚫 User `{user_id}` banned.")

    if Config.LOG_CHANNEL:
        await client.send_message(
            Config.LOG_CHANNEL,
            f"🚫 User `{user_id}` has been banned."
        )

# /unban
@bot.on_message(filters.command("unban") & filters.user(Config.ADMIN))
async def unban_user(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage:\n/unban user_id")
        return

    user_id = int(message.command[1])
    banned_users.discard(user_id)
    await message.reply_text(f"✅ User `{user_id}` unbanned.")

    if Config.LOG_CHANNEL:
        await client.send_message(
            Config.LOG_CHANNEL,
            f"✅ User `{user_id}` has been unbanned."
        )

# /users
@bot.on_message(filters.command("users") & filters.user(Config.ADMIN))
async def list_users(client, message):
    text = "**👥 Users and Modes:**\n"
    for uid, mode in user_modes.items():
        text += f"• `{uid}` → **{mode}**\n"
    if not user_modes:
        text += "No users have selected a mode yet."

    await message.reply_text(text)

# fallback if user sends files before choosing mode
@bot.on_message((filters.document | filters.video | filters.audio | filters.photo) & filters.private)
async def warn_if_no_mode(client, message):
    user_id = message.from_user.id

    # Check ban
    if user_id in banned_users:
        await message.reply_text("🚫 You are banned from using this bot.")
        return

    if user_id not in user_modes:
        await message.reply_text(
            "❗ Please select a mode first:\n/rename_on or /merge_on"
        )

bot.run()
