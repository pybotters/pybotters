import asyncio
import json
from unittest.mock import mock_open

import aiohttp
import pytest
import pytest_mock

import pybotters


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
    read_data = '{"name1":["key1","secret1"],"name2":["key2","secret2"],"name3":["key3","secret3"]}'
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
    m.assert_called_once_with('/path/to/apis.json', encoding='utf-8')


async def test_client_warn(mocker: pytest_mock.MockerFixture):
    apis = {'name1', 'key1', 'secret1'}
    base_url = 'http://example.com'
    async with pybotters.Client(apis=apis, base_url=base_url) as client:
        assert isinstance(client._session, aiohttp.ClientSession)
        assert not client._session.closed
    assert client._base_url == base_url
    assert client._session.closed
    assert client._session.__dict__['_apis'] == {}

async def test_client_open_error(mocker: pytest_mock.MockerFixture):
    read_data = 'name1:\- key1\n- secret1'
    m = mocker.patch('pybotters.client.open', mock_open(read_data=read_data))
    apis = '/path/to/apis.json'
    with pytest.raises(json.JSONDecodeError):
        async with pybotters.Client(apis=apis) as client:
            pass


async def test_client_request_get(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.request('GET', 'http://example.com', params={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


async def test_client_request_post(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.request('POST', 'http://example.com', data={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


async def test_client_get(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.get('http://example.com', params={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


async def test_client_post(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.post('http://example.com', data={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


async def test_client_put(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.put('http://example.com', data={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


async def test_client_delete(mocker: pytest_mock.MockerFixture):
    patched = mocker.patch('aiohttp.client.ClientSession._request')
    async with pybotters.Client() as client:
        ret = client.delete('http://example.com', data={'foo': 'bar'})
    assert patched.called
    assert isinstance(ret, aiohttp.client._RequestContextManager)


async def test_client_ws_connect_str(mocker: pytest_mock.MockerFixture):
    event = asyncio.Event()
    event.set()
    mocker.patch('asyncio.Event', return_value=event)
    task = mocker.patch('asyncio.create_task')
    coro = mocker.patch('pybotters.client.ws_run_forever')
    async with pybotters.Client() as client:
        ret = await client.ws_connect(
            'ws://test.org',
            send_str='{"foo":"bar"}',
            hdlr_str=lambda msg, ws: ...,
        )
    assert coro.called
    assert task.called
    assert ret == task.return_value


async def test_client_ws_connect_json(mocker: pytest_mock.MockerFixture):
    event = asyncio.Event()
    event.set()
    mocker.patch('asyncio.Event', return_value=event)
    task = mocker.patch('asyncio.create_task')
    coro = mocker.patch('pybotters.client.ws_run_forever')
    async with pybotters.Client() as client:
        ret = await client.ws_connect(
            'ws://test.org',
            send_json={'foo': 'bar'},
            hdlr_json=lambda msg, ws: ...,
        )
    assert coro.called
    assert task.called
    assert ret == task.return_value
