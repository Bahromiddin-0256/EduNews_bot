import json

from aiogram import Router
from aiogram.types import CallbackQuery

from core.sessions import blocked_users_cache, like_action_counter
from db.crud import get_counter
from db.models import User, Post
from core.config import settings, redis
from filters.callback_data import LikeButton
from filters.common import ChannelFilter
from localization.strings import _

router = Router()


@router.callback_query(LikeButton.filter(), ChannelFilter(channel=[settings.MAIN_CHANNEL_ID, settings.TOURNAMENT_CHECK_CHANNEL_ID]))
async def perform_like(call: CallbackQuery, user: User, callback_data: LikeButton):
    if not user.like_allowed:
        await call.answer(text=_('join_alert', user.lang_code), show_alert=True)
        return
    block_list_key = f'like_blocked:{user.tg_id}:{callback_data.counter_id}'

    if block_list_key in blocked_users_cache:
        await call.answer(text=_('too_many_requests', user.lang_code), show_alert=True)
        blocked_users_cache[block_list_key] = True
        return

    like_pressed_key = f'liked:{user.tg_id}:{callback_data.counter_id}'
    if like_pressed_key in like_action_counter:
        blocked_users_cache[block_list_key] = True
        await call.answer(text=_('too_many_requests', user.lang_code), show_alert=True)
        return
    like_action_counter[like_pressed_key] = True

    counter, existence = await get_counter(callback_data.counter_id, user=user)

    if existence:
        text = _('like_taken', user.lang_code)
    else:
        text = _('liked', user.lang_code)

    data = {
        'counter_id': counter.pk,
        'existence': existence,
    }
    await redis.rpush("bot_caches:post_like_press", json.dumps(data))
    await call.answer(text=text, show_alert=True)
