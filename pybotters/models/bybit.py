from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Optional, Union

import aiohttp

from ..store import DataStore, DataStoreManager
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BybitInverseDataStore(DataStoreManager):
    """
    Bybit Inverse契約のデータストアマネージャー
    """

    def _init(self) -> None:
        self.create("orderbook", datastore_class=OrderBookInverse)
        self.create("trade", datastore_class=TradeInverse)
        self.create("insurance", datastore_class=Insurance)
        self.create("instrument", datastore_class=InstrumentInverse)
        self.create("kline", datastore_class=KlineInverse)
        self.create("liquidation", datastore_class=LiquidationInverse)
        self.create("position", datastore_class=PositionInverse)
        self.create("execution", datastore_class=ExecutionInverse)
        self.create("order", datastore_class=OrderInverse)
        self.create("stoporder", datastore_class=StopOrderInverse)
        self.create("wallet", datastore_class=WalletInverse)
        self.timestamp_e6: Optional[int] = None

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """
        対応エンドポイント

        - GET /v2/private/order (DataStore: order)
        - GET /futures/private/order (DataStore: order)
        - GET /v2/private/stop-order (DataStore: stoporder)
        - GET /futures/private/stop-order (DataStore: stoporder)
        - GET /v2/private/position/list (DataStore: position)
        - GET /futures/private/position/list (DataStore: position)
        - GET /v2/private/wallet/balance (DataStore: wallet)
        - GET /v2/public/kline/list (DataStore: kline)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if data["ret_code"] != 0:
                raise ValueError(
                    "Response error at DataStore initialization\n"
                    f"URL: {resp.url}\n"
                    f"Data: {data}"
                )
            if resp.url.path in (
                "/v2/private/order",
                "/futures/private/order",
            ):
                self.order._onresponse(data["result"])
            elif resp.url.path in (
                "/v2/private/stop-order",
                "/futures/private/stop-order",
            ):
                self.stoporder._onresponse(data["result"])
            elif resp.url.path in (
                "/v2/private/position/list",
                "/futures/private/position/list",
            ):
                self.position._onresponse(data["result"])
            elif resp.url.path == "/v2/public/kline/list":
                self.kline._onresponse(data["result"])
            elif resp.url.path == "/v2/private/wallet/balance":
                self.wallet._onresponse(data["result"])

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if "success" in msg:
            if not msg["success"]:
                logger.warning(msg)
        if "topic" in msg:
            topic: str = msg["topic"]
            data = msg["data"]
            if any(
                [
                    topic.startswith("orderBookL2_25"),
                    topic.startswith("orderBook_200"),
                ]
            ):
                self.orderbook._onmessage(topic, msg["type"], data)
            elif topic.startswith("trade"):
                self.trade._onmessage(data)
            elif topic.startswith("insurance"):
                self.insurance._onmessage(data)
            elif topic.startswith("instrument_info"):
                self.instrument._onmessage(topic, msg["type"], data)
            if topic.startswith("klineV2"):
                self.kline._onmessage(topic, data)
            elif topic.startswith("liquidation"):
                self.liquidation._onmessage(data)
            elif topic == "position":
                self.position._onmessage(data)
            elif topic == "execution":
                self.execution._onmessage(data)
            elif topic == "order":
                self.order._onmessage(data)
            elif topic == "stop_order":
                self.stoporder._onmessage(data)
            elif topic == "wallet":
                self.wallet._onmessage(data)
        if "timestamp_e6" in msg:
            self.timestamp_e6 = int(msg["timestamp_e6"])

    @property
    def orderbook(self) -> "OrderBookInverse":
        return self.get("orderbook", OrderBookInverse)

    @property
    def trade(self) -> "TradeInverse":
        return self.get("trade", TradeInverse)

    @property
    def insurance(self) -> "Insurance":
        return self.get("insurance", Insurance)

    @property
    def instrument(self) -> "InstrumentInverse":
        return self.get("instrument", InstrumentInverse)

    @property
    def kline(self) -> "KlineInverse":
        return self.get("kline", KlineInverse)

    @property
    def liquidation(self) -> "LiquidationInverse":
        return self.get("liquidation", LiquidationInverse)

    @property
    def position(self) -> "PositionInverse":
        """
        インバース契約(無期限/先物)用のポジション
        """
        return self.get("position", PositionInverse)

    @property
    def execution(self) -> "ExecutionInverse":
        return self.get("execution", ExecutionInverse)

    @property
    def order(self) -> "OrderInverse":
        """
        アクティブオーダーのみ(約定・キャンセル済みは削除される)
        """
        return self.get("order", OrderInverse)

    @property
    def stoporder(self) -> "StopOrderInverse":
        """
        アクティブオーダーのみ(トリガー済みは削除される)
        """
        return self.get("stoporder", StopOrderInverse)

    @property
    def wallet(self) -> "WalletInverse":
        return self.get("wallet", WalletInverse)


class BybitUSDTDataStore(DataStoreManager):
    """
    Bybit USDT契約のデータストアマネージャー
    """

    def _init(self) -> None:
        self.create("orderbook", datastore_class=OrderBookUSDT)
        self.create("trade", datastore_class=TradeUSDT)
        self.create("insurance", datastore_class=Insurance)
        self.create("instrument", datastore_class=InstrumentUSDT)
        self.create("kline", datastore_class=KlineUSDT)
        self.create("liquidation", datastore_class=LiquidationUSDT)
        self.create("position", datastore_class=PositionUSDT)
        self.create("execution", datastore_class=ExecutionUSDT)
        self.create("order", datastore_class=OrderUSDT)
        self.create("stoporder", datastore_class=StopOrderUSDT)
        self.create("wallet", datastore_class=WalletUSDT)
        self.timestamp_e6: Optional[int] = None

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """
        対応エンドポイント

        - GET /private/linear/order/search (DataStore: order)
        - GET /private/linear/stop-order/search (DataStore: stoporder)
        - GET /private/linear/position/list (DataStore: position)
        - GET /private/linear/position/list (DataStore: position)
        - GET /public/linear/kline (DataStore: kline)
        - GET /v2/private/wallet/balance (DataStore: wallet)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if data["ret_code"] != 0:
                raise ValueError(
                    "Response error at DataStore initialization\n"
                    f"URL: {resp.url}\n"
                    f"Data: {data}"
                )
            if resp.url.path == "/private/linear/order/search":
                self.order._onresponse(data["result"])
            elif resp.url.path == "/private/linear/stop-order/search":
                self.stoporder._onresponse(data["result"])
            elif resp.url.path == "/private/linear/position/list":
                self.position._onresponse(data["result"])
            elif resp.url.path == "/public/linear/kline":
                self.kline._onresponse(data["result"])
            elif resp.url.path == "/v2/private/wallet/balance":
                self.wallet._onresponse(data["result"])

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if "success" in msg:
            if not msg["success"]:
                logger.warning(msg)
        if "topic" in msg:
            topic: str = msg["topic"]
            data = msg["data"]
            if any(
                [
                    topic.startswith("orderBookL2_25"),
                    topic.startswith("orderBook_200"),
                ]
            ):
                self.orderbook._onmessage(topic, msg["type"], data)
            elif topic.startswith("trade"):
                self.trade._onmessage(data)
            elif topic.startswith("instrument_info"):
                self.instrument._onmessage(topic, msg["type"], data)
            if topic.startswith("candle"):
                self.kline._onmessage(topic, data)
            elif topic.startswith("liquidation"):
                self.liquidation._onmessage(data)
            elif topic == "position":
                self.position._onmessage(data)
            elif topic == "execution":
                self.execution._onmessage(data)
            elif topic == "order":
                self.order._onmessage(data)
            elif topic == "stop_order":
                self.stoporder._onmessage(data)
            elif topic == "wallet":
                self.wallet._onmessage(data)
        if "timestamp_e6" in msg:
            self.timestamp_e6 = int(msg["timestamp_e6"])

    @property
    def orderbook(self) -> "OrderBookUSDT":
        return self.get("orderbook", OrderBookUSDT)

    @property
    def trade(self) -> "TradeUSDT":
        return self.get("trade", TradeUSDT)

    @property
    def instrument(self) -> "InstrumentUSDT":
        return self.get("instrument", InstrumentUSDT)

    @property
    def kline(self) -> "KlineUSDT":
        return self.get("kline", KlineUSDT)

    @property
    def liquidation(self) -> "LiquidationUSDT":
        return self.get("liquidation", LiquidationUSDT)

    @property
    def position(self) -> "PositionUSDT":
        """
        USDT契約用のポジション
        """
        return self.get("position", PositionUSDT)

    @property
    def execution(self) -> "ExecutionUSDT":
        return self.get("execution", ExecutionUSDT)

    @property
    def order(self) -> "OrderUSDT":
        """
        アクティブオーダーのみ(約定・キャンセル済みは削除される)
        """
        return self.get("order", OrderUSDT)

    @property
    def stoporder(self) -> "StopOrderUSDT":
        """
        アクティブオーダーのみ(トリガー済みは削除される)
        """
        return self.get("stoporder", StopOrderUSDT)

    @property
    def wallet(self) -> "WalletUSDT":
        return self.get("wallet", WalletUSDT)


class OrderBookInverse(DataStore):
    _KEYS = ["symbol", "id", "side"]

    def sorted(self, query: Optional[Item] = None) -> dict[str, list[Item]]:
        if query is None:
            query = {}
        result = {"Sell": [], "Buy": []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item["side"]].append(item)
        result["Sell"].sort(key=lambda x: x["id"])
        result["Buy"].sort(key=lambda x: x["id"], reverse=True)
        return result

    def _onmessage(self, topic: str, type_: str, data: Union[list[Item], Item]) -> None:
        if type_ == "snapshot":
            symbol = topic.split(".")[-1]
            # ex: "orderBookL2_25.BTCUSD", "orderBook_200.100ms.BTCUSD"
            result = self.find({"symbol": symbol})
            self._delete(result)
            self._insert(data)
        elif type_ == "delta":
            self._delete(data["delete"])
            self._update(data["update"])
            self._insert(data["insert"])


class OrderBookUSDT(OrderBookInverse):
    def _onmessage(self, topic: str, type_: str, data: Union[list[Item], Item]) -> None:
        if type_ == "snapshot":
            symbol = topic.split(".")[-1]
            # ex: "orderBookL2_25.BTCUSDT", "orderBook_200.100ms.BTCUSDT"
            result = self.find({"symbol": symbol})
            self._delete(result)
            self._insert(data["order_book"])
        elif type_ == "delta":
            self._delete(data["delete"])
            self._update(data["update"])
            self._insert(data["insert"])


class TradeInverse(DataStore):
    _KEYS = ["trade_id"]
    _MAXLEN = 99999

    def _onmessage(self, data: list[Item]) -> None:
        self._insert(data)


class TradeUSDT(TradeInverse):
    ...


class Insurance(DataStore):
    _KEYS = ["currency"]

    def _onmessage(self, data: list[Item]) -> None:
        self._update(data)


class InstrumentInverse(DataStore):
    _KEYS = ["symbol"]

    def _onmessage(self, topic: str, type_: str, data: Item) -> None:
        if type_ == "snapshot":
            symbol = topic.split(".")[-1]  # ex: "instrument_info.100ms.BTCUSD"
            result = self.find({"symbol": symbol})
            self._delete(result)
            self._insert([data])
        elif type_ == "delta":
            self._update(data["update"])


class InstrumentUSDT(InstrumentInverse):
    ...


class KlineInverse(DataStore):
    _KEYS = ["start", "symbol", "interval"]

    def _onmessage(self, topic: str, data: list[Item]) -> None:
        topic_split = topic.split(".")  # ex:"klineV2.1.BTCUSD"
        for item in data:
            item["symbol"] = topic_split[-1]
            item["interval"] = topic_split[-2]
        self._update(data)

    def _onresponse(self, data: list[Item]) -> None:
        for item in data:
            item["start"] = item.pop("open_time")
        self._update(data)


class KlineUSDT(KlineInverse):
    ...


class LiquidationInverse(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, item: Item) -> None:
        self._insert([item])


class LiquidationUSDT(LiquidationInverse):
    ...


class PositionInverse(DataStore):
    _KEYS = ["symbol", "position_idx"]

    def one(self, symbol: str) -> Optional[Item]:
        return self.get({"symbol": symbol, "position_idx": 0})

    def both(self, symbol: str) -> dict[str, Optional[Item]]:
        return {
            "Sell": self.get({"symbol": symbol, "position_idx": 2}),
            "Buy": self.get({"symbol": symbol, "position_idx": 1}),
        }

    def _onresponse(self, data: Union[Item, list[Item]]) -> None:
        if isinstance(data, dict):
            self._update([data])  # ex: {"symbol": "BTCUSD", ...}
        elif isinstance(data, list):
            for item in data:
                if "is_valid" in item:
                    if item["is_valid"]:
                        self._update([item["data"]])
                        # ex:
                        # [
                        #     {
                        #         "is_valid": True,
                        #         "data": {"symbol": "BTCUSDM21", ...}
                        #     },
                        #     ...
                        # ]
                else:
                    self._update([item])
                    # ex: [{"symbol": "BTCUSDT", ...}, ...]

    def _onmessage(self, data: list[Item]) -> None:
        self._update(data)


class PositionUSDT(PositionInverse):
    def _onmessage(self, data: list[Item]) -> None:
        for item in data:
            item["position_idx"] = int(item["position_idx"])
            self._update([item])


class ExecutionInverse(DataStore):
    _KEYS = ["exec_id"]

    def _onmessage(self, data: list[Item]) -> None:
        self._update(data)


class ExecutionUSDT(ExecutionInverse):
    ...


class OrderInverse(DataStore):
    _KEYS = ["order_id"]

    def _onresponse(self, data: list[Item]) -> None:
        if isinstance(data, list):
            self._update(data)
        elif isinstance(data, dict):
            self._update([data])

    def _onmessage(self, data: list[Item]) -> None:
        for item in data:
            if item["order_status"] in ("Created", "New", "PartiallyFilled"):
                self._update([item])
            else:
                self._delete([item])


class OrderUSDT(OrderInverse):
    ...


class StopOrderInverse(DataStore):
    _KEYS = ["order_id"]

    def _onresponse(self, data: list[Item]) -> None:
        if isinstance(data, list):
            self._update(data)
        elif isinstance(data, dict):
            self._update([data])

    def _onmessage(self, data: list[Item]) -> None:
        for item in data:
            if item["order_status"] in ("Active", "Untriggered"):
                self._update([item])
            else:
                self._delete([item])


class StopOrderUSDT(StopOrderInverse):
    _KEYS = ["stop_order_id"]


class WalletInverse(DataStore):
    _KEYS = ["coin"]

    def _onresponse(self, data: dict[str, Item]) -> None:
        data.pop("USDT", None)
        for coin in data:
            self._update(
                [
                    {
                        "coin": coin,
                        "available_balance": data[coin]["available_balance"],
                        "wallet_balance": data[coin]["wallet_balance"],
                    }
                ]
            )

    def _onmessage(self, data: list[Item]) -> None:
        self._update(data)


class WalletUSDT(WalletInverse):
    def _onresponse(self, data: dict[str, Item]) -> None:
        if "USDT" in data:
            self._update(
                [
                    {
                        "coin": "USDT",
                        "wallet_balance": data["USDT"]["wallet_balance"],
                        "available_balance": data["USDT"]["available_balance"],
                    }
                ]
            )

    def _onmessage(self, data: list[Item]) -> None:
        for item in data:
            self._update([{"coin": "USDT", **item}])
