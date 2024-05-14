import asyncio
from contextlib import suppress
from typing import Awaitable, Callable, Type
from unittest.mock import AsyncMock

import aiohttp
import pytest
import pytest_asyncio
from aiohttp import web
from aiohttp.test_utils import TestServer
from aiohttp.typedefs import StrOrURL
from yarl import URL

import pybotters
from pybotters.helpers.gmocoin import GMOCoinHelper
from pybotters.request import ClientRequest


@pytest_asyncio.fixture
async def pybotters_client(
    aiohttp_client_cls: Type[aiohttp.ClientSession],
    monkeypatch: pytest.MonkeyPatch,
):
    # From https://github.com/aio-libs/pytest-aiohttp/blob/v1.0.4/pytest_aiohttp/plugin.py#L139

    clients = []

    async def go(app, **kwargs):
        server = TestServer(app)
        aiohttp_client = aiohttp_client_cls(server)
        aiohttp_client._session._request_class = ClientRequest

        await aiohttp_client.start_server()
        clients.append(aiohttp_client)

        def dummy_request(method: str, str_or_url: StrOrURL, **kwargs):
            return aiohttp_client._request(method, URL(str_or_url).path_qs, **kwargs)

        _pybotters_client = pybotters.Client(**kwargs)
        monkeypatch.setattr(
            _pybotters_client._session,
            _pybotters_client._session._request.__name__,
            dummy_request,
        )
        return _pybotters_client

    yield go

    while clients:
        await clients.pop().close()


async def create_access_token(request: web.Request):
    return web.json_response(
        {
            "status": 0,
            "data": "xxxxxxxxxxxxxxxxxxxx",
            "responsetime": "2019-03-19T02:15:06.102Z",
        }
    )


async def extend_access_token(request: web.Request):
    return web.json_response(
        {
            "status": 0,
            "responsetime": "2019-03-19T02:15:06.102Z",
        }
    )


async def create_access_token_error(request: web.Request):
    return web.json_response(
        {
            "status": 5,
            "messages": [
                {
                    "message_code": "ERR-5201",
                    "message_string": "MAINTENANCE. Please wait for a while",
                }
            ],
        }
    )


async def extend_access_token_error(request: web.Request):
    return web.json_response(
        {
            "status": 1,
            "messages": [
                {
                    "message_code": "ERR-5106",
                    "message_string": "Invalid request parameter.",
                }
            ],
            "responsetime": "2024-05-11T02:02:40.501Z",
        }
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "base_url, extend_access_handler, create_access_handler, expected_token",
    [
        (
            "",
            extend_access_token,
            create_access_token,
            "aaaaaaaaaa",
        ),
        (
            "https://api.coin.z.com",
            extend_access_token,
            create_access_token,
            "aaaaaaaaaa",
        ),
        (
            "https://api.coin.z.com",
            extend_access_token_error,
            create_access_token,
            "xxxxxxxxxxxxxxxxxxxx",
        ),
        (
            "https://api.coin.z.com",
            extend_access_token_error,
            create_access_token_error,
            "aaaaaaaaaa",
        ),
    ],
)
async def test_gmo_manage_ws_token(
    extend_access_handler: Callable[..., Awaitable[web.Response]],
    create_access_handler: Callable[..., Awaitable[web.Response]],
    pybotters_client: Callable[..., Awaitable[pybotters.Client]],
    base_url: str,
    expected_token: str,
    monkeypatch: pytest.MonkeyPatch,
):
    async def sleep_canceller(delay):
        raise asyncio.CancelledError()

    app = web.Application()
    app.router.add_put("/private/v1/ws-auth", extend_access_handler)
    app.router.add_post("/private/v1/ws-auth", create_access_handler)
    client = await pybotters_client(app, base_url=base_url)

    token = "aaaaaaaaaa"
    url = f"wss://api.coin.z.com/ws/private/v1/{token}"
    m_ws = AsyncMock()
    m_ws.url = url

    helper = GMOCoinHelper(client)
    with monkeypatch.context() as m, suppress(asyncio.CancelledError):
        m.setattr(asyncio, asyncio.sleep.__name__, sleep_canceller)
        await helper.manage_ws_token(
            m_ws,
            token,
            300.0,
        )

    assert m_ws.url == f"wss://api.coin.z.com/ws/private/v1/{expected_token}"
