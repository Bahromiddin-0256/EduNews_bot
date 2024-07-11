import asyncio
from tortoise import Tortoise
from core.config import settings, TORTOISE_ORM

async def init():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    # Your other initialization code here

# Adjusting the event loop for environments like IPython
try:
    # Attempt to get the current running loop; if not found, create a new one.
    loop = asyncio.get_running_loop()
except RuntimeError:
    # If no running loop is found, create a new event loop and set it as the current one.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Run the init coroutine using the adjusted event loop
loop.run_until_complete(init())

# Continue with IPython or standard shell
try:
    from IPython import start_ipython
    start_ipython(argv=[])
except ImportError:
    import code
    code.interact(local=locals())