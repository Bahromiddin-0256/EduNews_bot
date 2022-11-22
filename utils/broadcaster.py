from aiogram.types import Message
from core.config import logger


async def send_copy(message: Message, chat_id: int):
    try:
        await message.send_copy(chat_id=chat_id)
    except Exception as error:
        logger.error(error)
    else:
        return True
    return False
