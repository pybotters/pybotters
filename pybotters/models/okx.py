from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Awaitable

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    import aiohttp

    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class OKXDataStore(DataStoreCollection):
    """OKX の DataStoreCollection クラス"""

    def _init(self) -> None:
        self._create("instruments", datastore_class=Instruments)
        self._create("tickers", datastore_class=Tickers)
        self._create("open-interest", datastore_class=OpenInterest)
        self._create("candle", datastore_class=Candle)
        self._create("trades", datastore_class=Trades)
        self._create("estimated-price", datastore_class=EstimatedPrice)
        self._create("mark-price", datastore_class=MarkPrice)
        self._create("mark-price-candle", datastore_class=MarkPriceCandle)
        self._create("price-limit", datastore_class=PriceLimit)
        self._create("books", datastore_class=Books)
        self._create("opt-summary", datastore_class=OptSummary)
        self._create("funding-rate", datastore_class=FundingRate)
        self._create("index-candle", datastore_class=IndexCandle)
        self._create("index-tickers", datastore_class=IndexTickers)
        self._create("status", datastore_class=Status)
        self._create("account", datastore_class=Account)
        self._create("positions", datastore_class=Positions)
        self._create("balance_and_position", datastore_class=BalanceAndPosition)
        self._create("orders", datastore_class=Orders)
        self._create("orders-algo", datastore_class=OrdersAlgo)
        self._create("algo-advance", datastore_class=AlgoAdvance)
        self._create("liquidation-warning", datastore_class=LiquidationWarning)
        self._create("account-greeks", datastore_class=AccountGreeks)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data.

        対応エンドポイント

        - GET /api/v5/trade/orders-pending (:attr:`.OKXDataStore.orders`)
        - GET /api/v5/trade/orders-algo-pending (:attr:`.OKXDataStore.ordersalgo` :attr:`.OKXDataStore.algoadvance`)
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
            if target_onmessage := getattr(self[channel], "_onmessage", None):
                target_onmessage(msg)

    @property
    def instruments(self) -> "Instruments":
        """instruments channel.

        https://www.okx.com/docs-v5/en/#public-data-websocket-instruments-channel
        """
        return self._get("instruments", Instruments)

    @property
    def tickers(self) -> "Tickers":
        """tickers channel.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-tickers-channel
        """
        return self._get("tickers", Tickers)

    @property
    def openinterest(self) -> "OpenInterest":
        """open-interest channel.

        https://www.okx.com/docs-v5/en/#public-data-websocket-open-interest-channel
        """
        return self._get("open-interest", OpenInterest)

    @property
    def candle(self) -> "Candle":
        """candle channel.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-candlesticks-channel
        """
        return self._get("candle", Candle)

    @property
    def trades(self) -> "Trades":
        """trades channel.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-trades-channel
        """
        return self._get("trades", Trades)

    @property
    def estimatedprice(self) -> "EstimatedPrice":
        """estimated-price channel.

        https://www.okx.com/docs-v5/en/#public-data-websocket-estimated-delivery-exercise-price-channel
        """
        return self._get("estimated-price", EstimatedPrice)

    @property
    def markprice(self) -> "MarkPrice":
        """mark-price channel.

        https://www.okx.com/docs-v5/en/#public-data-websocket-mark-price-channel
        """
        return self._get("mark-price", MarkPrice)

    @property
    def markpricecandle(self) -> "MarkPriceCandle":
        """mark-price-candle channel.

        https://www.okx.com/docs-v5/en/#public-data-websocket-mark-price-candlesticks-channel
        """
        return self._get("mark-price-candle", MarkPriceCandle)

    @property
    def pricelimit(self) -> "PriceLimit":
        """price-limit channel.

        https://www.okx.com/docs-v5/en/#public-data-websocket-price-limit-channel
        """
        return self._get("price-limit", PriceLimit)

    @property
    def books(self) -> "Books":
        """books channel.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-order-book-channel
        """
        return self._get("books", Books)

    @property
    def optsummary(self) -> "OptSummary":
        """opt-summary channel.

        https://www.okx.com/docs-v5/en/#public-data-websocket-option-summary-channel
        """
        return self._get("opt-summary", OptSummary)

    @property
    def fundingrate(self) -> "FundingRate":
        """funding-rate channel.

        https://www.okx.com/docs-v5/en/#public-data-websocket-funding-rate-channel
        """
        return self._get("funding-rate", FundingRate)

    @property
    def indexcandle(self) -> "IndexCandle":
        """index-candle channel.

        https://www.okx.com/docs-v5/en/#public-data-websocket-index-candlesticks-channel
        """
        return self._get("index-candle", IndexCandle)

    @property
    def indextickers(self) -> "IndexTickers":
        """index-tickers channel.

        https://www.okx.com/docs-v5/en/#public-data-websocket-index-tickers-channel
        """
        return self._get("index-tickers", IndexTickers)

    @property
    def account(self) -> "Account":
        """account channel.

        https://www.okx.com/docs-v5/en/#trading-account-websocket-account-channel
        """
        return self._get("account", Account)

    @property
    def positions(self) -> "Positions":
        """positions channel.

        https://www.okx.com/docs-v5/en/#trading-account-websocket-positions-channel
        """
        return self._get("positions", Positions)

    @property
    def balance_and_position(self) -> "BalanceAndPosition":
        """balance_and_position channel.

        https://www.okx.com/docs-v5/en/#trading-account-websocket-balance-and-position-channel
        """
        return self._get("balance_and_position", BalanceAndPosition)

    @property
    def orders(self) -> "Orders":
        """orders channel.

        アクティブオーダーのみデータが格納されます。 キャンセル、約定済みなどは削除されます。

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-ws-order-channel
        """
        return self._get("orders", Orders)

    @property
    def ordersalgo(self) -> "OrdersAlgo":
        """ordersalgo channel.

        https://www.okx.com/docs-v5/en/#order-book-trading-algo-trading-ws-algo-orders-channel
        """
        return self._get("orders-algo", OrdersAlgo)

    @property
    def algoadvance(self) -> "AlgoAdvance":
        """algoadvance channel.

        https://www.okx.com/docs-v5/en/#order-book-trading-algo-trading-ws-advance-algo-orders-channel
        """
        return self._get("algo-advance", AlgoAdvance)

    @property
    def liquidationwarning(self) -> "LiquidationWarning":
        """liquidation-warning channel.

        https://www.okx.com/docs-v5/en/#trading-account-websocket-position-risk-warning
        """
        return self._get("liquidation-warning", LiquidationWarning)

    @property
    def accountgreeks(self) -> "AccountGreeks":
        """account-greeks channel.

        https://www.okx.com/docs-v5/en/#trading-account-websocket-account-greeks-channel
        """
        return self._get("account-greeks", AccountGreeks)


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


class Instruments(_UpdateStore): ...


class Tickers(_UpdateStore): ...


class OpenInterest(_UpdateStore): ...


class Candle(_CandleStore):
    _LIST_KEYS = ["ts", "o", "h", "l", "c", "vol", "volCcy"]


class Trades(_InsertStore): ...


class EstimatedPrice(_UpdateStore): ...


class MarkPrice(_UpdateStore): ...


class MarkPriceCandle(_CandleStore): ...


class PriceLimit(_UpdateStore): ...


class Books(DataStore):
    _KEYS = ["instId", "side", "px"]
    _LIST_KEYS = ["px", "sz", "liqSz", "ordSz"]

    def _init(self) -> None:
        self.checksum: dict[str, int] = {}
        self.ts: str | None = None

    def sorted(
        self, query: Item | None = None, limit: int | None = None
    ) -> dict[str, list[Item]]:
        return self._sorted(
            item_key="side",
            item_asc_key="asks",
            item_desc_key="bids",
            sort_key="px",
            query=query,
            limit=limit,
        )

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


class OptSummary(_UpdateStore): ...


class FundingRate(_UpdateStore): ...


class IndexCandle(_CandleStore): ...


class IndexTickers(_UpdateStore): ...


class Status(_InsertStore): ...


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


class LiquidationWarning(_UpdateStore): ...


class AccountGreeks(_UpdateStore):
    _KEYS = ["ccy"]
