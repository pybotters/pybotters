[![pytest](https://github.com/MtkN1/pybotters/actions/workflows/pytest.yml/badge.svg)](https://github.com/MtkN1/pybotters/actions/workflows/pytest.yml)

# [Preview] pybotters

An advanced api client for python botters.

## 📌 Description

`pybotters`は[仮想通貨botter](https://note.com/hht/n/n61e6ecefd059)向けのPythonライブラリです。

複数取引所に対応した非同期I/OのAPIクライアントであり、bot開発により素晴らしいDXを提供します。

## 👩‍💻👨‍💻 In development

`pybotters` は現在 ** **Previewバージョン** ** です。
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
    - 型ヒントのサポート

## 🏦 Exchanges

| Name | API auth | DataStore | API docs |
| --- | --- | --- | --- |
| Bybit | ✅ | ✅ | [Official](https://bybit-exchange.github.io/docs/inverse) |
| Binance | ✅ | ✅ | [Official](https://binance-docs.github.io/apidocs/spot/en/) |
| OKX | ✅ | ✅ | [Official](https://www.okx.com/docs-v5/en/) |
| Phemex | ✅ | ✅ | [Official](https://github.com/phemex/phemex-api-docs) |
| Bitget | ✅ | ✅ | [Official](https://bitgetlimited.github.io/apidoc/en/mix/) |
| MEXC | ✅ | WIP | [Official](https://mxcdevelop.github.io/APIDoc/) / [v3](https://mxcdevelop.github.io/apidocs/spot_v3_en/) |
| FTX | ✅ | ✅ | [Official](https://docs.ftx.com/) |
| KuCoin | ✅ | ✅ | [Official](https://docs.kucoin.com/) |
| BitMEX | ✅ | ✅ | [Official](https://www.bitmex.com/app/apiOverview) |
| bitFlyer | ✅ | ✅ | [Official](https://lightning.bitflyer.com/docs) |
| GMO Coin | ✅ | ✅ | [Official](https://api.coin.z.com/docs/) |
| Liquid | ✅ | WIP | [Official](https://document.liquid.com/) |
| bitbank | ✅ | ✅ | [Official](https://docs.bitbank.cc/) |
| Coincheck | ✅ | ✅ | [Official](https://coincheck.com/documents/exchange/api) |

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

        # WebSocket API (with defautl print handler)
        ws = await client.ws_connect(
            url='wss://stream.bybit.com/realtime',
            send_json={'op': 'subscribe', 'args': ['trade.BTCUSD', 'order', 'position']},
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
    'bybit': ['BYBIT_API_KEY', 'BYBIT_API_SECRET'],
    'binance': ['BINANCE_API_KEY', 'BINANCE_API_SECRET'],
}

async def main():
    async with pybotters.Client(apis=apis) as client:
        await client.post('https://api.bybit.com/v2/private/order/create', data={'symbol': 'BTCUSD', ...: ...})
        ...
        await client.post('https://dapi.binance.com/dapi/v1/order', data={'symbol': 'BTCUSD_PERP', ...: ...})
        ...
```

## 📖 Wiki

詳しい利用方法は👉[Wikiページへ](https://github.com/MtkN1/pybotters/wiki)

現在こちらにに移行中です👉[Read the Docs](https://pybotters.readthedocs.io/ja/latest/)

## 🗽 License

MIT

## 💖 Author

Twitter:
https://twitter.com/MtkN1XBt

Discord:
https://discord.com/invite/CxuWSX9U69