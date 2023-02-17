from typing import Dict, List, Type

from aiogram import Dispatcher, BaseMiddleware

__all__ = [
    'setup'
]

__middlewares: Dict[str, List[Type[BaseMiddleware]]] = {
    "update": [],
    "message": [],
    "edited_message": [],
    "channel_post": [],
    "edited_channel_post": [],
    "inline_query": [],
    "chosen_inline_result": [],
    "callback_query": [],
    "shipping_query": [],
    "pre_checkout_query": [],
    "poll": [],
    "poll_answer": [],
    "my_chat_member": [],
    "chat_member": [],
    "chat_join_request": [],
    "error": [],
}


def setup(dp: Dispatcher):
    for _observer in __middlewares:
        for middleware in __middlewares[_observer]:
            dp.observers[_observer].middleware.register(middleware())
