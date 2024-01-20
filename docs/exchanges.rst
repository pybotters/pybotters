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
