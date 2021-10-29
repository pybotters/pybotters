import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum, auto
from typing import Any, Awaitable, Dict, List, Optional, cast

import aiohttp
from pybotters.store import DataStore, DataStoreManager
from pybotters.typedefs import Item

from ..ws import ClientWebSocketResponse

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

logger = logging.getLogger(__name__)


def parse_datetime(x: Any) -> datetime:
    if isinstance(x, str):
        return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        raise ValueError(f'x only support str, but {type(x)} passed.')


class ApiType(Enum):
    """
    API 区分
    """

    Public = auto()
    Private = auto()


class Channel(Enum):
    """
    WebSocket API チャンネル
    """

    # Public
    TICKER = auto()
    ORDER_BOOKS = auto()
    TRADES = auto()
    # Private
    EXECUTION_EVENTS = auto()
    ORDER_EVENTS = auto()
    POSITION_EVENTS = auto()
    POSITION_SUMMARY_EVENTS = auto()

    @staticmethod
    def from_str(name: str) -> "Channel":
        if not hasattr(Channel, "_table"):
            Channel._table = {
                "ticker": Channel.TICKER,
                "orderbooks": Channel.ORDER_BOOKS,
                "trades": Channel.TRADES,
                "executionEvents": Channel.EXECUTION_EVENTS,
                "orderEvents": Channel.ORDER_EVENTS,
                "positionEvents": Channel.POSITION_EVENTS,
                "positionSummaryEvents": Channel.POSITION_SUMMARY_EVENTS,
            }
        return Channel._table[name]


class MessageType(Enum):
    """
    メッセージタイプ
    """

    NONE = auto()
    ER = auto()
    NOR = auto()
    ROR = auto()
    COR = auto()
    OPR = auto()
    UPR = auto()
    ULR = auto()
    CPR = auto()
    INIT = auto()
    UPDATE = auto()
    PERIODIC = auto()


class Symbol(Enum):
    """
    取り扱い銘柄
    """

    BTC = auto()
    ETH = auto()
    BCH = auto()
    LTC = auto()
    XRP = auto()
    BTC_JPY = auto()
    ETH_JPY = auto()
    BCH_JPY = auto()
    LTC_JPY = auto()
    XRP_JPY = auto()


class OrderSide(Enum):
    """
    売買区分
    """

    BUY = auto()
    SELL = auto()


class ExecutionType(Enum):
    """
    注文タイプ
    """

    MARKET = auto()
    LIMIT = auto()
    STOP = auto()


class TimeInForce(Enum):
    """
    執行数量条件
    """

    FAK = auto()
    FAS = auto()
    FOK = auto()
    SOK = auto()


class SettleType(Enum):
    """
    決済区分
    """

    OPEN = auto()
    CLOSE = auto()
    LOSS_CUT = auto()


class OrderType(Enum):
    """
    取引区分
    """

    NORMAL = auto()
    LOSSCUT = auto()


class OrderStatus(Enum):
    """
    注文ステータス
    """

    WAITING = auto()
    ORDERED = auto()
    MODIFYING = auto()
    CANCELLING = auto()
    CANCELED = auto()
    EXECUTED = auto()
    EXPIRED = auto()


class CancelType(Enum):
    """
    取消区分
    """

    NONE = auto()
    USER = auto()
    POSITION_LOSSCUT = auto()
    INSUFFICIENT_BALANCE = auto()
    INSUFFICIENT_MARGIN = auto()
    ACCOUNT_LOSSCUT = auto()
    MARGIN_CALL = auto()
    MARGIN_CALL_LOSSCUT = auto()
    EXPIRED_FAK = auto()
    EXPIRED_FOK = auto()
    EXPIRED_SOK = auto()
    CLOSED_ORDER = auto()
    SOK_TAKER = auto()
    PRICE_LIMIT = auto()


class Ticker(TypedDict):
    ask: Decimal
    bid: Decimal
    high: Decimal
    last: Decimal
    low: Decimal
    symbol: Symbol
    timestamp: datetime
    volume: Decimal


class OrderLevel(TypedDict):
    symbol: Symbol
    side: OrderSide
    price: Decimal
    size: Decimal


class OrderBook(TypedDict):
    asks: List[OrderLevel]
    bids: List[OrderLevel]
    symbol: Symbol
    timestamp: datetime


class Trade(TypedDict):
    price: Decimal
    side: OrderSide
    size: Decimal
    timestamp: datetime
    symbol: Symbol


class Execution(TypedDict):
    execution_id: int
    order_id: int
    symbol: Symbol
    side: OrderSide
    settle_type: SettleType
    size: Decimal
    price: Decimal
    timestamp: datetime
    loss_gain: Decimal
    fee: Decimal
    # properties that only appears websocket message
    position_id: Optional[int]
    execution_type: Optional[ExecutionType]
    order_price: Optional[Decimal]
    order_size: Optional[Decimal]
    order_executed_size: Optional[Decimal]
    order_timestamp: Optional[datetime]
    time_in_force: Optional[str]


class Order(TypedDict):
    order_id: int
    symbol: Symbol
    settle_type: SettleType
    execution_type: ExecutionType
    side: OrderSide
    order_status: OrderStatus
    order_timestamp: datetime
    price: Decimal
    size: Decimal
    executed_size: Decimal
    losscut_price: Decimal
    time_in_force: TimeInForce
    # properties that only appears websocket message
    cancel_type: Optional[CancelType]


class Position(TypedDict):
    position_id: int
    symbol: Symbol
    side: OrderSide
    size: Decimal
    orderd_size: Decimal
    price: Decimal
    loss_gain: Decimal
    leverage: Decimal
    losscut_price: Decimal
    timestamp: datetime


class PositionSummary(TypedDict):
    symbol: Symbol
    side: OrderSide
    average_position_rate: Decimal
    position_loss_gain: Decimal
    sum_order_quantity: Decimal
    sum_position_quantity: Decimal
    timestamp: datetime


class TickerStore(DataStore):
    def _onmessage(self, mes: Ticker) -> None:
        self._update([cast(Item, mes)])


class OrderBookStore(DataStore):
    _KEYS = ["symbol", "side", "price"]

    def sorted(self, query: Optional[Item] = None) -> Dict[OrderSide, List[OrderLevel]]:
        if query is None:
            query = {}
        result: Dict[OrderSide, List[OrderLevel]] = {
            OrderSide.BUY: [],
            OrderSide.SELL: [],
        }
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item["side"]].append(cast(OrderLevel, item))
        result[OrderSide.SELL].sort(key=lambda x: x["price"])
        result[OrderSide.BUY].sort(key=lambda x: x["price"], reverse=True)
        return result

    def _onmessage(self, mes: OrderBook) -> None:
        data = mes["asks"] + mes["bids"]
        result = self.find({"symbol": mes["symbol"]})
        self._delete(result)
        self._insert(cast(List[Item], data))


class TradeStore(DataStore):
    def _onmessage(self, mes: Trade) -> None:
        self._insert([cast(Item, mes)])


class OrderStore(DataStore):
    _KEYS = ["order_id"]

    def _onresponse(self, data: List[Order]) -> None:
        self._insert(cast(List[Item], data))

    def _onmessage(self, mes: Order) -> None:
        if mes["order_status"] in (OrderStatus.WAITING, OrderStatus.ORDERED):
            self._update([cast(Item, mes)])
        else:
            self._delete([cast(Item, mes)])

    def _onexecution(self, mes: Execution) -> None:
        current = cast(Order, self.get({"order_id": mes["order_id"]}))
        if (
            mes["order_executed_size"]
            and current
            and current["executed_size"] < mes["order_executed_size"]
        ):
            current["executed_size"] = mes["order_executed_size"]
            remain = current["size"] - current["executed_size"]
            if remain == 0:
                self._delete([cast(Item, current)])
            else:
                self._update([cast(Item, current)])


class ExecutionStore(DataStore):
    _KEYS = ["execution_id"]

    def sorted(self, query: Optional[Item] = None) -> List[Execution]:
        if query is None:
            query = {}
        result = []
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result.append(item)
        result.sort(key=lambda x: x["execution_id"], reverse=True)
        return result

    def _onresponse(self, data: List[Execution]) -> None:
        self._insert(cast(List[Item], data))

    def _onmessage(self, mes: Execution) -> None:
        self._insert([cast(Item, mes)])


class PositionStore(DataStore):
    _KEYS = ["position_id"]

    def _onresponse(self, data: List[Position]) -> None:
        self._update(cast(List[Item], data))

    def _onmessage(self, mes: Position, type: MessageType) -> None:
        if type == MessageType.OPR:
            self._insert([cast(Item, mes)])
        elif type == MessageType.CPR:
            self._delete([cast(Item, mes)])
        else:
            self._update([cast(Item, mes)])


class PositionSummaryStore(DataStore):
    _KEYS = ["symbol", "side"]

    def _onresponse(self, data: List[PositionSummary]) -> None:
        self._update(cast(List[Item], data))

    def _onmessage(self, mes: PositionSummary) -> None:
        self._update([cast(Item, mes)])


class MessageHelper:
    @staticmethod
    def to_tickers(data: List[Item]) -> List["Ticker"]:
        return [MessageHelper.to_ticker(x) for x in data]

    @staticmethod
    def to_ticker(data: Item) -> "Ticker":
        return Ticker(
            ask=Decimal(data["ask"]),
            bid=Decimal(data["bid"]),
            high=Decimal(data["high"]),
            last=Decimal(data["last"]),
            low=Decimal(data["low"]),
            symbol=Symbol[data["symbol"]],
            timestamp=parse_datetime(data.get("timestamp")),
            volume=Decimal(data["volume"]),
        )

    @staticmethod
    def to_orderbook(data: Item) -> "OrderBook":
        return OrderBook(
            asks=[
                OrderLevel(
                    symbol=Symbol[data["symbol"]],
                    side=OrderSide.SELL,
                    price=Decimal(ol["price"]),
                    size=Decimal(ol["size"]),
                )
                for ol in data["asks"]
            ],
            bids=[
                OrderLevel(
                    symbol=Symbol[data["symbol"]],
                    side=OrderSide.BUY,
                    price=Decimal(ol["price"]),
                    size=Decimal(ol["size"]),
                )
                for ol in data["bids"]
            ],
            symbol=Symbol[data["symbol"]],
            timestamp=parse_datetime(data.get("timestamp")),
        )

    @staticmethod
    def to_trades(data: List[Item]) -> List["Trade"]:
        return [MessageHelper.to_trade(x) for x in data]

    @staticmethod
    def to_trade(data: Item) -> "Trade":
        return Trade(
            price=Decimal(data["price"]),
            side=OrderSide[data["side"]],
            size=Decimal(data["size"]),
            timestamp=parse_datetime(data.get("timestamp")),
            symbol=Symbol[data["symbol"]],
        )

    @staticmethod
    def to_executions(data: List[Item]) -> List["Execution"]:
        return [MessageHelper.to_execution(x) for x in data]

    @staticmethod
    def to_execution(data: Item) -> "Execution":
        return Execution(
            order_id=data["orderId"],
            execution_id=data["executionId"],
            symbol=Symbol[data["symbol"]],
            settle_type=SettleType[data["settleType"]],
            side=OrderSide[data["side"]],
            price=Decimal(data.get("executionPrice", data.get("price"))),
            size=Decimal(data.get("executionSize", data.get("size"))),
            timestamp=parse_datetime(
                data.get("executionTimestamp", data.get("timestamp"))
            ),
            loss_gain=Decimal(data["lossGain"]),
            fee=Decimal(data["fee"]),
            # properties that only appears websocket message
            position_id=data["positionId"] if "positionId" in data else None,
            execution_type=ExecutionType[data["executionType"]]
            if "executionType" in data
            else None,
            order_price=Decimal(data["orderPrice"]) if "orderPrice" in data else None,
            order_size=Decimal(data["orderSize"]) if ("orderSize" in data) else None,
            order_executed_size=Decimal(data["orderExecutedSize"])
            if "orderExecutedSize" in data
            else None,
            order_timestamp=parse_datetime(data["orderTimestamp"])
            if "orderTimestamp" in data
            else None,
            time_in_force=data.get("timeInForce", None),
        )

    @staticmethod
    def to_orders(data: List[Item]) -> List["Order"]:
        return [MessageHelper.to_order(x) for x in data]

    @staticmethod
    def to_order(data: Item) -> "Order":
        status = OrderStatus[data.get("status", data.get("orderStatus"))]
        timestamp = parse_datetime(data.get("orderTimestamp", data.get("timestamp")))
        return Order(
            order_id=data["orderId"],
            symbol=Symbol[data["symbol"]],
            settle_type=SettleType[data["settleType"]],
            execution_type=ExecutionType[data["executionType"]],
            side=OrderSide[data["side"]],
            order_status=status,
            cancel_type=CancelType[data.get("cancelType", CancelType.NONE.name)],
            order_timestamp=timestamp,
            price=Decimal(data.get("price", data.get("orderPrice"))),
            size=Decimal(data.get("size", data.get("orderSize"))),
            executed_size=Decimal(
                data.get("executedSize", data.get("orderExecutedSize"))
            ),
            losscut_price=Decimal(data["losscutPrice"]),
            time_in_force=data["timeInForce"],
        )

    @staticmethod
    def to_positions(data: List[Item]) -> List["Position"]:
        return [MessageHelper.to_position(x) for x in data]

    @staticmethod
    def to_position(data: Item) -> "Position":
        return Position(
            position_id=data["positionId"],
            symbol=Symbol[data["symbol"]],
            side=OrderSide[data["side"]],
            size=Decimal(data["size"]),
            orderd_size=Decimal(data["orderdSize"]),
            price=Decimal(data["price"]),
            loss_gain=Decimal(data["lossGain"]),
            leverage=Decimal(data["leverage"]),
            losscut_price=Decimal(data["losscutPrice"]),
            timestamp=parse_datetime(data.get("timestamp")),
        )

    @staticmethod
    def to_position_summaries(data: List[Item]) -> List["PositionSummary"]:
        return [MessageHelper.to_position_summary(x) for x in data]

    @staticmethod
    def to_position_summary(data: Item) -> "PositionSummary":
        return PositionSummary(
            symbol=Symbol[data["symbol"]],
            side=OrderSide[data["side"]],
            average_position_rate=Decimal(data["averagePositionRate"]),
            position_loss_gain=Decimal(data["positionLossGain"]),
            sum_order_quantity=Decimal(data["sumOrderQuantity"]),
            sum_position_quantity=Decimal(data["sumPositionQuantity"]),
            timestamp=parse_datetime(data.get("timestamp"))
            if data.get("timestamp")
            else datetime.now(timezone.utc),
        )


class GMOCoinDataStore(DataStoreManager):
    def _init(self) -> None:
        self.create("ticker", datastore_class=TickerStore)
        self.create("orderbooks", datastore_class=OrderBookStore)
        self.create("trades", datastore_class=TradeStore)
        self.create("orders", datastore_class=OrderStore)
        self.create("positions", datastore_class=PositionStore)
        self.create("executions", datastore_class=ExecutionStore)
        self.create("position_summary", datastore_class=PositionSummaryStore)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if (
                resp.url.path == "/private/v1/latestExecutions"
                and "list" in data["data"]
            ):
                self.executions._onresponse(
                    MessageHelper.to_executions(data["data"]["list"])
                )
            if resp.url.path == "/private/v1/activeOrders" and "list" in data["data"]:
                self.orders._onresponse(MessageHelper.to_orders(data["data"]["list"]))
            if resp.url.path == "/private/v1/openPositions" and "list" in data["data"]:
                self.positions._onresponse(
                    MessageHelper.to_positions(data["data"]["list"])
                )
            if (
                resp.url.path == "/private/v1/positionSummary"
                and "list" in data["data"]
            ):
                self.position_summary._onresponse(
                    MessageHelper.to_position_summaries(data["data"]["list"])
                )

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if "channel" in msg:
            msg_type = MessageType[msg.get("msgType", MessageType.NONE.name)]
            channel: Channel = Channel.from_str(msg["channel"])
            # Public
            if channel == Channel.TICKER:
                self.ticker._onmessage(MessageHelper.to_ticker(msg))
            elif channel == Channel.ORDER_BOOKS:
                self.orderbooks._onmessage(MessageHelper.to_orderbook(msg))
            elif channel == Channel.TRADES:
                self.trades._onmessage(MessageHelper.to_trade(msg))
            # Private
            elif channel == Channel.EXECUTION_EVENTS:
                self.orders._onexecution(MessageHelper.to_execution(msg))
                self.executions._onmessage(MessageHelper.to_execution(msg))
            elif channel == Channel.ORDER_EVENTS:
                self.orders._onmessage(MessageHelper.to_order(msg))
            elif channel == Channel.POSITION_EVENTS:
                self.positions._onmessage(MessageHelper.to_position(msg), msg_type)
            elif channel == Channel.POSITION_SUMMARY_EVENTS:
                self.position_summary._onmessage(MessageHelper.to_position_summary(msg))

    @property
    def ticker(self) -> TickerStore:
        return self.get("ticker", TickerStore)

    @property
    def orderbooks(self) -> OrderBookStore:
        return self.get("orderbooks", OrderBookStore)

    @property
    def trades(self) -> TradeStore:
        return self.get("trades", TradeStore)

    @property
    def orders(self) -> OrderStore:
        return self.get("orders", OrderStore)

    @property
    def positions(self) -> PositionStore:
        return self.get("positions", PositionStore)

    @property
    def executions(self) -> ExecutionStore:
        return self.get("executions", ExecutionStore)

    @property
    def position_summary(self) -> PositionSummaryStore:
        return self.get("position_summary", PositionSummaryStore)
