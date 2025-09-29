from __future__ import annotations

from .__version__ import __version__
from .auth import Auth
from .client import Client, FetchResult, NotJSONContent
from .models.binance import (
    BinanceCOINMDataStore,
    BinanceSpotDataStore,
    BinanceUSDSMDataStore,
)
from .models.bitbank import bitbankDataStore, bitbankPrivateDataStore
from .models.bitflyer import bitFlyerDataStore
from .models.bitget import BitgetDataStore
from .models.bitget_v2 import BitgetV2DataStore
from .models.bitmex import BitMEXDataStore
from .models.bybit import BybitDataStore
from .models.coincheck import CoincheckDataStore, CoincheckPrivateDataStore
from .models.gmocoin import GMOCoinDataStore
from .models.hyperliquid import HyperliquidDataStore
from .models.kucoin import KuCoinDataStore
from .models.okx import OKXDataStore
from .models.phemex import PhemexDataStore
from .store import DataStore, DataStoreCollection, StoreChange, StoreStream
from .ws import ClientWebSocketResponse, WebSocketApp, WebSocketQueue

__all__: tuple[str, ...] = (
    # version
    "__version__",
    # client
    "Client",
    "FetchResult",
    "NotJSONContent",
    # ws
    "ClientWebSocketResponse",
    "WebSocketApp",
    "WebSocketQueue",
    # store
    "DataStore",
    "DataStoreCollection",
    "StoreChange",
    "StoreStream",
    # models
    "BinanceCOINMDataStore",
    "BinanceSpotDataStore",
    "BinanceUSDSMDataStore",
    "BitMEXDataStore",
    "BitgetV2DataStore",
    "BitgetDataStore",
    "BybitDataStore",
    "CoincheckDataStore",
    "CoincheckPrivateDataStore",
    "GMOCoinDataStore",
    "HyperliquidDataStore",
    "KuCoinDataStore",
    "OKXDataStore",
    "PhemexDataStore",
    "bitFlyerDataStore",
    "bitbankDataStore",
    "bitbankPrivateDataStore",
    # auth
    "Auth",
)
