from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse


class bitbankDataStore(DataStoreCollection):
    """bitbank の DataStoreCollection クラス"""

    def _init(self) -> None:
        self._create("transactions", datastore_class=Transactions)
        self._create("depth", datastore_class=Depth)
        self._create("ticker", datastore_class=Ticker)

    def _onmessage(self, msg: str, ws: ClientWebSocketResponse) -> None:
        if msg.startswith("42"):
            data_json = json.loads(msg[2:])
            room_name = data_json[1]["room_name"]
            data = data_json[1]["message"]["data"]
            if "transactions" in room_name:
                self.transactions._onmessage(room_name, data)
            elif "depth" in room_name:
                self.depth._onmessage(room_name, data)
            elif "ticker" in room_name:
                self.ticker._onmessage(room_name, data)

    @property
    def transactions(self) -> "Transactions":
        """transactions channel.

        https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-stream.md#transactions
        """
        return self._get("transactions", Transactions)

    @property
    def depth(self) -> "Depth":
        """depth channel.

        * https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-stream.md#depth-diff
        * https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-stream.md#depth-whole
        """
        return self._get("depth", Depth)

    @property
    def ticker(self) -> "Ticker":
        """ticker channel.

        https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-stream.md#ticker
        """
        return self._get("ticker", Ticker)


class Transactions(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, room_name: str, data: dict[str, list[Item]]) -> None:
        for item in data["transactions"]:
            pair = room_name.replace("transactions_", "")
            self._insert([{"pair": pair, **item}])


class Depth(DataStore):
    _KEYS = ["pair", "side", "price"]

    def _init(self) -> None:
        self.timestamp: int | None = None

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

    def _onmessage(self, room_name: str, data: dict[str, object]) -> None:
        if "whole" in room_name:
            pair = room_name.replace("depth_whole_", "")
            result = self.find({"pair": pair})
            self._delete(result)
            tuples = (("bids", "bids"), ("asks", "asks"))
            self.timestamp = cast(int, data["timestamp"])
        else:
            pair = room_name.replace("depth_diff_", "")
            tuples = (("b", "bids"), ("a", "asks"))
            self.timestamp = cast(int, data["t"])

        for side_item, side in tuples:
            for item in cast("list[list[str]]", data[side_item]):
                if item[1] != "0":
                    self._update(
                        [
                            {
                                "pair": pair,
                                "side": side,
                                "price": item[0],
                                "amount": item[1],
                            }
                        ]
                    )
                else:
                    self._delete([{"pair": pair, "side": side, "price": item[0]}])


class Ticker(DataStore):
    _KEYS = ["pair"]

    def _onmessage(self, room_name: str, item: Item) -> None:
        pair = room_name.replace("ticker_", "")
        self._insert([{"pair": pair, **item}])
