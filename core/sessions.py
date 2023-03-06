from aiogram.client.session.aiohttp import AiohttpSession
from cachetools import TTLCache

from utils.session import ClientSession

bot_session = AiohttpSession()
bot_client_session = ClientSession()
private_messages_cache = TTLCache(maxsize=30000, ttl=1)
user_cache = TTLCache(maxsize=30000, ttl=60)
blocked_users_cache = TTLCache(maxsize=30000, ttl=30)
like_action_counter = TTLCache(maxsize=30000, ttl=1.7)
dashboard_cache = TTLCache(maxsize=100000, ttl=300)
post_counter_cache = TTLCache(maxsize=20000, ttl=120)


async def close():
    await bot_session.close()
    await bot_client_session.close()
