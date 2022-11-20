from datetime import datetime

import pytz
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from core.config import settings
from db.models import User, Post
from filters.common import TranslatedText
from filters.states import NewPostState
from keyboards.inline_markup import admin_contact, post_confirmation_markup, post_confirmation_markup_admin
from keyboards.reply_markup import translated_button, main_menu_tm
from localization.strings import _
from middlewares.base_middlewares import PermissionMiddleware
from utils.shortcuts import send_main_menu, post_text_maker

router = Router()
router.message.middleware(PermissionMiddleware())


@router.message(TranslatedText('add_post'))
async def new_post(message: types.Message, user: User, state: FSMContext):
    now = datetime.now(tz=pytz.timezone('Asia/Tashkent'))
    if not user.post_permission:
        await message.answer(text=_('contact_to_admin', user.lang_code), reply_markup=admin_contact)
        return
    # if today.weekday() == 6 or now.hour >= 22 or now.hour < 4:
    #     await message.answer(text=_('working_hours_alert', user.lang_code).format(name=user.full_name))
    #     return
    if len(await Post.filter(created_at__year=now.year, created_at__month=now.month,
                             created_at__day=now.day, author=user)) > 0:
        await message.answer(text=_('daily_limit_alert', user.lang_code))
        return
    await message.answer(text=_('enter_post_media', user.lang_code),
                         reply_markup=(await translated_button(user, 'cancel')))
    await state.set_state(NewPostState.media_upload)


@router.message(NewPostState.media_upload, TranslatedText('cancel'))
async def back_to_menu(message: types.Message, user: User, state: FSMContext):
    await send_main_menu(message, user)
    await state.clear()


@router.message(NewPostState.media_upload, F.content_type.in_({'document'}))
async def document_upload_alert(message: types.Message, user: User):
    await message.answer(text=_('file_upload_not_allowed', user.lang_code))


@router.message(NewPostState.media_upload, F.content_type.in_({'photo', 'video'}))
async def input_post_media(message: types.Message, user: User, state: FSMContext):
    if message.content_type == 'video':
        if message.video.file_size > 52428800:
            await message.answer(text=_('video_size_exceeded', user.lang_code))
            return
        else:
            await state.update_data(media_type='video')
            await state.update_data(media_id=message.video.file_id)
    else:
        await state.update_data(media_type='photo')
        await state.update_data(media_id=message.photo[-1].file_id)

    await message.answer(text=_('enter_post_title', user.lang_code))
    await state.set_state(NewPostState.title_input)


@router.message(NewPostState.title_input, F.content_type == 'text')
async def input_post_title(message: types.Message, user: User, state: FSMContext):
    if len(message.text) > 100:
        await message.answer(text=_('title_length_exceeded', user.lang_code))
        return
    else:
        await state.update_data(title=message.text)
        await message.answer(text=_('enter_post_description', user.lang_code))
        await state.set_state(NewPostState.description_input)


@router.message(NewPostState.description_input, F.content_type == 'text')
async def input_post_description(message: types.Message, user: User, state: FSMContext):
    if len(message.text) > 850:
        await message.answer(text=_('caption_too_long', user.lang_code))
        return
    data = await state.get_data()
    media_id = data['media_id']
    media_type = data['media_type']
    data['description'] = message.text
    data['district_name'] = user.district.name
    data['school_name'] = user.school.name
    await state.update_data(data)

    await message.answer(text=_('request_to_accept', user.lang_code))

    text = post_text_maker(data)
    markup = await post_confirmation_markup(user)

    if media_type == 'photo':
        await message.answer_photo(photo=media_id, caption=text, reply_markup=markup)
    elif media_type == 'video':
        await message.answer_video(video=media_id, caption=text, reply_markup=markup)
    await state.set_state(NewPostState.confirmation)


@router.callback_query(NewPostState.confirmation, F.data == 'restart')
async def restart_post_upload(call: types.CallbackQuery, user: User, state: FSMContext):
    await call.message.delete()
    await call.message.answer(text=_('enter_post_media', user.lang_code))
    await state.set_state(NewPostState.media_upload)


@router.callback_query(NewPostState.confirmation, F.data == 'accept')
async def confirm_post_creation(call: types.CallbackQuery, user: User, state: FSMContext):
    data = await state.get_data()
    media_id = data['media_id']
    media_type = data['media_type']
    data['author'] = user
    data['district'] = user.district
    data['school'] = user.school
    post: Post = await Post.create(**data)

    markup = await post_confirmation_markup_admin(user=user, post=post)
    notification_text = f"<b>User:</b>   {user.mention}\n\n" + (await post.context())

    from misc import bot
    if media_type == 'photo':
        await bot.send_photo(chat_id=settings.CONSIDERATION_CHANNEL_ID, photo=media_id, caption=notification_text,
                             reply_markup=markup)
    elif media_type == 'video':
        await bot.send_video(chat_id=settings.CONSIDERATION_CHANNEL_ID, video=media_id, caption=notification_text,
                             reply_markup=markup)

    await call.message.delete()
    data = await main_menu_tm(user=user)
    data['text'] = _('post_taken_to_consideration', user.lang_code)
    await call.message.answer(**data)
    await state.clear()
