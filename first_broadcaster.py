# import asyncio
# from datetime import datetime
#
# from tortoise import Tortoise, run_async
#
# from db.crud import stat_info
# from db.models import Post, PostLikes
# from core.misc import bot
# from core.config import TORTOISE_ORM, BASE_DIR, settings
# from utils.facebook import upload_on_facebook
# from utils.post_publisher import publish_post
#
#
# async def test():
#     await Tortoise.init(config=TORTOISE_ORM)
#     post = await Post.get(id=49).prefetch_related('author', 'district', 'school')
#     print(post.created_at)
#     print(post.created_at.astimezone(tz=settings.TIME_ZONE) - datetime.now(tz=settings.TIME_ZONE))
#
#
# run_async(test())
import asyncio

from core.misc import bot
from users import var

var = [973021229]

file_id = "AgACAgIAAxkBAAEIySxjf1aZhondvi6qjOZXwoKzUjJFzwAC2cIxG6l6-UvSuQSDlRiyhQEAAwIAA3kAAysE"

text = """🤖 Bot ish faoliyatini yangi imkoniyatlar bilan boshladi

💬 Yuklamalaringiz facebook tarmog'iga ham yuklanadi

✅ Yuklamalaringizni tuman yoki maktab kanallariga ham chiqarish imkoni mavjuda

🤖 Botdan 3 xil
🇺🇿 O'zbek tili
🇷🇺 Rus tili
🇺🇸 Ingiliz tilida foydalanishingiz mumkin

Boshlash uchun 👉 /start 👈 ni bosing."""


async def start_broadcasting():
    print("Broadcast started...")
    users = var
    users_count = len(users)
    percent_range = int(users_count * .01)
    percent_range = percent_range if percent_range else 1
    count = 0
    blocked = 0
    other_reasons = 0
    try:
        for i in range(users_count):
            try:
                await bot.send_message(chat_id=users[i], text="Sorry for bothering you. that was a test")
                count += 1
            except Exception as exp:

                if exp.__str__() == 'Forbidden: bot was blocked by the user':
                    blocked += 1
                else:
                    other_reasons += 1
            k = i + 1
            if k % percent_range == 0:
                print(
                    f"Status: {k}/{users_count}, {int(k / users_count * 100)}%, ({blocked + other_reasons}) couldn't "
                    f"be sent, blocked: {blocked}")
            # await asyncio.sleep(.01)
    finally:
        print(f"Message has been sent to <b>{count}</b> users.")


loop = asyncio.new_event_loop()

loop.run_until_complete(start_broadcasting())
