from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pybotters.store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from pybotters.typedefs import Item
    from pybotters.ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class HyperliquidDataStore(DataStoreCollection):
    """DataStoreCollection for Hyperliquid."""

    def _init(self) -> None:
        self._create("allMids", datastore_class=AllMids)
        self._create("notification", datastore_class=Notification)
        self._create("webData2", datastore_class=WebData2)
        self._create("candle", datastore_class=Candle)
        self._create("l2Book", datastore_class=L2Book)
        self._create("trades", datastore_class=Trades)
        self._create("orderUpdates", datastore_class=OrderUpdates)
        self._create("userEvents", datastore_class=UserEvents)
        self._create("userFills", datastore_class=UserFills)
        self._create("userFundings", datastore_class=UserFundings)
        self._create(
            "userNonFundingLedgerUpdates",
            datastore_class=UserNonFundingLedgerUpdates,
        )
        self._create("activeAssetCtx", datastore_class=ActiveAssetCtx)
        self._create("activeAssetData", datastore_class=ActiveAssetData)
        self._create("userTwapSliceFills", datastore_class=UserTwapSliceFills)
        self._create("userTwapHistory", datastore_class=UserTwapHistory)
        self._create("bbo", datastore_class=Bbo)
        # TODO: Add other data streams

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse | None = None) -> None:
        channel = msg.get("channel")

        if channel == "allMids":
            self.all_mids._onmessage(msg)
        elif channel == "notification":
            self.notification._onmessage(msg)
        elif channel == "webData2":
            self.web_data2._onmessage(msg)
        elif channel == "candle":
            self.candle._onmessage(msg)
        elif channel == "l2Book":
            self.l2_book._onmessage(msg)
        elif channel == "trades":
            self.trades._onmessage(msg)
        elif channel == "orderUpdates":
            self.order_updates._onmessage(msg)
        elif channel == "user":
            self.user_events._onmessage(msg)
        elif channel == "userFills":
            self.user_fills._onmessage(msg)
        elif channel == "userFundings":
            self.user_fundings._onmessage(msg)
        elif channel == "userNonFundingLedgerUpdates":
            self.user_non_funding_ledger_updates._onmessage(msg)
        elif channel == "activeAssetCtx":
            self.active_asset_ctx._onmessage(msg)
        elif channel == "activeAssetData":
            self.active_asset_data._onmessage(msg)
        elif channel == "userTwapSliceFills":
            self.user_twap_slice_fills._onmessage(msg)
        elif channel == "userTwapHistory":
            self.user_twap_history._onmessage(msg)
        elif channel == "bbo":
            self.bbo._onmessage(msg)
        elif channel == "error":
            logger.warning(msg)

    @property
    def all_mids(self) -> AllMids:
        """``allMids`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Mutable

        Keys: ``["coin"]``

        Data structure:

        .. code:: python

            [
                {"coin": "AVAX", "px": "18.435"},
                {"coin": "@107", "px": "18.62041381"},
            ]
        """
        return self._get("allMids", AllMids)

    @property
    def notification(self) -> Notification:
        """``notification`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Append-only

        Data structure:

        .. code:: python


            [
                {"notification": "<notification>"},
            ]
        """
        return self._get("notification", Notification)

    @property
    def web_data2(self) -> WebData2:
        """``webData2`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Mutable

        Keys: ``["user"]``

        Data structure:

        .. code:: python

            [
                {
                    "clearinghouseState": {
                        "marginSummary": {
                            "accountValue": "29.78001",
                            "totalNtlPos": "0.0",
                            "totalRawUsd": "29.78001",
                            "totalMarginUsed": "0.0",
                        },
                        "crossMarginSummary": {
                            "accountValue": "29.78001",
                            "totalNtlPos": "0.0",
                            "totalRawUsd": "29.78001",
                            "totalMarginUsed": "0.0",
                        },
                        "crossMaintenanceMarginUsed": "0.0",
                        "withdrawable": "29.78001",
                        "assetPositions": [],
                        "time": 1733968369395,
                    },
                    "user": "0x0000000000000000000000000000000000000001",
                },
            ]
        """
        return self._get("webData2", WebData2)

    @property
    def candle(self) -> Candle:
        """``candle`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Mutable

        Keys: ``["t", "T", "s", "i"]``

        Data structure:

        .. code:: python


            [
                {
                    "t": 1681923600000,
                    "T": 1681924499999,
                    "s": "BTC",
                    "i": "1m",
                    "o": "106640.0",
                    "c": "106678.0",
                    "h": "106678.0",
                    "l": "106640.0",
                    "v": "1.92753",
                    "n": 80,
                },
            ]
        """
        return self._get("candle", Candle)

    @property
    def l2_book(self) -> L2Book:
        """``l2Book`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Mutable

        Keys: ``["coin", "side", "px"]``

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

        Data type: Append-only

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

    @property
    def order_updates(self) -> OrderUpdates:
        """``orderUpdates`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Mutable; active orders only

        Keys: ``["coin", "oid"]``

        Data structure:

        .. code:: python

            [
                {
                    "coin": "ETH",
                    "side": "A",
                    "limitPx": "2412.7",
                    "sz": "0.0",
                    "oid": 1,
                    "timestamp": 1724361546645,
                    "origSz": "0.0076",
                    "cloid": None,
                    "status": "<status>",
                    "statusTimestamp": 1724361546645,
                },
            ]
        """
        return self._get("orderUpdates", OrderUpdates)

    @property
    def user_events(self) -> UserEvents:
        """``userEvents`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Append-only

        Data structure:

        .. code:: python

            [
                # fills
                {
                    "type": "fills",
                    "coin": "AVAX",
                    "px": "18.435",
                    "sz": "93.53",
                    "side": "B",
                    "time": 1681222254710,
                    "startPosition": "26.86",
                    "dir": "Open Long",
                    "closedPnl": "0.0",
                    "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                    "oid": 90542681,
                    "crossed": False,
                    "fee": "0.01",
                    "tid": 118906512037719,
                    "liquidation": {
                        "liquidatedUser": "0x0000000000000000000000000000000000000000",
                        "markPx": "18.435",
                        "method": "<method>",
                    },
                    "feeToken": "USDC",
                    "builderFee": "0.01",
                },
                # funding
                {
                    "type": "funding",
                    "time": 1681222254710,
                    "coin": "ETH",
                    "usdc": "-3.625312",
                    "szi": "49.1477",
                    "fundingRate": "0.0000417",
                },
                # liquidation
                {
                    "type": "liquidation",
                    "lid": 0,
                    "liquidator": "0x0000000000000000000000000000000000000000",
                    "liquidated_user": "0x0000000000000000000000000000000000000000",
                    "liquidated_ntl_pos": "0.0",
                    "liquidated_account_value": "0.0",
                },
                # nonUserCancel
                {
                    "type": "nonUserCancel",
                    "coin": "AVAX",
                    "oid": 90542681,
                },
            ]
        """
        return self._get("userEvents", UserEvents)

    @property
    def user_fills(self) -> UserFills:
        """``userFills`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Append-only

        Data structure:

        .. code:: python

            [
                {
                    "coin": "AVAX",
                    "px": "18.435",
                    "sz": "93.53",
                    "side": "B",
                    "time": 1681222254710,
                    "startPosition": "26.86",
                    "dir": "Open Long",
                    "closedPnl": "0.0",
                    "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                    "oid": 90542681,
                    "crossed": False,
                    "fee": "0.01",
                    "tid": 118906512037719,
                    "liquidation": {
                        "liquidatedUser": "0x0000000000000000000000000000000000000000",
                        "markPx": "18.435",
                        "method": "<method>",
                    },
                    "feeToken": "USDC",
                    "builderFee": "0.01",
                },
            ]
        """
        return self._get("userFills", UserFills)

    @property
    def user_fundings(self) -> UserFundings:
        """``userFundings`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Append-only

        Data structure:

        .. code:: python

            [
                {
                    "time": 1681222254710,
                    "coin": "ETH",
                    "usdc": "-3.625312",
                    "szi": "49.1477",
                    "fundingRate": "0.0000417",
                },
            ]
        """
        return self._get("userFundings", UserFundings)

    @property
    def user_non_funding_ledger_updates(self) -> UserNonFundingLedgerUpdates:
        """``userNonFundingLedgerUpdates`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Append-only

        Data structure:

        .. code:: python

            [
                {
                    "time": 1681222254710,
                    "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                    "delta": {
                        "type": "<type>",
                        "usdc": "0.0",
                    },
                },
            ]
        """
        return self._get("userNonFundingLedgerUpdates", UserNonFundingLedgerUpdates)

    @property
    def active_asset_ctx(self) -> ActiveAssetCtx:
        """``activeAssetCtx`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Mutable

        Keys: ``["coin"]``

        Data structure:

        .. code:: python

            [
                {
                    "coin": "BTC",
                    "dayNtlVlm": "1169046.29406",
                    "prevDayPx": "15.322",
                    "markPx": "14.3161",
                    "midPx": "14.314",
                    "funding": "0.0000125",
                    "openInterest": "688.11",
                    "oraclePx": "14.32",
                },
                {
                    "coin": "USDC",
                    "dayNtlVlm": "8906.0",
                    "prevDayPx": "0.20432",
                    "markPx": "0.14",
                    "midPx": "0.209265",
                    "circulatingSupply": "851681534.05516005",
                },
            ]
        """
        return self._get("activeAssetCtx", ActiveAssetCtx)

    @property
    def active_asset_data(self) -> ActiveAssetData:
        """``activeAssetData`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Mutable

        Keys: ``["user", "coin"]``

        Data structure:

        .. code:: python

            [
                {
                    "user": "0x0000000000000000000000000000000000000001",
                    "coin": "ETH",
                    "leverage": {
                        "type": "cross",
                        "value": 20,
                    },
                    "maxTradeSzs": ["0.0", "0.0"],
                    "availableToTrade": ["0.0", "0.0"],
                },
            ]
        """
        return self._get("activeAssetData", ActiveAssetData)

    @property
    def user_twap_slice_fills(self) -> UserTwapSliceFills:
        """``userTwapSliceFills`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Append-only

        Data structure:

        .. code:: python

            [
                {
                    "coin": "AVAX",
                    "px": "18.435",
                    "sz": "93.53",
                    "side": "B",
                    "time": 1681222254710,
                    "startPosition": "26.86",
                    "dir": "Open Long",
                    "closedPnl": "0.0",
                    "hash": "0xa166e3fa63c25663024b03f2e0da011a00307e4017465df020210d3d432e7cb8",
                    "oid": 90542681,
                    "crossed": False,
                    "fee": "0.01",
                    "tid": 118906512037719,
                    "liquidation": {
                        "liquidatedUser": "0x0000000000000000000000000000000000000000",
                        "markPx": "18.435",
                        "method": "<method>",
                    },
                    "feeToken": "USDC",
                    "builderFee": "0.01",
                    "twapId": 3156,
                },
            ]
        """
        return self._get("userTwapSliceFills", UserTwapSliceFills)

    @property
    def user_twap_history(self) -> UserTwapHistory:
        """``userTwapHistory`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Append-only

        Data structure:

        .. code:: python

            [
                {
                    "state": {},
                    "status": {
                        "status": "<status>",
                        "description": "<description>",
                    },
                    "time": 1681222254710,
                },
            ]
        """
        return self._get("userTwapHistory", UserTwapHistory)

    @property
    def bbo(self) -> Bbo:
        """``bbo`` data stream.

        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions

        Data type: Mutable

        Keys: ``["coin"]``

        Data structure:

        .. code:: python

            [
                {
                    "coin": "TEST",
                    "time": 1708622398623,
                    "bbo": [
                        {"px": "19900", "sz": "1", "n": 1},
                        {"px": "20100", "sz": "1", "n": 1},
                    ],
                },
            ]
        """
        return self._get("bbo", Bbo)


class AllMids(DataStore):
    _KEYS = ["coin"]

    def _onmessage(self, msg: Item) -> None:
        data_to_update: list[Item] = []

        if (
            isinstance(msg["data"], dict)
            and "mids" in msg["data"]
            and isinstance(msg["data"]["mids"], dict)
        ):
            for coin, px in msg["data"]["mids"].items():
                data_to_update.append({"coin": coin, "px": px})

        self._update(data_to_update)


class Notification(DataStore):
    def _onmessage(self, msg: Item) -> None:
        self._insert([msg["data"]])


class WebData2(DataStore):
    _KEYS = ["user"]

    def _onmessage(self, msg: Item) -> None:
        self._update([msg["data"]])


class Candle(DataStore):
    _KEYS = ["t", "T", "s", "i"]
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        self._insert([msg["data"]])


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
        self,
        query: Item | None = None,
        limit: int | None = None,
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


class OrderUpdates(DataStore):
    _KEYS = ["coin", "oid"]

    def _onmessage(self, msg: Item) -> None:
        data_to_update: list[Item] = []
        data_to_delete: list[Item] = []

        if isinstance(msg["data"], list):
            for item in msg["data"]:
                if (
                    isinstance(item, dict)
                    and "order" in item
                    and "status" in item
                    and isinstance(item["order"], dict)
                ):
                    order = item.pop("order")
                    flattened_order = {**order, **item}

                    if item["status"] == "open":
                        data_to_update.append(flattened_order)
                    else:
                        data_to_delete.append(flattened_order)

        self._update(data_to_update)
        self._delete(data_to_delete)


class UserEvents(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        data_to_insert: list[Item] = []

        if isinstance(msg["data"], dict):
            for key, value in msg["data"].items():
                if isinstance(value, list):
                    for item in value:
                        flattened_event = {"type": key, **item}
                        data_to_insert.append(flattened_event)
                elif isinstance(value, dict):
                    flattened_event = {"type": key, **value}
                    data_to_insert.append(flattened_event)

        self._insert(data_to_insert)


class UserFills(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        if (
            isinstance(msg["data"], dict)
            and "fills" in msg["data"]
            and isinstance(msg["data"]["fills"], list)
        ):
            self._insert(msg["data"]["fills"])


class UserFundings(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        if (
            isinstance(msg["data"], dict)
            and "fundings" in msg["data"]
            and isinstance(msg["data"]["fundings"], list)
        ):
            self._insert(msg["data"]["fundings"])


class UserNonFundingLedgerUpdates(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        if (
            isinstance(msg["data"], dict)
            and "nonFundingLedgerUpdates" in msg["data"]
            and isinstance(msg["data"]["nonFundingLedgerUpdates"], list)
        ):
            self._insert(msg["data"]["nonFundingLedgerUpdates"])


class ActiveAssetCtx(DataStore):
    _KEYS = ["coin"]

    def _onmessage(self, msg: Item) -> None:
        if (
            isinstance(msg["data"], dict)
            and "ctx" in msg["data"]
            and isinstance(msg["data"]["ctx"], dict)
        ):
            flattened_ctx = {"coin": msg["data"]["coin"], **msg["data"]["ctx"]}
            self._update([flattened_ctx])


class ActiveAssetData(DataStore):
    _KEYS = ["user", "coin"]

    def _onmessage(self, msg: Item) -> None:
        self._update([msg["data"]])


class UserTwapSliceFills(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        if (
            isinstance(msg["data"], dict)
            and "twapSliceFills" in msg["data"]
            and isinstance(msg["data"]["twapSliceFills"], list)
        ):
            self._insert(msg["data"]["twapSliceFills"])


class UserTwapHistory(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        if (
            isinstance(msg["data"], dict)
            and "history" in msg["data"]
            and isinstance(msg["data"]["history"], list)
        ):
            self._insert(msg["data"]["history"])


class Bbo(DataStore):
    _KEYS = ["coin"]

    def _onmessage(self, msg: Item) -> None:
        self._update([msg["data"]])
