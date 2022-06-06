import asyncio
import logging
from typing import Any, Callable, Dict, Generator, List, Optional, Union

import aiohttp
from aiohttp.typedefs import StrOrURL
from pyee.asyncio import AsyncIOEventEmitter

from .client_ws import ClientWebSocketResponse
from .helpers import BaseAuth
from .ws_handlers import (
    MessageHandler,
    MessageQueue,
    MessageSender,
    WebSocketMessageQueue,
)

logger = logging.getLogger(__name__)


class WebSocketApp(AsyncIOEventEmitter):
    _currentws: Optional[ClientWebSocketResponse] = None

    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: StrOrURL,
        *,
        send_str: Optional[Union[str, List[str]]] = None,
        send_bytes: Optional[Union[bytes, List[bytes]]] = None,
        send_json: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        receive_str: Optional[
            Union[
                Callable[[str, ClientWebSocketResponse], None],
                List[Callable[[str, ClientWebSocketResponse], None]],
            ]
        ] = None,
        receive_bytes: Optional[
            Union[
                Callable[[bytes, ClientWebSocketResponse], None],
                List[Callable[[bytes, ClientWebSocketResponse], None]],
            ]
        ] = None,
        receive_json: Optional[
            Union[
                Callable[[Any, ClientWebSocketResponse], None],
                List[Callable[[Any, ClientWebSocketResponse], None]],
            ]
        ] = None,
        auth: Optional[BaseAuth] = BaseAuth,
        reconnect: bool = True,
        cooldown_sec: float = 60.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(session._loop)

        self.url = url

        self._awaiter = asyncio.Event()
        self.add_listener("open", self._set_awaiter)
        self.add_listener("close", self._clear_awaiter)

        if send_str is not None:
            for data in [send_str] if isinstance(send_str, str) else send_str:
                self.add_listener("open", MessageSender("send_str", data))
        if send_bytes is not None:
            for data in [send_bytes] if isinstance(send_bytes, bytes) else send_bytes:
                self.add_listener("open", MessageSender("send_bytes", data))
        if send_json is not None:
            for data in [send_json] if isinstance(send_json, dict) else send_json:
                self.add_listener("open", MessageSender("send_json", data))

        self.message_handler = MessageHandler()
        if receive_str is not None:
            for hdlr in [receive_str] if callable(receive_str) else receive_str:
                self.message_handler.add_listener("str", hdlr)
        if receive_bytes is not None:
            for hdlr in [receive_bytes] if callable(receive_bytes) else receive_bytes:
                self.message_handler.add_listener("bytes", hdlr)
        if receive_json is not None:
            for hdlr in [receive_json] if callable(receive_json) else receive_json:
                self.message_handler.add_listener("json", hdlr)
        self.add_listener("message", self.message_handler)

        self._task = self._loop.create_task(
            self._ws_connect(
                session,
                auth=auth,
                reconnect=reconnect,
                cooldown_sec=cooldown_sec,
                **kwargs,
            )
        )

    @property
    def closed(self) -> bool:
        if self._currentws is not None:
            return self._currentws.closed
        else:
            return True

    async def send_str(self, data: Union[str, List[str]]) -> None:
        if isinstance(data, str):
            data = [data]

        for msg in data:
            self.add_listener("open", MessageSender("send_str", msg))

        if self._currentws is not None:
            await asyncio.wait(
                [self._loop.create_task(self._currentws.send_str(msg)) for msg in data]
            )

    async def send_bytes(self, data: Union[bytes, List[bytes]]) -> None:
        if isinstance(data, bytes):
            data = [data]

        for msg in data:
            self.add_listener("open", MessageSender("send_bytes", msg))

        if self._currentws is not None:
            await asyncio.wait(
                [
                    self._loop.create_task(self._currentws.send_bytes(msg))
                    for msg in data
                ]
            )

    async def send_json(
        self, data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> None:
        if isinstance(data, dict):
            data = [data]

        for msg in data:
            self.add_listener("open", MessageSender("send_json", msg))

        if self._currentws is not None:
            await asyncio.wait(
                [self._loop.create_task(self._currentws.send_json(msg)) for msg in data]
            )

    def receive_str(self) -> WebSocketMessageQueue:
        return WebSocketMessageQueue(self.message_handler, "str")

    def receive_bytes(self) -> WebSocketMessageQueue:
        return WebSocketMessageQueue(self.message_handler, "bytes")

    def receive_json(self) -> WebSocketMessageQueue:
        return WebSocketMessageQueue(self.message_handler, "json")

    async def close(self) -> None:
        if self._task.cancel():
            await self.wait()

    async def wait(self) -> None:
        try:
            await self._task
        except asyncio.CancelledError:
            return

    async def _ws_connect(
        self,
        session: aiohttp.ClientSession,
        *,
        auth: Optional[BaseAuth],
        reconnect: bool,
        cooldown_sec: float,
        **kwargs: Any,
    ):
        while not session.closed:
            cooldown = self._loop.create_task(asyncio.sleep(cooldown_sec))
            try:
                async with session.ws_connect(
                    self.url,
                    auth=auth,
                    **kwargs,
                ) as self._currentws:
                    self.emit("open", self._currentws)
                    async for msg in self._currentws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            self.emit("message", msg, self._currentws)
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            self.emit("message", msg, self._currentws)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.emit("error", e)
            finally:
                if self._currentws is not None:
                    self.emit("close", self._currentws)
                    self._currentws = None
            if not reconnect:
                break
            await cooldown

    def _set_awaiter(self, ws: ClientWebSocketResponse) -> None:
        self._awaiter.set()

    def _clear_awaiter(self, ws: ClientWebSocketResponse) -> None:
        self._awaiter.clear()

    async def _wait_awaiter(self) -> "WebSocketApp":
        if self._task.cancelled():
            raise asyncio.CancelledError()

        await self._awaiter.wait()
        return self

    def __await__(self) -> Generator[Any, None, "WebSocketApp"]:
        return self._wait_awaiter().__await__()
