import asyncio
import json
import logging

from rocketry import Rocketry
from rocketry.conds import every
from tortoise import Tortoise

from core.config import settings, TORTOISE_ORM, media_points
from aioredis import Redis
from core.misc import bot
from db.crud import update_points
from db.models import Post, PostLikes
from keyboards.inline_markup import make_post_markup
from utils.post_publisher.post_publisher import publish_post

app = Rocketry(config={"task_execution": "async"})
redis = Redis.from_url(url=settings.REDIS_URL)
cache_key = "bot_caches:post_like_press"


async def on_startup():
    await Tortoise.init(config=TORTOISE_ORM)


def make_delta(values: list[bool]):
    trues = values.count(True)
    falses = values.count(False)
    return trues - falses


@app.task(every(f"{settings.POST_RANGE} seconds"))
async def check_for_unpublished_posts():
    remaining_posts = (
        await Post.filter(status="approved", is_published=False)
        .order_by("created_at")
        .prefetch_related("author", "district", "school")
    )
    if remaining_posts:
        await publish_post(post=remaining_posts[0], bot=bot)


@app.task(every("15 seconds"))
async def checker():
    req = await redis.lpop(cache_key)
    aggregate = {}

    while req is not None:
        if req:
            data = json.loads(req)
            if data["counter_id"] in aggregate:
                aggregate[data["counter_id"]].append(data["existence"])
            else:
                aggregate[data["counter_id"]] = [data["existence"]]
        req = await redis.lpop(cache_key)

    for counter_id, values in aggregate.items():
        counter = await PostLikes.get(pk=counter_id).prefetch_related("post")

        delta = make_delta(values)

        if not delta:
            return

        points = await update_points(post=counter.post, delta=delta)
        markup = make_post_markup(
            counter_id=counter_id,
            number=points - media_points[counter.post.media_type],
            facebook_id=counter.post.facebook_id(),
        )
        try:
            await bot.edit_message_reply_markup(
                chat_id=settings.MAIN_CHANNEL_ID,
                message_id=counter.post.message_id,
                reply_markup=markup,
            )
            asyncio.sleep(0.05)
        except Exception as error:
            logging.warning(msg=error.__str__())


if __name__ == "__main__":
    asyncio.run(on_startup())
    app.run()
