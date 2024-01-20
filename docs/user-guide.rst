User Guide
==========

Client class
------------

:class:`pybotters.Client` は HTTP リクエストを行う為のメインクラスです。

:class:`~.Client` のインスタンスを生成するには非同期コンテキストマネージャー ``async with`` を利用します。

.. code:: python

    import asyncio

    import pybotters


    async def main():
        async with pybotters.Client() as client:
            ...


    asyncio.run(main())

:class:`~.Client` インスタンスのメソッドから HTTP リクエストと WebSocket 接続を利用することができます。


HTTP API
-------------

.. _fetch-api:

Fetch API
~~~~~~~~~

:meth:`pybotters.Client.fetch` メソッドで HTTP リクエストを作成します。

.. code-block:: python

    async def main():
        async with pybotters.Client() as client:
            result = await client.fetch(
                "GET",
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            )
            print(result.data)

:ref:`Fetch API <fetch-api>` は従来の :ref:`HTTP メソッド API <http-method-api>` と比較して、シンプルなインターフェースです。

一度の ``await`` 式で HTTP レスポンスデータの JSON デコードまで行います。
返り値は :class:`~.FetchResult` となっており、デコードされた JSON データは :attr:`~.FetchResult.data` 属性から参照できます。

.. versionadded:: 1.0

.. _http-method-api:

HTTP method API
~~~~~~~~~~~~~~~

従来の :ref:`HTTP メソッド API <http-method-api>` で HTTP リクエストを作成します。

* :meth:`pybotters.Client.request`
* :meth:`pybotters.Client.get`
* :meth:`pybotters.Client.post`
* :meth:`pybotters.Client.put`
* :meth:`pybotters.Client.delete`

.. code-block:: python

    async def main():
        async with pybotters.Client() as client:
            async with client.request(
                "GET",
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            ) as resp:
                data = await resp.json()
            print(data)

            async with client.get(
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            ) as resp:
                data = await resp.json()
            print(data)


WebSocket API
-------------

:meth:`pybotters.Client.ws_connect` メソッドで WebSocket 接続を作成します。

:meth:`~.Client.ws_connect` メソッドは ``asyncio`` の機能を利用して非同期で WebSocket コネクションを作成します。

.. code-block:: python

    async def main():
        async with pybotters.Client() as client:
            ws = await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "lightning_ticker_BTC_JPY"},
                },
                hdlr_json=lambda msg, ws: print(msg),
            )
            await ws.wait()  # Ctrl+C to break

* WebSocket メッセージの送信
    ``send_str``, ``send_bytes``, ``send_json`` 引数で送信する WebSocket メッセージを指定します。
    上記のコードでは ``hello`` というメッセージを送信しています。
* WebSocket メッセージの受信
    ``hdlr_str``, ``hdlr_bytes``, ``hdlr_json`` 引数で受信した WebSocket メッセージのハンドラ (コールバック) を指定します。
    指定するハンドラは第 1 引数 ``msg: aiohttp.WSMessage`` 第 2 引数 ``ws: aiohttp.ClientWebSocketResponse`` を取る必要があります。
    上記のコードでは無名関数をハンドラに指定して WebSocket メッセージを標準出力しています。

    pybotters には組み込みの便利なハンドラ :class:`pybotters.WebSocketQueue` クラスや、仮想通貨取引所固有の WebSocket データを扱う :ref:`DataStore <datastore>` があります。
* 再接続
    さらに :meth:`~.Client.ws_connect` メソッドで作成した WebSocket 接続は **自動再接続** の機能を備えています。 これにより切断を意識することなく継続的にデータの取得が可能です。


Exchange authentication
-----------------------

仮想通貨取引所の Private API を利用するには、API キー・シークレットによるユーザー認証が必要です。

pybotters では :class:`~.Client` クラスの引数 ``apis`` に API 情報を渡すことで認証処理を自動的に行うことができます。
以下のコードでは pybotters の自動認証を利用して bitFlyer の Private API で資産残高の取得 (``/v1/me/getbalance``) のリクエストを作成します。

.. code:: python

    async def main():
        apis = {
            "bitflyer": ["BITFLYER_API_KEY", "BITFLYER_API_SECRET"],
        }
        async with pybotters.Client(apis=apis) as client:
            result = await client.fetch("GET", "https://api.bitflyer.com/v1/me/getbalance")
            print(result.data)

まるで Publib API かのように Private API をリクエストできました！

もちろん、WebSocket API でも自動的に認証処理が行われます。
以下のコードでは bitFlyer の Private WebSocket API で注文イベント (``child_order_events``) を購読します。

.. code:: python

    async def main():
        apis = {
        "bitflyer": ["BITFLYER_API_KEY", "BITFLYER_API_SECRET"],
        }
        async with pybotters.Client(apis=apis) as client:
            ws = await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "child_order_events"},
                    "id": 123,
                },
                hdlr_json=lambda msg, ws: print(msg),
            )
            await ws.wait()  # Ctrl+C to break

.. warning::
    コード上に API 情報をハードコードすることはセキュリティリスクがあります。
    ドキュメント上は説明の為にハードコードしていますが、実際は環境変数を利用して ``os.getenv`` などから取得することを推奨します。

.. または、API情報をJSON形式で保存している場合、ディレクトリパスを渡すことで読み込むことが可能です。

.. ``api.json``

.. .. code:: json

..    {
..        "bybit": ["BYBIT_API_KEY", "BYBIT_API_SECRET"],
..        "binance": ["BINANCE_API_KEY", "BINANCE_API_SECRET"],
..        "....": ["...", "..."]
..    }

.. .. code:: python

..    async def main():
..        async with pybotters.Client(apis='apis.json') as client:
..            ...

.. _api-name:


引数 ``apis`` の形式は以下のような辞書形式です。

.. code-block:: python

    {
        "API_NAME": [
            "YOUR_API_KEY",
            "YOUR_API_SECRET",
            # "API_PASSPHRASE",  # Optional
        ],
        "...": ["...", "..."],
    }

pybotters の自動認証が対応している取引所の API 名はこちらの表から設定します。

========================= =========================
Exchange                  API name
========================= =========================
Binance                   ``binance``
Binance Testsnet (Future) ``binancefuture_testnet``
Binance Testsnet (Spot)   ``binancespot_testnet``
bitbank                   ``bitbank``
bitFlyer                  ``bitflyer``
Bitget                    ``bitget``
BitMEX                    ``bitmex``
BitMEX Testnet            ``bitmex_testnet``
Bybit                     ``bybit``
Bybit Testnet             ``bybit_testnet``
Coincheck                 ``coincheck``
GMO Coin                  ``gmocoin``
KuCoin                    ``kucoin``
MECX                      ``mexc``
OKX                       ``okx``
OKX Demo trading          ``okx_demo``
Phemex                    ``phemex``
Phemex Testnet            ``phemex_testnet``
========================= =========================


.. _datastore:

DataStore
---------

:ref:`DataStore <datastore>` を利用することで、WebSocket のデータを簡単に処理・参照ができます。

* データの参照
    * :meth:`pybotters.DataStore.get`
    * :meth:`pybotters.DataStore.find`
* データの参照 (特殊)
    * :meth:`pybotters.DataStore.sorted` (※板情報系のみ)
* データの待機
    * :meth:`pybotters.DataStore.wait`
* データのストリーム
    * :meth:`pybotters.DataStore.watch`
* データのハンドリング
    * :meth:`pybotters.DataStoreManager.onmessage`

.. note::
    仮想通貨取引所の WebSocket API ではリアルタイムで配信されるマーケットやアカウントのデータを取得できます。
    しかし WebSocket で配信されるデータは、差分データとなっている場合があります。
    例えば、板情報であればは配信されるのは更新された価格と数量だけ、アカウントの注文情報であれば配信されるのは更新された注文 ID の情報だけ、などです。
    その場合は、事前に全体のデータを保持しておいて、差分データを受信したら追加／更新／削除の処理をする必要があります。

    pybotters でそれを実現するのが :ref:`DataStore <datastore>` です。
    pybotters では取引所固有の :ref:`DataStore <datastore>` が実装されています。

    :ref:`DataStore <datastore>` は「ドキュメント指向データベース」のような機能とデータ構造を持っています。

以下に :ref:`DataStore <datastore>` のデータ構造と :meth:`~.DataStore.get` 及び :meth:`~.DataStore.find` によるデータ取得方法を示します。

>>> ds = pybotters.DataStore(
...     keys=["id"],
...     data=[
...         {"id": 1, "data": "foo"},
...         {"id": 2, "data": "bar"},
...         {"id": 3, "data": "baz"},
...         {"id": 4, "data": "foo"},
...     ],
... )
>>> print(ds.get({"id": 1}))
{'id': 1, 'data': 'foo'}
>>> print(ds.get({"id": 999}))
None
>>> print(ds.find())
[{'id': 1, 'data': 'foo'}, {'id': 2, 'data': 'bar'}, {'id': 3, 'data': 'baz'}, {'id': 4, 'data': 'foo'}]
>>> print(ds.find({"data": "foo"}))
[{'id': 1, 'data': 'foo'}, {'id': 4, 'data': 'foo'}]

.. note::
    :class:`~.DataStore` クラス単体ではあまり役に立ちません。 トレード bot などでは、次の取引所固有の DataStore を利用します。

Exchange-specific DataStore
---------------------------

取引所固有の :ref:`DataStore <datastore>` は :class:`~.DataStoreManager` を継承しており、
その取引所の WebSocket チャンネルを表す :class:`~.DataStore` が複数のプロパティとして定義されています。

:class:`~.DataStoreManager` と :class:`~.DataStore` の関係を一般的な RDB システムに例えると
「データベース」と「テーブル」のようなものです。 「データベース」には複数の「テーブル」が存在しており、「テーブル」にはデータの実体があります。

例:

* :class:`pybotters.bitFlyerDataStore` (bitFlyer の WebSocket データをハンドリングする :class:`~.DataStoreManager`)
    * :attr:`~.bitFlyerDataStore.ticker` (bitFlyer の Ticker チャンネルをハンドリングする :class:`~.DataStore`)
    * :attr:`~.bitFlyerDataStore.executions` (bitFlyer の約定履歴チャンネルをハンドリングする :class:`~.DataStore`)
    * :attr:`~.bitFlyerDataStore.board` (bitFlyer の板情報チャンネルをハンドリングする :class:`~.DataStore`)
    * ...

次に :class:`~.bitFlyerDataStore` で Ticker、約定履歴、板情報、を利用する例を説明します。

Ticker
~~~~~~

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            store = pybotters.bitFlyerDataStore()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "lightning_ticker_BTC_JPY"},
                    "id": 1,
                },
                hdlr_json=store.onmessage,
            )

            while True:  # Ctrl+C to break
                ticker = store.ticker.get({"product_code": "BTC_JPY"})
                print(ticker)

                await store.ticker.wait()

* :class:`~.bitFlyerDataStore` のインスタンスを生成します。
* :meth:`~.Client.ws_connect` の引数 ``send_json`` に Ticker の購読メッセージを渡します。
* :meth:`~.Client.ws_connect` の引数 ``hdlr_json`` に :class:`~.bitFlyerDataStore` のコールバック :meth:`~.DataStoreManager.onmessage` を渡します。
* :meth:`~.DataStore.get` で ``BTC_JPY`` の Ticker を取得して標準出力します。
* :meth:`~.DataStore.wait` で Ticker の更新を待機します。
* WebSocket によりデータが非同期で受信しているので :meth:`~.DataStore.get` による Ticker の取得はループごとに異なる値にはるはずです。

.. note::
    :meth:`~.DataStore.get` は最初は ``None`` が出力されるはずです。
    これは WebSocket は非同期でデータがやりとりされていることを意味します。
    トレード bot のロジックで WebSocket のデータを扱うには、:meth:`~.DataStore.wait` を用いて初期データを受信しておくことが重要です。

または複数銘柄のデータがあるなどの場合は :meth:`~.DataStore.find` でストア内の全てのデータを取得できます。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            store = pybotters.bitFlyerDataStore()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json=[
                    {
                        "method": "subscribe",
                        "params": {"channel": "lightning_ticker_BTC_JPY"},
                        "id": 1,
                    },
                    {
                        "method": "subscribe",
                        "params": {"channel": "lightning_ticker_ETH_JPY"},
                        "id": 2,
                    },
                ],
                hdlr_json=store.onmessage,
            )

            while True:  # Ctrl+C to break
                tickers = store.ticker.find()
                print(tickers)

                await store.ticker.wait()

Execution History
~~~~~~~~~~~~~~~~~

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            store = pybotters.bitFlyerDataStore()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "lightning_executions_BTC_JPY"},
                    "id": 1,
                },
                hdlr_json=store.onmessage,
            )

            with store.executions.watch() as stream:
                async for change in stream:  # Ctrl+C to break
                    print(change.data)

* :class:`~.bitFlyerDataStore` のインスタンスを生成します。
* :meth:`~.Client.ws_connect` の引数 ``send_json`` に約定履歴の購読メッセージを渡します。
* :meth:`~.Client.ws_connect` の引数 ``hdlr_json`` に :class:`~.bitFlyerDataStore` のコールバック :meth:`~.DataStoreManager.onmessage` を渡します。
* :meth:`~.DataStore.watch` で約定履歴の変更ストリーム :class:`~.StoreStream` を開きます。
* ``async for`` で変更ストリームをイテレートして変更クラス :class:`~.StoreChange` を取得します。
* 約定履歴の変更ストリームは、約定履歴の追加 (``insert``) ごとにイテレートされます。 つまり取引所で約定が発生するごとに ``async for`` がループします。
    * 変更ストリームは他に更新 (``update``) 削除 (``delete``) イベントが存在します。 更新、削除が行われる板情報や注文などのストアで発生します。

.. note::
    取引所において約定が発生するまでデータは出力されません。 約定がない場合は時間をおいて確認してみてください。

Order Book
~~~~~~~~~~

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            store = pybotters.bitFlyerDataStore()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json=[
                    {
                        "method": "subscribe",
                        "params": {"channel": "lightning_board_snapshot_BTC_JPY"},
                        "id": 1,
                    },
                    {
                        "method": "subscribe",
                        "params": {"channel": "lightning_board_BTC_JPY"},
                        "id": 2,
                    },
                ],
                hdlr_json=store.onmessage,
            )

            while True:  # Ctrl+C to break
                board = store.board.sorted()
                board_10 = board["SELL"][:5][::-1] + board["BUY"][:5]
                if board_10:
                    print(*board_10, sep="\n", end="\n\n")

                await asyncio.sleep(1.0)

* :class:`~.bitFlyerDataStore` のインスタンスを生成します。
* :meth:`~.Client.ws_connect` の引数 ``send_json`` に板情報 (スナップショットと差分) の購読メッセージを渡します。
* :meth:`~.Client.ws_connect` の引数 ``hdlr_json`` に :class:`~.bitFlyerDataStore` のコールバック :meth:`~.DataStoreManager.onmessage` を渡します。
* :meth:`~.bitFlyerDataStore.sorted` で Asks / Bids 別の板情報を形成します。
* Asks / Bids ベスト 5 (合計 10 行) の板情報を作成して標準出力します。


WebSocketQueue
--------------

DataStore が実装されていない取引所であったり、自らの実装でデータを処理したい場合は :class:`~.WebSocketQueue` を利用できます。

.. code-block:: python

    async def main():
        async with pybotters.Client() as client:
            wsqueue = pybotters.WebSocketQueue()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "lightning_ticker_BTC_JPY"},
                },
                hdlr_json=wsqueue.onmessage,
            )

            async for msg in wsqueue:  # Ctrl+C to break
                print(msg)


Differences from aiohttp
------------------------

aiohttp との違いについて。

pybotters は `aiohttp <https://pypi.org/project/aiohttp/>`_ を基盤として利用しているライブラリです。

その為、:class:`pybotters.Client` におけるインターフェースの多くは ``aiohttp.ClientSession`` と同様です。
また pybotters の HTTP リクエストのレスポンスクラスは aiohttp のレスポンスクラスを返します。

aiohttp ライブラリを理解することは pybotters の理解に繋がります。

ただし幾つかの違いも存在します。

- pybotters は HTTP リクエストの自動認証機能により、自動的に HTTP ヘッダーなどを編集します。
- POST リクエストのデータは ``data`` に渡します。 aiohttp では ``json`` 引数を許可しますが pybotters では許可されません。 これは認証機能による都合です。
- :meth:`pybotters.Client.fetch` は pybotters 独自の API です。 aiohttp には存在しません。
- :meth:`pybotters.Client.ws_connect` は aiohttp にも存在しますが、再接続機能などを備えた pybotters 独自の API です。
