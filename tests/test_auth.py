import random

import aiohttp.formdata
import pytest
import pytest_mock
from multidict import CIMultiDict
from yarl import URL

import pybotters.auth


def util_api_generater():
    """
    $ python
    >>> from tests.test_auth import util_api_generater
    >>> print(util_api_generater())
    """
    keys = {item.name for item in pybotters.auth.Hosts.items.values()}
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    print(chars)
    return {k: (
        ''.join([random.choice(chars) for i in range(24)]),
        ''.join([random.choice(chars) for i in range(48)]).encode(),
    ) for k in keys}


@pytest.fixture
def mock_session(mocker: pytest_mock.MockerFixture):
    m_sess = mocker.MagicMock()
    apis = {
        'bybit': ('77SQfUG7X33JhYZ3Jswpx5To', b'PrYiNnCnP76YzpTLvRtV9O1RBa5ecOXqrOTyXuTADCEXYoEX'),
        'bybit_testnet': ('vDGsldGGevgVkG3ATH1PzBYd', b'fVp9Y9iZbkCb4JXyprq2ZbbDXupWz5V3H06REf2eJ53DyQju'),
        'btcmex': ('fSvgi9a85yDFx3efr94tmJpH', b'1GGUedysKk2s2rMMWRmMe7uAp1mKAbORgR3rUSMe15I70P1A'),
        'binance': ('9qm1u2s4GoHt9ryIm1D2fHV8', b'7pDOQJ49zyyDjrNGAvB31RcnAada8nkxkl2IWKop6b0E3tXh'),
        'binance_testnet': ('EDYH5JVoHJlhroiQkDntBHn8', b'lMFc3hibQUEOzSeG6YEvx7lMRgNBUlF07PVEm9g9U6HEWtEZ'),
    }
    assert set(apis.keys()) == set(item.name for item in pybotters.auth.Hosts.items.values())
    m_sess.__dict__['_apis'] = apis
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


def test_bybit_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'GET',
        URL('https://api.bybit.com/v2/private/order/list').with_query({
            'symbol': 'BTCUSD',
            'cursor': 'w01XFyyZc8lhtCLl6NgAaYBRfsN9Qtpp1f2AUy3AS4+fFDzNSlVKa0od8DKCqgAn',
        }),
    )
    kwargs = {
        'data': None,
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('https://api.bybit.com/v2/private/order/list?symbol=BTCUSD&cursor=w01XFyyZc8lhtCLl6NgAaYBRfsN9Qtpp1f2AUy3AS4%2BfFDzNSlVKa0od8DKCqgAn&api_key=77SQfUG7X33JhYZ3Jswpx5To&timestamp=2085848895000&sign=885c1dcbbcb5a0edb5f6298e0aa40e23b7c6bc7f1acab600739962cfd7e7c0ac')
    )
    expected_kwargs = {
        'data': None,
        'session': mock_session,
    }
    args = pybotters.auth.Auth.bybit(args, kwargs)
    assert args == expected_args
    assert kwargs['data'] == expected_kwargs['data']


def test_bybit_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'POST',
        URL('https://api.bybit.com/v2/private/order/create'),
    )
    kwargs = {
        'data': {
            'symbol': 'BTCUSD',
            'side': 'Buy',
            'order_type': 'Market',
            'qty': 100,
            'time_in_force': 'GoodTillCancel',
        },
        'session': mock_session,
    }
    expected_args = (
        'POST',
        URL('https://api.bybit.com/v2/private/order/create')
    )
    expected_kwargs = {
        'data': aiohttp.formdata.FormData({
            'api_key': '77SQfUG7X33JhYZ3Jswpx5To',
            'order_type': 'Market',
            'qty': '100',
            'side': 'Buy',
            'symbol': 'BTCUSD',
            'time_in_force': 'GoodTillCancel',
            'timestamp': '2085848895000',
            'sign': 'c377e178195d2e4b9316cf085e21e2881cc1b413c9a23873ea0c9d57d8e2b685'
        })(),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.bybit(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value


def test_bybit_ws(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'GET',
        URL('wss://stream.bybit.com/realtime'),
    )
    kwargs = {
        'data': None,
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('wss://stream.bybit.com/realtime?api_key=77SQfUG7X33JhYZ3Jswpx5To&expires=2085848897000&signature=ea0eb717f560e0ad7a6104e3e9a6dd6ae8e3cdd96b43f0a449d35aff16e1fdf6'),
    )
    expected_kwargs = {
        'data': None,
        'session': mock_session,
    }
    args = pybotters.auth.Auth.bybit(args, kwargs)
    assert args == expected_args
    assert kwargs['data'] == expected_kwargs['data']


def test_btcmex_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'GET',
        URL('https://www.btcmex.com/api/v1/order').with_query({
            'symbol': 'XBTUSD',
        }),
    )
    kwargs = {
        'data': None,
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('https://www.btcmex.com/api/v1/order?symbol=XBTUSD')
    )
    expected_kwargs = {
        'data': aiohttp.formdata.FormData({})(),
        'headers': CIMultiDict({
            'api-expires': '2085848901',
            'api-key': 'fSvgi9a85yDFx3efr94tmJpH',
            'api-signature': '7547642ac62bdda8349dc38c247c8cf96ea1cb8bbfc317aacf6713d274c36928'
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.btcmex(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_btcmex_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'POST',
        URL('https://www.btcmex.com/api/v1/order'),
    )
    kwargs = {
        'data': {
            'symbol': 'XBTUSD',
            'side': 'Buy',
            'orderQty': 100,
            'ordType': 'Market',
        },
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'POST',
        URL('https://www.btcmex.com/api/v1/order')
    )
    expected_kwargs = {
        'data': aiohttp.formdata.FormData({
            'symbol': 'XBTUSD',
            'side': 'Buy',
            'orderQty': 100,
            'ordType': 'Market',
        })(),
        'headers': CIMultiDict({
            'api-expires': '2085848901',
            'api-key': 'fSvgi9a85yDFx3efr94tmJpH',
            'api-signature': '245198eb7d480a695feeb3c6cc349895578738e9358e508315b6649c05ef2b33'
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.btcmex(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_btcmex_ws(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'GET',
        URL('wss://www.btcmex.com/realtime'),
    )
    kwargs = {
        'data': None,
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('wss://www.btcmex.com/realtime?api_key=fSvgi9a85yDFx3efr94tmJpH&expires=2085848897000&signature=78e31b74c66fba9233d2c99ce7c4635104670b9306a481d9160fd8e4c8d1675b'),
    )
    expected_kwargs = {
        'data': None,
        'session': mock_session,
    }
    args = pybotters.auth.Auth.bybit(args, kwargs)
    assert args == expected_args
    assert kwargs['data'] == expected_kwargs['data']
