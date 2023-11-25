import tortoise
from tortoise.functions import Count, Sum
from core.config import TORTOISE_ORM
from db.models import User, District, School
from db.crud import stat_info
import unittest


async def main():
    await tortoise.Tortoise.init(config=TORTOISE_ORM)
    await User.filter(district_id=18).update(points=0)
    await School.filter(district_id=18).update(points=0)
    await District.get(id=18).update(points=0)


tortoise.run_async(main())
