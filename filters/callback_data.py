from aiogram.filters.callback_data import CallbackData


class PostAction(CallbackData, prefix='post_action'):
    post_id: int
    action: str


class LikeButton(CallbackData, prefix='like'):
    counter_id: int


class MyPosts(CallbackData, prefix='my_posts'):
    index: int
