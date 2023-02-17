from aiogram import Router

from .private import router as private_router
from .channel import router as channel_router
from .groups import router as group_router
from .error_handler import router as error_router
from middlewares.base_middlewares import DatabaseProviderCallbackQuery, DatabaseProviderMessage

router = Router()
router.message.middleware(DatabaseProviderMessage())
router.callback_query.middleware(DatabaseProviderCallbackQuery())

router.include_router(private_router)
router.include_router(channel_router)
router.include_router(group_router)
router.include_router(error_router)
