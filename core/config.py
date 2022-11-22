import os

from aioredis import Redis
from pydantic import BaseSettings, validator

from db.models import Admin
from utils.providers import LoginProvider
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    HOST: str
    SERVER_IP: str
    PORT: int
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

    @validator("WEBHOOK_URL")
    def webhook_url(cls, v, values: dict):
        host = values['HOST']
        if 'localhost' in host:
            host += f":{values['PORT']}"
        return f"{host}{values['WEBHOOK_PATH']}"

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
