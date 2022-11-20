from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from db.models import User, District
from localization.strings import get_all_languages, _

cancel_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚫 Cancel")]
    ],
    resize_keyboard=True
)


async def translated_button(user: User, key: str):
    back_button = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_(key, user.lang_code))]
        ],
        resize_keyboard=True
    )

    return back_button


async def languages_tm() -> dict:
    languages_list = get_all_languages()
    languages_title = [_("language", lang_id) for lang_id in languages_list]

    text = f"🈯️  <b>{' | '.join(languages_title)}</b>\n\n"
    text += "\n——————————————\n".join([_('language_choose', lang_id)
                                       for lang_id in languages_list])

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_('language_my', lang_id))
             for lang_id in languages_list],
        ],
        resize_keyboard=True,
    )
    return {'text': text, 'reply_markup': markup}


async def full_name_tm(user: User) -> dict:
    text = _('request_fullname_msg', user.lang_code)
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=user.tg_name)]
        ],
        resize_keyboard=True
    )
    if len(user.tg_name.split()) >= 2:
        return {'text': text, 'reply_markup': markup}
    else:
        return {'text': text, 'reply_markup': ReplyKeyboardRemove()}


async def contact_number_tm(user: User) -> dict:
    text = _('request_contact', user.lang_code)
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_('request_contact_btn', user.lang_code),
                               request_contact=True),
            ]
        ],
        resize_keyboard=True,
    )
    return {'text': text, 'reply_markup': markup}


async def district_tm(user: User) -> dict:
    text = _('request_district', user.lang_code)
    builder = ReplyKeyboardBuilder()
    districts = await District.all()
    for district in districts:
        builder.button(text=district.name)
    builder.adjust(2)

    return {'text': text, 'reply_markup': builder.as_markup(resize_keyboard=True)}


async def school_tm(user: User, district: District) -> dict:
    text = _('request_school', user.lang_code)
    builder = ReplyKeyboardBuilder()
    await district.fetch_related('schools')
    schools = await district.schools.all()
    for school in schools:
        builder.button(text=school.name)
    builder.adjust(2)
    builder.row(KeyboardButton(text=_('back', user.lang_code)))
    return {'text': text, 'reply_markup': builder.as_markup(resize_keyboard=True)}


async def main_menu_tm(user: User) -> dict:
    text = _('main_menu', user.lang_code)
    markup = ReplyKeyboardMarkup(
        row_width=2,
        keyboard=[
            [
                KeyboardButton(text=_('add_post', user.lang_code)),
            ],
            [
                KeyboardButton(text=_('my_posts', user.lang_code)),
                KeyboardButton(text=_('statistics', user.lang_code)),
            ],
            [
                KeyboardButton(text=_('settings', user.lang_code)),
                KeyboardButton(text=_('leave_comment', user.lang_code))
            ],
        ],
        resize_keyboard=True,
    )
    return {'text': text, 'reply_markup': markup}


async def settings_tm(user: User) -> dict:
    text = _('change_settings_msg', user.lang_code)
    markup = ReplyKeyboardMarkup(
        row_width=2,
        keyboard=[
            [
                KeyboardButton(text=_('change_language', user.lang_code)),
                KeyboardButton(text=_('change_full_name', user.lang_code)),
            ],
            [
                KeyboardButton(text=_('change_number', user.lang_code)),
                KeyboardButton(text=_('change_school', user.lang_code)),
            ],
            [
                KeyboardButton(text=_('back', user.lang_code)),
                KeyboardButton(text=_('my_linked_channels', user.lang_code))
            ]
        ],
        resize_keyboard=True,
    )
    return {'text': text, 'reply_markup': markup}
