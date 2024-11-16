from __future__ import annotations

import asyncio
import base64
import datetime
import hashlib
import hmac
import inspect
import json
import logging
import random
import struct
import time
import uuid
import zlib
from dataclasses import dataclass
from secrets import token_hex
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import urlencode

import aiohttp

from .auth import Auth as _Auth

if TYPE_CHECKING:
    from collections.abc import (
        AsyncIterator,
        Awaitable,
        Generator,
    )

    from .typedefs import (
        WsBytesHandler,
        WsHeartBeatHandler,
        WsJsonHandler,
        WsRateLimitHandler,
        WsStrHandler,
    )

logger = logging.getLogger(__name__)


def pretty_modulename(e: Exception) -> str:
    modulename = e.__class__.__name__
    module = inspect.getmodule(e)
    if module:
        modulename = f"{module.__name__}.{modulename}"
    return modulename


class WebSocketApp:
    _BACKOFF_MIN = 1.92
    _BACKOFF_MAX = 60.0
    _BACKOFF_FACTOR = 1.618
    _BACKOFF_INITIAL = 5.0
    _DEFAULT_BACKOFF = (_BACKOFF_MIN, _BACKOFF_MAX, _BACKOFF_FACTOR, _BACKOFF_INITIAL)

    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: str,
        *,
        send_str: str | list[str] | None = None,
        send_bytes: bytes | list[bytes] | None = None,
        send_json: dict | list[dict] | None = None,
        hdlr_str: WsStrHandler | list[WsStrHandler] | None = None,
        hdlr_bytes: WsBytesHandler | list[WsBytesHandler] | None = None,
        hdlr_json: WsJsonHandler | list[WsJsonHandler] | None = None,
        backoff: tuple[float, float, float, float] = _DEFAULT_BACKOFF,
        **kwargs: Any,
    ) -> None:
        """WebSocket Application.

        自動再接続、自動認証、自動 PING/PONG を備えた WebSocket アプリケーションです。

        Usage example: :ref:`websocketqueue`
        """
        self._session = session
        self._url = url

        self._loop = session._loop
        self._current_ws: aiohttp.ClientWebSocketResponse | None = None
        self._event = asyncio.Event()

        self._autoping = kwargs.pop("autoping", True)
        self._pings: dict[bytes, asyncio.Event] = {}

        if send_str is None:
            send_str = []
        elif isinstance(send_str, str):
            send_str = [send_str]

        if send_bytes is None:
            send_bytes = []
        elif isinstance(send_bytes, bytes):
            send_bytes = [send_bytes]

        if send_json is None:
            send_json = []
        elif isinstance(send_json, dict):
            send_json = [send_json]

        if hdlr_str is None:
            hdlr_str = []
        elif callable(hdlr_str):
            hdlr_str = [hdlr_str]

        if hdlr_bytes is None:
            hdlr_bytes = []
        elif callable(hdlr_bytes):
            hdlr_bytes = [hdlr_bytes]

        if hdlr_json is None:
            hdlr_json = []
        elif callable(hdlr_json):
            hdlr_json = [hdlr_json]

        self._task = self._loop.create_task(
            self._run_forever(
                send_str=send_str,
                send_bytes=send_bytes,
                send_json=send_json,
                hdlr_str=hdlr_str,
                hdlr_bytes=hdlr_bytes,
                hdlr_json=hdlr_json,
                backoff=backoff,
                **kwargs,
            )
        )

    @property
    def url(self) -> str:
        """WebSocket URL.

        WebSocket の接続 URL です。
        接続中に値を変更した場合は、再接続時に設定 URL に接続されます。
        """
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        self._url = url

    @property
    def current_ws(self) -> aiohttp.ClientWebSocketResponse | None:
        """Current WebSocket connection.

        現在の WebSocket コネクションです。
        現在のコネクションが存在する場合は ClientWebSocketResponse を返します。
        コネクションが存在しない場合は None を返します。
        """
        return self._current_ws

    async def _run_forever(
        self,
        *,
        send_str: list[str],
        send_bytes: list[bytes],
        send_json: list[dict],
        hdlr_str: list[WsStrHandler],
        hdlr_bytes: list[WsBytesHandler],
        hdlr_json: list[WsJsonHandler],
        backoff: tuple[float, float, float, float],
        **kwargs: Any,
    ) -> None:
        BACKOFF_MIN, BACKOFF_MAX, BACKOFF_FACTOR, BACKOFF_INITIAL = backoff

        backoff_delay = BACKOFF_MIN
        while not self._session.closed:
            try:
                await self._ws_connect(
                    send_str=send_str,
                    send_bytes=send_bytes,
                    send_json=send_json,
                    hdlr_str=hdlr_str,
                    hdlr_bytes=hdlr_bytes,
                    hdlr_json=hdlr_json,
                    **kwargs,
                )
            # From https://github.com/python-websockets/websockets/blob/12.0/src/websockets/legacy/client.py#L600-L624
            # Licensed under the BSD-3-Clause
            except Exception as e:
                logger.warning(f"{pretty_modulename(e)}: {e}")
                if backoff_delay == BACKOFF_MIN:
                    initial_delay = random.random() * BACKOFF_INITIAL
                    await asyncio.sleep(initial_delay)
                else:
                    await asyncio.sleep(int(backoff_delay))
                backoff_delay = backoff_delay * BACKOFF_FACTOR
                backoff_delay = min(backoff_delay, BACKOFF_MAX)
            else:
                backoff_delay = BACKOFF_MIN
            # End https://github.com/python-websockets/websockets/blob/12.0/src/websockets/legacy/client.py#L600-L624
            finally:
                self._current_ws = None
                self._event.clear()

    async def _ws_connect(
        self,
        *,
        send_str: list[str],
        send_bytes: list[bytes],
        send_json: list[dict],
        hdlr_str: list[WsStrHandler],
        hdlr_bytes: list[WsBytesHandler],
        hdlr_json: list[WsJsonHandler],
        **kwargs: Any,
    ) -> None:
        async with self._session.ws_connect(self._url, autoping=False, **kwargs) as ws:
            self._current_ws = ws
            self._event.set()

            await cast(ClientWebSocketResponse, ws)._wait_authtask()

            await self._ws_send(ws, send_str, send_bytes, send_json)

            await self._ws_receive(ws, hdlr_str, hdlr_bytes, hdlr_json)

    async def _ws_send(
        self,
        ws: aiohttp.ClientWebSocketResponse,
        send_str: list[str],
        send_bytes: list[bytes],
        send_json: list[dict],
    ) -> None:
        await asyncio.gather(
            *(ws.send_str(x) for x in send_str),
            *(ws.send_bytes(x) for x in send_bytes),
            *(ws.send_json(x) for x in send_json),
        )

    async def _ws_receive(
        self,
        ws: aiohttp.ClientWebSocketResponse,
        hdlr_str: list[WsStrHandler],
        hdlr_bytes: list[WsBytesHandler],
        hdlr_json: list[WsJsonHandler],
    ) -> None:
        async for msg in ws:
            self._loop.call_soon(
                self._onmessage, msg, ws, hdlr_str, hdlr_bytes, hdlr_json
            )

    def _onmessage(
        self,
        msg: aiohttp.WSMessage,
        ws: aiohttp.ClientWebSocketResponse,
        hdlr_str: list[WsStrHandler],
        hdlr_bytes: list[WsBytesHandler],
        hdlr_json: list[WsJsonHandler],
    ) -> None:
        hdlr: WsStrHandler | WsJsonHandler | WsJsonHandler
        if msg.type == aiohttp.WSMsgType.TEXT:
            for hdlr in hdlr_str:
                self._loop.call_soon(hdlr, msg.data, ws)
        elif msg.type == aiohttp.WSMsgType.BINARY:
            for hdlr in hdlr_bytes:
                self._loop.call_soon(hdlr, msg.data, ws)

        if hdlr_json and msg.type in {aiohttp.WSMsgType.TEXT, aiohttp.WSMsgType.BINARY}:
            try:
                data = msg.json()
            except json.JSONDecodeError as e:
                if msg.data not in {"ping", "pong"}:
                    logger.warning(f"{pretty_modulename(e)}: {e} {e.doc}")
            else:
                for hdlr in hdlr_json:
                    self._loop.call_soon(hdlr, data, ws)

        if msg.type == aiohttp.WSMsgType.PING and self._autoping:
            self._loop.create_task(ws.pong(msg.data))
        elif msg.type == aiohttp.WSMsgType.PONG:
            data = bytes(msg.data)
            if data in self._pings:
                self._pings[data].set()

    async def heartbeat(self, timeout: float = 10.0) -> None:
        """Ensure WebSocket connection is open with Ping-Pong.

        WebSocket の Ping-Pong で接続の疎通を確認します。
        ユーザーコード内で WebSocket のデータを利用する前にこのコルーチンを待機することで、
        WebSocket の接続性を保証するのに役に立ちます。

        一定時間 Pong が返ってこない場合は再接続を試みます。
        このメソッドは疎通が確認されるまで待機します。

        Args:
            timeout: WebSocket Ping-Pong ハートビート (デフォルト 10.0 秒)
        """
        while True:
            await self._wait_handshake()

            ping = struct.pack("!I", random.getrandbits(32))
            self._pings[ping] = asyncio.Event()
            if self._current_ws:
                await self._current_ws.ping(ping)

            try:
                await asyncio.wait_for(self._pings[ping].wait(), timeout=timeout)
            except asyncio.TimeoutError:
                if self._current_ws:
                    self._current_ws._pong_not_received()
                    self._current_ws = None
                    self._event.clear()
            else:
                return
            finally:
                del self._pings[ping]

    async def wait(self) -> None:
        """Wait WebSocketApp.

        WebSocketApp の待機を待ちます。
        ただし WebSocketApp は自動再接続の機構を備えるので、実質的に無限待機です。
        プログラムの終了を防ぐのに役に立ちます。
        """
        await self._task

    async def _wait_handshake(self) -> "WebSocketApp":
        await self._event.wait()
        return self

    def __await__(self) -> Generator[Any, None, "WebSocketApp"]:
        return self._wait_handshake().__await__()


class WebSocketQueue(asyncio.Queue):
    """WebSocket queue (from asyncio.Queue)."""

    def onmessage(self, msg: Any, ws: aiohttp.ClientWebSocketResponse):
        """WebSocket message hander callback."""
        self.put_nowait(msg)

    async def __aiter__(self) -> AsyncIterator[Any]:
        """Receive WebSocket message."""
        while True:
            yield await self.get()


class Heartbeat:
    @staticmethod
    async def bybit(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('{"op":"ping"}')
            await asyncio.sleep(20.0)

    @staticmethod
    async def bitbank(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str("2")
            await asyncio.sleep(15.0)

    @staticmethod
    async def binance(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.pong()
            await asyncio.sleep(60.0)

    @staticmethod
    async def phemex(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('{"method":"server.ping","params":[],"id":123}')
            await asyncio.sleep(10.0)

    @staticmethod
    async def okx(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str("ping")
            await asyncio.sleep(15.0)

    @staticmethod
    async def bitget(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str("ping")
            # Refer to official SDK
            # https://github.com/BitgetLimited/v3-bitget-api-sdk/blob/09179123a62cf2a63ea1cfbb289b85e3a40018f8/bitget-python-sdk-api/bitget/ws/bitget_ws_client.py#L58
            await asyncio.sleep(25.0)

    @staticmethod
    async def mexc(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('{"method":"ping"}')
            await asyncio.sleep(10.0)

    @staticmethod
    async def kucoin(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str(f'{{"id": "{uuid.uuid4()}", "type": "ping"}}')
            await asyncio.sleep(15)

    @staticmethod
    async def okj(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str("ping")
            await asyncio.sleep(15.0)

    @staticmethod
    async def bittrade(ws: aiohttp.ClientWebSocketResponse):
        # Retail
        if ws._response.url.path == "/retail/ws":
            while not ws.closed:
                ts = int(time.time())
                await ws.send_json({"action": 5, "ts": ts})
                await asyncio.sleep(10.0)
        # Public
        elif ws._response.url.path == "/ws":
            while not ws.closed:
                ts = int(time.time() * 1000)
                await ws.send_json({"pong": ts})
                await asyncio.sleep(5.0)
        # Private
        elif ws._response.url.path == "/ws/v2":
            while not ws.closed:
                ts = int(time.time() * 1000)
                await ws.send_json({"action": "pong", "data": {"ts": ts}})
                await asyncio.sleep(20.0)


class Auth:
    @staticmethod
    async def bybit(ws: aiohttp.ClientWebSocketResponse):
        if "public" in ws._response.url.parts:
            return

        key: str = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][1]

        expires = int((time.time() + 5.0) * 1000)
        path = f"GET/realtime{expires}"
        signature = hmac.new(
            secret, path.encode(), digestmod=hashlib.sha256
        ).hexdigest()

        await ws.send_json({"op": "auth", "args": [key, expires, signature]})
        async for msg in ws:
            data = msg.json()
            if data.get("op") == "auth":
                if not data.get("success"):
                    logger.warning(data)
                break

    @staticmethod
    async def bitflyer(ws: aiohttp.ClientWebSocketResponse):
        key: str = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][1]

        timestamp = int(time.time() * 1000)
        nonce = token_hex(16)
        sign = hmac.new(
            secret, f"{timestamp}{nonce}".encode(), digestmod=hashlib.sha256
        ).hexdigest()
        await ws.send_json(
            {
                "method": "auth",
                "params": {
                    "api_key": key,
                    "timestamp": timestamp,
                    "nonce": nonce,
                    "signature": sign,
                },
                "id": "auth",
            }
        )
        async for msg in ws:
            data = msg.json()
            if data.get("id") == "auth":
                if "error" in data:
                    logger.warning(data)
                break

    @staticmethod
    async def phemex(ws: aiohttp.ClientWebSocketResponse):
        key: str = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][1]

        expiry = int(time.time() + 60.0)
        signature = hmac.new(
            secret, f"{key}{expiry}".encode(), digestmod=hashlib.sha256
        ).hexdigest()
        msg_to_send = {
            "method": "user.auth",
            "params": ["API", key, signature, expiry],
            "id": 123,
        }
        await ws.send_json(msg_to_send)
        async for msg in ws:
            data = msg.json()
            if data.get("id") == 123:
                if data.get("error"):
                    logger.warning(data)
                break

    @staticmethod
    async def okx(ws: aiohttp.ClientWebSocketResponse):
        key: str = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][1]
        passphrase: bytes = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][2]

        timestamp = str(int(time.time()))
        text = f"{timestamp}GET/users/self/verify"
        sign = base64.b64encode(
            hmac.new(secret, text.encode(), digestmod=hashlib.sha256).digest()
        ).decode()
        msg_to_send = {
            "op": "login",
            "args": [
                {
                    "apiKey": key,
                    "passphrase": passphrase,
                    "timestamp": timestamp,
                    "sign": sign,
                }
            ],
        }
        await ws.send_json(msg_to_send)
        async for msg in ws:
            try:
                data = msg.json()
            except json.JSONDecodeError:
                pass
            else:
                event = data.get("event")
                if event == "error":
                    logger.warning(data)
                    break
                elif event == "login":
                    break

    @staticmethod
    async def bitget(ws: aiohttp.ClientWebSocketResponse):
        key: str = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][1]
        passphrase: bytes = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][2]

        timestamp = int(round(time.time()))
        sign = base64.b64encode(
            hmac.new(
                secret, f"{timestamp}GET/user/verify".encode(), digestmod=hashlib.sha256
            ).digest()
        ).decode()
        msg_to_send = {
            "op": "login",
            "args": [
                {
                    "api_key": key,
                    "passphrase": passphrase,
                    "timestamp": str(timestamp),
                    "sign": sign,
                }
            ],
        }
        await ws.send_json(msg_to_send)
        async for msg in ws:
            try:
                data = msg.json()
            except json.JSONDecodeError:
                pass
            else:
                event = data.get("event")
                if event == "error":
                    logger.warning(data)
                    break
                elif event == "login":
                    break

    @staticmethod
    async def mexc(ws: aiohttp.ClientWebSocketResponse):
        key: str = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][1]

        timestamp = str(int(time.time()))
        sign = hmac.new(
            secret, f"{key}{timestamp}".encode(), digestmod=hashlib.sha256
        ).hexdigest()

        msg = {
            "method": "login",
            "param": {
                "apiKey": key,
                "reqTime": timestamp,
                "signature": sign,
            },
        }
        await ws.send_json(msg)

    @staticmethod
    async def okj(ws: aiohttp.ClientWebSocketResponse):
        key: str = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][1]
        passphrase: bytes = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][2]

        timestamp = str(time.time())
        text = f"{timestamp}GET/users/self/verify"
        sign = base64.b64encode(
            hmac.new(secret, text.encode(), digestmod=hashlib.sha256).digest()
        ).decode()
        msg_to_send = {
            "op": "login",
            "args": [key, passphrase, timestamp, sign],
        }
        await ws.send_json(msg_to_send)
        async for msg in ws:
            if msg.type != aiohttp.WSMsgType.BINARY:
                continue
            try:
                data = json.loads(zlib.decompress(msg.data, -zlib.MAX_WBITS))
            except json.JSONDecodeError:
                pass
            else:
                event = data.get("event")
                if event == "error":
                    logger.warning(data)
                    break
                elif event == "login":
                    break

    @staticmethod
    async def bittrade(ws: aiohttp.ClientWebSocketResponse):
        method = "GET"
        host = ws._response.url.host
        path = ws._response.url.path

        key: str = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__["_apis"][
            AuthHosts.items[ws._response.url.host].name
        ][1]

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        params = {
            "accessKey": key,
            "signatureMethod": "HmacSHA256",
            "signatureVersion": "2.1",
            "timestamp": timestamp,
        }
        params_str = urlencode(params)
        sign_str = f"{method}\n{host}\n{path}\n{params_str}".encode()
        signature = base64.b64encode(
            hmac.new(secret, sign_str, hashlib.sha256).digest()
        ).decode()

        msg_to_send = {
            "action": "req",
            "ch": "auth",
            "params": {
                "authType": "api",
                "accessKey": key,
                "signatureMethod": params["signatureMethod"],
                "signatureVersion": params["signatureVersion"],
                "timestamp": timestamp,
                "signature": signature,
            },
        }

        await ws.send_json(msg_to_send)

        async for msg in ws:
            if msg.type != aiohttp.WSMsgType.TEXT:
                continue

            data: dict[str, Any] = msg.json()
            if data.get("ch") == "auth":
                if data.get("code") == 200:
                    break
                else:
                    logger.warning(data)


@dataclass
class Item:
    name: str
    func: Any


class HeartbeatHosts:
    # NOTE: yarl.URL.host is also allowed to be None. So, for brevity, relax the type check on the `items` key.
    items: dict[str | None, WsHeartBeatHandler] = {
        "stream.bitbank.cc": Heartbeat.bitbank,
        "stream.bybit.com": Heartbeat.bybit,
        "stream.bytick.com": Heartbeat.bybit,
        "stream-demo.bybit.com": Heartbeat.bybit,
        "stream-testnet.bybit.com": Heartbeat.bybit,
        "stream.binance.com": Heartbeat.binance,
        "fstream.binance.com": Heartbeat.binance,
        "dstream.binance.com": Heartbeat.binance,
        "vstream.binance.com": Heartbeat.binance,
        "stream.binancefuture.com": Heartbeat.binance,
        "dstream.binancefuture.com": Heartbeat.binance,
        "testnet.binanceops.com": Heartbeat.binance,
        "testnetws.binanceops.com": Heartbeat.binance,
        "phemex.com": Heartbeat.phemex,
        "api.phemex.com": Heartbeat.phemex,
        "vapi.phemex.com": Heartbeat.phemex,
        "testnet.phemex.com": Heartbeat.phemex,
        "testnet-api.phemex.com": Heartbeat.phemex,
        "ws.okx.com": Heartbeat.okx,
        "wsaws.okx.com": Heartbeat.okx,
        "wspap.okx.com": Heartbeat.okx,
        "ws.bitget.com": Heartbeat.bitget,
        "contract.mexc.com": Heartbeat.mexc,
        "ws-api-spot.kucoin.com": Heartbeat.kucoin,
        "ws-api-futures.kucoin.com": Heartbeat.kucoin,
        "connect.okcoin.jp": Heartbeat.okj,
        "api-cloud.bittrade.co.jp": Heartbeat.bittrade,
    }


class AuthHosts:
    # NOTE: yarl.URL.host is also allowed to be None. So, for brevity, relax the type check on the `items` key.
    items: dict[str | None, Item] = {
        "stream.bybit.com": Item("bybit", Auth.bybit),
        "stream.bytick.com": Item("bybit", Auth.bybit),
        "stream-demo.bybit.com": Item("bybit_demo", Auth.bybit),
        "stream-testnet.bybit.com": Item("bybit_testnet", Auth.bybit),
        "ws.lightstream.bitflyer.com": Item("bitflyer", Auth.bitflyer),
        "phemex.com": Item("phemex", Auth.phemex),
        "ws.phemex.com": Item("phemex", Auth.phemex),
        "vapi.phemex.com": Item("phemex", Auth.phemex),
        "testnet.phemex.com": Item("phemex_testnet", Auth.phemex),
        "testnet-api.phemex.com": Item("phemex_testnet", Auth.phemex),
        "ws.okx.com": Item("okx", Auth.okx),
        "wsaws.okx.com": Item("okx", Auth.okx),
        "wspap.okx.com": Item("okx_demo", Auth.okx),
        "ws.bitget.com": Item("bitget", Auth.bitget),
        "contract.mexc.com": Item("mexc", Auth.mexc),
        "connect.okcoin.jp": Item("okj", Auth.okj),
        "api-cloud.bittrade.co.jp": Item("bittrade", Auth.bittrade),
    }


class ClientWebSocketResponse(aiohttp.ClientWebSocketResponse):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self._response.url.host in HeartbeatHosts.items:
            self.__dict__["_pingtask"] = asyncio.create_task(
                HeartbeatHosts.items[self._response.url.host](self)
            )
        if self._response.__dict__["_auth"] is _Auth:
            if self._response.url.host in AuthHosts.items:
                if (
                    AuthHosts.items[self._response.url.host].name
                    in self._response._session.__dict__["_apis"]
                ):
                    self.__dict__["_authtask"] = asyncio.create_task(
                        AuthHosts.items[self._response.url.host].func(self)
                    )
        self._lock = asyncio.Lock()

    async def _wait_authtask(self):
        if "_authtask" in self.__dict__:
            await self.__dict__["_authtask"]

    async def send_str(self, *args, **kwargs) -> None:
        if self._response.url.host not in RequestLimitHosts.items:
            await super().send_str(*args, **kwargs)
        else:
            super_send_str = super().send_str(*args, **kwargs)
            await RequestLimitHosts.items[self._response.url.host](self, super_send_str)

    async def send_json(self, *args, **kwargs) -> None:
        if (
            (kwargs.pop("auth", _Auth) is _Auth)
            and (self._response.url.host in MessageSignHosts.items)
            and (
                MessageSignHosts.items[self._response.url.host].name
                in self._response._session.__dict__["_apis"]
            )
        ):
            data = kwargs.get("data", args[0] if len(args) > 0 else None)
            if data:
                MessageSignHosts.items[self._response.url.host].func(self, data)

        return await super().send_json(*args, **kwargs)


class RequestLimit:
    @staticmethod
    async def gmocoin(ws: aiohttp.ClientWebSocketResponse, send_str: Awaitable[None]):
        session = cast(aiohttp.ClientSession, ws._response._session)
        async with cast(ClientWebSocketResponse, ws)._lock:
            await send_str
            r = await session.get("https://api.coin.z.com/public/v1/status", auth=_Auth)
            data = await r.json()
            before = datetime.datetime.fromisoformat(data["responsetime"][:-1])
            while True:
                await asyncio.sleep(1.0)
                r = await session.get(
                    "https://api.coin.z.com/public/v1/status", auth=_Auth
                )
                data = await r.json()
                after = datetime.datetime.fromisoformat(data["responsetime"][:-1])
                delta = after - before
                if delta.total_seconds() >= 1.0:
                    break

    @staticmethod
    async def binance(
        ws: aiohttp.ClientWebSocketResponse, send_str: Awaitable[None]
    ) -> None:
        session = cast(aiohttp.ClientSession, ws._response._session)
        async with cast(ClientWebSocketResponse, ws)._lock:
            await send_str
            r = await session.get("https://api.binance.com/api/v3/time", auth=None)
            data = await r.json()
            before = datetime.datetime.fromtimestamp(data["serverTime"] / 1000)
            while True:
                await asyncio.sleep(0.25)  # limit of 5 incoming messages per second
                r = await session.get("https://api.binance.com/api/v3/time", auth=None)
                data = await r.json()
                after = datetime.datetime.fromtimestamp(data["serverTime"] / 1000)
                delta = after - before
                if delta.total_seconds() > 0.25:
                    break


class RequestLimitHosts:
    items: dict[str | None, WsRateLimitHandler] = {
        "api.coin.z.com": RequestLimit.gmocoin,
        "stream.binance.com": RequestLimit.binance,
    }


class MessageSign:
    @staticmethod
    def binance(ws: aiohttp.ClientWebSocketResponse, data: dict[str, Any]):
        key: str = ws._response._session.__dict__["_apis"][
            MessageSignHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__["_apis"][
            MessageSignHosts.items[ws._response.url.host].name
        ][1]

        if "params" not in data:
            data["params"] = {}

        params = data["params"]
        params["apiKey"] = key
        params["timestamp"] = int(time.time() * 1000)
        payload = "&".join(
            [f"{param}={value}" for param, value in sorted(params.items())]
        )
        signature = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature

    @staticmethod
    def bybit(ws: aiohttp.ClientWebSocketResponse, data: dict[str, Any]):
        if "trade" not in ws._response.url.parts:
            return

        if "header" not in data:
            data["header"] = {"X-BAPI-TIMESTAMP": str(int(time.time() * 1000))}


class MessageSignHosts:
    # NOTE: yarl.URL.host is also allowed to be None. So, for brevity, relax the type check on the `items` key.
    items: dict[str | None, Item] = {
        "ws-api.binance.com": Item("binance", MessageSign.binance),
        "testnet.binance.vision": Item("binancespot_testnet", MessageSign.binance),
        "stream.bybit.com": Item("bybit", MessageSign.bybit),
        "stream-demo.bybit.com": Item("bybit_demo", MessageSign.bybit),
        "stream-testnet.bybit.com": Item("bybit_testnet", MessageSign.bybit),
    }
