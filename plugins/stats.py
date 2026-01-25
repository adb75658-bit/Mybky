import time
import psutil
import info
import script 

from pymongo import MongoClient
from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# IMPORT YOUR EXISTING CONFIGS
from info import (
    DATABASE_URI,
    DATABASE_URI2,
    DATABASE_NAME,
    COLLECTION_NAME,
    MULTIPLE_DB
)

from script import MULTI_STATUS_TXT

# ────────────────────────
# START TIME
# ────────────────────────
START_TIME = time.time()

# ────────────────────────
# DATABASE CONNECTIONS
# ────────────────────────
db1 = MongoClient(DATABASE_URI)[DATABASE_NAME][COLLECTION_NAME]

db2 = None
if MULTIPLE_DB:
    db2 = MongoClient(DATABASE_URI2)[DATABASE_NAME][COLLECTION_NAME]

# ────────────────────────
# HELPERS
# ────────────────────────
def format_size(size):
    for unit in ("Bytes", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def stats_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔄 Rᴇғʀᴇsʜ", callback_data="bot_stats"),
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")
            ]
        ]
    )

# ────────────────────────
# CALLBACK HANDLER
# ────────────────────────
@Client.on_callback_query()
async def stats_callback(client, query):

    if query.data != "bot_stats":
        return

    await query.answer("Refreshing stats...")

    # BOT STATS
    users = await client.get_users_count()
    chats = await client.get_dialogs_count()

    # DB 1
    files1 = db1.count_documents({})
    size1 = sum(
        f.get("file_size", 0)
        for f in db1.find({}, {"file_size": 1})
    )
    free1 = (512 * 1024 * 1024) - size1

    # DB 2
    if MULTIPLE_DB and db2:
        files2 = db2.count_documents({})
        size2 = sum(
            f.get("file_size", 0)
            for f in db2.find({}, {"file_size": 1})
        )
        free2 = (512 * 1024 * 1024) - size2
    else:
        files2 = 0
        size2 = 0
        free2 = 0

    # SYSTEM STATS
    uptime = time.strftime(
        "%Hh %Mm %Ss",
        time.gmtime(time.time() - START_TIME)
    )

    text = MULTI_STATUS_TXT.format(
        users,
        chats,
        files1,
        format_size(size1),
        format_size(free1),
        files2,
        format_size(size2),
        format_size(free2),
        uptime,
        psutil.virtual_memory().percent,
        psutil.cpu_percent(),
        files1 + files2
    )

    await query.message.edit_text(
        text=text,
        reply_markup=stats_buttons(),
        parse_mode=enums.ParseMode.HTML
)
