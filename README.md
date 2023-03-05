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


# [Preview] pybotters

An advanced API client for python botters.

## 📌 Description

`pybotters` は [仮想通貨 botter](https://note.com/hht/n/n61e6ecefd059) 向けの Python ライブラリです。

複数取引所に対応した非同期 I/O の API クライアントであり、bot 開発により素晴らしい DX を提供します。

## 🚧 In development

`pybotters` は現在 ** **Previewバージョン** ** です。
一部機能は開発中です。

開発状況については [こちら(Issues)](https://github.com/MtkN1/pybotters/issues) を参照してください。

## 🚀 Features

- ✨ HTTP / WebSocket Client
    - 複数取引所のプライベート API を自動認証
    - [`aiohttp`](https://docs.aiohttp.org/) ライブラリを基盤とした非同期通信
    - WebSocket の自動再接続、自動ハートビート
- ✨ DataStore
    - WebSocket 用のデータ保管クラス
    - ピュア Python データモデルによる高速なデータ参照
    - 取引所別モデルの実装
- ✨ Developer Experience
    - `asyncio` ライブラリを利用した非同期プログラミング
    - 型ヒントのサポート

## 🏦 Exchanges

| Name | API auth | DataStore | API docs |
| --- | --- | --- | --- |
| Bybit | ✅ | ✅ (Futures v2) | [Official v5](https://bybit-exchange.github.io/docs/v5/intro) / [Futures v2](https://bybit-exchange.github.io/docs-legacy/futuresV2/inverse/) |
| Binance | ✅ | ✅ | [Official](https://binance-docs.github.io/apidocs/spot/en/) |
| OKX | ✅ | ✅ | [Official](https://www.okx.com/docs-v5/en/) |
| Phemex | ✅ | ✅ | [Official](https://phemex-docs.github.io/) |
| Bitget | ✅ | ✅ | [Official](https://bitgetlimited.github.io/apidoc/en/mix/) |
| MEXC | ✅ | WIP | [Official](https://mxcdevelop.github.io/APIDoc/) / [v3](https://mxcdevelop.github.io/apidocs/spot_v3_en/) |
| KuCoin | ✅ | ✅ | [Official](https://docs.kucoin.com/) |
| BitMEX | ✅ | ✅ | [Official](https://www.bitmex.com/app/apiOverview) |
| bitFlyer | ✅ | ✅ | [Official](https://lightning.bitflyer.com/docs) |
| GMO Coin | ✅ | ✅ | [Official](https://api.coin.z.com/docs/) |
| bitbank | ✅ | ✅ | [Official](https://docs.bitbank.cc/) |
| Coincheck | ✅ | ✅ | [Official](https://coincheck.com/documents/exchange/api) |

## 🐍 Requires

Python 3.7+

## 🔧 Installation

```sh
pip install pybotters
```

## 🌏 Quickstart

### Single exchange

```python
import asyncio
import pybotters

apis = {
    "bybit": ["BYBIT_API_KEY", "BYBIT_API_SECRET"],
}

async def main():
    async with pybotters.Client(apis=apis, base_url="https://api.bybit.com") as client:
        # REST API
        resp = await client.get("/v2/private/position/list", params={"symbol": "BTCUSD"})
        data = await resp.json()
        print(data)

        # WebSocket API (with defautl print handler)
        ws = await client.ws_connect(
            url="wss://stream.bybit.com/realtime",
            send_json={"op": "subscribe", "args": ["trade.BTCUSD", "order", "position"]},
        )
        await ws # Ctrl+C to break

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
```

### Multiple exchanges

```python
apis = {
    "bybit": ["BYBIT_API_KEY", "BYBIT_API_SECRET"],
    "binance": ["BINANCE_API_KEY", "BINANCE_API_SECRET"],
}

async def main():
    async with pybotters.Client(apis=apis) as client:
        await client.post("https://api.bybit.com/v2/private/order/create", data={"symbol": "BTCUSD", ...: ...})
        ...
        await client.post("https://dapi.binance.com/dapi/v1/order", data={"symbol": "BTCUSD_PERP", ...: ...})
        ...
```

## 📖 Wiki

詳しい利用方法は 👉 [GitHub Wiki](https://github.com/MtkN1/pybotters/wiki)

現在こちらに移行中です 👉 [Read the Docs](https://pybotters.readthedocs.io/ja/latest/)

## 🗽 License

MIT

## 💖 Author

Twitter:

[![Twitter Follow](https://img.shields.io/twitter/follow/MtkN1XBt?style=social)](https://twitter.com/MtkN1XBt)

Discord:

[![Discord Widget](https://discord.com/api/guilds/832651305155297331/widget.png?style=banner2)](https://discord.com/invite/CxuWSX9U69)
