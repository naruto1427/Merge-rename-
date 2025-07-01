import feedparser
import asyncio
import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient
import logging

# --- Config ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))
MONGO_URI = os.getenv("MONGODB_URI")

# --- Mongo Setup ---
mongo = MongoClient(MONGO_URI)
db = mongo["nyaa_bot"]
admins_col = db["admins"]
sources_col = db["sources"]
config_col = db["config"]

# --- Global vars ---
latest_links = {}
bot = Bot(token=BOT_TOKEN)

# --- Load from DB ---
def get_admins():
    return set(x["user_id"] for x in admins_col.find())

def get_sources():
    return {x["name"]: x["url"] for x in sources_col.find()}

def get_quality():
    config = config_col.find_one({"_id": "quality"})
    return config["value"] if config else "1080p"

def set_quality(val):
    config_col.update_one({"_id": "quality"}, {"$set": {"value": val}}, upsert=True)

# --- Admin check ---
def is_admin(uid):
    return uid in get_admins()

# --- Feed Loop ---
async def check_feeds():
    while True:
        sources = get_sources()
        for name, url in sources.items():
            await check_uploader(name, url)
        await asyncio.sleep(60)

async def check_uploader(name, url):
    feed = feedparser.parse(url)
    if not feed.entries:
        return
    entry = feed.entries[0]
    title = entry.title
    link = entry.link
    size = entry.get("nyaa_size", "Unknown")
    quality = get_quality()

    if quality.lower() not in title.lower():
        return

    if link != latest_links.get(name):
        latest_links[name] = link
        msg = (
            f"📤 <b>{name}</b> uploaded:\n"
            f"<b>{title}</b>\n"
            f"💾 Size: <code>{size}</code>\n"
            f"<a href=\"{link}\">🔗 Torrent Link</a>"
        )
        try:
            await bot.send_message(chat_id=TARGET_CHAT_ID, text=msg, parse_mode='HTML')
        except Exception as e:
            print(f"Error sending message: {e}")

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Nyaa RSS Bot is online.")

async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    sources = get_sources()
    for name, url in sources.items():
        await check_uploader(name, url)
    await update.message.reply_text("🔄 Manual refresh done.")

async def addsource(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addsource <name> <rss_url>")
        return
    name, url = context.args[0], context.args[1]
    sources_col.update_one({"name": name}, {"$set": {"url": url}}, upsert=True)
    await update.message.reply_text(f"✅ Added source: {name}")

async def removesource(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /removesource <name>")
        return
    name = context.args[0]
    sources_col.delete_one({"name": name})
    await update.message.reply_text(f"❌ Removed source: {name}")

async def listsources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    sources = get_sources()
    text = "\n".join([f"{k}: {v}" for k, v in sources.items()]) or "No sources."
    await update.message.reply_text(f"📡 Current Sources:\n{text}")

async def setquality_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /setquality <value>")
        return
    q = context.args[0]
    set_quality(q)
    await update.message.reply_text(f"✅ Quality set to: {q}")

async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /addadmin <user_id>")
        return
    uid = int(context.args[0])
    admins_col.update_one({"user_id": uid}, {"$set": {"user_id": uid}}, upsert=True)
    await update.message.reply_text(f"✅ Added admin: {uid}")

async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /removeadmin <user_id>")
        return
    uid = int(context.args[0])
    admins_col.delete_one({"user_id": uid})
    await update.message.reply_text(f"❌ Removed admin: {uid}")

async def listadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    admins = get_admins()
    text = "\n".join(str(uid) for uid in admins) or "No admins."
    await update.message.reply_text(f"👑 Admins:\n{text}")

# --- Main ---
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("refresh", refresh))
    app.add_handler(CommandHandler("addsource", addsource))
    app.add_handler(CommandHandler("removesource", removesource))
    app.add_handler(CommandHandler("listsources", listsources))
    app.add_handler(CommandHandler("setquality", setquality_cmd))
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("removeadmin", removeadmin))
    app.add_handler(CommandHandler("admins", listadmins))
    asyncio.get_event_loop().create_task(check_feeds())
    app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_bot()