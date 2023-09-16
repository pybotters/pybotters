QuickStart
===============

Installation
------------

``pybotters`` をお使いの環境にpip installしましょう。

.. code:: bash

   pip install pybotters

.. note::
   パッケージアップデートの際はこちらのコマンドを利用してください。

   .. code:: bash

      pip install --upgrade pybotters

インストールできたらまずはコード内で ``pybotters``
パッケージをimportしましょう！

.. code:: python

   import pybotters

API Client
----------

``pybotters``
のAPIクライアントは非同期I/Oのクラスです。 ``pybotters.Client``
クラスを非同期関数の中からコンテキストマネージャーで開いてインスタンスを生成しましょう。

.. code:: python

   async def main():
       async with pybotters.Client() as client:
           ...

   asyncio.run(main())

自動API認証機能を利用するためには引数 ``apis``
にAPIキー・シークレットの情報を渡します。 ``apis``
の情報を渡した取引所はREST/WebSocket
APIを叩いた際、ホスト名を判別し自動で認証情報の付与が行われます。

.. code:: python

   apis = {
       'bybit': ['BYBIT_API_KEY', 'BYBIT_API_SECRET'],
       'binance': ['BINANCE_API_KEY', 'BINANCE_API_SECRET'],
       "okx": ["OKX_API_KEY", "OKX_API_SECRET", "OKX_API_PASSPHRASE"],
       '...': ['...', '...'],
   }

   async def main():
       async with pybotters.Client(apis=apis) as client:
           ...

   asyncio.run(main())

または、API情報をJSON形式で保存している場合、ディレクトリパスを渡すことで読み込むことが可能です。

``api.json``

.. code:: json

   {
       "bybit": ["BYBIT_API_KEY", "BYBIT_API_SECRET"],
       "binance": ["BINANCE_API_KEY", "BINANCE_API_SECRET"],
       "....": ["...", "..."]
   }

.. code:: python

   async def main():
       async with pybotters.Client(apis='apis.json') as client:
           ...

各取引所に対応する ``apis`` のキー名は、こちらの表から設定してください。

======== ==================================
Exchange ``apis`` Key Name
======== ==================================
Bybit    ``bybit``\ \ ``bybit_testnet``
Binance  ``binance``\ \ ``binance_testnet``
OKX      ``okx``\ \ ``okx_demo``
Phemex   ``phemex``\ \ ``phemex_testnet``
Bitget   ``bitget``
MEXC     ``mexc``
KuCoin   ``kucoin``
BitMEX   ``bitmex``\ \ ``bitmex_testnet``
bitFlyer ``bitflyer``
GMO Coin ``gmocoin``
bitbank  ``bitbank``
======== ==================================

REST API
--------

REST APIを利用するためには ``request``, ``get``, ``post``, ``put``,
``delete`` メソッドがあります。 いずれも非同期なので ``await``
で呼び出してください。

.. code:: python

   async def main():
       async with pybotters.Client(apis=apis) as client:
           r = await client.request('GET', 'https://...')
           r = await client.get('https://...', params={'foo': 'bar'})
           r = await client.post('https://...', data={'foo': 'bar'})
           r = await client.put('https://...', data={'foo': 'bar'})
           r = await client.delete('https://...', data={'foo': 'bar'})

..

.. note::
   HTTPリクエストの特性上、\ ``GET`` メソッドの場合は引数 ``params``
   にパラメーター(クエリストリング)を指定します。
   それ以外のHTTPメソッドは引数 ``data``
   にパラメーター(リクエストボディ)を指定します。

戻り値はライブラリ ``aiohttp.ClientResponse`` のインターフェースです。
``status`` プロパティでHTTPステータスを取得できます。 ``json``, ``text``
メソッドでレスポンスボディを取得できます。

その他のインターフェースの詳細は
`aiohttpのリファレンス <https://docs.aiohttp.org/en/stable/client_reference.html#response-object>`__
を確認してください。

.. code:: python

   async def main():
       async with pybotters.Client(apis=apis) as client:
           r = await client.get('https://...', params={'foo': 'bar'})
           print(r.status)
           data = await r.json()
           print(data)

クライアントクラスの生成時に引数 ``base_url``
を指定しておくことでホスト名の省略が可能です。
単一の取引所のみ利用する場合に便利です。 ※ ``base_url``
はWebSocket(``ws_connect``\ メソッド)のURLには適応しません。

以下はBybitで利用する例です。

.. code:: python

   async def main():
       async with pybotters.Client(apis=apis, base_url='https://api.bybit.com') as client:
           r = await client.get('/v2/private/order', params={'symbol': 'BTCUSD'})
           r = await client.post('/v2/private/order/create', data={'symbol': 'BTCUSD', ...: ...})

クライアントクラスの生成時に引数 ``headers``
を指定しておくことでデフォルトヘッダーの指定が可能です。
リクエストメソッドでも上書きで使用できます。
例えばOKXのデモトレードを利用する場合に便利です。

.. code:: python

   async def main():
       async with pybotters.Client(apis=apis, base_url='https://www.okx.com', headers={'x-simulated-trading': '1'}) as client:
           r = await client.get('...')

WebSocket API
-------------

WebSocket APIを利用するためには ``ws_connect`` メソッドを利用します。
メソッドは非同期なので ``await`` で呼び出してください。

.. code:: python

   async def main():
       async with pybotters.Client(apis=apis) as client:
           wstask = await client.ws_connect('wss://...')

引数 ``send_json``, ``hdlr_json``
にそれぞれ接続時に送信するメッセージオブジェクト、受信したメッセージを処理するハンドラ関数を指定します。
文字列で処理したい場合は ``send_str``, ``hdlr_str`` を指定します。
また、接続時に複数のメッセージを送信したい場合はリスト形式のデータを引数に指定します。
``send_json``, ``hdlr_json`` どちらも指定していない場合はデフォルトで
``hdlr_json`` に ``pybotters.print_handler``
が設定されWebSocketで受信したメッセージが表示されます。

.. code:: python

   async def main():
       async with pybotters.Client(apis=apis) as client:
           wstask = await client.ws_connect(
               'wss://...',
               send_json={'foo': 'bar'},
               hdlr_json=pybotters.print_handler,
               # OR string
               # send_str='{"foo":"bar"}',
               # hdlr_str=pybotters.print_handler,
               # OR Multiple request
               # send_json=[{'foo': 'bar'}, {'baz': 'foobar'}],
               # send_str=['{"foo": "bar"}', '{"baz": "foobar"}'],
           )
           await wstask

戻り値は ``asyncio.Task`` です。
開始したWebSocketタスクではコネクション切断時は自動的に再接続が行われるので、基本的には戻り値のタスクに対して操作する必要はありません。

.. note::
   上記のコードを実行しても ``main``
   ルーチンではWebSocket接続後何も処理がないためプログラムは終了してしまい、受信メッセージはprintされません。
   (※通常であればこのあとにbotロジックを記載するでしょう。) そこで
   ``ws_connect`` の戻り値は無限ループタスクなので、それを利用して
   ``await wstask``
   とすることでプログラムの終了を防ぎハンドラの動作を確認することができます。
   これはpybottersでbotロジックではなくWebSocketアプリケーションを作成する際に便利です。

DataStore
---------

``pybotters``
は各取引所のWebSocketで受信したメッセージを処理して扱いやすい形式で保管する
``DataStore`` クラスを実装しています。
上記では単純なprintハンドラを利用しましたが、オーダー管理・ポジション自炊など本格的にWebSocketのデータを扱いたい場合は
``DataStore`` クラスのハンドラを利用しましょう。

WebSocketのデータ形式は取引所ごとに違うのでそれぞれ別のクラスを実装しています。
以下はBybitでオーダーを監視する例です。

.. code:: python

   async def main():
       async with pybotters.Client(apis=apis) as client:
           store = pybotters.BybitDataStore()
           wstask = await client.ws_connect(
               'wss://stream.bybit.com/realtime',
               send_json={
                   'op': 'subscribe',
                   'args': ['order'],
               },
               hdlr_json=store.onmessage,
           )
           # Ctrl+C to break
           while True:
               await store.wait()
               print(store.order.find())

上記を段階を踏んで解説しましょう。 まず最初に
**データストアマネージャー** クラスを生成します。
このマネージャークラスは複数の **データストア**
を持っており、いわゆる複数のテーブルを持つデータベースのようなものです。

.. code:: python

   store = pybotters.BybitDataStore()

生成したデータストアマネージャーの ``onmessage``
関数はWebSocket用のハンドラです。 クライアントの ``ws_connect``
メソッドの引数 ``hdlr_json`` に渡します。
WebSocket接続後、受信データがデータストアで処理されるようになります。

.. code:: python

   await client.ws_connect(
       ...,
       hdlr_json=store.onmessage,
   )

データストアには辞書のようにしてアクセスすることができます。
取引所モデルによってはメンバ変数として定義してあります。

.. code:: python

   # dictionary access
   store['order']
   # member access
   store.order

データストアマネージャー及びデータストアクラスは ``wait``
メソッドでWebSocketメッセージの受信があるまで待機することができます。

データストアマネージャーの ``wait``
メソッドはWebSocketで何かメッセージを受信するまで待機します。
データストアの ``wait``
メソッドはそのストアに関するメッセージを受信するまで待機します。

上記の例ではオーダーしかトピックを購読していないので
``await store.wait()`` で受信を待機しています。

.. code:: python

   # onmessage wait
   await store.wait()
   # order store wait
   await store.order.wait()

データストアは ``get`` メソッドと ``find``
メソッドでデータを参照することができます。

``get``
メソッドは引数にデータストアのキーを指定し、一意のアイテムを取得することができます。
データストアのキーは ``_keys`` メンバで確認できます。

``find``
メソッドは引数に指定した辞書に部分一致する全てのアイテムをリストで取得することができます。
指定しない場合はデータストアの全てのアイテムを取得します。

.. code:: python

   print(store.order._keys)
   # ['order_id']

   print(store.order.get({'order_id': 'aabbccdd'}))
   # {'order_id': 'aabbccdd', 'symbol': 'BTCUSD', 'side': 'Buy', ...: ...}

   print(store.order.get({'order_id': 'zzzzzzzz'}))
   # None

   print(store.order.find({'symbol': 'BTCUSD', 'side': 'Buy'}))
   # [
   #     {'order_id': 'aabbccdd', 'symbol': 'BTCUSD', 'side': 'Buy', ...: ...},
   #     {'order_id': 'eeffgghh', 'symbol': 'BTCUSD', 'side': 'Buy', ...: ...},
   # ]

   print(store.order.find({'order_id': 'zzzzzzzz'}))
   # []

   print(store.order.find())
   # [
   #     {'order_id': 'aabbccdd', 'symbol': 'BTCUSD', 'side': 'Buy', ...: ...},
   #     {'order_id': 'eeffgghh', 'symbol': 'BTCUSD', 'side': 'Buy', ...: ...},
   #     {'order_id': 'iijjkkll', 'symbol': 'BTCUSD', 'side': 'Sell', ...: ...},
   # ]
