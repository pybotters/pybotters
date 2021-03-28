# [BETA] pybotters

An advanced api client for python botters.

## 📌 Description

`pybotters`は[仮想通貨botter](https://note.com/hht/n/n61e6ecefd059)向けのPythonライブラリです。複数取引所に対応した非同期APIクライアントであり、bot開発により素晴らしいDXを提供します。

## 🚀 Features

- ✨HTTP / WebSocket Client
    - 複数取引所のプライベートAPIを自動署名
    - [aiohttp](https://docs.aiohttp.org/)ライブラリを基盤とした非同期通信
    - WebSocketの自動再接続、自動ハートビート
- ✨DataStore
    - WebSocket用の自動データ保管クラス
    - 参照渡しによる高速なデータ参照
    - 取引所別データモデルの実装
- ✨Developer Experience
    - `asyncio`ライブラリを利用した非同期プログラミング
    - `typing`モジュールによる型ヒントのサポート

## 🏦 Exchanges

| Name | API Client | DataStore | 
| --- | --- | --- |
| Bybit | ✅ | WIP |
| BTCMEX | ✅ | WIP |
| Binance | ✅ | WIP |
| bitFlyer | WIP | WIP |
| GMO Coin | WIP | WIP |
| Liquid | WIP | WIP |
| bitbank | WIP | WIP |
| FTX | WIP | WIP |
| BitMEX | WIP | WIP |

※表の順番は著者個人の優先度順です

## 🐍 Requires

Python 3.7+

## 🛠 Installation

```sh
pip install git+https://github.com/MtkN1/pybotters
```

## 🗽 License

MIT

## 💖Author

https://twitter.com/MtkN1XBt
