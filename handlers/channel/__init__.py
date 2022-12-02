from aiogram import Router

from middlewares.base_middlewares import DatabaseProviderMessage, DatabaseProviderCallbackQuery
from .membership import router as membership_router
from .post_actions import router as post_actions_router
from .connect_channel import router as connect_channel_router

from filters.chat_type import ChatTypes


class ChannelFilter(ChatTypes):
    chat_types = 'channel'


router = Router()

for observer_key in router.observers:
    router.observers[observer_key].filter(ChannelFilter())

router.include_router(membership_router)
router.include_router(connect_channel_router)
router.include_router(post_actions_router)
