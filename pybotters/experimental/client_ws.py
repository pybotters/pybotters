import asyncio
from typing import Any, Coroutine, Optional, TYPE_CHECKING

import aiohttp
from aiohttp.typedefs import JSONEncoder

from .exchange_hosts import APIS_TABLE, WSPING_HOSTS, WSRATELIMIT_HOSTS

if TYPE_CHECKING:
    from .client_reqrep import ClientResponse


class ClientWebSocketResponse(aiohttp.ClientWebSocketResponse):
    _response: "ClientResponse"
    _lock: Optional[asyncio.Lock] = None
    _queue: Optional[asyncio.Queue] = None
    _ratelimit: Optional[Coroutine[Any, Any, None]] = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._create_authtask()
        self._create_pingtask()
        self._set_ratelimit()

    def _create_authtask(self) -> None:
        auth = self._response.request_info.auth
        if auth is not None:
            self._loop.create_task(auth.wssign(self))

    def _create_pingtask(self) -> None:
        host = self._response.url.host
        if host in WSPING_HOSTS:
            self._loop.create_task(APIS_TABLE[WSPING_HOSTS[host]].wsping(self))

    def _set_ratelimit(self) -> None:
        host = self._response.url.host
        if host in WSRATELIMIT_HOSTS:
            self._acquire_lock(no_queue=True)
            self._ratelimit = APIS_TABLE[WSRATELIMIT_HOSTS[host]].wsratelimit

    def _acquire_lock(self, no_queue: bool = False) -> None:
        if self._lock is None:
            self._lock = asyncio.Lock()
        if not no_queue and self._queue is None:
            self._queue = asyncio.Queue()

    def _release_lock(self) -> None:
        self._queue = None
        self._lock = None

    async def send_str(self, data: str, compress: Optional[int] = None) -> None:
        # print(">", data)
        if self._lock is None:
            await super().send_str(data, compress)
        else:
            async with self._lock:
                await super().send_str(data, compress)
                if self._ratelimit is not None:
                    await self._ratelimit(self)

    async def send_bytes(self, data: bytes, compress: Optional[int] = None) -> None:
        if self._lock is None:
            await super().send_bytes(data, compress)
        else:
            async with self._lock:
                await super().send_bytes(data, compress)
                if self._ratelimit is not None:
                    await self._ratelimit(self)

    async def send_json(
        self,
        data: Any,
        compress: Optional[int] = None,
        *,
        dumps: Optional[JSONEncoder] = None,
    ) -> None:
        if dumps is None:
            dumps = self._response.request_info.json_serialize

        await super().send_json(data, compress, dumps=dumps)

    async def receive(self, timeout: Optional[float] = None) -> aiohttp.WSMessage:
        msg = await super().receive(timeout)
        # print("<", msg)

        if self._queue is not None:
            self._queue.put_nowait(msg)

        return msg
