from aiogram import Router, types

from db.crud import show_user_stat
from db.models import User
from filters.common import TranslatedText

router = Router()


@router.message(TranslatedText('statistics'))
async def show_statistics(message: types.Message, user: User):
    data = await show_user_stat(user)
    await message.answer(text=data)
