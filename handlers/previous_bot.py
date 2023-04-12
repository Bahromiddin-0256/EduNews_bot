from aiogram import Router, types


router = Router()


@router.message()
async def forward_to_new_bot(message: types.Message):
    await message.answer("🤖 Bot o'zgardi, iltimos yangi botdan foydalaning: \n\n👉 @Media_probot")