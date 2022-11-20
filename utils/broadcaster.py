from aiogram.types import Message
from core.log_conf import logging

log = logging.getLogger('broadcaster')


async def send_copy(message: Message, chat_id: int):
    try:
        await message.send_copy(chat_id=chat_id)
    except Exception as error:
        log.error(f"Error [ID:{chat_id}]: {error}")
    else:
        return True
    return False
