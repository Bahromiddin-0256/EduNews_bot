import os

import pytz
from aioredis import Redis
from pydantic import BaseSettings, validator

from core.logger import CustomizeLogger
from db.models import Admin
from utils.providers import LoginProvider
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    WORKERS: int = 1
    HOST: str
    PORT: int
    WEBHOOK_HOST: str
    WEBHOOK_PATH: str = "/bot{token}"
    WEBHOOK_URL: str = None
    BOT_TOKEN: str
    BOT_USERNAME: str
    FACEBOOK_PAGE_ID: int
    FACEBOOK_TOKEN: str
    BOT_API_SERVER: str
    ALLOWED_UPDATES: list = ['message', 'edited_message', 'channel_post', 'edited_channel_post', 'inline_query',
                             'chosen_inline_result', 'callback_query', 'shipping_query', 'pre_checkout_query', 'poll',
                             'poll_answer', 'my_chat_member', 'chat_member', 'chat_join_request']
    ADMINS: list = []
    CONSIDERATION_CHANNEL_ID: int
    MAIN_CHANNEL_ID: int
    REQUIRED_CHANNELS_IDS: list = []
    REQUIRED_CHANNELS_USERNAMES: list = []
    REQUIRED_CHANNELS_NAMES: list = []
    REDIS_URL: str
    DATABASE: str
    DATABASE_HOST: str = 'localhost'
    DATABASE_PORT: str = 5432
    DATABASE_USER: str = 'postgres'
    DATABASE_PASSWORD: str
    DEBUG: bool
    TIME_ZONE: str = 'Asia/Tashkent'
    POST_RANGE: int
    LOGS_PATH: str
    LOG_LEVEL: str

    @validator("WEBHOOK_URL")
    def webhook_url(cls, v, values: dict) -> str:
        host = values['WEBHOOK_HOST']
        if 'localhost' in host:
            host += f":{values['PORT']}"
        return f"{host}{values['WEBHOOK_PATH']}"

    @validator("TIME_ZONE")
    def time_zone(cls, v: str):
        return pytz.timezone(zone=v)

    class Config:
        env_file = '.env'
        enf_file_encoding = 'utf-8'


settings = Settings()
redis: Redis = Redis.from_url(settings.REDIS_URL)

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": settings.DATABASE_HOST,
                "database": settings.DATABASE,
                "port": settings.DATABASE_PORT,
                "user": settings.DATABASE_USER,
                "password": settings.DATABASE_PASSWORD,
            }
        }
    },
    "apps": {
        "models": {
            "models": ["db.models", "aerich.models"],
            "default_connection": "default",
        }
    },
    'user_tz': True,
    'timezone': settings.TIME_ZONE.__str__()
}

admin_config = {
    "logo_url": "https://preview.tabler.io/static/logo-white.svg",
    "template_folders": [os.path.join(BASE_DIR, "templates")],
    "favicon_url": "https://raw.githubusercontent.com/fastapi-admin/fastapi-admin/dev/images/favicon.png",
    "providers": [
        LoginProvider(
            login_logo_url="https://preview.tabler.io/static/logo.svg",
            admin_model=Admin,
        )
    ],
    "redis": redis,
    "language_switch": False,
}

logger_config = {
    "logger": {
        "path": settings.LOGS_PATH,
        "level": settings.LOG_LEVEL,
        "rotation": "20 days",
        "retention": "1 months",
        "format": "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - <cyan>{"
                  "name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level> "

    }
}

logger = CustomizeLogger.make_logger(config=logger_config)
