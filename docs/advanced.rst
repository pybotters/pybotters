Advanced Usage
==============

Base URL
----------------------------

ベース URL について。

Implicit loading of ``apis``
----------------------------

``pybotters.Client`` の引数 ``apis`` を指定せず以下のように暗黙的な読み込みが可能です。

1. カレントディレクトリに ``apis.json`` を配置する

Pythonの実行カレントディレクトリに ``apis.json`` という名前のファイルを配置することで自動的にそのファイルを読み込ます。

.. code:: bash

    # bash
    $ ls
    apis.json

.. NOTE::
    カレントディレクトリはPython標準の ``os`` モジュールの ``getcwd`` で確認できます。

2. 環境変数 ``PYBOTTERS_APIS`` にファイルパスを設定する

環境変数 ``PYBOTTERS_APIS`` に同様の形式のJSONファイルパス設定することでそのファイルを読み込みます。
カレントディレクトリ以外に配置している場合に有効です。

.. code:: bash

    # bash
    $ export PYBOTTERS_APIS=/path/to/apis.json

* 優先順位

以下のような優先順位で、下位のものは設定があっても無視されます。

引数 ``apis`` の明示的な指定 ＞ カレントディレクトリの ``apis.json`` ＞ 環境変数 ``PYBOTTERS_APIS``


Disable Authentication
----------------------

認証を無効にします。


Fetch data handling
-------------------

フェッチデータハンドリングについて。


aiohttp Parameters
------------------

aiohttp に渡すパラメーターについて。


Multiple Websocket senders/handlers
-----------------------------------

WebSocket で複数のメッセージ送信／ハンドラを設定する方法について。


WebSocket reconnection backoff
------------------------------

WebSocket 再接続のバックオフについて。


URL when reconnecting to WebSocket
----------------------------------

WebSocket 再接続時 URL について。


WebSocket Handshake
-------------------

WebSocket ハンドシェイクについて。


Current WebSocket connection
----------------------------

現在の WebSocket コネクションについて。


DataStore Iteration
-------------------

DataStore をイテレーションで探索する。


Maximum number of data in DataStore
-----------------------------------

DataStore の最大データ数について。


How to implement original DataStore
-----------------------------------

DataStore を実装する方法について。
