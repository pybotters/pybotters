Contributing
============

pybotters はオープンソースソフトウェアですので、どなたでも開発に参加できます。

**あなたの Pull request やアイディアを積極的に受け入れています！**

当プロジェクトに参加する方法や選定しているツールなどの環境構築方法、リポジトリの運用方針を記載します。


TL;DR
-----

**ワークフロー**

0. (Optional) メンテナと議論が必要な場合 `Discussion <https://github.com/pybotters/pybotters/discussions>`_ または `Issue <https://github.com/pybotters/pybotters/pulls>`_ を作成する
1. マシンをセットアップする (Python 3.9, uv ...)
2. リポジトリを Fork する
3. main ブランチを元に、変更する内容を表す名称のブランチ (トピックブランチ) を作成する
4. あなたのアイディアをソースコードに反映する 💎💎
5. pytest, ruff を実行して正しいコードかチェックする
6. コードをプッシュして CI をパスする
7. Pull request を作成して、変更内容を記載する
8. レビューを受け、必要なら修正を行う
9. あなたのソースコードがマージされます 🚀🚀


Discussion and Issue
--------------------

**Discussion 👉 Issue 👉 Pull request 👉 Merge!!**

バグの疑いがある動作を発見したり、追加の機能リクエスト、質問などがある場合は `GitHub Discussion <https://github.com/pybotters/pybotters/discussions>`_ から始めましょう。
その内容についてメンテナと議論して明確な回答を得ることができます。

Discussion によってバグの修正や追加機能などの課題が明確化した場合は、その内容を `GitHub Issue <https://github.com/pybotters/pybotters/pulls>`_ にエスカレーションします。
Issue はやるべきことのトラッカーとして利用します。
メンテナまたはコントリビューターはこの Issue リストを元に Pull request をします。

しかし、このプロセスに完全に則る必要はありません。
内容が明確に感じている場合は Issue から作成しても問題ないし、初めから Pull request を作成しても構いません。
例えば明らかな小規模バグやドキュメントの誤字修正は Pull request から始めるのが早いです。
ただし、内容が間違っていたりプロジェクトの方針と異なる場合は我々はご提案を受け付けることができない場合があります。
内容に不安を感じるのでれば、あなたの時間を無駄にしない為にも Discussion から始めるのがベストだと思います 💬

もちろん Discord サーバーでカジュアルにチャットするのでも構いません！


Computing
---------

プロジェクトに貢献するためには、Python を実行する為のコンピューティング環境を用意します。
**ローカル** または **Codespaces** を利用する方法があります。

Local
~~~~~

いつも通りのあなたが使用しているコンピューターの環境です。

Codespaces
~~~~~~~~~~

より簡単にセットアップするには **GitHub Codespaces** がおすすめです。

https://docs.github.com/ja/codespaces

GitHub Codespaces は GitHub が提供するクラウドベースの開発環境です。
誰でも無料枠があるので OSS にコントリビュートするのに最適です。

``Code`` ボタンからクリックするだけで Web 上から簡単に Codespaces 環境を立ち上げることができます。
使い終わった環境は削除することができるので、ローカル環境を汚すことなくプロジェクトに貢献できます。


Python
------

pybotters は最小要求を **Python 3.9** としています。
Python 3.9 の最新マイナーバージョンをインストールしてコーディングすることを推奨します。

Python のインストール方法は多岐にわたります。
`こちらの記事 (python.jp) <https://www.python.jp/install/install.html>`__ を参考にするか、または次に紹介する **uv** を利用してください。

uv
--

**uv** は Astral によって開発されている非常に高速な Python プロジェクトマネージャーです。

uv は機能の一つとして環境作成時に **目的の Python バージョンを自動でダウンロード** するので基本的なセットアップを省略できます。
当プロジェクトでは作業ごとの uv コマンドを Bash スクリプトとして定義済みなので (``scripts`` 配下) これを利用することで簡単にテストなどを実行できます。

https://docs.astral.sh/uv/

uv は上記公式ドキュメントからインストールしてください。


Git
---

まずは `pybotters の GitHub リポジトリ <https://github.com/pybotters/pybotters>`_ を Fork してください。

ローカル環境を利用している場合は Git でコードをチェックアウトします。
Git がローカルにない場合はインストールしてください。

.. code:: sh

    git clone https://github.com/<your-account>/pybotters

.. NOTE::
    Codespaces 環境なら既に Git がインストール済みでコードがチェックアウトされているはずです ✨


Dependencies
------------

仮想環境の作成と、プロジェクト及び依存関係をインストールします。

.. code:: sh

    ./scripts/sync


CI
--

コードをリモートブランチにプッシュすると **GitHub Actions** によって定義されている CI が実行されます。

CI は **Static analysis** と **Type check** 及び **Test** についてのチェックが実施されます。
これらのチェックがエラーになる場合は、コードを修正してから再度プッシュしてください。
またはローカルでチェックを実施する場合は、以下の手順を参考にしてください。


Static analysis
---------------

当プロジェクトではコード静的解析として **Ruff** を採用しています。
上記プロジェクトセットアップ時に依存関係としてインストールされます。

https://docs.astral.sh/ruff/

Format
~~~~~~

フォーマット機能を利用してコードを自動修正できます。

.. code:: bash

    ./scripts/format

Lint
~~~~

静的解析機能を利用してコードの品質をチェックできます。

.. code:: bash

    ./scripts/lint


Type check
----------

当プロジェクトではタイプチェッカーとして **mypy** を採用しています。
上記プロジェクトセットアップ時に依存関係としてインストールされます。

https://mypy.readthedocs.io/

型チェックのコマンドは以下の通りです。

.. code:: bash

    ./scripts/typing


Testing
-------

当プロジェクトではテストに **pytest** を採用しています。
上記プロジェクトセットアップ時に依存関係としてインストールされます。

https://docs.pytest.org

実装したコードに対するテストコードを作成してください。
テストコードは ``tests/`` 配下にあります。

.. code:: sh

    ./scripts/test

全ての Python バージョンに対してテストカバレッジを実行するには、以下のコマンドを実行してください。

.. code:: sh

    ./scripts/test-all

テストを実行すると標準出力と HTML のカバレッジレポートが生成されます。
HTML のレポートを確認するには、以下のコマンドを実行してください。

.. code:: sh

    python -m http.server -d htmlcov

**テストの基準**

* すべてのコードに対して **全て** テストを書いてください。 カバレッジ率は 100% です。
* 例外として :ref:`DataStore <datastore>` に関する単体テストコードは、テスト方法を確立するまで省略しています。
* ただし DataStore の動作確認ができる実環境用の機能テストコードを Pull request のコメントに張り付けてください。
* 外部との通信部分はモック化してください。


Documentation
-------------

Sphinx ドキュメントを自動ビルドしてローカル環境で閲覧することができます。

.. code:: sh

    ./scripts/serve

ローカル環境にホストせずにドキュメントをビルドすることもできます。

.. code:: sh

    ./scripts/docs


Branch Strategy
---------------

GitHub Flow (`日本語訳 <https://gist.github.com/Gab-km/3705015>`_) に従います。

main ブランチが最新の開発ブランチです。
Fork 及び Clone したリポジトリの main からトピックブランチ (例: ``fix-some-auth``)を作成します。

.. code:: sh

    git switch -c fix-some-auth main

変更したコードをリモートにプッシュしたら upstream/main を対象に Pull request を送信してください。


Pull request
------------

Branch Strategy に記したように、main ブランチを対象に Pull request を送信してください。

Pull request タイトルは、英語でかつコミットメッセージとなる文で記述することを推奨します。
(例: *Fix xxx in SomeExchangeDataStore* *Support SomeExchange HTTP auth* など)
内容については日本語でも構いません。

Pull request はメンテナによって *Squash-and-Merge* 戦略でマージされます。
*Squash-and-Merge* 戦略とは Pull request の変更が複数のコミットあったとしてもマージ時に 1 つに押し潰されます。

* あなたが Git に不慣れで作業経過のコミットが沢山あったとしても、それらは 1 つに押し潰されます
* あなたが Git を心得ていて沢山の素敵なコミットメッセージを残したとしても、それらは 1 つに押し潰されます

設計思想や細かい変数名のデザインなどは、レビューし修正コードを提案します。
お気軽にプルリクください！

OSS 開発にご興味がある方、是非プロジェクトにご参加ください✨🍰✨
