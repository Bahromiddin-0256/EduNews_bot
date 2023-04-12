from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from db.models import User
from filters.callback_data import MyPosts
from filters.common import TranslatedText
from filters.states import MyPostsState
from keyboards.inline_markup import my_posts_tm
from keyboards.reply_markup import translated_button
from localization.strings import _
from middlewares.base_middlewares import PermissionMiddleware
from utils.shortcuts import send_main_menu
import logging

router = Router()
router.message.middleware(PermissionMiddleware())


@router.message(TranslatedText('my_posts'))
async def show_my_posts(message: types.Message, user: User, state: FSMContext):
    try:
        data = await my_posts_tm(user=user, index=0)
        if data is None:
            await message.answer(text=_('no_uploaded_posts', user.lang_code))
            return
        else:
            await message.answer(text=_('uploaded_posts', user.lang_code), reply_markup=translated_button(user, 'back'))
            if data.get('photo') is not None:
                _m = await message.answer_photo(**data)
            else:
                _m = await message.answer_video(**data)
            await state.update_data(message_id=_m.message_id)
            await state.set_state(MyPostsState.view)
    except Exception as er:
        print(er)


@router.callback_query(MyPostsState.view, F.data == 'null')
async def null_answer(call: CallbackQuery):
    await call.answer()


@router.callback_query(MyPostsState.view, MyPosts.filter())
async def change_current_post(call: CallbackQuery, user: User, callback_data: MyPosts, state: FSMContext):
    data = await my_posts_tm(user=user, index=callback_data.index)
    if data.get('photo') is not None:
        _m = await call.message.edit_media(media=types.input_media_photo.InputMediaPhoto(media=data['photo'], caption=data['caption']), reply_markup=data['reply_markup'])
    else:
        _m = await call.message.edit_media(media=types.input_media_video.InputMediaVideo(media=data['video'], caption=data['caption']), reply_markup=data['reply_markup'])
    await state.update_data(message_id=_m.message_id)


@router.message(MyPostsState.view, TranslatedText('back'))
async def go_back(message: types.Message, user: User, state: FSMContext):
    from core.misc import bot
    data = await state.get_data()
    msg_id = data['message_id']
    await bot.delete_message(chat_id=user.tg_id, message_id=msg_id)
    await send_main_menu(message, user)
