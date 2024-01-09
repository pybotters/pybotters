from __future__ import annotations

__version__ = "0.17.0"


from .client import Client, FetchResult
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
from .ws import WebSocketQueue

__all__: tuple[str, ...] = (
    # client
    "Client",
    "FetchResult",
    # ws
    "WebSocketQueue",
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
