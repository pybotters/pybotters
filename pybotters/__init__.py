from __future__ import annotations

import asyncio
from typing import Any, Mapping, Optional, Tuple, Union

import aiohttp
from aiohttp import hdrs
from rich import print

from .client import Client
from .models import experimental
from .models.binance import BinanceDataStore
from .models.bitbank import bitbankDataStore
from .models.bitflyer import bitFlyerDataStore
from .models.bitmex import BitMEXDataStore
from .models.bybit import BybitDataStore
from .models.experimental.bybit import BybitInverseDataStore, BybitUSDTDataStore
from .models.ftx import FTXDataStore
from .models.gmocoin import GMOCoinDataStore
from .models.phemex import PhemexDataStore
from .typedefs import WsJsonHandler, WsStrHandler

__all__: Tuple[str, ...] = (
    'Client',
    'request',
    'get',
    'post',
    'put',
    'delete',
    'BybitDataStore',
    'BybitInverseDataStore',
    'BybitUSDTDataStore',
    'FTXDataStore',
    'BinanceDataStore',
    'bitbankDataStore',
    'bitFlyerDataStore',
    'BitMEXDataStore',
    'GMOCoinDataStore',
    'PhemexDataStore',
    'experimental',
    'print',
    'print_handler',
)


def print_handler(msg: Any, ws: aiohttp.ClientWebSocketResponse):
    print(msg)


class SyncClientResponse(aiohttp.ClientResponse):
    def text(self, *args, **kwargs) -> str:
        return self._loop.run_until_complete(super().text(*args, **kwargs))

    def json(self, *args, **kwargs) -> Any:
        return self._loop.run_until_complete(super().json(*args, **kwargs))


async def _request(
    method: str,
    url: str,
    *,
    params: Optional[Mapping[str, str]] = None,
    data: Any = None,
    apis: Optional[Union[dict[str, list[str]], str]] = None,
    **kwargs: Any,
) -> SyncClientResponse:
    if apis is None:
        apis = {}
    async with Client(apis=apis, response_class=SyncClientResponse) as client:
        async with client.request(
            method, url, params=params, data=data, **kwargs
        ) as resp:
            await resp.read()
            return resp


def request(
    method: str,
    url: str,
    *,
    params: Optional[Mapping[str, str]] = None,
    data: Any = None,
    apis: Optional[Union[dict[str, list[str]], str]] = None,
    **kwargs: Any,
) -> SyncClientResponse:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        _request(method, url, params=params, data=data, apis=apis, **kwargs)
    )


def get(
    url: str,
    *,
    params: Optional[Mapping[str, str]] = None,
    apis: Optional[Union[dict[str, list[str]], str]] = None,
    **kwargs: Any,
) -> SyncClientResponse:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        _request(hdrs.METH_GET, url, params=params, apis=apis, **kwargs)
    )


def post(
    url: str,
    *,
    data: Any = None,
    apis: Optional[Union[dict[str, list[str]], str]] = None,
    **kwargs: Any,
) -> SyncClientResponse:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        _request(hdrs.METH_POST, url, data=data, apis=apis, **kwargs)
    )


def put(
    url: str,
    *,
    data: Any = None,
    apis: Optional[Union[dict[str, list[str]], str]] = None,
    **kwargs: Any,
) -> SyncClientResponse:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        _request(hdrs.METH_PUT, url, data=data, apis=apis, **kwargs)
    )


def delete(
    url: str,
    *,
    data: Any = None,
    apis: Optional[Union[dict[str, list[str]], str]] = None,
    **kwargs: Any,
) -> SyncClientResponse:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        _request(hdrs.METH_DELETE, url, data=data, apis=apis, **kwargs)
    )


async def _ws_connect(
    url: str,
    *,
    send_str: Optional[Union[str, list[str]]] = None,
    send_json: Any = None,
    hdlr_str: Optional[WsStrHandler] = None,
    hdlr_json: Optional[WsJsonHandler] = None,
    apis: Optional[Union[dict[str, list[str]], str]] = None,
    **kwargs: Any,
) -> None:
    if apis is None:
        apis = {}
    async with Client(apis=apis) as client:
        wstask = await client.ws_connect(
            url,
            send_str=send_str,
            send_json=send_json,
            hdlr_str=hdlr_str,
            hdlr_json=hdlr_json,
            **kwargs,
        )
        await wstask


def ws_connect(
    url: str,
    *,
    send_str: Optional[Union[str, list[str]]] = None,
    send_json: Any = None,
    hdlr_str: Optional[WsStrHandler] = None,
    hdlr_json: Optional[WsJsonHandler] = None,
    apis: Optional[Union[dict[str, list[str]], str]] = None,
    **kwargs: Any,
) -> None:
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            _ws_connect(
                url,
                send_str=send_str,
                send_json=send_json,
                hdlr_str=hdlr_str,
                hdlr_json=hdlr_json,
                apis=apis,
                **kwargs,
            )
        )
    except KeyboardInterrupt:
        pass
