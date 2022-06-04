from __future__ import annotations

import asyncio
import logging
import operator
from decimal import Decimal
from typing import Awaitable

import aiohttp

from ..store import DataStore, DataStoreManager
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class bitFlyerDataStore(DataStoreManager):
    def _init(self) -> None:
        self.create("board", datastore_class=Board)
        self.create("ticker", datastore_class=Ticker)
        self.create("executions", datastore_class=Executions)
        self.create("childorderevents", datastore_class=ChildOrderEvents)
        self.create("childorders", datastore_class=ChildOrders)
        self.create("parentorderevents", datastore_class=ParentOrderEvents)
        self.create("parentorders", datastore_class=ParentOrders)
        self.create("positions", datastore_class=Positions)
        self._snapshots = set()

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if resp.url.path == "/v1/me/getchildorders":
                self.childorders._onresponse(data)
            elif resp.url.path == "/v1/me/getparentorders":
                self.parentorders._onresponse(data)
            elif resp.url.path == "/v1/me/getpositions":
                self.positions._onresponse(data)

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if "error" in msg:
            logger.warning(msg)
        if "params" in msg:
            channel: str = msg["params"]["channel"]
            message = msg["params"]["message"]
            if channel.startswith("lightning_board_"):
                if channel.startswith("lightning_board_snapshot_"):
                    asyncio.create_task(
                        ws.send_json(
                            {
                                "method": "unsubscribe",
                                "params": {"channel": channel},
                            }
                        )
                    )
                    product_code = channel.replace("lightning_board_snapshot_", "")
                    self.board._delete(self.board.find({"product_code": product_code}))
                    self._snapshots.add(product_code)
                else:
                    product_code = channel.replace("lightning_board_", "")
                if product_code in self._snapshots:
                    self.board._onmessage(product_code, message)
            elif channel.startswith("lightning_ticker_"):
                self.ticker._onmessage(message)
            elif channel.startswith("lightning_executions_"):
                product_code = channel.replace("lightning_executions_", "")
                self.executions._onmessage(product_code, message)
            elif channel == "child_order_events":
                self.childorderevents._onmessage(message)
                self.childorders._onmessage(message)
                self.positions._onmessage(message)
            elif channel == "parent_order_events":
                self.parentorderevents._onmessage(message)
                self.parentorders._onmessage(message)

    @property
    def board(self) -> "Board":
        return self.get("board", Board)

    @property
    def ticker(self) -> "Ticker":
        return self.get("ticker", Ticker)

    @property
    def executions(self) -> "Executions":
        return self.get("executions", Executions)

    @property
    def childorderevents(self) -> "ChildOrderEvents":
        return self.get("childorderevents", ChildOrderEvents)

    @property
    def childorders(self) -> "ChildOrders":
        return self.get("childorders", ChildOrders)

    @property
    def parentorderevents(self) -> "ParentOrderEvents":
        return self.get("parentorderevents", ParentOrderEvents)

    @property
    def parentorders(self) -> "ParentOrders":
        return self.get("parentorders", ParentOrders)

    @property
    def positions(self) -> "Positions":
        return self.get("positions", Positions)


class Board(DataStore):
    _KEYS = ["product_code", "side", "price"]

    def _init(self) -> None:
        self.mid_price: dict[str, float] = {}

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

    def _onmessage(self, product_code: str, message: Item) -> None:
        self.mid_price[product_code] = message["mid_price"]
        for key, side in (("bids", "BUY"), ("asks", "SELL")):
            for item in message[key]:
                if item["size"]:
                    self._insert([{"product_code": product_code, "side": side, **item}])
                else:
                    self._delete([{"product_code": product_code, "side": side, **item}])
        board = self.sorted({"product_code": product_code})
        targets = []
        for side, ope in (("BUY", operator.le), ("SELL", operator.gt)):
            for item in board[side]:
                if ope(item["price"], message["mid_price"]):
                    break
                else:
                    targets.append(item)
        self._delete(targets)


class Ticker(DataStore):
    _KEYS = ["product_code"]

    def _onmessage(self, message: Item) -> None:
        self._update([message])


class Executions(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, product_code: str, message: list[Item]) -> None:
        for item in message:
            self._insert([{"product_code": product_code, **item}])


class ChildOrderEvents(DataStore):
    def _onmessage(self, message: list[Item]) -> None:
        self._insert(message)


class ParentOrderEvents(DataStore):
    def _onmessage(self, message: list[Item]) -> None:
        self._insert(message)


class ChildOrders(DataStore):
    _KEYS = ["child_order_acceptance_id"]

    def _onresponse(self, data: list[Item]) -> None:
        if data:
            self._delete(self.find({"product_code": data[0]["product_code"]}))
            for item in data:
                if item["child_order_state"] == "ACTIVE":
                    self._insert([item])

    def _onmessage(self, message: list[Item]) -> None:
        for item in message:
            if item["event_type"] == "ORDER":
                self._insert([item])
            elif item["event_type"] in ("CANCEL", "EXPIRE"):
                self._delete([item])
            elif item["event_type"] == "EXECUTION":
                if item["outstanding_size"]:
                    childorder = self.get(item)
                    if childorder:
                        if isinstance(childorder["size"], int) and isinstance(
                            item["size"], int
                        ):
                            childorder["size"] -= item["size"]
                        else:
                            childorder["size"] = float(
                                Decimal(str(childorder["size"]))
                                - Decimal(str(item["size"]))
                            )
                else:
                    self._delete([item])


class ParentOrders(DataStore):
    _KEYS = ["parent_order_acceptance_id"]

    def _onresponse(self, data: list[Item]) -> None:
        if data:
            self._delete(self.find({"product_code": data[0]["product_code"]}))
            for item in data:
                if item["parent_order_state"] == "ACTIVE":
                    self._insert([item])

    def _onmessage(self, message: list[Item]) -> None:
        for item in message:
            if item["event_type"] == "ORDER":
                self._insert([item])
            elif item["event_type"] in ("CANCEL", "EXPIRE"):
                self._delete([item])
            elif item["event_type"] == "COMPLETE":
                parentorder = self.get(item)
                if parentorder:
                    if parentorder["parent_order_type"] in ("IFD", "IFDOCO"):
                        if item["parameter_index"] >= 2:
                            self._delete([item])
                    else:
                        self._delete([item])


class Positions(DataStore):
    _COMMON_KEYS = [
        "product_code",
        "side",
        "price",
        "size",
        "commission",
        "sfd",
    ]

    def _common_keys(self, item: Item) -> Item:
        return {key: item[key] for key in self._COMMON_KEYS}

    def _onresponse(self, data: list[Item]) -> None:
        if data:
            positions = self._find_with_uuid({"product_code": data[0]["product_code"]})
            if positions:
                self._remove(list(positions.keys()))
            for item in data:
                self._insert([self._common_keys(item)])

    def _onmessage(self, message: list[Item]) -> None:
        for item in message:
            if item["event_type"] == "EXECUTION":
                positions = self._find_with_uuid({"product_code": item["product_code"]})
                if positions:
                    if positions[next(iter(positions))]["side"] == item["side"]:
                        self._insert([self._common_keys(item)])
                    else:
                        for uid, pos in positions.items():
                            if pos["size"] > item["size"]:
                                if isinstance(pos["size"], int) and isinstance(
                                    item["size"], int
                                ):
                                    pos["size"] -= item["size"]
                                    item["size"] = 0
                                else:
                                    pos["size"] = float(
                                        Decimal(str(pos["size"]))
                                        - Decimal(str(item["size"]))
                                    )
                                    item["size"] = 0.0
                                break
                            else:
                                if isinstance(pos["size"], int) and isinstance(
                                    item["size"], int
                                ):
                                    item["size"] -= pos["size"]
                                else:
                                    item["size"] = float(
                                        Decimal(str(item["size"]))
                                        - Decimal(str(pos["size"]))
                                    )
                                self._remove([uid])
                        if item["size"] > 0:
                            self._insert([self._common_keys(item)])
                else:
                    try:
                        self._insert([self._common_keys(item)])
                    except KeyError:
                        pass
