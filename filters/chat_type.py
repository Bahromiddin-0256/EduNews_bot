from typing import List, Union

from aiogram import types
from aiogram.filters import BaseFilter


class ChatTypes(BaseFilter):
    chat_types: Union[str, list]

    async def __call__(self, event: types.TelegramObject, event_chat: types.Chat = None) -> bool:
        if isinstance(self.chat_types, str):
            return event_chat.type == self.chat_types
        else:
            return event_chat.type in self.chat_types
