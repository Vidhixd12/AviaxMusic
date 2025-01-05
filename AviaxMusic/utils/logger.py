from pyrogram.enums import ParseMode
from AviaxMusic import app
from AviaxMusic.utils.database import is_on_off, blacklist_chat, blacklisted_chats
from config import LOG_GROUP_ID

import re
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Burmese Unicode range
BURMESE_PATTERN = r"[\u1000-\u109F]+"  # Unicode range for Burmese script


async def play_logs(message, streamtype):
    # Check if logging is enabled
    if await is_on_off(2):
        # Extract query safely
        query = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else "No Query"

        # Check if the chat is already blacklisted
        blacklisted_chats_list = await blacklisted_chats()
        if message.chat.id in blacklisted_chats_list:
            logger.info(f"Blocked chat '{message.chat.title}' attempted interaction. Ignored.")
            return

        # Check for Burmese language in the query
        if re.search(BURMESE_PATTERN, query):
            try:
                # Blacklist the chat
                blacklisted = await blacklist_chat(message.chat.id)
                if blacklisted:
                    logger.info(f"Chat '{message.chat.title}' blacklisted due to Burmese query.")

                # Notify the group before leaving
                await app.send_message(
                    chat_id=message.chat.id,
                    text="⚠️ This bot is restricted to Indian groups only. Please use another bot for your queries."
                )

                # Log the blacklisting to the log group
                log_text = f"""
#leftchat 🚫 <b>Blacklisted Burmese Group</b>

<b>ᴄʜᴀᴛ ɪᴅ :</b> <code>{message.chat.id}</code>
<b>ᴄʜᴀᴛ ɴᴀᴍᴇ :</b> {message.chat.title}
<b>ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.chat.username}

<b>ǫᴜᴇʀʏ :</b> {query}
<b>sᴛʀᴇᴀᴍᴛʏᴘᴇ :</b> {streamtype}
"""
                await app.send_message(
                    chat_id=LOG_GROUP_ID,
                    text=log_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

                # Leave the group
                await app.leave_chat(message.chat.id)
                logger.info(f"Left group '{message.chat.title}' due to Burmese query: {query}")
            except Exception as e:
                logger.error(f"Failed to leave chat '{message.chat.title}' (ID: {message.chat.id}): {str(e)}")
            return  # Exit function without processing further logs

        # Log normal queries in the log group if no Burmese detected
        logger_text = f"""
<b>{app.mention} ᴘʟᴀʏ ʟᴏɢ</b>

<b>ᴄʜᴀᴛ ɪᴅ :</b> <code>{message.chat.id}</code>
<b>ᴄʜᴀᴛ ɴᴀᴍᴇ :</b> {message.chat.title}
<b>ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.chat.username}

<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>
<b>ɴᴀᴍᴇ :</b> {message.from_user.mention}
<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}

<b>ǫᴜᴇʀʏ :</b> {query}
<b>sᴛʀᴇᴀᴍᴛʏᴘᴇ :</b> {streamtype}"""
        if message.chat.id != LOG_GROUP_ID:
            try:
                await app.send_message(
                    chat_id=LOG_GROUP_ID,
                    text=logger_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Exception as e:
                logger.error(f"Failed to send log for chat '{message.chat.title}': {str(e)}")

