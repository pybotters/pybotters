Advanced Usage
==============

.. _implicit-loading-of-apis:

Implicit loading of ``apis``
----------------------------

:class:`.Client` の引数 ``apis`` を指定せず以下のように暗黙的な読み込みが可能です。

1. カレントディレクトリに ``apis.json`` を配置する
    カレントディレクトリに ``apis.json`` という名前の JSON ファイルを配置することで自動的にそのファイルを読み込ます。

    .. NOTE::
        カレントディレクトリとは :meth:`os.getcwd` で得られる ``python`` コマンドを実行したディレクトリです。

    .. warning::
        Git などのバージョン管理を利用している場合、セキュリティ上の観点からカレントディレクトリの ``apis.json`` ファイルはバージョン管理外にするべきです。
        ``.gitignore`` に ``apis.json`` を追加してください。

2. 環境変数 ``PYBOTTERS_APIS`` にファイルパスを設定する
    環境変数 ``PYBOTTERS_APIS`` に API 認証情報の JSON ファイルパスを設定することでそのファイルを読み込みます。
    UNIX 系の環境を利用している場合は、``~/.bashrc`` ファイルなどを編集することで環境変数を設定できます。

    .. code:: bash

        # .~/.bashrc
        export PYBOTTERS_APIS=/path/to/apis.json

**優先順位**

以下のような優先順位で pybotters に API 認証情報が読み込まれます。 複数の設定があった場合、下位の設定は無視されます。

1. :class:`.Client` の引数 ``apis`` を明示的に指定する
2. カレントディレクトリに ``apis.json`` JSON ファイルを配置する
3. 環境変数 ``PYBOTTERS_APIS`` に JSON ファイルパスを設定する


Disable Authentication
----------------------

pybotters の自動認証処理を無効にする場合は、リクエストメソッドの引数 ``auth=None`` を設定します。

.. code:: python

    async def main():
        apis = {"some_exchange": ["KEY", "SECRET"]}
        async with pybotters.Client(apis=apis) as client:
            r = await client.fetch("GET", "/public/endpoint", auth=None)

.. note::

    pybotters では :class:`~.Client` の引数 ``apis`` に API 認証情報を渡すことでホスト名に紐づく **全てのリクエスト** への自動認証が有効になります。
    その為 Public API エンドポイントなどに対しても認証処理が働きます
    (これは pybotters が取引所のホスト名のみ把握しており、URL パス以降を把握していない為です) 。

    Public API エンドポイントにおいて認証処理を無効にしたい場合は例のように引数 ``auth=None`` を設定します。

    殆どの取引所では Public API に対して認証処理をしてもレスポンスには影響ありません。
    ただし Binance Spot など一部では Public API がエラーになります。
    その場合はこの ``auth=None`` を設定してください。


Fetch data validation
---------------------

:meth:`Client.fetch() <.Client.fetch>` メソッドの返り値にあるプロパティ :attr:`FetchResult.data <.FetchResult.data>` は通常 JSON をパースしたオブジェクトが格納されますが、
少なくとも単純に ``if`` 文で評価しておくことでコードの安全性が高くなります。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            r = await client.fetch("GET", "https://google.com")  # Not JSON content

            if r.data:  # NotJSONContent
                print(r["data"])  # KeyError will be raised
            else:
                print(f"Not JSON content: {r.text[:50]} ... {r.text[-50:]}")

レスポンスが JSON ではないケースでは :attr:`FetchResult.data <.FetchResult.data>` には :class:`.NotJSONContent` が格納されます。
:class:`.NotJSONContent` は評価結果は必ず ``False`` となります。 その為 ``if r.data:``  で評価しておくことにより意図しないエラーを防げます。

.. note::

    JSON の検証をより堅牢にするには Python 3.10 + の機能である ``match`` 文の Mapping Pattern を使うことをおすすめします。

    https://peps.python.org/pep-0635/#mapping-patterns

    .. code:: python

        async def main():
            async with pybotters.Client(base_url="https://api.bitflyer.com") as client:
                r = await client.fetch(
                    "GET", "/v1/getticker", params={"product_code": "BTC_JPY"}
                )

                match r.data:
                    case {"product_code": str()}:
                        print("Correct response", r.data)
                    case {"status": int()}:
                        print("Incorrect response", r.data)
                    case pybotters.NotJSONContent():
                        print("NotJSONContent", r.data)


aiohttp Keyword Arguments
-------------------------

クライアント :class:`.Client` とリクエストメソッド :meth:`.Client.fetch` や :meth:`.Client.get` のキーワード引数 ``**kwargs`` に対応する引数を渡すことで、
pybotters がラップしている :class:`aiohttp.ClientSession` や :meth:`aiohttp.ClientSession.get` の引数にバイパスすることができます。

以下の例では aiohttp の実装である ``timeout`` 引数を設定してリクエストを作成します。 ``timeout`` 引数は pybotters には存在しません。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            # TimeoutError will be raised
            await client.fetch("GET", "https://httpbin.org/delay/10", timeout=3.0)


.. _multiple-websocket-senders-handlers:

Multiple WebSocket senders/handlers
-----------------------------------

:meth:`.Client.ws_connect` の ``send_*`` 引数と ``hdlr_*`` 引数には対応するオブジェクトのリスト形式で渡すことで
複数のメッセージが送信、または受信メッセージを複数のコールバックでハンドリングすることができます。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            ws = await client.ws_connect(
                "ws://...",
                send_json=[
                    {"op": "subscribe", "channel": "ch1"},
                    {"op": "subscribe", "channel": "ch2"},
                    {"op": "subscribe", "channel": "ch3"},
                ],
                hdlr_json=[
                    func1,
                    func2,
                    func3,
                ],
            )
            await ws.wait()

.. warning::

    これの副作用として「最上位がリスト形式の JSON」を ``send_json`` 引数に指定して送信することができません。
    回避策として ``send_str`` 引数に ``json.dumps`` で文字列にダンプした値を与えてください。
    しかしながら、仮想通貨取引所の WebSocket API において「最上位がリスト形式の JSON」を要求するものは今のところ確認していません。


Current WebSocket connection
----------------------------

:attr:`.WebSocketApp.current_ws` プロパティから aiohttp の WebSocket クラス
`ClientWebSocketResponse <https://docs.aiohttp.org/en/stable/client_reference.html#clientwebsocketresponse>`_
にアクセスできます。
このクラスから 1 回限りの WebSocket メッセージ送信などができます。
これは取引所 WebSocket API で注文の作成に対応しているケースなどで有用です。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            ws = await client.ws_connect("ws://...")

            if ws.current_ws:
                await ws.current_ws.send_json({"channel": "order"})

            await ws.wait()

ただし pybotters が管理している WebSocket が切断中にある場合、:attr:`.WebSocketApp.current_ws` プロパティは ``None`` が格納されます。
つまりプロパティのオブジェクトが動的に変化する可能性があると言いう意味です。
コードの安全性を高めるには、上記のコードのようにまず ``if ws.current_ws:`` と評価してから :attr:`.WebSocketApp.current_ws` を参照するべきです。

.. note::

    :meth:`.WebSocketApp.current_ws.send_json` などで行うリクエストはその場限りのメッセージ送信になります。
    これをチャンネルの購読に利用するべきではありません。
    反対に :meth:`.Client.ws_connect` などの ``send_json`` 引数に与えるメッセージは、再接続も含めて接続直後に毎回送信するメッセージとなります。


WebSocket Handshake
-------------------

:class:`.WebSocketApp` は ``await`` することで WebSocket ハンドシェイクが行われます。
正確にはバックグラウンドタスクによってハンドシェイクが終わるまで待機します。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            ws = await client.ws_connect("ws://...")  # Wait WebSocket handshake

上記のコードをみると勘違いしがちですが :meth:`.Client.ws_connect` は **非同期関数ではなく同期関数です** 。
その正体としては :class:`.WebSocketApp` を生成しているだけです。
また :class:`.WebSocketApp` は ``await`` すると自身を返します。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            ws = client.ws_connect("ws://...")  # type: WebSocketApp
            ws = await ws  # Wait WebSocket handshake, No need to assign ws variable

各状態のおける ``await WebSocketApp`` の仕様としては以下の通りです。

1. WebSocket 接続がない (初回または切断中) 場合、 WebSocket ハンドシェイクが行われるまで ``await`` によって待機します。
2. WebSocket 接続がある場合、 ``await`` による待機は即時完了します。


Automatic WebSocket heartbeat
-----------------------------

:class:`.WebSocketApp` はデフォルトで自動 WebSocket ハートビートが有効になっています。

この動作は :class:`.Client.ws_connect` の引数 ``heartbeat`` によって変更できます。
``heartbeat`` には ``float`` の秒数を指定します。 引数を指定しない場合デフォルトでは 10 秒です。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            ws = await client.ws_connect("ws://...", heartbeat=10.0)  # default value

``heartbeat`` を設定するとバックグラウンドタスクが起動し、一定間隔で対象の WebSocket サーバーに Ping フレームを送信します。
その後 ``heartbeat`` 秒数間のタイムアウトを待ち、 Pong フレームを受信した場合はタイムアウトをリセットして次の Ping フレームを送信するまで待機します。
タイムアウトが発生した場合は現在の WebSocket 接続を切断して再接続を試みます。

``heartbeat`` に ``None`` を指定すると Ping-Pong メッセージの送信を無効にします。

.. note::
    WebSocket ハートビートは、 WebSocket の接続を保証する為の重要な機能です。

    「お行儀のよい」 WebSocket サーバーは、切断時にクライアントに対して明示的な切断メッセージを送信します。
    しかし一部の WebSocket サーバーは切断時に何もメッセージを送信しないため、クライアントは接続が切断されたかどうかを検知できません。
    クライアントは接続が確立していると認識しているので pybotters に組み込まれている自動再接続も試行されません。

    そういった状態に陥ると結果的に bot コードでは WebSocket データを受信せずにループ動作し続けることになります。
    つまり、WebSocket 経由でポジションや注文や板情報などのデータを受信している場合はデータの状態が古いままになり、取引に支障をきたす可能性があります。

    そこで WebSocket ハートビートを利用することでこの状態に陥ることを防ぎます。
    Ping 及び Pong フレームは `WebSocket の仕様 <https://datatracker.ietf.org/doc/html/rfc6455#section-5.5.2>`_ で定義されており、アプリケーションのメッセージ受信には影響されません。
    これを送受信することで相手方のサービスが機能しているかを確認します。

    前述の通りハートビートはデフォルトで有効になっており、トレード bot のユースケースでこれを無効にすることは推奨されません。

    なお、このハートビート機能は `aiohttp の実装 <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession.ws_connect>`_ によるものです。


.. _manual-websocket-heartbeat:

Manual WebSocket heartbeat
--------------------------

:class:`.WebSocketApp` は自動で WebSocket ハートビートを実行しますが、:meth:`.WebSocketApp.heartbeat` メソッドを呼び出すことで手動でハートビートを実行できます。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            ws = await client.ws_connect("ws://...")

            while True:
                await ws.heartbeat()

                ... # Trading strategy

自動ハートビートによってある程度接続は保証されますが、手動ハートビートを実行することで任意のタイミングで接続を保証を確認できます。

:meth:`.WebSocketApp.heartbeat` を ``await`` することで、Ping フレームを送信して対応する Pong フレームの受信を待機します。
Pong フレームが引数 ``timeout`` の秒数受信できない場合は、現在の WebSocket 接続を切断して再接続を試みます。
その後、再度 Ping フレームを送信して Pong フレームの受信を試みます。
これらのハートビートシーケンスが終了するまで ``await`` によって待機します。

ハートビートのタイムアウトは引数 ``timeout`` で設定できます。
デフォルトは 10 秒です。

このメソッドは接続を保証したいステップで呼び出すべきでしょう。
例えば、WebSocket 経由でデータを受信して利用している場合はそれを利用する前が最適です。


WebSocket reconnection backoff
------------------------------

:meth:`.Client.ws_connect` の引数 ``backoff`` に ``float`` のタプルを設定することで、再接続の指数バックオフを変更できます。
タプルの意味は ``(最小待機秒, 最大待機秒, 係数, 初期待機秒)`` です。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            ws = await client.ws_connect("ws://...", backoff=(1.92, 60.0, 1.618, 5.0))  # default value

既定のバックオフ動作は以下の通りです。

* 正常切断であれば待機なしで再接続します
* ハンドシェイク失敗であれば指数バックオフの秒数待機します
    * 初回の接続失敗であれば 0 ~ 5 秒 (BACKOFF_INITIAL) の間のランダムな時間待機します
    * 二回目の接続失敗であれば 1.92 秒 (BACKOFF_MIN) に 1.618 (BACKOFF_FACTOR) を掛けた時間待機します
    * その後の接続失敗であれば前回の待機時間にさらに 1.618 (BACKOFF_FACTOR) を掛けた時間待機します
    * ただし待機時間の上限は 60.0 秒 (BACKOFF_MAX) です
    * 接続に成功した場合はバックオフの計算は初回のステップにリセットされます


URL when reconnecting to WebSocket
----------------------------------

:attr:`.WebSocketApp.url` に URL を代入することで、接続する WebSocket URL を変更できます。

.. code:: python

    async def main():
        async with pybotters.Client() as client:
            ws = await client.ws_connect("ws://example.com/ws?token=xxxxx")
            ...
            ws.url = "ws://example.com/ws?token=yyyyy"

接続中の場合は直ちに影響はなく、その接続が終了した次回の接続で設定した WebSocket URL が利用されます。

.. note::
    これはトークン認証方式を採用している取引所の WebSocket 接続に便利です。
    多くの場合はそのトークンを延長する API がありますが、何かの原因でトークンが失効してしまった場合に別のトークンを発行してそれを URL に設定できます。


DataStore Iteration
-------------------

:ref:`datastore` では :meth:`.DataStore.get` と :meth:`.DataStore.find` でデータを取得する方法を説明しましたが、他にもイテレーションによって取得することもできます。

>>> ds = pybotters.DataStore(
...     keys=["id"],
...     data=[
...         {"id": 1, "data": "foo"},
...         {"id": 2, "data": "bar"},
...         {"id": 3, "data": "baz"},
...         {"id": 4, "data": "foo"},
...     ],
... )
>>> for item in ds:
...     print(item)
... 
{'id': 1, 'data': 'foo'}
{'id': 2, 'data': 'bar'}
{'id': 3, 'data': 'baz'}
{'id': 4, 'data': 'foo'}

または :func:`reversed` を利用して逆順で取得もできます。

>>> for item in reversed(ds):
...     print(item)
... 
{'id': 4, 'data': 'foo'}
{'id': 3, 'data': 'baz'}
{'id': 2, 'data': 'bar'}
{'id': 1, 'data': 'foo'}


Maximum number of data in DataStore
-----------------------------------

DataStore は :attr:`.DataStore._MAXLEN` 変数にて最大件数の制限を設けています。

これはトレード履歴のような大量に配信されるデータの格納することによって、マシンの RAM が枯渇しないようにするためです。
この制限を超えると、古いデータから順に自動で削除されます。

:attr:`.DataStore._MAXLEN` は、取引所固有の DataStore にてチャンネルごとに異なる値が設定されています。
通常は最大 9,999 件、トレード履歴などは最大 99,999 件として設定しています。

以下は例として :class:`.bitFlyerDataStore` で Ticker と約定履歴ストアの最大件数を確認するコードです。

>>> store = pybotters.bitFlyerDataStore()
>>> store.ticker._MAXLEN
9999
>>> store.executions._MAXLEN
99999


How to implement original DataStore
-----------------------------------

:class:`.DataStoreCollection` と :class:`.DataStore` を継承したクラスを作成することで、
ユーザーは pybotters が対応していない取引所や、pybotters ビルドインの実装に満足しない場合に独自の DataStore を実装することができます。

以下の手順に従うことで、pybotters 既定仕様の DataStore が実装できます。

* :class:`.DataStoreCollection` のサブクラス
    1. :meth:`_init` メソッド
        * 引数: なし
        * 処理: :meth:`.DataStoreCollection.create` を使って取引所の WebSocket チャンネルに相当する DataStore を生成する処理を実装します
    2. :meth:`_onmessage` メソッド
        * 引数: ``msg: Any, ws: ClientWebSocketResponse``
        * 処理: 受信した WebSocket メッセージのチャンネルを解釈して各 DataStore に振り分ける処理を実装します
    3. *async* :meth:`initialize` メソッド
        * 引数: ``*aws: Awaitable[aiohttp.ClientResponse]``
        * 処理: 初期化用の HTTP API のレスポンスを解釈して各 DataStore に振り分ける処理を実装します
    4. class Properties
        * :meth:`_init` メソッド内で生成した DataStore に便宜的にアクセスできるように、クラスに同名のプロパティを定義します
* :class:`.DataStore` のサブクラス
    1. :const:`_KEYS` 変数
        * 解釈した WebSocket メッセージにキーが存在する場合、それをリストで設定します
            * 差分データが配信される WebSocket チャンネルにおいてこれを設定します
            * 例えば板情報について考えると、 ``"銘柄"`` と ``"方向"`` と ``"価格"`` がキーとなります。 このキーを元に ``"数量"`` を更新したりあるいはデータを削除します
        * キーが存在しないデータは :const:`_KEYS` を設定する必要がありません
            * 例えば約定履歴は時系列データです。新しいデータが配信されますが、過去のデータが更新されることはありません
    2. :const:`_MAXLEN` 変数
        * 変数を上書きしない場合値は 9999 となっています。 pybotters の既定では時系列データの場合は値を 99999 に上書きしています
    3. :meth:`_onmessage` メソッド
        * 引数: ``msg: Any``
            * ※ :meth:`.DataStoreCollection._onmessage` から渡す引数仕様に変更可能です
        * 処理: :meth:`.DataStore._insert` :meth:`.DataStore._update` :meth:`.DataStore._delete` などの CURD メソッドを用いて、WebSocket メッセージを解釈して内部のデータを更新します
    4. :meth:`_onresponse` メソッド
        * 引数: ``msg: Any``
            * ※ :meth:`.DataStoreCollection.initialize` から渡す引数仕様に変更可能です
        * 処理: :meth:`.DataStore._insert` :meth:`.DataStore._update` :meth:`.DataStore._delete` などの CURD メソッドを用いて、レスポンスを解釈して内部のデータを更新します
    5. :meth:`sorted` メソッド (※板情報系のみ)
        * 引数: ``query: dict[str, Any]``
        * 処理: 板情報を ``"売り", "買い"`` で分類した辞書を返します (:ref:`bitFlyerDataStore での例 <sorted>`) 。

次のコードはシンプルな独自の DataStore の例です。

.. code:: python

    class SomeDataStore(DataStoreCollection):
        """ Some Exchange データストア"""

        def _init(self):
            self.create("trade")
            self.create("orderbook")
            self.create("position")

        def _onmessage(self, msg, ws):
            # ex: msg = {"channel": "xxx", "data": ...}
            channel = msg.get("channel")
            data = msg.get("data")
            if channel == "trade":
                self.trade._onmessage(data)
            elif channel == "orderbook"
                self.orderbook._onmessage(data)
            elif channel == "position"
                self.position._onmessage(data)

        async def initialize(self, *aws):
            for f in asyncio.as_completed(aws):
                resp = await f
                data = await resp.json()
                if resp.url.path == "/api/position":
                    self.position._onresponse(data)

        @property
        def trade(self) -> "Trade":
            return self.get("trade")

        @property
        def orderbook(self) -> "OrderBook":
            return self.get("orderbook")

        @property
        def position(self) -> "Position":
            return self.get("position")


    class Trade(DataStore):
        """約定履歴ストア"""
        _MAXLEN = 99999

        def _onmessage(self, data):
            # ex: data = [{"symbol": "xxx", "price": 1234, "...": ...}]
            self._insert(data)


    class OrderBook(DataStore):
        """板情報ストア"""
        _KEYS = ["symbol", "side", "price"]

        def _onmessage(self, data):
            # ex: data = {"symbol": xxx", "asks": {"price": 1234, "size": 0.1}, ...}, "bids": ...}
            symbol = data["symbol"]
            data_to_update = []
            data_to_delete = []

            for side in ("asks", "bids"):
                for row in data[side]:
                    row = {"symbol": symbol, "side": side, **row}
                    if row["price"] == 0.0:
                        data_to_delete.append(row)
                    else:
                        data_to_update.append(row)

            self._update(data_to_update)
            self._update(data_to_delete)

        def sorted(self, query=None, limit=None):
            return self._sorted(
                item_key="side",
                item_asc_key="asks",
                item_desc_key="bids",
                sort_key="price",
                query=query,
                limit=limit,
            )


    class Position(DataStore):
        """ポジションストア"""
        _KEYS = ["symbol"]

        def _onmessage(self, data):
            # ex: data = [{"symbol": "xxx", "side": "Buy", "size": 0.1]
            self._update(data)

        def _onresponse(self, data):
            # ex: data = [{"symbol": "xxx", "side": "Buy", "size": 0.1]
            self._clear()
            self._update(data)


既存の DataStore 実装を参考にするには、リポジトリの ``models/`` 内ソースコードを参照してください。

もし pybotters が未対応の取引所の DataStore を実装された場合は、pybotters へのコントリビュート (ソースコードの寄付) を検討して頂けるとありがたいです 🙏
pybotters は無料のオープンソースソフトウェア・プロジェクトであり人々のボランティア精神によって成り立っています。
コントリビュートするには GitHub リポジトリに Pull request を作成します。
詳しくは :doc:`contributing` ページをご覧ください。
