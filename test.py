from tortoise import run_async, Tortoise

from core.config import TORTOISE_ORM
from db.models import District


async def main():
    await Tortoise.init(config=TORTOISE_ORM)
    d_all = await District.all().prefetch_related('schools')
    for d in d_all:
        async for school in d.schools.all():
            t = await d.schools.filter(name=school.name)
            print(len(t))


run_async(main())
