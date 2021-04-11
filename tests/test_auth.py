import random

import aiohttp.formdata
import aiohttp.payload
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
        'bitflyer': ('Pcm1rbtSRqKxTvirZDDOct1k', b'AKHZlv3PoAXZ0KXIKIVKOmS4ji3rV7ZIVIJRstwyplaw0FQ4'),
        'gmocoin': ('GnHvwP7d5FbWdZinoI2hKBTR', b'jFRfAL7PiFLvYP6rS9u6TmTjTyVI1z21QXgDqxsCdPkMmN6I'),
        'liquid': ('5DjzgmQXRksQNDBQ5G1rNIv7', b'WXlZDDzyjWtz1bd7MsGoXPMEohkdUuB95HHgBbKwKBaCyDrp'),
        'bitbank': ('l5HGaEzIC3KiMqbYwtAl1r48', b'6lgYlHSYj31SAU67jCtxn6qh60pZTeekd5iRseYZNzrC2kX5'),
        'ftx': ('J6vXtiZunV4lsRWoLHNYNiCa', b'8ORbaZIrTNcV6Lw48x12RrEzuT0YqbCiluml7LITzG2ud2Nf'),
    }
    assert set(apis.keys()) == set(item.name for item in pybotters.auth.Hosts.items.values())
    m_sess.__dict__['_apis'] = apis
    return m_sess


def test_hosts():
    assert hasattr(pybotters.auth.Hosts, 'items')
    assert isinstance(pybotters.auth.Hosts.items, dict)
    for host, item in pybotters.auth.Hosts.items.items():
        assert isinstance(host, str)
        assert isinstance(item.name, str)
        assert callable(item.func)


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
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('wss://www.btcmex.com/realtime'),
    )
    expected_kwargs = {
        'data': aiohttp.formdata.FormData({})(),
        'headers': CIMultiDict({
            'api-expires': '2085848901',
            'api-key': 'fSvgi9a85yDFx3efr94tmJpH',
            'api-signature': '125c388f8af1e5d93146064d8aada1ccf6dc80616a3057e67ca26f5970e393ac',
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.btcmex(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_binance_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'GET',
        URL('https://dapi.binance.com/dapi/v1/order').with_query({
            'symbol': 'BTCUSD_PERP',
        }),
    )
    kwargs = {
        'data': None,
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('https://dapi.binance.com/dapi/v1/order?symbol=BTCUSD_PERP&timestamp=2085848896000&signature=cfd48880dc0ceb003e5f009205a4ebd6415ddeb40addafd1c134528681d98ccf')
    )
    expected_kwargs = {
        'data': None,
        'headers': CIMultiDict({'X-MBX-APIKEY': '9qm1u2s4GoHt9ryIm1D2fHV8'}),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.binance(args, kwargs)
    assert args == expected_args
    assert kwargs['data'] == expected_kwargs['data']
    assert kwargs['headers'] == expected_kwargs['headers']


def test_binance_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'POST',
        URL('https://dapi.binance.com/dapi/v1/order'),
    )
    kwargs = {
        'data': {
            'symbol': 'BTCUSD_PERP',
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': 1,
        },
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'POST',
        URL('https://dapi.binance.com/dapi/v1/order')
    )
    expected_kwargs = {
        'data': aiohttp.formdata.FormData({
            'symbol': 'BTCUSD_PERP',
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': 1,
            'timestamp': '2085848896000',
            'signature': 'ab855d04b87a8043830ca5dfabcded89012c69ed2ddeaaa1fc1dad54a82d1675',
        })(),
        'headers': CIMultiDict({'X-MBX-APIKEY': '9qm1u2s4GoHt9ryIm1D2fHV8'}),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.binance(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_bybit_ws(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'GET',
        URL('wss://dstream.binance.com/ws/pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6a81va65sdf19v8a65a1'),
    )
    kwargs = {
        'data': None,
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('wss://dstream.binance.com/ws/pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6a81va65sdf19v8a65a1'),
    )
    expected_kwargs = {
        'data': None,
        'headers': CIMultiDict({'X-MBX-APIKEY': '9qm1u2s4GoHt9ryIm1D2fHV8'}),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.binance(args, kwargs)
    assert args == expected_args
    assert kwargs['data'] == expected_kwargs['data']
    assert kwargs['headers'] == expected_kwargs['headers']


def test_bitflyer_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'GET',
        URL('https://api.bitflyer.com/v1/me/getchildorders').with_query({
            'product_code': 'FX_BTC_JPY',
            'child_order_state': 'ACTIVE',
        }),
    )
    kwargs = {
        'data': None,
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('https://api.bitflyer.com/v1/me/getchildorders?product_code=FX_BTC_JPY&child_order_state=ACTIVE')
    )
    expected_kwargs = {
        'data': aiohttp.formdata.FormData({})(),
        'headers': CIMultiDict({
            'ACCESS-KEY': 'Pcm1rbtSRqKxTvirZDDOct1k',
            'ACCESS-TIMESTAMP': '2085848896',
            'ACCESS-SIGN': 'd264cf935540b434b7073e0341d0d43dc1450c4c1cbcc47024931486dbd5a785'
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.bitflyer(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_bitflyer_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'POST',
        URL('https://api.bitflyer.com/v1/me/sendchildorder'),
    )
    kwargs = {
        'data': {
            'product_code': 'FX_BTC_JPY',
            'child_order_type': 'MARKET',
            'side': 'BUY',
            'size': 0.01,
        },
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'POST',
        URL('https://api.bitflyer.com/v1/me/sendchildorder')
    )
    expected_kwargs = {
        'data': aiohttp.formdata.FormData({
            'product_code': 'FX_BTC_JPY',
            'child_order_type': 'MARKET',
            'side': 'BUY',
            'size': 0.01,
        })(),
        'headers': CIMultiDict({
            'ACCESS-KEY': 'Pcm1rbtSRqKxTvirZDDOct1k',
            'ACCESS-TIMESTAMP': '2085848896',
            'ACCESS-SIGN': '6f7f1d1e348788362015d5b283fc97649a0f9173dc85fe7ba4668f4ab1a1f9a8'
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.bitflyer(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_gmocoin_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'GET',
        URL('https://api.coin.z.com/private/v1/activeOrders').with_query({
            'symbol': 'BTC_JPY',
            'page': 1,
            'count': 100,
        }),
    )
    kwargs = {
        'data': None,
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('https://api.coin.z.com/private/v1/activeOrders?symbol=BTC_JPY&page=1&count=100')
    )
    expected_kwargs = {
        'data': aiohttp.formdata.FormData({})(),
        'headers': CIMultiDict({
            'API-KEY': 'GnHvwP7d5FbWdZinoI2hKBTR',
            'API-TIMESTAMP': '2085848896000',
            'API-SIGN': 'e6f0c55c381b08f0892daad0c5e27f69050dab787d98e45680802e340849978a'
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.gmocoin(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_gmocoin_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'POST',
        URL('https://api.coin.z.com/private/v1/order'),
    )
    kwargs = {
        'data': {
            'symbol': 'BTC_JPY',
            'side': 'BUY',
            'executionType': 'MARKET',
            'size': 0.01,
        },
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'POST',
        URL('https://api.coin.z.com/private/v1/order')
    )
    expected_kwargs = {
        'data': aiohttp.payload.JsonPayload({
            'symbol': 'BTC_JPY',
            'side': 'BUY',
            'executionType': 'MARKET',
            'size': 0.01,
        }),
        'headers': CIMultiDict({
            'API-KEY': 'GnHvwP7d5FbWdZinoI2hKBTR',
            'API-TIMESTAMP': '2085848896000',
            'API-SIGN': 'b6e96f0fe71993d29b50dc8a9a0bebe974fb38749e2ee7aed1e4abb845b063bf'
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.gmocoin(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_liquid_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'GET',
        URL('https://api.liquid.com/orders').with_query({
            'id': 5,
        }),
    )
    kwargs = {
        'data': None,
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('https://api.liquid.com/orders?id=5')
    )
    expected_kwargs = {
        'data': aiohttp.formdata.FormData({})(),
        'headers': CIMultiDict({
            'X-Quoine-API-Version': '2',
            'X-Quoine-Auth': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiL29yZGVycz9pZD01Iiwibm9uY2UiOiIyMDg1ODQ4ODk2MDAwIiwidG9rZW5faWQiOiI1RGp6Z21RWFJrc1FOREJRNUcxck5JdjcifQ.Q8jvnnFafWJ_piQyB1GyEc1nxfil0uwnyjMvNV2icgA',
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.liquid(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_liquid_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'POST',
        URL('https://api.liquid.com/orders'),
    )
    kwargs = {
        'data': {
            'quantity': 0.01,
            'order_type': 'market',
            'product_id': 5,
            'side': 'buy',
        },
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'POST',
        URL('https://api.liquid.com/orders')
    )
    expected_kwargs = {
        'data': aiohttp.payload.JsonPayload({
            'quantity': 0.01,
            'order_type': 'market',
            'product_id': 5,
            'side': 'buy',
        }),
        'headers': CIMultiDict({
            'X-Quoine-API-Version': '2',
            'X-Quoine-Auth': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiL29yZGVycyIsIm5vbmNlIjoiMjA4NTg0ODg5NjAwMCIsInRva2VuX2lkIjoiNURqemdtUVhSa3NRTkRCUTVHMXJOSXY3In0.vS_l9BAKGTrROl2uVFlEP1SA4FaI9TL4JuRpLCyilG0',
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.liquid(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_bitbank_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'GET',
        URL('https://api.bitbank.cc/v1/user/spot/order').with_query({
            'pair': 'btc_jpy',
        }),
    )
    kwargs = {
        'data': None,
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('https://api.bitbank.cc/v1/user/spot/order?pair=btc_jpy')
    )
    expected_kwargs = {
        'data': aiohttp.formdata.FormData({})(),
        'headers': CIMultiDict({
            'ACCESS-KEY': 'l5HGaEzIC3KiMqbYwtAl1r48',
            'ACCESS-NONCE': '2085848896',
            'ACCESS-SIGNATURE': 'ad1de787eef27d0d3f594c33b13c6df90bef4926466d77386f39a8c951baf67a'
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.bitbank(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_bitbank_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'POST',
        URL('https://api.bitbank.cc/v1/user/spot/order'),
    )
    kwargs = {
        'data': {
            'pair': 'btc_jpy',
            'amount': '0.01',
            'side': 'buy',
            'type': 'market',
        },
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'POST',
        URL('https://api.bitbank.cc/v1/user/spot/order')
    )
    expected_kwargs = {
        'data': aiohttp.payload.JsonPayload({
            'pair': 'btc_jpy',
            'amount': '0.01',
            'side': 'buy',
            'type': 'market',
        }),
        'headers': CIMultiDict({
            'ACCESS-KEY': 'l5HGaEzIC3KiMqbYwtAl1r48',
            'ACCESS-NONCE': '2085848896',
            'ACCESS-SIGNATURE': '56cc247424153a185c53bd0c4d1614f2321b2a424c9db12ff4cd2f7b89361219'
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.bitbank(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_ftx_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'GET',
        URL('https://ftx.com/api/orders').with_query({
            'market': 'BTC-PERP',
        }),
    )
    kwargs = {
        'data': None,
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'GET',
        URL('https://ftx.com/api/orders?market=BTC-PERP')
    )
    expected_kwargs = {
        'data': aiohttp.formdata.FormData({})(),
        'headers': CIMultiDict({
            'FTX-KEY': 'J6vXtiZunV4lsRWoLHNYNiCa',
            'FTX-SIGN': '8905ce229394d1b4aa26ebb6a05476f33e5c9a553ed98f79d4b23b28e25cd18e',
            'FTX-TS': '2085848896000'
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.ftx(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']


def test_bitbank_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch('time.time', return_value=2085848896.0)
    args = (
        'POST',
        URL('https://ftx.com/api/orders'),
    )
    kwargs = {
        'data': {
            'market': 'BTC-PERP',
            'side': 'buy',
            'type': 'market',
            'size': '0.01',
        },
        'headers': CIMultiDict(),
        'session': mock_session,
    }
    expected_args = (
        'POST',
        URL('https://ftx.com/api/orders')
    )
    expected_kwargs = {
        'data': aiohttp.payload.JsonPayload({
            'market': 'BTC-PERP',
            'side': 'buy',
            'type': 'market',
            'size': '0.01',
        }),
        'headers': CIMultiDict({
            'FTX-KEY': 'J6vXtiZunV4lsRWoLHNYNiCa',
            'FTX-SIGN': '50d50ce69efc8e87bc8776511997544bdef4aad497c7506b26ac633f526363e3',
            'FTX-TS': '2085848896000'
        }),
        'session': mock_session,
    }
    args = pybotters.auth.Auth.ftx(args, kwargs)
    assert args == expected_args
    assert kwargs['data']._value == expected_kwargs['data']._value
    assert kwargs['headers'] == expected_kwargs['headers']
