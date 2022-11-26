import datetime
import logging

from aiogram import Bot

from core.config import settings, media_points
from db.crud import update_points
from db.models import Post, PostLikes, ConnectedChannel
from keyboards.inline_markup import make_post_markup, post_approved_tm, make_url_markup
from utils.post_publisher.facebook import upload_on_facebook


async def publish_post(post: Post, bot: Bot):
    author = post.author
    counter = await PostLikes.create(post=post)
    context = await post.context()

    if post.media_type == 'photo':
        upload = await bot.send_photo(chat_id=settings.MAIN_CHANNEL_ID, photo=post.media_id, caption=context,
                                      reply_markup=make_post_markup(counter.pk, 0))
    else:
        upload = await bot.send_video(chat_id=settings.MAIN_CHANNEL_ID, video=post.media_id, caption=context,
                                      reply_markup=make_post_markup(counter.pk, 0))
    delta = media_points[post.media_type]

    post.url = upload.get_url()
    post.message_id = upload.message_id
    post.is_published = True
    post.published_at = datetime.datetime.now()
    await post.save()
    await update_points(post=post, delta=delta)

    try:
        facebook_upload = await upload_on_facebook(post, bot)
        logging.info(msg=facebook_upload)
        counter = await PostLikes.get(pk=counter.pk)
        post.facebook_url = f"https://facebook.com/{facebook_upload['id']}"
        await post.save()
        await bot.edit_message_reply_markup(chat_id=settings.MAIN_CHANNEL_ID, message_id=post.message_id,
                                            reply_markup=make_post_markup(counter.pk, number=counter.likes - delta,
                                                                          facebook_id=facebook_upload['id']))
    except Exception:
        logging.error("Couldn't upload on facebook:", exc_info=True)

    data = await post_approved_tm(author, post)
    await bot.send_message(chat_id=author.tg_id, **data)

    markup = make_url_markup(text='👍 Like', url=post.url)
    current_district = post.district
    linked_channels = await ConnectedChannel.all().prefetch_related('user__district')
    for channel in linked_channels:
        if channel.user.district == current_district:
            if post.media_type == 'photo':
                await bot.send_photo(chat_id=channel.channel_id, photo=post.media_id, caption=context,
                                     reply_markup=markup)
            else:
                await bot.send_video(chat_id=channel.channel_id, video=post.media_id, caption=context,
                                     reply_markup=markup)
