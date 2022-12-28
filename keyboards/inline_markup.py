from typing import Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hide_link

from core.config import settings
from db.models import User, Post
from filters.callback_data import PostAction, LikeButton, MyPosts
from localization.strings import _


def make_url_markup(text: str, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=[
            [
                InlineKeyboardButton(text=text, url=url)
            ]
        ]
    )


admin_contact = make_url_markup(text="👤 Admin", url="https://t.me/Javohirbek_uz")


def make_post_markup(counter_id: int, number: int, facebook_id: str = None):
    inline_keyboard = [
        [
            InlineKeyboardButton(text=f'👍 {number}',
                                 callback_data=LikeButton(counter_id=counter_id).pack()),
        ],
    ]
    if facebook_id:
        inline_keyboard.append([
            InlineKeyboardButton(text="🔗 Facebook", url=f"https://facebook.com/{facebook_id}")
        ])
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=inline_keyboard)


async def post_confirmation_markup(user: User) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1,
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(
                                              text=_('confirm', user.lang_code), callback_data='accept')
                                      ],
                                      [
                                          InlineKeyboardButton(
                                              text=_('restart', user.lang_code), callback_data='restart')
                                      ]
                                  ])
    return markup


async def post_confirmation_markup_admin(user: User, post: Post):
    markup = InlineKeyboardMarkup(row_width=1,
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text="✅ Approve",
                                                               callback_data=PostAction(post_id=post.pk,
                                                                                        action='accept').pack())
                                      ],
                                      [
                                          InlineKeyboardButton(text="🚫 Reject",
                                                               callback_data=PostAction(post_id=post.pk,
                                                                                        action='reject').pack())
                                      ]
                                  ])
    return markup


async def required_channels_tm(user: User) -> dict:
    text = _('membership_alert', user.lang_code)

    keyboard_list = []
    for i in range(len(settings.REQUIRED_CHANNELS_IDS)):
        keyboard_list.append([InlineKeyboardButton(text=settings.REQUIRED_CHANNELS_NAMES[i],
                                                   url=f"https://t.me/{settings.REQUIRED_CHANNELS_USERNAMES[i]}")])

    keyboard_list.append([InlineKeyboardButton(text=_('confirm', user.lang_code), callback_data='check_membership')])
    markup = InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=keyboard_list,
    )
    return {'text': text, 'reply_markup': markup}


async def my_posts_tm(user: User, index: int) -> Union[dict, None]:
    posts = await user.posts.filter(is_published=True).prefetch_related('counter', 'district', 'school')
    count = len(posts)

    if count == 0:
        return None

    post = posts[index]
    post: Post
    builder = InlineKeyboardBuilder()
    builder.adjust(3)
    builder.button(text=f'👍 {post.counter.last_updated_likes}', url=post.url)
    if index == 0:
        previous_button = "null"
    else:
        previous_button = MyPosts(index=index - 1).pack()
    if index == count - 1:
        next_button = "null"
    else:
        next_button = MyPosts(index=index + 1).pack()

    builder.row(
        InlineKeyboardButton(text="◀️",
                             callback_data=previous_button,
                             ),
        InlineKeyboardButton(text=f"{index + 1}/{count}",
                             callback_data="null",
                             ),
        InlineKeyboardButton(text="▶️",
                             callback_data=next_button,
                             )
    )
    builder.row(InlineKeyboardButton(text=_('share', user.lang_code),
                                     url=f"https://t.me/share/url?url={post.url}&text={post.title}"))

    caption = await post.context()
    print(builder.as_markup())
    if post.media_type == 'photo':
        return {'photo': post.media_id, 'caption': caption, 'reply_markup': builder.as_markup()}
    return {'video': post.media_id, 'caption': caption, 'reply_markup': builder.as_markup()}


async def post_approved_tm(user: User, post: Post) -> dict:
    text = f"{hide_link(url=post.url)}{_('post_approved', user.lang_code)}"
    builder = InlineKeyboardBuilder()
    builder.button(text=_('view', user.lang_code), url=post.url)
    builder.button(text=_('share', user.lang_code), url=f"https://t.me/share/url?url={post.url}&text={post.title}")
    builder.adjust(1)
    return {'text': text, 'reply_markup': builder.as_markup()}
