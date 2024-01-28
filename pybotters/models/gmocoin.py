from __future__ import annotations

import asyncio
import logging
from typing import Awaitable

import aiohttp

from pybotters.store import DataStore, DataStoreManager
from pybotters.typedefs import Item

from ..auth import Auth
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class TickerStore(DataStore):
    _KEYS = ["symbol"]

    def _onmessage(self, mes: Item) -> None:
        self._update([mes])


class OrderBookStore(DataStore):
    _KEYS = ["symbol", "side", "price"]

    def _init(self) -> None:
        self.timestamp: str | None = None

    def sorted(
        self, query: Item | None = None, limit: int | None = None
    ) -> dict[str, list[Item]]:
        return self._sorted(
            item_key="side",
            item_asc_key="asks",
            item_desc_key="bids",
            sort_key="price",
            query=query,
            limit=limit,
        )

    def _onmessage(self, mes: Item) -> None:
        data = []
        for side in ("asks", "bids"):
            for row in mes[side]:
                store_row = {
                    "symbol": mes["symbol"],
                    "side": side,
                    "price": row["price"],
                    "size": row["size"],
                }
                data.append(store_row)
        self._find_and_delete({"symbol": mes["symbol"]})
        self._insert(data)
        self.timestamp = mes["timestamp"]


class TradeStore(DataStore):
    def _onmessage(self, mes: Item) -> None:
        self._insert([mes])


class OrderStore(DataStore):
    _KEYS = ["orderId"]

    def _onresponse(self, data: list[Item]) -> None:
        self._update(data)

    def _onmessage(self, mes: Item) -> None:
        if mes["msgType"] in ("NOR", "ROR"):
            self._update([mes])
        else:
            self._delete([mes])

    def _onexecution(self, mes: Item) -> None:
        if mes["orderSize"] == mes["orderExecutedSize"]:
            self._delete([mes])
        else:
            update_item = {
                "orderId": mes["orderId"],
                "orderExecutedSize": mes["orderExecutedSize"],
            }
            self._update([update_item])


class ExecutionStore(DataStore):
    _KEYS = ["executionId"]

    def _onresponse(self, data: list[Item]) -> None:
        self._insert(data)

    def _onmessage(self, mes: Item) -> None:
        self._insert([mes])


class PositionStore(DataStore):
    _KEYS = ["positionId"]

    def _onresponse(self, data: list[Item]) -> None:
        self._update(data)

    def _onmessage(self, mes: Item) -> None:
        if mes["msgType"] == "OPR":
            self._insert([mes])
        elif mes["msgType"] == "CPR":
            self._delete([mes])
        else:
            self._update([mes])


class PositionSummaryStore(DataStore):
    _KEYS = ["symbol", "side"]

    def _onresponse(self, data: list[Item]) -> None:
        self._update(data)

    def _onmessage(self, mes: Item) -> None:
        self._update([mes])


class GMOCoinDataStore(DataStoreManager):
    """
    GMOコインのデータストアマネージャー
    """

    def _init(self) -> None:
        self.create("ticker", datastore_class=TickerStore)
        self.create("orderbooks", datastore_class=OrderBookStore)
        self.create("trades", datastore_class=TradeStore)
        self.create("orders", datastore_class=OrderStore)
        self.create("positions", datastore_class=PositionStore)
        self.create("executions", datastore_class=ExecutionStore)
        self.create("position_summary", datastore_class=PositionSummaryStore)
        self.token: str | None = None

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """
        対応エンドポイント

        - GET /private/v1/latestExecutions (DataStore: executions)
        - GET /private/v1/activeOrders (DataStore: orders)
        - GET /private/v1/openPositions (DataStore: positions)
        - GET /private/v1/positionSummary (DataStore: position_summary)
        - POST /private/v1/ws-auth (Property: token)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()

            if data.get("status") != 0:
                raise ValueError(
                    "Response error at DataStore initialization\n"
                    f"URL: {resp.url}\n"
                    f"Data: {data}"
                )

            if (
                resp.url.path == "/private/v1/latestExecutions"
                and "list" in data["data"]
            ):
                self.executions._onresponse(data["data"]["list"])
            if resp.url.path == "/private/v1/activeOrders" and "list" in data["data"]:
                self.orders._onresponse(data["data"]["list"])
            if resp.url.path == "/private/v1/openPositions" and "list" in data["data"]:
                self.positions._onresponse(data["data"]["list"])
            if (
                resp.url.path == "/private/v1/positionSummary"
                and "list" in data["data"]
            ):
                self.position_summary._onresponse(data["data"]["list"])
            if resp.url.path == "/private/v1/ws-auth":
                self.token = data["data"]
                asyncio.create_task(self._token(resp.__dict__["_raw_session"]))

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if "error" in msg:
            logger.warning(msg)
        if "channel" in msg:
            channel = msg.get("channel")
            # Public
            if channel == "ticker":
                self.ticker._onmessage(msg)
            elif channel == "orderbooks":
                self.orderbooks._onmessage(msg)
            elif channel == "trades":
                self.trades._onmessage(msg)
            # Private
            elif channel == "executionEvents":
                self.orders._onexecution(msg)
                self.executions._onmessage(msg)
            elif channel == "orderEvents":
                self.orders._onmessage(msg)
            elif channel == "positionEvents":
                self.positions._onmessage(msg)
            elif channel == "positionSummaryEvents":
                self.position_summary._onmessage(msg)

    async def _token(self, session: aiohttp.ClientSession):
        while not session.closed:
            await session.put(
                "https://api.coin.z.com/private/v1/ws-auth",
                data={"token": self.token},
                auth=Auth,
            )
            await asyncio.sleep(1800.0)  # 30 minutes

    @property
    def ticker(self) -> TickerStore:
        return self.get("ticker", TickerStore)

    @property
    def orderbooks(self) -> OrderBookStore:
        return self.get("orderbooks", OrderBookStore)

    @property
    def trades(self) -> TradeStore:
        return self.get("trades", TradeStore)

    @property
    def orders(self) -> OrderStore:
        """
        アクティブオーダーのみ(約定・キャンセル済みは削除される)
        """
        return self.get("orders", OrderStore)

    @property
    def positions(self) -> PositionStore:
        return self.get("positions", PositionStore)

    @property
    def executions(self) -> ExecutionStore:
        return self.get("executions", ExecutionStore)

    @property
    def position_summary(self) -> PositionSummaryStore:
        return self.get("position_summary", PositionSummaryStore)
