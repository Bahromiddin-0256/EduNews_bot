from fastapi import Depends
from fastapi_admin.app import app
from fastapi_admin.depends import get_resources, get_current_admin
from fastapi_admin.template import templates
from starlette.requests import Request
from fastapi_admin.exceptions import (
    forbidden_error_exception,
    not_found_error_exception,
    server_error_exception,
)
from starlette.responses import RedirectResponse, Response
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from core.config import settings
from db.models import User
from utils.exceptions import unauthorized_error_exception


async def read_document(path: str) -> str:
    try:
        with open(path, 'r') as doc:
            return ''.join(doc.readlines())
    except Exception:
        pass


async def write_config(data: str) -> str:
    try:
        with open('.env', 'w') as file:
            lines = data.split('\n')
            file.writelines(lines)
            file.close()
            return 'ok'
    except Exception as error:
        return error.__str__()


@app.get("/", dependencies=[Depends(get_current_admin)])
async def home(
        request: Request,
        resources=Depends(get_resources),
):
    return templates.TemplateResponse(
        "dashboard.html",
        context={
            "request": request,
            "resources": resources,
            "resource_label": "Dashboard",
            "page_pre_title": "overview",
            "page_title": "Dashboard"
        },
    )


@app.get("/config", dependencies=[Depends(get_current_admin)])
async def config(
        request: Request,
        resources=Depends(get_resources),
):
    return templates.TemplateResponse(
        "config.html",
        context={
            "request": request,
            "resources": resources,
            "resource_label": "Configuration",
            "page_pre_title": "overview",
            "page_title": "Environment variables",
            "config_data": (await read_document(path='.env'))
        },
    )


@app.post("/config", dependencies=[Depends(get_current_admin)])
async def config(
        request: Request,
        resources=Depends(get_resources),
):
    form = await request.form()
    data = form.get('configuration')
    result = await write_config(data)

    if result == 'ok':
        return templates.TemplateResponse(
            "config.html",
            context={
                "request": request,
                "resources": resources,
                "resource_label": "Configuration",
                "page_pre_title": "overview",
                "page_title": "Environment variables",
                "config_data": data
            },
        )
    return templates.TemplateResponse(
        "config.html",
        context={
            "request": request,
            "resources": resources,
            "resource_label": "Configuration",
            "page_pre_title": "overview",
            "page_title": "Environment variables",
            "config_data": data,
            "errors": result
        },
    )


@app.get("/logs", dependencies=[Depends(get_current_admin)])
async def logs(
        request: Request,
        resources=Depends(get_resources),
):
    return templates.TemplateResponse(
        "logs.html",
        context={
            "request": request,
            "resources": resources,
            "resource_label": "Logs",
            "page_pre_title": "overview",
            "page_title": "Logs",
            "errors": (await read_document(path=settings.LOGS_PATH))
        },
    )


@app.get("/logs/clear", dependencies=[Depends(get_current_admin)])
async def clear_logs(
        request: Request,
        resources=Depends(get_resources),
):
    try:
        with open(settings.LOGS_PATH, 'w') as f:
            f.close()
    except Exception:
        pass
    return RedirectResponse(url='/admin/logs/')


# http://127.0.0.1:8000/admin/user/change_post_permission/4
@app.post('/user/change_post_permission/{pk}', dependencies=[Depends(get_current_admin)])
async def change_post_permission(request: Request, pk: int):
    user = await User.get(pk=pk)
    user.post_permission = not user.post_permission
    await user.save()
    return Response(status_code=201)


app.add_exception_handler(HTTP_500_INTERNAL_SERVER_ERROR, server_error_exception)
app.add_exception_handler(HTTP_404_NOT_FOUND, not_found_error_exception)
app.add_exception_handler(HTTP_403_FORBIDDEN, forbidden_error_exception)
app.add_exception_handler(HTTP_401_UNAUTHORIZED, unauthorized_error_exception)
