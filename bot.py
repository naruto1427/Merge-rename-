import os
import sys
from datetime import datetime
from pytz import timezone
from pyrogram import Client, filters, __version__
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw.all import layer
from aiohttp import web
from config import Config
from route import web_server
# plugins_rename
from plugins_rename.start import start_handler as rename_start
from plugins_rename.rename import rename_file
from plugins_rename.save import save_thumb
from plugins_rename.delete import delete_thumb

# plugins_merge
from plugins_merge.start import start_handler as merge_start
from plugins_merge.commands import handle_files as merge_handle_files
from plugins_merge.thumb import save_thumbnail as merge_save_thumb
from plugins_merge.thumb import delete_thumbnail as merge_delete_thumb

# user_modes keeps track of each user's chosen mode
user_modes = {}

# add helpers folders to path
sys.path.insert(0, os.path.abspath("helper_rename"))
sys.path.insert(0, os.path.abspath("helper_merge"))

# Import handlers from rename plugins
from plugins_rename.start import start_handler as rename_start
from plugins_rename.rename import rename_file
from plugins_rename.save import save_thumb
from plugins_rename.delete import delete_thumb
# ...import other rename plugin functions you need

# Import handlers from merge plugins
from plugins_merge.start import start_handler as merge_start
from plugins_merge.commands import handle_files as merge_handle_files
from plugins_merge.thumb import save_thumbnail as merge_save_thumb
from plugins_merge.thumb import delete_thumbnail as merge_delete_thumb
# ...import other merge plugin functions you need

class ComboBot(Client):
    def __init__(self):
        super().__init__(
            name="combo_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=300,
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

# /start
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    mode = user_modes.get(user_id, "rename")
    if mode == "rename":
        await rename_start(client, message)
    elif mode == "merge":
        await merge_start(client, message)

# /mode
@bot.on_message(filters.command("mode") & filters.private)
async def mode_command(client, message):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Rename", callback_data="set_mode_rename"),
            InlineKeyboardButton("🎬 Merge", callback_data="set_mode_merge")
        ]
    ])
    await message.reply_text("Choose your working mode:", reply_markup=keyboard)

# Callback to set mode
@bot.on_callback_query(filters.regex(r"set_mode_(rename|merge)"))
async def set_mode(client, callback_query):
    mode = callback_query.data.split("_")[-1]
    user_id = callback_query.from_user.id
    user_modes[user_id] = mode

    await callback_query.answer(f"Mode set to {mode.capitalize()}")
    await callback_query.message.edit_text(
        f"✅ Mode set to **{mode.capitalize()}**.\nNow send your files!"
    )

# File upload handler (documents, videos, audio, photos)
@bot.on_message(
    (filters.document | filters.video | filters.audio | filters.photo)
    & filters.private
)
async def file_router(client, message):
    user_id = message.from_user.id
    mode = user_modes.get(user_id, "rename")

    if mode == "rename":
        await rename_file(client, message)
    elif mode == "merge":
        await merge_handle_files(client, message)
    else:
        await message.reply_text("❗ Please choose a mode first using /mode.")

# Optional: thumb handlers
@bot.on_message(filters.command(["savethumb", "setthumb"]) & filters.private)
async def save_thumb_handler(client, message):
    user_id = message.from_user.id
    mode = user_modes.get(user_id, "rename")

    if mode == "rename":
        await save_thumb(client, message)
    elif mode == "merge":
        await merge_save_thumb(client, message)

@bot.on_message(filters.command(["deletethumb"]) & filters.private)
async def delete_thumb_handler(client, message):
    user_id = message.from_user.id
    mode = user_modes.get(user_id, "rename")

    if mode == "rename":
        await delete_thumb(client, message)
    elif mode == "merge":
        await merge_delete_thumb(client, message)

bot.run()
