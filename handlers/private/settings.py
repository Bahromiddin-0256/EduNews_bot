from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.markdown import hlink

from db.models import User, District, School, ConnectedChannel
from filters.common import TranslatedText, full_name_validator
from filters.states import SettingsState
from keyboards.reply_markup import settings_tm, languages_tm, translated_button, full_name_tm, contact_number_tm, \
    district_tm, school_tm
from localization.strings import get_language_code, _
from middlewares.base_middlewares import PermissionMiddleware
from utils.shortcuts import phone_number_validator, send_main_menu

router = Router()
router.message.middleware(PermissionMiddleware())


async def send_main_settings(message: types.Message, user: User, state: FSMContext) -> None:
    data = await settings_tm(user)

    await message.answer(**data)
    await state.set_state(SettingsState.main_settings)


@router.message(TranslatedText('settings'))
async def open_settings(message: types.Message, user: User, state: FSMContext):
    await send_main_settings(message, user, state)


@router.message(SettingsState.main_settings, TranslatedText('back'))
async def set_district(message: types.Message, user: User, state: FSMContext):
    await send_main_menu(message, user)


@router.message(SettingsState(), TranslatedText('cancel'))
async def back_to_main_settings(message: types.Message, user: User, state: FSMContext):
    data = await settings_tm(user)

    await message.answer(**data)
    await state.set_state(SettingsState.main_settings)


@router.message(SettingsState.main_settings, TranslatedText('change_language'))
async def change_language(message: types.Message, user: User, state: FSMContext):
    data = await languages_tm()

    data['reply_markup'].keyboard.append((await translated_button(user, 'cancel')).keyboard[0])
    await message.answer(**data)
    await state.set_state(SettingsState.language)


@router.message(SettingsState.language, TranslatedText('language_my'))
async def set_language(message: types.Message, user: User, state: FSMContext):
    user.lang_code = get_language_code(key='language_my', text=message.text)
    await user.save()
    await message.answer(_('language_changed', user.lang_code))
    await send_main_settings(message, user, state)


@router.message(SettingsState.main_settings, TranslatedText('change_full_name'))
async def change_language(message: types.Message, user: User, state: FSMContext):
    data = await full_name_tm(user)

    if data['reply_markup'] is not list:
        data['reply_markup'] = await translated_button(user, 'cancel')

    else:
        data['reply_markup'].keyboard.append((await translated_button(user, 'cancel')).keyboard[0])

    await message.answer(**data)
    await state.set_state(SettingsState.full_name)


@router.message(SettingsState.full_name)
async def set_full_name(message: types.Message, user: User, state: FSMContext):
    if await full_name_validator(message):
        user.full_name = message.text
        await user.save()
        await message.answer(_('full_name_changed', user.lang_code).format(new_full_name=message.text),
                             reply_markup=ReplyKeyboardRemove())
        await send_main_settings(message, user, state)
    else:
        await message.answer(text=_('incorrect_full_name_format', user.lang_code))


@router.message(SettingsState.main_settings, TranslatedText('change_number'))
async def change_language(message: types.Message, user: User, state: FSMContext):
    data = await contact_number_tm(user)

    data['reply_markup'].keyboard.append((await translated_button(user, 'cancel')).keyboard[0])

    await message.answer(**data)
    await state.set_state(SettingsState.phone_number)


@router.message(SettingsState.phone_number, F.content_type == 'contact')
async def set_phone_number(message: types.Message, user: User, state: FSMContext):
    phone_number = await phone_number_validator(message)
    if phone_number is None:
        await message.answer(text=_('incorrect_format_number', user.lang_code))
        return
    else:
        user.contact_number = phone_number
        await user.save()
        await message.answer(text=_('phone_number_changed', user.lang_code).format(new_number=phone_number))
        await send_main_settings(message, user, state)


@router.message(SettingsState.main_settings, TranslatedText('change_school'))
async def change_language(message: types.Message, user: User, state: FSMContext):
    data = await district_tm(user)

    data['reply_markup'].keyboard.append((await translated_button(user, 'cancel')).keyboard[0])

    await message.answer(**data)
    await state.set_state(SettingsState.district)


@router.message(SettingsState.district)
async def set_district(message: types.Message, user: User, state: FSMContext):
    district = await District.get_or_none(name=message.text)
    if district is None:
        await message.answer(text=_('invalid_district', user.lang_code))
        return
    await state.update_data(district=district.name)
    data = await school_tm(user, district)
    data['reply_markup'].keyboard.append((await translated_button(user, 'cancel')).keyboard[0])
    await message.answer(**data)
    await state.set_state(SettingsState.school)


@router.message(SettingsState.school, TranslatedText('back'))
async def set_district(message: types.Message, user: User, state: FSMContext):
    data = await district_tm(user)
    await message.answer(**data)
    data['reply_markup'].keyboard.append((await translated_button(user, 'cancel')).keyboard[0])
    await state.set_state(SettingsState.district)


@router.message(SettingsState.school)
async def set_school(message: types.Message, user: User, state: FSMContext):
    data = await state.get_data()
    district = await District.get(name=data['district'])
    school = await School.get_or_none(district=district, name=message.text)

    if school is None:
        await message.answer(text=_('invalid_school', user.lang_code))
        return

    user.district = district
    user.school = school
    await user.save()
    await message.answer(
        text=_('school_changed', user.lang_code).format(district_name=district.name, school_name=message.text))
    await send_main_settings(message, user, state)


@router.message(SettingsState.main_settings, TranslatedText('my_linked_channels'))
async def change_language(message: types.Message, user: User):
    my_joined_channels = await ConnectedChannel.filter(user=user)
    if len(my_joined_channels) == 0:
        await message.answer(text=_('no_added_channels', user.lang_code))
    else:
        text = "\n\n".join(
            [hlink(title=channel.channel_title, url=f'https://t.me/{channel.channel_username}') for channel in
             my_joined_channels])
        text = _('channels_you_added', user.lang_code) + text
        await message.answer(text=text)
