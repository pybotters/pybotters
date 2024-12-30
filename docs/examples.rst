Examples
========

このページでは :mod:`pybotters` のサンプルコードを紹介します。

.. note::

    ここのサンプルコードでは `rich <https://pypi.org/project/rich/>`_ ライブラリの print を利用しています。

    :mod:`rich` はターミナル上に美しい形式のテキストを表示してくれるライブラリです。
    API で取得した JSON を ``rich.print`` すると、人間に分かりやすく綺麗に表示してくれるのでとても役に立ちます。
    別途インストールすることをおすすめします。

    .. code:: bash

        pip install rich

Trading bot
-----------

:mod:`pybotters` で :ref:`websocket-api` と :ref:`datastore` を利用した bitFlyer トレード bot の基礎的な構成例です。
説明はコードの下にあります。

.. literalinclude:: ../examples/trading-bot/bitflyer.py

Workflow
~~~~~~~~

このサンプルコードは以下のような処理フローとなっています。

1. 環境変数から API 認証情報などを取得する
2. DataStore を生成して HTTP API で初期化する
3. WebSocket に接続する
4. WebSocket からの初期データを待機する
5. メインループを開始する

メインループは、以下のような処理フローとなっています。

1. DataStore から各種データを取得する
2. アルゴリズム関数にデータを入力して、注文条件を計算する
    .. note::
        
        アルゴリズムはトレード bot の損益を左右する最も重要な部分です。
        あなたのトレード戦略を実装しましょう！

        サンプルコードでは「既存の注文がない場合、ベスト Bid - 1000 に買い指値を置く」というアルゴリズムになっています。
3. 注文の執行条件が真の場合、注文を執行する
    1. 注文イベントの変更ストリームを開く
    2. HTTP API で注文を送信する
    3. HTTP API レスポンスが正常なら、DataStore のデータを同期するため待機します
        1. 注文イベントの変更ストリームを開始して、データを取得するまで待機する
        2. 取得したデータの注文受付 ID が HTTP API と同じ ID ならストリームを抜ける

        .. note::

            DataStore の注文やポジションを利用してアルゴリズムで注文条件を管理している場合、**この待機処理は重要です** 。

            HTTP API で注文した結果は WebSocket の注文イベントとして流れてきます。
            その注文イベントによって DataStore のデータが更新されます。
            しかしその WebSocket の注文イベントはいつ流れてくるか分かりません。
            このサンプルコードでは 1 秒後に次のループに移ります。
            bitFlyer の取引マッチングエンジンが混雑している場合、 1 秒より後に流れてくるかもしれません。
            そうすると、DataStore が同期されていないので次のループでは **既存の注文がない** ことになります。
            サンプルコードでのアルゴリズムは、既存の注文がない場合指値注文をするので **重複注文が発生することになります** 。

            WebSocket を利用しつつ注文やポジションを厳密に管理するアプローチでは、このようにして待機処理を行います。
            もちろん、このように厳密に管理せず小口で注文するようなアプローチも考えられるので、あなたのトレード戦略にあったアプローチを検討してください。

4. 1 秒待機して次のループに移る


Place Order
-----------

Hyperliquid
~~~~~~~~~~~

.. _examples-place-order-hyperliquid:

.. literalinclude:: ../examples/order/hyperliquid.py


Order Book watching
-------------------

対応取引所の :ref:`取引所固有の DataStore <exchange-specific-datastore>` を利用した板情報を監視するサンプルコードです。

このサンプルコードでは以下について理解できるでしょう。

1. それぞれの取引所に WebSocket 接続する
2. WebSocket でチャンネルを購読する
3. Order Book 系ストアの扱い方
4. Order Book 系ストアのデータ構造

bitFlyer
~~~~~~~~

.. literalinclude:: ../examples/datastore/bitflyer.py

GMO Coin
~~~~~~~~

.. literalinclude:: ../examples/datastore/gmocoin.py

bitbank
~~~~~~~

.. literalinclude:: ../examples/datastore/bitbank.py

Coincheck
~~~~~~~~~

.. literalinclude:: ../examples/datastore/coincheck.py

Bybit
~~~~~

.. literalinclude:: ../examples/datastore/bybit.py

Binance
~~~~~~~

.. literalinclude:: ../examples/datastore/binance.py

OKX
~~~

.. literalinclude:: ../examples/datastore/okx.py

Phemex
~~~~~~

.. literalinclude:: ../examples/datastore/phemex.py

Bitget
~~~~~~

.. literalinclude:: ../examples/datastore/bitget.py

KuCoin
~~~~~~

.. literalinclude:: ../examples/datastore/kucoin.py

BitMEX
~~~~~~

.. literalinclude:: ../examples/datastore/bitmex.py

Hyperliquid
~~~~~~~~~~~

.. literalinclude:: ../examples/datastore/hyperliquid.py

Helpers
-------

.. _GMOCoinHelper:

GMO Coin
~~~~~~~~

:class:`.helpers.GMOCoinHelper` を利用したサンプルコードです。

:meth:`~.helpers.GMOCoinHelper.manage_ws_token` を利用することで、`Private WebSocket のアクセストークン <https://api.coin.z.com/docs/#ws-auth-post>`_ を管理します。
デフォルトでは 5 分ごとにアクセストークンを延長します。 延長が失敗した場合は、アクセストークンを新しく作成します。
このメソッドは無限ループとなっているので、 :meth:`asyncio.create_task` でタスクとしてスケジュールしてください。

以下は適当なチャンネルを購読して、アクセストークン管理ヘルパーのタスクをスケジュールするサンプルコードです。

.. literalinclude:: ../examples/helpers/gmocoin.py
