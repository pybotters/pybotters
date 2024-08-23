from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Awaitable, TypedDict, cast

from pybotters.store import DataStore, DataStoreCollection

from ...auth import Auth

if TYPE_CHECKING:
    import aiohttp

    from ...typedefs import Item
    from ...ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


def parse_datetime(x: Any) -> datetime:
    if isinstance(x, str):
        if len(x) > 20:
            return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f%z")
        else:
            return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z")
    else:
        raise ValueError(f"x only support str, but {type(x)} passed.")


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
            Channel._table = {  # type: ignore
                "ticker": Channel.TICKER,
                "orderbooks": Channel.ORDER_BOOKS,
                "trades": Channel.TRADES,
                "executionEvents": Channel.EXECUTION_EVENTS,
                "orderEvents": Channel.ORDER_EVENTS,
                "positionEvents": Channel.POSITION_EVENTS,
                "positionSummaryEvents": Channel.POSITION_SUMMARY_EVENTS,
            }
        return Channel._table[name]  # type: ignore


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
    XEM = auto()
    XLM = auto()
    BAT = auto()
    XTZ = auto()
    QTUM = auto()
    ENJ = auto()
    DOT = auto()
    ATOM = auto()
    MKR = auto()
    DAI = auto()
    XYM = auto()
    MONA = auto()
    FCR = auto()
    ADA = auto()
    LINK = auto()
    DOGE = auto()
    SOL = auto()
    ASTR = auto()
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
    asks: list[OrderLevel]
    bids: list[OrderLevel]
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
    position_id: int | None
    execution_type: ExecutionType | None
    order_price: Decimal | None
    order_size: Decimal | None
    order_executed_size: Decimal | None
    order_timestamp: datetime | None
    time_in_force: str | None


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
    cancel_type: CancelType | None


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
    _KEYS = ["symbol"]

    def _onmessage(self, mes: Ticker) -> None:
        self._update([cast("Item", mes)])


class OrderBookStore(DataStore):
    _KEYS = ["symbol", "side", "price"]

    def _init(self) -> None:
        self.timestamp: datetime | None = None

    def sorted(self, query: Item | None = None) -> dict[OrderSide, list[OrderLevel]]:
        if query is None:
            query = {}
        result: dict[OrderSide, list[OrderLevel]] = {
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
        self._insert(cast("list[Item]", data))
        self.timestamp = mes["timestamp"]


class TradeStore(DataStore):
    def _onmessage(self, mes: Trade) -> None:
        self._insert([cast("Item", mes)])


class OrderStore(DataStore):
    _KEYS = ["order_id"]

    def _onresponse(self, data: list[Order]) -> None:
        self._insert(cast("list[Item]", data))

    def _onmessage(self, mes: Order) -> None:
        if mes["order_status"] in (OrderStatus.WAITING, OrderStatus.ORDERED):
            self._update([cast("Item", mes)])
        else:
            self._delete([cast("Item", mes)])

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
                self._delete([cast("Item", current)])
            else:
                self._update([cast("Item", current)])


class ExecutionStore(DataStore):
    _KEYS = ["execution_id"]

    def sorted(self, query: Item | None = None) -> list[Execution]:
        if query is None:
            query = {}
        result: list[Execution] = []
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result.append(item)  # type: ignore
        result.sort(key=lambda x: x["execution_id"], reverse=True)
        return result

    def _onresponse(self, data: list[Execution]) -> None:
        self._insert(cast("list[Item]", data))

    def _onmessage(self, mes: Execution) -> None:
        self._insert([cast("Item", mes)])


class PositionStore(DataStore):
    _KEYS = ["position_id"]

    def _onresponse(self, data: list[Position]) -> None:
        self._update(cast("list[Item]", data))

    def _onmessage(self, mes: Position, type: MessageType) -> None:
        if type == MessageType.OPR:
            self._insert([cast("Item", mes)])
        elif type == MessageType.CPR:
            self._delete([cast("Item", mes)])
        else:
            self._update([cast("Item", mes)])


class PositionSummaryStore(DataStore):
    _KEYS = ["symbol", "side"]

    def _onresponse(self, data: list[PositionSummary]) -> None:
        self._update(cast("list[Item]", data))

    def _onmessage(self, mes: PositionSummary) -> None:
        self._update([cast("Item", mes)])


class MessageHelper:
    @staticmethod
    def to_tickers(data: list[Item]) -> list["Ticker"]:
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
    def to_trades(data: list[Item]) -> list["Trade"]:
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
    def to_executions(data: list[Item]) -> list["Execution"]:
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
    def to_orders(data: list[Item]) -> list["Order"]:
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
    def to_positions(data: list[Item]) -> list["Position"]:
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
    def to_position_summaries(data: list[Item]) -> list["PositionSummary"]:
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


class GMOCoinDataStore(DataStoreCollection):
    """
    GMOコインのデータストアマネージャー
    """

    def _init(self) -> None:
        self._create("ticker", datastore_class=TickerStore)
        self._create("orderbooks", datastore_class=OrderBookStore)
        self._create("trades", datastore_class=TradeStore)
        self._create("orders", datastore_class=OrderStore)
        self._create("positions", datastore_class=PositionStore)
        self._create("executions", datastore_class=ExecutionStore)
        self._create("position_summary", datastore_class=PositionSummaryStore)
        self.token: str | None = None

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """
        対応エンドポイント

        - GET /private/v1/latestExecutions (DataStore: executions)
        - GET /private/v1/activeOrders (DataStore: orders)
        - GET /private/v1/openPositions (DataStore: positions)
        - GET /private/v1/positionSummary (DataStore: position_summary)
        - POST /private/v1/ws-auth (Property: token)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()

            if data.get("status") != 0:
                raise ValueError(
                    "Response error at DataStore initialization\n"
                    f"URL: {resp.url}\n"
                    f"Data: {data}"
                )

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
            if resp.url.path == "/private/v1/ws-auth":
                self.token = data["data"]
                asyncio.create_task(self._token(resp.__dict__["_raw_session"]))

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if "error" in msg:
            logger.warning(msg)
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

    async def _token(self, session: aiohttp.ClientSession):
        while not session.closed:
            await session.put(
                "https://api.coin.z.com/private/v1/ws-auth",
                data={"token": self.token},
                auth=Auth,
            )
            await asyncio.sleep(1800.0)  # 30 minutes

    @property
    def ticker(self) -> TickerStore:
        return self._get("ticker", TickerStore)

    @property
    def orderbooks(self) -> OrderBookStore:
        return self._get("orderbooks", OrderBookStore)

    @property
    def trades(self) -> TradeStore:
        return self._get("trades", TradeStore)

    @property
    def orders(self) -> OrderStore:
        """
        アクティブオーダーのみ(約定・キャンセル済みは削除される)
        """
        return self._get("orders", OrderStore)

    @property
    def positions(self) -> PositionStore:
        return self._get("positions", PositionStore)

    @property
    def executions(self) -> ExecutionStore:
        return self._get("executions", ExecutionStore)

    @property
    def position_summary(self) -> PositionSummaryStore:
        return self._get("position_summary", PositionSummaryStore)
