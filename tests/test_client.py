from unittest.mock import mock_open

import aiohttp
import pybotters
import pytest
import pytest_mock
from asyncmock import AsyncMock


async def test_client():
    apis = {
        "name1": ["key1", "secret1"],
        "name2": ["key2", "secret2"],
        "name3": ["key3", "secret3"],
    }
    base_url = "http://example.com"
    async with pybotters.Client(apis=apis, base_url=base_url) as client:
        assert isinstance(client._session, aiohttp.ClientSession)
        assert not client._session.closed
    assert client._base_url == base_url
    assert client._session.closed
    assert client._session.__dict__["_apis"] == {
        "name1": tuple(["key1", "secret1".encode()]),
        "name2": tuple(["key2", "secret2".encode()]),
        "name3": tuple(["key3", "secret3".encode()]),
    }
    assert [tuple(x) for x in apis.values()] != [
        x for x in client._session.__dict__["_apis"].values()
    ]


async def test_client_warn(mocker: pytest_mock.MockerFixture):
    apis = {"name1", "key1", "secret1"}
    base_url = "http://example.com"
    async with pybotters.Client(apis=apis, base_url=base_url) as client:  # type: ignore
        assert isinstance(client._session, aiohttp.ClientSession)
        assert not client._session.closed
    assert client._base_url == base_url
    assert client._session.closed
    assert client._session.__dict__["_apis"] == {}


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
    assert pybotters.Client._load_apis(["foo", "bar"]) == {}


@pytest.mark.asyncio
async def test_client_request_get(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch("aiohttp.client.ClientSession._request")
    async with pybotters.Client() as client:
        ret = client.request("GET", "http://example.com", params={"foo": "bar"})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_request_post(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch("aiohttp.client.ClientSession._request")
    async with pybotters.Client() as client:
        ret = client.request("POST", "http://example.com", data={"foo": "bar"})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_get(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch("aiohttp.client.ClientSession._request")
    async with pybotters.Client() as client:
        ret = client.get("http://example.com", params={"foo": "bar"})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_post(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch("aiohttp.client.ClientSession._request")
    async with pybotters.Client() as client:
        ret = client.post("http://example.com", data={"foo": "bar"})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_put(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch("aiohttp.client.ClientSession._request")
    async with pybotters.Client() as client:
        ret = client.put("http://example.com", data={"foo": "bar"})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_delete(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch("aiohttp.client.ClientSession._request")
    async with pybotters.Client() as client:
        ret = client.delete("http://example.com", data={"foo": "bar"})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_ws_connect(mocker: pytest_mock.MockerFixture):
    runner_mock = mocker.Mock()
    runner_mock.wait = AsyncMock()
    m = mocker.patch("pybotters.client.WebSocketRunner", return_value=runner_mock)
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
        )
    assert m.called
    assert m.call_args == [
        ("ws://test.org", client._session),
        {
            "send_str": '{"foo":"bar"}',
            "send_bytes": b'{"foo":"bar"}',
            "send_json": {"foo": "bar"},
            "hdlr_str": hdlr_str,
            "hdlr_bytes": hdlr_bytes,
            "hdlr_json": hdlr_json,
        },
    ]
    assert ret == runner_mock
