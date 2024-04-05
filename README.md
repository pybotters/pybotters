[
  ![PyPI](https://img.shields.io/pypi/v/pybotters)
  ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pybotters)
  ![PyPI - License](https://img.shields.io/pypi/l/pybotters)
](https://pypi.org/project/pybotters/)
[![Downloads](https://static.pepy.tech/badge/pybotters)](https://pepy.tech/project/pybotters)

[![CI](https://github.com/pybotters/pybotters/actions/workflows/ci.yml/badge.svg)](https://github.com/pybotters/pybotters/actions/workflows/ci.yml)
[![publish](https://github.com/pybotters/pybotters/actions/workflows/publish.yml/badge.svg)](https://github.com/pybotters/pybotters/actions/workflows/publish.yml)
[![codecov](https://codecov.io/gh/pybotters/pybotters/graph/badge.svg?token=ARR29R726W)](https://codecov.io/gh/pybotters/pybotters)
[![Documentation Status](https://readthedocs.org/projects/pybotters/badge/?version=latest)](https://pybotters.readthedocs.io/ja/latest/?badge=latest)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[![GitHub Repo stars](https://img.shields.io/github/stars/pybotters/pybotters?style=social)](https://github.com/pybotters/pybotters/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/pybotters/pybotters?style=social)](https://github.com/pybotters/pybotters/network/members)
[![Discord](https://img.shields.io/discord/832651305155297331?label=Discord&logo=discord&style=social)](https://discord.com/invite/CxuWSX9U69)
[![GitHub Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23db61a2.svg?&logo=github&logoColor=181717&&style=flat-square&labelColor=white)](https://github.com/sponsors/MtkN1)


# pybotters

![pybotters logo](https://raw.githubusercontent.com/pybotters/pybotters/main/docs/logo_150.png)

An advanced API client for python botters. This project is in Japanese.

## 📌 Description

`pybotters` is a Python library for [仮想通貨 botter (crypto bot traders)](https://medium.com/perpdex/botter-the-crypto-bot-trader-in-japan-2f5f2a65856f).

This library is an **HTTP and WebSocket API client**.
It has the following features, making it useful for developing a trading bot.

## 🚀 Features

- ✨ HTTP / WebSocket Client
    - **Automatic authentication** for private APIs.
    - WebSocket **automatic reconnection** and **automatic heartbeat**.
    - A client based on [`aiohttp`](https://docs.aiohttp.org/).
- ✨ DataStore
    - WebSocket message data handler.
    - **Processing of differential data** such as order book updates
    - **High-speed data processing** and querying
- ✨ Other Experiences
    - Support for type hints.
    - Asynchronous programming using [`asyncio`](https://docs.python.org/ja/3/library/asyncio.html).
    - Discord community.

## 🏦 Exchanges

| Name | API auth | DataStore | Exchange API docs |
| --- | --- | --- | --- |
| bitFlyer | ✅ | ✅ | [Link](https://lightning.bitflyer.com/docs) |
| GMO Coin | ✅ | ✅ | [Link](https://api.coin.z.com/docs/) |
| bitbank | ✅ | ✅ | [Link](https://github.com/bitbankinc/bitbank-api-docs) |
| Coincheck | ✅ | ✅ | [Link](https://coincheck.com/ja/documents/exchange/api) |
| Bybit | ✅ | ✅ | [Link](https://bybit-exchange.github.io/docs/v5/intro) |
| Binance | ✅ | ✅ | [Link](https://binance-docs.github.io/apidocs/spot/en/) |
| OKX | ✅ | ✅ | [Link](https://www.okx.com/docs-v5/en/) |
| Phemex | ✅ | ✅ | [Link](https://phemex-docs.github.io/) |
| Bitget | ✅ | ✅ | [Link](https://bitgetlimited.github.io/apidoc/en/mix/) |
| MEXC | ✅ | No support | [Link](https://mexcdevelop.github.io/apidocs/spot_v3_en/) |
| KuCoin | ✅ | ✅ | [Link](https://www.kucoin.com/docs/beginners/introduction) |
| BitMEX | ✅ | ✅ | [Link](https://www.bitmex.com/app/apiOverview) |

## 🐍 Requires

Python 3.8+

## 🔧 Installation

From [PyPI](https://pypi.org/project/pybotters/) (stable version):

```sh
pip install pybotters
```

From [GitHub](https://github.com/pybotters/pybotters) (latest version):

```sh
pip install git+https://github.com/pybotters/pybotters.git
```

## 📝 Usage

Example of bitFlyer API:

### HTTP API

New interface from version 1.0: **Fetch API**.

More simple request/response.

```py
import asyncio

import pybotters

apis = {
    "bitflyer": ["YOUER_BITFLYER_API_KEY", "YOUER_BITFLYER_API_SECRET"],
}


async def main():
    async with pybotters.Client(
        apis=apis, base_url="https://api.bitflyer.com"
    ) as client:
        # Fetch balance
        r = await client.fetch("GET", "/v1/me/getbalance")

        print(r.response.status, r.response.reason, r.response.url)
        print(r.data)

        # Create order
        CREATE_ORDER = False  # Set to `True` if you are trying to create an order.
        if CREATE_ORDER:
            r = await client.fetch(
                "POST",
                "/v1/me/sendchildorder",
                data={
                    "product_code": "BTC_JPY",
                    "child_order_type": "MARKET",
                    "side": "BUY",
                    "size": 0.001,
                },
            )

            print(r.response.status, r.response.reason, r.response.url)
            print(r.data)


asyncio.run(main())
```

aiohttp-based API.

```python
import asyncio

import pybotters

apis = {
    "bitflyer": ["YOUER_BITFLYER_API_KEY", "YOUER_BITFLYER_API_SECRET"],
}


async def main():
    async with pybotters.Client(
        apis=apis, base_url="https://api.bitflyer.com"
    ) as client:
        # Fetch balance
        async with client.get("/v1/me/getbalance") as resp:
            data = await resp.json()

        print(resp.status, resp.reason)
        print(data)

        # Create order
        CREATE_ORDER = False  # Set to `True` if you are trying to create an order.
        if CREATE_ORDER:
            async with client.post(
                "/v1/me/sendchildorder",
                data={
                    "product_code": "BTC_JPY",
                    "child_order_type": "MARKET",
                    "side": "BUY",
                    "size": 0.001,
                },
            ) as resp:
                data = await resp.json()

            print(data)


asyncio.run(main())
```

### WebSocket API

```python
import asyncio

import pybotters


async def main():
    async with pybotters.Client() as client:
        # Create a Queue
        wsqueue = pybotters.WebSocketQueue()

        # Connect to WebSocket and subscribe to Ticker
        await client.ws_connect(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            send_json={
                "method": "subscribe",
                "params": {"channel": "lightning_ticker_BTC_JPY"},
            },
            hdlr_json=wsqueue.onmessage,
        )

        # Iterate message (Ctrl+C to break)
        async for msg in wsqueue:
            print(msg)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
```

### DataStore

```py
import asyncio

import pybotters


async def main():
    async with pybotters.Client() as client:
        # Create DataStore
        store = pybotters.bitFlyerDataStore()

        # Connect to WebSocket and subscribe to Board
        await client.ws_connect(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            send_json=[
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_board_snapshot_BTC_JPY"},
                },
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_board_BTC_JPY"},
                },
            ],
            hdlr_json=store.onmessage,
        )

        # Watch for the best prices on Board. (Ctrl+C to break)
        with store.board.watch() as stream:
            async for change in stream:
                board = store.board.sorted(limit=2)
                print(board)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
```

## 📖 Documentation

🔗 https://pybotters.readthedocs.io/ja/stable/ (Japanese)

## 🗽 License

MIT

## 💖 Author

Please sponsor me!:

[![GitHub Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23db61a2.svg?&logo=github&logoColor=181717&&style=flat-square&labelColor=white)](https://github.com/sponsors/MtkN1)

X:

[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/MtkN1XBt)](https://twitter.com/MtkN1XBt)

Discord:

[![Discord Widget](https://discord.com/api/guilds/832651305155297331/widget.png?style=banner3)](https://discord.com/invite/CxuWSX9U69)
