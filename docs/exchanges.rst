Exchanges
=========

対応取引所における pybotters の個別の仕様について説明します。

コード例などについては :doc:`examples` をご覧ください。


bitFlyer
--------

https://lightning.bitflyer.com/docs

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bitflyer": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://lightning.bitflyer.com/docs#%E8%AA%8D%E8%A8%BC
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信されます (*JSON-RPC 2.0 over WebSocket* のみ) 。

    https://bf-lightning-api.readme.io/docs/realtime-api-auth

WebSocket
~~~~~~~~~

bitFlyer の WebSocket には *Socket.IO* と *JSON-RPC 2.0 over WebSocket* がありますが、
pybotters の認証と DataStore は *JSON-RPC 2.0 over WebSocket* のみ対応しています。

DataStore
~~~~~~~~~

* :class:`.bitFlyerDataStore` (*JSON-RPC 2.0 over WebSocket* のみ)

以下の DataStore に格納される値は pybotters による独自実装です。 また特定のキーのみが更新されます。
    * :attr:`.bitFlyerDataStore.positions`
        * ``size`` キーのみが更新されます。
    * :attr:`.bitFlyerDataStore.collateral`
        * ``collateral`` キーのみが更新されます。
    * :attr:`.bitFlyerDataStore.balance`
        * ``amount`` キーのみが更新されます。
    .. warning::
        bitFlyer の WebSocket チャンネル ``child_order_events`` は各種データを提供しておらず、計算の元となる約定情報のみを提供しています。 その為 ``bitFlyerDataStore`` は約定情報から独自に各種データを計算しています。 値が正確になるよう努めていますが、端数処理などの影響で実データとズレが生じる可能性があることに注意してください。 正確な値を必要とする場合は、HTTP API による :meth:`.bitFlyerDataStore.initialize` を利用してください。

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* をご覧ください。


GMO Coin
--------

https://api.coin.z.com/docs/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"gmocoin": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://api.coin.z.com/docs/#authentication-private
* WebSocket 認証
    GMO Coin はトークン認証方式です。

    https://api.coin.z.com/docs/#authentication-private-ws

    :class:`.helpers.GMOCoinHelper` には「アクセストークン」を管理する機能があります。

    :class:`.helpers.GMOCoinHelper` を利用すると「アクセストークンを延長」と「アクセストークンを取得」を自動で実行します。
    さらに取得したアクセストークンから Private WebSocket URL を構築して :attr:`.WebSocketApp.url` を自動で更新します。
    通常、 `GMO コインの定期メンテナンス <https://support.coin.z.com/hc/ja/articles/115007815487-%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E3%83%A1%E3%83%B3%E3%83%86%E3%83%8A%E3%83%B3%E3%82%B9%E6%99%82%E9%96%93%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6%E6%95%99%E3%81%88%E3%81%A6%E3%81%8F%E3%81%A0%E3%81%95%E3%81%84>`_
    後はアクセストークンは失効して Private WebSocket の再接続は失敗してしまいます。
    このヘルパーを使うと、失効したアクセストークンを自動で再取得するので、メンテナンス後の再接続を確立するのに便利です。

    利用可能なコードは :ref:`Examples GMOCoinHelper <GMOCoinHelper>` をご覧ください。

WebSocket
~~~~~~~~~

* レート制限
    pybotters は GMO コインの WebSocket API の購読レート制限に対応しています。

    https://api.coin.z.com/docs/#restrictions

    :meth:`.Client.ws_connect` でメッセージを送信する際、レート制限が自動適用されます。

DataStore
~~~~~~~~~

* :class:`.GMOCoinDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* をご覧ください。


bitbank
-------

https://github.com/bitbankinc/bitbank-api-docs

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bitbank": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。 認証方式は ``ACCESS-TIME-WINDOW`` を採用します。

    https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api_JP.md#%E8%AA%8D%E8%A8%BC
* WebSocket 認証
    *現時点で Private WebSocket API はありません*

WebSocket
~~~~~~~~~

* Socket.IO
    bitbank の WebSocket は Socket.IO で実装されています。
    pybotters は Socket.IO にネイティブでは対応していない為、低レベルで URL の指定と購読リクエストを送信をする必要があります。

    低レベルで Socket.IO の購読リクエストには :meth:`.Client.ws_connect` の引数 ``send_str`` を ``'42["join-room","depth_whole_btc_jpy"]'`` のように指定します。

    また pybotters は Socket.IO v4 に対応していません。
    接続するには URL で v3 ``EIO=3`` を指定する必要があります。

    利用可能なコードは :doc:`examples` をご覧ください。
* Ping-Pong
    * Socket.IO の Ping-Pong が自動で送信されます。

DataStore
~~~~~~~~~

* :class:`.bitbankDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* をご覧ください。


Coincheck
---------

https://coincheck.com/ja/documents/exchange/api

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"coincheck": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://coincheck.com/ja/documents/exchange/api#auth
* WebSocket 認証
    *現時点で Private WebSocket API はありません*

DataStore
~~~~~~~~~

* :class:`.CoincheckDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* をご覧ください。


OKJ
---

https://dev.okcoin.jp/en/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"okj": ["API_KEY", "API_SERCRET", "API_PASSPHRASE"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://dev.okcoin.jp/en/#summary-yan-zheng
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信されます。

    https://dev.okcoin.jp/en/#spot_ws-login

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信されます。

    https://dev.okcoin.jp/en/#spot_ws-limit

DataStore
~~~~~~~~~

未サポート。


BitTrade
--------

https://api-doc.bittrade.co.jp/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bittrade": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://api-doc.bittrade.co.jp/#4adc7a21f5
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信されます。

    https://api-doc.bittrade.co.jp/#7a52d716ff

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信されます。

    * https://api-doc.bittrade.co.jp/#401564b16d
    * https://api-doc.bittrade.co.jp/#111d6cb2aa

DataStore
~~~~~~~~~

未サポート。


Bybit
-----

https://bybit-exchange.github.io/docs/v5/intro

V5 API のみ対応しています。 V3 API には対応していません。

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bybit": ["API_KEY", "API_SERCRET"]}``
    * ``{"bybit_demo": ["API_KEY", "API_SERCRET"]}``
    * ``{"bybit_testnet": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://bybit-exchange.github.io/docs/v5/guide#authentication
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信されます。

    https://bybit-exchange.github.io/docs/v5/ws/connect#authentication

    また Websocket Trade API におけるメッセージ送信では ``header`` オブジェクトにタイムスタンプ ``X-BAPI-TIMESTAMP`` が自動付与されます。

    https://bybit-exchange.github.io/docs/v5/websocket/trade/guideline

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信されます。

    https://bybit-exchange.github.io/docs/v5/ws/connect#how-to-send-the-heartbeat-packet

DataStore
~~~~~~~~~

* :class:`.BybitDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* をご覧ください。


Binance
-------

https://developers.binance.com/docs/binance-spot-api-docs/CHANGELOG

pybotters は Binance API において Spot /USDⓈ-M / COIN-M / WebSocket API (Spot) で動作確認をしています。

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"binance": ["API_KEY", "API_SERCRET"]}`` (Mainnet: Spot/USDⓈ-M/COIN-M)
    * ``{"binancespot_testnet": ["API_KEY", "API_SERCRET"]}`` (Testnet: Spot)
    * ``{"binancefuture_testnet": ["API_KEY", "API_SERCRET"]}`` (Testnet: USDⓈ-M/COIN-M)
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    * https://developers.binance.com/docs/binance-spot-api-docs/rest-api#signed-endpoint-examples-for-post-apiv3order
    * https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info#signed-trade-and-user_data-endpoint-security
    * https://developers.binance.com/docs/derivatives/coin-margined-futures/general-info#signed-trade-and-user_data-endpoint-security
* WebSocket 認証
    Binance はトークン認証方式の為、ユーザーコードで URL に ``listenKey`` 含める必要があります。

    * https://developers.binance.com/docs/binance-spot-api-docs/user-data-stream
    * https://developers.binance.com/docs/derivatives/usds-margined-futures/user-data-streams/Connect
    * https://developers.binance.com/docs/derivatives/coin-margined-futures/user-data-streams/Connect

    ただし Binance 系 DataStore に ``listenKey`` を管理する機能があります。

    Binance 系 DataStore の ``initialize()`` は「*Create a ListenKey*」系の POST リクエストに対応しています。
    これにより ``listenKey`` が DataStore の属性 ``listenkey`` に格納されます。
    この属性を利用すると ``listenKey`` 付き URL を構築するのに便利です。

    また DataStore 側で「*Ping/Keep-alive a ListenKey*」系の定期リクエストが有効になる為、ユーザーコードでの延長処理は不要です。
* WebSocket 認証 (*WebSocket API*)
    pybotters では Binance で *WebSocket API* と表されるタイプの API 認証に対応しています。
    これは WebSocket メッセージで注文の作成などを可能にするもので、現時点では Spot のみ対応しています。

    https://developers.binance.com/docs/binance-spot-api-docs/web-socket-api

    送信する WebSocket メッセージに対して、取引所が定める認証情報が自動設定されます。

    https://developers.binance.com/docs/binance-spot-api-docs/web-socket-api#signed-trade-and-user_data-request-security

    これを利用するには、 :attr:`.WebSocketApp.current_ws` から ``send_json()`` メソッドを利用して引数 ``auth=pybotters.Auth`` を設定します。

WebSocket
~~~~~~~~~

* レート制限
    pybotters は Binance Spot のみにある WebSocket API の購読レート制限に対応しています。

    https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#websocket-limits

    :meth:`.Client.ws_connect` でメッセージを送信する際、レート制限が自動適用されます。


DataStore
~~~~~~~~~

* :class:`.BinanceSpotDataStore` (Spot)
* :class:`.BinanceUSDSMDataStore` (USDⓈ-M)
* :class:`.BinanceCOINMDataStore` (COIN-M)

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* をご覧ください。


OKX
---

https://www.okx.com/docs-v5/en/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"okx": ["API_KEY", "API_SERCRET", "API_PASSPHRASE"]}`` (Live trading)
    * ``{"okx_demo": ["API_KEY", "API_SERCRET", "API_PASSPHRASE"]}`` (Demo trading)
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://www.okx.com/docs-v5/en/#overview-rest-authentication
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信されます。

    https://www.okx.com/docs-v5/en/#overview-websocket-login

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信されます。

    https://www.okx.com/docs-v5/en/#overview-websocket-overview

DataStore
~~~~~~~~~

* :class:`.OKXDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* をご覧ください。


Phemex
------

https://phemex-docs.github.io/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"phemex": ["API_KEY", "API_SERCRET"]}`` (Mainnet)
    * ``{"phemex_testnet": ["API_KEY", "API_SERCRET"]}`` (Testnet)
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://phemex-docs.github.io/#rest-request-header
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信されます。

    https://phemex-docs.github.io/#user-authentication

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信されます。

    https://phemex-docs.github.io/#heartbeat

DataStore
~~~~~~~~~

* :class:`.PhemexDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* をご覧ください。


Bitget
------

https://www.bitget.com/api-doc/common/intro

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bitget": ["API_KEY", "API_SERCRET", "API_PASSPHRASE"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://www.bitget.com/api-doc/common/signature
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信されます。

    https://www.bitget.com/api-doc/common/websocket-intro

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信されます。

    https://www.bitget.com/api-doc/common/websocket-intro#connect

DataStore
~~~~~~~~~

* :class:`.BitgetV2DataStore`
* :class:`.BitgetDataStore`


MEXC
----

https://mexcdevelop.github.io/apidocs/spot_v3_en/

.. warning::

    MEXC Future は注文系 API が *maintenance* となっているので、**実質的に API トレードできません**。

    https://mexcdevelop.github.io/apidocs/contract_v1_en/#update-log

    また Spot についても一部銘柄 (**なんと BTC/USDT を含む**) は同じく注文系 API が利用停止になっています。

    `https://support.mexc.com/hc/ja/articles/15149585234969-MEXC-BTC-USDT-FTM-USDT-OP-USDT-DOGE-USDT各取引ペアのAPIアップグレード-及びメンテナンスに関するお知らせ <https://support.mexc.com/hc/ja/articles/15149585234969-MEXC-BTC-USDT-FTM-USDT-OP-USDT-DOGE-USDT%E5%90%84%E5%8F%96%E5%BC%95%E3%83%9A%E3%82%A2%E3%81%AEAPI%E3%82%A2%E3%83%83%E3%83%97%E3%82%B0%E3%83%AC%E3%83%BC%E3%83%89-%E5%8F%8A%E3%81%B3%E3%83%A1%E3%83%B3%E3%83%86%E3%83%8A%E3%83%B3%E3%82%B9%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E3%81%8A%E7%9F%A5%E3%82%89%E3%81%9B>`_

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"mexc": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://mexcdevelop.github.io/apidocs/spot_v3_en/#signed
* WebSocket 認証
    MEXC はトークン認証方式の為、ユーザーコードで URL に ``listenKey`` 含める必要があります。

    https://mexcdevelop.github.io/apidocs/spot_v3_en/#websocket-user-data-streams

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信されます。

    https://mexcdevelop.github.io/apidocs/spot_v3_en/#websocket-market-streams

DataStore
~~~~~~~~~

注文系 API が利用できないことを鑑みて、サポート対象外としています。


KuCoin
------

https://www.kucoin.com/docs/beginners/introduction

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"kucoin": ["API_KEY", "API_SERCRET", "API_PASSPHRASE"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://www.kucoin.com/docs/basic-info/connection-method/authentication/creating-a-request
* WebSocket 認証
    KuCoin はトークン認証方式の為、ユーザーコードで URL と ``token`` の発行をする必要があります。

    https://www.kucoin.com/docs/websocket/basic-info/apply-connect-token/private-channels-authentication-request-required-

    ただし KuCoin 系 DataStore には発行された URL と ``token`` を管理する機能があります。

    KuCoin 系 DataStore の ``initialize()`` は上記 ``/api/v1/bullet-private`` の POST リクエストに対応しています。
    これにより発行された URL と ``token`` が DataStore の属性 ``endpoint`` に格納されます。
    この属性を利用すると KuCoin の WebSocket URL を構築するのに便利です。

    また同様に ``initialize()`` は ``/api/v1/bullet-public`` の POST リクエストにも対応しています。
    https://www.kucoin.com/docs/websocket/basic-info/apply-connect-token/public-token-no-authentication-required-

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信されます。

    https://www.kucoin.com/docs/websocket/basic-info/ping

DataStore
~~~~~~~~~

* :class:`.KuCoinDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* をご覧ください。


BitMEX
------

https://www.bitmex.com/app/apiOverview

.. warning::

    BitMEX Mainnet は日本国内からは利用できません。
    Testnet のみ利用可能です。

    https://blog.bitmex.com/ja-jp-notice-to-japan-residents/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bitmex": ["API_KEY", "API_SERCRET"]}`` (Mainnet)
    * ``{"bitmex_testnet": ["API_KEY", "API_SERCRET"]}`` (Testnet)
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://www.bitmex.com/app/apiKeysUsage#Authenticating-with-an-API-Key
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報が自動設定されます。

    https://www.bitmex.com/app/wsAPI#API-Keys

DataStore
~~~~~~~~~

* :class:`.BitMEXDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* をご覧ください。

Hyperliquid
-----------

https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api


Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"hyperliquid": ["SECRET_KEY"]}`` (Mainnet)
    * ``{"hyperliquid_testnet": ["SECRET_KEY"]}`` (Testnet)
* HTTP 認証
    `Exchange endpoint <https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint>`_ (``/exchange``) へのリクエストに対して以下の Request Body を省略することができます。 省略した場合、以下の値が自動設定されます。

    * ``nonce``: 現在時刻のミリ秒
    * ``signature``: ``action`` をハッシュ化し秘密鍵で署名した値

    実際の利用方法は :ref:`Examples <examples-place-order-hyperliquid>` を参照してください。
* WebSocket 認証
    まだ対応していません (Work in progress)。 以下のように手動で署名を行うことも可能です。

手動で署名をする必要がある場合は、より低レベルな署名ヘルパー :mod:`pybotters.helpers.hyperliquid` を利用してください。


DataStore
~~~~~~~~~

* :class:`.HyperliquidDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* をご覧ください。

.. warning::

    部分的なサポートです。 一部のチャンネルは未対応です。 `#354 <https://github.com/pybotters/pybotters/issues/354>`_
