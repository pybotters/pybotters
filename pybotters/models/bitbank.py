from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from collections.abc import Awaitable

    import aiohttp

    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class bitbankDataStore(DataStoreCollection):
    """bitbank の DataStoreCollection クラス"""

    def _init(self) -> None:
        self._create("transactions", datastore_class=Transactions)
        self._create("depth", datastore_class=Depth)
        self._create("ticker", datastore_class=Ticker)

    def _onmessage(self, msg: str, ws: ClientWebSocketResponse | None = None) -> None:
        if msg.startswith("42"):
            data_json = json.loads(msg[2:])
            room_name = data_json[1]["room_name"]
            data = data_json[1]["params"]["data"]
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


class bitbankPrivateDataStore(DataStoreCollection):
    """DataStoreCollection for bitbank Private Stream API.

    .. seealso::

        The bitbank Private Stream API is provided via PubNub. It is not a WebSocket
        API.

        The :meth:`~.DataStoreCollection.onmessage` handler can be used with the
        built-in PubNub helper functions :mod:`pybotters.helpers.bitbank` or the
        first-party `PubNub SDK <https://www.pubnub.com/docs/sdks/python>`_.
    """

    def _init(self) -> None:
        self._create("asset", datastore_class=Asset)
        self._create("spot_order", datastore_class=SpotOrder)
        self._create("spot_trade", datastore_class=SpotTrade)
        self._create("dealer_order", datastore_class=DealerOrder)
        self._create("withdrawal", datastore_class=Withdrawal)
        self._create("deposit", datastore_class=Deposit)
        self._create("margin_position", datastore_class=MarginPosition)
        self._create("margin_payable", datastore_class=MarginPayable)
        self._create("margin_notice", datastore_class=MarginNotice)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data.

        Supported endpoints:

        - GET /user/assets (:attr:`.bitbankPrivateDataStore.asset`)
        - GET /user/spot/active_orders (:attr:`.bitbankPrivateDataStore.spot_order`)
        - GET /user/margin/positions (:attr:`.bitbankPrivateDataStore.margin_position`)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            root = await resp.json()

            if not isinstance(root, dict) or root.get("success") != 1:
                logger.warning(root)
                continue

            if resp.url.path == "/v1/user/assets":
                self.asset._onresponse(root["data"])
            elif resp.url.path == "/v1/user/spot/active_orders":
                self.spot_order._onresponse(root["data"])
            elif resp.url.path == "/v1/user/margin/positions":
                self.margin_position._onresponse(root["data"])

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse | None = None) -> None:
        method = msg.get("method")

        if method == "asset_update":
            self.asset._onmessage(msg["params"])
        elif method in {"spot_order_new", "spot_order"}:
            self.spot_order._onmessage(msg["params"])
        elif method == "spot_order_invalidation":
            self.spot_order._oninvalidation(msg["params"])
        elif method == "spot_trade":
            self.spot_trade._onmessage(msg["params"])
        elif method == "dealer_order_new":
            self.dealer_order._onmessage(msg["params"])
        elif method == "withdrawal":
            self.withdrawal._onmessage(msg["params"])
        elif method == "deposit":
            self.deposit._onmessage(msg["params"])
        elif method == "margin_position_update":
            self.margin_position._onmessage(msg["params"])
        elif method == "margin_payable_update":
            self.margin_payable._onmessage(msg["params"])
        elif method == "margin_notice_update":
            self.margin_notice._onmessage(msg["params"])

    @property
    def asset(self) -> Asset:
        """``asset_update`` method.

        Keys: ``["asset"]``
        """
        return self._get("asset", Asset)

    @property
    def spot_order(self) -> SpotOrder:
        """``spot_order_new``, ``spot_order``, ``spot_order_invalidation`` method.

        FIXME: ``spot_order_invalidation`` behavior on the bitbank side is not well
        understood.

        Keys: ``["order_id"]``

        Only active orders are stored. Completed and canceled orders are removed from
        the store.
        """
        return self._get("spot_order", SpotOrder)

    @property
    def spot_trade(self) -> SpotTrade:
        """``spot_trade`` method.

        Keys: ``["trade_id"]``
        """
        return self._get("spot_trade", SpotTrade)

    @property
    def dealer_order(self) -> DealerOrder:
        """``dealer_order_new`` method.

        Keys: ``["order_id"]``
        """
        return self._get("dealer_order", DealerOrder)

    @property
    def withdrawal(self) -> Withdrawal:
        """``withdrawal`` method.

        Keys: ``["uuid"]``
        """
        return self._get("withdrawal", Withdrawal)

    @property
    def deposit(self) -> Deposit:
        """``deposit`` method.

        Keys: ``["uuid"]``
        """
        return self._get("deposit", Deposit)

    @property
    def margin_position(self) -> MarginPosition:
        """``margin_position_update`` method.

        Keys: ``["pair", "position_side"]``
        """
        return self._get("margin_position", MarginPosition)

    @property
    def margin_payable(self) -> MarginPayable:
        """``margin_payable_update`` method.

        No keys. This store always updates only one item.
        """
        return self._get("margin_payable", MarginPayable)

    @property
    def margin_notice(self) -> MarginNotice:
        """``margin_notice_update`` method.

        No keys.
        """
        return self._get("margin_notice", MarginNotice)


class _BasicUpdateMixin(ABC):
    @abstractmethod
    def _update(self, data: list[Item]) -> None: ...

    def _onmessage(self, params: list[Item]) -> None:
        self._update(params)


class Asset(DataStore, _BasicUpdateMixin):
    _KEYS = ["asset"]

    def _onresponse(self, data: Item) -> None:
        assets = data.get("assets", [])
        self._clear()
        self._update(assets)


class SpotOrder(DataStore):
    _KEYS = ["order_id"]

    def _onresponse(self, data: Item) -> None:
        orders = data.get("orders", [])
        self._clear()
        self._update(orders)

    def _onmessage(self, params: list[Item]) -> None:
        data_to_delete: list[Item] = []
        data_to_update: list[Item] = []
        for item in params:
            status = item["status"]
            if status in {
                "INACTIVE",
                "FULLY_FILLED",
                "CANCELED_UNFILLED",
                "CANCELED_PARTIALLY_FILLED",
            }:
                data_to_delete.append(item)
            else:
                data_to_update.append(item)

        self._delete(data_to_delete)
        self._update(data_to_update)

    def _oninvalidation(self, params: Item) -> None:
        data_to_delete: list[Item] = []
        for order_id in params["order_id"]:
            data_to_delete.append({"order_id": order_id})


class SpotTrade(DataStore, _BasicUpdateMixin):
    _KEYS = ["trade_id"]


class DealerOrder(DataStore, _BasicUpdateMixin):
    _KEYS = ["order_id"]


class Withdrawal(DataStore, _BasicUpdateMixin):
    _KEYS = ["uuid"]


class Deposit(DataStore, _BasicUpdateMixin):
    _KEYS = ["uuid"]


class MarginPosition(DataStore, _BasicUpdateMixin):
    _KEYS = ["pair", "position_side"]

    def _onresponse(self, data: Item) -> None:
        orders = data.get("positions", [])
        self._clear()
        self._update(orders)


class MarginPayable(DataStore):
    def _onmessage(self, params: list[Item]) -> None:
        # This store always updates only one item.
        for item in params:
            for orig_item in self:
                orig_item.clear()
                orig_item.update(item)
                self._put("update", source=orig_item, item=orig_item)
                self._set()


class MarginNotice(DataStore):
    def _onmessage(self, params: list[Item]) -> None:
        self._insert(params)
