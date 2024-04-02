Contributing
============

pybotters はオープンソースソフトウェアですので、どなたでも開発に参加できます。

**あなたの Pull request やアイディアを積極的に受け入れています！**

当プロジェクトに参加する方法や選定しているツールなどの環境構築方法、リポジトリの運用方針を記載します。


TL;DR
-----

**ワークフロー**

0. (Optional) メンテナと議論が必要な場合 `Discussion <https://github.com/pybotters/pybotters/discussions>`_ または `Issue <https://github.com/pybotters/pybotters/pulls>`_ を作成する
1. マシンをセットアップする (Python 3.8, Hatch ...)
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

pybotters は最小要求を **Python 3.8** としています。
Python 3.8 の最新マイナーバージョンをインストールしてコーディングすることを推奨します。

Python のインストール方法は多岐にわたります。
`こちらの記事 (python.jp) <https://www.python.jp/install/install.html>`__ を参考にするか、または次に紹介する **Hatch** を利用してください。

.. NOTE::
    当プロジェクトは標準の ``pyproject.toml`` に則っているので通常の pip のみでもインストール可能です。
    Hatch の利用は必須ではありません。

Hatch
~~~~~

**Hatch** は PyPA より配布されているモダンで高機能なプロジェクト管理ツールです。

機能の一つとして環境作成時に **目的の Python バージョンを自動でダウンロード** します。
当プロジェクトでは Hatch 環境を定義済みなのでこれを利用すれば Python のセットアップも省略できます。
また他には環境を分離した便利なスクリプトランナーや、マトリクステストを実行できます。

https://hatch.pypa.io/latest/

Hatch をインストールするには **pipx** の利用をおすすめします。
pipx をインストールしてからその上で Hatch をインストールしましょう。

.. code:: sh

    pipx install hatch

.. NOTE::
    Codespaces 環境なら既に ``pipx`` が入っているはずです ✨


Git
---

ローカル環境を利用している場合はまず Git でコードをチェックアウトします。
Git がローカルにない場合はインストールしてください。

.. code:: sh

    git clone https://github.com/<your-account>/pybotters

.. NOTE::
    Codespaces 環境なら既に Git がインストール済みでコードがチェックアウトされているはずです ✨


Dependencies
------------

プロジェクトとその依存関係をインストールします。
**pip** または **Hatch** を利用する方法があります。

pip
~~~

仮想環境を作成して `dev` エクストラで Editable インストールします。

.. code:: sh

    python3.8 -m venv .venv

.. code:: sh

    source .venv/bin/activate

.. code:: sh

    pip install -e .[dev]

Hatch
~~~~~

Hatch の ``default`` 環境を作成すると、依存関係をインストールできます。

.. code:: sh

    hatch env create


Linter
------

当プロジェクトでは Linter / Formatter として **Ruff** を採用しています。
上記プロジェクトセットアップ時に依存関係としてインストールされます。

https://docs.astral.sh/ruff/

Format
~~~~~~

フォーマット機能を利用してコードを自動修正できます。

.. code:: bash

    ruff format; ruff check --fix-only

Hatch を利用している場合は、以下のコマンドで実行できます。

.. code:: bash

    hatch run fmt

Lint
~~~~

静的解析機能を利用してコードの品質をチェックできます。
エラー箇所を修正してからコードをコミットしてください。

.. code:: bash

    ruff format --check; ruff check

Hatch を利用している場合は、以下のコマンドで実行できます。

.. code:: bash

    hatch run lint


Testing
-------

当プロジェクトではテストに **pytest** を採用しています。
上記プロジェクトセットアップ時に依存関係としてインストールされます。

https://docs.pytest.org

実装したコードに対するテストコードを作成してください。
テストコードは ``tests/`` 配下にあります。

pytest コマンドでテストを実行できます。

.. code:: sh

    pytest tests

Hatch を利用している場合は、以下のコマンドで実行できます。

.. code:: sh

    hatch run test

全ての Python バージョンに対してテストカバレッジを実行するには、以下のコマンドを実行してください。

.. code:: sh

    hatch run all:cov

.. NOTE::
    Hatch を利用していない場合はローカルでテストマトリクスを実行するのは難しいです。
    その場合は CI でテストを実行してください。

**テストの基準**

* すべてのコードに対して **全て** テストを書いてください。 カバレッジ率は 100% です。
* 例外として :ref:`DataStore <datastore>` に関する単体テストコードは、テスト方法を確立するまで省略しています。
* ただし DataStore の動作確認ができる実環境用の機能テストコードを Pull request のコメントに張り付けてください。
* 外部との通信部分はモック化してください。


CI
--

コードをリモートブランチにプッシュすると **GitHub Actions** によって定義されている CI が実行されます。

CI は **Lint** と **Test** についてのチェックが実施されます。
これらのチェックがエラーになる場合は、コードを修正してから再度プッシュしてください。


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
