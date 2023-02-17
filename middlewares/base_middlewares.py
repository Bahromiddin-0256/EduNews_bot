from typing import *

from aiogram import BaseMiddleware

from aiogram.types import Message, CallbackQuery


from db.crud import get_user
from db.models import User
from core.config import settings

from utils.shortcuts import send_membership_alert


class PermissionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:

        user = data["user"]

        if user.is_member and user.registered:

            return await handler(event, data)
        else:

            await send_membership_alert(event, user)
            return


class AdminMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:

        user = data["user"]

        if user.tg_id in settings.ADMINS or user.is_superuser:
            return await handler(event, data)
        else:

            return


class DatabaseProviderMessage(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:

        user: User = await get_user(event.from_user, "district", "school")

        data["user"] = user

        return await handler(event, data)


class DatabaseProviderCallbackQuery(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:

        user: User = await get_user(event.from_user, "district", "school")

        data["user"] = user

        return await handler(event, data)
