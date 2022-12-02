import asyncio

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from db.models import User
from filters.common import CommentReply
from filters.states import AdminState
from keyboards.reply_markup import cancel_button, main_menu_tm
from utils.broadcaster import send_copy
from utils.shortcuts import send_main_menu
from middlewares.base_middlewares import AdminMessageMiddleware

router = Router()
router.message.middleware.register(AdminMessageMiddleware())


@router.message(F.content_type == "text", CommentReply())
async def comment_reply(message: types.Message, comment_author: User):
    await message.send_copy(chat_id=comment_author.tg_id)


@router.message(Command("broadcast"))
async def ask_broadcast_message(message: types.Message, state: FSMContext):
    await message.answer(
        text="Send your message to be broadcast:", reply_markup=cancel_button
    )
    await state.set_state(AdminState.input_broadcast_message)


@router.message(AdminState.input_broadcast_message, F.text == "🚫 Cancel")
async def cancel_broadcast(message: types.Message, user: User, state: FSMContext):
    await state.clear()
    await send_main_menu(message=message, user=user)


@router.message(
    AdminState.input_broadcast_message,
    F.content_type.in_(
        {"text", "audio", "photo", "video", "video_note", "location", "document"}
    ),
)
async def start_broadcasting(message: types.Message, user: User, state: FSMContext):
    await state.clear()
    broadcast_status = await message.answer("Broadcast started...")
    users = await User.all().exclude(pk=user.pk)
    users_count = len(users)
    percent_range = int(users_count * 0.01) * 5
    percent_range = percent_range if percent_range else 1
    count = 0
    try:
        for i in range(users_count):
            if await send_copy(message=message, chat_id=users[i].tg_id):
                count += 1
            k = i + 1
            if k % percent_range == 0 or i == users_count - 1:
                await broadcast_status.edit_text(
                    f"Status: {k}/{users_count}, {int(k / users_count * 100)}%"
                )
            await asyncio.sleep(0.05)
    finally:
        data = await main_menu_tm(user=user)
        data["text"] = f"Message has been sent to <b>{count}</b> users."
        await message.answer(**data)
