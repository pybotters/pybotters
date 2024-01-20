Contributing
============

pybottersはオープンソースソフトウェアですので、どなたでも開発に参加できます。
当プロジェクトに参加する方法や選定しているツールなどの環境構築する方法を記載します。

Python
------

pybottersはPython 3.8以上を対象としています。 可能な限り最新のPython
3.8でコーディングを行ってください。

参考 Python 3.8のインストール～仮想環境の作成方法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

poetry
------

`poetry <https://python-poetry.org>`__ はPythonの依存関係管理とパッケージングを支援するツールです。
仮想環境に開発ライブラリをインストールする為に使用します。

参考 poetryのインストール～依存関係インストール
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   # 1. Install poetry
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
(これらはpoetryによってインストールされます。)

コードをコミットする際にはこれらを適用してください。

参考 blackの適用方法
~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   # 手動で適用する場合
   balck .

   # VS Codeで自動適用を利用する場合
   # .vscode/settings.json を編集
   # {
   #     "python.formatting.provider": "black",
   #     "editor.formatOnSave": true
   # }

参考 flake8の適用方法
~~~~~~~~~~~~~~~~~~~~~

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
(ライブラリはpoetryによってインストールされます。)

実装したロジックに対するテストコードを作成してください。
また、テストはGitHub
Actionsによってリモートリポジトリコミット時に自動実行されます。

テストの基準
~~~~~~~~~~~~

-  現状、DataStoreに関するテストコードは省いています。(※開発速度優先の為。正式版リリースまでには対応する予定)
-  それ以外の部分についてはテストを追加してください。
-  外部との通信部分はモック化してください。

参考 pytestの実行方法
~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   pytest

Pull Request
------------

pybottersをForkして、 `developブランチ <https://github.com/MtkN1/pybotters/tree/develop>`__
を元にコードを作成してください。 Pull
Requestは同ブランチに対して行ってください。
またコミットメッセージはできれば、「英文～～～
(#存在する関連イシュー番号)」で行ってください。

参考 クローン～developブランチチェックアウト
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   git clone https://github.com/[YourAccountName]/pybotters
   git checkout develop

設計思想や細かい変数名のデザインなどは、レビューし修正コードを提案します。
お気軽にプルリクください！

OSS開発にご興味がある方、是非プロジェクトにご参加ください✨🍰✨
