import asyncio
import functools
from unittest.mock import AsyncMock, MagicMock, call

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
        backoff=WebSocketApp.DEFAULT_BACKOFF,
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


def test_wsresponse_without_heartbeat(mocker: pytest_mock.MockerFixture):
    items = {
        "example.com": lambda ws: ...,
    }
    m_create_task = mocker.patch("asyncio.create_task")
    mocker.patch.object(pybotters.ws.HeartbeatHosts, "items", items)
    m_response = MagicMock()
    m_response.url = URL("ws://not-example.com")
    m_response.__dict__["_auth"] = None
    pybotters.ws.ClientWebSocketResponse(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        m_response,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    assert not m_create_task.called


def test_wsresponse_with_heartbeat(mocker: pytest_mock.MockerFixture):
    items = {
        "example.com": lambda ws: ...,
    }
    m_create_task = mocker.patch("asyncio.create_task")
    mocker.patch.object(pybotters.ws.HeartbeatHosts, "items", items)
    m_response = MagicMock()
    m_response.url = URL("ws://example.com")
    m_response.__dict__["_auth"] = None
    pybotters.ws.ClientWebSocketResponse(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        m_response,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    assert m_create_task.called


def test_authhosts():
    assert hasattr(pybotters.ws.AuthHosts, "items")
    assert isinstance(pybotters.ws.AuthHosts.items, dict)
    for host, item in pybotters.ws.AuthHosts.items.items():
        assert isinstance(host, str)
        assert isinstance(item, pybotters.ws.Item)
        assert isinstance(item.name, str)
        assert callable(item.func)


def test_wsresponse_without_auth(mocker: pytest_mock.MockerFixture):
    items = {
        "example.com": pybotters.ws.Item("example", lambda ws: ...),
    }
    m_create_task = mocker.patch("asyncio.create_task")
    mocker.patch.object(pybotters.ws.AuthHosts, "items", items)
    m_response = MagicMock()
    m_response.url = URL("ws://example.com")
    m_response.__dict__["_auth"] = None
    m_session = MagicMock()
    m_session.__dict__["_apis"] = {}
    m_response._session = m_session
    pybotters.ws.ClientWebSocketResponse(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        m_response,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    assert not m_create_task.called


def test_wsresponse_with_auth(mocker: pytest_mock.MockerFixture):
    items = {
        "example.com": pybotters.ws.Item("example", lambda ws: ...),
    }
    m_create_task = mocker.patch("asyncio.create_task")
    mocker.patch.object(pybotters.ws.AuthHosts, "items", items)
    m_response = MagicMock()
    m_response.url = URL("ws://example.com")
    m_response.__dict__["_auth"] = pybotters.auth.Auth
    m_session = MagicMock()
    m_session.__dict__["_apis"] = {"example": ("key", "secret".encode())}
    m_response._session = m_session
    pybotters.ws.ClientWebSocketResponse(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        m_response,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    assert m_create_task.called


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
async def test_bybit_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)

    async def dummy_send(msg, **kwargs):
        expected = {
            "op": "auth",
            "args": [
                "77SQfUG7X33JhYZ3Jswpx5To",
                2085848901000,
                "a8bcd91ad5f8efdaefaf4ca6f38e551d739d6b42c2b54c85667fb181ecbc29a4",
            ],
        }
        assert msg == expected

    ws = MagicMock()
    ws._response.url.host = "stream.bybit.com"
    ws._response.url.path = "/v5/private"
    ws._response._session.__dict__["_apis"] = {
        "bybit": (
            "77SQfUG7X33JhYZ3Jswpx5To",
            b"PrYiNnCnP76YzpTLvRtV9O1RBa5ecOXqrOTyXuTADCEXYoEX",
        ),
    }
    ws.send_json.side_effect = dummy_send
    await pybotters.ws.Auth.bybit(ws)


@pytest.mark.asyncio
async def test_bitflyer_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    mocker.patch(
        "pybotters.ws.token_hex", return_value="d73b41172d6deca2285e8e58533db082"
    )

    async def dummy_send(msg, **kwargs):
        expected = {
            "method": "auth",
            "params": {
                "api_key": "Pcm1rbtSRqKxTvirZDDOct1k",
                "timestamp": 2085848896000,
                "nonce": "d73b41172d6deca2285e8e58533db082",
                "signature": (
                    "f47526dec80c4773815fb1121058c2e3bcc531d1224b683e8babf76e52b0ba9c"
                ),
            },
            "id": "auth",
        }
        assert msg == expected

    async def dummy_generator():
        yield

    ws = MagicMock()
    ws._response.url.host = "ws.lightstream.bitflyer.com"
    ws._response._session.__dict__["_apis"] = {
        "bitflyer": (
            "Pcm1rbtSRqKxTvirZDDOct1k",
            b"AKHZlv3PoAXZ0KXIKIVKOmS4ji3rV7ZIVIJRstwyplaw0FQ4",
        ),
    }
    ws.send_json.side_effect = dummy_send
    # ws.__aiter__.side_effect = dummy_generator
    await pybotters.ws.Auth.bitflyer(ws)


@pytest.mark.asyncio
async def test_phemex_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)

    async def dummy_send(msg, **kwargs):
        expected = {
            "method": "user.auth",
            "params": [
                "API",
                "9kYxQXZ6PrR8h17lsVdDcpnJ",
                "196f317edfa0662ec3d388099683b40a25607919ca3546b131108b9ee5cbed4a",
                2085848956,
            ],
            "id": 123,
        }
        assert msg == expected

    async def dummy_generator():
        yield

    ws = MagicMock()
    ws._response.url.host = "phemex.com"
    ws._response._session.__dict__["_apis"] = {
        "phemex": (
            "9kYxQXZ6PrR8h17lsVdDcpnJ",
            b"ZBAUiPBTQOjYgTihYnZMw2HFkTooufRnNY5iuahBPMspRYQJ",
        ),
    }
    ws.send_json.side_effect = dummy_send
    # ws.__aiter__.side_effect = dummy_generator
    await pybotters.ws.Auth.phemex(ws)


@pytest.mark.asyncio
async def test_okx_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)

    async def dummy_send(msg, **kwargs):
        expected = {
            "op": "login",
            "args": [
                {
                    "apiKey": "gYmX9fr0kqqxptUlDKESxetg",
                    "passphrase": "MyPassphrase123",
                    "timestamp": "2085848896",
                    "sign": "6QVd7Mgd70We2/oDJr0+KnqxXZ+Gf1zIIl3qJk/Pqx8=",
                }
            ],
        }
        assert msg == expected

    ws = MagicMock()
    ws._response.url.host = "ws.okx.com"
    ws._response.url.path = "/ws/v5/private"
    ws._response._session.__dict__["_apis"] = {
        "okx": (
            "gYmX9fr0kqqxptUlDKESxetg",
            b"YUJHBdFNrbz7atmV3f261ZhdRffTo4S9KZKC7C7qdqcHbRR4",
            "MyPassphrase123",
        ),
    }
    ws.send_json.side_effect = dummy_send
    await pybotters.ws.Auth.okx(ws)


@pytest.mark.asyncio
async def test_bitget_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)

    async def dummy_send(msg, **kwargs):
        expected = {
            "op": "login",
            "args": [
                {
                    "api_key": "jbcfbye8AJzXxXwMKluXM12t",
                    "passphrase": "MyPassphrase123",
                    "timestamp": "2085848896",
                    "sign": "RmRhCixsMce8H7j2uyvR6sk11tCRbYenohbd87nchH8=",
                }
            ],
        }
        assert msg == expected

    ws = MagicMock()
    ws._response.url.host = "ws.bitget.com"
    ws._response._session.__dict__["_apis"] = {
        "bitget": (
            "jbcfbye8AJzXxXwMKluXM12t",
            b"mVd40qhnarPtxk3aqg0FCyY1qlTgBOKOXEcmMYfkerGUKmvr",
            "MyPassphrase123",
        ),
    }
    ws.send_json.side_effect = dummy_send

    await pybotters.ws.Auth.bitget(ws)
