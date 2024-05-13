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
    GMO Coin はトークン認証方式の為、ユーザーコードで URL に「アクセストークン」含める必要があります。

    https://api.coin.z.com/docs/#authentication-private-ws

    ただし :class:`.GMOCoinDataStore` 及び :class:`.helpers.GMOCoinHelper` に「アクセストークン」を管理する機能があります。

    :meth:`.GMOCoinDataStore.initialize` は「アクセストークンを取得」の POST リクエストに対応しています。
    これにより「アクセストークン」が属性 :attr:`.GMOCoinDataStore.token` に格納されます。
    この属性を利用するとトークン付き URL を構築するのに便利です。

    また DataStore 側で「アクセストークンを延長」の定期リクエストが有効になる為、ユーザーコードでの延長処理は不要です。

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
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

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


Bybit
-----

https://bybit-exchange.github.io/docs/v5/intro

V5 API のみ対応しています。 V3 API には対応していません。

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bybit": ["API_KEY", "API_SERCRET"]}``
    * ``{"bybit_testnet": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://bybit-exchange.github.io/docs/v5/guide#authentication
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信されます。

    https://bybit-exchange.github.io/docs/v5/ws/connect#authentication

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

https://binance-docs.github.io/apidocs/spot/en/

pybotters は Binance API において Spot /USDⓈ-M / COIN-M / WebSocket API (Spot) で動作確認をしています。

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"binance": ["API_KEY", "API_SERCRET"]}`` (Mainnet: Spot/USDⓈ-M/COIN-M)
    * ``{"binancespot_testnet": ["API_KEY", "API_SERCRET"]}`` (Testnet: Spot)
    * ``{"binancefuture_testnet": ["API_KEY", "API_SERCRET"]}`` (Testnet: USDⓈ-M/COIN-M)
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    * https://binance-docs.github.io/apidocs/spot/en/#signed-trade-user_data-and-margin-endpoint-security
    * https://binance-docs.github.io/apidocs/futures/en/#signed-trade-and-user_data-endpoint-security
    * https://binance-docs.github.io/apidocs/delivery/en/#signed-trade-and-user_data-endpoint-security
* WebSocket 認証
    Binance はトークン認証方式の為、ユーザーコードで URL に ``listenKey`` 含める必要があります。

    * https://binance-docs.github.io/apidocs/spot/en/#user-data-streams
    * https://binance-docs.github.io/apidocs/futures/en/#user-data-streams
    * https://binance-docs.github.io/apidocs/delivery/en/#user-data-streams

    ただし Binance 系 DataStore に ``listenKey`` を管理する機能があります。

    Binance 系 DataStore の ``initialize()`` は「*Create a ListenKey*」系の POST リクエストに対応しています。
    これにより ``listenKey`` が DataStore の属性 ``listenkey`` に格納されます。
    この属性を利用すると ``listenKey`` 付き URL を構築するのに便利です。

    また DataStore 側で「*Ping/Keep-alive a ListenKey*」系の定期リクエストが有効になる為、ユーザーコードでの延長処理は不要です。
* WebSocket 認証 (*WebSocket API*)
    pybotters では Binance で *WebSocket API* と表されるタイプの API 認証に対応しています。
    これは WebSocket メッセージで注文の作成などを可能にするもので、現時点では Spot のみ対応しています。

    https://binance-docs.github.io/apidocs/websocket_api/en/

    送信する WebSocket メッセージに対して、取引所が定める認証情報が自動設定されます。

    https://binance-docs.github.io/apidocs/websocket_api/en/#signed-trade-and-user_data-request-security

    これを利用するには、 :attr:`.WebSocketApp.current_ws` から ``send_json()`` メソッドを利用して引数 ``auth=pybotters.Auth`` を設定します。

WebSocket
~~~~~~~~~

* レート制限
    pybotters は Binance Spot のみにある WebSocket API の購読レート制限に対応しています。

    https://binance-docs.github.io/apidocs/spot/en/#limits

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

https://bitgetlimited.github.io/apidoc/en/mix/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bitget": ["API_KEY", "API_SERCRET", "API_PASSPHRASE"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定されます。

    https://bitgetlimited.github.io/apidoc/en/mix/#signature
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信されます。

    https://bitgetlimited.github.io/apidoc/en/mix/#login

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信されます。

    https://bitgetlimited.github.io/apidoc/en/mix/#connect

DataStore
~~~~~~~~~

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
