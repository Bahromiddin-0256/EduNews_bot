from datetime import datetime
from typing import Union

from aiogram import types

from core.config import settings
from core.sessions import user_cache, ranking_cache, post_counter_cache
from db.models import User, PostLikes, Post, District, School
from localization.strings import _


def get_current_time(format_: str = "%d/%m/%Y, %H:%M"):
    now = datetime.now(tz=settings.TIME_ZONE)
    return now.strftime(format_)


async def get_user(bot_user: types.User, *args) -> User:
    defaults = {
        "tg_username": bot_user.username,
        "tg_name": bot_user.full_name,
    }
    key = f"bot_user:{bot_user.id}"
    if key in user_cache:
        return user_cache[key]
    user, _ = await User.get_or_create(tg_id=bot_user.id, defaults=defaults)
    await user.fetch_related(*args)
    user_cache[key] = user
    return user


async def get_counter(counter_id: int, user: User):
    cache_key = f"post:{counter_id}"
    if cache_key in post_counter_cache:
        counter = post_counter_cache[cache_key]
    else:
        counter = await PostLikes.get(id=counter_id).prefetch_related("post")
        post_counter_cache[cache_key] = counter
    existence = bool(await counter.liked_users.filter(id=user.pk))
    if existence:
        await counter.liked_users.remove(user)
    else:
        await counter.liked_users.add(user)
    return counter, existence


async def update_points(post: Post, delta: int):
    await post.fetch_related("author", "school", "district", "counter")
    post.counter.likes += delta
    post.author.points += delta
    post.school.points += delta
    post.district.points += delta
    await post.counter.save()
    await post.author.save()
    await post.school.save()
    await post.district.save()
    return post.counter.likes


async def update_likes(existence: bool, counter: PostLikes):
    if existence:
        delta = -1
    else:
        delta = 1
    post: Post = counter.post
    return await update_points(post=post, delta=delta)


async def stat_info() -> dict:
    if "districts_ranking" in ranking_cache:
        return ranking_cache["districts_ranking"]
    districts = (
        await District.all().order_by("-points").prefetch_related("schools", "users")
    )
    res = []
    for district in districts:
        district: District
        res.append(
            {
                "id": district.pk,
                "name": district.name,
                "points": district.points,
                "schools": len(district.schools),
                "users": len(district.users),
            }
        )
    result = {"districts": res, "last_update": get_current_time()}
    ranking_cache["districts_ranking"] = result
    return result


async def schools_stat_info(district_id: int) -> dict:
    cache_key = f"district_{district_id}_ranking"
    if cache_key in ranking_cache:
        return ranking_cache[cache_key]
    district = await District.get(pk=district_id).prefetch_related("schools")
    res = []
    schools = await district.schools.all().order_by("-points").prefetch_related("users")
    for school in schools:
        res.append(
            {
                "id": school.pk,
                "name": school.name,
                "users": len(await school.users),
                "points": school.points,
            }
        )
    result = {"district": district, "schools": res, "last_update": get_current_time()}
    ranking_cache[cache_key] = result
    return result


async def users_stat_info(district_id: int, school_id: int) -> dict:
    district = await District.get(pk=district_id)
    school = await School.get(pk=school_id).prefetch_related("users")
    users = await school.users.filter(points__gt=0).order_by('-points')
    return {
        "district": district,
        "users": users,
        "school": school,
        "last_update": get_current_time(),
    }


async def show_user_stat(user: User):
    photos = len(await user.posts.filter(media_type="photo"))
    videos = len(await user.posts.filter(media_type="video"))
    await user.fetch_related("school", "district")
    school_in_region = len(await School.filter(points__gt=user.school.points)) + 1
    school_in_district = (
        len(await School.filter(points__gt=user.school.points, district=user.district))
        + 1
    )
    district_in_region = len(await District.filter(points__gt=user.district.points)) + 1

    return "\n".join(
        [
            f"<b>{_('statistics', user.lang_code)}:</b>\n",
            _("total_uploads", user.lang_code).format(
                total=photos + videos, photo=photos, video=videos
            ),
            _("total_points", user.lang_code).format(total=user.points),
            _("school_rating", user.lang_code).format(school=user.school.name),
            _("school_in_district", user.lang_code).format(rank=school_in_district),
            _("school_in_region", user.lang_code).format(rank=school_in_region),
            _("district_rating", user.lang_code).format(
                district=user.district.name, rank=district_in_region
            ),
        ]
    )


async def check_active_posts(user: User) -> bool:
    now = datetime.now(tz=settings.TIME_ZONE)
    await user.fetch_related("posts")
    for post in user.posts:
        if post.created_at.date() == now.date():
            return True
    return False


async def create_post(user: User, data: dict) -> Union[Post, None]:
    if await check_active_posts(user=user):
        return None
    else:
        post = await Post.create(**data)
        return post