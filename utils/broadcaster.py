from aiogram.types import Message


async def send_copy(message: Message, chat_id: int):
    try:
        await message.send_copy(chat_id=chat_id)
        return True
    except:
        return False
