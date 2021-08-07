Advanced Usage
==============

``apis`` の暗黙的な読み込み
----------------------------

``pybotters.Client`` の引数 ``apis`` を指定せず以下のように暗黙的な読み込みが可能です。

カレントディレクトリに ``apis.json`` を配置する
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pythonの実行カレントディレクトリに ``apis.json`` という名前のファイルを配置することで自動的にそのファイルを読み込ます。

.. code:: bash

   # bash
   $ ls
   apis.json

.. NOTE::
   カレントディレクトリはPython標準の ``os`` モジュールの ``getcwd`` で確認できます。

環境変数 ``PYBOTTERS_APIS`` にファイルパスを設定する
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

環境変数 ``PYBOTTERS_APIS`` に同様の形式のJSONファイルパス設定することでそのファイルを読み込みます。
カレントディレクトリ以外に配置している場合に有効です。

.. code:: bash

   # bash
   $ export PYBOTTERS_APIS=/path/to/apis.json

優先順位
~~~~~~~~

以下のような優先順位で、下位のものは設定があっても無視されます。

引数 ``apis`` の明示的な指定 ＞ カレントディレクトリの ``apis.json`` ＞ 環境変数 ``PYBOTTERS_APIS``

同期リクエスト
--------------

``pybotters`` は ``requests`` ライブラリのようにパッケージトップレベルでリクエスト関数をサポートしています。
この関数は非同期ではないので ``await`` で呼び出す必要はありません。
またはレスポンスボディの取得にも ``await`` を付ける必要はありません。

上記の ``apis`` の暗黙的な読み込みと合わせることで、REPL(対話モード)で ``pybotters`` を利用する際に便利です。

.. code:: python

   r = pybotters.request('GET', 'https://...', apis=apis)
   r = pybotters.get('https://...', params={'foo': 'bar'}, apis=apis)
   r = pybotters.post('https://...', data={'foo': 'bar'}, apis=apis)
   r = pybotters.put('https://...', data={'foo': 'bar'}, apis=apis)
   r = pybotters.delete('https://...', data={'foo': 'bar'}, apis=apis)

   print(r.text())
   print(r.json())

.. note::
   内部的には\ ``pybotters.Client``\ の非同期関数を同期的に実行しています。
   リクエスト毎にセッションは閉じられる為keep-alive接続ではありません。
