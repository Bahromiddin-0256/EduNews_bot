from typing import Optional

from aiohttp import ClientSession as AiohttpClientSession


class ClientSession:
    def __init__(self):
        self._session: Optional[AiohttpClientSession] = None

    @property
    def session(self):
        if self._session is None or self._session.closed:
            self._session = AiohttpClientSession()
        return self._session

    async def close(self):
        if self._session is not None:
            if not self._session.closed:
                await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return await self.session.close()
