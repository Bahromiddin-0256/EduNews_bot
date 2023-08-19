import tortoise
from tortoise.functions import Count, Sum
from core.config import TORTOISE_ORM
from db.models import User, District, School
from db.crud import stat_info
import unittest


async def main():
    await tortoise.Tortoise.init(config=TORTOISE_ORM)
    await User.all().update(post_permission=False, points=0)
    await School.all().update(points=0)
    await District.all().update(points=0)


tortoise.run_async(main())
