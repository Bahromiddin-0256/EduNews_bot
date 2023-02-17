import os

import uvicorn
from fastapi import Response, BackgroundTasks, Body, status, FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.template import templates
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from tortoise import Tortoise

import middlewares
from core import sessions
from core.config import settings, TORTOISE_ORM, admin_config, BASE_DIR, logger
from db.crud import stat_info, schools_stat_info, users_stat_info
from core.misc import bot, dp
import db.resources
import routes

app = FastAPI()
app.logger = logger

if settings.DEBUG:
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(BASE_DIR, "static")),
        name="static",
    )


@app.get("/")
async def overall_stat(
        request: Request,
):
    data = await stat_info()
    return templates.TemplateResponse(
        "index/index.html",
        context={
            "request": request,
            **data,
        },
    )


@app.get("/district/{district_id}/")
async def schools_stat(
        request: Request,
        district_id: int,
):
    data = await schools_stat_info(district_id=district_id)
    return templates.TemplateResponse(
        "index/school_ranking.html",
        context={
            "request": request,
            **data,
        },
    )


@app.get("/district/{district_id}/{school_id}")
async def schools_stat(
        request: Request,
        district_id: int,
        school_id: int,
):
    data = await users_stat_info(district_id=district_id, school_id=school_id)
    return templates.TemplateResponse(
        "index/user_ranking.html",
        context={
            "request": request,
            **data,
        },
    )


@app.on_event("startup")
async def on_startup():
    await Tortoise.init(config=TORTOISE_ORM)
    await admin_app.configure(**admin_config)
    if settings.DEBUG is False:
        webhook_url = settings.WEBHOOK_URL.format(token=settings.BOT_TOKEN)
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != webhook_url:
            await bot.set_webhook(
                webhook_url,
                drop_pending_updates=True,
                allowed_updates=settings.ALLOWED_UPDATES,
            )
    else:
        await bot.delete_webhook(drop_pending_updates=True)
    middlewares.setup(dp)


@app.on_event("shutdown")
async def on_shutdown():
    await Tortoise.close_connections()
    await sessions.close()


app.mount("/admin", admin_app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


async def feed_update(update):
    await dp.feed_raw_update(bot, update)


@app.post(settings.WEBHOOK_PATH, include_in_schema=False)
async def telegram_update(
        token: str, background_tasks: BackgroundTasks, update: dict = Body(...)
) -> Response:
    if token == bot.token:
        background_tasks.add_task(feed_update, update)
        return Response(status_code=status.HTTP_202_ACCEPTED)
    return Response(status_code=status.HTTP_401_UNAUTHORIZED)


if __name__ == "__main__":
    if settings.DEBUG:
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        dp.run_polling(bot, allowed_updates=settings.ALLOWED_UPDATES)
    else:
        uvicorn.run(
            "app:app",
            host="localhost",
            port=settings.PORT,
            workers=settings.WORKERS,
        )
