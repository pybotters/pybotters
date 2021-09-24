import asyncio
import logging
from typing import Awaitable, Dict, List, Optional, Union

import aiohttp

from ..store import DataStore, DataStoreManager
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BybitInverseDataStore(DataStoreManager):
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
        self.timestamp_e6: Optional[int] = None

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
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
        return self.get("position", PositionInverse)

    @property
    def execution(self) -> "ExecutionInverse":
        return self.get("execution", ExecutionInverse)

    @property
    def order(self) -> "OrderInverse":
        return self.get("order", OrderInverse)

    @property
    def stoporder(self) -> "StopOrderInverse":
        return self.get("stoporder", StopOrderInverse)


class BybitUSDTDataStore(DataStoreManager):
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
        self.create("wallet", datastore_class=Wallet)
        self.timestamp_e6: Optional[int] = None

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
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
            elif resp.url.path == "/v2/public/kline/list":
                self.kline._onresponse(data["result"])

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
        return self.get("position", PositionUSDT)

    @property
    def execution(self) -> "ExecutionUSDT":
        return self.get("execution", ExecutionUSDT)

    @property
    def order(self) -> "OrderUSDT":
        return self.get("order", OrderUSDT)

    @property
    def stoporder(self) -> "StopOrderUSDT":
        return self.get("stoporder", StopOrderUSDT)

    @property
    def wallet(self) -> "Wallet":
        return self.get("wallet", Wallet)


class CastDataStore(DataStore):
    _CAST_TYPES = {}

    def _cast(self, data: List[Item]) -> None:
        for item in data:
            for x in self._CAST_TYPES:
                for k in self._CAST_TYPES[x]:
                    try:
                        item[k] = x(item[k])
                    except KeyError:
                        pass
                    except TypeError:
                        pass

    def _insert(self, data: List[Item]) -> None:
        self._cast(data)
        super()._insert(data)

    def _update(self, data: List[Item]) -> None:
        self._cast(data)
        super()._update(data)

    def _delete(self, data: List[Item]) -> None:
        self._cast(data)
        super()._delete(data)


class OrderBookInverse(CastDataStore):
    _KEYS = ["symbol", "id", "side"]
    _CAST_TYPES = {
        float: [
            "price",
        ],
    }

    def sorted(self, query: Item = {}) -> Dict[str, List[Item]]:
        result = {"Sell": [], "Buy": []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item["side"]].append(item)
        result["Sell"].sort(key=lambda x: x["id"])
        result["Buy"].sort(key=lambda x: x["id"], reverse=True)
        return result

    def _onmessage(self, topic: str, type_: str, data: Union[List[Item], Item]) -> None:
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
    _CAST_TYPES = {
        float: [
            "price",
        ],
        int: [
            "id",
        ],
    }

    def _onmessage(self, topic: str, type_: str, data: Union[List[Item], Item]) -> None:
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


class TradeInverse(CastDataStore):
    _KEYS = ['trade_id']
    _MAXLEN = 99999

    def _onmessage(self, data: List[Item]) -> None:
        self._insert(data)


class TradeUSDT(TradeInverse):
    _CAST_TYPES = {
        float: [
            "price",
        ],
        int: [
            "trade_time_ms",
        ],
    }


class Insurance(CastDataStore):
    _KEYS = ["currency"]

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)


class InstrumentInverse(CastDataStore):
    _KEYS = ["symbol"]
    _CAST_TYPES = {
        float: [
            "last_price",
            "bid1_price",
            "ask1_price",
            "prev_price_24h",
            "high_price_24h",
            "low_price_24h",
            "prev_price_1h",
            "mark_price",
            "index_price",
        ],
    }

    def _onmessage(self, topic: str, type_: str, data: Item) -> None:
        if type_ == "snapshot":
            symbol = topic.split(".")[-1]  # ex: "instrument_info.100ms.BTCUSD"
            result = self.find({"symbol": symbol})
            self._delete(result)
            self._insert([data])
        elif type_ == "delta":
            self._update(data["update"])


class InstrumentUSDT(InstrumentInverse):
    _CAST_TYPES = {
        float: [
            "last_price",
            "prev_price_24h",
            "high_price_24h",
            "low_price_24h",
            "prev_price_1h",
            "mark_price",
            "index_price",
            "bid1_price",
            "ask1_price",
        ],
        int: [
            "last_price_e4",
            "prev_price_24h_e4",
            "price_24h_pcnt_e6",
            "high_price_24h_e4",
            "low_price_24h_e4",
            "prev_price_1h_e4",
            "price_1h_pcnt_e6",
            "mark_price_e4",
            "index_price_e4",
            "open_interest_e8",
            "total_turnover_e8",
            "turnover_24h_e8",
            "total_volume_e8",
            "volume_24h_e8",
            "funding_rate_e6",
            "predicted_funding_rate_e6",
            "cross_seq",
            "count_down_hour",
            "bid1_price_e4",
            "ask1_price_e4",
        ],
    }


class KlineInverse(CastDataStore):
    _KEYS = ["start", "symbol", "interval"]

    def _onmessage(self, topic: str, data: List[Item]) -> None:
        topic_split = topic.split(".")  # ex:"klineV2.1.BTCUSD"
        for item in data:
            item["symbol"] = topic_split[-1]
            item["interval"] = topic_split[-2]
        self._update(data)

    def _onresponse(self, data: List[Item]) -> None:
        for item in data:
            item["start"] = item.pop("open_time")
        self._update(data)


class KlineUSDT(KlineInverse):
    _CAST_TYPES = {
        float: [
            "volume",
            "turnover",
        ],
    }


class LiquidationInverse(CastDataStore):
    _CAST_TYPES = {
        float: [
            "price",
        ],
        int: [
            "qty",
        ],
    }
    _MAXLEN = 99999

    def _onmessage(self, item: Item) -> None:
        self._insert([item])


class LiquidationUSDT(LiquidationInverse):
    _CAST_TYPES = {
        float: [
            "price",
            "qty",
        ],
        int: [
            "qty",
        ],
    }


class PositionInverse(CastDataStore):
    _KEYS = ["symbol", "position_idx"]
    _CAST_TYPES = {
        float: [
            "position_value",
            "entry_price",
            "liq_price",
            "bust_price",
            "leverage",
            "order_margin",
            "position_margin",
            "available_balance",
            "take_profit",
            "stop_loss",
            "realised_pnl",
            "trailing_stop",
            "trailing_active",
            "wallet_balance",
            "occ_closing_fee",
            "occ_funding_fee",
            "cum_realised_pnl",
        ],
    }

    def one(self, symbol: str) -> Optional[Item]:
        return self.get({"symbol": symbol, "position_idx": 0})

    def both(self, symbol: str) -> Dict[str, Optional[Item]]:
        return {
            "Sell": self.get({"symbol": symbol, "position_idx": 2}),
            "Buy": self.get({"symbol": symbol, "position_idx": 1}),
        }

    def _onresponse(self, data: Union[Item, List[Item]]) -> None:
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

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)


class PositionUSDT(PositionInverse):
    _KEYS = ["symbol", "side"]
    _CAST_TYPES = {
        int: [
            "user_id",
            "auto_add_margin",
            "position_id",
            "position_seq",
            "adl_rank_indicator",
            "risk_id",
        ],
    }

    def both(self, symbol: str) -> Dict[str, Optional[Item]]:
        return {
            "Sell": self.get({"symbol": symbol, "side": "Sell"}),
            "Buy": self.get({"symbol": symbol, "side": "Buy"}),
        }


class ExecutionInverse(CastDataStore):
    _KEYS = ["exec_id"]
    _CAST_TYPES = {
        float: [
            "price",
            "exec_fee",
        ],
    }

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)


class ExecutionUSDT(ExecutionInverse):
    _CAST_TYPES = {}


class OrderInverse(CastDataStore):
    _KEYS = ["order_id"]
    _CAST_TYPES = {
        float: [
            "price",
            "cum_exec_value",
            "cum_exec_fee",
            "take_profit",
            "stop_loss",
            "trailing_stop",
            "last_exec_price",
        ],
    }

    def _onresponse(self, data: List[Item]) -> None:
        if isinstance(data, list):
            self._update(data)
        elif isinstance(data, dict):
            self._update([data])

    def _onmessage(self, data: List[Item]) -> None:
        for item in data:
            if item["order_status"] in ("Created", "New", "PartiallyFilled"):
                self._update([item])
            else:
                self._delete([item])


class OrderUSDT(OrderInverse):
    _CAST_TYPES = {}


class StopOrderInverse(CastDataStore):
    _KEYS = ["order_id"]
    _CAST_TYPES = {
        float: [
            "price",
            "trigger_price",
        ],
    }

    def _onresponse(self, data: List[Item]) -> None:
        if isinstance(data, list):
            self._update(data)
        elif isinstance(data, dict):
            self._update([data])

    def _onmessage(self, data: List[Item]) -> None:
        for item in data:
            if item["order_status"] in ("Active", "Untriggered"):
                self._update([item])
            else:
                self._delete([item])


class StopOrderUSDT(StopOrderInverse):
    _KEYS = ["stop_order_id"]
    _CAST_TYPES = {
        int: [
            "user_id",
        ],
    }


class Wallet(CastDataStore):
    def _onmessage(self, data: List[Item]) -> None:
        self._clear()
        self._update(data)
