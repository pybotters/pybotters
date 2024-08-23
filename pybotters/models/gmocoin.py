from __future__ import annotations

import asyncio
import logging
import warnings
from typing import TYPE_CHECKING, Awaitable

from pybotters.store import DataStore, DataStoreCollection

from ..auth import Auth

if TYPE_CHECKING:
    import aiohttp

    from pybotters.typedefs import Item

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


class GMOCoinDataStore(DataStoreCollection):
    """GMO Coin の DataStoreCollection クラス"""

    def _init(self) -> None:
        self._create("ticker", datastore_class=TickerStore)
        self._create("orderbooks", datastore_class=OrderBookStore)
        self._create("trades", datastore_class=TradeStore)
        self._create("orders", datastore_class=OrderStore)
        self._create("positions", datastore_class=PositionStore)
        self._create("executions", datastore_class=ExecutionStore)
        self._create("position_summary", datastore_class=PositionSummaryStore)
        self.token: str | None = None  # DeprecationWarning

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data.

        対応エンドポイント

        - GET /private/v1/latestExecutions (:attr:`.CoincheckDataStore.executions`)
        - GET /private/v1/activeOrders (:attr:`.CoincheckDataStore.orders`)
        - GET /private/v1/openPositions (:attr:`.CoincheckDataStore.positions`)
        - GET /private/v1/positionSummary (:attr:`.CoincheckDataStore.position_summary`)
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
            if resp.url.path == "/private/v1/ws-auth":  # DeprecationWarning
                warnings.warn(
                    "Initializing `POST /private/v1/ws-auth` with this method is deprecated. "
                    "Please migrate to helpers.GMOCoinHelper.",
                    DeprecationWarning,
                    stacklevel=2,
                )

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

    async def _token(self, session: aiohttp.ClientSession):  # DeprecationWarning
        while not session.closed:
            await session.put(
                "https://api.coin.z.com/private/v1/ws-auth",
                data={"token": self.token},
                auth=Auth,
            )
            await asyncio.sleep(1800.0)  # 30 minutes

    @property
    def ticker(self) -> TickerStore:
        """ticker channel.

        https://api.coin.z.com/docs/#ws-ticker
        """
        return self._get("ticker", TickerStore)

    @property
    def orderbooks(self) -> OrderBookStore:
        """orderbooks channel.

        https://api.coin.z.com/docs/#ws-orderbooks
        """
        return self._get("orderbooks", OrderBookStore)

    @property
    def trades(self) -> TradeStore:
        """trades channel.

        https://api.coin.z.com/docs/#ws-trades
        """
        return self._get("trades", TradeStore)

    @property
    def orders(self) -> OrderStore:
        """orderEvents channel.

        アクティブオーダーのみデータが格納されます。 キャンセル、約定済みなどは削除されます。

        https://api.coin.z.com/docs/#ws-order-events
        """
        return self._get("orders", OrderStore)

    @property
    def positions(self) -> PositionStore:
        """positionEvents channel.

        https://api.coin.z.com/docs/#ws-position-events
        """
        return self._get("positions", PositionStore)

    @property
    def executions(self) -> ExecutionStore:
        """executionEvents channel.

        https://api.coin.z.com/docs/#ws-execution-events
        """
        return self._get("executions", ExecutionStore)

    @property
    def position_summary(self) -> PositionSummaryStore:
        """positionSummaryEvents channel.

        https://api.coin.z.com/docs/#ws-position-summary-events
        """
        return self._get("position_summary", PositionSummaryStore)
