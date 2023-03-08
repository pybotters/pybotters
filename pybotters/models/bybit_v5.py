from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Optional

import aiohttp
from yarl import URL

from ..store import DataStore, DataStoreManager
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BybitV5DataStore(DataStoreManager):
    def _init(self) -> None:
        self.create("orderbook", datastore_class=OrderBook)
        self.create("publicTrade", datastore_class=Trade)
        self.create("tickers", datastore_class=Ticker)
        self.create("kline", datastore_class=Kline)
        self.create("liquidation", datastore_class=Liquidation)
        self.create("kline_lt", datastore_class=LTKline)
        self.create("tickers_lt", datastore_class=LTTicker)
        self.create("lt", datastore_class=LTNav)
        self.create("position", datastore_class=Position)
        self.create("execution", datastore_class=Execution)
        self.create("order", datastore_class=Order)
        self.create("wallet", datastore_class=Wallet)
        self.create("greeks", datastore_class=Greek)

    _MAP_PATH_TOPIC = {
        "/v5/position/list": "position",
        "/v5/order/realtime": "order",
        "/v5/account/wallet-balance": "wallet",
    }

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """
        対応エンドポイント

        - GET /v5/position/list (DataStore: position)
        - GET /v5/order/realtime (DataStore: order)
        - GET /v5/account/wallet-balance (DataStore: wallet)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()

            if data is None or "retCode" not in data or data["retCode"] != 0:
                raise ValueError(
                    "Response error at DataStore initialization\n"
                    f"URL: {resp.url}\n"
                    f"Data: {data}"
                )

            if resp.url.path in self._MAP_PATH_TOPIC:
                topic = self._MAP_PATH_TOPIC[resp.url.path]
                if topic in self:
                    getattr(self[topic], "_onresponse")(resp.url, data)

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if "success" in msg:
            if not msg["success"]:
                logger.warning(msg)

        if "topic" in msg:
            dot_topic: str = msg["topic"]
            topic, *topic_ext = dot_topic.split(".")

            if topic in self:
                getattr(self[topic], "_onmessage")(msg, topic_ext)

    @property
    def orderbook(self) -> "OrderBook":
        return self.get("orderbook", OrderBook)

    @property
    def trade(self) -> "Trade":
        return self.get("publicTrade", Trade)

    @property
    def ticker(self) -> "Ticker":
        return self.get("tickers", Ticker)

    @property
    def kline(self) -> "Kline":
        return self.get("kline", Kline)

    @property
    def liquidation(self) -> "Liquidation":
        return self.get("liquidation", Liquidation)

    @property
    def lt_kline(self) -> "LTKline":
        return self.get("kline_lt", LTKline)

    @property
    def lt_ticker(self) -> "LTTicker":
        return self.get("tickers_lt", LTTicker)

    @property
    def lt_nav(self) -> "LTNav":
        return self.get("lt", LTNav)

    @property
    def position(self) -> "Position":
        return self.get("position", Position)

    @property
    def execution(self) -> "Execution":
        return self.get("execution", Execution)

    @property
    def order(self) -> "Order":
        return self.get("order", Order)

    @property
    def wallet(self) -> "Wallet":
        return self.get("wallet", Wallet)

    @property
    def greek(self) -> "Greek":
        return self.get("greeks", Greek)


class OrderBook(DataStore):
    _KEYS = ["symbol", "side", "price"]

    def sorted(self, query: Optional[Item] = None) -> dict[str, list[Item]]:
        if query is None:
            query = {}
        result = {"asks": [], "bids": []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item["side"]].append(item)
        result["asks"].sort(key=lambda x: x["price"])
        result["bids"].sort(key=lambda x: x["price"], reverse=True)
        return result

    def _onmessage(self, msg: Item, topic_ext: list[str]) -> None:
        operation = {"delete": [], "update": [], "insert": []}

        is_snapshot = msg["type"] == "snapshot"
        if is_snapshot:
            operation["delete"].extend(self.find({"symbol": msg["data"]["s"]}))

        for side_k, side_v in (("a", "asks"), ("b", "bids")):
            for item in msg["data"][side_k]:
                dsitem = {
                    "symbol": msg["data"]["s"],
                    "side": side_v,
                    "price": item[0],
                    "size": item[1],
                }
                if is_snapshot:
                    operation["insert"].append(dsitem)
                elif dsitem["size"] == "0":
                    operation["delete"].append(dsitem)
                else:
                    operation["update"].append(dsitem)

        self._delete(operation["delete"])
        self._update(operation["update"])
        self._insert(operation["insert"])


class Trade(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: Item, topic_ext: list[str]) -> None:
        self._insert(msg["data"])


class Ticker(DataStore):
    _KEYS = ["symbol"]

    def _onmessage(self, msg: Item, topic_ext: list[str]) -> None:
        self._update([msg["data"]])


class Kline(DataStore):
    _KEYS = ["symbol", "start", "end"]

    def _onmessage(self, msg: Item, topic_ext: list[str]) -> None:
        msg["data"] = [{"symbol": topic_ext[1], **x} for x in msg["data"]]
        self._update(msg["data"])


class Liquidation(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: Item, topic_ext: list[str]) -> None:
        self._insert([msg["data"]])


class LTKline(Kline):
    ...


class LTTicker(Ticker):
    ...


class LTNav(Ticker):
    ...


class Position(DataStore):
    _KEYS = ["symbol", "positionIdx"]

    def _onresponse(self, url: URL, data: Item) -> None:
        self._update(data["result"]["list"])

    def _onmessage(self, msg: Item, topic_ext: list[str]) -> None:
        self._update(msg["data"])


class Execution(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: Item, topic_ext: list[str]) -> None:
        self._insert(msg["data"])


class Order(DataStore):
    _KEYS = ["orderId"]
    _MAP_ORDER_STATUS = {
        "Created": "pending",
        "New": "pending",
        "Rejected": "failure",
        "PartiallyFilled": "pending",
        "PartiallyFilledCanceled": "filled",
        "Filled": "filled",
        "Cancelled": "canceled",
        "Untriggered": "pending",
        "Triggered": "filled",
        "Deactivated": "canceled",
        "Active": "pending",
    }

    def _onresponse(self, url: URL, data: dict[str, dict[str, list[Item]]]) -> None:
        # Delete inactive orders
        if "symbol" in url.query:
            delete_orders = list(
                filter(
                    lambda x: x["symbol"] == url.query["symbol"],
                    self.find({"category": url.query["category"]}),
                )
            )
            self._delete(delete_orders)
        elif "baseCoin" in url.query:
            delete_orders = list(
                filter(
                    lambda x: x["symbol"].startswith(url.query["baseCoin"]),
                    self.find({"category": url.query["category"]}),
                )
            )
            self._delete(delete_orders)
        elif "settleCoin" in url.query:
            delete_orders = list(
                filter(
                    lambda x: x["symbol"].endswith(url.query["settleCoin"]),
                    self.find({"category": url.query["category"]}),
                )
            )
            self._delete(delete_orders)

        # Update active orders
        for item in data["result"]["list"]:
            item["category"] = url.query["category"]
            self._update([item])

    def _onmessage(self, msg: Item, topic_ext: list[str]) -> None:
        for item in msg["data"]:
            order_status = self._MAP_ORDER_STATUS.get(item["orderStatus"])
            # Update active order
            if order_status == "pending":
                self._update([item])
            # Delete inactive order
            elif order_status in ("filled", "canceled", "failure"):
                self._delete([item])
                # inactive conditional order in spot
                if item["orderLinkId"]:
                    self._delete(self.find({"orderLinkId": item["orderLinkId"]}))


class Wallet(DataStore):
    _KEYS = ["accountType"]

    def _onresponse(self, url: URL, data: Item) -> None:
        for item in data["result"]["list"]:
            orig_item = self.get(item)
            if orig_item:
                current_coins = set(map(lambda x: x["coin"], item["coin"]))
                item["coin"].extend(
                    filter(lambda x: x["coin"] not in current_coins, orig_item["coin"])
                )
            self._update([item])

    def _onmessage(self, msg: Item, topic_ext: list[str]) -> None:
        for item in msg["data"]:
            orig_item = self.get(item)
            if orig_item:
                current_coins = set(map(lambda x: x["coin"], item["coin"]))
                item["coin"].extend(
                    filter(lambda x: x["coin"] not in current_coins, orig_item["coin"])
                )
            self._update([item])


class Greek(DataStore):
    _KEYS = ["baseCoin"]

    def _onmessage(self, msg: Item, topic_ext: list[str]) -> None:
        self._update(msg["data"])
