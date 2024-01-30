import asyncio
import functools
import json
import logging
from unittest.mock import ANY, AsyncMock, MagicMock, PropertyMock, call

import aiohttp
import pytest
import pytest_asyncio
import pytest_mock
from aiohttp import web
from aiohttp.test_utils import TestServer
from yarl import URL

import pybotters
import pybotters.auth
import pybotters.ws
from pybotters.ws import WebSocketApp


@pytest_asyncio.fixture
async def client_session():
    async with aiohttp.ClientSession() as session:
        yield session


hdlr_str = functools.partial(lambda msg, ws: None)
hdlr_bytes = functools.partial(lambda msg, ws: None)
hdlr_json = functools.partial(lambda msg, ws: None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "test_input",
        "expected",
    ),
    [
        (
            {
                "send_str": "spam",
                "send_bytes": b"egg",
                "send_json": {"bacon": "tomato"},
                "hdlr_str": hdlr_str,
                "hdlr_bytes": hdlr_bytes,
                "hdlr_json": hdlr_json,
            },
            {
                "send_str": ["spam"],
                "send_bytes": [b"egg"],
                "send_json": [{"bacon": "tomato"}],
                "hdlr_str": [hdlr_str],
                "hdlr_bytes": [hdlr_bytes],
                "hdlr_json": [hdlr_json],
            },
        ),
        (
            {
                "send_str": ["spam"],
                "send_bytes": [b"egg"],
                "send_json": [{"bacon": "tomato"}],
                "hdlr_str": [hdlr_str],
                "hdlr_bytes": [hdlr_bytes],
                "hdlr_json": [hdlr_json],
            },
            {
                "send_str": ["spam"],
                "send_bytes": [b"egg"],
                "send_json": [{"bacon": "tomato"}],
                "hdlr_str": [hdlr_str],
                "hdlr_bytes": [hdlr_bytes],
                "hdlr_json": [hdlr_json],
            },
        ),
        (
            {
                "send_str": None,
                "send_bytes": None,
                "send_json": None,
                "hdlr_str": None,
                "hdlr_bytes": None,
                "hdlr_json": None,
            },
            {
                "send_str": [],
                "send_bytes": [],
                "send_json": [],
                "hdlr_str": [],
                "hdlr_bytes": [],
                "hdlr_json": [],
            },
        ),
        (
            {
                "heartbeat": 10.0,
            },
            {
                "send_str": [],
                "send_bytes": [],
                "send_json": [],
                "hdlr_str": [],
                "hdlr_bytes": [],
                "hdlr_json": [],
                "heartbeat": 10.0,
            },
        ),
    ],
)
async def test_websocketapp_init(
    mocker: pytest_mock.MockerFixture,
    client_session: aiohttp.ClientSession,
    test_input,
    expected,
):
    m_run_forever = mocker.patch.object(
        WebSocketApp, WebSocketApp._run_forever.__name__
    )

    url = "wss://example.com"
    backoff = (1.92, 60.0, 1.618, 5.0)

    ws = WebSocketApp(
        client_session,
        url,
        **test_input,
        backoff=backoff,
    )

    assert ws._session == client_session
    assert ws._url == url
    assert isinstance(ws._task, asyncio.Task)
    assert m_run_forever.called
    assert list(m_run_forever.call_args) == [
        tuple(),
        dict(
            **expected,
            backoff=backoff,
        ),
    ]


@pytest_asyncio.fixture
async def websocketapp(
    mocker: pytest_mock.MockerFixture, client_session: aiohttp.ClientSession
):
    m_run_forever = mocker.patch.object(
        WebSocketApp, WebSocketApp._run_forever.__name__
    )

    ws = WebSocketApp(
        client_session,
        "wss://example.com",
        backoff=WebSocketApp._DEFAULT_BACKOFF,
    )

    mocker.stop(m_run_forever)

    return ws


@pytest.mark.asyncio
async def test_websocketapp_run_forever(
    mocker: pytest_mock.MockerFixture, websocketapp: WebSocketApp
):
    websocketapp._event.set()
    websocketapp._current_ws = MagicMock()

    m_ws_connect = mocker.patch.object(WebSocketApp, WebSocketApp._ws_connect.__name__)
    m_random = mocker.patch("random.random")
    m_asyncio_sleep = mocker.patch("asyncio.sleep")

    m_ws_connect.side_effect = [
        aiohttp.WSServerHandshakeError(MagicMock(), tuple()),
        aiohttp.WSServerHandshakeError(MagicMock(), tuple()),
        aiohttp.WSServerHandshakeError(MagicMock(), tuple()),
        None,
        aiohttp.WSServerHandshakeError(MagicMock(), tuple()),
        KeyboardInterrupt("BOOM"),
    ]
    m_random.return_value = 42.0

    assert websocketapp._event.is_set()

    with pytest.raises(KeyboardInterrupt, match="BOOM"):
        await websocketapp._run_forever(
            send_str=["spam"],
            send_bytes=[b"egg"],
            send_json=[{"bacon": "tomato"}],
            hdlr_str=[hdlr_str],
            hdlr_bytes=[hdlr_bytes],
            hdlr_json=[hdlr_json],
            backoff=(10.0, 30.0, 2.0, 1.0),
            heartbeat=10.0,
        )

    assert list(m_ws_connect.call_args) == [
        tuple(),
        dict(
            send_str=["spam"],
            send_bytes=[b"egg"],
            send_json=[{"bacon": "tomato"}],
            hdlr_str=[hdlr_str],
            hdlr_bytes=[hdlr_bytes],
            hdlr_json=[hdlr_json],
            heartbeat=10.0,
        ),
    ]
    assert m_random.call_count == 2
    assert m_asyncio_sleep.call_args_list == [
        call(42.0),
        call(20),
        call(30),
        call(42.0),
    ]

    assert websocketapp._current_ws is None
    assert not websocketapp._event.is_set()


@pytest.mark.asyncio
async def test_ws_connect(
    mocker: pytest_mock.MockerFixture, websocketapp: WebSocketApp
):
    m_ws_connect = mocker.patch("aiohttp.client.ClientSession.ws_connect")
    m_wsresp: AsyncMock = m_ws_connect.return_value.__aenter__.return_value
    m_wsresp.__aiter__.return_value = [
        aiohttp.WSMessage(aiohttp.WSMsgType.TEXT, '{"spam":"egg"}', None),
        aiohttp.WSMessage(aiohttp.WSMsgType.BINARY, b'{"bacon":"tomato"}', None),
        aiohttp.WSMessage(aiohttp.WSMsgType.TEXT, "__TEXT__", None),
        aiohttp.WSMessage(aiohttp.WSMsgType.BINARY, b"__BYTES__", None),
    ]
    hdlr_str = MagicMock()
    hdlr_bytes = MagicMock()
    hdlr_json = MagicMock()

    assert not websocketapp._event.is_set()

    await websocketapp._ws_connect(
        send_str=["spam"],
        send_bytes=[b"egg"],
        send_json=[{"bacon": "tomato"}],
        hdlr_str=[hdlr_str],
        hdlr_bytes=[hdlr_bytes],
        hdlr_json=[hdlr_json],
        heartbeat=10.0,
    )
    await asyncio.create_task(asyncio.sleep(0))

    assert list(m_ws_connect.call_args) == [
        tuple([websocketapp._url]),
        dict(heartbeat=10.0),
    ]
    assert websocketapp._event.is_set()

    assert m_wsresp.send_str.call_args == call("spam")
    assert m_wsresp.send_bytes.call_args == call(b"egg")
    assert m_wsresp.send_json.call_args == call({"bacon": "tomato"})

    assert hdlr_str.call_args_list == [
        call('{"spam":"egg"}', m_wsresp),
        call("__TEXT__", m_wsresp),
    ]
    assert hdlr_bytes.call_args_list == [
        call(b'{"bacon":"tomato"}', m_wsresp),
        call(b"__BYTES__", m_wsresp),
    ]
    assert hdlr_json.call_args_list == [
        call({"spam": "egg"}, m_wsresp),
        call({"bacon": "tomato"}, m_wsresp),
    ]


@pytest.mark.asyncio
async def test_websocketapp_wait(websocketapp: WebSocketApp):
    websocketapp._task.cancel()
    websocketapp._task = asyncio.create_task(AsyncMock()._run_forever())

    assert not websocketapp._task.done()

    await websocketapp.wait()

    assert websocketapp._task.done()


@pytest.mark.asyncio
async def test_websocketapp_await(websocketapp: WebSocketApp):
    websocketapp._task.cancel()
    websocketapp._task = asyncio.create_task(AsyncMock()._run_forever())
    websocketapp._task.add_done_callback(lambda f: websocketapp._event.set())

    assert not websocketapp._event.is_set()

    await websocketapp

    assert websocketapp._event.is_set()


@pytest.mark.asyncio
async def test_websocketapp_url(websocketapp: WebSocketApp):
    new_url = "wss://new-websocket-url.com"
    assert websocketapp.url != new_url

    websocketapp.url = new_url

    assert websocketapp.url == new_url


@pytest.mark.asyncio
async def test_websocketapp_current_ws(websocketapp: WebSocketApp):
    new_current_ws = MagicMock()
    websocketapp._current_ws = new_current_ws

    assert websocketapp.current_ws == new_current_ws


@pytest_asyncio.fixture
async def test_server():
    call_count = 0

    async def echo_json(request: web.Request):
        nonlocal call_count
        call_count += 1

        if call_count in (2, 3, 4):
            raise web.HTTPServiceUnavailable()

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        msg = await ws.receive_json()
        await ws.send_json(msg)

        await ws.close()
        return ws

    app = web.Application()
    app.add_routes([web.get("/ws", echo_json)])

    async with TestServer(app) as server:
        yield server


@pytest.mark.asyncio
async def test_websocketapp_functional(
    mocker: pytest_mock.MockerFixture, test_server: TestServer
):
    m_random = mocker.patch("random.random")
    m_random.return_value = 42.0
    m_asyncio_sleep = mocker.patch("asyncio.sleep")

    wsq = pybotters.WebSocketQueue()
    send_message = {"spam": "egg"}

    async def message_ping_pong():
        async with pybotters.Client() as client:
            ws = await client.ws_connect(
                f"ws://localhost:{test_server.port}/ws",
                send_json=send_message,
                hdlr_json=wsq.onmessage,
                backoff=(10.0, 30.0, 2.0, 1.0),
            )
            await ws.wait()

    wstask = asyncio.create_task(message_ping_pong())
    received_messages = [
        (await asyncio.wait_for(wsq.get(), timeout=5.0)),
        (await asyncio.wait_for(wsq.get(), timeout=5.0)),
    ]
    wstask.cancel()
    await asyncio.wait([wstask], timeout=5.0)

    assert received_messages == [send_message, send_message]
    assert wstask.cancelled()

    assert m_random.call_count == 1
    assert m_asyncio_sleep.call_args_list == [
        call(42.0),
        call(20),
        call(30),
    ]


def test_heartbeathosts():
    assert hasattr(pybotters.ws.HeartbeatHosts, "items")
    assert isinstance(pybotters.ws.HeartbeatHosts.items, dict)
    for host, func in pybotters.ws.HeartbeatHosts.items.items():
        assert isinstance(host, str)
        assert callable(func)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (URL("ws://example.com"), True),
        (URL("ws://not-example.com"), False),
    ],
)
async def test_wsresponse_heartbeat(
    mocker: pytest_mock.MockerFixture, test_input, expected
):
    m_heartbeat = AsyncMock()
    items = {
        "example.com": m_heartbeat,
    }
    mocker.patch.object(pybotters.ws.HeartbeatHosts, "items", items)
    m_resp = MagicMock()
    m_resp.url = test_input
    m_resp.__dict__["_auth"] = None

    wsresp = pybotters.ws.ClientWebSocketResponse(
        reader=AsyncMock(),
        writer=AsyncMock(),
        protocol=None,
        response=m_resp,
        timeout=10.0,
        autoclose=True,
        autoping=True,
        loop=asyncio.get_running_loop(),
    )

    assert m_heartbeat.called is expected
    if expected:
        assert m_heartbeat.call_args == call(wsresp)
        await asyncio.wait_for(wsresp.__dict__["_pingtask"], timeout=5.0)
        assert wsresp.__dict__["_pingtask"].done()


def test_authhosts():
    assert hasattr(pybotters.ws.AuthHosts, "items")
    assert isinstance(pybotters.ws.AuthHosts.items, dict)
    for host, item in pybotters.ws.AuthHosts.items.items():
        assert isinstance(host, str)
        assert isinstance(item, pybotters.ws.Item)
        assert isinstance(item.name, str)
        assert callable(item.func)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "test_input",
        "expected",
    ),
    [
        # called auth task
        (
            {
                "auth": pybotters.auth.Auth,
                "url": URL("ws://example.com"),
                "apis": {"example": ["KEY", b"SECRET"]},
            },
            {"called": True},
        ),
        # not called auth task, api name dose not exist in apis
        (
            {
                "auth": pybotters.auth.Auth,
                "url": URL("ws://example.com"),
                "apis": {"not-example": ["KEY", b"SECRET"]},
            },
            {"called": False},
        ),
        # not called auth task, url dose not exist in hosts
        (
            {
                "auth": pybotters.auth.Auth,
                "url": URL("ws://not-example.com"),
                "apis": {"example": ["KEY", b"SECRET"]},
            },
            {"called": False},
        ),
        # not called auth task, auth is None
        (
            {
                "auth": None,
                "url": URL("ws://example.com"),
                "apis": {"example": ["KEY", b"SECRET"]},
            },
            {"called": False},
        ),
    ],
)
async def test_wsresponse_auth(mocker: pytest_mock.MockerFixture, test_input, expected):
    m_auth = AsyncMock()
    items = {
        "example.com": pybotters.ws.Item("example", m_auth),
    }
    mocker.patch.object(pybotters.ws.AuthHosts, "items", items)
    m_resp = MagicMock()
    m_resp.__dict__["_auth"] = test_input["auth"]
    m_resp.url = test_input["url"]
    m_resp._session.__dict__["_apis"] = test_input["apis"]

    wsresp = pybotters.ws.ClientWebSocketResponse(
        reader=AsyncMock(),
        writer=AsyncMock(),
        protocol=None,
        response=m_resp,
        timeout=10.0,
        autoclose=True,
        autoping=True,
        loop=asyncio.get_running_loop(),
    )

    assert m_auth.called is expected["called"]
    if expected["called"]:
        assert m_auth.call_args == call(wsresp)
        await asyncio.wait_for(wsresp.__dict__["_authtask"], timeout=5.0)
        assert wsresp.__dict__["_authtask"].done()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "test_input",
        "expected",
    ),
    [
        (URL("ws://example.com"), True),
        (URL("ws://not-example.com"), False),
    ],
)
async def test_wsresponse_send_str(
    mocker: pytest_mock.MockerFixture, test_input, expected
):
    m_ratelimit = AsyncMock()
    items = {
        "example.com": m_ratelimit,
    }
    mocker.patch.object(pybotters.ws.RequestLimitHosts, "items", items)
    m_resp = MagicMock()
    m_resp.__dict__["_auth"] = None
    m_resp.url = test_input

    wsresp = pybotters.ws.ClientWebSocketResponse(
        reader=AsyncMock(),
        writer=AsyncMock(),
        protocol=None,
        response=m_resp,
        timeout=10.0,
        autoclose=True,
        autoping=True,
        loop=asyncio.get_running_loop(),
    )
    await asyncio.wait_for(wsresp.send_str("foo"), timeout=5.0)

    assert m_ratelimit.called is expected
    if expected:
        assert m_ratelimit.call_args == call(wsresp, ANY)
        # Avoid the "coroutine was never awaited" warning
        await m_ratelimit.call_args.args[1]


@pytest.mark.asyncio
async def test_wsresponse_send_json_itself(mocker: pytest_mock.MockerFixture):
    m_auth = AsyncMock()
    items = {
        "example.com": pybotters.ws.Item("example", m_auth),
    }
    mocker.patch.object(pybotters.ws.AuthHosts, "items", items)
    m_resp = MagicMock()
    m_resp.__dict__["_auth"] = pybotters.auth.Auth
    m_resp.url = URL("ws://example.com")
    m_resp._session.__dict__["_apis"] = {"example": ["KEY", b"SECRET"]}

    wsresp = pybotters.ws.ClientWebSocketResponse(
        reader=AsyncMock(),
        writer=AsyncMock(),
        protocol=None,
        response=m_resp,
        timeout=10.0,
        autoclose=True,
        autoping=True,
        loop=asyncio.get_running_loop(),
    )
    await asyncio.wait_for(wsresp.send_json({"foo": "bar"}, _itself=False), timeout=5.0)

    assert m_auth.called
    assert m_auth.call_args == call(wsresp)
    assert wsresp.__dict__["_authtask"].done()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "test_input",
        "expected",
    ),
    [
        (
            # called, send_json(data)
            {
                "argument": call({"foo": "bar"}, auth=pybotters.auth.Auth),
                "url": URL("ws://example.com"),
                "apis": {"example": ["KEY", b"SECRET"]},
            },
            {
                "called": True,
                "data": {"foo": "bar"},
            },
        ),
        (
            # called, send_json(data=data)
            {
                "argument": call(data={"foo": "bar"}, auth=pybotters.auth.Auth),
                "url": URL("ws://example.com"),
                "apis": {"example": ["KEY", b"SECRET"]},
            },
            {
                "called": True,
                "data": {"foo": "bar"},
            },
        ),
        (
            # not called, data is None
            {
                "argument": call(None, auth=pybotters.auth.Auth),
                "url": URL("ws://example.com"),
                "apis": {"example": ["KEY", b"SECRET"]},
            },
            {
                "called": False,
                "data": None,
            },
        ),
        (
            # not called, api name dose not exist in apis
            {
                "argument": call({"foo": "bar"}, auth=pybotters.auth.Auth),
                "url": URL("ws://example.com"),
                "apis": {"not-example": ["KEY", b"SECRET"]},
            },
            {
                "called": False,
                "data": None,
            },
        ),
        (
            # not called, url dose not exist in hosts
            {
                "argument": call({"foo": "bar"}, auth=pybotters.auth.Auth),
                "url": URL("ws://not-example.com"),
                "apis": {"example": ["KEY", b"SECRET"]},
            },
            {
                "called": False,
                "data": None,
            },
        ),
        (
            # not called, auth argument is None
            {
                "argument": call({"foo": "bar"}, auth=None),
                "url": URL("ws://example.com"),
                "apis": {"example": ["KEY", b"SECRET"]},
            },
            {
                "called": False,
                "data": None,
            },
        ),
    ],
)
async def test_wsresponse_send_json_msgsign(
    mocker: pytest_mock.MockerFixture, test_input, expected
):
    m_msgsign = MagicMock()
    items = {
        "example.com": pybotters.ws.Item("example", m_msgsign),
    }
    mocker.patch.object(pybotters.ws.MessageSignHosts, "items", items)
    m_resp = MagicMock()
    m_resp.__dict__["_auth"] = None
    m_resp.url = test_input["url"]
    m_resp._session.__dict__["_apis"] = test_input["apis"]

    wsresp = pybotters.ws.ClientWebSocketResponse(
        reader=AsyncMock(),
        writer=AsyncMock(),
        protocol=None,
        response=m_resp,
        timeout=10.0,
        autoclose=True,
        autoping=True,
        loop=asyncio.get_running_loop(),
    )
    await asyncio.wait_for(
        wsresp.send_json(*test_input["argument"].args, **test_input["argument"].kwargs),
        timeout=5.0,
    )

    assert m_msgsign.called is expected["called"]
    if expected["called"]:
        assert m_msgsign.call_args == call(wsresp, expected["data"])


@pytest.mark.asyncio
async def test_websocketqueue():
    wsq = pybotters.ws.WebSocketQueue()

    menu = [
        "spam",
        "ham",
        "eggs",
    ]
    ws = MagicMock()

    for dish in menu:
        wsq.onmessage(dish, ws)

    result = []
    async for item in wsq:
        result.append(item)

        if len(result) == len(menu):
            break

    assert result == menu


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("test_input",),
    [
        (pybotters.ws.Heartbeat.bybit,),
        (pybotters.ws.Heartbeat.bitbank,),
        (pybotters.ws.Heartbeat.phemex,),
        (pybotters.ws.Heartbeat.okx,),
        (pybotters.ws.Heartbeat.bitget,),
        (pybotters.ws.Heartbeat.mexc,),
        (pybotters.ws.Heartbeat.kucoin,),
    ],
)
async def test_heartbeat_text(mocker: pytest_mock.MockerFixture, test_input):
    m_wsresp = AsyncMock()
    type(m_wsresp).closed = PropertyMock(side_effect=[False, True])
    m_asyncio_sleep = mocker.patch("asyncio.sleep")

    await asyncio.wait_for(test_input(m_wsresp), timeout=5.0)

    assert m_wsresp.send_str.called
    assert m_asyncio_sleep.called


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("test_input",),
    [
        (pybotters.ws.Heartbeat.binance,),
    ],
)
async def test_heartbeat_frame(mocker: pytest_mock.MockerFixture, test_input):
    m_wsresp = AsyncMock()
    type(m_wsresp).closed = PropertyMock(side_effect=[False, True])
    m_asyncio_sleep = mocker.patch("asyncio.sleep")

    await asyncio.wait_for(test_input(m_wsresp), timeout=5.0)

    assert m_wsresp.pong.called
    assert m_asyncio_sleep.called


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "test_input",
        "expected",
    ),
    [
        # signed - mainnet
        (
            {
                "url": URL("wss://stream.bybit.com/v5/private"),
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps(
                            {
                                "success": True,
                                "ret_msg": "",
                                "op": "auth",
                                "conn_id": "cejreaspqfh3sjdnldmg-p",
                            }
                        ),
                        None,
                    ),
                ],
            },
            {
                "call_args": call(
                    {
                        "op": "auth",
                        "args": [
                            "77SQfUG7X33JhYZ3Jswpx5To",
                            2085848901000,
                            "a8bcd91ad5f8efdaefaf4ca6f38e551d739d6b42c2b54c85667fb181ecbc29a4",  # noqa: E501
                        ],
                    },
                    _itself=True,
                ),
                "records": [],
            },
        ),
        # signed - testnet
        (
            {
                "url": URL("wss://stream.bybit.com/v5/private"),
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps(
                            {
                                "success": True,
                                "ret_msg": "",
                                "op": "auth",
                                "conn_id": "cejreaspqfh3sjdnldmg-p",
                            }
                        ),
                        None,
                    ),
                ],
            },
            {
                "call_args": call(
                    {
                        "op": "auth",
                        "args": [
                            "77SQfUG7X33JhYZ3Jswpx5To",
                            2085848901000,
                            "a8bcd91ad5f8efdaefaf4ca6f38e551d739d6b42c2b54c85667fb181ecbc29a4",  # noqa: E501
                        ],
                    },
                    _itself=True,
                ),
                "records": [],
            },
        ),
        # invalid signature
        (
            {
                "url": URL("wss://stream.bybit.com/v5/private"),
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps(
                            {
                                "success": False,
                                "ret_msg": "Params Error",
                                "op": "auth",
                                "conn_id": "cejreaspqfh3sjdnldmg-p",
                            }
                        ),
                        None,
                    ),
                ],
            },
            {
                "call_args": call(
                    {
                        "op": "auth",
                        "args": [
                            "77SQfUG7X33JhYZ3Jswpx5To",
                            2085848901000,
                            "a8bcd91ad5f8efdaefaf4ca6f38e551d739d6b42c2b54c85667fb181ecbc29a4",  # noqa: E501
                        ],
                    },
                    _itself=True,
                ),
                "records": [("pybotters.ws", logging.WARNING, ANY)],
            },
        ),
        # not signed
        (
            {
                "url": URL("wss://stream.bybit.com/v5/public/spot"),
                "messages": [],
            },
            {"call_args": None, "records": []},
        ),
    ],
)
async def test_auth_bybit_ws(
    mocker: pytest_mock.MockerFixture,
    caplog: pytest.LogCaptureFixture,
    test_input,
    expected,
):
    mocker.patch("time.time", return_value=2085848896.0)

    m_wsresp = AsyncMock()
    m_wsresp._response.url = test_input["url"]
    m_wsresp._response._session.__dict__["_apis"] = {
        "bybit": (
            "77SQfUG7X33JhYZ3Jswpx5To",
            b"PrYiNnCnP76YzpTLvRtV9O1RBa5ecOXqrOTyXuTADCEXYoEX",
        ),
        "bybit_testnet": (
            "77SQfUG7X33JhYZ3Jswpx5To",
            b"PrYiNnCnP76YzpTLvRtV9O1RBa5ecOXqrOTyXuTADCEXYoEX",
        ),
    }
    m_wsresp.__aiter__.return_value = test_input["messages"]

    await asyncio.wait_for(pybotters.ws.Auth.bybit(m_wsresp), timeout=5.0)

    assert m_wsresp.send_json.call_args == expected["call_args"]
    assert caplog.record_tuples == expected["records"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "test_input",
        "expected",
    ),
    [
        # signed
        (
            {
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps({"jsonrpc": "2.0", "id": "auth", "result": True}),
                        None,
                    ),
                ],
            },
            {
                "records": [],
            },
        ),
        # invalid signature
        (
            {
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": "auth",
                                "error": {
                                    "code": -32602,
                                    "message": "Invalid signature",
                                },
                            }
                        ),
                        None,
                    ),
                ],
            },
            {
                "records": [("pybotters.ws", logging.WARNING, ANY)],
            },
        ),
    ],
)
async def test_auth_bitflyer_ws(
    mocker: pytest_mock.MockerFixture,
    caplog: pytest.LogCaptureFixture,
    test_input,
    expected,
):
    mocker.patch("time.time", return_value=2085848896.0)
    mocker.patch(
        "pybotters.ws.token_hex", return_value="d73b41172d6deca2285e8e58533db082"
    )

    m_wsresp = AsyncMock()
    m_wsresp._response.url = URL("wss://ws.lightstream.bitflyer.com/json-rpc")
    m_wsresp._response._session.__dict__["_apis"] = {
        "bitflyer": (
            "Pcm1rbtSRqKxTvirZDDOct1k",
            b"AKHZlv3PoAXZ0KXIKIVKOmS4ji3rV7ZIVIJRstwyplaw0FQ4",
        ),
    }
    m_wsresp.__aiter__.return_value = test_input["messages"]

    await asyncio.wait_for(pybotters.ws.Auth.bitflyer(m_wsresp), timeout=5.0)

    assert m_wsresp.send_json.call_args == call(
        {
            "method": "auth",
            "params": {
                "api_key": "Pcm1rbtSRqKxTvirZDDOct1k",
                "timestamp": 2085848896000,
                "nonce": "d73b41172d6deca2285e8e58533db082",
                "signature": (
                    "f47526dec80c4773815fb1121058c2e3bcc531d1224b683e8babf76e52b0ba9c"  # noqa: E501
                ),
            },
            "id": "auth",
        },
        _itself=True,
    )
    assert caplog.record_tuples == expected["records"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "test_input",
        "expected",
    ),
    [
        # signed - mainnet
        (
            {
                "url": URL("wss://ws.phemex.com/ws"),
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps(
                            {
                                "error": None,
                                "id": 123,
                                "result": {"status": "success"},
                            }
                        ),
                        None,
                    ),
                ],
            },
            {
                "records": [],
            },
        ),
        # signed - testnet
        (
            {
                "url": URL("wss://testnet-api.phemex.com/ws"),
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps(
                            {
                                "error": None,
                                "id": 123,
                                "result": {"status": "success"},
                            }
                        ),
                        None,
                    ),
                ],
            },
            {
                "records": [],
            },
        ),
        # invalid signature
        (
            {
                "url": URL("wss://ws.phemex.com/ws"),
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps(
                            {
                                "error": {
                                    "code": 6012,
                                    "message": "invalid login token",
                                },
                                "id": 123,
                                "result": None,
                            }
                        ),
                        None,
                    ),
                ],
            },
            {
                "records": [("pybotters.ws", logging.WARNING, ANY)],
            },
        ),
    ],
)
async def test_auth_phemex_ws(
    mocker: pytest_mock.MockerFixture,
    caplog: pytest.LogCaptureFixture,
    test_input,
    expected,
):
    mocker.patch("time.time", return_value=2085848896.0)

    m_wsresp = AsyncMock()
    m_wsresp._response.url = test_input["url"]
    m_wsresp._response._session.__dict__["_apis"] = {
        "phemex": (
            "9kYxQXZ6PrR8h17lsVdDcpnJ",
            b"ZBAUiPBTQOjYgTihYnZMw2HFkTooufRnNY5iuahBPMspRYQJ",
        ),
        "phemex_testnet": (
            "9kYxQXZ6PrR8h17lsVdDcpnJ",
            b"ZBAUiPBTQOjYgTihYnZMw2HFkTooufRnNY5iuahBPMspRYQJ",
        ),
    }
    m_wsresp.__aiter__.return_value = test_input["messages"]

    await asyncio.wait_for(pybotters.ws.Auth.phemex(m_wsresp), timeout=5.0)

    assert m_wsresp.send_json.call_args == call(
        {
            "method": "user.auth",
            "params": [
                "API",
                "9kYxQXZ6PrR8h17lsVdDcpnJ",
                "196f317edfa0662ec3d388099683b40a25607919ca3546b131108b9ee5cbed4a",
                2085848956,
            ],
            "id": 123,
        },
        _itself=True,
    )
    assert caplog.record_tuples == expected["records"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "test_input",
        "expected",
    ),
    [
        # signed - live trading
        (
            {
                "url": URL("wss://ws.okx.com:8443/ws/v5/private"),
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        "pong",
                        None,
                    ),
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps(
                            {
                                "event": "login",
                                "code": "0",
                                "msg": "",
                                "connId": "a4d3ae55",
                            }
                        ),
                        None,
                    ),
                ],
            },
            {
                "records": [],
            },
        ),
        # signed - demo trading
        (
            {
                "url": URL("wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999"),
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        "pong",
                        None,
                    ),
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps(
                            {
                                "event": "login",
                                "code": "0",
                                "msg": "",
                                "connId": "a4d3ae55",
                            }
                        ),
                        None,
                    ),
                ],
            },
            {
                "records": [],
            },
        ),
        # invalid signature
        (
            {
                "url": URL("wss://ws.okx.com:8443/ws/v5/private"),
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps(
                            {
                                "event": "error",
                                "code": "60009",
                                "msg": "Login failed.",
                                "connId": "a4d3ae55",
                            }
                        ),
                        None,
                    ),
                ],
            },
            {
                "records": [("pybotters.ws", logging.WARNING, ANY)],
            },
        ),
    ],
)
async def test_auth_okx_ws(
    mocker: pytest_mock.MockerFixture,
    caplog: pytest.LogCaptureFixture,
    test_input,
    expected,
):
    mocker.patch("time.time", return_value=2085848896.0)

    m_wsresp = AsyncMock()
    m_wsresp._response.url = test_input["url"]
    m_wsresp._response._session.__dict__["_apis"] = {
        "okx": (
            "gYmX9fr0kqqxptUlDKESxetg",
            b"YUJHBdFNrbz7atmV3f261ZhdRffTo4S9KZKC7C7qdqcHbRR4",
            "MyPassphrase123",
        ),
        "okx_demo": (
            "gYmX9fr0kqqxptUlDKESxetg",
            b"YUJHBdFNrbz7atmV3f261ZhdRffTo4S9KZKC7C7qdqcHbRR4",
            "MyPassphrase123",
        ),
    }
    m_wsresp.__aiter__.return_value = test_input["messages"]

    await asyncio.wait_for(pybotters.ws.Auth.okx(m_wsresp), timeout=5.0)

    assert m_wsresp.send_json.call_args == call(
        {
            "op": "login",
            "args": [
                {
                    "apiKey": "gYmX9fr0kqqxptUlDKESxetg",
                    "passphrase": "MyPassphrase123",
                    "timestamp": "2085848896",
                    "sign": "6QVd7Mgd70We2/oDJr0+KnqxXZ+Gf1zIIl3qJk/Pqx8=",
                }
            ],
        },
        _itself=True,
    )
    assert caplog.record_tuples == expected["records"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "test_input",
        "expected",
    ),
    [
        # signed
        (
            {
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        "pong",
                        None,
                    ),
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps({"event": "login", "code": "0", "msg": ""}),
                        None,
                    ),
                ],
            },
            {
                "records": [],
            },
        ),
        # invalid signature
        (
            {
                "messages": [
                    aiohttp.WSMessage(
                        aiohttp.WSMsgType.TEXT,
                        json.dumps({"event": "error", "code": "30005", "msg": "error"}),
                        None,
                    ),
                ],
            },
            {
                "records": [("pybotters.ws", logging.WARNING, ANY)],
            },
        ),
    ],
)
async def test_auth_bitget_ws(
    mocker: pytest_mock.MockerFixture,
    caplog: pytest.LogCaptureFixture,
    test_input,
    expected,
):
    mocker.patch("time.time", return_value=2085848896.0)

    m_wsresp = AsyncMock()
    m_wsresp._response.url = URL("wss://ws.bitget.com/mix/v1/stream")
    m_wsresp._response._session.__dict__["_apis"] = {
        "bitget": (
            "jbcfbye8AJzXxXwMKluXM12t",
            b"mVd40qhnarPtxk3aqg0FCyY1qlTgBOKOXEcmMYfkerGUKmvr",
            "MyPassphrase123",
        ),
    }
    m_wsresp.__aiter__.return_value = test_input["messages"]

    await asyncio.wait_for(pybotters.ws.Auth.bitget(m_wsresp), timeout=5.0)

    assert m_wsresp.send_json.call_args == call(
        {
            "op": "login",
            "args": [
                {
                    "api_key": "jbcfbye8AJzXxXwMKluXM12t",
                    "passphrase": "MyPassphrase123",
                    "timestamp": "2085848896",
                    "sign": "RmRhCixsMce8H7j2uyvR6sk11tCRbYenohbd87nchH8=",
                }
            ],
        },
        _itself=True,
    )
    assert caplog.record_tuples == expected["records"]


@pytest.mark.asyncio
async def test_auth_mexc_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)

    m_wsresp = AsyncMock()
    m_wsresp._response.url = URL("wss://contract.mexc.com/ws")
    m_wsresp._response._session.__dict__["_apis"] = {
        "mexc": (
            "0uVJRVNmR2ZHiCXtf6yEwrwy",
            b"39aw3fMqFhHsuhbkQ0wa8JzuUgodvbTVl9tZblpSKFnB9Qh3",
        ),
    }

    await pybotters.ws.Auth.mexc(m_wsresp)

    assert m_wsresp.send_json.call_args == call(
        {
            "method": "login",
            "param": {
                "apiKey": "0uVJRVNmR2ZHiCXtf6yEwrwy",
                "reqTime": "2085848896",
                "signature": "cd92edf98d52d973e96ffdce6f845c930f9900c5e4aa47ca4ef81d80533ab882",  # noqa: E501
            },
        },
        _itself=True,
    )


@pytest.mark.asyncio
async def test_ratelimit_gmocoin(mocker: pytest_mock.MockerFixture):
    m_sleep = mocker.patch("asyncio.sleep")

    m_resp = AsyncMock()
    m_resp.json.side_effect = [
        {
            "status": 0,
            "data": {"status": "OPEN"},
            "responsetime": "2024-01-18T02:28:40.000Z",
        },
        {
            "status": 0,
            "data": {"status": "OPEN"},
            "responsetime": "2024-01-18T02:28:40.800Z",
        },
        {
            "status": 0,
            "data": {"status": "OPEN"},
            "responsetime": "2024-01-18T02:28:41.600Z",
        },
        AssertionError(),
    ]
    m_wsresp = AsyncMock()
    m_wsresp._lock = AsyncMock()
    m_wsresp._response._session.get.return_value = m_resp
    m_send_str = AsyncMock().send_str()

    await asyncio.wait_for(
        pybotters.ws.RequestLimit.gmocoin(m_wsresp, m_send_str), timeout=5.0
    )

    assert m_wsresp._response._session.get.call_count == 3
    assert m_resp.json.call_count == 3
    assert m_sleep.call_count == 2


@pytest.mark.asyncio
async def test_ratelimit_binance(mocker: pytest_mock.MockerFixture):
    m_sleep = mocker.patch("asyncio.sleep")

    m_resp = AsyncMock()
    m_resp.json.side_effect = [
        {"serverTime": 1705545344000},
        {"serverTime": 1705545344200},
        {"serverTime": 1705545344400},
        AssertionError(),
    ]
    m_wsresp = AsyncMock()
    m_wsresp._lock = AsyncMock()
    m_wsresp._response._session.get.return_value = m_resp
    m_send_str = AsyncMock().send_str()

    await asyncio.wait_for(
        pybotters.ws.RequestLimit.binance(m_wsresp, m_send_str), timeout=5.0
    )

    assert m_wsresp._response._session.get.call_count == 3
    assert m_resp.json.call_count == 3
    assert m_sleep.call_count == 2


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        # session.logon, testnet
        (
            {
                "url": URL("wss://testnet.binance.vision/ws-api/v3"),
                "data": {
                    "method": "session.logon",
                },
            },
            {
                "data": {
                    "method": "session.logon",
                    "params": {
                        "apiKey": "9qm1u2s4GoHt9ryIm1D2fHV8",
                        "signature": "b8e612f5ae4bfe8ca85fd6e6f0305dc17bed58b05ae26e33f73b4690b9daa490",  # noqa: E501
                        "timestamp": 2085848896000,
                    },
                }
            },
        ),
        # session.logon, mainnet,
        (
            {
                "url": URL("wss://ws-api.binance.com:443/ws-api/v3"),
                "data": {
                    "method": "session.logon",
                },
            },
            {
                "data": {
                    "method": "session.logon",
                    "params": {
                        "apiKey": "9qm1u2s4GoHt9ryIm1D2fHV8",
                        "signature": "b8e612f5ae4bfe8ca85fd6e6f0305dc17bed58b05ae26e33f73b4690b9daa490",  # noqa: E501
                        "timestamp": 2085848896000,
                    },
                }
            },
        ),
        # order.place
        (
            {
                "url": URL("wss://ws-api.binance.com:443/ws-api/v3"),
                "data": {
                    "method": "order.place",
                    "params": {
                        "symbol": "BTCUSDT",
                        "side": "SELL",
                        "type": "LIMIT",
                        "timeInForce": "GTC",
                        "price": "23416.10000000",
                        "quantity": "0.00847000",
                    },
                },
            },
            {
                "data": {
                    "method": "order.place",
                    "params": {
                        "symbol": "BTCUSDT",
                        "side": "SELL",
                        "type": "LIMIT",
                        "timeInForce": "GTC",
                        "price": "23416.10000000",
                        "quantity": "0.00847000",
                        "apiKey": "9qm1u2s4GoHt9ryIm1D2fHV8",
                        "signature": "c119b5309bb35cf7a72d34812dbcd3895f4ce9bdda06001b7bb3a50a43fc74d6",  # noqa: E501
                        "timestamp": 2085848896000,
                    },
                },
            },
        ),
    ],
)
def test_msgsign_binance(mocker: pytest_mock.MockerFixture, test_input, expected):
    mocker.patch("time.time", return_value=2085848896.0)

    m_wsresp = AsyncMock()
    m_wsresp._response._session.__dict__["_apis"] = {
        "binance": (
            "9qm1u2s4GoHt9ryIm1D2fHV8",
            b"7pDOQJ49zyyDjrNGAvB31RcnAada8nkxkl2IWKop6b0E3tXh",
        ),
        "binancespot_testnet": (
            "9qm1u2s4GoHt9ryIm1D2fHV8",
            b"7pDOQJ49zyyDjrNGAvB31RcnAada8nkxkl2IWKop6b0E3tXh",
        ),
    }
    m_wsresp._response.url = test_input["url"]

    pybotters.ws.MessageSign.binance(m_wsresp, test_input["data"])

    assert test_input["data"] == expected["data"]
