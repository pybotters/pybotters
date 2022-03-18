import json
from unittest.mock import mock_open

import aiohttp
import pybotters
import pytest
import pytest_mock
from asyncmock import AsyncMock


async def test_client():
    apis = {
        'name1': ['key1', 'secret1'],
        'name2': ['key2', 'secret2'],
        'name3': ['key3', 'secret3'],
    }
    base_url = 'http://example.com'
    async with pybotters.Client(apis=apis, base_url=base_url) as client:
        assert isinstance(client._session, aiohttp.ClientSession)
        assert not client._session.closed
    assert client._base_url == base_url
    assert client._session.closed
    assert client._session.__dict__['_apis'] == {
        'name1': tuple(['key1', 'secret1'.encode()]),
        'name2': tuple(['key2', 'secret2'.encode()]),
        'name3': tuple(['key3', 'secret3'.encode()]),
    }


async def test_client_open(mocker: pytest_mock.MockerFixture):
    read_data = (
        '{"name1":["key1","secret1"],"name2":["key2","secret2"],"name3":["key3","secret'
        '3"]}'
    )
    m = mocker.patch('pybotters.client.open', mock_open(read_data=read_data))
    apis = '/path/to/apis.json'
    async with pybotters.Client(apis=apis) as client:
        assert isinstance(client._session, aiohttp.ClientSession)
        assert not client._session.closed
    assert client._session.closed
    assert client._session.__dict__['_apis'] == {
        'name1': tuple(['key1', 'secret1'.encode()]),
        'name2': tuple(['key2', 'secret2'.encode()]),
        'name3': tuple(['key3', 'secret3'.encode()]),
    }
    m.assert_called_once_with(apis)


async def test_client_warn(mocker: pytest_mock.MockerFixture):
    apis = {'name1', 'key1', 'secret1'}
    base_url = 'http://example.com'
    async with pybotters.Client(apis=apis, base_url=base_url) as client:  # type: ignore
        assert isinstance(client._session, aiohttp.ClientSession)
        assert not client._session.closed
    assert client._base_url == base_url
    assert client._session.closed
    assert client._session.__dict__['_apis'] == {}


async def test_client_open_error(mocker: pytest_mock.MockerFixture):
    read_data = r'name1:\- key1\n- secret1'
    mocker.patch('pybotters.client.open', mock_open(read_data=read_data))
    apis = '/path/to/apis.json'
    with pytest.raises(json.JSONDecodeError):
        async with pybotters.Client(apis=apis):
            pass


@pytest.mark.asyncio
async def test_client_request_get(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.request('GET', 'http://example.com', params={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_request_post(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.request('POST', 'http://example.com', data={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_get(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.get('http://example.com', params={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_post(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.post('http://example.com', data={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_put(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.put('http://example.com', data={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_delete(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.delete('http://example.com', data={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


@pytest.mark.asyncio
async def test_client_ws_connect(mocker: pytest_mock.MockerFixture):
    runner_mock = mocker.Mock()
    runner_mock.wait = AsyncMock()
    m = mocker.patch('pybotters.client.WebSocketRunner', return_value=runner_mock)
    hdlr_str = mocker.Mock()
    hdlr_bytes = mocker.Mock()
    hdlr_json = mocker.Mock()
    async with pybotters.Client() as client:
        ret = await client.ws_connect(
            'ws://test.org',
            send_str='{"foo":"bar"}',
            send_bytes=b'{"foo":"bar"}',
            send_json={'foo': 'bar'},
            hdlr_str=hdlr_str,
            hdlr_bytes=hdlr_bytes,
            hdlr_json=hdlr_json,
        )
    assert m.called
    assert m.call_args == [
        ('ws://test.org', client._session),
        {
            'send_str': '{"foo":"bar"}',
            'send_bytes': b'{"foo":"bar"}',
            'send_json': {'foo': 'bar'},
            'hdlr_str': hdlr_str,
            'hdlr_bytes': hdlr_bytes,
            'hdlr_json': hdlr_json,
        },
    ]
    assert ret == runner_mock
