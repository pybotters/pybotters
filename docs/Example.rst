Example
=======

このページでは ``pybotters`` を利用したbotの実装例を紹介します。

Bybit インバース無期限契約
--------------------------

低頻度botのサンプル
~~~~~~~~~~~~~~~~~~~

ローソク足(1分足)を元にトレードを行うbot

.. code:: python

   import asyncio
   import time

   import pybotters


   # apis
   apis = {
       'bybit': ['BYBIT_API_KEY', 'BYBIT_API_SECRET']
   }

   async def main():
       async with pybotters.Client(apis=apis, base_url='https://api.bybit.com') as client:
           # 必要な初期処理
           ...

           # メインループ
           while True:
               # REST APIデータ並列リクエスト
               resps = await asyncio.gather(
                   client.get('/v2/public/kline/list', params={
                       'symbol': 'BTCUSD', 'interval': 1, 'from': int(time.time()) - 3600
                   }),
                   client.get('/v2/private/order', params={'symbol': 'BTCUSD'}),
                   client.get('/v2/private/position/list', params={'symbol': 'BTCUSD'}),
               )
               kline, order, position = await asyncio.gather(*[r.json() for r in resps])

               # シグナル計算
               """
               something awesome logic...
               """
               cond = 'Whether to execute...'
               side = 'Buy or Sell...'
               qty = 'Calculated value...'

               # オーダー執行
               if cond:
                   await client.post('/v2/private/order/create', data={
                       'symbol': 'BTCUSD',
                       'side': side,
                       'order_type': 'Market',
                       'qty': qty,
                       # 'price': price,
                       'time_in_force': 'GoodTillCancel',
                   })

               # 待機(60秒)
               await asyncio.sleep(60.0)


   # 非同期メイン関数を実行(Ctrl+Cで終了)
   if __name__ == '__main__':
       try:
           asyncio.run(main())
       except KeyboardInterrupt:
           pass

高頻度botの場合
~~~~~~~~~~~~~~~

板情報を元にトレードを行うbot

.. code:: python

   import asyncio

   import pybotters


   # apis
   apis = {
       'bybit': ['...', '...'],
   }

   async def main():
       async with pybotters.Client(apis=apis, base_url='https://api.bybit.com') as client:
           # データストアのインスタンスを生成する
           store = pybotters.BybitDataStore()

           # REST API由来のデータ(オーダー・ポジション・残高)を初期データとしてデータストアに挿入する
           await store.initialize(
               client.get('/v2/private/order', params={'symbol': 'BTCUSD'}),
               client.get('/v2/private/position/list', params={'symbol': 'BTCUSD'}),
               client.get('/v2/private/wallet/balance', params={'symbol': 'BTCUSD'}),
           )

           # WebSocket接続
           wstask = await client.ws_connect(
               'wss://stream.bybit.com/realtime',
               send_json={'op': 'subscribe', 'args': [
                   'orderBookL2_25.BTCUSD',
                   'trade.BTCUSD',
                   'instrument_info.100ms.BTCUSD',
                   'position',
                   'execution',
                   'order',
               ]},
               hdlr_json=store.onmessage,
           )

           # WebSocketでデータを受信するまで待機
           while not all([
               len(store.orderbook),
               len(store.instrument),
           ]):
               await store.wait()

           # その他必要な初期処理
           ...

           # メインループ
           while True:
               # データ参照
               orderbook = store.orderbook.find()
               order = store.order.find()
               position = store.position_inverse.find()

               # シグナル計算
               """
               something awesome logic...
               """
               cond = 'Whether to execute...'
               side = 'Buy or Sell...'
               qty = 'Calculated value...'
               price = 'Amazing price...'

               # オーダー執行
               if cond:
                   # 高頻度では重複オーダーしないようにオーダー後WebSocketでデータ受信するまで待機させる
                   # RESTの応答よりWebSocketのイベントの方が速い可能性があるので先にイベント待機タスクをスケジュールする
                   event = asyncio.create_task(store.order.wait())
                   await client.post('/v2/private/order/create', data={
                       'symbol': 'BTCUSD',
                       'side': side,
                       'order_type': 'Limit',
                       'qty': qty,
                       'price': price,
                       'time_in_force': 'GoodTillCancel',
                   })
                   await event

               # 板情報のイベントまで待機
               await store.orderbook.wait()


   # 非同期メイン関数を実行(Ctrl+Cで終了)
   if __name__ == '__main__':
       try:
           asyncio.run(main())
       except KeyboardInterrupt:
           pass
