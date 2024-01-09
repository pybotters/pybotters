[
  ![PyPI](https://img.shields.io/pypi/v/pybotters)
  ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pybotters)
  ![PyPI - License](https://img.shields.io/pypi/l/pybotters)
](https://pypi.org/project/pybotters/)
[![Downloads](https://static.pepy.tech/badge/pybotters)](https://pepy.tech/project/pybotters)

[![pytest](https://github.com/MtkN1/pybotters/actions/workflows/pytest.yml/badge.svg)](https://github.com/MtkN1/pybotters/actions/workflows/pytest.yml)
[![publish](https://github.com/MtkN1/pybotters/actions/workflows/publish.yml/badge.svg)](https://github.com/MtkN1/pybotters/actions/workflows/publish.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/pybotters/badge/?version=latest)](https://pybotters.readthedocs.io/ja/latest/?badge=latest)

[![GitHub Repo stars](https://img.shields.io/github/stars/MtkN1/pybotters?style=social)](https://github.com/MtkN1/pybotters/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/MtkN1/pybotters?style=social)](https://github.com/MtkN1/pybotters/network/members)
[![Discord](https://img.shields.io/discord/832651305155297331?label=Discord&logo=discord&style=social)](https://discord.com/invite/CxuWSX9U69)


# pybotters

An advanced API client for python botters. This project is in Japanese.

## 📌 Description

`pybotters` は [仮想通貨 botter](https://note.com/hht/n/n61e6ecefd059) 向けの Python ライブラリです。

このライブラリは **HTTP / WebSocket API クライアント** です。 複数の取引所の認証処理に対応しており、簡単に Private API を利用できるため、素早くトレード bot を構築することができます。また、 WebSocket の接続機能とデータハンドラーにより、リアルタイムでの情報取得が可能です。これにより、高頻度トレード bot の構築に役立ちます。

## 🚀 Features

- ✨ HTTP / WebSocket Client
    - HTTP / WebSocket の自動認証
    - WebSocket の自動再接続、自動ハートビート
    - [`aiohttp`](https://docs.aiohttp.org/) ライブラリを基盤とした非同期 I/O
- ✨ DataStore
    - WebSocket メッセージのデータハンドラー
    - オーダーブックなどの差分データの結合処理
    - 軽量データモデルによる高速なデータ処理と参照
- ✨ Other Experiences
    - 型ヒントのサポート
    - `asyncio` を基盤とした非同期プログラミング
    - Discord コミュニティによるサポート

## 🏦 Exchanges

| Name | API auth | DataStore | API docs |
| --- | --- | --- | --- |
| Bybit | ✅ | ✅ | [Official](https://bybit-exchange.github.io/docs/v5/intro) |
| Binance | ✅ | ✅ | [Official](https://binance-docs.github.io/apidocs/spot/en/) |
| OKX | ✅ | ✅ | [Official](https://www.okx.com/docs-v5/en/) |
| Phemex | ✅ | ✅ | [Official](https://phemex-docs.github.io/) |
| Bitget | ✅ | ✅ | [Official](https://bitgetlimited.github.io/apidoc/en/mix/) |
| MEXC | ✅ | No support | [Official](https://mexcdevelop.github.io/apidocs/spot_v3_en/) |
| KuCoin | ✅ | ✅ | [Official](https://www.kucoin.com/docs/beginners/introduction) |
| BitMEX | ✅ | ✅ | [Official](https://www.bitmex.com/app/apiOverview) |
| bitFlyer | ✅ | ✅ | [Official](https://lightning.bitflyer.com/docs) |
| GMO Coin | ✅ | ✅ | [Official](https://api.coin.z.com/docs/) |
| bitbank | ✅ | ✅ | [Official](https://github.com/bitbankinc/bitbank-api-docs) |
| Coincheck | ✅ | ✅ | [Official](https://coincheck.com/ja/documents/exchange/api) |

## 🐍 Requires

Python 3.8+

## 🔧 Installation

From [PyPI](pybotters) (stable version):

```sh
pip install pybotters
```

From [GitHub](https://github.com/MtkN1/pybotters) (latest version):

```sh
pip install git+https://github.com/MtkN1/pybotters.git
```

## 📝 Usage

Example of bitFlyer API:

### HTTP API

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

#### New interface

pybotters v1.0+ **New interface - `fetch` API**

More simple request/response:

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
        async for msg in wsqueue.iter_msg():
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
                board = store.board.sorted()
                print({k: v[:1] for k, v in board.items()})


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
```

## 📖 Documentation

🔗 https://pybotters.readthedocs.io/ja/stable/

## 🗽 License

MIT

## 💖 Author

X:

[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/MtkN1XBt)](https://twitter.com/MtkN1XBt)

Discord:

[![Discord Widget](https://discord.com/api/guilds/832651305155297331/widget.png?style=banner3)](https://discord.com/invite/CxuWSX9U69)
