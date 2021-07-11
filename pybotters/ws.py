import asyncio
import base64
import datetime
import hashlib
import hmac
import logging
import time
from dataclasses import dataclass
from secrets import token_hex
from typing import Any, List, Optional, Union

import aiohttp
from aiohttp.http_websocket import json
from aiohttp.typedefs import StrOrURL

import pybotters

from .auth import Auth as _Auth

logger = logging.getLogger(__name__)


async def ws_run_forever(
    url: StrOrURL,
    session: aiohttp.ClientSession,
    event: asyncio.Event,
    *,
    send_str: Optional[Union[str, List[str]]] = None,
    send_json: Any = None,
    hdlr_str=None,
    hdlr_json=None,
    auth=_Auth,
    **kwargs: Any,
) -> None:
    if all([hdlr_str is None, hdlr_json is None]):
        hdlr_json = pybotters.print_handler
    iscorofunc_str = asyncio.iscoroutinefunction(hdlr_str)
    iscorofunc_json = asyncio.iscoroutinefunction(hdlr_json)
    while not session.closed:
        cooldown = asyncio.create_task(asyncio.sleep(60.0))
        try:
            async with session.ws_connect(url, auth=auth, **kwargs) as ws:
                event.set()
                if '_authtask' in ws.__dict__:
                    await ws.__dict__['_authtask']
                if send_str is not None:
                    if isinstance(send_str, list):
                        await asyncio.gather(*[ws.send_str(item) for item in send_str])
                    else:
                        await ws.send_str(send_str)
                if send_json is not None:
                    if isinstance(send_json, list):
                        await asyncio.gather(
                            *[ws.send_json(item) for item in send_json]
                        )
                    else:
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
        except (aiohttp.WSServerHandshakeError, aiohttp.ClientOSError) as e:
            logger.warning(repr(e))
        await cooldown


class Heartbeat:
    @staticmethod
    async def bybit(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('{"op":"ping"}')
            await asyncio.sleep(30.0)

    @staticmethod
    async def bitbank(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('2')
            await asyncio.sleep(15.0)

    @staticmethod
    async def liquid(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('{"event":"pusher:ping","data":{}}')
            await asyncio.sleep(60.0)

    @staticmethod
    async def ftx(ws: aiohttp.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('{"op":"ping"}')
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


class Auth:
    @staticmethod
    async def bitflyer(ws: aiohttp.ClientWebSocketResponse):
        key: str = ws._response._session.__dict__['_apis'][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__['_apis'][
            AuthHosts.items[ws._response.url.host].name
        ][1]

        timestamp = int(time.time())
        nonce = token_hex(16)
        sign = hmac.new(
            secret, f'{timestamp}{nonce}'.encode(), digestmod=hashlib.sha256
        ).hexdigest()
        await ws.send_json(
            {
                'method': 'auth',
                'params': {
                    'api_key': key,
                    'timestamp': timestamp,
                    'nonce': nonce,
                    'signature': sign,
                },
                'id': 'auth',
            }
        )
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = msg.json()
                if 'id' in data:
                    if data['id'] == 'auth':
                        break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break

    @staticmethod
    async def liquid(ws: aiohttp.ClientWebSocketResponse):
        key: str = ws._response._session.__dict__['_apis'][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__['_apis'][
            AuthHosts.items[ws._response.url.host].name
        ][1]

        json_payload = json.dumps(
            {
                'path': '/realtime',
                'nonce': str(int(time.time() * 1000)),
                'token_id': key,
            },
            separators=(',', ':'),
        ).encode()
        json_header = json.dumps(
            {'typ': 'JWT', 'alg': 'HS256'},
            separators=(',', ':'),
        ).encode()
        segments = [
            base64.urlsafe_b64encode(json_header).replace(b'=', b''),
            base64.urlsafe_b64encode(json_payload).replace(b'=', b''),
        ]
        signing_input = b'.'.join(segments)
        signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
        segments.append(base64.urlsafe_b64encode(signature).replace(b'=', b''))
        encoded_string = b'.'.join(segments).decode()

        await ws.send_json(
            {
                'event': 'quoine:auth_request',
                'data': {
                    'path': '/realtime',
                    'headers': {'X-Quoine-Auth': encoded_string},
                },
            }
        )

    @staticmethod
    async def ftx(ws: aiohttp.ClientWebSocketResponse):
        key: str = ws._response._session.__dict__['_apis'][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__['_apis'][
            AuthHosts.items[ws._response.url.host].name
        ][1]

        ts = int(time.time() * 1000)
        sign = hmac.new(
            secret, f'{ts}websocket_login'.encode(), digestmod=hashlib.sha256
        ).hexdigest()

        msg = {
            'op': 'login',
            'args': {'key': key, 'sign': sign, 'time': ts},
        }
        if 'FTX-SUBACCOUNT' in ws._response.request_info.headers:
            msg['args']['subaccount'] = ws._response.request_info.headers[
                'FTX-SUBACCOUNT'
            ]
        await ws.send_json(msg)

    @staticmethod
    async def phemex(ws: aiohttp.ClientWebSocketResponse):
        key: str = ws._response._session.__dict__['_apis'][
            AuthHosts.items[ws._response.url.host].name
        ][0]
        secret: bytes = ws._response._session.__dict__['_apis'][
            AuthHosts.items[ws._response.url.host].name
        ][1]

        expiry = int(time.time() + 60.0)
        signature = hmac.new(
            secret, f'{key}{expiry}'.encode(), digestmod=hashlib.sha256
        ).hexdigest()
        msg = {
            'method': 'user.auth',
            'params': ['API', key, signature, expiry],
            'id': 123,
        }
        await ws.send_json(msg)
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = msg.json()
                if data['result'] == {'status': 'success'}:
                    break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break


@dataclass
class Item:
    name: str
    func: Any


class HeartbeatHosts:
    items = {
        'stream.bitbank.cc': Heartbeat.bitbank,
        'stream.bybit.com': Heartbeat.bybit,
        'stream.bytick.com': Heartbeat.bybit,
        'stream-testnet.bybit.com': Heartbeat.bybit,
        'tap.liquid.com': Heartbeat.liquid,
        'ftx.com': Heartbeat.ftx,
        'stream.binance.com': Heartbeat.binance,
        'fstream.binance.com': Heartbeat.binance,
        'dstream.binance.com': Heartbeat.binance,
        'vstream.binance.com': Heartbeat.binance,
        'stream.binancefuture.com': Heartbeat.binance,
        'dstream.binancefuture.com': Heartbeat.binance,
        'testnet.binanceops.com': Heartbeat.binance,
        'testnetws.binanceops.com': Heartbeat.binance,
        'phemex.com': Heartbeat.phemex,
        'testnet.phemex.com': Heartbeat.phemex,
    }


class AuthHosts:
    items = {
        'ws.lightstream.bitflyer.com': Item('bitflyer', Auth.bitflyer),
        'tap.liquid.com': Item('liquid', Auth.liquid),
        'ftx.com': Item('ftx', Auth.ftx),
        'phemex.com': Item('phemex', Auth.phemex),
        'testnet.phemex.com': Item('phemex_testnet', Auth.phemex),
    }


class ClientWebSocketResponse(aiohttp.ClientWebSocketResponse):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self._response.url.host in HeartbeatHosts.items:
            self.__dict__['_pingtask'] = asyncio.create_task(
                HeartbeatHosts.items[self._response.url.host](self)
            )
        if self._response.__dict__['_auth'] is _Auth:
            if self._response.url.host in AuthHosts.items:
                if (
                    AuthHosts.items[self._response.url.host].name
                    in self._response._session.__dict__['_apis']
                ):
                    self.__dict__['_authtask'] = asyncio.create_task(
                        AuthHosts.items[self._response.url.host].func(self)
                    )
        self._lock = asyncio.Lock()

    async def send_str(self, *args, **kwargs) -> None:
        if self._response.url.host not in RequestLimitHosts.items:
            await super().send_str(*args, **kwargs)
        else:
            super_send_str = super().send_str(*args, **kwargs)
            await RequestLimitHosts.items[self._response.url.host](self, super_send_str)


class RequestLimit:
    @staticmethod
    async def gmocoin(ws: ClientWebSocketResponse, send_str):
        async with ws._lock:
            await send_str
            r = await ws._response._session.get(
                'https://api.coin.z.com/public/v1/status', auth=_Auth
            )
            data = await r.json()
            before = datetime.datetime.fromisoformat(data['responsetime'][:-1])
            while True:
                await asyncio.sleep(1.0)
                r = await ws._response._session.get(
                    'https://api.coin.z.com/public/v1/status', auth=_Auth
                )
                data = await r.json()
                after = datetime.datetime.fromisoformat(data['responsetime'][:-1])
                delta = after - before
                if delta.total_seconds() >= 1.0:
                    break


class RequestLimitHosts:
    items = {
        'api.coin.z.com': RequestLimit.gmocoin,
    }
