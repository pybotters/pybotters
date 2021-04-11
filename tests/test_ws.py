from unittest.mock import MagicMock

import pytest
import pytest_mock
from yarl import URL

import pybotters.ws


def test_heartbeathosts():
    assert hasattr(pybotters.ws.HeartbeatHosts, 'items')
    assert isinstance(pybotters.ws.HeartbeatHosts.items, dict)
    for host, func in pybotters.ws.HeartbeatHosts.items.items():
        assert isinstance(host, str)
        assert callable(func)


def test_wsresponse_without_heartbeat(mocker: pytest_mock.MockerFixture):
    items = {
        'example.com': lambda ws: ...,
    }
    m_create_task = mocker.patch('asyncio.create_task')
    mocker.patch.object(pybotters.ws.HeartbeatHosts, 'items', items)
    m_response = MagicMock()
    m_response.url = URL('ws://not-example.com')
    ws = pybotters.ws.ClientWebSocketResponse(
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
        'example.com': lambda ws: ...,
    }
    m_create_task = mocker.patch('asyncio.create_task')
    mocker.patch.object(pybotters.ws.HeartbeatHosts, 'items', items)
    m_response = MagicMock()
    m_response.url = URL('ws://example.com')
    ws = pybotters.ws.ClientWebSocketResponse(
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
    assert hasattr(pybotters.ws.AuthHosts, 'items')
    assert isinstance(pybotters.ws.AuthHosts.items, dict)
    for host, item in pybotters.ws.AuthHosts.items.items():
        assert isinstance(host, str)
        assert isinstance(item, pybotters.ws.Item)
        assert isinstance(item.name, str)
        assert callable(item.func)


def test_wsresponse_without_auth(mocker: pytest_mock.MockerFixture):
    items = {
        'example.com': pybotters.ws.Item('example', lambda ws: ...),
    }
    m_create_task = mocker.patch('asyncio.create_task')
    mocker.patch.object(pybotters.ws.AuthHosts, 'items', items)
    m_response = MagicMock()
    m_response.url = URL('ws://example.com')
    m_session = MagicMock()
    m_session.__dict__['_apis'] = {}
    m_response._session = m_session
    ws = pybotters.ws.ClientWebSocketResponse(
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
        'example.com': pybotters.ws.Item('example', lambda ws: ...),
    }
    m_create_task = mocker.patch('asyncio.create_task')
    mocker.patch.object(pybotters.ws.AuthHosts, 'items', items)
    m_response = MagicMock()
    m_response.url = URL('ws://example.com')
    m_session = MagicMock()
    m_session.__dict__['_apis'] = {'example': ('key', 'secret'.encode())}
    m_response._session = m_session
    ws = pybotters.ws.ClientWebSocketResponse(
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
async def test_bitflyer_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    mocker.patch('pybotters.ws.token_hex', return_value='d73b41172d6deca2285e8e58533db082')
    async def dummy_send(msg):
        expected = {
            'method': 'auth',
            'params': {
                'api_key': 'Pcm1rbtSRqKxTvirZDDOct1k',
                'timestamp': 2085848896,
                'nonce': 'd73b41172d6deca2285e8e58533db082',
                'signature': '62781062bd2edd3ece50fa5adca3987869f7446ab7af0f47c9679d76a6cbeb73',
            },
            'id': 'auth',
        }
        assert msg == expected
    async def dummy_generator():
        yield
    ws = MagicMock()
    ws._response.url.host = 'ws.lightstream.bitflyer.com'
    ws._response._session.__dict__['_apis'] = {
        'bitflyer': ('Pcm1rbtSRqKxTvirZDDOct1k', b'AKHZlv3PoAXZ0KXIKIVKOmS4ji3rV7ZIVIJRstwyplaw0FQ4'),
    }
    ws.send_json.side_effect = dummy_send
    # ws.__aiter__.side_effect = dummy_generator
    # TODO: Test __aiter__ code, Currently MagicMock does not have __aiter__
    with pytest.raises(TypeError):
        await pybotters.ws.Auth.bitflyer(ws)


@pytest.mark.asyncio
async def test_liquid_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    async def dummy_send(msg):
        expected = {
            'event': 'quoine:auth_request',
            'data': {
                'path': '/realtime',
                'headers': {
                    'X-Quoine-Auth': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiL3JlYWx0aW1lIiwibm9uY2UiOiIyMDg1ODQ4ODk2MDAwIiwidG9rZW5faWQiOiI1RGp6Z21RWFJrc1FOREJRNUcxck5JdjcifQ.9BS3xGAJW_Ggr_0LzfH1TNf8LjFeXl95yGvn9A7sKm4'
                },
            },
        }
        assert msg == expected
    ws = MagicMock()
    ws._response.url.host = 'tap.liquid.com'
    ws._response._session.__dict__['_apis'] = {
        'liquid': ('5DjzgmQXRksQNDBQ5G1rNIv7', b'WXlZDDzyjWtz1bd7MsGoXPMEohkdUuB95HHgBbKwKBaCyDrp'),
    }
    ws.send_json.side_effect = dummy_send
    await pybotters.ws.Auth.liquid(ws)


@pytest.mark.asyncio
async def test_ftx_ws(mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    async def dummy_send(msg):
        expected = {
            'op': 'login',
            'args': {
                'key': 'J6vXtiZunV4lsRWoLHNYNiCa', 'sign': 'b810f0085a627ea8cad1b2923d63ee05916166a464ab4f89e366abfc7f76a8ac', 'time': 2085848896000
            },
        }
        assert msg == expected
    ws = MagicMock()
    ws._response.url.host = 'ftx.com'
    ws._response._session.__dict__['_apis'] = {
        'ftx': ('J6vXtiZunV4lsRWoLHNYNiCa', b'8ORbaZIrTNcV6Lw48x12RrEzuT0YqbCiluml7LITzG2ud2Nf'),
    }
    ws.send_json.side_effect = dummy_send
    await pybotters.ws.Auth.ftx(ws)
