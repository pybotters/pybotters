from __future__ import annotations

import logging
from typing import Any, Awaitable

import aiohttp

from ..store import DataStore, DataStoreManager
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


def _symbol_from_msg(msg):
    return msg["topic"].split(":")[-1]


class KucoinDataStore(DataStoreManager):
    """
    Kucoinのデータストアマネージャー
    """

    def _init(self) -> None:
        self.create("ticker", datastore_class=Ticker)
        self.create("kline", datastore_class=Kline)
        self.create("symbolsnapshot", datastore_class=SymbolSnapshot)
        self.create("orderbook5", datastore_class=TopKOrderBook)
        self.create("orderbook50", datastore_class=TopKOrderBook)
        self.create("execution", datastore_class=Execution)
        self.create("indexprice", datastore_class=IndexPrice)
        self.create("markprice", datastore_class=MarkPrice)
        self.create("orderevents", datastore_class=OrderEvents)
        self.create("orders", datastore_class=Orders)
        self.create("balance", datastore_class=Balance)


    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """
        対応エンドポイント

        """
        pass

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if "topic" in msg:
            topic = msg["topic"]
            if topic.startswith("/market/ticker"):
                self.ticker._onmessage(msg)
            elif topic.startswith("/market/candles"):
                self.kline._onmessage(msg)
            elif topic.startswith("/market/snapshot"):
                self.symbolsnapshot._onmessage(msg)
            elif topic.startswith("/spotMarket/level2Depth50"):
                self.orderbook50._onmessage(msg)
            elif topic.startswith("/spotMarket/level2Depth5"):
                self.orderbook5._onmessage(msg)
            elif topic.startswith("/market/match"):
                self.execution._onmessage(msg)
            elif topic.startswith("/indicator/index"):
                self.indexprice._onmessage(msg)
            elif topic.startswith("/indicator/markPrice"):
                self.markprice._onmessage(msg)
            elif topic == "/spotMarket/tradeOrders" or topic == "/spotMarket/advancedOrders":
                self.orderevents._onmessage(msg)
                self.orders._onmessage(msg)
            elif topic.startswith("/spotMarket/level2"):
                raise NotImplementedError
            elif topic.startswith("/margin/fundingBook"):
                raise NotImplementedError

    @property
    def ticker(self) -> "Ticker":
        return self.get("ticker", Ticker)

    @property
    def kline(self) -> "Kline":
        return self.get("kline", Kline)

    @property
    def symbolsnapshot(self) -> "SymbolSnapshot":
        return self.get("symbolsnapshot", SymbolSnapshot)

    @property
    def orderbook5(self) -> "TopKOrderBook":
        return self.get("orderbook5", TopKOrderBook)

    @property
    def orderbook50(self) -> "TopKOrderBook":
        return self.get("orderbook50", TopKOrderBook)

    @property
    def execution(self) -> "Execution":
        return self.get("execution", Execution)

    @property
    def indexprice(self) -> "IndexPrice":
        return self.get("indexprice", IndexPrice)

    @property
    def markprice(self) -> "MarkPrice":
        return self.get("markprice", MarkPrice)

    @property
    def orderevents(self) -> "OrderEvents":
        return self.get("orderevents", OrderEvents)

    @property
    def orders(self) -> "Orders":
        return self.get("orders", Orders)

    @property
    def balance(self) -> "Balance":
        return self.get("balance", Balance)

class _InsertStore(DataStore):
    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert([msg["data"]])

class _UpdateStore(DataStore):
    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._update([msg["data"]])


class Ticker(DataStore):
    """
    - https://docs.kucoin.com/#all-symbols-ticker
    """
    _KEYS = ["symbol"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        if msg["topic"].endswith("all"):
            symbol = msg["subject"]
        else:
            symbol = _symbol_from_msg(msg)
        self._update([{"symbol": symbol, **msg["data"]}])


class SymbolSnapshot(DataStore):
    """
    - https://docs.kucoin.com/#symbol-snapshot
    - https://docs.kucoin.com/#market-snapshot
    """
    _KEYS = ["symbol"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._update([msg["data"]["data"]])


class Orderbook(DataStore):
    """
    - https://docs.kucoin.com/#level-2-market-data
    """
    _KEYS = ["symbol"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        raise NotImplementedError


class TopKOrderBook(DataStore):
    """
    - https://docs.kucoin.com/#level2-5-best-ask-bid-orders
    - https://docs.kucoin.com/#level2-50-best-ask-bid-orders
    """
    _KEYS = ["symbol", "k"]

    def __init__(self, *args, **kwargs):
        super(TopKOrderBook, self).__init__(*args, **kwargs)

    def _onmessage(self, msg: dict[str, Any]) -> None:
        symbol = _symbol_from_msg(msg)

        self._delete([])
        data = []
        for side in ("asks", "bids"):
            items = msg["data"][side]
            for k, i in enumerate(items, start=1):
                data.append({
                    "symbol": symbol,
                    "k": k,
                    "side": side[:-1],
                    "price": float(i[0]),
                    "size": float(i[1]),
                    "timestamp": msg["data"]["timestamp"]
                })

        self._update(data)


class Kline(DataStore):
    """
    - https://docs.kucoin.com/#klines
    """
    _KEYS = ["symbol", "interval"]

    def __init__(self, *args, **kwargs):
        super(Kline, self).__init__(*args, **kwargs)
        # 未確定足保存用
        self._latests = {}

    def latest(self, symbol: str, interval: str):
        """ 未確定足取得用

        """
        return self._latests.get((symbol, interval), None)

    def _onmessage(self, msg: dict[str, Any]) -> None:
        data = self._parse_msg(msg)

        key = tuple(data[k] for k in self._keys)
        latest_candle = self._latests.get(key, None)
        if latest_candle and latest_candle["timestamp"] != data["timestamp"]:
            # 足確定
            self._insert([latest_candle])
        self._latests[key] = data

    def _parse_msg(self, msg):
        symbol, interval = msg["topic"].split(":")[-1].split("_")
        data = msg["data"]
        candles = data["candles"]
        ohlcva = {
            "timestamp": int(candles[0]),
            "open": float(candles[1]),
            "close": float(candles[2]),
            "high": float(candles[3]),
            "low": float(candles[4]),
            "volume": float(candles[5]),
            "amount": float(candles[6])
        }

        return {
            "symbol": symbol,
            "interval": interval,
            "received_at": int(data["time"]),
            **ohlcva,
        }


class Execution(DataStore):
    """
    - https://docs.kucoin.com/#match-execution-data
    """
    _KEYS = ["tradeId"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert([msg["data"]])


class IndexPrice(_UpdateStore):
    """
    - https://docs.kucoin.com/#index-price
    """
    _KEYS = ["symbol"]


class MarkPrice(_UpdateStore):
    """
    - https://docs.kucoin.com/#mark-price
    """
    _KEYS = ["symbol"]


class OrderEvents(_InsertStore):
    """
    - https://docs.kucoin.com/#private-order-change-events
    """
    _KEYS = ["orderId"]


class Orders(DataStore):
    """
    - https://docs.kucoin.com/#private-order-change-events
    """
    _KEYS = ["orderId"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        d = msg["data"]
        tp = d["type"]
        item = self.get(d)
        if item is None:
            # new order
            if tp == "open":
                self._insert([d])
        else:
            if tp in ("match", "triggered"):
                # Market order
                pass
            elif tp in ("canceled", "filled"):
                self._delete([item])
            elif tp == "update":
                self._update([item])
            else:
                raise RuntimeError(f"Unknown type: {tp} ({d})")


class Balance(_UpdateStore):
    """
    - https://docs.kucoin.com/#account-balance-notice
    """
    _KEYS = ['accountId']


# TODO: Margin Trade Channels

