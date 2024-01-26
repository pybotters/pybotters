from contextlib import nullcontext
from functools import partial
from unittest.mock import MagicMock, patch

import pybotters
import pybotters.models.legacy.gmocoin

ALL_STORE_CLASSES = [
    # Top-level
    pybotters.BinanceCOINMDataStore,
    pybotters.BinanceSpotDataStore,
    pybotters.BinanceUSDSMDataStore,
    pybotters.BitMEXDataStore,
    pybotters.BitgetDataStore,
    pybotters.BybitDataStore,
    pybotters.CoincheckDataStore,
    pybotters.GMOCoinDataStore,
    pybotters.KuCoinDataStore,
    pybotters.OKXDataStore,
    pybotters.PhemexDataStore,
    pybotters.bitFlyerDataStore,
    pybotters.bitbankDataStore,
    # legacy
    pybotters.models.legacy.gmocoin.GMOCoinDataStore,
]


def test_create_all_stores():
    """Lazy tests"""
    for cls in ALL_STORE_CLASSES:
        store = cls()

        if cls is pybotters.bitbankDataStore:
            cm_partial = partial(patch, "json.loads")
        else:
            cm_partial = partial(nullcontext)

        with cm_partial():
            store.onmessage(MagicMock(), MagicMock())
