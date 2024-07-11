import asyncio
from tortoise import Tortoise
from core.config import settings, TORTOISE_ORM

async def init():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    from db.models import Admin

# Run the init coroutine
loop = asyncio.get_event_loop()
loop.run_until_complete(init())

# If using IPython, you can start it here, or just use the standard shell
try:
    from IPython import start_ipython
    start_ipython(argv=[])
except ImportError:
    import code
    code.interact(local=locals())