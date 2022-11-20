from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.filters import LEAVE_TRANSITION, ChatMemberUpdatedFilter, JOIN_TRANSITION

from core.config import settings
from db.crud import get_user
from db.models import User
from filters.common import ChannelFilter
from keyboards.inline_markup import required_channels_tm
from localization.strings import _

router = Router()


@router.chat_member(ChannelFilter(channel=settings.REQUIRED_CHANNELS_IDS), ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def warn_user(event: ChatMemberUpdated):
    from misc import bot
    user: User = await get_user(event.from_user)

    user.is_member = False
    user.like_allowed = False
    await user.save()

    data = await required_channels_tm(user)
    data['text'] = _('left_action_reminder', user.lang_code)
    try:
        await bot.send_message(chat_id=user.tg_id, **data)
    except:
        pass


@router.chat_member(ChannelFilter(channel=settings.MAIN_CHANNEL_ID), ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def change_user_status(event: ChatMemberUpdated):
    user = await get_user(bot_user=event.new_chat_member.user)
    user.like_allowed = True
    await user.save()
