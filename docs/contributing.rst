Contributing
============

pybotters はオープンソースソフトウェアですので、どなたでも開発に参加できます。

当プロジェクトに参加する方法や選定しているツールなどの環境構築方法、リポジトリの運用方針を記載します。


TL;DR
-----

**ワークフロー**

0. マシンをセットアップする (Python 3.8, Poetry, dependencies ...)
1. メンテナと先に議論が必要な場合、Issue を作成する
2. リポジトリを Fork して Clone する、または既にある場合 origin main を pull する
3. main ブランチを元に、変更する内容を表す名称のブランチを作成する
4. 素晴らしいアイディアをソースコードに反映する 💎💎
5. pytest, black, flake8 を実行して正しいコードかチェックする
6. Pull Request を作成して、変更内容を記載する
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
Fork 及び Clone したリポジトリの main からトピックブランチを作成して、main を対象に Pull Request を送信してください。


Issue
-----

メンテナと先に議論する必要がある場合は、Issue を作成してください。

小規模な変更の場合は恐らく不要でしょう。
大規模な変更の場合は Issue で要件を確認する方が賢明です。
またはメンテナは小規模な変更でもバックログとして Issue を作成することがあるので、そのように利用しても構いません。

あなたが Pull Request を行わない場合でも、Issue でバグ報告・伺い・提案として Issue を利用することもできます。


Pull Request
------------

Branch Strategy に記したように、main を対象に Pull Request を送信してください。

タイトル及び内容は、日本語または英語で記載してください。

Pull Request はメンテナによって *Squash-and-Merge* 戦略でマージされます。
*Squash-and-Merge* 戦略とは Pull Request の変更が複数のコミットあったとしてもマージ時に 1 つに押し潰されます。

* あなたが Git に不慣れで作業経過のコミットが沢山あったとしても、それらは 1 つに押し潰されます
* あなたが Git を心得ていて沢山の素敵なコミットメッセージを残したとしても、それらは 1 つに押し潰されます

設計思想や細かい変数名のデザインなどは、レビューし修正コードを提案します。
お気軽にプルリクください！

OSS 開発にご興味がある方、是非プロジェクトにご参加ください✨🍰✨
