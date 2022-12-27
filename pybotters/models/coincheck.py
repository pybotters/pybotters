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
                pair = resp.url.query.get("pair")
                self.orderbook._onresponse(pair, data)

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        first_item = next(iter(msg), None)
        if isinstance(first_item, list):
            self.trades._onmessage(msg)
        elif isinstance(first_item, str):
            self.orderbook._onmessage(*msg)

    @property
    def trades(self) -> "Trades":
        return self.get("trades", Trades)

    @property
    def orderbook(self) -> "Orderbook":
        return self.get("orderbook", Orderbook)


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

    def _init(self):
        self.last_update_at: Optional[str] = None

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

    def _onresponse(self, pair: Optional[str], data: dict[list[str]]) -> None:
        if pair is None:
            pair = "btc_jpy"
        self._find_and_delete({"pair": pair})
        for side in data:
            for rate, amount in data[side]:
                self._insert(
                    [{"pair": pair, "side": side, "rate": rate, "amount": amount}]
                )

    def _onmessage(self, pair: str, data: dict[str, list[list[str]]]) -> None:
        self.last_update_at = data.pop("last_update_at")
        for side in data:
            for rate, amount in data[side]:
                if amount == "0":
                    self._delete([{"pair": pair, "side": side, "rate": rate}])
                else:
                    self._update(
                        [{"pair": pair, "side": side, "rate": rate, "amount": amount}]
                    )
