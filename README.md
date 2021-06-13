[![pytest](https://github.com/MtkN1/pybotters/actions/workflows/pytest.yml/badge.svg)](https://github.com/MtkN1/pybotters/actions/workflows/pytest.yml)

# [BETA] pybotters

An advanced api client for python botters.

## 📌 Description

`pybotters`は[仮想通貨botter](https://note.com/hht/n/n61e6ecefd059)向けのPythonライブラリです。

複数取引所に対応した非同期I/OのAPIクライアントであり、bot開発により素晴らしいDXを提供します。

## 👩‍💻👨‍💻 In development

`pybotters` は現在 ** **BETAバージョン** ** です。
一部機能は開発中です。

開発状況については [こちら(Issues)](https://github.com/MtkN1/pybotters/issues) を参照してください。

## 🚀 Features

- ✨ HTTP / WebSocket Client
    - 複数取引所のプライベートAPIを自動認証
    - [`aiohttp`](https://docs.aiohttp.org/)ライブラリを基盤とした非同期通信
    - WebSocketの自動再接続、自動ハートビート
- ✨ DataStore
    - WebSocket用の自動データ保管クラス
    - 参照渡しによる高速なデータ参照
    - 取引所別データモデルの実装
- ✨ Developer Experience
    - `asyncio`ライブラリを利用した非同期プログラミング
    - `typing`モジュールによる型ヒントのサポート

## 🏦 Exchanges

| Name | API auth | DataStore | API docs |
| --- | --- | --- | --- |
| Bybit | ✅ | ✅ | [LINK](https://bybit-exchange.github.io/docs/inverse) |
| Binance | ✅ | ✅(USDⓈ-M) | [LINK](https://binance-docs.github.io/apidocs/spot/en/) |
| FTX | ✅ | ✅ | [LINK](https://docs.ftx.com/) |
| BTCMEX | ✅ | ✅ | [LINK](https://help.btcmex.com/hc/ja/articles/360035945452-API) |
| BitMEX | ✅ | WIP | [LINK](https://www.bitmex.com/app/apiOverview) |
| bitFlyer | ✅ | WIP | [LINK](https://lightning.bitflyer.com/docs) |
| GMO Coin | ✅ | WIP | [LINK](https://api.coin.z.com/docs/) |
| Liquid | ✅ | WIP | [LINK](https://document.liquid.com/) |
| bitbank | ✅ | WIP | [LINK](https://docs.bitbank.cc/) |

## 🐍 Requires

Python 3.7+

## 🛠 Installation

```sh
pip install pybotters
```

## 🔰 Usage

### Single exchange

```python
import asyncio
import pybotters

apis = {
    'bybit': ['BYBIT_API_KEY', 'BYBIT_API_SECRET'],
}

async def main():
    async with pybotters.Client(apis=apis, base_url='https://api.bybit.com') as client:
        # REST API
        resp = await client.get('/v2/private/position/list', params={'symbol': 'BTCUSD'})
        data = await resp.json()
        print(data)

        # WebSocket API (with print handler)
        ws = await client.ws_connect(
            url='wss://stream.bybit.com/realtime',
            send_json={'op': 'subscribe', 'args': ['trade.BTCUSD', 'order', 'position']},
            hdlr_json=lambda msg, ws: print(msg),
        )
        await ws # this await is wait forever (for usage)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
```

### Multiple exchanges

```python
apis = {
    'bybit': ['BYBIT_API_KEY', 'BYBIT_API_SECRET'],
    'btcmex': ['BTCMEX_API_KEY', 'BTCMEX_API_SECRET'],
    'binance': ['BINANCE_API_KEY', 'BINANCE_API_SECRET'],
}

async def main():
    async with pybotters.Client(apis=apis) as client:
        await client.post('https://api.bybit.com/v2/private/order/create', data={'symbol': 'BTCUSD', ...: ...})
        ...
        await client.post('https://www.btcmex.com/api/v1/order', data={'symbol': 'XBTUSD', ...: ...})
        ...
        await client.post('https://dapi.binance.com/dapi/v1/order', data={'symbol': 'BTCUSD_PERP', ...: ...})
        ...
```

## 📖 Wiki

詳しい利用方法は👉[Wikiページへ](https://github.com/MtkN1/pybotters/wiki)

## 🗽 License

MIT

## 💖 Author

https://twitter.com/MtkN1XBt
