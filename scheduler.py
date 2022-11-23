from rocketry import Rocketry
from rocketry.conds import every
from tortoise import Tortoise

from core.config import settings, TORTOISE_ORM
from core.misc import bot
from db.models import Post
from utils.post_publisher.post_publisher import publish_post

app = Rocketry(config={"task_execution": "async"})


@app.task(every(f"{settings.POST_RANGE} seconds"))
async def check_for_unpublished_posts():
    await Tortoise.init(config=TORTOISE_ORM)
    remaining_posts = await Post.filter(status='approved', is_published=False) \
        .order_by('created_at').prefetch_related('author', 'district', 'school')
    if remaining_posts:
        await publish_post(post=remaining_posts[0], bot=bot)


if __name__ == '__main__':
    app.run()
