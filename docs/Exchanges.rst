Exchanges
=========

それぞれの取引所での固有の用法を記載します。

Bybit
-----

Initialize
~~~~~~~~~~

BybitのWebSocketはオーダー・ポジション等の初期値が送信されないのでRESTでの初期化が必要です。

初期化するにはデータストアの ``initialize`` メソッドを実行します。
引数にはリクエストのコルーチンを可変長で渡します。

.. code:: python

   async def main():
       async with pybotters.Client(apis=apis, base_url='https://api.bybit.com') as client:
           store = pybotters.BybitDataStore()
           await store.initialize(
               # Inverse
               client.get('/v2/private/order', params={'symbol': 'BTCUSD'}),
               client.get('/v2/private/position/list', params={'symbol': 'BTCUSD'}),
               # USDT
               client.get('/private/linear/order/search', params={'symbol': 'BTCUSDT'}),
               client.get('/private/linear/position/list', params={'symbol': 'BTCUSDT'}),
               client.get('/v2/private/wallet/balance', params={'coin': 'USDT'}),
           )
           # Inverse
           wstask = await client.ws_connect(
               'wss://stream.bybit.com/realtime',
               send_json={'op': 'subscribe', 'args': ['position', 'order']},
               hdlr_json=store.onmessage,
           )
           # USDT
           wstask = await client.ws_connect(
               'wss://stream.bybit.com/realtime_private',
               send_json={'op': 'subscribe', 'args': ['position', 'order', 'wallet']},
               hdlr_json=store.onmessage,
           )

対応エンドポイント

-  オーダー

    -  ``/v2/private/order``
    -  ``/private/linear/order/search``
    -  ``/futures/private/order``

-  条件付きオーダー

    -  ``/v2/private/stop-order``
    -  ``/private/linear/stop-order/search``
    -  ``/futures/private/stop-order``

-  ポジション

    -  ``/v2/private/position/list``
    -  ``/private/linear/position/list``
    -  ``/futures/private/position/list``

-  残高

    -  ``/v2/private/wallet/balance``

FTX
---

Subaccount
~~~~~~~~~~

サブアカウントで取引を行う場合はヘッダーにサブアカウントの情報を指定します。(`FTX
APIドキュメント <https://docs.ftx.com/#authentication>`__)

``pybotters.Client`` またはリクエストメソッドの引数 ``headers`` に ``FTX-SUBACCOUNT`` を指定してください。

.. code:: python

   async def main():
       async with pybotters.Client(apis=apis, base_url='https://ftx.com/api', headers={'FTX-SUBACCOUNT': 'my_subaccount_1'}) as client:
           # REST
           r = await client.get('/positions') # equal my_subaccount_1
           r = await client.get('/positions', headers={'FTX-SUBACCOUNT': 'my_subaccount_2'})
           # WebSocket
           wstask = await client.ws_connect('wss://ftx.com/ws/', send_json=...) # equal my_subaccount_1
           wstask = await client.ws_connect('wss://ftx.com/ws/', send_json=..., headers={'FTX-SUBACCOUNT': 'my_subaccount_2'})

.. note::
   本来のFTXの仕様ではWebSocketはヘッダーを指定するものではありませんが、pybottersがそれを判定して自動的にWebSocketの認証メッセージにサブアカウントを付与して送信しています。

.. _initialize-1:

Initialize
~~~~~~~~~~

FTXのWebSocketはオーダーの初期値が送信されないのでRESTでの初期化が必要です。

初期化するにはデータストアの ``initialize`` メソッドを実行します。
引数にはリクエストのコルーチンを可変長で渡します。

また、データストアにポジションを用意していますが、FTXのWebSocketにはポジション情報ありません。
その代わりに ``initialize`` メソッドにポジションのエンドポイントを渡すことで、WebSocketの ``fills`` チャンネル受信時にREST
APIを自動フェッチしてデータストアを更新する機能が有効化されます。(※ ``fills`` チャンネルを購読してください。)
FTXのREST
API制限は ``30回/1秒`` と非常に緩いですが、制限が気になる場合はこの機能は利用しないでください。

.. code:: python

   async def main():
       async with pybotters.Client(apis=apis, base_url='https://ftx.com/api') as client:
           store = pybotters.FTXDataStore()
           await store.initialize(
               client.get('/orders', params={'market': 'BTC-PERP'}),
               client.get('/positions', params={'showAvgPrice': 'true'}),
           )
           wstask = await client.ws_connect(
               'wss://ftx.com/ws/',
               send_json=[
                   {'op': 'subscribe', 'channel': 'orders'},
                   {'op': 'subscribe', 'channel': 'fills'},
               ],
               hdlr_json=store.onmessage,
           )

対応エンドポイント

-  オーダー

    -  ``/orders``
    -  ``/conditional_orders``

-  ポジション

    -  ``/positions`` ※ ``fills`` 受信時の自動フェッチを有効化する

DataStore
~~~~~~~~~

FTXのデータストアはWebSocketから受信したデータ形式からデータストアとして扱いやすい形式に加工して格納しています。
特に板情報のデータストアは以下の様に加工しています。
※それ以外のデータストアは ``market`` 名を付与している程度です。

Example:

.. code:: python

   # input data format
   {
       'asks': [[4114.25, 6.263]],
       'bids': [[4112.25, 49.29]]
   }
   # store.orderbook.find()
   [
       {'market': 'BTC-PERP', 'side': 'sell', 'price': 4114.25, 'size': 6.263},
       {'market': 'BTC-PERP', 'side': 'buy', 'price': 4112.25, 'size': 49.29}
   ]

BitMEX
------

.. _initialize-2:

Initialize
~~~~~~~~~~

BitMEXのWebSocketは全ての必要な初期値が送信されます。
その都合上、データストアの生成もWebSocketで初期データを受信したタイミングに行われます。(受信されるまではNoneになります。)

.. code:: python

   async def main():
       async with pybotters.Client() as client:
           store = pybotters.BitMEXDataStore()
           wstask = await client.ws_connect(
               'wss://www.bitmex.com/realtime',
               send_json={'op': 'subscribe', 'args': ['orderBookL2_25:XBTUSD']},
               hdlr_json=store.onmessage,
           )
           print(type(store.orderbook))
           # None
           while store.orderbook is None:
               await store.wait()
           print(type(store.orderbook))
           # <class 'pybotters.store.DataStore'>

bitbank
-------

WebSocket
~~~~~~~~~

bitbankのWebSocket
APIは `Socket.IOによって実装されています <https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-stream_JP.md#api-%E6%A6%82%E8%A6%81>`__ 。
pybottersのaiohttp基盤なのでSocket.IOクライアントには対応していません。とは言っても高レベルなSocket.IOクライアントを利用できないだけで大枠のWebSocketという規格としては同じです。なのでデータの送受信プロトコルを低レベルで記述することで接続が可能です。

サンプルコード (任意でwhile True内のコメントアウトを変更してください)

.. code:: python

   async def main():
       async with pybotters.Client() as client:
           store = pybotters.bitbankDataStore()
           wstask = await client.ws_connect(
               'wss://stream.bitbank.cc/socket.io/?EIO=3&transport=websocket',
               send_str=[
                   '42["join-room","ticker_xrp_jpy"]',
                   '42["join-room","transactions_xrp_jpy"]',
                   '42["join-room","depth_whole_xrp_jpy"]',
               ],
               hdlr_str=store.onmessage,
           )
           while True:
               # Transactions
               # await store.transactions.wait()
               # pybotters.print(store.transactions.find()[-1])

               # Depth
               await store.depth.wait()
               pybotters.print({k:v[:6] for k, v in store.depth.sorted().items()})

               # Ticker
               # await store.ticker.wait()
               # pybotters.print(store.ticker.find())

ポイントは - URLに ``EIO=3&transport=websocket``
といったクエリパラメーターを付与すること - 購読は ``send_str``
引数を利用して配列形式の文字列に ``42`` プレフィックスを付けること -
DataStoreのハンドラは ``hdlr_str`` 引数を利用すること

これによってSocket.IOプロトコルでWebSocketに接続でき、DataStoreのハンドラもSocket.IOの解釈に対応している為データを保管できます。

GMO Coin
--------

.. _websocket-1:

WebSocket
~~~~~~~~~

GMOコインのWebSocketのチャンネル購読は
`1秒間1回が上限という制限 <https://api.coin.z.com/docs/#restrictions>`__
があります。

pybottersの通常の仕様は *send_json* または *send_str*
の送信メッセージは非同期でリクエストされます。
しかしGMOコインにおいては上記のような制限があり正常にチャンネルを購読できなくなる為、pybottersはGMOコインのWebSocketを自動的に判別して制限を回避します。
メッセージを送信する時に非同期処理のロックし1秒間の待機が行われます。
またこの際正確な1秒間を判別する為にGMOコインのPublic API
``GET /public/v1/status``
でサーバータイムをメッセージ送信毎にリクエストします。

この仕組みについてユーザー側で操作は不要ですが、購読するチャンネル数ごとに1秒間待機が発生することと、Public
APIのリクエストが発生することに注意してください。
