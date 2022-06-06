from decimal import Decimal
from typing import Any, TYPE_CHECKING

import aiohttp
from pyee import EventEmitter

from ...store import DataStore, DataStoreManager


if TYPE_CHECKING:
    from ..client_ws import ClientWebSocketResponse


class GMOCoinWebSocketHandler:
    def __init__(self) -> None:
        self.response = EventEmitter()
        self.channel = EventEmitter()

    def onmessage(self, data: Any, ws: "ClientWebSocketResponse") -> None:
        if "channel" in data:
            self.channel.emit(data["channel"], data, ws)
        else:
            if "error" in data:
                self.response.emit("error", data, ws)
            else:
                self.response.emit("message", data, ws)


class GMOCoinDataStore(DataStoreManager):
    def _init(self) -> None:
        self.create("execution", datastore_class=GMOCoinExecution)
        self.create("order", datastore_class=GMOCoinOrder)
        self.create("position", datastore_class=GMOCoinPosition)
        self.create("positionSummary", datastore_class=GMOCoinPositionSummary)

        self.wshander = GMOCoinWebSocketHandler()
        self.wshander.channel.add_listener("executionEvents", self.execution._onmessage)
        self.wshander.channel.add_listener("executionEvents", self.order._onexecution)
        self.wshander.channel.add_listener("orderEvents", self.order._onmessage)
        self.wshander.channel.add_listener("positionEvents", self.position._onmessage)
        self.wshander.channel.add_listener(
            "positionSummaryEvents", self.position_summary._onmessage
        )

    @property
    def execution(self) -> "GMOCoinExecution":
        return self["execution"]

    @property
    def order(self) -> "GMOCoinOrder":
        return self["order"]

    @property
    def position(self) -> "GMOCoinPosition":
        return self["position"]

    @property
    def position_summary(self) -> "GMOCoinPositionSummary":
        return self["positionSummary"]

    def _onmessage(self, data: Any, ws: "ClientWebSocketResponse") -> None:
        self.wshander.onmessage(data, ws)


class GMOCoinExecution(DataStore):
    _KEYS = ["executionId"]

    def _onmessage(self, data: Any, ws: "ClientWebSocketResponse") -> None:
        self._insert([data])


class GMOCoinOrder(DataStore):
    _KEYS = ["orderId"]

    def _onmessage(self, data: Any, ws: "ClientWebSocketResponse") -> None:
        if data["msgType"] == "NOR":
            self._insert([data])
        elif data["msgType"] == "ROR":
            self._update([data])
        elif data["msgType"] in ("COR", "ER"):
            self._delete([data])

    def _onexecution(self, data: Any, ws: "ClientWebSocketResponse") -> None:
        if data["orderExecutedSize"] == data["orderSize"]:
            self._delete([data])
        else:
            self._update(
                [
                    {
                        "orderId": data["orderId"],
                        "orderExecutedSize": data["orderExecutedSize"],
                    }
                ]
            )


class GMOCoinPosition(DataStore):
    _KEYS = ["positionId"]

    def _onmessage(self, data: Any, ws: "ClientWebSocketResponse") -> None:
        if data["msgType"] == "OPR":
            self._insert([data])
        elif data["msgType"] in ("UPR", "ULR"):
            self._update([data])
        elif data["msgType"] == ("CPR"):
            self._delete([data])


class GMOCoinPositionSummary(DataStore):
    _KEYS = ["symbol", "side"]

    def _onmessage(self, data: Any, ws: "ClientWebSocketResponse") -> None:
        if data["msgType"] == "INIT":
            self._insert([data])
        elif data["msgType"] in ("UPDATE", "PERIODIC"):
            self._update([data])
