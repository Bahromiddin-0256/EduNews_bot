from aiogram import Router, types

from db.crud import show_user_stat
from db.models import User
from filters.common import TranslatedText
from middlewares.base_middlewares import PermissionMiddleware

router = Router()
router.message.middleware(PermissionMiddleware())


@router.message(TranslatedText('statistics'))
async def show_statistics(message: types.Message, user: User):
    data = await show_user_stat(user)
    await message.answer(text=data)
