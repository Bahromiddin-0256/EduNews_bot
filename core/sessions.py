from aiogram.client.session.aiohttp import AiohttpSession
from cachetools import TTLCache

from utils.session import ClientSession

bot_session = AiohttpSession()
bot_client_session = ClientSession()
private_messages_cache = TTLCache(maxsize=30000, ttl=1)
caches = TTLCache(maxsize=30000, ttl=10)
blocked_users_cache = TTLCache(maxsize=30000, ttl=30)
like_action_counter = TTLCache(maxsize=30000, ttl=1)
ranking_cache = TTLCache(maxsize=30000, ttl=120)


async def close():
    await bot_session.close()
    await bot_client_session.close()
