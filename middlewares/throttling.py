from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from core.sessions import private_messages_cache


class ThrottlingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        if event.chat.id in private_messages_cache:
            return
        else:
            private_messages_cache[event.chat.id] = None
        return await handler(event, data)
