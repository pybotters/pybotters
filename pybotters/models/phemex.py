from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Awaitable

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    import aiohttp

    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class PhemexDataStore(DataStoreCollection):
    """Phemex の DataStoreCollection クラス"""

    def _init(self) -> None:
        self._create("trade", datastore_class=Trade)
        self._create("orderbook", datastore_class=OrderBook)
        self._create("ticker", datastore_class=Ticker)
        self._create("market24h", datastore_class=Market24h)
        self._create("kline", datastore_class=Kline)
        self._create("accounts", datastore_class=Accounts)
        self._create("orders", datastore_class=Orders)
        self._create("positions", datastore_class=Positions)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data.

        対応エンドポイント

        - GET /exchange/public/md/v2/kline (:attr:`.PhemexDataStore.kline`)
        - GET /exchange/public/md/kline (:attr:`.PhemexDataStore.kline`)
        - GET /exchange/public/md/v2/kline/last (:attr:`.PhemexDataStore.kline`)
        - GET /exchange/public/md/v2/kline/list (:attr:`.PhemexDataStore.kline`)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if resp.url.path in (
                "/exchange/public/md/v2/kline",
                "/exchange/public/md/kline",
                "/exchange/public/md/v2/kline/last",
                "/exchange/public/md/v2/kline/list",
            ):
                symbol = resp.url.query.get("symbol")
                if symbol:
                    self.kline._onresponse(symbol, data)

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if not msg.get("id"):
            if "trades" in msg or "trades_p" in msg:
                self.trade._onmessage(msg)
            elif "book" in msg or "orderbook_p" in msg:
                self.orderbook._onmessage(msg)
            elif "tick" in msg or "tick_p" in msg:
                self.ticker._onmessage(msg)
            elif "market24h" in msg or "market24h_p" in msg:
                self.market24h._onmessage(msg)
            elif "kline" in msg or "kline_p" in msg:
                self.kline._onmessage(msg)

            if "accounts" in msg or "accounts_p" in msg:
                self.accounts._onmessage(msg)
            if "orders" in msg or "orders_p" in msg:
                self.orders._onmessage(msg)
            if "positions" in msg or "positions_p" in msg:
                self.positions._onmessage(msg)

        if msg.get("error"):
            logger.warning(msg)

    @property
    def trade(self) -> "Trade":
        """trades/trades_p channel.

        * Contract Websocket API
            * https://phemex-docs.github.io/#trade-message
        * Hedged Contract Websocket API
            * https://phemex-docs.github.io/#trade-message-format
        * Spot Websocket API
            * https://phemex-docs.github.io/#trade-message-2
        """
        return self._get("trade", Trade)

    @property
    def orderbook(self) -> "OrderBook":
        """book/orderbook_p channel.

        * Contract Websocket API
            * https://phemex-docs.github.io/#orderbook-message
        * Hedged Contract Websocket API
            * https://phemex-docs.github.io/#orderbook-message-2
        * Spot Websocket API
            * https://phemex-docs.github.io/#orderbook-message-3
        """
        return self._get("orderbook", OrderBook)

    @property
    def ticker(self):
        """tick/tick_p channel.

        * Contract Websocket API
            * https://phemex-docs.github.io/#tick-message
        * Hedged Contract Websocket API
            * https://phemex-docs.github.io/#push-event
        """
        return self._get("ticker", Ticker)

    @property
    def market24h(self) -> "Market24h":
        """market24h/market24h_p channel.

        * Contract Websocket API
            * https://phemex-docs.github.io/#24-hours-ticker-message
        * Hedged Contract Websocket API
            * httpshttps://phemex-docs.github.io/#hours-ticker-message-format
        """
        return self._get("market24h", Market24h)

    @property
    def kline(self) -> "Kline":
        """kline/kline_pkline_p channel.

        * Contract Websocket API
            * https://phemex-docs.github.io/#kline-message
        * Hedged Contract Websocket API
            * https://phemex-docs.github.io/#kline-message-format
        * Spot Websocket API
            * https://phemex-docs.github.io/#kline-message-2
        """
        return self._get("kline", Kline)

    @property
    def accounts(self) -> "Accounts":
        """accounts/accounts_p channel.

        * Contract Websocket API
            * https://phemex-docs.github.io/#account-order-position-aop-message
        * Hedged Contract Websocket API
            * https://phemex-docs.github.io/#account-order-position-aop-message-sample
        """
        return self._get("accounts", Accounts)

    @property
    def orders(self) -> "Orders":
        """orders/orders_p channel.

        アクティブオーダーのみデータが格納されます。 キャンセル、約定済みなどは削除されます。

        * Contract Websocket API
            * https://phemex-docs.github.io/#account-order-position-aop-message
        * Hedged Contract Websocket API
            * https://phemex-docs.github.io/#account-order-position-aop-message-sample
        """
        return self._get("orders", Orders)

    @property
    def positions(self) -> "Positions":
        """positions/positions_p channel.

        * Contract Websocket API
            * https://phemex-docs.github.io/#account-order-position-aop-message
        * Hedged Contract Websocket API
            * https://phemex-docs.github.io/#account-order-position-aop-message-sample
        """
        return self._get("positions", Positions)


class Trade(DataStore):
    _KEYS = ["symbol", "timestamp"]
    _MAXLEN = 99999

    def _onmessage(self, message: Item) -> None:
        symbol = message.get("symbol")
        for trades in (message.get("trades", []), message.get("trades_p", [])):
            self._insert(
                [
                    {
                        "symbol": symbol,
                        "timestamp": item[0],
                        "side": item[1],
                        "priceEp": item[2],
                        "qty": item[3],
                    }
                    for item in trades
                ]
            )


class OrderBook(DataStore):
    _KEYS = ["symbol", "side", "priceEp"]

    def _init(self) -> None:
        self.timestamp: int | None = None

    def sorted(
        self, query: Item | None = None, limit: int | None = None
    ) -> dict[str, list[Item]]:
        return self._sorted(
            item_key="side",
            item_asc_key="asks",
            item_desc_key="bids",
            sort_key="priceEp",
            query=query,
            limit=limit,
        )

    def _onmessage(self, message: Item) -> None:
        symbol = message["symbol"]
        if message.get("type") == "snapshot":
            self._find_and_delete({"symbol": symbol})
        for book in (message.get("book"), message.get("orderbook_p")):
            if book is None:
                continue
            for side in ("asks", "bids"):
                for item in book[side]:
                    if float(item[1]) != 0.0:
                        self._insert(
                            [
                                {
                                    "symbol": symbol,
                                    "side": side,
                                    "priceEp": item[0],
                                    "qty": item[1],
                                }
                            ]
                        )
                    else:
                        self._delete(
                            [
                                {
                                    "symbol": symbol,
                                    "side": side,
                                    "priceEp": item[0],
                                }
                            ]
                        )

        self.timestamp = message["timestamp"]


class Ticker(DataStore):
    _KEYS = ["symbol"]

    def _onmessage(self, message: Item):
        if "tick" in message:
            self._update([message["tick"]])
        if "tick_p" in message:
            self._update([message["tick_p"]])


class Market24h(DataStore):
    _KEYS = ["symbol"]

    def _onmessage(self, message: Item) -> None:
        if "market24h" in message:
            self._update([message["market24h"]])
        if "market24h_p" in message:
            self._update([message["market24h_p"]])


class Kline(DataStore):
    _KEYS = ["symbol", "timestamp", "interval"]

    def _onresponse(self, symbol: str, data: Item) -> None:
        self._insert(
            [
                {
                    "symbol": symbol,
                    "timestamp": item[0],
                    "interval": item[1],
                    "last_close": item[2],
                    "open": item[3],
                    "high": item[4],
                    "low": item[5],
                    "close": item[6],
                    "volume": item[7],
                    "turnover": item[8],
                }
                for item in data["data"]["rows"]
            ]
        )

    def _onmessage(self, message: Item) -> None:
        symbol = message.get("symbol")
        for kline in (message.get("kline", []), message.get("kline_p", [])):
            self._insert(
                [
                    {
                        "symbol": symbol,
                        "timestamp": item[0],
                        "interval": item[1],
                        "last_close": item[2],
                        "open": item[3],
                        "high": item[4],
                        "low": item[5],
                        "close": item[6],
                        "volume": item[7],
                        "turnover": item[8],
                    }
                    for item in kline
                ]
            )


class Accounts(DataStore):
    _KEYS = ["accountID", "currency"]

    def _onmessage(self, message: Item) -> None:
        for data in (message.get("accounts", []), message.get("accounts_p", [])):
            self._update(data)


class Orders(DataStore):
    _KEYS = ["orderID"]

    def _onmessage(self, message: Item) -> None:
        for data in (message.get("orders", []), message.get("orders_p", [])):
            for item in data:
                if item["ordStatus"] == "New":
                    if self.get(item):
                        self._update([item])
                    else:
                        self._insert([item])
                elif item["ordStatus"] == "Untriggered":
                    self._insert([item])
                elif item["ordStatus"] == "PartiallyFilled":
                    self._update([item])
                elif item["ordStatus"] in ("Filled", "Deactivated"):
                    self._delete([item])
                elif item["ordStatus"] == "Canceled" and item["action"] != "Replace":
                    self._delete([item])


class Positions(DataStore):
    _KEYS = ["accountID", "symbol"]

    def _onmessage(self, message: Item) -> None:
        for data in (message.get("positions", []), message.get("positions_p", [])):
            self._insert(data)
