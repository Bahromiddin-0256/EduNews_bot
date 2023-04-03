from datetime import datetime

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from core.config import settings
from db.crud import check_active_posts, create_post
from db.models import User, Tournament, Post
from filters.common import TranslatedText
from filters.states import NewPostState, TournamentPostState
from keyboards.inline_markup import admin_contact, post_confirmation_markup, post_confirmation_markup_admin
from keyboards.reply_markup import translated_button, main_menu_tm, get_tournaments_list
from localization.strings import _
from middlewares.base_middlewares import PermissionMiddleware
from utils.shortcuts import send_main_menu, post_text_maker, check_tournament_name

router = Router()
router.message.middleware(PermissionMiddleware())


@router.message(TournamentPostState(), TranslatedText('cancel'))
async def back_to_menu(message: types.Message, user: User, state: FSMContext):
    await send_main_menu(message, user)
    await state.clear()
    

@router.message(TranslatedText('tournaments'))
async def post_for_tournament(message: types.Message, user: User, state: FSMContext):
    data = await get_tournaments_list(user=user)
    if data is None:
        await message.answer(text=_('no_active_tournaments', user.lang_code))
        return
    await message.answer(**data)
    await state.set_state(TournamentPostState.tournaments_list)
    

@router.message(TournamentPostState.tournaments_list, F.content_type == 'text')
async def input_tournament(message: types.Message, user: User, state: FSMContext):
    tournament: Tournament = await check_tournament_name(message.text)
    if tournament:
        existence = await tournament.participants.filter(author=user)
        if len(existence) != 0:
            await message.answer(_('already_participated', user.lang_code))
            return
        await state.update_data(tournament_id=tournament.id)
        await state.set_state(TournamentPostState.media_upload)
        await message.answer(text=_('enter_tournament_post_media', user.lang_code),
                             reply_markup=translated_button(user, 'cancel'))
    else:
        await message.answer(text=_('incorrect_tournament_name', user.lang_code))


@router.message(TournamentPostState.media_upload, F.content_type.in_({'document'}))
async def document_upload_alert(message: types.Message, user: User):
    await message.answer(text=_('file_upload_not_allowed', user.lang_code))


@router.message(TournamentPostState.media_upload, F.content_type.in_({'photo', 'video'}))
async def input_post_media(message: types.Message, user: User, state: FSMContext):
    if message.content_type == 'video':
        if message.video.file_size > 524288000:
            await message.answer(text=_('video_size_exceeded', user.lang_code))
            return
        else:
            await state.update_data(media_type='video')
            await state.update_data(media_id=message.video.file_id)
    else:
        await state.update_data(media_type='photo')
        await state.update_data(media_id=message.photo[-1].file_id)

    await message.answer(text=_('enter_post_title', user.lang_code))
    await state.set_state(TournamentPostState.title_input)


@router.message(TournamentPostState.title_input, F.content_type == 'text')
async def input_post_title(message: types.Message, user: User, state: FSMContext):
    if len(message.text) > 100:
        await message.answer(text=_('title_length_exceeded', user.lang_code))
        return
    else:
        await state.update_data(title=message.text)
        await message.answer(text=_('enter_post_description', user.lang_code))
        await state.set_state(TournamentPostState.description_input)


@router.message(TournamentPostState.description_input, F.content_type == 'text')
async def input_post_description(message: types.Message, user: User, state: FSMContext):
    if len(message.text) > 850:
        await message.answer(text=_('caption_too_long', user.lang_code))
        return

    data = await state.get_data()
    media_id = data['media_id']
    media_type = data['media_type']
    data['description'] = message.text
    await user.fetch_related('district', 'school')
    data['district_name'] = user.district.name
    data['school_name'] = user.school.name
    selected_tournament = await Tournament.get(id=data['tournament_id'])
    await state.update_data(data)

    request_message = await message.answer(text=_('request_to_accept', user.lang_code))
    await state.update_data(request_message_id=request_message.message_id)

    text = post_text_maker(data, tournament_name=selected_tournament.name)
    markup = await post_confirmation_markup(user)

    if media_type == 'photo':
        await message.answer_photo(photo=media_id, caption=text, reply_markup=markup)
    elif media_type == 'video':
        await message.answer_video(video=media_id, caption=text, reply_markup=markup)
    await state.set_state(TournamentPostState.confirmation)


@router.callback_query(TournamentPostState.confirmation, F.data == 'restart')
async def restart_post_upload(call: types.CallbackQuery, user: User, state: FSMContext):
    await call.message.delete()
    data = await get_tournaments_list(user=user)
    await call.message.answer(**data)
    await state.set_state(TournamentPostState.tournaments_list)


@router.callback_query(TournamentPostState.confirmation, F.data == 'accept')
async def confirm_post_creation(call: types.CallbackQuery, user: User, state: FSMContext):
    from core.misc import bot
    data = await state.get_data()
    media_id = data['media_id']
    media_type = data['media_type']
    data['author'] = user
    data['district'] = user.district
    data['school'] = user.school
    await call.message.delete()
    await bot.delete_message(chat_id=call.from_user.id, message_id=data['request_message_id'])
    await state.clear()
    post = await Post.create(**data)

    if post is None:
        await call.message.answer("Oops, Something went wrong.")
        await send_main_menu(call.message, user)
        return
    
    markup = await post_confirmation_markup_admin(user=user, post=post)
    notification_text = f"<b>User:</b>   {user.mention}\n\n" + (await post.context())

    if media_type == 'photo':
        await bot.send_photo(chat_id=settings.TOURNAMENT_CHECK_CHANNEL_ID, photo=media_id, caption=notification_text,
                             reply_markup=markup)
    elif media_type == 'video':
        await bot.send_video(chat_id=settings.TOURNAMENT_CHECK_CHANNEL_ID, video=media_id, caption=notification_text,
                             reply_markup=markup)

    data = await main_menu_tm(user=user)
    data['text'] = _('post_taken_to_consideration', user.lang_code)
    await call.message.answer(**data)
