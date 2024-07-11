import asyncio
from tortoise import Tortoise
from core.config import settings, TORTOISE_ORM

# If using IPython, you can start it here, or just use the standard shell

def main():
    try:
        from IPython import start_ipython
        start_ipython(argv=[])
    except ImportError:
        import code
        code.interact(local=locals())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Tortoise.init(config=TORTOISE_ORM))
    loop.run_until_complete(Tortoise.generate_schemas())
    asyncio.run(main())
    