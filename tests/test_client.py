import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, mock_open

import aiohttp
import pytest
import pytest_asyncio
import pytest_mock

import pybotters
import pybotters.auth


@pytest.mark.asyncio
async def test_client():
    apis = {
        "name1": ["key1", "secret1"],
        "name2": ["key2", "secret2"],
        "name3": ["key3", "secret3", "passphrase3"],
        "name4": [
            "key4",
        ],
    }
    base_url = "http://example.com"
    async with pybotters.Client(apis=apis, base_url=base_url) as client:
        assert isinstance(client._session, aiohttp.ClientSession)
        assert not client._session.closed
    assert client._base_url == base_url
    assert client._session.closed
    assert client._session.__dict__["_apis"] == {
        "name1": tuple(["key1", "secret1".encode(), ""]),
        "name2": tuple(["key2", "secret2".encode(), ""]),
        "name3": tuple(["key3", "secret3".encode(), "passphrase3"]),
        "name4": tuple(["key4", b"", ""]),
    }
    assert [tuple(x) for x in apis.values()] != [
        x for x in client._session.__dict__["_apis"].values()
    ]
    assert "pybotters" in client._session.headers["User-Agent"].split("/")[0]
    assert client._session.headers["User-Agent"].split("/")[1] == pybotters.__version__


@pytest.mark.asyncio
async def test_client_warn(mocker: pytest_mock.MockerFixture):
    apis = {"name1", "key1", "secret1"}
    base_url = "http://example.com"
    async with pybotters.Client(apis=apis, base_url=base_url) as client:  # type: ignore
        assert isinstance(client._session, aiohttp.ClientSession)
        assert not client._session.closed
    assert client._base_url == base_url
    assert client._session.closed
    assert client._session.__dict__["_apis"] == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_input",
    list(pybotters.auth.PassphraseRequiredExchanges.items),
)
async def test_client_with_missing_passphrase_apis(
    caplog: pytest.LogCaptureFixture, test_input
):
    apis = {test_input: ["key", "secret"]}
    async with pybotters.Client(apis=apis):
        pass

    assert [rec.message for rec in caplog.records] == [
        f"Missing passphrase for {test_input}"
    ]


def test_client_load_apis_current(mocker: pytest_mock.MockerFixture):
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data='{"foo":"bar"}'))
    assert pybotters.Client._load_apis(None) == {"foo": "bar"}


def test_client_load_apis_env(mocker: pytest_mock.MockerFixture):
    mocker.patch("os.path.isfile", side_effect=[False, True])
    mocker.patch("os.getenv", return_value="/path/to/apis.json")
    mocker.patch("builtins.open", mock_open(read_data='{"foo":"bar"}'))
    assert pybotters.Client._load_apis(None) == {"foo": "bar"}


def test_client_load_apis_nothing(mocker: pytest_mock.MockerFixture):
    mocker.patch("os.path.isfile", return_value=False)
    mocker.patch("os.getenv", return_value=None)
    assert pybotters.Client._load_apis(None) == {}


def test_client_load_apis_str_open(mocker: pytest_mock.MockerFixture):
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data='{"foo":"bar"}'))
    assert pybotters.Client._load_apis("/path/to/apis.json") == {"foo": "bar"}


def test_client_load_apis_str_warn(mocker: pytest_mock.MockerFixture):
    mocker.patch("os.path.isfile", return_value=False)
    assert pybotters.Client._load_apis("/path/to/apis.json") == {}


def test_client_load_apis_deepcopy(mocker: pytest_mock.MockerFixture):
    mocker.patch("os.path.isfile", return_value=False)
    apis = {"foo": ["bar", "baz"]}
    actual = pybotters.Client._load_apis(apis)
    assert actual == apis
    apis["foo"].append("qux")
    assert actual != apis


def test_client_load_apis_invalid(mocker: pytest_mock.MockerFixture):
    invalid_apis: Any = ["foo", "bar"]
    assert pybotters.Client._load_apis(invalid_apis) == {}


@pytest_asyncio.fixture
async def pybotters_client():
    async with pybotters.Client() as client:
        yield client


def test_client_request_get(
    mocker: pytest_mock.MockerFixture, pybotters_client: pybotters.Client
):
    patched = mocker.patch("aiohttp.ClientSession._request", new_callable=MagicMock)

    pybotters_client.request("GET", "http://example.com", params={"foo": "bar"})

    assert patched.called
    assert patched.call_args.args == ("GET", "http://example.com")
    assert patched.call_args.kwargs == dict(
        params={"foo": "bar"},
        data=None,
        auth=pybotters.auth.Auth,
    )


def test_client_request_post(
    mocker: pytest_mock.MockerFixture, pybotters_client: pybotters.Client
):
    patched = mocker.patch("aiohttp.ClientSession._request", new_callable=MagicMock)

    pybotters_client.request("POST", "http://example.com", data={"foo": "bar"})

    assert patched.called
    assert patched.call_args.args == ("POST", "http://example.com")
    assert patched.call_args.kwargs == dict(
        params=None,
        data={"foo": "bar"},
        auth=pybotters.auth.Auth,
    )


def test_client_get(
    mocker: pytest_mock.MockerFixture, pybotters_client: pybotters.Client
):
    patched = mocker.patch("aiohttp.ClientSession._request", new_callable=MagicMock)

    pybotters_client.get("http://example.com", params={"foo": "bar"})

    assert patched.called
    assert patched.call_args.args == ("GET", "http://example.com")
    assert patched.call_args.kwargs == dict(
        params={"foo": "bar"},
        data=None,
        auth=pybotters.auth.Auth,
    )


def test_client_post(
    mocker: pytest_mock.MockerFixture, pybotters_client: pybotters.Client
):
    patched = mocker.patch("aiohttp.ClientSession._request", new_callable=MagicMock)

    pybotters_client.post("http://example.com", data={"foo": "bar"})

    assert patched.called
    assert patched.call_args.args == ("POST", "http://example.com")
    assert patched.call_args.kwargs == dict(
        params=None,
        data={"foo": "bar"},
        auth=pybotters.auth.Auth,
    )


def test_client_put(
    mocker: pytest_mock.MockerFixture, pybotters_client: pybotters.Client
):
    patched = mocker.patch("aiohttp.ClientSession._request", new_callable=MagicMock)

    pybotters_client.put("http://example.com", data={"foo": "bar"})

    assert patched.called
    assert patched.call_args.args == ("PUT", "http://example.com")
    assert patched.call_args.kwargs == dict(
        params=None,
        data={"foo": "bar"},
        auth=pybotters.auth.Auth,
    )


def test_client_delete(
    mocker: pytest_mock.MockerFixture, pybotters_client: pybotters.Client
):
    patched = mocker.patch("aiohttp.ClientSession._request", new_callable=MagicMock)

    pybotters_client.delete(
        "http://example.com", params={"foo": "bar"}, data={"baz": "qux"}
    )

    assert patched.called
    assert patched.call_args.args == ("DELETE", "http://example.com")
    assert patched.call_args.kwargs == dict(
        params={"foo": "bar"},
        data={"baz": "qux"},
        auth=pybotters.auth.Auth,
    )


@pytest.mark.asyncio
async def test_client_fetch(mocker: pytest_mock.MockerFixture):
    m_resp = AsyncMock()
    m_resp.text.return_value = '{"foo":"bar"}'
    m_resp.json.return_value = {"foo": "bar"}
    m_actx = AsyncMock()
    m_actx.__aenter__.return_value = m_resp
    m_req = mocker.patch("pybotters.client.Client.request")
    m_req.return_value = m_actx

    async with pybotters.Client() as client:
        r = await client.fetch("GET", "http://example.com", params={"foo": "bar"})

    assert isinstance(r, pybotters.FetchResult)
    assert isinstance(r.response, type(m_resp))
    assert r.text == m_resp.text.return_value
    assert r.data == m_resp.json.return_value
    assert m_req.called


@pytest.mark.asyncio
async def test_client_fetch_error(mocker: pytest_mock.MockerFixture):
    m_resp = AsyncMock()
    m_resp.text.return_value = "pong"
    m_resp.json.side_effect = json.JSONDecodeError(
        msg="Expecting value", doc="pong", pos=0
    )
    m_actx = AsyncMock()
    m_actx.__aenter__.return_value = m_resp
    m_req = mocker.patch("pybotters.client.Client.request")
    m_req.return_value = m_actx

    async with pybotters.Client() as client:
        r = await client.fetch("GET", "http://example.com", params={"foo": "bar"})

    assert isinstance(r, pybotters.FetchResult)
    assert isinstance(r.response, type(m_resp))
    assert r.text == m_resp.text.return_value
    assert isinstance(r.data, pybotters.NotJSONContent)
    assert not r.data
    assert m_req.called


@pytest.mark.asyncio
async def test_client_ws_connect(mocker: pytest_mock.MockerFixture):
    m = mocker.patch("pybotters.client.WebSocketApp", new_callable=AsyncMock)
    hdlr_str = mocker.Mock()
    hdlr_bytes = mocker.Mock()
    hdlr_json = mocker.Mock()
    async with pybotters.Client() as client:
        ret = await client.ws_connect(
            "ws://test.org",
            send_str='{"foo":"bar"}',
            send_bytes=b'{"foo":"bar"}',
            send_json={"foo": "bar"},
            hdlr_str=hdlr_str,
            hdlr_bytes=hdlr_bytes,
            hdlr_json=hdlr_json,
            backoff=(1.92, 60.0, 1.618, 5.0),
            autoping=True,
            heartbeat=42.0,
            auth=None,
        )
    assert m.called
    assert m.call_args == [
        (client._session, "ws://test.org"),
        {
            "send_str": '{"foo":"bar"}',
            "send_bytes": b'{"foo":"bar"}',
            "send_json": {"foo": "bar"},
            "hdlr_str": hdlr_str,
            "hdlr_bytes": hdlr_bytes,
            "hdlr_json": hdlr_json,
            "backoff": (1.92, 60.0, 1.618, 5.0),
            "autoping": True,
            "heartbeat": 42.0,
            "auth": None,
        },
    ]
    assert ret == m.return_value
