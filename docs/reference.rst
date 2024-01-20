API Reference
=============

Client class
------------

.. autosummary::
   :toctree: generated

   pybotters.Client


Fetch API Returns
-----------------

:meth:`pybotters.Client.fetch` Returns

.. autosummary::
   :toctree: generated

   pybotters.FetchResult
   pybotters.NotJSONContent


WebSocket API Returns
---------------------

:meth:`pybotters.Client.ws_connect` Returns

.. autosummary::
   :toctree: generated

   pybotters.WebSocketApp


WebSocket handlers
------------------

WebSocket handlers for :meth:`pybotters.Client.ws_connect`

.. autosummary::
   :toctree: generated

   pybotters.WebSocketQueue


Exchange specific WebSocket handlers
------------------------------------

Exchange specific WebSocket handlers for :meth:`pybotters.Client.ws_connect`

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

Abstract WebSocket handler for :meth:`pybotters.Client.ws_connect`

.. autosummary::
   :toctree: generated

   pybotters.DataStoreManager
   pybotters.DataStore
   pybotters.StoreChange
   pybotters.StoreStream


Hosts
-----

.. autosummary::
   :toctree: generated

   pybotters.auth.Hosts
   pybotters.ws.AuthHosts
   pybotters.ws.HeartbeatHosts
   pybotters.ws.RequestLimitHosts
   pybotters.ws.MessageSignHosts
