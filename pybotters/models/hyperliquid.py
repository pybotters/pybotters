from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class HyperliquidDataStore(DataStoreCollection):
    """DataStoreCollection for Hyperliquid"""

    def _init(self) -> None:
        self._create("l2Book", datastore_class=L2Book)
        self._create("trades", datastore_class=Trades)
        # TODO: Add other data streams

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        channel = msg.get("channel")

        if channel == "l2Book":
            self.l2_book._onmessage(msg)
        elif channel == "trades":
            self.trades._onmessage(msg)

        # TODO: Add other data streams

        elif channel == "error":
            logger.warning(msg)

    @property
    def l2_book(self) -> L2Book:
        """``l2Book`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data structure:

        .. code:: python

            [
                {
                    "coin": "BTC",
                    "side": "A",
                    "px": "20300",
                    "sz": "3",
                    "n": 3,
                },
                {
                    "coin": "BTC",
                    "side": "A",
                    "px": "20200",
                    "sz": "2",
                    "n": 2,
                },
                {
                    "coin": "BTC",
                    "side": "A",
                    "px": "20100",
                    "sz": "1",
                    "n": 1,
                },
                {
                    "coin": "BTC",
                    "side": "B",
                    "px": "19900",
                    "sz": "1",
                    "n": 1,
                },
                {
                    "coin": "BTC",
                    "side": "B",
                    "px": "19800",
                    "sz": "2",
                    "n": 2,
                },
                {
                    "coin": "BTC",
                    "side": "B",
                    "px": "19700",
                    "sz": "3",
                    "n": 3,
                },
            ]
        """
        return self._get("l2Book", L2Book)

    @property
    def trades(self) -> Trades:
        """``trades`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data structure:

        .. code:: python

            [
                {
                    "coin": "AVAX",
                    "side": "B",
                    "px": "18.435",
                    "sz": "93.53",
                    "time": 1681222254710,
                    "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                    "tid": 118906512037719,
                    "users": [
                        "0x0000000000000000000000000000000000000000",
                        "0x0000000000000000000000000000000000000000",
                    ],
                },
            ]
        """
        return self._get("trades", Trades)


class L2Book(DataStore):
    _KEYS = ["coin", "side", "px"]

    def _init(self) -> None:
        self._time: int | None = None

    def _onmessage(self, msg: Item) -> None:
        coin = msg["data"]["coin"]
        time = msg["data"]["time"]
        levels = msg["data"]["levels"]

        data_to_insert: list[Item] = []
        for side_id, side_index in (("B", 0), ("A", 1)):
            for level in levels[side_index]:
                item = {
                    "coin": coin,
                    "side": side_id,
                    "px": level["px"],
                    "sz": level["sz"],
                    "n": level["n"],
                }
                data_to_insert.append(item)

        self._find_and_delete({"coin": coin})
        self._insert(data_to_insert)

        self._time = time

    def sorted(
        self, query: Item | None = None, limit: int | None = None
    ) -> dict[str, list[Item]]:
        return self._sorted(
            item_key="side",
            item_asc_key="A",
            item_desc_key="B",
            sort_key="px",
            query=query,
            limit=limit,
        )

    @property
    def time(self) -> int | None:
        """Timestamp of the last update."""
        return self._time


class Trades(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        self._insert(msg["data"])
