from aiogram import Dispatcher, Bot
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from core import sessions
from core.config import settings, redis
from handlers import router
from handlers.old_bot import router as forward_message_router


TELEGRAM_SERVER = TelegramAPIServer.from_base(settings.BOT_API_SERVER)

if settings.DEBUG is False:
    sessions.bot_session.api = TELEGRAM_SERVER

bot = Bot(token=settings.BOT_TOKEN, session=sessions.bot_session, parse_mode="HTML")
bot2 = Bot(token=settings.BOT2_TOKEN, parse_mode='HTML')

storage = RedisStorage(redis, key_builder=DefaultKeyBuilder(with_bot_id=True))

dp = Dispatcher(storage=storage)
dp2 = Dispatcher()

dp.include_router(router)
dp2.include_router(forward_message_router)
print(dp2.sub_routers)

if not settings.DEBUG:
    dp.shutdown.register(redis.close)
