from aiogram import Router
from .forward import router as forward_router

from filters.chat_type import ChatTypes


class PrivateFilter(ChatTypes):
    chat_types = "private"


router = Router()

for observer_key in router.observers:
    router.observers[observer_key].filter(PrivateFilter())

router.include_router(forward_router)
