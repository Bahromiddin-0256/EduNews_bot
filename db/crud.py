from datetime import datetime

import pytz
from aiogram import types

from core.config import settings
from core.sessions import caches
from db.models import User, PostLikes, Post, District, School
from localization.strings import _


def get_current_time(format_: str = "%d/%m/%Y, %H:%M"):
    now = datetime.now(tz=settings.TIME_ZONE)
    return now.strftime(format_)


async def get_user(bot_user: types.User, *args) -> User:
    defaults = {
        'tg_username': bot_user.username,
        'tg_name': bot_user.full_name,
    }
    key = f"bot_user:{bot_user.id}"
    if key in caches:
        return caches[key]
    user, _ = await User.update_or_create(tg_id=bot_user.id, defaults=defaults)
    await user.fetch_related(*args)
    caches[key] = user
    return user


async def update_points(post: Post, delta: int):
    await post.fetch_related('author', 'school', 'district', 'counter')
    post.counter.likes += delta
    post.author.points += delta
    post.school.points += delta
    post.district.points += delta
    await post.counter.save()
    await post.author.save()
    await post.school.save()
    await post.district.save()


async def update_likes(existence: bool, counter: PostLikes, user: User):
    if existence:
        delta = -1
        await counter.liked_users.remove(user)
    else:
        delta = 1
        await counter.liked_users.add(user)
    post: Post = counter.post
    await update_points(post=post, delta=delta)


async def stat_info() -> dict:
    districts = await District.all().order_by('-points').prefetch_related('schools', 'users')
    res = []
    for district in districts:
        district: District
        res.append({
            'id': district.pk,
            'name': district.name,
            'points': district.points,
            'schools': len(district.schools),
            'users': len(district.users),
        })
    return {'districts': res, 'last_update': get_current_time()}


async def schools_stat_info(district_id: int) -> dict:
    district = await District.get(pk=district_id).prefetch_related('schools')
    res = []
    schools = await district.schools.all().order_by('-points').prefetch_related('users')
    for school in schools:
        res.append({
            'id': school.pk,
            'name': school.name,
            'users': len(await school.users),
            'points': school.points,
        })
    return {'district': district, 'schools': res, 'last_update': get_current_time()}


async def users_stat_info(district_id: int, school_id: int) -> dict:
    district = await District.get(pk=district_id)
    school = await School.get(pk=school_id).prefetch_related('users')
    users = await school.users.filter(points__gt=0)
    return {'district': district, 'users': users, 'school': school, 'last_update': get_current_time()}


async def show_user_stat(user: User):
    photos = len(await user.posts.filter(media_type='photo'))
    videos = len(await user.posts.filter(media_type='video'))
    await user.fetch_related('school', 'district')
    school_in_region = len(await School.filter(points__gt=user.school.points)) + 1
    school_in_district = len(await School.filter(points__gt=user.school.points, district=user.district)) + 1
    district_in_region = len(await District.filter(points__gt=user.district.points)) + 1

    return "\n".join(
        [
            f"<b>{_('statistics', user.lang_code)}:</b>\n",
            _('total_uploads', user.lang_code).format(total=photos + videos, photo=photos, video=videos),
            _('total_points', user.lang_code).format(total=user.points),
            _('school_rating', user.lang_code).format(school=user.school.name),
            _('school_in_district', user.lang_code).format(rank=school_in_district),
            _('school_in_region', user.lang_code).format(rank=school_in_region),
            _('district_rating', user.lang_code).format(district=user.district.name, rank=district_in_region),
        ]
    )
