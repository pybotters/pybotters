import asyncio
import hashlib
import hmac
import logging
import time
from dataclasses import dataclass
from secrets import token_hex
from typing import Any, Optional

import aiohttp
from aiohttp.http_websocket import json
from aiohttp.typedefs import StrOrURL

logger = logging.getLogger(__name__)


async def ws_run_forever(
    url: StrOrURL,
    session: aiohttp.ClientSession,
    event: asyncio.Event,
    *,
    send_str: Optional[str]=None,
    send_json: Optional[Any]=None,
    hdlr_str=None,
    hdlr_json=None,
    **kwargs: Any,
) -> None:
    iscorofunc_str = asyncio.iscoroutinefunction(hdlr_str)
    iscorofunc_json = asyncio.iscoroutinefunction(hdlr_json)
    while not session.closed:
        separator = asyncio.create_task(asyncio.sleep(60.0))
        try:
            async with session.ws_connect(url, **kwargs) as ws:
                event.set()
                if send_str is not None:
                    await ws.send_str(send_str)
                if send_json is not None:
                    await ws.send_json(send_json)
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        if hdlr_str is not None:
                            try:
                                if iscorofunc_str:
                                    await hdlr_str(msg.data, ws)
                                else:
                                    hdlr_str(msg.data, ws)
                            except Exception as e:
                                logger.error(repr(e))
                        if hdlr_json is not None:
                            try:
                                data = msg.json()
                            except json.decoder.JSONDecodeError:
                                pass
                            else:
                                try:
                                    if iscorofunc_json:
                                        await hdlr_json(data, ws)
                                    else:
                                        hdlr_json(data, ws)
                                except Exception as e:
                                    logger.error(repr(e))
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
        except aiohttp.WSServerHandshakeError as e:
            logger.warning(repr(e))
        await separator


class Heartbeat:
    @staticmethod
    async def bybit(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('{"op":"ping"}')
            await asyncio.sleep(30.0)

    @staticmethod
    async def btcmex(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('ping')
            await asyncio.sleep(30.0)


class Auth:
    @staticmethod
    async def bitflyer(ws: aiohttp.ClientWebSocketResponse):
        key: str = ws._response._session.__dict__['_apis'][AuthHosts.items[ws._response.url.host].name][0]
        secret: bytes = ws._response._session.__dict__['_apis'][AuthHosts.items[ws._response.url.host].name][1]

        timestamp = int(time.time())
        nonce = token_hex(16)
        sign = hmac.new(secret, (str(timestamp) + nonce).encode(), digestmod=hashlib.sha256).hexdigest()
        await ws.send_json({
            'method': 'auth',
            'params': {
                'api_key': key, 'timestamp': timestamp, 'nonce': nonce, 'signature': sign
            },
            'id': 'auth',
        })


@dataclass
class Item:
    name: str
    func: Any


class HeartbeatHosts:
    items = {
        'www.btcmex.com': Heartbeat.btcmex,
        'stream.bybit.com': Heartbeat.bybit,
        'stream.bytick.com': Heartbeat.bybit,
        'stream-testnet.bybit.com': Heartbeat.bybit,
        'stream-testnet.bybit.com': Heartbeat.bybit,
    }


class AuthHosts:
    items = {
        'ws.lightstream.bitflyer.com': Item('bitflyer', Auth.bitflyer),
    }


class ClientWebSocketResponse(aiohttp.ClientWebSocketResponse):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self._response.url.host in HeartbeatHosts.items:
            asyncio.create_task(HeartbeatHosts.items[self._response.url.host](self))
        if self._response.url.host in AuthHosts.items:
            if AuthHosts.items[self._response.url.host].name in self._response._session.__dict__['_apis']:
                asyncio.create_task(AuthHosts.items[self._response.url.host].func(self))
