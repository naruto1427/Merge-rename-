from pyrogram import Client, filters

@Client.on_message(filters.command("dummy"))
async def dummy(c, m):
    await m.reply_text("Default mode loaded.")
