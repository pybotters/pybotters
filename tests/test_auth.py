import random

import pytest
import pytest_mock
from yarl import URL

import pybotters.auth


@pytest.fixture
def mock_session(mocker: pytest_mock.MockerFixture):
    m_sess = mocker.MagicMock()
    keys = {item.name for item in pybotters.auth.Hosts.items.values()}
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    m_sess.__dict__['_apis'] = {k: (
        ''.join([random.choice(chars) for i in range(6)]),
        ''.join([random.choice(chars) for i in range(12)]).encode(),
    ) for k in keys}
    return m_sess


def test_hosts():
    assert hasattr(pybotters.auth.Hosts, 'items')
    assert isinstance(pybotters.auth.Hosts.items, dict)


def test_item():
    name = 'example'
    def func(*args, **kwargs):
        return args
    item = pybotters.auth.Item(name, func)
    assert item.name == name
    assert item.func == func


def test_bybit(mock_session):
    args = (
        'GET',
        URL('https://api.bybit.com/v2/order/list').with_query({'foo': 'bar'}),
    )
    kwargs = {
        'data': None,
        'headers': None,
        'session': mock_session,
    }
    ret = pybotters.auth.Auth.bybit(args, kwargs)
