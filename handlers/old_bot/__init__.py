from aiogram import Router

from .private import router as private_router
from .channel import router as channel_router
router = Router()

router.include_router(private_router)
router.include_router(channel_router)
