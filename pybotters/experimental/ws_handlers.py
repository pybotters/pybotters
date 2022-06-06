import asyncio
import json
import logging
from typing import Any, Generator, Union

import aiohttp
from pyee.asyncio import AsyncIOEventEmitter

from .client_ws import ClientWebSocketResponse
from .helpers import pretty_description


logger = logging.getLogger(__name__)


def pretty_exception(e: Exception) -> None:
    logger.error(pretty_description(e))


class MessageSender:
    def __init__(self, attr: str, data: Any) -> None:
        self._attr = attr
        self._data = data

    async def __call__(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        await getattr(ws, self._attr)(self._data)


class MessageHandler(AsyncIOEventEmitter):
    def __call__(self, msg: aiohttp.WSMessage, ws: ClientWebSocketResponse) -> None:
        if msg.type == aiohttp.WSMsgType.TEXT:
            self.emit("str", msg.data, ws)
        elif msg.type == aiohttp.WSMsgType.BINARY:
            self.emit("bytes", msg.data, ws)

        if self.listeners("json"):
            try:
                data = msg.json()
            except json.JSONDecodeError as e:
                self.emit("JSONDecodeError", e)
            else:
                self.emit("json", data, ws)


class MessageQueue(asyncio.Queue):
    def __call__(self, data: Any, ws: ClientWebSocketResponse) -> None:
        self.put_nowait(data)


class WebSocketMessageQueue:
    def __init__(self, ee: AsyncIOEventEmitter, event: str) -> None:
        self._ee = ee
        self._event = event

        self._queue = asyncio.Queue()

    async def get(self) -> Union[str, bytes, Any]:
        return self._queue.get()

    def __call__(
        self, data: Union[str, bytes, Any], ws: ClientWebSocketResponse
    ) -> None:
        self._queue.put_nowait(data)

    def __enter__(self) -> "MessageQueue":
        self._ee.add_listener(self._event, self)
        return self

    def __exit__(self, *args: Any) -> None:
        self._ee.remove_listener(self._event, self)
        return

    def __aiter__(self) -> "MessageQueue":
        return self

    async def __anext__(self) -> Union[str, bytes, Any]:
        return await self._queue.get()

    def __await__(self) -> Generator[Any, None, Union[str, bytes, Any]]:
        self._ee.once(self._event, self)
        return self._queue.get().__await__()


def print_hander(value: object, ws: ClientWebSocketResponse) -> None:
    print(value)
