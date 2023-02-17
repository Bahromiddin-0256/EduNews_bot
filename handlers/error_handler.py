from typing import Any

from aiogram import Router
from aiogram.handlers import ErrorHandler
import logging

router = Router()


@router.errors()
class MyHandler(ErrorHandler):
    async def handle(self) -> Any:
        logging.exception(
            "Cause unexpected exception %s: %s",
            self.exception_name,
            self.exception_message
        )
