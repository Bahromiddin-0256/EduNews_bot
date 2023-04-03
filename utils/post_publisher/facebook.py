import json
import aiohttp
from aiogram import Bot

from core.config import settings, BASE_DIR
from db.models import Post


async def download_and_get_url(post: Post, bot: Bot):
    if post.media_type == 'photo':
        path = '/static/temp/image.jpg'
    else:
        path = '/static/temp/video.mp4'

    await bot.download(file=post.media_id, destination=f"{BASE_DIR}{path}")
    return f"{settings.HOST}{path}"


async def upload_on_facebook(post: Post, bot: Bot):
    file_url = await download_and_get_url(post, bot)
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
    return await res.json()
