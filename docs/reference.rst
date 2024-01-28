API Reference
=============

Client class
------------

.. autosummary::
   :toctree: generated

   pybotters.Client


Fetch API Returns
-----------------

.. autosummary::
   :toctree: generated

   pybotters.FetchResult
   pybotters.NotJSONContent


WebSocket API Returns
---------------------

.. autosummary::
   :toctree: generated

   pybotters.WebSocketApp


WebSocket handlers
------------------

.. autosummary::
   :toctree: generated

   pybotters.WebSocketQueue


.. _exchange-specific-websocket-handlers:

Exchange-specific WebSocket handlers
------------------------------------

.. autosummary::
   :toctree: generated

   pybotters.BinanceCOINMDataStore
   pybotters.BinanceSpotDataStore
   pybotters.BinanceUSDSMDataStore
   pybotters.BitMEXDataStore
   pybotters.BitgetDataStore
   pybotters.BybitDataStore
   pybotters.CoincheckDataStore
   pybotters.GMOCoinDataStore
   pybotters.KuCoinDataStore
   pybotters.OKXDataStore
   pybotters.PhemexDataStore
   pybotters.bitFlyerDataStore
   pybotters.bitbankDataStore


Abstract WebSocket handlers
---------------------------

.. autosummary::
   :toctree: generated

   pybotters.DataStoreCollection
   pybotters.DataStore
   pybotters.StoreChange
   pybotters.StoreStream
