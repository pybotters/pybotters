## Usage of experimental version

### Migration of auth

`apis` 引数を Client から削除、 `auth` 引数を追加

- current version

```py
async def main():
    apis = {"exchange": ["key", "secret"]}
    async with pybotters.Client(apis=apis) as client:
        ...
```

- experimental version

```py
async def main():
    apis = {"exchange": ["key", "secret"]}
    async with pybotters.experimental.Client(auth=pybotters.experimental.Auth(apis)) as client:
        ...
```

### Single auth

単一の取引所認証クラスを追加

- current version

```py
"""not available"""
```

- experimental version

```py
async def main():
    auth = pybotters.experimental.FTXAuth(key="key", secret="secret")
    async with pybotters.experimental.Client(auth=auth) as client:
        ...
```

### Migration of ws_connect

引数 `hdlr_{str,bytes,json}` の名称を `receive_{str,bytes,json}` に変更、またハンドラーのリストの受け付け可能

- current version

```py
async def main():
    async with pybotters.Client() as client:
        await client.ws_connect(
            "wss://...",
            send_json={"...": "..."},
            hdlr_json=store.onmessage,
        )
```

- experimental version

```py
async def main():
    async with pybotters.experimental.Client() as client:
        await client.ws_connect(
            "wss://...",
            send_json={"...": "..."},
            receive_json=store.onmessage,
        )

        await client.ws_connect(
            "wss://...",
            send_json={"...": "..."},
            receive_json=[store.onmessage, print],
        )
```

### Event listener

1. `ws_connect` が `WebSocketApp` を返すように
1. `WebSocketApp` は pyee ライブラリの `AsyncIOEventEmitter` を継承している
1. `add_listener` メソッドなどが利用可能
1. `WebSocketApp` には `open` `message` `error` `close` のイベントを定義済み

- current version

```py
"""not available"""
```

- experimental version

```py
async def main():
    async with pybotters.experimental.Client() as client:
        ws = await client.ws_connect("wss://...")  # type: WebSocketApp
        ws.add_listener("message", print)
```

### WebSocketApp

1. `url` プロパティで再接続時の URL を編集可能
1. `closed` プロパティでコネクションの確認が可能
1. `send_{str,bytes,json}` メソッドで接続後にリクエスト可能
1. `receive_{str,bytes,json}` メソッドで単一データの取得が可能

### `await ws`

`await ws` の機能を `await ws.wait()` メソッドに変更

- current version

```py
async def main():
    async with pybotters.Client() as client:
        ws = await client.ws_connect("wss://...")
        await ws
```

- experimental version

```py
async def main():
    async with pybotters.experimental.Client() as client:
        ws = await client.ws_connect("wss://...")  # type: WebSocketApp
        await ws.wait()
```
