from __future__ import annotations

import asyncio
import logging
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Awaitable, cast

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    import aiohttp

    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class CoincheckDataStore(DataStoreCollection):
    """Coincheck の DataStoreCollection クラス"""

    def _init(self) -> None:
        self._create("trades", datastore_class=Trades)
        self._create("orderbook", datastore_class=Orderbook)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data.

        対応エンドポイント

        - GET /api/order_books (:attr:`.CoincheckDataStore.orderbook`)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if resp.url.path == "/api/order_books":
                pair = resp.url.query.get("pair")
                self.orderbook._onresponse(pair, data)

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse | None = None) -> None:
        first_item = next(iter(msg), None)
        if isinstance(first_item, list):
            self.trades._onmessage(msg)
        elif isinstance(first_item, str):
            self.orderbook._onmessage(*msg)

    @property
    def trades(self) -> "Trades":
        """trades channel.

        https://coincheck.com/ja/documents/exchange/api#websocket-trades
        """
        return self._get("trades", Trades)

    @property
    def orderbook(self) -> "Orderbook":
        """orderbook channel.

        https://coincheck.com/ja/documents/exchange/api#websocket-order-book
        """
        return self._get("orderbook", Orderbook)


class Trades(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: list[list[str]]) -> None:
        for item in msg:
            self._insert(
                [
                    {
                        "timestamp": item[0],
                        "id": item[1],
                        "pair": item[2],
                        "rate": item[3],
                        "amount": item[4],
                        "side": item[5],
                        "taker_id": item[6],
                        "maker_id": item[7],
                    }
                ]
            )


class Orderbook(DataStore):
    _KEYS = ["pair", "side", "rate"]

    def _init(self) -> None:
        self.last_update_at: str | None = None

    def sorted(
        self, query: Item | None = None, limit: int | None = None
    ) -> dict[str, list[Item]]:
        return self._sorted(
            item_key="side",
            item_asc_key="asks",
            item_desc_key="bids",
            sort_key="rate",
            query=query,
            limit=limit,
        )

    def _onresponse(self, pair: str | None, data: dict[str, list[list[str]]]) -> None:
        if pair is None:
            pair = "btc_jpy"
        self._find_and_delete({"pair": pair})
        for side in data:
            for rate, amount in data[side]:
                self._insert(
                    [{"pair": pair, "side": side, "rate": rate, "amount": amount}]
                )

    def _onmessage(self, pair: str, data: dict[str, list[list[str]] | str]) -> None:
        self.last_update_at = cast("dict[str, str]", data).pop("last_update_at")
        for side in cast("dict[str, list[list[str]]]", data):
            for rate, amount in cast("list[list[str]]", data[side]):
                if amount == "0":
                    self._delete([{"pair": pair, "side": side, "rate": rate}])
                else:
                    self._update(
                        [{"pair": pair, "side": side, "rate": rate, "amount": amount}]
                    )


class CoincheckPrivateDataStore(DataStoreCollection):
    """DataStoreCollection for Coincheck Private WebSocket API"""

    def _init(self) -> None:
        self._create("order-events", datastore_class=Order)
        self._create("execution-events", datastore_class=Execution)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data.

        Supported endpoints:

        - ``GET /api/exchange/orders/opens`` (:attr:`.coincheckPrivateDataStore.order`)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()

            if not data.get("success"):
                logger.warning(data)
                continue

            if resp.url.path == "/api/exchange/orders/opens":
                self.order._clear()
                self.order._insert(data["orders"])

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse | None = None) -> None:
        if not (isinstance(msg, dict) and msg.get("success", True)):
            logger.warning(msg)
            return

        channel = msg.get("channel")

        if channel == "order-events":
            self.order._onmessage(msg)
        elif channel == "execution-events":
            self.execution._onmessage(msg)

    @property
    def order(self) -> Order:
        """``order-events`` channel.

        https://coincheck.com/ja/documents/exchange/api#websocket-order-events

        Only active orders are stored. Completed and canceled orders are removed from the store.

        The fields ``pending_amount`` and ``pending_market_buy_amount`` are added to
        each item to track pending orders.

        .. warning::

            New-order events are not sent from the WebSocket, you should call
            :meth:`Order.feed_response` to insert the response from
            ``POST /api/exchange/orders`` into the DataStore.

        .. automethod:: pybotters.models.coincheck.Order.feed_response
        """
        return self._get("order-events", Order)

    @property
    def execution(self) -> Execution:
        """``execution-events`` channel.

        https://coincheck.com/ja/documents/exchange/api#websocket-execution-events
        """
        return self._get("execution-events", Execution)


class Order(DataStore):
    _KEYS = ["id", "pair"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        # WebSocket does not receive new order events; they are retrieved via the REST API.
        # To prevent inconsistencies, processing is performed only on existing items.
        if not (orig := self.get(msg)):
            return

        order_event = msg.get("order_event")

        if order_event in {"TRIGGERED"}:
            self._update([msg])
        elif order_event in {"PARTIALLY_FILL"}:
            if msg["latest_executed_amount"]:
                msg["pending_amount"] = str(
                    Decimal(orig["pending_amount"])
                    - Decimal(msg["latest_executed_amount"])
                )

            if msg["latest_executed_market_buy_amount"]:
                msg["pending_market_buy_amount"] = str(
                    Decimal(orig["pending_market_buy_amount"])
                    - Decimal(msg["latest_executed_market_buy_amount"])
                )

            self._update([msg])
        elif order_event in {"FILL", "EXPIRY", "CANCEL"}:
            self._delete([msg])

    def feed_response(self, data: dict[str, Any]) -> None:
        """Feed the response data from `POST /api/exchange/orders` into the DataStore.

        The fields ``pending_amount`` and ``pending_market_buy_amount`` are added to
        each item to track pending orders.
        """
        if not (isinstance(data, dict) and data.get("success")):
            logger.warning(data)
            return

        data["pending_amount"] = data["amount"]
        data["pending_market_buy_amount"] = data["market_buy_amount"]

        self._insert([data])


class Execution(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert([msg])
