import json

import aiohttp
from aiogram import Bot

from core.config import settings
from db.models import Post


async def upload_on_facebook(post: Post, bot: Bot):
    file_path = await bot.get_file(file_id=post.media_id)
    file_url = f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_path.file_path}"
    context = await post.context(fb=True)
    data = {
        'published': 'true',
        'access_token': settings.FACEBOOK_TOKEN,
    }

    if post.media_type == 'photo':
        url = f'https://graph.facebook.com/v15.0/{settings.FACEBOOK_PAGE_ID}/photos'
        data['message'] = context
        data['url'] = file_url
    else:
        url = f'https://graph.facebook.com/v15.0/{settings.FACEBOOK_PAGE_ID}/videos'
        data['description'] = context
        data['file_url'] = file_url
    session = aiohttp.ClientSession()
    res = await session.post(url=url, data=data)
    await session.close()
    return json.loads(await res.text())
