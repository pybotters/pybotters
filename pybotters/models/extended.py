from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pybotters.store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from pybotters.typedefs import Item
    from pybotters.ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class ExtendedDataStore(DataStoreCollection):
    """DataStoreCollection for Extended exchange.

    https://api.docs.extended.exchange/
    """

    def _init(self) -> None:
        self._create("orderbook", datastore_class=Orderbook)
        self._create("trades", datastore_class=Trades)
        self._create("funding", datastore_class=Funding)
        self._create("candles", datastore_class=Candles)
        self._create("orders", datastore_class=Orders)
        self._create("positions", datastore_class=Positions)
        self._create("balance", datastore_class=Balance)
        self._create("account_trades", datastore_class=AccountTrades)

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse | None = None) -> None:
        type_ = msg.get("type")
        data = msg.get("data")

        if data is None:
            if msg.get("error"):
                logger.warning(msg)
            return

        if type_ == "SNAPSHOT":
            self.orderbook._onsnapshot(data)
        elif type_ == "DELTA":
            self.orderbook._ondelta(data)
        elif type_ == "TRADE":
            self.trades._onmessage(data)
        elif type_ == "BALANCE":
            self.balance._onmessage(data)
        elif type_ == "ORDER":
            self.orders._onmessage(data)
        elif type_ == "POSITION":
            self.positions._onmessage(data)

    @property
    def orderbook(self) -> Orderbook:
        return self._get("orderbook", Orderbook)

    @property
    def trades(self) -> Trades:
        return self._get("trades", Trades)

    @property
    def funding(self) -> Funding:
        return self._get("funding", Funding)

    @property
    def candles(self) -> Candles:
        return self._get("candles", Candles)

    @property
    def orders(self) -> Orders:
        return self._get("orders", Orders)

    @property
    def positions(self) -> Positions:
        return self._get("positions", Positions)

    @property
    def balance(self) -> Balance:
        return self._get("balance", Balance)

    @property
    def account_trades(self) -> AccountTrades:
        return self._get("account_trades", AccountTrades)


class Orderbook(DataStore):
    _KEYS = ["market", "side", "price"]

    def _onsnapshot(self, data: Item) -> None:
        market = data.get("m") or data.get("market", "")
        items: list[Item] = []
        for entry in data.get("b") or data.get("bid", []):
            price = entry.get("p") or entry.get("price")
            qty = entry.get("q") or entry.get("qty")
            items.append(
                {"market": market, "side": "bid", "price": price, "qty": qty}
            )
        for entry in data.get("a") or data.get("ask", []):
            price = entry.get("p") or entry.get("price")
            qty = entry.get("q") or entry.get("qty")
            items.append(
                {"market": market, "side": "ask", "price": price, "qty": qty}
            )
        self._find_and_delete({"market": market})
        self._insert(items)

    def _ondelta(self, data: Item) -> None:
        self._onsnapshot(data)

    def sorted(
        self,
        query: Item | None = None,
        limit: int | None = None,
    ) -> dict[str, list[Item]]:
        return self._sorted(
            item_key="side",
            item_asc_key="ask",
            item_desc_key="bid",
            sort_key="price",
            query=query,
            limit=limit,
        )


class Trades(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, data: Item | list[Item]) -> None:
        if isinstance(data, list):
            self._insert(data)
        elif isinstance(data, dict):
            self._insert([data])


class Funding(DataStore):
    _KEYS = ["market"]

    def _onmessage(self, data: Item) -> None:
        if isinstance(data, dict):
            self._update([data])


class Candles(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, data: Item | list[Item]) -> None:
        if isinstance(data, list):
            self._insert(data)
        elif isinstance(data, dict):
            self._insert([data])


class Orders(DataStore):
    _KEYS = ["id"]

    def _onmessage(self, data: Item | list[Item]) -> None:
        items = data if isinstance(data, list) else [data]
        self._update(items)


class Positions(DataStore):
    _KEYS = ["market"]

    def _onmessage(self, data: Item | list[Item]) -> None:
        items = data if isinstance(data, list) else [data]
        self._update(items)


class Balance(DataStore):
    def _onmessage(self, data: Item) -> None:
        if isinstance(data, dict):
            self._clear()
            self._insert([data])


class AccountTrades(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, data: Item | list[Item]) -> None:
        if isinstance(data, list):
            self._insert(data)
        elif isinstance(data, dict):
            self._insert([data])
