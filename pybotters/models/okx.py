from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Optional

import aiohttp

from ..store import DataStore, DataStoreManager
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class OKXDataStore(DataStoreManager):
    """
    OKXのデータストアマネージャー
    """

    def _init(self) -> None:
        self.create("instruments", datastore_class=Instruments)
        self.create("tickers", datastore_class=Tickers)
        self.create("open-interest", datastore_class=OpenInterest)
        self.create("candle", datastore_class=Candle)
        self.create("trades", datastore_class=Trades)
        self.create("estimated-price", datastore_class=EstimatedPrice)
        self.create("mark-price", datastore_class=MarkPrice)
        self.create("mark-price-candle", datastore_class=MarkPriceCandle)
        self.create("price-limit", datastore_class=PriceLimit)
        self.create("books", datastore_class=Books)
        self.create("opt-summary", datastore_class=OptSummary)
        self.create("funding-rate", datastore_class=FundingRate)
        self.create("index-candle", datastore_class=IndexCandle)
        self.create("index-tickers", datastore_class=IndexTickers)
        self.create("status", datastore_class=Status)
        self.create("account", datastore_class=Account)
        self.create("positions", datastore_class=Positions)
        self.create("balance_and_position", datastore_class=BalanceAndPosition)
        self.create("orders", datastore_class=Orders)
        self.create("orders-algo", datastore_class=OrdersAlgo)
        self.create("algo-advance", datastore_class=AlgoAdvance)
        self.create("liquidation-warning", datastore_class=LiquidationWarning)
        self.create("account-greeks", datastore_class=AccountGreeks)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """
        対応エンドポイント

        - GET /api/v5/trade/orders-pending (DataStore: orders)
        - GET /api/v5/trade/orders-algo-pending (DataStore: ordersalgo, algoadvance)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if data["code"] != "0":
                logger.warning(f"Invalid response: {data}")
            if resp.url.path == "/api/v5/trade/orders-pending":
                self.orders._onresponse(data["data"])
            elif resp.url.path == "/api/v5/trade/orders-algo-pending":
                self.ordersalgo._onresponse(data["data"])
                self.algoadvance._onresponse(data["data"])

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if "event" in msg:
            if msg["event"] == "error":
                logger.warning(msg)
        if all(k in msg for k in ("arg", "data")):
            channel: str = msg["arg"]["channel"]
            if "candle" in channel:
                if channel.startswith("candle"):
                    channel = "candle"
                elif channel.startswith("mark-price-candle"):
                    channel = "mark-price-candle"
                elif channel.startswith("index-candle"):
                    channel = "index-candle"
            if "books" in channel:
                if channel.startswith("books"):
                    channel = "books"
            if channel in self:
                self[channel]._onmessage(msg)

    @property
    def instruments(self) -> "Instruments":
        return self.get("instruments", Instruments)

    @property
    def tickers(self) -> "Tickers":
        return self.get("tickers", Tickers)

    @property
    def openinterest(self) -> "OpenInterest":
        return self.get("open-interest", OpenInterest)

    @property
    def candle(self) -> "Candle":
        return self.get("candle", Candle)

    @property
    def trades(self) -> "Trades":
        return self.get("trades", Trades)

    @property
    def estimatedprice(self) -> "EstimatedPrice":
        return self.get("estimated-price", EstimatedPrice)

    @property
    def markprice(self) -> "MarkPrice":
        return self.get("mark-price", MarkPrice)

    @property
    def markpricecandle(self) -> "MarkPriceCandle":
        return self.get("mark-price-candle", MarkPriceCandle)

    @property
    def pricelimit(self) -> "PriceLimit":
        return self.get("price-limit", PriceLimit)

    @property
    def books(self) -> "Books":
        return self.get("books", Books)

    @property
    def optsummary(self) -> "OptSummary":
        return self.get("opt-summary", OptSummary)

    @property
    def fundingrate(self) -> "FundingRate":
        return self.get("funding-rate", FundingRate)

    @property
    def indexcandle(self) -> "IndexCandle":
        return self.get("index-candle", IndexCandle)

    @property
    def indextickers(self) -> "IndexTickers":
        return self.get("index-tickers", IndexTickers)

    @property
    def account(self) -> "Account":
        return self.get("account", Account)

    @property
    def positions(self) -> "Positions":
        return self.get("positions", Positions)

    @property
    def balance_and_position(self) -> "BalanceAndPosition":
        return self.get("balance_and_position", BalanceAndPosition)

    @property
    def orders(self) -> "Orders":
        return self.get("orders", Orders)

    @property
    def ordersalgo(self) -> "OrdersAlgo":
        return self.get("orders-algo", OrdersAlgo)

    @property
    def algoadvance(self) -> "AlgoAdvance":
        return self.get("algo-advance", AlgoAdvance)

    @property
    def liquidationwarning(self) -> "LiquidationWarning":
        return self.get("liquidation-warning", LiquidationWarning)

    @property
    def accountgreeks(self) -> "AccountGreeks":
        return self.get("account-greeks", AccountGreeks)


class _InsertStore(DataStore):
    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert(msg["data"])


class _UpdateStore(DataStore):
    _KEYS = ["instId"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._update(msg["data"])


class _CandleStore(DataStore):
    _KEYS = ["channel", "instId", "ts"]
    _LIST_KEYS = ["ts", "o", "h", "l", "c"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        for item in msg["data"]:
            self._update([{**msg["arg"], **dict(zip(self._LIST_KEYS, item))}])


class Instruments(_UpdateStore):
    ...


class Tickers(_UpdateStore):
    ...


class OpenInterest(_UpdateStore):
    ...


class Candle(_CandleStore):
    _LIST_KEYS = ["ts", "o", "h", "l", "c", "vol", "volCcy"]


class Trades(_InsertStore):
    ...


class EstimatedPrice(_UpdateStore):
    ...


class MarkPrice(_UpdateStore):
    ...


class MarkPriceCandle(_CandleStore):
    ...


class PriceLimit(_UpdateStore):
    ...


class Books(DataStore):
    _KEYS = ["instId", "side", "px"]
    _LIST_KEYS = ["px", "sz", "liqSz", "ordSz"]

    def _init(self) -> None:
        self.checksum: dict[str, int] = {}
        self.ts: Optional[str] = None

    def sorted(self, query: Optional[Item] = None) -> dict[str, list[list[str]]]:
        if query is None:
            query = {}
        result = {"asks": [], "bids": []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item["side"]].append([item[k] for k in self._LIST_KEYS])
        result["asks"].sort(key=lambda x: float(x[0]))
        result["bids"].sort(key=lambda x: float(x[0]), reverse=True)
        return result

    def _onmessage(self, msg: dict[str, Any]) -> None:
        inst_id = msg["arg"]["instId"]
        action = msg.get("action", "snapshot")
        if action == "snapshot":
            self._delete(self.find({"instId": inst_id}))
        for book in msg["data"]:
            for side in ("asks", "bids"):
                for item in book[side]:
                    item = {
                        "instId": inst_id,
                        "side": side,
                        **dict(zip(self._LIST_KEYS, item)),
                    }
                    if item["sz"] != "0":
                        self._update([item])
                    else:
                        self._delete([item])
            if "checksum" in book:
                self.checksum[msg["arg"]["instId"]] = book["checksum"]
            self.ts = book["ts"]


class OptSummary(_UpdateStore):
    ...


class FundingRate(_UpdateStore):
    ...


class IndexCandle(_CandleStore):
    ...


class IndexTickers(_UpdateStore):
    ...


class Status(_InsertStore):
    ...


class Account(DataStore):
    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._clear()
        self._insert(msg["data"])


class Positions(_UpdateStore):
    _KEYS = ["instId", "mgnMode", "posSide"]


class BalanceAndPosition(DataStore):
    def _init(self) -> None:
        self.balance = _AndBalance()
        self.position = _AndPosition()

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert(msg["data"])
        for item in msg["data"]:
            self.balance._onmessage(item["balData"])
            self.position._onmessage(item["posData"])


class _AndBalance(DataStore):
    _KEYS = ["ccy"]

    def _onmessage(self, data: list[Item]) -> None:
        self._update(data)


class _AndPosition(DataStore):
    _KEYS = ["instId", "mgnMode", "posSide"]

    def _onmessage(self, data: list[Item]) -> None:
        self._update(data)


class Orders(DataStore):
    _KEYS = ["ordId"]

    def _onresponse(self, data: list[Item]) -> None:
        self._update(data)

    def _onmessage(self, msg: dict[str, Any]) -> None:
        for item in msg["data"]:
            if item["state"] in ("live", "partially_filled"):
                self._update([item])
            else:
                self._delete([item])


class OrdersAlgo(_UpdateStore):
    _KEYS = ["algoId"]

    def _onresponse(self, data: list[Item]) -> None:
        self._update(
            [
                item
                for item in data
                if item["ordType"] in ("conditional", "oco", "trigger")
            ]
        )

    def _onmessage(self, msg: dict[str, Any]) -> None:
        for item in msg["data"]:
            if item["state"] in ("live", "order_failed"):
                self._update([item])
            else:
                self._delete([item])


class AlgoAdvance(_UpdateStore):
    _KEYS = ["algoId"]

    def _onresponse(self, data: list[Item]) -> None:
        self._update(
            [
                item
                for item in data
                if item["ordType"] in ("iceberg", "twap", "move_order_stop")
            ]
        )

    def _onmessage(self, msg: dict[str, Any]) -> None:
        for item in msg["data"]:
            if item["state"] in ("live", "partially_filled"):
                self._update([item])
            else:
                self._delete([item])


class LiquidationWarning(_UpdateStore):
    ...


class AccountGreeks(_UpdateStore):
    _KEYS = ["ccy"]
