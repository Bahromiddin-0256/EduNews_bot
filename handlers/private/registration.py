from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

from db.models import User, District, School
from filters.common import TranslatedText, full_name_validator
from filters.states import RegistrationState
from keyboards.reply_markup import (
    languages_tm,
    full_name_tm,
    contact_number_tm,
    district_tm,
    school_tm,
)
from localization.strings import get_language_code, _
from utils.shortcuts import (
    phone_number_validator,
    send_main_menu,
    send_membership_alert,
    check_channels,
)

router = Router()


@router.message(CommandStart())
async def start_command(message: types.Message, user: User, state: FSMContext):
    if not user.registered:
        if not user.lang_code:
            data = await languages_tm()
            await state.set_state(RegistrationState.language)
        elif not user.full_name:
            data = await full_name_tm(user)
            await state.set_state(RegistrationState.full_name)
        elif not user.contact_number:
            data = await contact_number_tm(user)
            await state.set_state(RegistrationState.contact_number)
        elif not user.district:
            data = await district_tm(user)
            await state.set_state(RegistrationState.district)
        elif not user.school:
            data = await school_tm(user, user.district)
            await state.set_state(RegistrationState.school)
        else:
            user.registered = True
            await user.save()
            return
        await message.answer(**data)
    else:
        if user.is_member:
            await send_main_menu(message, user)
            await state.clear()
        else:
            await send_membership_alert(message, user)


@router.message(RegistrationState.language, TranslatedText("language_my"))
async def set_language(message: types.Message, user: User, state: FSMContext):
    user.lang_code = get_language_code(key="language_my", text=message.text)
    await user.save()
    data = await full_name_tm(user)
    await message.answer(**data)
    await state.set_state(RegistrationState.full_name)


@router.message(RegistrationState.full_name)
async def set_full_name(message: types.Message, user: User, state: FSMContext):
    if await full_name_validator(message):
        user.full_name = message.text
        await user.save()
        data = await contact_number_tm(user)
        await message.answer(**data)
        await state.set_state(RegistrationState.contact_number)
    else:
        await message.answer(text=_("incorrect_full_name_format", user.lang_code))


@router.message(RegistrationState.contact_number, F.content_type == "contact")
async def set_phone_number(message: types.Message, user: User, state: FSMContext):
    phone_number = await phone_number_validator(message)
    if phone_number is None:
        await message.answer(text=_("incorrect_format_number", user.lang_code))
        return
    else:
        user.contact_number = phone_number
        await user.save()
        data = await district_tm(user)
        await message.answer(**data)
        await state.set_state(RegistrationState.district)


@router.message(RegistrationState.district)
async def set_district(message: types.Message, user: User, state: FSMContext):
    district = await District.get_or_none(name=message.text)
    if district is None:
        await message.answer(text=_("invalid_district", user.lang_code))
        return
    await state.update_data(district=district.name)
    data = await school_tm(user, district)
    await message.answer(**data)
    await state.set_state(RegistrationState.school)


@router.message(RegistrationState.school, TranslatedText("back"))
async def set_district(message: types.Message, user: User, state: FSMContext):
    data = await district_tm(user)
    await message.answer(**data)
    await state.set_state(RegistrationState.district)


@router.message(RegistrationState.school)
async def set_school(message: types.Message, user: User, state: FSMContext):
    data = await state.get_data()
    district = await District.get(name=data["district"])
    school = await School.get_or_none(district=district, name=message.text)

    if school is None:
        await message.answer(text=_("invalid_school", user.lang_code))
        return

    user.district = district
    user.school = school
    user.registered = True
    await user.save()
    _t = await message.answer(text="🔄", reply_markup=ReplyKeyboardRemove())
    await _t.delete()
    await send_membership_alert(message, user)
    await state.clear()


@router.callback_query(F.data == "check_membership")
async def check_membership(call: CallbackQuery, user: User, state: FSMContext):
    if user.is_member:
        await call.message.delete()
        return

    if not user.registered:
        await call.message.delete()

    status = await check_channels(user)
    if status:
        user.like_allowed = True
        user.is_member = True
        await user.save()
        await call.answer(text=_("membership_success", user.lang_code), show_alert=True)
        await call.message.delete()
        await send_main_menu(message=call.message, user=user)
        await state.clear()
    else:
        if user.is_member:
            user.is_member = False
            await user.save()
        await call.answer(text=_("membership_fail", user.lang_code), show_alert=True)
