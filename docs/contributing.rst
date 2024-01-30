Contributing
============

pybotters はオープンソースソフトウェアですので、どなたでも開発に参加できます。

**あなたの Pull request やアイディアを積極的に受け入れています！**

当プロジェクトに参加する方法や選定しているツールなどの環境構築方法、リポジトリの運用方針を記載します。


TL;DR
-----

**ワークフロー**

0. マシンをセットアップする (Python 3.8, Poetry, venv, dependencies ...)
1. (Optional) メンテナと議論が必要な場合 `Discussion <https://github.com/MtkN1/pybotters/discussions>`_ または `Issue <https://github.com/MtkN1/pybotters/pulls>`_ を作成する
2. リポジトリを Fork する
3. main ブランチを元に、変更する内容を表す名称のブランチ (トピックブランチ) を作成する
4. あなたのアイディアをソースコードに反映する 💎💎
5. pytest, black, flake8 を実行して正しいコードかチェックする
6. Pull request を作成して、変更内容を記載する
7. レビューを受け、必要なら修正を行う
8. あなたのソースコードがマージされます 🚀🚀


Dev Container
-------------

(**Optional**)

pybotters は VS Code の `Dev Container <https://code.visualstudio.com/docs/remote/containers>`_ を定義しています。
Dev Container を利用するには VS Code と Docker が必要です。

Dev Container の機能を用いることで以降の項目で説明している開発に必要なソフトウェアや設定を自動で構築することが出来ます。

* Python 3.8
* Poetry
* 依存ライブラリ
* Formatter と Linster の設定

ただし pybotters はピュアな Python プロジェクトなのでそれほど難しい依存関係はありません。
お使いの環境にて個々にツールをインストールして頂くことで環境を構築することもできます。


Python
------

pybotters は最小要求を Python 3.8 以上としています。 Python 3.8 の最新マイナーで
コーディングすることをおすすめします。

**参考 Python 3.8 のインストール～仮想環境作成の簡易サンプル**

.. code:: bash

    # 1. Install build dependencies.
    # See pyenv Wiki
    # https://github.com/pyenv/pyenv/wiki#suggested-build-environment

    # 2. Get latest Python 3.8 source, extract it.
    wget https://www.python.org/ftp/python/3.8.18/Python-3.8.18.tgz
    # See here for the latest Python 3.8.
    # https://www.python.org/downloads/source/
    tar -xf Python-3.8.18.tgz

    # 3. Build, Install.
    cd Python-3.8.18
    ./configure --prefix=${HOME}/.local && make && make altinstall

    # 4. Create virtual environment, activate it.
    ~/.local/bin/python3.8 -m venv ~/.venv/pybotters
    . ~/.venv/pybotters/bin/activate

Poetry
------

`Poetry <https://python-poetry.org>`__ は Python の依存関係管理とパッケージングを支援するツールです。
仮想環境に開発ライブラリをインストールする為に使用します。

**参考 Poetry のインストール～依存関係インストール**

.. code:: sh

    # 1. Install Poetry
    # See https://python-poetry.org/docs/#installation

    # 2. Install dependencies.
    # Activate venv.
    . ~/.venv/pybotters/bin/activate
    # Clone pybotters
    git clone https://github.com/MtkN1/pybotters
    cd pybotters
    # Install.
    poetry install

Formatter, Linter
-----------------

当プロジェクトではフォーマッターは
`black <https://black.readthedocs.io/en/stable/>`__, リンターは
`flake8 <https://flake8.pycqa.org/en/latest/>`__ を採用しています。
(これらは Poetry によってインストールされます。)

コードをコミットする際にはこれらを適用してください。

**参考 blackの適用方法**

.. code:: bash

    # 手動で適用する場合
    balck .

    # VS Codeで自動適用を利用する場合
    # .vscode/settings.json を編集
    # {
    #     "python.formatting.provider": "black",
    #     "editor.formatOnSave": true
    # }

**参考 flake8 の適用方法**

.. code:: bash

    # 手動でチェックする場合(確認後、コードを修正してください)
    flake8 .

    # VS Codeで自動チェックする場合
    # .vscode/settings.json を編集
    # {
    #     "python.linting.flake8Enabled": true,
    #     "python.linting.enabled": true,
    #     "python.linting.pylintEnabled": false
    # }

Testing
-------

当プロジェクトではテストに `pytest <https://docs.pytest.org>`__ を採用しています。
(ライブラリは Poetry によってインストールされます。)

実装したロジックに対するテストコードを作成してください。
テストコードは ``tests/`` 配下にあります。
また、テストは GitHub
Actions によってプッシュ時及び Pull request 作成時に自動実行されます。

**テストの基準**

* 現状 :ref:`DataStore <datastore>` に関する単体テストコードは、テスト方法を確立するまで省略しています。
    * ただし DataStore の動作確認ができる実環境用の機能テストコードを Pull request のコメントに張り付けてください。
* それ以外の部分については単体テストを追加してください。
* 外部との通信部分はモック化してください。

**参考 pytest の実行方法**

.. code:: sh

    pytest tests/


Branch Strategy
---------------

GitHub Flow (`日本語訳 <https://gist.github.com/Gab-km/3705015>`_) に従います。

main ブランチが最新の開発ブランチです。
Fork 及び Clone したリポジトリの main からトピックブランチを作成して、main を対象に Pull request を送信してください。


Discussion and Issue
--------------------

**Discussion 👉 Issue 👉 Pull request 👉 Merge!!**

バグの疑いがある動作を発見したり、追加の機能リクエスト、質問などがある場合は `GitHub Discussion <https://github.com/MtkN1/pybotters/discussions>`_ から始めましょう。
その内容についてメンテナと議論して明確な回答を得ることができます。

Discussion によってバグの修正や追加機能などの課題が明確化した場合は、その内容を `GitHub Issue <https://github.com/MtkN1/pybotters/pulls>`_ にエスカレーションします。
Issue はやるべきことのトラッカーとして利用します。
メンテナまたはコントリビューターはこの Issue リストを元に Pull request をします。

しかし、このプロセスに完全に則る必要はありません。
内容が明確に感じている場合は Issue から作成しても問題ないし、初めから Pull request を作成しても構いません。
例えば明らかな小規模バグやドキュメントの誤字修正は Pull request から始めるのが早いです。
ただし、内容が間違っていたりプロジェクトの方針と異なる場合は我々はご提案を受け付けることができない場合があります。
内容に不安を感じるのでれば、あなたの時間を無駄にしない為にも Discussion から始めるのがベストだと思います 💬

もちろん Discord サーバーでカジュアルにチャットするのでも構いません！


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
