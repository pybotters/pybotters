from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Optional

import aiohttp

from ..store import DataStore, DataStoreManager
from ..typedefs import Item
from ..ws import ClientWebSocketResponse


class CoincheckDataStore(DataStoreManager):
    def _init(self) -> None:
        self.create("trades", datastore_class=Trades)
        self.create("orderbook", datastore_class=Orderbook)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if resp.url.path == "/api/order_books":
                symbol = resp.url.query.get("symbol")
                self.orderbook._onresponse(symbol, data)

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if len(msg) == 5:
            self.trades._onmessage(*msg)
        elif len(msg) == 2:
            self.orderbook._onmessage(*msg)

    @property
    def trades(self) -> "Trades":
        return self.get("trades", Trades)

    @property
    def orderbook(self) -> "Orderbook":
        return self.get("orderbook", Orderbook)


class Trades(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, id: int, pair: str, rate: str, amount: str, side: str) -> None:
        self._insert(
            [{"id": id, "pair": pair, "rate": rate, "amount": amount, "side": side}]
        )


class Orderbook(DataStore):
    _KEYS = ["side", "rate"]

    def sorted(self, query: Optional[Item] = None) -> dict[str, list[list[str]]]:
        if query is None:
            query = {}
        result = {"asks": [], "bids": []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item["side"]].append([item["rate"], item["amount"]])
        result["asks"].sort(key=lambda x: float(x[0]))
        result["bids"].sort(key=lambda x: float(x[0]), reverse=True)
        return result

    def _onresponse(self, symbol: Optional[str], data: dict[list[str]]) -> None:
        if symbol is None:
            symbol = "btc_jpy"
        result = []
        for side in data:
            for rate, amount in data[side]:
                result.append(
                    {"symbol": symbol, "side": side, "rate": rate, "amount": amount}
                )
        self._insert(result)

    def _onmessage(self, pair: str, data: dict[str, list[list[str]]]) -> None:
        for side in data:
            for rate, amount in data[side]:
                if amount == "0":
                    self._delete([{"side": side, "rate": rate}])
                else:
                    self._update([{"side": side, "rate": rate, "amount": amount}])
