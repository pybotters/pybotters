from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Awaitable, cast

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    import aiohttp

    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse


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

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
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
