from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BitgetV2DataStore(DataStoreCollection):
    """DataStoreCollection for Bitget V2 API"""

    def _init(self) -> None:
        self._create("ticker", datastore_class=Ticker)
        self._create("candle", datastore_class=Candle)
        self._create("book", datastore_class=Book)
        self._create("trade", datastore_class=Trade)
        self._create("account", datastore_class=Account)
        self._create("positions", datastore_class=Positions)
        self._create("fill", datastore_class=Fill)
        self._create("orders", datastore_class=Orders)
        self._create("orders-algo", datastore_class=OrdersAlgo)
        self._create("positions-history", datastore_class=PositionsHistory)

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        data = msg.get("data")
        if data:
            channel: str = msg["arg"]["channel"]
            if channel == "ticker":
                self.ticker._onmessage(msg)
            elif channel.startswith("candle"):
                self.candle._onmessage(msg)
            elif channel.startswith("books"):
                self.book._onmessage(msg)
            elif channel == "trade":
                self.trade._onmessage(msg)
            elif channel == "account":
                self.account._onmessage(msg)
            elif channel == "positions":
                self.positions._onmessage(msg)
            elif channel == "fill":
                self.fill._onmessage(msg)
            elif channel == "orders":
                self.orders._onmessage(msg)
            elif channel == "orders-algo":
                self.orders_algo._onmessage(msg)
            elif channel == "positions-history":
                self.positions_history._onmessage(msg)

        event = msg.get("event")
        if event == "error":
            logger.warning(msg)

    @property
    def ticker(self):
        """ticker channel.

        * https://www.bitget.com/api-doc/spot/websocket/public/Tickers-Channel
        * https://www.bitget.com/api-doc/contract/websocket/public/Tickers-Channel

        The following data will be added as identifiers:

        * ``instType``
        """
        return self._get("ticker", Ticker)

    @property
    def candle(self) -> Candle:
        """candle channel.

        * https://www.bitget.com/api-doc/spot/websocket/public/Candlesticks-Channel
        * https://www.bitget.com/api-doc/contract/websocket/public/Candlesticks-Channel

        For the source data, the array is converted to a dictionary in the following format:

        * ``[0]`` -> ``startTime``
        * ``[1]`` -> ``openPr``
        * ``[2]`` -> ``highPr``
        * ``[3]`` -> ``lowPr``
        * ``[4]`` -> ``closePr``
        * ``[5]`` -> ``baseVolume``
        * ``[6]`` -> ``quoteVolume``
        * ``[7]`` -> ``usdtVolume``

        The following data will be added as identifiers:

        * ``instType``
        * ``instId``
        * ``granularity``
        """
        return self._get("candle", Candle)

    @property
    def book(self) -> Book:
        """book channel.

        * https://www.bitget.com/api-doc/spot/websocket/public/Depth-Channel
        * https://www.bitget.com/api-doc/contract/websocket/public/Order-Book-Channel

        For the source data, the asks/bids array is converted to a dictionary in the following format:

        * ``[0]`` -> ``price``
        * ``[1]`` -> ``amount``

        The following data will be added as identifiers:

        * ``instType``
        * ``instId``
        * ``side``
        """
        return self._get("book", Book)

    @property
    def trade(self) -> Trade:
        """trade channel.

        * https://www.bitget.com/api-doc/spot/websocket/public/Trades-Channel
        * https://www.bitget.com/api-doc/contract/websocket/public/New-Trades-Channel

        The following data will be added as identifiers:

        * ``instType``
        * ``instId``
        """
        return self._get("trade", Trade)

    @property
    def account(self) -> Account:
        """account channel.

        * https://www.bitget.com/api-doc/spot/websocket/private/Account-Channel
        * https://www.bitget.com/api-doc/contract/websocket/private/Account-Channel

        The following data will be added as identifiers:

        * ``instType``
        """
        return self._get("account", Account)

    @property
    def positions(self) -> Positions:
        """positions channel.

        * https://www.bitget.com/api-doc/contract/websocket/private/Positions-Channel

        The following data will be added as identifiers:

        * ``instType``
        """
        return self._get("positions", Positions)

    @property
    def fill(self) -> Fill:
        """fill channel.

        * https://www.bitget.com/api-doc/spot/websocket/private/Fill-Channel
        * https://www.bitget.com/api-doc/contract/websocket/private/Fill-Channel

        The following data will be added as identifiers:

        * ``instType``
        """
        return self._get("fill", Fill)

    @property
    def orders(self) -> Orders:
        """orders channel.

        * https://www.bitget.com/api-doc/spot/websocket/private/Order-Channel
        * https://www.bitget.com/api-doc/contract/websocket/private/Order-Channel

        The following data will be added as identifiers:

        * ``instType``
        """
        return self._get("orders", Orders)

    @property
    def orders_algo(self) -> OrdersAlgo:
        """orders-algo channel.

        * https://www.bitget.com/api-doc/spot/websocket/private/Plan-Order-Channel
        * https://www.bitget.com/api-doc/contract/websocket/private/Plan-Order-Channel

        The following data will be added as identifiers:

        * ``instType``
        """
        return self._get("orders-algo", OrdersAlgo)

    @property
    def positions_history(self) -> PositionsHistory:
        """positions-history channel.

        * https://www.bitget.com/api-doc/contract/websocket/private/History-Positions-Channel

        The following data will be added as identifiers:

        * ``instType``
        """
        return self._get("positions-history", PositionsHistory)


class Ticker(DataStore):
    _KEYS = ["instType", "instId"]

    def _onmessage(self, msg: Item) -> None:
        inst_type = msg["arg"]["instType"]
        # Combine "instType" to identify markets
        data = [{"instType": inst_type} | x for x in msg["data"]]

        # The action in ticker will only receive "snapshot"
        self._update(data)


class Candle(DataStore):
    _KEYS = ["instType", "instId", "granularity", "startTime"]

    def _onmessage(self, msg: Item) -> None:
        inst_type = msg["arg"]["instType"]
        inst_id = msg["arg"]["instId"]
        granularity = msg["arg"]["channel"]

        # Convert array to dictionary
        data = [
            {
                "instType": inst_type,
                "instId": inst_id,
                "granularity": granularity,
                "startTime": x[0],
                "openPr": x[1],
                "highPr": x[2],
                "lowPr": x[3],
                "closePr": x[4],
                "baseVolume": x[5],
                "quoteVolume": x[6],
                "usdtVolume": x[7],  # NOTE: Is this correct? from market/Get-Tickers.
            }
            for x in msg["data"]
        ]

        action = msg["action"]
        if action == "snapshot":
            self._insert(data)
        elif action == "update":
            self._update(data)


class Book(DataStore):
    _KEYS = ["instType", "instId", "side", "price"]

    def _onmessage(self, msg: Item) -> None:
        action = msg["action"]
        inst_type = msg["arg"]["instType"]
        inst_id = msg["arg"]["instId"]

        data_to_insert = []
        data_to_update = []
        data_to_delete = []
        for book in msg["data"]:
            for side in ("asks", "bids"):
                for row in book[side]:
                    converted_row = {
                        "instType": inst_type,
                        "instId": inst_id,
                        "side": side,
                        "price": row[0],
                        "amount": row[1],
                    }
                    if action == "snapshot":
                        data_to_insert.append(converted_row)
                    elif converted_row["amount"] != "0":
                        data_to_update.append(converted_row)
                    else:
                        data_to_delete.append(converted_row)

        # Cleanup on reconnect
        if action == "snapshot":
            self._find_and_delete({"instType": inst_type, "instId": inst_id})

        self._insert(data_to_insert)
        self._update(data_to_update)
        self._delete(data_to_delete)

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


class Trade(DataStore):
    _KEYS = ["instType", "instId", "tradeId"]
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        inst_type = msg["arg"]["instType"]
        inst_id = msg["arg"]["instId"]

        # Combine "instType" and "instId" to identify markets
        data = [{"instType": inst_type, "instId": inst_id} | x for x in msg["data"]]

        self._insert(data)


class Account(DataStore):
    _KEYS = ["instType"]

    def _onmessage(self, msg: Item) -> None:
        inst_type = msg["arg"]["instType"]

        data = [{"instType": inst_type} | x for x in msg["data"]]

        self._update(data)


class Positions(DataStore):
    _KEYS = ["instType", "instId", "posId"]

    def _onmessage(self, msg: Item) -> None:
        inst_type = msg["arg"]["instType"]

        data_to_update = []
        data_to_delete = []
        for item in msg["data"]:
            item = {"instType": inst_type} | item
            if item["available"] != "0":
                data_to_update.append(item)
            else:
                data_to_delete.append(item)

        self._update(data_to_update)
        self._delete(data_to_delete)


class Fill(DataStore):
    _KEYS = ["instType", "tradeId", "symbol"]
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        inst_type = msg["arg"]["instType"]

        data = [{"instType": inst_type} | x for x in msg["data"]]

        self._insert(data)


class Orders(DataStore):
    _KEYS = ["instType", "instId", "orderId"]

    def _onmessage(self, msg: Item) -> None:
        inst_type = msg["arg"]["instType"]

        data_to_update = []
        data_to_delete = []
        for item in msg["data"]:
            item = {"instType": inst_type} | item
            if item["status"] in ("live", "partially_filled"):
                data_to_update.append(item)
            elif item["status"] in ("filled", "canceled"):
                data_to_delete.append(item)

        self._update(data_to_update)
        self._delete(data_to_delete)


class OrdersAlgo(DataStore):
    _KEYS: list[str] = ["instType", "instId", "orderId"]

    def _onmessage(self, msg: Item) -> None:
        inst_type = msg["arg"]["instType"]

        data_to_update = []
        data_to_delete = []
        for item in msg["data"]:
            item = {"instType": inst_type} | item
            if item["status"] in ("live", "executing"):
                data_to_update.append(item)
            elif item["status"] in ("executed", "fail_execute", "cancelled"):
                data_to_delete.append(item)

        self._update(data_to_update)
        self._delete(data_to_delete)


class PositionsHistory(DataStore):
    _KEYS = ["instType", "instId", "posId"]
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        inst_type = msg["arg"]["instType"]

        data = [{"instType": inst_type} | x for x in msg["data"]]

        self._insert(data)
