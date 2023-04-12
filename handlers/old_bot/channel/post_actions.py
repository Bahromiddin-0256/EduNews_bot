from aiogram import Router
from aiogram.types import CallbackQuery
from core.config import settings
from filters.callback_data import LikeButton
from filters.common import ChannelFilter
from localization.strings import _

router = Router()


@router.callback_query(LikeButton.filter(), ChannelFilter(channel=[settings.MAIN_CHANNEL_ID]))
async def perform_like(call: CallbackQuery):
    await call.answer()
