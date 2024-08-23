from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Awaitable

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    import aiohttp
    from yarl import URL

    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BybitDataStore(DataStoreCollection):
    """Bybit の DataStoreCollection クラス"""

    def _init(self) -> None:
        self._create("orderbook", datastore_class=OrderBook)
        self._create("publicTrade", datastore_class=Trade)
        self._create("tickers", datastore_class=Ticker)
        self._create("kline", datastore_class=Kline)
        self._create("liquidation", datastore_class=Liquidation)
        self._create("kline_lt", datastore_class=LTKline)
        self._create("tickers_lt", datastore_class=LTTicker)
        self._create("lt", datastore_class=LTNav)
        self._create("position", datastore_class=Position)
        self._create("execution", datastore_class=Execution)
        self._create("order", datastore_class=Order)
        self._create("wallet", datastore_class=Wallet)
        self._create("greeks", datastore_class=Greek)

    _MAP_PATH_TOPIC = {
        "/v5/position/list": "position",
        "/v5/order/realtime": "order",
        "/v5/account/wallet-balance": "wallet",
    }

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data.

        対応エンドポイント

        - GET /v5/position/list (:attr:`.BybitDataStore.position`)
        - GET /v5/order/realtime (:attr:`.BybitDataStore.order`)
        - GET /v5/account/wallet-balance (:attr:`.BybitDataStore.wallet`)
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
                if target_onresponse := getattr(self[topic], "_onresponse", None):
                    target_onresponse(resp.url, data)

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if "success" in msg:
            if not msg["success"]:
                logger.warning(msg)

        if "topic" in msg:
            dot_topic: str = msg["topic"]
            topic, *topic_ext = dot_topic.split(".")

            if target_onmessage := getattr(self[topic], "_onmessage", None):
                target_onmessage(msg, topic_ext)

    @property
    def orderbook(self) -> "OrderBook":
        """orderbook topic.

        https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook
        """
        return self._get("orderbook", OrderBook)

    @property
    def trade(self) -> "Trade":
        """trade topic.

        https://bybit-exchange.github.io/docs/v5/websocket/public/trade
        """
        return self._get("publicTrade", Trade)

    @property
    def ticker(self) -> "Ticker":
        """ticker topic.

        https://bybit-exchange.github.io/docs/v5/websocket/public/ticker
        """
        return self._get("tickers", Ticker)

    @property
    def kline(self) -> "Kline":
        """kline topic.

        https://bybit-exchange.github.io/docs/v5/websocket/public/kline
        """
        return self._get("kline", Kline)

    @property
    def liquidation(self) -> "Liquidation":
        """liquidation topic.

        https://bybit-exchange.github.io/docs/v5/websocket/public/liquidation
        """
        return self._get("liquidation", Liquidation)

    @property
    def lt_kline(self) -> "LTKline":
        """lt_kline topic.

        https://bybit-exchange.github.io/docs/v5/websocket/public/etp-kline
        """
        return self._get("kline_lt", LTKline)

    @property
    def lt_ticker(self) -> "LTTicker":
        """lt_ticker topic.

        https://bybit-exchange.github.io/docs/v5/websocket/public/etp-ticker
        """
        return self._get("tickers_lt", LTTicker)

    @property
    def lt_nav(self) -> "LTNav":
        """lt_nav topic.

        https://bybit-exchange.github.io/docs/v5/websocket/public/etp-nav
        """
        return self._get("lt", LTNav)

    @property
    def position(self) -> "Position":
        """position topic.

        https://bybit-exchange.github.io/docs/v5/websocket/private/position"""

        return self._get("position", Position)

    @property
    def execution(self) -> "Execution":
        """execution topic.

        https://bybit-exchange.github.io/docs/v5/websocket/private/execution
        """
        return self._get("execution", Execution)

    @property
    def order(self) -> "Order":
        """order topic.

        アクティブオーダーのみデータが格納されます。 キャンセル、約定済みなどは削除されます。

        https://bybit-exchange.github.io/docs/v5/websocket/private/order
        """
        return self._get("order", Order)

    @property
    def wallet(self) -> "Wallet":
        """wallet topic.

        https://bybit-exchange.github.io/docs/v5/websocket/private/wallet
        """
        return self._get("wallet", Wallet)

    @property
    def greek(self) -> "Greek":
        """greek topic.

        https://bybit-exchange.github.io/docs/v5/websocket/private/greek
        """
        return self._get("greeks", Greek)


class OrderBook(DataStore):
    _KEYS = ["s", "S", "p"]

    def sorted(
        self, query: Item | None = None, limit: int | None = None
    ) -> dict[str, list[Item]]:
        return self._sorted(
            item_key="S",
            item_asc_key="a",
            item_desc_key="b",
            sort_key="p",
            query=query,
            limit=limit,
        )

    def _onmessage(self, msg: Item, topic_ext: list[str]) -> None:
        operation: dict[str, list[Item]] = {"delete": [], "update": [], "insert": []}

        is_snapshot = msg["type"] == "snapshot"
        if is_snapshot:
            operation["delete"].extend(self.find({"s": msg["data"]["s"]}))

        for side in ("a", "b"):
            for item in msg["data"][side]:
                dsitem = {
                    "s": msg["data"]["s"],
                    "S": side,
                    "p": item[0],
                    "v": item[1],
                }
                if is_snapshot:
                    operation["insert"].append(dsitem)
                elif dsitem["v"] == "0":
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


class LTKline(Kline): ...


class LTTicker(Ticker): ...


class LTNav(Ticker): ...


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
