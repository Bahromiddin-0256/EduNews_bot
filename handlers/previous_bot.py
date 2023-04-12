from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from filters.chat_type import ChatTypes
from .channel import router as channel_router

class PrivateFilter(ChatTypes):
    chat_types = "private"

main_router = Router()
private_router = Router()

for observer_key in private_router.observers:
    private_router.observers[observer_key].filter(PrivateFilter())


@private_router.message()
async def forward_to_new_bot(message: types.Message):
    await message.answer("🤖 Bot o'zgardi, iltimos yangi botdan foydalaning: \n\n👉 @Media_probot", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏩ Botga o'tish", url="https://t.me/Media_probot")
        ]
    ]))

main_router.include_router(private_router)
main_router.include_router(channel_router)