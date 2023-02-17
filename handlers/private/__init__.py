from aiogram import Router
from middlewares.throttling import ThrottlingMiddleware
from .registration import router as registration_router
from .admin import router as admin_router
from .settings import router as settings_router
from .new_post import router as new_post_router
from .my_posts import router as my_posts_router
from .comment import router as comment_router
from .statistics import router as statistics_router
from .digital_education import router as digital_education_router

from filters.chat_type import ChatTypes


class PrivateFilter(ChatTypes):
    chat_types = "private"


router = Router()
router.message.middleware(ThrottlingMiddleware())

for observer_key in router.observers:
    router.observers[observer_key].filter(PrivateFilter())

router.include_router(admin_router)
router.include_router(registration_router)
router.include_router(settings_router)
router.include_router(new_post_router)
router.include_router(my_posts_router)
router.include_router(comment_router)
router.include_router(statistics_router)
router.include_router(digital_education_router)
