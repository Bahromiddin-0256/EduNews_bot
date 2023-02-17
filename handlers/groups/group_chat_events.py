from aiogram import Router, F, types

from core.config import settings
from db.models import ConnectedChannel, User

router = Router()


@router.message(F.new_chat_members & (F.new_chat_members[0].username == settings.BOT_USERNAME))
async def new_grou_member(message: types.Message, user: User):
    chat = message.chat
    await ConnectedChannel.create(user=user, channel_id=chat.id, channel_title=chat.title,
                                  channel_username=chat.username, channel_type=chat.type)


@router.message(F.left_chat_member & (F.left_chat_member.username == settings.BOT_USERNAME))
async def left_group_member(message: types.Message):
    chat = await ConnectedChannel.get_or_none(channel_id=message.chat.id)
    if chat:
        await chat.delete()
