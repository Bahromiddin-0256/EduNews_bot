from typing import Union, List, Dict, Any

from aiogram.filters import Filter
from aiogram.types import Message, ChatMemberUpdated, CallbackQuery

from core.config import settings
from db.models import User
from localization.strings import check_for_translation


async def full_name_validator(message: Message) -> bool:
    async def is_valid(text: str):
        for ch in text:
            if ch.isalpha() or ch == "'":
                continue
            else:
                return False
        return True

    full_name = message.text.split()
    return len(full_name) == 2 and (await is_valid(full_name[0])) and (await is_valid(full_name[1]))


class TranslatedText(Filter):
    def __init__(self, key: str) -> None:
        self.key = key

    async def __call__(self, message: Message) -> bool:
        return await check_for_translation(key=self.key, text=message.text)


class IsAdmin(Filter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        return event.from_user.id in settings.ADMINS


class CommentReply(Filter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        if not message.reply_to_message or not message.reply_to_message.entities:
            return False
        for entity in message.reply_to_message.entities:
            if entity.type == 'code':
                try:
                    user_id = entity.extract_from(message.reply_to_message.text)
                    user = await User.get_or_none(tg_id=int(user_id))
                    if not user:
                        return False
                    else:
                        return {'comment_author': user}
                except:
                    return False
        return False


class ChannelFilter(Filter):
    def __init__(self, channel: Union[int, List[int]]):
        if isinstance(channel, int):
            self.channel = [channel]
        else:
            self.channel = channel

    async def __call__(self, event: Union[ChatMemberUpdated, CallbackQuery, Message]) -> bool:
        if isinstance(event, CallbackQuery):
            event = event.message
        return event.chat.id in self.channel
