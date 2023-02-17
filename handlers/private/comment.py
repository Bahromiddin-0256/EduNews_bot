from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hpre

from core.config import settings
from db.models import User
from filters.common import TranslatedText
from filters.states import CommentState
from keyboards.reply_markup import translated_button, main_menu_tm
from localization.strings import _
from middlewares.base_middlewares import PermissionMiddleware
from utils.shortcuts import send_main_menu

router = Router()
router.message.middleware(PermissionMiddleware())


@router.message(TranslatedText('leave_comment'))
async def leave_comment(message: types.Message, user: User, state: FSMContext):
    text = _('send_your_comment', user.lang_code)
    markup = await translated_button(user, 'cancel')

    await message.answer(text=text, reply_markup=markup)
    await state.set_state(CommentState.input_comment)


@router.message(CommentState.input_comment, TranslatedText('cancel'))
async def back_to_main_menu(message: types.Message, user: User, state: FSMContext):
    await send_main_menu(message, user)
    await state.clear()


@router.message(CommentState.input_comment, F.content_type == 'text')
async def send_comment(message: types.Message, user: User, state: FSMContext):
    from core.misc import bot
    comment = f'💬 New feedback from {user.mention}\nID: <code>{user.tg_id}</code>\n\n{hpre(message.text)}'
    data = await main_menu_tm(user=user)
    data['text'] = _('comment_sent', user.lang_code)
    await message.answer(**data)
    await state.clear()
    for admin_id in settings.ADMINS:
        await bot.send_message(chat_id=admin_id, text=comment)
    admins = await User.filter(is_superuser=True)
    for admin in admins:
        if admin.tg_id not in settings.ADMINS:
            await bot.send_message(chat_id=admin.tg_id, text=comment)
