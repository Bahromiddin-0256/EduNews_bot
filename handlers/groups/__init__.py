from aiogram import Router

from middlewares.base_middlewares import DatabaseProviderMessage, DatabaseProviderCallbackQuery
from .group_chat_events import router as group_event_router

from filters.chat_type import ChatTypes


class GroupFilter(ChatTypes):
    chat_types = ['group', 'supergroup']


router = Router()

for observer_key in router.observers:
    router.observers[observer_key].filter(GroupFilter())

router.include_router(group_event_router)
