from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

router = Router()


@router.message()
async def forward_to_new_bot(message: Message):
    await message.answer("🤖 Bot o'zgardi, iltimos yangi botdan foydalaning: \n\n👉 @Media_probot", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏩ Botga o'tish", url="https://t.me/Media_probot")
        ]
    ]))
