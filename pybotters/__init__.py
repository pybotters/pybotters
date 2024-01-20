from __future__ import annotations

__version__ = "0.17.0"


from .client import Client, FetchResult, NotJSONContent
from .models.binance import (
    BinanceCOINMDataStore,
    BinanceSpotDataStore,
    BinanceUSDSMDataStore,
)
from .models.bitbank import bitbankDataStore
from .models.bitflyer import bitFlyerDataStore
from .models.bitget import BitgetDataStore
from .models.bitmex import BitMEXDataStore
from .models.bybit import BybitDataStore
from .models.coincheck import CoincheckDataStore
from .models.gmocoin import GMOCoinDataStore
from .models.kucoin import KuCoinDataStore
from .models.okx import OKXDataStore
from .models.phemex import PhemexDataStore
from .store import DataStore, DataStoreManager, StoreChange, StoreStream
from .ws import WebSocketApp, WebSocketQueue

__all__: tuple[str, ...] = (
    # client
    "Client",
    "FetchResult",
    "NotJSONContent",
    # ws
    "WebSocketApp",
    "WebSocketQueue",
    # store
    "DataStore",
    "DataStoreManager",
    "StoreChange",
    "StoreStream",
    # models
    "BinanceCOINMDataStore",
    "BinanceSpotDataStore",
    "BinanceUSDSMDataStore",
    "BitMEXDataStore",
    "BitgetDataStore",
    "BybitDataStore",
    "CoincheckDataStore",
    "GMOCoinDataStore",
    "KuCoinDataStore",
    "OKXDataStore",
    "PhemexDataStore",
    "bitFlyerDataStore",
    "bitbankDataStore",
)
