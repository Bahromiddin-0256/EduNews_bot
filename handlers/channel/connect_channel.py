from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION

from db.crud import get_user
from db.models import ConnectedChannel

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def test(update: ChatMemberUpdated):
    performer = await get_user(update.from_user)
    data = {
        'user': performer,
        'channel_id': str(update.chat.id),
        'channel_title': update.chat.title,
        'channel_username': update.chat.username,
    }
    await ConnectedChannel.create(**data)


@router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def test(update: ChatMemberUpdated):
    channel = await ConnectedChannel.get_or_none(channel_id=str(update.chat.id))
    if channel:
        await channel.delete()

