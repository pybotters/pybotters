import datetime
import json
import random

import aiohttp.abc
import aiohttp.formdata
import aiohttp.payload
import freezegun
import pytest
import pytest_mock
from multidict import CIMultiDict
from yarl import URL

import pybotters.auth


def util_api_generater():  # pragma: no cover
    """
    $ python
    >>> from tests.test_auth import util_api_generater
    >>> print(util_api_generater())
    """
    keys = {item.name for item in pybotters.auth.Hosts.items.values()}
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    print(chars)
    return {
        k: (
            "".join([random.choice(chars) for i in range(24)]),
            "".join([random.choice(chars) for i in range(48)]).encode(),
        )
        for k in keys
    }


@pytest.fixture
def mock_session(mocker: pytest_mock.MockerFixture):
    m_sess = mocker.MagicMock()
    apis = {
        "bybit": (
            "77SQfUG7X33JhYZ3Jswpx5To",
            b"PrYiNnCnP76YzpTLvRtV9O1RBa5ecOXqrOTyXuTADCEXYoEX",
        ),
        "bybit_testnet": (
            "vDGsldGGevgVkG3ATH1PzBYd",
            b"fVp9Y9iZbkCb4JXyprq2ZbbDXupWz5V3H06REf2eJ53DyQju",
        ),
        "bybit_demo": (
            "ZpfuTHcfmsWX1kLWpSIUdtsu",
            b"7wq6s78RI6xHfPRIIt4Dvii2hO7BtFcavs5S2VlKrnGTOnMf",
        ),
        "binance": (
            "9qm1u2s4GoHt9ryIm1D2fHV8",
            b"7pDOQJ49zyyDjrNGAvB31RcnAada8nkxkl2IWKop6b0E3tXh",
        ),
        "binancespot_testnet": (
            "LyM2qCkPqVaMxWIcRIe08V4s",
            b"34BkmXEjeq5qRIbvKjhODva3XsL2MWd1pAWSq6ZkHDxnaQjh",
        ),
        "binancefuture_testnet": (
            "EDYH5JVoHJlhroiQkDntBHn8",
            b"lMFc3hibQUEOzSeG6YEvx7lMRgNBUlF07PVEm9g9U6HEWtEZ",
        ),
        "bitflyer": (
            "Pcm1rbtSRqKxTvirZDDOct1k",
            b"AKHZlv3PoAXZ0KXIKIVKOmS4ji3rV7ZIVIJRstwyplaw0FQ4",
        ),
        "gmocoin": (
            "GnHvwP7d5FbWdZinoI2hKBTR",
            b"jFRfAL7PiFLvYP6rS9u6TmTjTyVI1z21QXgDqxsCdPkMmN6I",
        ),
        "bitbank": (
            "l5HGaEzIC3KiMqbYwtAl1r48",
            b"6lgYlHSYj31SAU67jCtxn6qh60pZTeekd5iRseYZNzrC2kX5",
        ),
        "bitmex": (
            "fSvgi9a85yDFx3efr94tmJpH",
            b"1GGUedysKk2s2rMMWRmMe7uAp1mKAbORgR3rUSMe15I70P1A",
        ),
        "bitmex_testnet": (
            "fSvgi9a85yDFx3efr94tmJpH",
            b"1GGUedysKk2s2rMMWRmMe7uAp1mKAbORgR3rUSMe15I70P1A",
        ),
        "phemex": (
            "9kYxQXZ6PrR8h17lsVdDcpnJ",
            b"ZBAUiPBTQOjYgTihYnZMw2HFkTooufRnNY5iuahBPMspRYQJ",
        ),
        "phemex_testnet": (
            "v7827R5upBIWwLSV2udjBTWm",
            b"rJixSEyllgmgtthIMcLSkQmUmOxLhix4S8I2a4zBQa0opQ7Y",
        ),
        "coincheck": (
            "FASfaGggPBYDtiIHu6XoJgK6",
            b"NNT34iDK8Qr2P6nlAt4XTuw42nQUdqzHaj3337Qlz4i5l4zu",
        ),
        "okx": (
            "gYmX9fr0kqqxptUlDKESxetg",
            b"YUJHBdFNrbz7atmV3f261ZhdRffTo4S9KZKC7C7qdqcHbRR4",
            "MyPassphrase123",
        ),
        "bitget": (
            "jbcfbye8AJzXxXwMKluXM12t",
            b"mVd40qhnarPtxk3aqg0FCyY1qlTgBOKOXEcmMYfkerGUKmvr",
            "MyPassphrase123",
        ),
        "mexc": (
            "0uVJRVNmR2ZHiCXtf6yEwrwy",
            b"39aw3fMqFhHsuhbkQ0wa8JzuUgodvbTVl9tZblpSKFnB9Qh3",
        ),
        "kucoin": (
            "CYdTygFbGgM1re2J54lU2t83",
            b"r9ugGEq5pJkrBuqs6GYFgHFIgsPr4iAw06awzFByoZPRjTJs",
            "MyPassphrase123",
        ),
        "okj": (
            "NpuOBinRJMsSKHE38Gbf6MAm",
            b"xNn5J6y2uSAOZNHOORX2f6hWdD8QqE2eW01KDrt4gq74Q7A6",
            "MyPassphrase123",
        ),
        "bittrade": (
            "e2xxxxxx-99xxxxxx-84xxxxxx-7xxxx",
            b"b0xxxxxx-c6xxxxxx-94xxxxxx-dxxxx",
        ),
        "hyperliquid": (
            "0x0123456789012345678901234567890123456789012345678901234567890123",
        ),
        "hyperliquid_testnet": (
            "0x0123456789012345678901234567890123456789012345678901234567890123",
        ),
    }
    assert set(apis.keys()) == set(
        item.name if isinstance(item.name, str) else item.name.__name__
        for item in pybotters.auth.Hosts.items.values()
    )
    m_sess.__dict__["_apis"] = apis
    return m_sess


def test_hosts():
    assert hasattr(pybotters.auth.Hosts, "items")
    assert isinstance(pybotters.auth.Hosts.items, dict)
    for host, item in pybotters.auth.Hosts.items.items():
        assert isinstance(host, str)
        assert isinstance(item.name, str) | callable(item.name)
        assert callable(item.func)


def test_item():
    name = "example"

    def func(*args, **kwargs): ...

    item = pybotters.auth.Item(name, func)
    assert item.name == name
    assert item.func == func


def test_selector_okx():
    api_name = pybotters.auth.DynamicNameSelector.okx(
        args=tuple(), kwargs={"headers": {}}
    )
    assert api_name == "okx"

    api_name = pybotters.auth.DynamicNameSelector.okx(
        args=tuple(), kwargs={"headers": {"foo": "bar"}}
    )
    assert api_name == "okx"

    api_name = pybotters.auth.DynamicNameSelector.okx(
        args=tuple(), kwargs={"headers": {"x-simulated-trading": "1"}}
    )
    assert api_name == "okx_demo"


def test_bybit_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://api.bybit.com/v5/order/history").with_query(
            {
                "category": "linear",
                "symbol": "BTCUSDT",
                "cursor": ("page_token%3D26854%26"),
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL(
            "https://api.bybit.com/v5/order/history?category=linear&symbol=BTCUSDT&curs"
            "or=page_token%253D26854%2526"
        ),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "X-BAPI-API-KEY": "77SQfUG7X33JhYZ3Jswpx5To",
                "X-BAPI-TIMESTAMP": "2085848896000",
                "X-BAPI-SIGN": (
                    "862bf2b354912bb4cf84113929aa8145376b5419d2a41457265394516e82afa9"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bybit(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_bybit_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://api.bybit.com/v5/order/create"),
    )
    kwargs = {
        "data": {
            "category": "linear",
            "symbol": "BTCUSDT",
            "side": "Buy",
            "orderType": "Market",
            "qty": "0.001",
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://api.bybit.com/v5/order/create"))
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "category": "linear",
                "symbol": "BTCUSDT",
                "side": "Buy",
                "orderType": "Market",
                "qty": "0.001",
            }
        ),
        "headers": CIMultiDict(
            {
                "X-BAPI-API-KEY": "77SQfUG7X33JhYZ3Jswpx5To",
                "X-BAPI-TIMESTAMP": "2085848896000",
                "X-BAPI-SIGN": (
                    "97918f80ac923cebb49dd0e643d949c2d79a79e2da697865b40c565fdf877591"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bybit(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_binance_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://testnet.binance.vision/api/v3/order/test").with_query(
            {
                "symbol": "BTCUSDT",
                "side": "SELL",
            }
        ),
    )
    kwargs = {
        "data": {
            "type": "MARKET",
            "quantity": "0.001",
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "POST",
        URL("https://testnet.binance.vision/api/v3/order/test").with_query(
            {
                "symbol": "BTCUSDT",
                "side": "SELL",
                "timestamp": "2085848896000",
                "signature": (
                    "4a538ce375d23684c909cfe01a2f63488080ef05d247156057067ee3c45358bc"
                ),
            }
        ),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData(
            {
                "type": "MARKET",
                "quantity": "0.001",
            }
        )(),
        "headers": CIMultiDict({"X-MBX-APIKEY": "LyM2qCkPqVaMxWIcRIe08V4s"}),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.binance(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_binance_post_listenkey(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://testnet.binance.vision/api/v3/userDataStream"),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "POST",
        URL("https://testnet.binance.vision/api/v3/userDataStream"),
    )
    expected_kwargs = {
        "data": None,
        "headers": CIMultiDict({"X-MBX-APIKEY": "LyM2qCkPqVaMxWIcRIe08V4s"}),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.binance(args, kwargs)
    assert args == expected_args
    assert kwargs["data"] == expected_kwargs["data"]
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_binance_ws_nosign(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL(
            "wss://testnet.binance.vision/ws/pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61"
            "cv6a81va65sdf19v8a65a1"
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict({"Upgrade": "websocket"}),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL(
            "wss://testnet.binance.vision/ws/pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61"
            "cv6a81va65sdf19v8a65a1"
        ),
    )
    expected_kwargs = {
        "data": None,
        "headers": CIMultiDict({"Upgrade": "websocket"}),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.binance(args, kwargs)
    assert args == expected_args
    assert kwargs["data"] == expected_kwargs["data"]
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_bitflyer_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://api.bitflyer.com/v1/me/getchildorders").with_query(
            {
                "product_code": "FX_BTC_JPY",
                "child_order_state": "ACTIVE",
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL(
            "https://api.bitflyer.com/v1/me/getchildorders?product_code=FX_BTC_JPY&chil"
            "d_order_state=ACTIVE"
        ),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "ACCESS-KEY": "Pcm1rbtSRqKxTvirZDDOct1k",
                "ACCESS-TIMESTAMP": "2085848896000",
                "ACCESS-SIGN": (
                    "7413e237eee917f1a2a276f6d1553a82fc8ca7b1b3353ff02a070b5e3c3deda5"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bitflyer(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_bitflyer_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://api.bitflyer.com/v1/me/sendchildorder"),
    )
    kwargs = {
        "data": {
            "product_code": "FX_BTC_JPY",
            "child_order_type": "MARKET",
            "side": "BUY",
            "size": 0.01,
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://api.bitflyer.com/v1/me/sendchildorder"))
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "product_code": "FX_BTC_JPY",
                "child_order_type": "MARKET",
                "side": "BUY",
                "size": 0.01,
            }
        ),
        "headers": CIMultiDict(
            {
                "ACCESS-KEY": "Pcm1rbtSRqKxTvirZDDOct1k",
                "ACCESS-TIMESTAMP": "2085848896000",
                "ACCESS-SIGN": (
                    "0e391462aad928c8152201a8854b095f084d1b9f6bd9c0d9b8b026c9963711b4"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bitflyer(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_gmocoin_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://api.coin.z.com/private/v1/activeOrders").with_query(
            {
                "symbol": "BTC_JPY",
                "page": 1,
                "count": 100,
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL(
            "https://api.coin.z.com/private/v1/activeOrders?symbol=BTC_JPY&page=1&count"
            "=100"
        ),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "API-KEY": "GnHvwP7d5FbWdZinoI2hKBTR",
                "API-TIMESTAMP": "2085848896000",
                "API-SIGN": (
                    "e6f0c55c381b08f0892daad0c5e27f69050dab787d98e45680802e340849978a"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.gmocoin(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_gmocoin_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://api.coin.z.com/private/v1/order"),
    )
    kwargs = {
        "data": {
            "symbol": "BTC_JPY",
            "side": "BUY",
            "executionType": "MARKET",
            "size": 0.01,
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://api.coin.z.com/private/v1/order"))
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "symbol": "BTC_JPY",
                "side": "BUY",
                "executionType": "MARKET",
                "size": 0.01,
            }
        ),
        "headers": CIMultiDict(
            {
                "API-KEY": "GnHvwP7d5FbWdZinoI2hKBTR",
                "API-TIMESTAMP": "2085848896000",
                "API-SIGN": (
                    "b6e96f0fe71993d29b50dc8a9a0bebe974fb38749e2ee7aed1e4abb845b063bf"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.gmocoin(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_bitbank_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://api.bitbank.cc/v1/user/spot/order").with_query(
            {
                "pair": "btc_jpy",
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL("https://api.bitbank.cc/v1/user/spot/order?pair=btc_jpy"),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "ACCESS-KEY": "l5HGaEzIC3KiMqbYwtAl1r48",
                "ACCESS-REQUEST-TIME": "2085848896000",
                "ACCESS-SIGNATURE": (
                    "87c0358b092b78c4ac8f46bbd447665acbe9c8a136068473d14f8143ac9ac6aa"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bitbank(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_bitbank_get_with_window(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://api.bitbank.cc/v1/user/spot/order").with_query(
            {
                "pair": "btc_jpy",
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict({"ACCESS-TIME-WINDOW": "1000"}),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL("https://api.bitbank.cc/v1/user/spot/order?pair=btc_jpy"),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "ACCESS-TIME-WINDOW": "1000",
                "ACCESS-KEY": "l5HGaEzIC3KiMqbYwtAl1r48",
                "ACCESS-REQUEST-TIME": "2085848896000",
                "ACCESS-SIGNATURE": (
                    "b01d3c62a7a80fcd6ca46736c9b956c703a7ebedc04d788b9b33b433979e84bd"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bitbank(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_bitbank_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://api.bitbank.cc/v1/user/spot/order"),
    )
    kwargs = {
        "data": {
            "pair": "btc_jpy",
            "amount": "0.01",
            "side": "buy",
            "type": "market",
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://api.bitbank.cc/v1/user/spot/order"))
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "pair": "btc_jpy",
                "amount": "0.01",
                "side": "buy",
                "type": "market",
            }
        ),
        "headers": CIMultiDict(
            {
                "ACCESS-KEY": "l5HGaEzIC3KiMqbYwtAl1r48",
                "ACCESS-REQUEST-TIME": "2085848896000",
                "ACCESS-SIGNATURE": (
                    "d3f190a3707dae355edf4cc38252c02d6aa360d8c3b84f2a734f1ac306b88812"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bitbank(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_bitmex_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://www.bitmex.com/api/v1/order").with_query(
            {
                "symbol": "XBTUSD",
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("GET", URL("https://www.bitmex.com/api/v1/order?symbol=XBTUSD"))
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "api-expires": "2085848901000",
                "api-key": "fSvgi9a85yDFx3efr94tmJpH",
                "api-signature": (
                    "62760c6f7c194d1b3aca1fd80cbf5d75a1adb154c593b6562be7f33b7d29a5dd"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bitmex(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_bitmex_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://www.bitmex.com/api/v1/order"),
    )
    kwargs = {
        "data": {
            "symbol": "XBTUSD",
            "side": "Buy",
            "orderQty": 100,
            "ordType": "Market",
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://www.bitmex.com/api/v1/order"))
    expected_kwargs = {
        "data": aiohttp.formdata.FormData(
            {
                "symbol": "XBTUSD",
                "side": "Buy",
                "orderQty": 100,
                "ordType": "Market",
            }
        )(),
        "headers": CIMultiDict(
            {
                "api-expires": "2085848901000",
                "api-key": "fSvgi9a85yDFx3efr94tmJpH",
                "api-signature": (
                    "2193e9dbfa05580140238a29822d8d6154b529a42efc4461cf767db56bbe4fc6"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bitmex(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_bitmex_ws(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("wss://www.bitmex.com/realtime"),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL("wss://www.bitmex.com/realtime"),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "api-expires": "2085848901000",
                "api-key": "fSvgi9a85yDFx3efr94tmJpH",
                "api-signature": (
                    "367f193b6d183f55edc2973611bc3f93cbc99ac9a4f9dac11185108d40052dee"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bitmex(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_phemex_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL(
            "https://api.phemex.com/orders/activeList?ordStatus=New&ordStatus=Partially"
            "Filled&ordStatus=Untriggered&symbol=BTCUSD"
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL(
            "https://api.phemex.com/orders/activeList?ordStatus=New&ordStatus=Partially"
            "Filled&ordStatus=Untriggered&symbol=BTCUSD"
        ),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "x-phemex-access-token": "9kYxQXZ6PrR8h17lsVdDcpnJ",
                "x-phemex-request-expiry": "2085848956",
                "x-phemex-request-signature": (
                    "abe7afcaaff085715ad26615b315007bdc4590390efcf5267b4317ce832ca6b5"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.phemex(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_phemex_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://api.phemex.com/orders"),
    )
    kwargs = {
        "data": {
            "symbol": "BTCUSD",
            "clOrdID": "uuid-1573058952273",
            "side": "Sell",
            "priceEp": 93185000,
            "orderQty": 7,
            "ordType": "Limit",
            "reduceOnly": False,
            "timeInForce": "GoodTillCancel",
            "takeProfitEp": 0,
            "stopLossEp": 0,
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://api.phemex.com/orders"))
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "symbol": "BTCUSD",
                "clOrdID": "uuid-1573058952273",
                "side": "Sell",
                "priceEp": 93185000,
                "orderQty": 7,
                "ordType": "Limit",
                "reduceOnly": False,
                "timeInForce": "GoodTillCancel",
                "takeProfitEp": 0,
                "stopLossEp": 0,
            }
        ),
        "headers": CIMultiDict(
            {
                "x-phemex-access-token": "9kYxQXZ6PrR8h17lsVdDcpnJ",
                "x-phemex-request-expiry": "2085848956",
                "x-phemex-request-signature": (
                    "5a02dc2e10c613256eec342d1833229fa00e5c7f58e522c70fd7ee12613ce7d6"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.phemex(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_coincheck_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://coincheck.com/api/deposit_money").with_query(
            {
                "currency": "BTC",
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL("https://coincheck.com/api/deposit_money?currency=BTC"),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "ACCESS-KEY": "FASfaGggPBYDtiIHu6XoJgK6",
                "ACCESS-NONCE": "2085848896000",
                "ACCESS-SIGNATURE": (
                    "8c5b1d6bcfb18f031955c33e9134143d3ab39187de7c50c020df446bbdd19b28"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.coincheck(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_coincheck_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://coincheck.com/api/exchange/orders"),
    )
    kwargs = {
        "data": {
            "pair": "btc_jpy",
            "order_type": "market_buy",
            "market_buy_amount": "BUY",
            "size": 0.01,
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://coincheck.com/api/exchange/orders"))
    expected_kwargs = {
        "data": aiohttp.formdata.FormData(
            {
                "pair": "btc_jpy",
                "order_type": "market_buy",
                "market_buy_amount": "BUY",
                "size": 0.01,
            }
        )(),
        "headers": CIMultiDict(
            {
                "ACCESS-KEY": "FASfaGggPBYDtiIHu6XoJgK6",
                "ACCESS-NONCE": "2085848896000",
                "ACCESS-SIGNATURE": (
                    "e2fb003781e70de254c0bce4f15ebed979175bdfca88c3839dafa17e48df94e0"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.coincheck(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


@pytest.mark.freeze_time(datetime.datetime(2036, 2, 5, 18, 28, 16))
def test_okx_get(mock_session, mocker: pytest_mock.MockerFixture):
    args = (
        "GET",
        URL("https://www.okx.com/api/v5/account/balance").with_query(
            {
                "ccy": "BTC,ETH",
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL("https://www.okx.com/api/v5/account/balance?ccy=BTC,ETH"),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "OK-ACCESS-KEY": "gYmX9fr0kqqxptUlDKESxetg",
                "OK-ACCESS-SIGN": "fWIucRPbzCxgeO2g9g0nV+FJyX1tr5/LKSypAyiVpQI=",
                "OK-ACCESS-TIMESTAMP": "2036-02-05T18:28:16.000Z",
                "OK-ACCESS-PASSPHRASE": "MyPassphrase123",
                "Content-Type": "application/json",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.okx(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


@pytest.mark.freeze_time(datetime.datetime(2036, 2, 5, 18, 28, 16))
def test_okx_post(mock_session, mocker: pytest_mock.MockerFixture):
    args = ("POST", URL("https://www.okx.com/api/v5/trade/order"))
    kwargs = {
        "data": {
            "instId": "BTC-USDT",
            "tdMode": "cash",
            "clOrdId": "b15",
            "side": "buy",
            "ordType": "limit",
            "px": "2.15",
            "sz": "2",
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://www.okx.com/api/v5/trade/order"))
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "instId": "BTC-USDT",
                "tdMode": "cash",
                "clOrdId": "b15",
                "side": "buy",
                "ordType": "limit",
                "px": "2.15",
                "sz": "2",
            }
        ),
        "headers": CIMultiDict(
            {
                "OK-ACCESS-KEY": "gYmX9fr0kqqxptUlDKESxetg",
                "OK-ACCESS-SIGN": "iIYMZ8i1gUDjJ2RNinu6VGMIuJwbdSFFVe6OYjzlh0Q=",
                "OK-ACCESS-TIMESTAMP": "2036-02-05T18:28:16.000Z",
                "OK-ACCESS-PASSPHRASE": "MyPassphrase123",
                "Content-Type": "application/json",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.okx(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_bitget_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://api.bitget.com/api/spot/v1/account/assets").with_query(
            {
                "symbol": "BTCUSDT_SPBL",
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL("https://api.bitget.com/api/spot/v1/account/assets?symbol=BTCUSDT_SPBL"),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "Content-Type": "application/json",
                "ACCESS-KEY": "jbcfbye8AJzXxXwMKluXM12t",
                "ACCESS-SIGN": "OGmz3F0LHbvSri0tCmgDYdxclRnsf29hZ5/qi0IOxGA=",
                "ACCESS-TIMESTAMP": "2085848896000",
                "ACCESS-PASSPHRASE": "MyPassphrase123",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bitget(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_bitget_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL(
            "https://api.bitget.com/api/spot/v1/account/assets/api/spot/v1/trade/fills"
        ),
    )
    kwargs = {
        "data": {
            "symbol": "BTCUSDT_SPBL-USDT",
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "POST",
        URL(
            "https://api.bitget.com/api/spot/v1/account/assets/api/spot/v1/trade/fills"
        ),
    )
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "symbol": "BTCUSDT_SPBL-USDT",
            }
        ),
        "headers": CIMultiDict(
            {
                "Content-Type": "application/json",
                "ACCESS-KEY": "jbcfbye8AJzXxXwMKluXM12t",
                "ACCESS-SIGN": "+EzKoSg9aBmeokTWaboMdWxLQes/K0ZAuaYIYNtKtLw=",
                "ACCESS-TIMESTAMP": "2085848896000",
                "ACCESS-PASSPHRASE": "MyPassphrase123",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bitget(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_mexc_v2_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://www.mexc.com/open/api/v2/order/open_orders").with_query(
            {
                "symbol": "BTC_USDT",
                "page_num": "1",
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL(
            "https://www.mexc.com/open/api/v2/order/open_orders?symbol=BTC_USDT&page_nu"
            "m=1"
        ),
    )
    expected_kwargs = {
        "data": None,
        "headers": CIMultiDict(
            {
                "ApiKey": "0uVJRVNmR2ZHiCXtf6yEwrwy",
                "Request-Time": "2085848896000",
                "Signature": (
                    "ce019ef241a13e8c41abca7daf029f3cbe0a0c89b115ed2f091d1937a209ca0a"
                ),
                "Content-Type": "application/json",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.mexc_v2(args, kwargs)
    assert args == expected_args
    assert kwargs["data"] == expected_kwargs["data"]
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_mexc_v2_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://www.mexc.com/open/api/v2/order/place"),
    )
    kwargs = {
        "data": {
            "symbol": "BTC_USDT",
            "price": "40000.0",
            "quantity": "1",
            "trade_type": "ASK",
            "order_type": "LIMIT_ORDER",
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://www.mexc.com/open/api/v2/order/place"))
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "symbol": "BTC_USDT",
                "price": "40000.0",
                "quantity": "1",
                "trade_type": "ASK",
                "order_type": "LIMIT_ORDER",
            }
        ),
        "headers": CIMultiDict(
            {
                "ApiKey": "0uVJRVNmR2ZHiCXtf6yEwrwy",
                "Request-Time": "2085848896000",
                "Signature": (
                    "d2a4b3fa386a6d4b96a00a7fafa5be223584cd6f511848330ca6615e67d0a994"
                ),
                "Content-Type": "application/json",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.mexc_v2(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_mexc_v3_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)

    # without query
    args = (
        "GET",
        URL("https://api.mexc.com/api/v3/account"),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL(
            "https://api.mexc.com/api/v3/account?timestamp=2085848896000&signature=bea4"
            "958a74f3d56f984e7fafd012cb2474813ff98d857b9e75d5eb46e4bcc5bc"
        ),
    )
    expected_kwargs = {
        "data": b"",
        "headers": CIMultiDict(
            {
                "X-MEXC-APIKEY": "0uVJRVNmR2ZHiCXtf6yEwrwy",
                "Content-Type": "application/json",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.mexc_v3(args, kwargs)
    assert args == expected_args
    assert kwargs["data"] == expected_kwargs["data"]
    assert kwargs["headers"] == expected_kwargs["headers"]

    # with query
    args = (
        "GET",
        URL("https://api.mexc.com/api/v3/openOrders").with_query(
            {
                "symbol": "BTCUSDT",
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL(
            "https://api.mexc.com/api/v3/openOrders?symbol=BTCUSDT&timestamp=2085848896"
            "000&signature=1923150018f1270770e4fcbb9d4362930eea069a2bdff8d14df6a8b4ad95"
            "460f"
        ),
    )
    expected_kwargs = {
        "data": b"",
        "headers": CIMultiDict(
            {
                "X-MEXC-APIKEY": "0uVJRVNmR2ZHiCXtf6yEwrwy",
                "Content-Type": "application/json",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.mexc_v3(args, kwargs)
    assert args == expected_args
    assert kwargs["data"] == expected_kwargs["data"]
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_mexc_v3_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://api.mexc.com/api/v3/order"),
    )
    kwargs = {
        "data": {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
            "quoteOrderQty": "5",
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "POST",
        URL(
            "https://api.mexc.com/api/v3/order?timestamp=2085848896000&signature=692fc1"
            "41d6a0bb9abc90714e253369b715b74c115358d9cbf6f450bdde688fdd"
        ),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData(
            {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quoteOrderQty": "5",
            }
        )()._value,
        "headers": CIMultiDict(
            {
                "X-MEXC-APIKEY": "0uVJRVNmR2ZHiCXtf6yEwrwy",
                "Content-Type": "application/json",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.mexc_v3(args, kwargs)
    assert args == expected_args
    assert kwargs["data"] == expected_kwargs["data"]
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_kucoin_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = ("GET", URL("https://api-futures.kucoin.com/api/v1/orders"))
    kwargs = {"data": None, "headers": CIMultiDict(), "session": mock_session}
    expected_args = ("GET", URL("https://api-futures.kucoin.com/api/v1/orders"))
    expected_kwargs = {
        "data": None,
        "headers": {
            "KC-API-SIGN": "S3VbT04nwftUSb9URF0s/KeCLJfzgz8FsytZ9gDaxsw=",
            "KC-API-TIMESTAMP": "2085848896000",
            "KC-API-KEY": "CYdTygFbGgM1re2J54lU2t83",
            "KC-API-PASSPHRASE": "NdCF6AMfsU+m1ywTeSVeBREs7l1veIb487x9csAONO4=",
            "KC-API-KEY-VERSION": "2",
        },
    }
    pybotters.auth.Auth.kucoin(args, kwargs)
    assert args == expected_args
    assert kwargs["data"] == expected_kwargs["data"]
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_kucoin_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://api-futures.kucoin.com/api/v1/orders"),
    )
    kwargs = {
        "data": {
            "clientOid": "1",
            "symbol": "XBTUSDTM",
            "side": "buy",
            "type": "limit",
            "leverage": "1",
            "price": "19200",
            "size": 1,
        },
        "headers": CIMultiDict({}),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://api-futures.kucoin.com/api/v1/orders"))
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "clientOid": "1",
                "symbol": "XBTUSDTM",
                "side": "buy",
                "type": "limit",
                "leverage": "1",
                "price": "19200",
                "size": 1,
            }
        ),
        "headers": CIMultiDict(
            {
                "KC-API-SIGN": "aoxLuRURO0t1z9hhh9ERbHjVp6bJ1K5bfoU2xHH25Y4=",
                "KC-API-TIMESTAMP": "2085848896000",
                "KC-API-KEY": "CYdTygFbGgM1re2J54lU2t83",
                "KC-API-PASSPHRASE": "NdCF6AMfsU+m1ywTeSVeBREs7l1veIb487x9csAONO4=",
                "KC-API-KEY-VERSION": "2",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.kucoin(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


@pytest.mark.freeze_time(datetime.datetime(2036, 2, 5, 18, 28, 16))
def test_okj_get(mock_session, mocker: pytest_mock.MockerFixture):
    args = (
        "GET",
        URL(
            "https://www.okcoin.jp/api/spot/v3/orders?instrument_id=BTC-JPY&state=filled&limit=2&&after=2500723297223680"
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL(
            "https://www.okcoin.jp/api/spot/v3/orders?instrument_id=BTC-JPY&state=filled&limit=2&&after=2500723297223680"
        ),
    )
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "OK-ACCESS-KEY": "NpuOBinRJMsSKHE38Gbf6MAm",
                "OK-ACCESS-SIGN": "z2O3V5la0FP21wbxkoFr5f+HDvoiqnZ5Cklz814LWJE=",
                "OK-ACCESS-TIMESTAMP": "2036-02-05T18:28:16.000Z",
                "OK-ACCESS-PASSPHRASE": "MyPassphrase123",
                "Content-Type": "application/json",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.okj(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


@pytest.mark.freeze_time(datetime.datetime(2036, 2, 5, 18, 28, 16))
def test_okj_post(mock_session, mocker: pytest_mock.MockerFixture):
    args = ("POST", URL("https://www.okcoin.jp/api/spot/v3/orders"))
    kwargs = {
        "data": {
            "type": "limit",
            "side": "buy",
            "instrument_id": "BTC-JPY",
            "size": "0.001",
            "client_oid": "oktspot79",
            "price": "4638.51",
            "notional": "",
            "order_type": "3",
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://www.okcoin.jp/api/spot/v3/orders"))
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "type": "limit",
                "side": "buy",
                "instrument_id": "BTC-JPY",
                "size": "0.001",
                "client_oid": "oktspot79",
                "price": "4638.51",
                "notional": "",
                "order_type": "3",
            }
        ),
        "headers": CIMultiDict(
            {
                "OK-ACCESS-KEY": "NpuOBinRJMsSKHE38Gbf6MAm",
                "OK-ACCESS-SIGN": "V/csv742qfo7G7QAi81qQQik8KrEmwKh5xsTHIFlq2M=",
                "OK-ACCESS-TIMESTAMP": "2036-02-05T18:28:16.000Z",
                "OK-ACCESS-PASSPHRASE": "MyPassphrase123",
                "Content-Type": "application/json",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.okj(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


@pytest.mark.freeze_time(datetime.datetime(2017, 5, 11, 15, 19, 30))
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            {
                "args": (
                    "GET",
                    URL("https://api-cloud.bittrade.co.jp/v1/order/orders").with_query(
                        {"order-id": "123456789"}
                    ),
                ),
                "kwargs": {"data": None, "headers": None},
            },
            {
                "args": (
                    "GET",
                    URL("https://api-cloud.bittrade.co.jp/v1/order/orders").with_query(
                        {
                            "order-id": "123456789",
                            "AccessKeyId": "e2xxxxxx-99xxxxxx-84xxxxxx-7xxxx",
                            "SignatureMethod": "HmacSHA256",
                            "SignatureVersion": "2",
                            "Timestamp": "2017-05-11T15:19:30",
                            "Signature": "qmHOHCJ+e8Psi2VqhdZELGKrhTcvAOaBekVOeFXQMc0=",
                        }
                    ),
                ),
                "kwargs": {"data": None, "headers": None},
            },
        ),
        (
            {
                "args": (
                    "POST",
                    URL("https://api-cloud.bittrade.co.jp/v1/order/orders/place"),
                ),
                "kwargs": {"data": {"order-id": "123456789"}, "headers": None},
            },
            {
                "args": (
                    "POST",
                    URL(
                        "https://api-cloud.bittrade.co.jp/v1/order/orders/place"
                    ).with_query(
                        {
                            "AccessKeyId": "e2xxxxxx-99xxxxxx-84xxxxxx-7xxxx",
                            "SignatureMethod": "HmacSHA256",
                            "SignatureVersion": "2",
                            "Timestamp": "2017-05-11T15:19:30",
                            "Signature": "/yTARtqPKvYXF9PkmdgkruvfJWSr8umI6HOrNgvs4uk=",
                        }
                    ),
                ),
                "kwargs": {
                    "data": aiohttp.payload.JsonPayload({"order-id": "123456789"}),
                    "headers": None,
                },
            },
        ),
    ],
)
def test_bittrade(mock_session, test_input, expected):
    args = test_input["args"]
    kwargs = test_input["kwargs"]
    kwargs["session"] = mock_session

    args = pybotters.auth.Auth.bittrade(args, kwargs)

    expected["kwargs"]["session"] = mock_session
    if isinstance(expected["kwargs"]["data"], aiohttp.payload.Payload):
        expected["kwargs"]["data"] = expected["kwargs"]["data"]._value
    if isinstance(kwargs["data"], aiohttp.payload.Payload):
        kwargs["data"] = kwargs["data"]._value

    assert {"args": args, "kwargs": kwargs} == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # Case 0: sign_l1_action
        (
            # test_input
            {
                "args": ("POST", URL("https://api.hyperliquid.xyz/exchange")),
                "kwargs": {
                    "data": {
                        "action": {
                            "type": "order",
                            "orders": [
                                {
                                    "a": 1,
                                    "b": True,
                                    "p": "100",
                                    "s": "100",
                                    "r": False,
                                    "t": {"limit": {"tif": "Gtc"}},
                                }
                            ],
                            "grouping": "na",
                        },
                    },
                    "headers": None,
                },
                "freeze_time": 0,
            },
            # expected
            {
                "args": ("POST", URL("https://api.hyperliquid.xyz/exchange")),
                "kwargs": {
                    "data": {
                        "action": {
                            "type": "order",
                            "orders": [
                                {
                                    "a": 1,
                                    "b": True,
                                    "p": "100",
                                    "s": "100",
                                    "r": False,
                                    "t": {"limit": {"tif": "Gtc"}},
                                }
                            ],
                            "grouping": "na",
                        },
                        "nonce": 0,
                        "signature": {
                            "r": "0xd65369825a9df5d80099e513cce430311d7d26ddf477f5b3a33d2806b100d78e",
                            "s": "0x2b54116ff64054968aa237c20ca9ff68000f977c93289157748a3162b6ea940e",
                            "v": 28,
                        },
                    },
                    "headers": None,
                },
            },
        ),
        # Case 1: sign_user_signed_action
        (
            # test_input
            {
                "args": ("POST", URL("https://api.hyperliquid.xyz/exchange")),
                "kwargs": {
                    "data": {
                        "action": {
                            "type": "usdSend",
                            "hyperliquidChain": "Testnet",
                            "destination": "0x5e9ee1089755c3435139848e47e6635505d5a13a",
                            "amount": "1",
                            "time": 1687816341423,
                        },
                    },
                    "headers": None,
                },
                "freeze_time": 1687816341.423,
            },
            # expected
            {
                "args": ("POST", URL("https://api.hyperliquid.xyz/exchange")),
                "kwargs": {
                    "data": {
                        "action": {
                            "type": "usdSend",
                            "hyperliquidChain": "Testnet",
                            "destination": "0x5e9ee1089755c3435139848e47e6635505d5a13a",
                            "amount": "1",
                            "time": 1687816341423,
                            "signatureChainId": "0x66eee",
                        },
                        "nonce": 1687816341423,
                        "signature": {
                            "r": "0x637b37dd731507cdd24f46532ca8ba6eec616952c56218baeff04144e4a77073",
                            "s": "0x11a6a24900e6e314136d2592e2f8d502cd89b7c15b198e1bee043c9589f9fad7",
                            "v": 27,
                        },
                    },
                    "headers": None,
                },
            },
        ),
        # Case 2: Testnet
        (
            # test_input
            {
                "args": ("POST", URL("https://api.hyperliquid-testnet.xyz/exchange")),
                "kwargs": {
                    "data": {
                        "action": {
                            "type": "order",
                            "orders": [
                                {
                                    "a": 1,
                                    "b": True,
                                    "p": "100",
                                    "s": "100",
                                    "r": False,
                                    "t": {"limit": {"tif": "Gtc"}},
                                }
                            ],
                            "grouping": "na",
                        },
                    },
                    "headers": None,
                },
                "freeze_time": 0,
            },
            # expected
            {
                "args": ("POST", URL("https://api.hyperliquid-testnet.xyz/exchange")),
                "kwargs": {
                    "data": {
                        "action": {
                            "type": "order",
                            "orders": [
                                {
                                    "a": 1,
                                    "b": True,
                                    "p": "100",
                                    "s": "100",
                                    "r": False,
                                    "t": {"limit": {"tif": "Gtc"}},
                                }
                            ],
                            "grouping": "na",
                        },
                        "nonce": 0,
                        "signature": {
                            "r": "0x82b2ba28e76b3d761093aaded1b1cdad4960b3af30212b343fb2e6cdfa4e3d54",
                            "s": "0x6b53878fc99d26047f4d7e8c90eb98955a109f44209163f52d8dc4278cbbd9f5",
                            "v": 27,
                        },
                    },
                    "headers": None,
                },
            },
        ),
        # Case 3: Info endpoint
        (
            # test_input
            {
                "args": ("POST", URL("https://api.hyperliquid.xyz/info")),
                "kwargs": {
                    "data": {"action": {"type": "meta"}},
                    "headers": None,
                },
                "freeze_time": 0,
            },
            # expected
            {
                "args": ("POST", URL("https://api.hyperliquid.xyz/info")),
                "kwargs": {
                    "data": {"action": {"type": "meta"}},
                    "headers": None,
                },
            },
        ),
    ],
)
def test_hyperliquid(mock_session, test_input, expected):
    args = test_input["args"]
    kwargs = test_input["kwargs"]
    kwargs["session"] = mock_session

    with freezegun.freeze_time(
        datetime.datetime.fromtimestamp(
            test_input["freeze_time"], tz=datetime.timezone.utc
        )
    ):
        args = pybotters.auth.Auth.hyperliquid(args, kwargs)

    expected["kwargs"]["session"] = mock_session
    if isinstance(kwargs["data"], aiohttp.payload.JsonPayload):
        kwargs["data"] = json.loads(kwargs["data"].decode())

    assert {"args": args, "kwargs": kwargs} == expected
