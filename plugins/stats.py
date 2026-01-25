from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from info import ADMINS, MULTIPLE_DB
from Script import script

from database.users_chats_db import db
from database.ia_filterdb import Media, Media2, db as db_stats, db2 as db2_stats

from utils import get_size, get_readable_time
from bot import botStartTime

import psutil
from time import time
from logging_helper import LOGGER


# ==============================
# STATS TEXT BUILDER
# ==============================

async def build_stats_text():
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    file1 = await Media.count_documents()

    DB_SIZE = 512 * 1024 * 1024  # 512MB

    dbstats = await db_stats.command("dbStats")
    db_size = dbstats["dataSize"]
    free = DB_SIZE - db_size

    uptime = get_readable_time(time() - botStartTime)
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent()

    if MULTIPLE_DB is False:
        return script.STATUS_TXT.format(
            total_users,
            totl_chats,
            file1,
            get_size(db_size),
            get_size(free),
            uptime,
            ram,
            cpu
        )

    file2 = await Media2.count_documents()

    db2stats = await db2_stats.command("dbStats")
    db2_size = db2stats["dataSize"]
    free2 = DB_SIZE - db2_size

    return script.MULTI_STATUS_TXT.format(
        total_users,
        totl_chats,
        file1,
        get_size(db_size),
        get_size(free),
        file2,
        get_size(db2_size),
        get_size(free2),
        uptime,
        ram,
        cpu,
        int(file1) + int(file2)
    )


def stats_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="bot_stats")
            ],
            [
                InlineKeyboardButton("⟸ Back", callback_data="help")
            ]
        ]
    )


# ==============================
# 📊 STATS CALLBACK ONLY
# ==============================

@Client.on_callback_query(filters.regex("^bot_stats$"))
async def stats_callback(bot: Client, query: CallbackQuery):
    if query.from_user.id not in ADMINS:
        return await query.answer("Admins only!", show_alert=True)

    await query.answer()

    try:
        await query.message.edit_text("ᴀᴄᴄᴇꜱꜱɪɴɢ ꜱᴛᴀᴛᴜꜱ ᴅᴇᴛᴀɪʟꜱ...")
        text = await build_stats_text()
        await query.message.edit(text, reply_markup=stats_buttons())
    except Exception as e:
        await query.message.edit(f"<b>Stats Error:</b> <code>{e}</code>")
        LOGGER.error(e)
