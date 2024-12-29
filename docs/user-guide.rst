User Guide
==========

Client class
------------

:class:`pybotters.Client` は HTTP リクエストを行う為のメインクラスです。
:class:`.Client` の利用を開始するにはいくつかのステップが必要です。

1. :mod:`asyncio` と :mod:`pybotters` を ``import`` する
2. 非同期関数を *async def* で定義する
3. 定義した非同期関数の中から *async with* ブロックで :class:`.Client` インスタンスを初期化する

.. code:: python

    import asyncio

    import pybotters


    async def main():
        async with pybotters.Client() as client:
            ...


    asyncio.run(main())

準備は整いましたか？
:class:`.Client` インスタンスのメソッドから、以降に説明する HTTP リクエストと WebSocket 接続の機能を利用することができます。

.. note::

    pybotters の中核機能は `asyncio <https://docs.python.org/ja/3/library/asyncio.html>`_ と `aiohttp <https://docs.aiohttp.org/en/stable/client_quickstart.html>`__ の上に構築されています。
    それらの知識が全くないと、このユーザーガイドを進めるのは難しいかもしれません。

    asyncio と aiohttp を掻い摘んで理解するには、著者によるこちらの記事がおすすめです。

    botterのためのasyncio
    https://zenn.dev/mtkn1/articles/c61e77c1d221aa

.. note::

    このユーザーガイドの以降で説明する HTTP / WebSocket API には、仮想通貨取引所 bitFlyer の API を例として利用します。
    ただし bitFlyer API の詳しい内容は説明を行いません。
    公式ドキュメントをご確認ください。

    https://lightning.bitflyer.com/docs


HTTP API
-------------

.. _fetch-api:

Fetch API
~~~~~~~~~

:meth:`.Client.fetch` メソッドで HTTP リクエストを作成します。

:ref:`Fetch API <fetch-api>` は従来の :ref:`HTTP メソッド API <http-method-api>` と比較して、シンプルなリクエスト／レスポンスのフローを提供します。
一度の ``await`` 式で HTTP レスポンスデータの JSON デコードまで行います。

.. code-block:: python

    async def main():
        async with pybotters.Client() as client:
            result = await client.fetch(
                "GET",
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            )
            print(result.response.status, result.response.reason)
            print(result.data)


第 1 引数 (``method``) は HTTP メソッドです。 文字列で ``"GET"`` ``"POST"`` 等の HTTP メソッドを指定します。
第 2 引数 (``url``) はリクエストの URL です。 文字列で指定します。

返り値は :class:`.FetchResult` です。
:attr:`.FetchResult.response` 属性には `aiohttp.ClientResponse <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientResponse>`_ が格納されており、
:attr:`.FetchResult.data` 属性にはデコードされた JSON データが格納されています。

.. versionadded:: 1.0

.. _http-method-api:

HTTP method API
~~~~~~~~~~~~~~~

従来の :ref:`HTTP メソッド API <http-method-api>` で HTTP リクエストを作成します。

:ref:`HTTP メソッド API <http-method-api>` でリクエストを開始するには *async with* ブロックを利用します。
こちらは従来の `aiohttp.ClientSession <https://docs.aiohttp.org/en/stable/client_reference.html#client-session>`_ と同様のリクエスト／レスポンスのフローになります。

* :meth:`.Client.request`
* :meth:`.Client.get`
* :meth:`.Client.post`
* :meth:`.Client.put`
* :meth:`.Client.delete`

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

まず *async with* ブロックの返り値によってレスポンス `aiohttp.ClientResponse <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientResponse>`_ を受信します。
このレスポンスは HTTP ヘッダーまでとなります。
そして *async* :meth:`json` メソッドを ``await`` するによって残りの HTTP 本文が受信され、データが JSON としてデコードされた値が返ります。

Request parameters
~~~~~~~~~~~~~~~~~~

HTTP リクエストのパラメーターは ``params`` 引数または ``data`` 引数に指定します。

``params`` 引数は「**URL クエリ文字列**」です。
主に ``GET`` リクエストに利用します。
ただし一部の仮想通貨取引所 API においては ``POST PUT DELETE`` リクエストでも利用することがあります。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            result = await client.fetch(
                "GET",
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            )
            print(r.response.status, r.response.reason)
            print(result.data)

``data`` 引数は「**HTTP 本文**」です。
主に ``POST`` リクエストで送信する JSON データとして利用します。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            result = await client.fetch(
                "POST",
                "https://api.bitflyer.com/v1/me/sendchildorder",
                data={"product_code": "BTC_JPY", "child_order_type": "MARKET", "size": 0.01},
            )  # NOTE: Authentication is required
            print(r.response.status, r.response.reason)
            print(result.data)

これらの仕様は :ref:`Fetch API <fetch-api>` と :ref:`HTTP メソッド API <http-method-api>` の間でも同様です。

.. note::

    この例は bitFlyer の「新規注文を出す」 API です。 実際にこれをリクエストするには自動認証 :ref:`authentication` が必要です。

.. warning::

    aiohttp の知識がある方は JSON データの POST リクエストに ``json`` 引数を使おうとするかもしれません。
    **しかし pybotters では** ``json`` **引数は利用できません** 。
    これは pybotters の自動認証処理による影響です。
    対応する取引所では ``data`` 引数を指定すると適切な JSON またはフォームなどの Content-Type が設定されます。

Response headers and data
~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`Fetch API <fetch-api>` の戻り値におけるオブジェクト属性 :attr:`.FetchResult.response` と、
:ref:`HTTP メソッド API <http-method-api>` の戻り値は共に `aiohttp.ClientResponse <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientResponse>`_ です。

HTTP レスポンスヘッダーについては、 ``headers`` 属性から取得できます。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            # Fetch API
            r = await client.fetch(
                "GET",
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            )
            print(r.response.headers)

            # HTTP method API
            async with client.get(
                "https://api.bitflyer.com/v1/getticker", params={"product_code": "BTC_JPY"}
            ) as resp:
                print(resp.headers)

HTTP レスポンスの JSON データについては、:ref:`Fetch API <fetch-api>` と :ref:`HTTP メソッド API <http-method-api>` にある説明の通りです。
:ref:`Fetch API <fetch-api>` では :attr:`.FetchResult.data` に格納されており、 :ref:`HTTP メソッド API <http-method-api>` では *async* :meth:`json` メソッドを ``await`` することで取得できます。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            # Fetch API
            r = await client.fetch(
                "GET",
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            )
            print(r.data)

            # HTTP method API
            async with client.get(
                "https://api.bitflyer.com/v1/getticker", params={"product_code": "BTC_JPY"}
            ) as resp:
                data = await resp.json()
                print(data)

Base URL
--------

:class:`.Client` の引数 ``base_url`` を設定することで、取引所 API エンドポイントのベース URL を省略して HTTP リクエストができます。

``base_url`` を設定した場合、HTTP リクエストでは続きの相対 URL パスを設定します。

.. code:: python

    async def main():
        async with pybotters.Client(base_url="https://api.bitflyer.com") as client:
            r = await client.fetch("GET", "/v1/getticker")
            r = await client.fetch("GET", "/v1/getboard")

            await client.ws_connect("wss://ws.lightstream.bitflyer.com/json-rpc")  # Base URL is not applicable

ただし pybotters では WebSocket API の URL には ``base_url`` は適用しません。
これは基本的に取引所の HTTP API と WebSocket API のベース URL が異なっている為であり、殆どの場合で期待される動作です。


.. _websocket-api:

WebSocket API
-------------

:meth:`.Client.ws_connect` メソッドで WebSocket 接続を作成します。

このメソッドは :mod:`asyncio` の機能により非同期で WebSocket コネクションを作成します。

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

    これらの引数は送信するメッセージをリストで括ることで複数のメッセージを送信できます (:ref:`multiple-websocket-senders-handlers`) 。
* WebSocket メッセージの受信
    ``hdlr_str``, ``hdlr_bytes``, ``hdlr_json`` 引数で受信した WebSocket メッセージのハンドラ (コールバック) を指定します。
    指定するハンドラは第 1 引数 ``msg: aiohttp.WSMessage`` 第 2 引数 ``ws: aiohttp.ClientWebSocketResponse`` を取る必要があります。
    上記のコードでは無名関数をハンドラに指定して WebSocket メッセージを標準出力しています。

    pybotters には組み込みのハンドラとして、汎用性の高い :ref:`websocketqueue` や、 :ref:`取引所固有の DataStore <exchange-specific-datastore>` があります。

    これらの引数はハンドラをリストで括ることで複数のハンドラを指定できます (:ref:`multiple-websocket-senders-handlers`) 。
* 再接続
    さらに :meth:`.Client.ws_connect` メソッドで作成した WebSocket 接続は **自動再接続** の機能を備えています。 これにより切断を意識することなく継続的にデータの取得が可能です。

戻り値は :class:`.WebSocketApp` です。 このクラスを利用して WebSocket のコネクションを操作できます。
上記の例では :meth:`.WebSocketApp.wait` メソッドで WebSocket の終了を待つことでプログラムの終了を防いでいます。

.. note::

    :class:`.WebSocketApp` はに自動再接続の機構があります。 その為 :meth:`.WebSocketApp.wait` の待機は **実質的に無限待機です** 。
    トレード bot ではなく、データ収集スクリプトなどのユースケースではハンドラに全ての処理を任せる場合があります。
    そうした時に :meth:`.WebSocketApp.wait` はプログラムの終了を防ぐのに役に立ちます。


.. _authentication:

Authentication
--------------

仮想通貨取引所の Private API を利用するには、API キー・シークレットによるユーザー認証が必要です。

pybotters では :class:`.Client` クラスの引数 ``apis`` に API 認証情報を渡すことで、認証処理が自動的に行われます。

以下のコードでは自動認証を利用して bitFlyer の Private API で資産残高の取得 (``/v1/me/getbalance``) のリクエストを作成します。

.. code:: python

    async def main():
        apis = {
            "bitflyer": ["BITFLYER_API_KEY", "BITFLYER_API_SECRET"],
        }
        async with pybotters.Client(apis=apis) as client:
            result = await client.fetch("GET", "https://api.bitflyer.com/v1/me/getbalance")
            print(result.data)

まるで Public API かのように Private API をリクエストを作成できます！

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
    コード上に API 認証情報をハードコードすることはセキュリティリスクがあります。
    ドキュメント上は説明の為にハードコードしていますが、実際は環境変数を利用して ``os.getenv`` などから取得することを推奨します。

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
Binance Testnet (Future)  ``binancefuture_testnet``
Binance Testnet (Spot)    ``binancespot_testnet``
bitbank                   ``bitbank``
bitFlyer                  ``bitflyer``
Bitget                    ``bitget``
BitMEX                    ``bitmex``
BitMEX Testnet            ``bitmex_testnet``
Bybit                     ``bybit``
Bybit Demo trading        ``bybit_demo``
Bybit Testnet             ``bybit_testnet``
Coincheck                 ``coincheck``
GMO Coin                  ``gmocoin``
Hyperliquid               ``hyperliquid``
Hyperliquid Testnet       ``hyperliquid_testnet``
KuCoin                    ``kucoin``
MECX                      ``mexc``
OKX                       ``okx``
OKX Demo trading          ``okx_demo``
Phemex                    ``phemex``
Phemex Testnet            ``phemex_testnet``
OKJ                       ``okj``
BitTrade                  ``bittrade``
========================= =========================

また ``apis`` 引数に辞書オブジェクトではなく代わりに **JSON ファイルパス** を文字列として渡すことで、pybotters はその JSON ファイルを読み込みます。

.. code:: python

    async def main():
        async with pybotters.Client(apis="/path/to/apis.json") as client:
            ...

さらに :ref:`implicit-loading-of-apis` では、独自の環境変数などを利用して ``apis`` 引数の指定を省略して API 認証情報のハードコードを避けることができます。

.. _datastore:

DataStore
---------

:ref:`datastore` を利用することで WebSocket からのデータを簡単に処理、参照ができます。

:ref:`datastore` は「ドキュメント指向データベース」のような機能とデータ構造を持っています。
以下はデータを参照する為のメソッド :meth:`.DataStore.get` と :meth:`.DataStore.find` の利用例です。

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
>>> print(ds.find({"id": "SPAM"}))
[]

* :meth:`.DataStore.get`
    * DataStore のキーを指定して一意のアイテム (1 件の辞書) を取得します
    * 一致するアイテムがない場合 ``None`` が返されます
* :meth:`.DataStore.find`
    * アイテムをリストで取得します
    * クエリを指定しない場合全てのデータを取得されます
    * クエリを指定すると条件のデータのみを取得します。 一致するアイテムがない場合は空のリストが返されます

ただし基本的に **DataStore クラスをそのまま利用するケースはありません**。

上記の例では :meth:`.DataStore.get` と :meth:`.DataStore.find` の説明の為に DataStore をそのまま利用しました。
基本的なユースケースでは次の :ref:`取引所固有の DataStore <exchange-specific-datastore>` を利用します。
そこで格納されたデータを参照する方法として上記のメソッドを覚えておく必要があります。

.. note::
    DataStore は、仮想通貨取引所の WebSocket API から高頻度で配信されるリアルタイムデータを処理してトレード bot から利用できるようにする為に開発されました。

    DataStore の設計は MongoDB などの「ドキュメント指向データベース」を参考にしており、それを単純なリストと辞書のデータ構造で実現しています。
    :mod:`sqlite3` のインメモリ機能などと比べても高速なデータ参照を実現しています。

    またキー情報をハッシュ化してインデックスを作成することで一意のデータを特定できるようにしています。
    それにより非常に高い頻度で更新される板情報などの更新処理に対応しています。
    例えば Pandas DataFrame などのリッチなデータライブラリでリアルタイムの板情報を扱おうとすると、処理時間の注意が必要です。
    DataFrame の更新には多くの処理が含まれる為、配信されるデータの更新頻度に対して DataFrame の更新処理が追い付かない場合があります。
    それに比べて pybotters の DataStore はシンプルなデータを構造により高速な更新処理を実現しています。

    ただし DataStore の内部構造は説明のように単純なリストと辞書なので **破壊可能である** ことに注意が必要です。
    取得したアイテムをユーザー側で更新するべきではありません。


.. _exchange-specific-datastore:

Exchange-specific DataStore
---------------------------

:ref:`取引所固有の DataStore <exchange-specific-datastore>` は対応取引所における WebSocket チャンネルの DataStore 実装です。

つまり、購読した WebSocket チャンネルのデータがこの取引所固有の DataStore に解釈されることでデータを利用できるようになります。

それぞれの :ref:`取引所固有の DataStore <exchange-specific-datastore>` は :class:`.DataStoreCollection` を継承しており、これは :class:`.DataStore` の集まりです。
:class:`.DataStoreCollection` と :class:`.DataStore` の関係を一般的な RDB システムに例えると
「データベース」と「テーブル」のようなものです。 「データベース」には複数の「テーブル」が存在しており、「テーブル」にはデータの実体があります。

例:

* :class:`.bitFlyerDataStore` (bitFlyer の WebSocket データをハンドリングする :class:`.DataStoreCollection`)
    * :attr:`.bitFlyerDataStore.ticker` (bitFlyer の Ticker チャンネルをハンドリングする :class:`.DataStore`)
    * :attr:`.bitFlyerDataStore.executions` (bitFlyer の約定履歴チャンネルをハンドリングする :class:`.DataStore`)
    * :attr:`.bitFlyerDataStore.board` (bitFlyer の板情報チャンネルをハンドリングする :class:`.DataStore`)
    * ...

pybotters で提供されている取引所固有の DataStore は :doc:`exchanges` のページから探せます。
全てのリファレンスについては :ref:`exchange-specific-datastore-reference` のページにあります。

Attributes
~~~~~~~~~~

WebSocket チャンネルに対応する DataStore は、それぞれの取引所固有の DataStore の属性として割り当てられています。

>>> store = pybotters.bitFlyerDataStore()
>>> store.ticker
<pybotters.models.bitflyer.Ticker object at 0x7f766b9d67f0>
>>> store.executions
<pybotters.models.bitflyer.Executions object at 0x7f766b9d6730>
>>> store.board
<pybotters.models.bitflyer.Board object at 0x7f7666398d90>

WebSocket チャンネルに対応する全ての属性については、個別のリファレンスをご覧ください。

.. _onmessage:

onmessage
~~~~~~~~~

取引所固有の DataStore を利用するには、コールバック :attr:`.DataStoreCollection.onmessage` を :meth:`.Client.ws_connect` のハンドラ引数に渡します。

次のコードは bitFlyer の Ticker チャンネルを購読して DataStore としてデータを参照する例です。

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

.. _initialize:

initialize
~~~~~~~~~~

WebSocket API は HTTP API と違って購読を開始しても「それ以降に更新されたデータ」しか配信されない場合があります。
そうするとプログラム開始時に「初期データ」が存在せず DataStore は空になってしまうので、トレード bot で利用するには不便です。

*async* :meth:`.DataStoreCollection.initialize` メソッドを利用すると HTTP API のデータを初期データとして格納できます。

次のコードは bitFlyer のポジションを HTTP API で初期化して、約定イベントチャンネルを購読することで完全なポジションを構築する例です。

.. code:: python

    async def main():
        apis = {
        "bitflyer": ["BITFLYER_API_KEY", "BITFLYER_API_SECRET"],
        }
        async with pybotters.Client(apis=apis, base_url="https://api.bitflyer.com") as client:
            store = pybotters.bitFlyerDataStore()

            await store.initialize(
                client.get("/v1/me/getpositions", params={"product_code": "FX_BTC_JPY"})
            )

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json=[
                    {
                        "method": "subscribe",
                        "params": {"channel": "child_order_events"},
                        "id": 1,
                    },
                ],
                hdlr_json=store.onmessage,
            )

            while True:  # Ctrl+C to break
                positions = store.positions.find()
                print(positions)

                await store.positions.wait()

:meth:`.DataStoreCollection.initialize` はそれぞれの取引所固有の DataStore において個別に実装されています。
その為、初期化に対応している HTTP API エンドポイントも異なります。
詳しくは個別のリファレンスをご覧ください。

.. _sorted:

sorted
~~~~~~

取引所固有の DataStore において Order Book 系の DataStore には :meth:`.DataStore.sorted` メソッドが実装されています。

これを利用するとリストでデータを参照する :meth:`.DataStore.find` とは違って、 ``{"asks": [...], "bids": [...]}`` のような辞書形式で板情報が参照できます。
また板情報はソート済みで返されるのでトレード bot で利用するのに便利です。

次のコードは bitFlyer の板情報を :meth:`.DataStore.sorted` で取得する例です。

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
                board = store.board.sorted(limit=2)
                print(board)

                await store.board.wait()

.. _wait:

wait
~~~~

*async* :meth:`.DataStore.wait` メソッドは、その DataStore に更新が発生するまで待機できます。

上で説明した :ref:`onmessage` と :ref:`sorted` の例では、データの受信が始まる前に ``while True`` のループが始まるので最初に ``None`` や空のデータが標準出力されるはずです。
DataStore の参照をする前に :meth:`.DataStore.wait` することでデータの受信を待機できます。

次のコードは bitFlyer の Ticker を 2 銘柄を購読して受信するまで待機する例です。

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

            while not len(store.ticker):
                await store.ticker.wait()

            print(store.ticker.find())

.. _watch:

watch
~~~~~

*async* :meth:`.DataStore.watch` メソッドは、変更ストリームを開いて ``async for`` ループで更新データを待機及び取得できます。

*async* :meth:`.DataStore.wait` メソッドと同様に待機できますが、:meth:`.DataStore.watch` では変更データとその詳細を取得できます。

次のコードは bitFlyer の約定履歴を :meth:`.DataStore.watch` で監視する例です。

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

.. _websocketqueue:

WebSocketQueue
--------------

DataStore が実装されていない取引所であったり、自らの実装でデータを処理したい場合は :class:`.WebSocketQueue` を利用できます。

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


Differences with aiohttp
------------------------

aiohttp との違いについて。

pybotters は `aiohttp <https://pypi.org/project/aiohttp/>`__ を基盤として利用しているライブラリです。

その為、:class:`pybotters.Client` におけるインターフェースの多くは ``aiohttp.ClientSession`` と同様です。
また pybotters の HTTP リクエストのレスポンスクラスは aiohttp のレスポンスクラスを返します。
その為 pybotters を高度に利用するには aiohttp ライブラリについても理解しておくことが重要です。

ただし **重要な幾つかの違いも存在します** 。

* pybotters は HTTP リクエストの自動認証機能により、自動的に HTTP ヘッダーなどを編集します。
* pybotters では POST リクエストなどのデータは引数 ``data`` に渡します。 aiohttp では ``json`` 引数を許可しますが pybotters では許可されません。 これは認証機能による都合です。
* :meth:`pybotters.Client.fetch` は pybotters 独自の API です。 aiohttp には存在しません。
* :meth:`pybotters.Client.ws_connect` は aiohttp にも存在しますが、 pybotters では全く異なる独自の API になっています。 これは再接続機能や認証機能を搭載する為です。
