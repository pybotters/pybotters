.. pybotters documentation master file, created by
    sphinx-quickstart on Thu Aug  5 19:33:41 2021.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

pybotters Docs
==============

.. toctree::
    :maxdepth: 2
    :hidden:

    user-guide
    advanced
    exchanges
    examples
    reference
    contributing


**pybotters** は仮想通貨取引所向けの **非同期 HTTP / WebSocket API クライアント** です。

様々な取引所の Private API 認証に対応しており、素早くトレード bot を構築することができます。
また **WebSocket** と **DataStore** の機能を使うことで、リアルタイムデータを簡単に利用できます。


Installation
------------

pybotters は PyPI または GitHub からインストールできます。

From `PyPI <https://pypi.org/project/pybotters/>`_ (リリースバージョン):

.. code-block:: console

    $ pip install pybotters

From `GitHub <https://github.com/MtkN1/pybotters>`_ (開発バージョン):

.. code-block:: console

    $ pip install git+https://github.com/MtkN1/pybotters.git


Usage
-----

`bitFlyer <https://lightning.bitflyer.com/trade>`_ の Private HTTP API と WebSocket API を利用する例です。

* HTTP API (Get Balance):

.. code-block:: python

    import asyncio

    import pybotters


    async def main():
        apis = {"bitflyer": ["BITFLYER_API_KEY", "BITFLYER_API_SECRET"]}

        async with pybotters.Client(
            apis=apis, base_url="https://api.bitflyer.com"
        ) as client:
            r = await client.fetch("GET", "/v1/me/getbalance")

            print(r.data)


    if __name__ == "__main__":
        asyncio.run(main())

.. note::
    :class:`pybotters.Client` に API 情報 ``apis`` を入力することで、HTTP リクエストの **自動認証機能** が有効になります。

* WebSocket API (Ticker channel):

.. code-block:: python

    import asyncio

    import pybotters


    async def main():
        async with pybotters.Client() as client:
            wsqueue = pybotters.WebSocketQueue()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "lightning_ticker_BTC_JPY"},
                },
                hdlr_json=wsqueue.onmessage,
            )

            async for msg in wsqueue:  # Ctrl+C to break
                print(msg)


    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass

.. note::
    :meth:`pybotters.Client.ws_connect` により、自動再接続機構を備えた WebSocket コネクションが作成されます。

.. warning::
    WebSocket メッセージの受信は永続的に実行されます。 プログラムを終了するには ``Ctrl+C`` を入力します。


What's next
-----------

まずは :doc:`user-guide` ページで pybotters の利用方法を学習しましょう。


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
