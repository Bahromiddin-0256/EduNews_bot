from aiogram import Router, types
from .channel.post_actions import router as channel_router

router = Router()
router.include_router(channel_router)


@router.message()
async def forward_to_new_bot(message: types.Message):
    await message.answer("🤖 Bot o'zgardi, iltimos yangi botdan foydalaning: \n\n👉 https://t.me/Media_probot")