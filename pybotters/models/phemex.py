from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Optional

import aiohttp

from ..store import DataStore, DataStoreCollection
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class PhemexDataStore(DataStoreCollection):
    """
    Phemexのデータストアマネージャー
    https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md
    """

    def _init(self) -> None:
        self.create("trade", datastore_class=Trade)
        self.create("orderbook", datastore_class=OrderBook)
        self.create("ticker", datastore_class=Ticker)
        self.create("market24h", datastore_class=Market24h)
        self.create("kline", datastore_class=Kline)
        self.create("accounts", datastore_class=Accounts)
        self.create("orders", datastore_class=Orders)
        self.create("positions", datastore_class=Positions)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """
        対応エンドポイント

        - GET /exchange/public/md/v2/kline (DataStore: kline)
        - GET /exchange/public/md/kline (DataStore: kline)
        - GET /exchange/public/md/v2/kline/last (DataStore: kline)
        - GET /exchange/public/md/v2/kline/list (DataStore: kline)
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
        return self.get("trade", Trade)

    @property
    def orderbook(self) -> "OrderBook":
        return self.get("orderbook", OrderBook)

    @property
    def ticker(self):
        return self.get("ticker", Ticker)

    @property
    def market24h(self) -> "Market24h":
        return self.get("market24h", Market24h)

    @property
    def kline(self) -> "Kline":
        return self.get("kline", Kline)

    @property
    def accounts(self) -> "Accounts":
        return self.get("accounts", Accounts)

    @property
    def orders(self) -> "Orders":
        return self.get("orders", Orders)

    @property
    def positions(self) -> "Positions":
        return self.get("positions", Positions)


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
                        "price": item[2],
                        "qty": item[3],
                    }
                    for item in trades
                ]
            )


class OrderBook(DataStore):
    _KEYS = ["symbol", "side", "price"]

    def _init(self) -> None:
        self.timestamp: Optional[int] = None

    def sorted(self, query: Item = None) -> dict[str, list[Item]]:
        if query is None:
            query = {}
        result = {"SELL": [], "BUY": []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item["side"]].append(item)
        result["SELL"].sort(key=lambda x: x["price"])
        result["BUY"].sort(key=lambda x: x["price"], reverse=True)
        return result

    def _onmessage(self, message: Item) -> None:
        symbol = message["symbol"]
        for book in (message.get("book"), message.get("orderbook_p")):
            if book is None:
                continue
            for key, side in (("bids", "BUY"), ("asks", "SELL")):
                for item in book[key]:
                    if item[1] != 0:
                        self._insert(
                            [
                                {
                                    "symbol": symbol,
                                    "side": side,
                                    "price": item[0],
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
                                    "price": item[0],
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

    def _onresponse(self, symbol: str, data: list[Item]) -> None:
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
