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
async def test_bitflyer(mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    mocker.patch('pybotters.ws.token_hex', return_value='d73b41172d6deca2285e8e58533db082')
    async def dummuy(msg):
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
    ws = MagicMock()
    ws._response.url.host = 'ws.lightstream.bitflyer.com'
    ws._response._session.__dict__['_apis'] = {'bitflyer': ('Pcm1rbtSRqKxTvirZDDOct1k', b'AKHZlv3PoAXZ0KXIKIVKOmS4ji3rV7ZIVIJRstwyplaw0FQ4')}
    ws.send_json.side_effect = dummuy
    await pybotters.ws.Auth.bitflyer(ws)
