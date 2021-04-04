from unittest.mock import MagicMock

import pytest_mock
from yarl import URL

import pybotters.ws


def test_hosts():
    assert hasattr(pybotters.ws.Hosts, 'items')
    assert isinstance(pybotters.ws.Hosts.items, dict)
    for host, func in pybotters.ws.Hosts.items.items():
        assert isinstance(host, str)
        assert callable(func)


def test_wsresponse_without_auth(mocker: pytest_mock.MockerFixture):
    items = {
        'example.com': lambda ws: ...,
    }
    m_create_task = mocker.patch('asyncio.create_task')
    mocker.patch.object(pybotters.ws.Hosts, 'items', items)
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


def test_wsresponse_with_auth(mocker: pytest_mock.MockerFixture):
    items = {
        'example.com': lambda ws: ...,
    }
    m_create_task = mocker.patch('asyncio.create_task')
    mocker.patch.object(pybotters.ws.Hosts, 'items', items)
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
