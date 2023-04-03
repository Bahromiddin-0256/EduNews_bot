from datetime import datetime, timedelta
from typing import Union

from aiogram import types
import asyncio
from core.config import settings
from core.sessions import user_cache, dashboard_cache, post_counter_cache
from db.models import User, PostLikes, Post, District, School, Tournament
from tortoise.functions import Count
from localization.strings import _
from tortoise.functions import Count
from tortoise.query_utils import Prefetch

lock = asyncio.Lock()


def get_current_time(format_: str = "%d/%m/%Y, %H:%M"):
    now = datetime.now(tz=settings.TIME_ZONE)
    return now.strftime(format_)


async def get_user(bot_user: types.User, *args) -> User:
    async with lock:
        defaults = {
            "tg_username": bot_user.username,
            "tg_name": bot_user.full_name,
        }
        key = f"bot_user:{bot_user.id}"
        if key in user_cache:
            return user_cache[key]
        user, _ = await User.get_or_create(defaults=defaults, tg_id=bot_user.id)
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


async def update_points(post: Post, delta: int) -> Union[int, None]:
    await post.fetch_related("author", "school", "district", "counter")
    post.counter.points += delta
    post.author.points += delta
    post.school.points += delta
    post.district.points += delta
    await post.counter.save()
    await post.author.save()
    await post.school.save()
    await post.district.save()
    await post.counter.fetch_related("liked_users")
    total_likes = await post.counter.liked_users.all().count()
    if total_likes != post.counter.last_updated_likes:
        post.counter.last_updated_likes = total_likes
        await post.counter.save()
        return total_likes
    else:
        return None


async def stat_info() -> dict:
    if "districts_ranking" in dashboard_cache:
        return dashboard_cache["districts_ranking"]
    districts = await District.all().order_by("-points").annotate(total_posts=Count('posts')).prefetch_related('schools', 'users')
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
                "posts": district.total_posts,
            }
        )
    result = {"districts": res, "last_update": get_current_time()}
    dashboard_cache["districts_ranking"] = result
    return result


async def schools_stat_info(district_id: int) -> dict:
    cache_key = f"district_{district_id}_ranking"
    if cache_key in dashboard_cache:
        return dashboard_cache[cache_key]
    district = await District.get(pk=district_id).prefetch_related("schools")
    res = []
    schools = await district.schools.all().order_by("-points").annotate(total_users=Count('users'))
    for school in schools:
        res.append(
            {
                "id": school.pk,
                "name": school.name,
                "users": school.total_users,
                "points": school.points,
            }
        )
    result = {"district": district, "schools": res, "last_update": get_current_time()}
    dashboard_cache[cache_key] = result
    return result


async def users_stat_info(district_id: int, school_id: int) -> dict:
    district = await District.get(pk=district_id)
    school = await School.get(pk=school_id).prefetch_related("users")
    users = await school.users.filter(points__gt=0).order_by("-points")
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


def lower_bound(nums, target):
    left = 0
    right = len(nums) - 1

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return left


async def get_user_count_data():
    if 'get_user_count_data' in dashboard_cache:
        return dashboard_cache['get_user_count_data']
    result = []
    users = await User.all().order_by('created_at').values('created_at')
    created_time_array = [user['created_at'].timestamp() for user in users]

    end_date = datetime.now(tz=settings.TIME_ZONE)
    end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    start_date = end_date - timedelta(days=365)
    for date in (start_date + timedelta(days=n) for n in range(365)):
        count = lower_bound(created_time_array, date.timestamp())
        result.append([date.timestamp() * 1000, count])
    dashboard_cache['get_user_count_data'] = result
    return result


async def get_post_stat_data():
    if 'get_post_stat_data' in dashboard_cache:
        return dashboard_cache['get_post_stat_data']
    result = []
    posts = await Post.all().order_by('created_at').values('created_at')
    created_time_array = [post['created_at'].timestamp() for post in posts]

    end_date = datetime.now(tz=settings.TIME_ZONE)
    end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    start_date = end_date - timedelta(days=365)
    for date in (start_date + timedelta(days=n) for n in range(365)):
        count = lower_bound(created_time_array, date.timestamp())
        result.append([date.timestamp() * 1000, count])
    dashboard_cache['get_post_stat_data'] = result
    return result


async def get_user_data_by_regions():
    if 'get_user_data_by_regions' in dashboard_cache:
        return dashboard_cache['get_user_data_by_regions']
    data = await stat_info()
    regions_users = []
    regions_posts = []
    regions_labels = []
    for region in data['districts']:
        regions_users.append(region['users'])
        regions_posts.append(region['posts'])
        regions_labels.append(region['name'].split(' ')[0])
    dashboard_cache['get_user_data_by_regions'] = regions_users, regions_posts, regions_labels
    return regions_users, regions_posts, regions_labels


async def get_tournaments_list():
    key = 'tournaments_list_key'
    if key in dashboard_cache:
        return dashboard_cache[key]
    tournaments = await Tournament.annotate(total_participants=Count('participants')).prefetch_related(
        'participants').all()
    result = {'tournaments': tournaments, 'last_update': get_current_time()}
    dashboard_cache[key] = result
    return result


async def tournament_participants_rating(tournament: Tournament):
    key = f'tournament_participants_rating:{tournament.id}'
    if key in dashboard_cache:
        return dashboard_cache[key]
    participants = await Post.filter(tournament=tournament).prefetch_related('author', 'district', 'school', 'counter').order_by('counter__last_updated_likes')
    result = {'participants': participants, 'last_update': get_current_time()}
    dashboard_cache[key] = result
    return result