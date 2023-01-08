import os
from typing import Type, List

from fastapi_admin.app import app
from fastapi_admin.enums import Method
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.resources import Dropdown, Link, Field, Model, Action
from fastapi_admin.widgets import inputs, displays, filters
from starlette.requests import Request
from tortoise import Model as db_model

from db import enums
from db.models import (
    District,
    Media,
    MediaCategory,
    School,
    User,
    Post,
    ConnectedChannel,
)
from core.config import BASE_DIR

upload = FileUpload(uploads_dir=os.path.join(BASE_DIR, "static", "uploads"))


class ForeignKeyDisplay(displays.Display):
    def __init__(self, model: Type[db_model], display_field: str = "name"):
        super().__init__()
        self.model_ = model
        self.display_field = display_field

    async def render(self, request: Request, value: int):
        if not value:
            return ""
        model_ = await self.model_.get(pk=value).values()
        url = f"/admin/{self.model_.__name__.lower()}/update/{value}"
        return f"<b><a href='{url}'>{model_[self.display_field]}</a></b>"


@app.register
class Dashboard(Link):
    label = "Dashboard"
    icon = "fas fa-home"
    url = "/admin"


@app.register
class UserResource(Model):
    label = "Users"
    icon = "fas fa-user"
    model = User
    filters = [
        filters.Search(
            name="full_name",
            label="Name",
            search_mode="contains",
            placeholder="Search for full name",
        ),
        filters.ForeignKey(model=District, name="district", label="District"),
        filters.ForeignKey(model=School, name="school", label="School"),
        filters.Enum(enum=enums.IsRegistered, name="registered", label="Is Registered"),
    ]
    fields = [
        Field(
            name="lang_code",
            label="Language",
            input_=inputs.Input(),
            display=displays.InputOnly(),
        ),
        "full_name",
        Field(
            name="tg_username",
            label="Telegram username",
            input_=inputs.Input(),
            display=displays.InputOnly(),
        ),
        Field(
            name="district_id",
            label="District",
            input_=inputs.ForeignKey(model=District),
            display=ForeignKeyDisplay(model=District, display_field="name"),
        ),
        Field(
            name="school_id",
            label="School",
            input_=inputs.ForeignKey(model=School),
            display=ForeignKeyDisplay(model=School, display_field="name"),
        ),
        "contact_number",
        "points",
        Field(
            name="is_superuser",
            label="Is Admin",
            input_=inputs.Switch(),
            display=displays.InputOnly(),
        ),
        Field(
            name="post_permission",
            label="Upload permission",
            input_=inputs.Switch(),
            display=displays.Boolean(),
        ),
    ]

    async def get_actions(self, request: Request) -> List[Action]:
        actions = await super().get_actions(request)
        switch_permission = Action(
            label="block",
            icon="ti ti-reload",
            name="change_post_permission",
            method=Method.POST,
        )
        show_posts = Action(
            label="posts",
            icon="ti ti-list",
            name="related_posts",
            method=Method.GET,
            ajax=False,
        )
        actions.append(switch_permission)
        actions.append(show_posts)
        return actions


@app.register
class Content(Dropdown):
    class DistrictResource(Model):
        label = "District"
        model = District
        fields = ["id", "name", "points"]

    class SchoolResource(Model):
        label = "School"
        model = School
        filters = [
            filters.ForeignKey(model=District, name="district", label="District")
        ]
        fields = [
            "id",
            Field(
                name="district_id",
                label="District",
                input_=inputs.ForeignKey(model=District),
                display=ForeignKeyDisplay(model=District, display_field="name"),
            ),
            "name",
            "points",
        ]

        async def get_actions(self, request: Request) -> List[Action]:
            actions = await super().get_actions(request)
            show_related_users = Action(
                label="users",
                icon="ti ti-list",
                name="show_users",
                method=Method.GET,
                ajax=False,
            )
            actions.append(show_related_users)
            return actions

    label = "Schools"
    icon = "fas fa-location-pin"
    resources = [DistrictResource, SchoolResource]


@app.register
class PostAdmin(Model):
    label = "Posts"
    icon = "fas fa-photo-film"
    model = Post
    filters = [filters.ForeignKey(model=User, name="author", label="User")]
    fields = [
        "status",
        Field(
            name="author_id",
            label="Author",
            input_=inputs.ForeignKey(model=User),
            display=ForeignKeyDisplay(model=User, display_field="full_name"),
        ),
        "title",
        Field(
            name="url",
            label="Telegram link",
            input_=inputs.Input(),
            display=displays.InputOnly(),
        ),
        Field(
            name="facebook_url",
            label="Facebook link",
            input_=inputs.Input(),
            display=displays.InputOnly(),
        ),
        "created_at",
    ]

    async def row_attributes(self, request: Request, obj: dict) -> dict:
        if obj["status"] == "waiting":
            return {"style": "background-color: rgb(245, 187, 61);"}
        elif obj["status"] == "approved" and obj["is_published"] is False:
            return {"style": "background-color: rgba(0, 255, 0, 0.5);"}
        else:
            return {"style": "background-color: rgb(0, 255, 0);"}


@app.register
class DigitalEducationAdmin(Dropdown):
    class MediaCategoryAdmin(Model):
        label = "Category"
        model = MediaCategory
        fields = ["id", "name"]

    class MediaAdmin(Model):
        label = "Media"
        model = Media
        filters = [filters.ForeignKey(model=MediaCategory, name='category', label='Category')]
        fields = [
            "id",
            Field(
                name="category_id",
                label="Category",
                input_=inputs.ForeignKey(model=MediaCategory),
                display=ForeignKeyDisplay(model=MediaCategory, display_field="name"),
            ),
            "title",
            "url",
        ]

    label = "Digital Education"
    icon = "fas fa-earth"
    resources = [MediaCategoryAdmin, MediaAdmin]


@app.register
class ConnectedChannelAdmin(Model):
    label = "Linked Channels"
    icon = "fas fa-link"
    model = ConnectedChannel
    fields = [
        "channel_title",
        "channel_username",
        "channel_type",
        Field(
            name="user_id",
            label="User",
            input_=inputs.ForeignKey(model=User),
            display=ForeignKeyDisplay(model=User, display_field="full_name"),
        ),
    ]


@app.register
class Configuration(Link):
    icon = "fas fa-sliders"
    label = "Configuration"
    url = "/admin/config"


@app.register
class Logs(Link):
    icon = "fas fa-bug"
    label = "Logs"
    url = "/admin/logs"
