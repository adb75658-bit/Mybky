from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from Script import script
from time import time
import psutil

from info import MULTIPLE_DB
from database import db, db2, Media, Media2
from utils import get_size, get_readable_time
from Script import botStartTime


@Client.on_callback_query(filters.regex("^bot_stats$"))
async def bot_stats_callback(bot, query):
    try:
        await query.answer("📊 Loading stats...")

        total_users = await db.total_users_count()
        total_chats = await db.total_chat_count()
        premium = await db.all_premium_users()

        file1 = await Media.count_documents()
        size = await db.get_db_size()
        free = 536870912 - size

        size = get_size(size)
        free = get_size(free)

        uptime = get_readable_time(time() - botStartTime)
        ram = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent()

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="bot_stats")],
            [InlineKeyboardButton("⟸ Back", callback_data="help")]
        ])

        if not MULTIPLE_DB:
            await query.message.edit_text(
                script.STATUS_TXT.format(
                    total_users,
                    total_chats,
                    premium,
                    file1,
                    size,
                    free,
                    uptime,
                    ram,
                    cpu
                ),
                reply_markup=buttons,
                disable_web_page_preview=True
            )
            return

        file2 = await Media2.count_documents()
        size2 = await db2.get_db_size()
        free2 = 536870912 - size2

        size2 = get_size(size2)
        free2 = get_size(free2)

        await query.message.edit_text(
            script.MULTI_STATUS_TXT.format(
                total_users,
                total_chats,
                premium,
                file1,
                size,
                free,
                file2,
                size2,
                free2,
                uptime,
                ram,
                cpu,
                int(file1) + int(file2)
            ),
            reply_markup=buttons,
            disable_web_page_preview=True
        )

    except Exception as e:
        print(e)
