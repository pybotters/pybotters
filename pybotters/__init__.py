from __future__ import annotations

__version__ = "0.17.0"

from typing import Any, Tuple

import aiohttp
from rich import print

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
from .models.bybit_v5 import BybitV5DataStore
from .models.coincheck import CoincheckDataStore
from .models.gmocoin import GMOCoinDataStore
from .models.kucoin import KuCoinDataStore
from .models.okx import OKXDataStore
from .models.phemex import PhemexDataStore
from .ws import WebSocketQueue

__all__: Tuple[str, ...] = (
    "Client",
    "FetchResult",
    "request",
    "get",
    "post",
    "put",
    "delete",
    "CoincheckDataStore",
    "BybitV5DataStore",
    "BinanceSpotDataStore",
    "BinanceUSDSMDataStore",
    "BinanceCOINMDataStore",
    "bitbankDataStore",
    "bitFlyerDataStore",
    "BitgetDataStore",
    "BitMEXDataStore",
    "GMOCoinDataStore",
    "KuCoinDataStore",
    "OKXDataStore",
    "PhemexDataStore",
    "experimental",
    "print",
    "print_handler",
    "WebSocketQueue",
)


def print_handler(msg: Any, ws: aiohttp.ClientWebSocketResponse):
    print(msg)
