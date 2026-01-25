import logging
import logging.config
from datetime import date, datetime
import pytz


from pyrogram import Client, __version__, types
from pyrogram.raw.all import layer
from pyrogram import utils as pyroutils

from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL
from utils import temp
from Script import script

# ---------------- LOGGING ----------------
logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

# ---------------- PEER ID FIX ----------------
pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999

# ---------------- BOT CLASS ----------------
class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=20,
            plugins={"root": "plugins"},
            sleep_threshold=5
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        await super().start()
        await Media.ensure_indexes()

        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = f"@{me.username}" if me.username else "No Username"

        logging.info(
            f"{me.first_name} started using Pyrogram v{__version__} (Layer {layer})"
        )
        logging.info(LOG_STR)
        logging.info(script.LOGO)

        tz = pytz.timezone("Asia/Kolkata")
        today = date.today()
        now = datetime.now(tz).strftime("%H:%M:%S %p")

        try:
            await self.send_message(
                chat_id=LOG_CHANNEL,
                text=script.RESTART_TXT.format(today, now)
            )
        except Exception as e:
            logging.error(f"LOG_CHANNEL error: {e}")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped successfully.")

# ---------------- RUN BOT ----------------

if __name__ == "__main__":
    Bot().run()
