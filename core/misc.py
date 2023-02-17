from aiogram import Dispatcher, Bot
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from core import sessions
from core.config import settings, redis
from handlers import router

TELEGRAM_SERVER = TelegramAPIServer.from_base(settings.BOT_API_SERVER)

if settings.DEBUG is False:
    sessions.bot_session.api = TELEGRAM_SERVER

bot = Bot(token=settings.BOT_TOKEN, session=sessions.bot_session, parse_mode="HTML")

storage = RedisStorage(redis, key_builder=DefaultKeyBuilder(with_bot_id=True))

dp = Dispatcher(storage=storage)

dp.include_router(router)

if not settings.DEBUG:
    dp.shutdown.register(redis.close)
