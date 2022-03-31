import datetime
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
        "binance": (
            "9qm1u2s4GoHt9ryIm1D2fHV8",
            b"7pDOQJ49zyyDjrNGAvB31RcnAada8nkxkl2IWKop6b0E3tXh",
        ),
        "binance_testnet": (
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
        "liquid": (
            "5DjzgmQXRksQNDBQ5G1rNIv7",
            b"WXlZDDzyjWtz1bd7MsGoXPMEohkdUuB95HHgBbKwKBaCyDrp",
        ),
        "bitbank": (
            "l5HGaEzIC3KiMqbYwtAl1r48",
            b"6lgYlHSYj31SAU67jCtxn6qh60pZTeekd5iRseYZNzrC2kX5",
        ),
        "ftx": (
            "J6vXtiZunV4lsRWoLHNYNiCa",
            b"8ORbaZIrTNcV6Lw48x12RrEzuT0YqbCiluml7LITzG2ud2Nf",
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
    }
    assert set(apis.keys()) == set(
        item.name if isinstance(item.name, str) else item.name({})
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

    def func(*args, **kwargs):
        return args

    item = pybotters.auth.Item(name, func)
    assert item.name == name
    assert item.func == func


def test_selector_okx():
    assert pybotters.auth.NameSelector.okx({}) == "okx"
    assert pybotters.auth.NameSelector.okx({"foo": "bar"}) == "okx"
    assert pybotters.auth.NameSelector.okx({"x-simulated-trading": "1"}) == "okx_demo"


def test_bybit_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://api.bybit.com/v2/private/order/list").with_query(
            {
                "symbol": "BTCUSD",
                "cursor": (
                    "w01XFyyZc8lhtCLl6NgAaYBRfsN9Qtpp1f2AUy3AS4+fFDzNSlVKa0od8DKCqgAn"
                ),
            }
        ),
    )
    kwargs = {
        "data": None,
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL(
            "https://api.bybit.com/v2/private/order/list?symbol=BTCUSD&cursor=w01XFyyZc"
            "8lhtCLl6NgAaYBRfsN9Qtpp1f2AUy3AS4%2BfFDzNSlVKa0od8DKCqgAn&api_key=77SQfUG7"
            "X33JhYZ3Jswpx5To&timestamp=2085848891000&recv_window=10000&sign=4f21ff83f9"
            "243422333d12905b167e075516a978307ff14899b90dd14091a0a9"
        ),
    )
    expected_kwargs = {
        "data": None,
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bybit(args, kwargs)
    assert args == expected_args
    assert kwargs["data"] == expected_kwargs["data"]


def test_bybit_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://api.bybit.com/v2/private/order/create"),
    )
    kwargs = {
        "data": {
            "symbol": "BTCUSD",
            "side": "Buy",
            "order_type": "Market",
            "qty": 100,
            "time_in_force": "GoodTillCancel",
        },
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://api.bybit.com/v2/private/order/create"))
    expected_kwargs = {
        "data": aiohttp.formdata.FormData(
            {
                "api_key": "77SQfUG7X33JhYZ3Jswpx5To",
                "order_type": "Market",
                "qty": "100",
                "recv_window": "10000",
                "side": "Buy",
                "symbol": "BTCUSD",
                "time_in_force": "GoodTillCancel",
                "timestamp": "2085848891000",
                "sign": (
                    "1547e15445903b6c4cb541f79830fd502c843c7d88f90022f122bca8a311819e"
                ),
            }
        )(),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bybit(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value


def test_bybit_ws(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("wss://stream.bybit.com/realtime"),
    )
    kwargs = {
        "data": None,
        "session": mock_session,
    }
    expected_args = (
        "GET",
        URL(
            "wss://stream.bybit.com/realtime?api_key=77SQfUG7X33JhYZ3Jswpx5To&expires=2"
            "085848901000&signature=a8bcd91ad5f8efdaefaf4ca6f38e551d739d6b42c2b54c85667"
            "fb181ecbc29a4"
        ),
    )
    expected_kwargs = {
        "data": None,
        "session": mock_session,
    }
    args = pybotters.auth.Auth.bybit(args, kwargs)
    assert args == expected_args
    assert kwargs["data"] == expected_kwargs["data"]


def test_binance_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://dapi.binance.com/dapi/v1/order").with_query(
            {
                "symbol": "BTCUSD_PERP",
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
            "https://dapi.binance.com/dapi/v1/order?symbol=BTCUSD_PERP&timestamp=208584"
            "8896000&signature=cfd48880dc0ceb003e5f009205a4ebd6415ddeb40addafd1c1345286"
            "81d98ccf"
        ),
    )
    expected_kwargs = {
        "data": None,
        "headers": CIMultiDict({"X-MBX-APIKEY": "9qm1u2s4GoHt9ryIm1D2fHV8"}),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.binance(args, kwargs)
    assert args == expected_args
    assert kwargs["data"] == expected_kwargs["data"]
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_binance_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://dapi.binance.com/dapi/v1/order"),
    )
    kwargs = {
        "data": {
            "symbol": "BTCUSD_PERP",
            "side": "BUY",
            "type": "MARKET",
            "quantity": 1,
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://dapi.binance.com/dapi/v1/order"))
    expected_kwargs = {
        "data": aiohttp.formdata.FormData(
            {
                "symbol": "BTCUSD_PERP",
                "side": "BUY",
                "type": "MARKET",
                "quantity": 1,
                "timestamp": "2085848896000",
                "signature": (
                    "ab855d04b87a8043830ca5dfabcded89012c69ed2ddeaaa1fc1dad54a82d1675"
                ),
            }
        )(),
        "headers": CIMultiDict({"X-MBX-APIKEY": "9qm1u2s4GoHt9ryIm1D2fHV8"}),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.binance(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_binance_ws(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL(
            "wss://dstream.binance.com/ws/pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6"
            "a81va65sdf19v8a65a1"
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
            "wss://dstream.binance.com/ws/pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6"
            "a81va65sdf19v8a65a1"
        ),
    )
    expected_kwargs = {
        "data": None,
        "headers": CIMultiDict({"X-MBX-APIKEY": "9qm1u2s4GoHt9ryIm1D2fHV8"}),
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


def test_liquid_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://api.liquid.com/orders").with_query(
            {
                "id": 5,
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("GET", URL("https://api.liquid.com/orders?id=5"))
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "X-Quoine-API-Version": "2",
                "X-Quoine-Auth": (
                    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiL29yZGVycz9pZD01I"
                    "iwibm9uY2UiOiIyMDg1ODQ4ODk2MDAwIiwidG9rZW5faWQiOiI1RGp6Z21RWFJrc1F"
                    "OREJRNUcxck5JdjcifQ.Q8jvnnFafWJ_piQyB1GyEc1nxfil0uwnyjMvNV2icgA"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.liquid(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_liquid_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://api.liquid.com/orders"),
    )
    kwargs = {
        "data": {
            "quantity": 0.01,
            "order_type": "market",
            "product_id": 5,
            "side": "buy",
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://api.liquid.com/orders"))
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "quantity": 0.01,
                "order_type": "market",
                "product_id": 5,
                "side": "buy",
            }
        ),
        "headers": CIMultiDict(
            {
                "X-Quoine-API-Version": "2",
                "X-Quoine-Auth": (
                    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiL29yZGVycyIsIm5vb"
                    "mNlIjoiMjA4NTg0ODg5NjAwMCIsInRva2VuX2lkIjoiNURqemdtUVhSa3NRTkRCUTV"
                    "HMXJOSXY3In0.vS_l9BAKGTrROl2uVFlEP1SA4FaI9TL4JuRpLCyilG0"
                ),
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.liquid(args, kwargs)
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
                "ACCESS-NONCE": "2085848896000",
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
                "ACCESS-NONCE": "2085848896000",
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


def test_ftx_get(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "GET",
        URL("https://ftx.com/api/orders").with_query(
            {
                "market": "BTC-PERP",
            }
        ),
    )
    kwargs = {
        "data": None,
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("GET", URL("https://ftx.com/api/orders?market=BTC-PERP"))
    expected_kwargs = {
        "data": aiohttp.formdata.FormData({})(),
        "headers": CIMultiDict(
            {
                "FTX-KEY": "J6vXtiZunV4lsRWoLHNYNiCa",
                "FTX-SIGN": (
                    "8905ce229394d1b4aa26ebb6a05476f33e5c9a553ed98f79d4b23b28e25cd18e"
                ),
                "FTX-TS": "2085848896000",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.ftx(args, kwargs)
    assert args == expected_args
    assert kwargs["data"]._value == expected_kwargs["data"]._value
    assert kwargs["headers"] == expected_kwargs["headers"]


def test_ftx_post(mock_session, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.time", return_value=2085848896.0)
    args = (
        "POST",
        URL("https://ftx.com/api/orders"),
    )
    kwargs = {
        "data": {
            "market": "BTC-PERP",
            "side": "buy",
            "type": "market",
            "size": "0.01",
        },
        "headers": CIMultiDict(),
        "session": mock_session,
    }
    expected_args = ("POST", URL("https://ftx.com/api/orders"))
    expected_kwargs = {
        "data": aiohttp.payload.JsonPayload(
            {
                "market": "BTC-PERP",
                "side": "buy",
                "type": "market",
                "size": "0.01",
            }
        ),
        "headers": CIMultiDict(
            {
                "FTX-KEY": "J6vXtiZunV4lsRWoLHNYNiCa",
                "FTX-SIGN": (
                    "50d50ce69efc8e87bc8776511997544bdef4aad497c7506b26ac633f526363e3"
                ),
                "FTX-TS": "2085848896000",
            }
        ),
        "session": mock_session,
    }
    args = pybotters.auth.Auth.ftx(args, kwargs)
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
        URL("https://www.mexc.com/open/api/v2/order/open_orders?symbol=BTC_USDT"),
    )
    expected_kwargs = {
        "data": None,
        "headers": CIMultiDict(
            {
                "ApiKey": "0uVJRVNmR2ZHiCXtf6yEwrwy",
                "Request-Time": "2085848896000",
                "Signature": (
                    "3c167e16870239537bd4a1534af3d89f9341f7b94f3f8dfd3b94d0a23b5ab48c"
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
    expected_args = ("POST", URL("https://api.mexc.com/api/v3/order"))
    expected_kwargs = {
        "data": aiohttp.formdata.FormData(
            {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quoteOrderQty": "5",
                "timestamp": "2085848896000",
                "signature": (
                    "4b5e31a683df50d43d4e0774fafb869e1b4d517f8fdbff23c275092517c84161"
                ),
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
