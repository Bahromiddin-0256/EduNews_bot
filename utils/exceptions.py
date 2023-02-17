from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse


async def unauthorized_error_exception(request: Request, exc: HTTPException):
    return RedirectResponse(url="/admin/login")
