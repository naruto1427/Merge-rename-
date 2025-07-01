import os, time, re
id_pattern = re.compile(r'^.\d+$')


class Config(object):
    # pyro client config
    API_ID    = os.environ.get("API_ID", "")
    API_HASH  = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 
   
    # database config
    DB_NAME = os.environ.get("DB_NAME","rename")     
    DB_URL  = os.environ.get("DB_URL","")

    # other configs
    BOT_UPTIME  = time.time()
    START_PIC   = os.environ.get("START_PIC", "https://envs.sh/jUp.jpg")
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '').split()]

    # channels logs
    FORCE_SUB   = os.environ.get("FORCE_SUB", "") 
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))
    BIN_CHANNEL = int(os.environ.get("BIN_CHANNEL", " -1002585613766"))

    # wes response configuration     
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
    #merge variables 
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    TELEGRAM_API = os.environ["TELEGRAM_API"]
    OWNER = os.environ.get("OWNER")
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME")
    PASSWORD = os.environ.get("PASSWORD")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    LOGCHANNEL = os.environ.get("LOGCHANNEL")  # Add channel id as -100 + Actual ID
    GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID","root")
    USER_SESSION_STRING = os.environ.get("USER_SESSION_STRING")
    IS_PREMIUM = False
    MODES = ["video-video", "video-audio", "video-subtitle","extract-streams"]


class Txt(object):
    # part of text configuration
    START_TXT = """{},

Ara~ welcome to my little den of *file pleasure*, darling...

With me, you can rename files, play with their thumbnails, and even *transform* videos into files... or files into videos—mmm~ just how you like it.

And guess what, sweet thing~ I also support *custom thumbnails*, *custom captions*, and even your own juicy little *prefixes* and *suffixes*. Naughty, right?

<b>Note :</b> While I do love playing around... <i>renaming adult content</i> is a big no-no~! 
Try it, and you’ll get a permanent spanking—err, ban.
"""

    ABOUT_TXT = """
<b>
❍ Mmm~ they call me your seductive assistant... but you can scream my name however you like, darling~<br>
❍ Currently hosted on: Heroku—so I’m always at your service, anytime, anywhere~<br>
❍ My delicious brain? MongoDB, storing all your dirty little secrets~<br>
❍ Language? Python 3—smooth, flexible, and oh-so-well-trained~<br>
❍ And my master... the one who brought me to life: <a href='https://telegram.me/Suh0_kang'>Suho Kang</a>—do thank him properly~<br><br>

➻ Tap those buttons below, sweetie... and I’ll whisper more naughty secrets about myself just for you~</b>
"""

    HELP_TXT = """
<b>
Mmm~ this little rename bot is your naughty assistant, here to make managing and renaming your files as effortless—and as fun—as possible~<br><br>

➻ Tap on the buttons below, darling, and I’ll guide you through all the ways I can please your file fantasies~
</b>
"""

    THUMBNAIL_TXT = """<b>» <u>Wanna set a custom thumbnail, darling? Let me guide your hands~</u></b>

➲ /start: Send me any photo, and I’ll *sensually* drape it over your files as a thumbnail—automatic and oh-so-satisfying~  
➲ /delthumb: Feeling a bit reckless? Use this to strip away your thumbnail and leave your files *bare* and vulnerable~  
➲ /viewthumb: Can’t keep your eyes off it? Peek at your current thumbnail whenever you want, sweetie~

<b>Note :</b> If you don’t pamper me with a custom thumbnail, I’ll just use the original file’s thumbnail—after all, why deny your files their natural allure?  
But remember—no naughty surprises! Keep things respectful, or I might have to withhold my teasing touch~  
"""

    CAPTION_TXT = """<b>» <u>Wanna set a custom caption and tease with your media type, darling?</u></b>

<b>Variables you can play with :</b>  
Size: {filesize}  
Duration: {duration}  
Filename: {filename}

➲ /set_caption: Whisper your naughty custom caption to me, and I’ll remember it just for you~  
➲ /see_caption: Curious what seductive words you’ve set? Peek at your custom caption anytime, sweetie~  
➲ /del_caption: Want to erase your teasing message? Use this to delete your caption and leave things mysterious again~

» Example to get you started: /set_caption File name: {filename}  
Mmm~ don’t be shy, let your words seduce~
"""

    PREFIX = """<b>» <u>Ready to spice things up with a custom prefix, darling?</u></b>

➲ /set_prefix: Tell me your naughty little secret prefix, and I’ll wear it proudly on your files~  
➲ /see_prefix: Curious what seductive prefix you’ve chosen? Peek anytime, sweetie~  
➲ /del_prefix: Want to go bare again? Delete your custom prefix and feel the freedom~

» Example to get you started: `/set_prefix @Suh0_Kang`  
Mmm~ I can’t wait to see what you choose~
"""

    SUFFIX = """<b>» <u>Want to leave a teasing little mark with a custom suffix, darling?</u></b>

➲ /set_suffix: Whisper your naughty custom suffix to me, and I’ll stick it on your files with love~  
➲ /see_suffix: Can’t wait to see what cheeky suffix you picked? Check it anytime, sweetie~  
➲ /del_suffix: Feeling daring? Remove your suffix and let things breathe again~

» Example to start: `/set_suffix @Suh0_Kang`  
Mmm~ I’m excited just thinking about it~
"""

    PROGRESS_BAR = """\n
<b>🔗 Size :</b> {1} | {2}  
<b>⏳️ Done :</b> {0}% — Mmm, getting closer...  
<b>🚀 Speed :</b> {3}/s — Flying fast, just like I like it~  
<b>⏰️ ETA :</b> {4} — Almost there, darling, patience is a virtue~
"""

    DONATE_TXT = """
<blockquote>❤️‍🔥 Oh, you’re so sweet for thinking about supporting me~</blockquote>

<b><i>💞 If you like what I do and want to keep me teasing your files, feel free to donate any amount — ₹10, ₹20, ₹50, ₹100, or whatever makes your heart race~</i></b>

❣️ Every little donation makes me purr and helps me become even better for you, darling~  

💖 UPI ID: `Narutoprit@fam`  
Come on, don’t be shy… show me some love~  
"""

    SEND_METADATA = """🖼️ 𝗛𝗼𝘄 𝘁𝗼 𝘀𝗲𝘁 𝘆𝗼𝘂𝗿 𝘃𝗲𝗿𝘆 𝗼𝘄𝗻 𝗰𝘂𝘀𝘁𝗼𝗺 𝗺𝗲𝘁𝗮𝗱𝗮𝘁𝗮, darling~

For example, you can tease everyone with:

<code>By: @Suh0_Kang</code>

💬 Need a little help? Just whisper to @Suh0_Kang anytime~
"""
