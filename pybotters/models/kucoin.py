from __future__ import annotations

import asyncio
import copy
import logging
import time
import uuid
from typing import TYPE_CHECKING, Any, Awaitable

import aiohttp

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


def _symbol_from_msg(msg):
    return msg["topic"].split(":")[-1]


class KuCoinDataStore(DataStoreCollection):
    """KuCoin の DataStoreCollection クラス"""

    def _init(self) -> None:
        self._create("ticker", datastore_class=Ticker)
        self._create("kline", datastore_class=Kline)
        self._create("symbolsnapshot", datastore_class=SymbolSnapshot)
        self._create("orderbook5", datastore_class=TopKOrderBook)
        self._create("orderbook50", datastore_class=TopKOrderBook)
        self._create("execution", datastore_class=Execution)
        self._create("indexprice", datastore_class=IndexPrice)
        self._create("markprice", datastore_class=MarkPrice)
        self._create("orderevents", datastore_class=OrderEvents)
        self._create("orders", datastore_class=Orders)
        self._create("balance", datastore_class=Balance)
        self._create("marginfundingbook", datastore_class=MarginFundingBook)
        self._create("marginpositions", datastore_class=MarginPositions)
        self._create("marginpositionevents", datastore_class=MarginPositionEvents)
        self._create("marginorderevents", datastore_class=MarginOrderEvents)
        self._create("marginorders", datastore_class=MarginOrders)
        self._create("instrument", datastore_class=Instrument)
        self._create("announcements", datastore_class=Announcements)
        self._create("transactionstats", datastore_class=TransactionStats)
        self._create("balanceevents", datastore_class=BalanceEvents)
        self._create("positions", datastore_class=Positions)
        self._endpoint = None

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data.

        対応エンドポイント

        - GET /api/v1/market/candles (:attr:`.KuCoinDataStore.kline`)
        - GET /api/v1/positions (:attr:`.KuCoinDataStore.positions`)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if resp.url.path == "/api/v1/positions":
                self.positions._onresponse(data["data"])
            elif resp.url.path == "/api/v1/market/candles":
                self.kline._onresponse(
                    data["data"], resp.url.query["symbol"], resp.url.query["type"]
                )
            elif resp.url.path.endswith("/bullet-public") or resp.url.path.endswith(
                "/bullet-private"
            ):
                if resp.status != 200:
                    raise RuntimeError(f"Failed to get a websocket endpoint: {data}")
                self._endpoint = self._create_endpoint(data["data"])

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if "topic" in msg:
            topic = msg["topic"]
            if (
                topic.startswith("/market/ticker")
                or topic.startswith("/contractMarket/tickerV2")
                or topic.startswith("/contractMarket/ticker")
            ):
                self.ticker._onmessage(msg)

            elif topic.startswith("/market/candles"):
                self.kline._onmessage(msg)

            elif topic.startswith("/market/snapshot"):
                self.symbolsnapshot._onmessage(msg)

            elif topic.startswith("/spotMarket/level2Depth50") or topic.startswith(
                "/contractMarket/level2Depth50"
            ):
                self.orderbook50._onmessage(msg)

            elif topic.startswith("/spotMarket/level2Depth5") or topic.startswith(
                "/contractMarket/level2Depth5"
            ):
                self.orderbook5._onmessage(msg)

            elif topic.startswith("/market/match") or topic.startswith(
                "/contractMarket/execution"
            ):
                self.execution._onmessage(msg)

            elif topic.startswith("/indicator/index"):
                self.indexprice._onmessage(msg)

            elif topic.startswith("/indicator/markPrice"):
                self.markprice._onmessage(msg)

            elif topic.endswith("tradeOrders") or topic.endswith("advancedOrders"):
                self.orderevents._onmessage(copy.deepcopy(msg))
                self.orders._onmessage(copy.deepcopy(msg))

            elif topic.startswith("/contract/instrument"):
                self.instrument._onmessage(msg)

            elif topic.startswith("/contract/announcement"):
                self.announcements._onmessage(msg)

            elif topic.startswith("/contractMarket/snapshot"):
                self.transactionstats._onmessage(msg)

            elif topic.startswith("/account/balance"):
                self.balance._onmessage(msg)

            elif topic.startswith("/margin/fundingBook"):
                self.marginfundingbook._onmessage(msg)

            elif topic.startswith("/margin/position"):
                self.marginpositions._onmessage(copy.deepcopy(msg))
                self.marginpositionevents._onmessage(copy.deepcopy(msg))

            elif topic.startswith("/margin/loan"):
                self.marginorders._onmessage(copy.deepcopy(msg))
                self.marginorderevents._onmessage(copy.deepcopy(msg))

            elif topic.startswith("/contractAccount/wallet"):
                self.balanceevents._onmessage(msg)

            elif topic.startswith("/contract/position"):
                self.positions._onmessage(msg)

            elif topic.startswith("/spotMarket/level2"):
                raise NotImplementedError
            elif topic.startswith("/margin/fundingBook"):
                raise NotImplementedError

    @property
    def ticker(self) -> "Ticker":
        """/market/ticker, /contractMarket/tickerV2, /contractMarket/ticker topic.

        * https://www.kucoin.com/docs/websocket/spot-trading/public-channels/ticker
        * https://www.kucoin.com/docs/websocket/futures-trading/public-channels/get-ticker-v2
        * https://www.kucoin.com/docs/websocket/futures-trading/public-channels/get-ticker
        """
        return self._get("ticker", Ticker)

    @property
    def kline(self) -> "Kline":
        """/market/candles topic.

        * https://www.kucoin.com/docs/websocket/spot-trading/public-channels/klines
        """
        return self._get("kline", Kline)

    @property
    def symbolsnapshot(self) -> "SymbolSnapshot":
        """/market/snapshot topic.

        * https://www.kucoin.com/docs/websocket/spot-trading/public-channels/symbol-snapshot
        """
        return self._get("symbolsnapshot", SymbolSnapshot)

    @property
    def orderbook5(self) -> "TopKOrderBook":
        """/spotMarket/level2Depth50, /contractMarket/level2Depth5 topic.

        * https://www.kucoin.com/docs/websocket/spot-trading/public-channels/level2-5-best-ask-bid-orders
        * https://www.kucoin.com/docs/websocket/futures-trading/public-channels/level2-5-best-ask-bid-orders
        """
        return self._get("orderbook5", TopKOrderBook)

    @property
    def orderbook50(self) -> "TopKOrderBook":
        """/spotMarket/level2Depth50, /contractMarket/level2Depth50 topic.

        * https://www.kucoin.com/docs/websocket/spot-trading/public-channels/level2-50-best-ask-bid-orders
        * https://www.kucoin.com/docs/websocket/futures-trading/public-channels/level2-50-best-ask-bid-orders
        """
        return self._get("orderbook50", TopKOrderBook)

    @property
    def execution(self) -> "Execution":
        """/market/match, /contractMarket/execution topic.

        * https://www.kucoin.com/docs/websocket/spot-trading/public-channels/match-execution-data
        * https://www.kucoin.com/docs/websocket/futures-trading/public-channels/match-execution-data
        """
        return self._get("execution", Execution)

    @property
    def indexprice(self) -> "IndexPrice":
        """/indicator/index topic.

        * https://www.kucoin.com/docs/websocket/margin-trading/public-channels/index-price
        """
        return self._get("indexprice", IndexPrice)

    @property
    def markprice(self) -> "MarkPrice":
        """/indicator/markPrice topic.

        * https://www.kucoin.com/docs/websocket/margin-trading/public-channels/mark-price
        """
        return self._get("markprice", MarkPrice)

    @property
    def orderevents(self) -> "OrderEvents":
        """/spotMarket/tradeOrders, /spotMarket/advancedOrders, /contractMarket/tradeOrders, /contractMarket/advancedOrders topic.

        * https://www.kucoin.com/docs/websocket/spot-trading/private-channels/private-order-change
        * https://www.kucoin.com/docs/websocket/spot-trading/private-channels/stop-order-event
        * https://www.kucoin.com/docs/websocket/futures-trading/private-channels/trade-orders
        * https://www.kucoin.com/docs/websocket/futures-trading/private-channels/stop-order-lifecycle-event
        """
        return self._get("orderevents", OrderEvents)

    @property
    def orders(self) -> "Orders":
        """tradeOrders/advancedOrders topic.

        アクティブオーダーのみデータが格納されます。 キャンセル、約定済みなどは削除されます。

        * https://www.kucoin.com/docs/websocket/spot-trading/private-channels/private-order-change
        * https://www.kucoin.com/docs/websocket/spot-trading/private-channels/stop-order-event
        * https://www.kucoin.com/docs/websocket/futures-trading/private-channels/trade-orders
        * https://www.kucoin.com/docs/websocket/futures-trading/private-channels/stop-order-lifecycle-event
        """
        return self._get("orders", Orders)

    @property
    def balance(self) -> "Balance":
        """/account/balance topic.

        * https://www.kucoin.com/docs/websocket/spot-trading/private-channels/account-balance-change
        """
        return self._get("balance", Balance)

    @property
    def marginfundingbook(self) -> "MarginFundingBook":
        """/margin/fundingBook topic.

        * https://www.kucoin.com/docs/websocket/margin-trading/public-channels/margin-funding-order-book-change
        """
        return self._get("marginfundingbook", MarginFundingBook)

    @property
    def marginpositions(self) -> "MarginPositions":
        """/margin/position topic.

        * https://www.kucoin.com/docs/websocket/margin-trading/private-channels/cross-margin-position-event
        """
        return self._get("marginpositions", MarginPositions)

    @property
    def marginpositionevents(self) -> "MarginPositionEvents":
        """/margin/position topic.

        * https://www.kucoin.com/docs/websocket/margin-trading/private-channels/cross-margin-position-event
        """
        return self._get("marginpositionevents", MarginPositionEvents)

    @property
    def marginorderevents(self) -> "MarginOrderEvents":
        """/margin/loan topic.

        * https://www.kucoin.com/docs/websocket/margin-trading/private-channels/margin-trade-order-event
        """
        return self._get("marginorderevents", MarginOrderEvents)

    @property
    def marginorders(self) -> "MarginOrders":
        """/margin/loan topic.

        アクティブオーダーのみデータが格納されます。 キャンセル、約定済みなどは削除されます。

        * https://www.kucoin.com/docs/websocket/margin-trading/private-channels/margin-trade-order-event
        """
        return self._get("marginorders", MarginOrders)

    @property
    def instrument(self) -> "Instrument":
        """/contract/instrument topic.

        * https://www.kucoin.com/docs/websocket/futures-trading/public-channels/contract-market-data
        """
        return self._get("instrument", Instrument)

    @property
    def announcements(self) -> "Announcements":
        """/contract/announcement topic.

        * https://www.kucoin.com/docs/websocket/futures-trading/public-channels/funding-fee-settlement
        """
        return self._get("announcements", Announcements)

    @property
    def transactionstats(self) -> "TransactionStats":
        """/contractMarket/snapshot topic.

        * https://www.kucoin.com/docs/websocket/futures-trading/public-channels/transaction-statistics-timer-event
        """
        return self._get("transactionstats", TransactionStats)

    @property
    def balanceevents(self) -> "BalanceEvents":
        """/contractAccount/wallet topic.

        * https://www.kucoin.com/docs/websocket/futures-trading/private-channels/account-balance-events
        """
        return self._get("balanceevents", BalanceEvents)

    @property
    def positions(self) -> "Positions":
        """/contract/position topic.

        * https://www.kucoin.com/docs/websocket/futures-trading/private-channels/position-change-events
        """
        return self._get("positions", Positions)

    @property
    def endpoint(self):
        """Retrieved KuCoin WebSocket endpoint."""

        if self._endpoint is None:
            raise RuntimeError("A websocket endpoint has not been initialized.")
        return self._endpoint

    @classmethod
    def _create_endpoint(cls, data):
        token = data["token"]
        servers = data["instanceServers"]
        id = str(uuid.uuid4())
        endpoint, host = None, None

        try:
            from pybotters.ws import HeartbeatHosts

            for s in servers:
                host = aiohttp.typedefs.URL(s["endpoint"]).host
                # HeartbeatHostsに登録してあるエンドポイントを優先して使う
                if host in HeartbeatHosts.items:
                    endpoint = s["endpoint"]
                    break
        except ImportError as e:
            logger.warning(
                "KuCoinDataStore cannot use 'HeartbeatHosts' "
                f"({e.__class__.__name__}: {e})"
            )
        # HeartbeatHostsに登録してあるエンドポイントがなかった場合、一番最初のものを使う
        if endpoint is None:
            endpoint = servers[0]["endpoint"]

        return f"{endpoint}?token={token}&acceptUserMessage=true&connectId={id}"


class _InsertStore(DataStore):
    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert([msg["data"]])


class _UpdateStore(DataStore):
    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._update([msg["data"]])


class Ticker(DataStore):
    """
    # Spot
    - https://docs.kucoin.com/#all-symbols-ticker

    # Future
    - https://docs.kucoin.com/futures/#get-real-time-symbol-ticker-v2
    - https://docs.kucoin.com/futures/#get-real-time-symbol-ticker (deprecated)

    """

    _KEYS = ["symbol"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        if msg["topic"].endswith("all"):
            symbol = msg["subject"]
        else:
            symbol = _symbol_from_msg(msg)
        self._update([{"symbol": symbol, **msg["data"]}])


class SymbolSnapshot(DataStore):
    """
    # Spot
    - https://docs.kucoin.com/#symbol-snapshot
    - https://docs.kucoin.com/#market-snapshot
    """

    _KEYS = ["symbol"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._update([msg["data"]["data"]])


class Orderbook(DataStore):
    """
    # Spot
    - https://docs.kucoin.com/#level-2-market-data

    # Future
    - https://docs.kucoin.com/futures/#level-2-market-data
    """

    _KEYS = ["symbol"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        raise NotImplementedError


class TopKOrderBook(DataStore):
    """

    # Spot
    - https://docs.kucoin.com/#level2-5-best-ask-bid-orders
    - https://docs.kucoin.com/#level2-50-best-ask-bid-orders

    # Future
    - https://docs.kucoin.com/futures/message-channel-for-the-5-best-ask-bid-full-data-of-level-2
    - https://docs.kucoin.com/futures/message-channel-for-the-50-best-ask-bid-full-data-of-level-2
    """

    _KEYS = ["symbol", "side", "price"]

    def __init__(self, *args, **kwargs):
        super(TopKOrderBook, self).__init__(*args, **kwargs)

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

    def _onmessage(self, msg: dict[str, Any]) -> None:
        symbol = _symbol_from_msg(msg)

        self._find_and_delete({"symbol": symbol})
        data = []
        for side in ("asks", "bids"):
            for item in msg["data"][side]:
                data.append(
                    {
                        "symbol": symbol,
                        "side": side,
                        "price": item[0],
                        "size": item[1],
                        "timestamp": msg["data"]["timestamp"],
                    }
                )

        self._update(data)


class Kline(DataStore):
    """
    # Spot
    - https://docs.kucoin.com/#klines
    """

    _KEYS = ["symbol", "interval", "timestamp"]

    def __init__(self, *args, **kwargs):
        super(Kline, self).__init__(*args, **kwargs)
        # 未確定足保存用
        self._latests = {}

    def latest(self, symbol: str, interval: str):
        """未確定足取得用"""
        return self._latests.get((symbol, interval), None)

    def _onmessage(self, msg: dict[str, Any]) -> None:
        data = self._parse_msg(msg)

        key = tuple(data[k] for k in self._keys if k != "timestamp")
        latest_candle = self._latests.get(key, None)
        if latest_candle and latest_candle["timestamp"] != data["timestamp"]:
            # 足確定
            self._insert([latest_candle])
        self._latests[key] = data

    def _onresponse(self, data, symbol, interval) -> None:
        for d in data[::-1]:
            self._insert(
                [
                    {
                        "symbol": symbol,
                        "interval": interval,
                        "received_at": int(time.time()),
                        **self._to_ohlcva(d),
                    }
                ]
            )

    def _parse_msg(self, msg):
        symbol, interval = msg["topic"].split(":")[-1].split("_")
        data = msg["data"]
        ohlcva = self._to_ohlcva(data["candles"])

        return {
            "symbol": symbol,
            "interval": interval,
            "received_at": data["time"],
            **ohlcva,
        }

    def _to_ohlcva(self, candles):
        return {
            "timestamp": candles[0],
            "open": candles[1],
            "close": candles[2],
            "high": candles[3],
            "low": candles[4],
            "volume": candles[5],
            "amount": candles[6],
        }


class Execution(DataStore):
    """
    # Spot
    - https://docs.kucoin.com/#match-execution-data

    # Future
    - https://docs.kucoin.com/futures/#execution-data
    """

    _KEYS = ["tradeId"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert([msg["data"]])


class IndexPrice(_UpdateStore):
    """
    # Spot
    - https://docs.kucoin.com/#index-price
    """

    _KEYS = ["symbol"]


class MarkPrice(_UpdateStore):
    """
    # Spot
    - https://docs.kucoin.com/#mark-price
    """

    _KEYS = ["symbol"]


class OrderEvents(_InsertStore):
    """
    # Spot
    - https://docs.kucoin.com/#private-order-change-events

    # Future
    - https://docs.kucoin.com/futures/#trade-orders
    - https://docs.kucoin.com/futures/#stop-order-lifecycle-event
    """

    _KEYS = ["orderId"]


class Orders(DataStore):
    """
    # Spot
    - https://docs.kucoin.com/#private-order-change-events

    # Future
    - https://docs.kucoin.com/futures/#trade-orders
    - https://docs.kucoin.com/futures/#stop-order-lifecycle-event
    """

    _KEYS = ["orderId"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        d = msg["data"]
        tp = d["type"]
        item = self.get(d)
        if item is None:
            # new order
            if tp == "open":
                self._insert([d])
        else:
            if tp in ("match", "triggered"):
                # Market order
                pass
            elif tp in ("cancel", "canceled", "filled"):
                self._delete([item])
            elif tp == "update":
                self._update([item])
            else:
                raise RuntimeError(f"Unknown type: {tp} ({d})")


class Balance(_UpdateStore):
    """
    # Spot
    - https://docs.kucoin.com/#account-balance-notice
    """

    _KEYS = ["accountId"]


class MarginFundingBook(_UpdateStore):
    """
    # Spot
    - https://docs.kucoin.com/#order-book-change
    """


class MarginOrderEvents(DataStore):
    """
    # Spot
    - https://docs.kucoin.com/#margin-trade-order-enters-event
    - https://docs.kucoin.com/#margin-order-update-event
    - https://docs.kucoin.com/#margin-order-done-event
    """

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert([{"subject": msg["subject"], **msg}])


class MarginOrders(DataStore):
    """
    # Spot
    - https://docs.kucoin.com/#margin-trade-order-enters-event
    - https://docs.kucoin.com/#margin-order-update-event
    - https://docs.kucoin.com/#margin-order-done-event
    """

    _KEYS = ["orderId"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        if msg["subject"] == "order.open":
            self._insert([msg["data"]])
        elif msg["subject"] == "order.update":
            self._update([msg["data"]])
        elif msg["subject"] == "order.done":
            self._delete([msg["data"]])


class MarginPositions(DataStore):
    """
    # Spot
    - https://docs.kucoin.com/#debt-ratio-change
    """

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._clear()
        self._insert([msg["data"]])


class MarginPositionEvents(_InsertStore):
    """
    # Spot
    - https://docs.kucoin.com/#position-status-change-event
    """


class Instrument(DataStore):
    """
    # Future
    - https://docs.kucoin.com/futures/#contract-market-data
    """

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert(
            [
                {
                    "symbol": _symbol_from_msg(msg),
                    "subject": msg["subject"],
                    **msg["data"],
                }
            ]
        )


class Announcements(DataStore):
    """

    # Future
    - https://docs.kucoin.com/futures/#contract-market-data
    """

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert([{"subject": msg["subject"], **msg["data"]}])


class TransactionStats(DataStore):
    """

    # Future
    - https://docs.kucoin.com/futures/#transaction-statistics-timer-event
    """

    _KEYS = ["symbol", "subject"]

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert(
            [
                {
                    "subject": msg["subject"],
                    "symbol": _symbol_from_msg(msg),
                    **msg["data"],
                }
            ]
        )


class BalanceEvents(DataStore):
    """

    # Future
    - https://docs.kucoin.com/futures/#account-balance-events
    """

    def _onmessage(self, msg: dict[str, Any]) -> None:
        self._insert(
            [
                {
                    "subject": msg["subject"],
                    "symbol": _symbol_from_msg(msg),
                    **msg["data"],
                }
            ]
        )


class Positions(DataStore):
    """
    # Future
    - https://docs.kucoin.com/futures/#position-change-events
    """

    # onewayのみ
    _KEYS = ["symbol"]

    def _onresponse(self, data) -> None:
        for d in data:
            if d["isOpen"]:
                assert d["currentQty"] != 0
                self._insert([{"side": "BUY" if d["currentQty"] > 0 else "SELL", **d}])

    def _onmessage(self, msg: dict[str, Any]) -> None:
        d = msg["data"]
        reason = d["changeReason"]
        if reason == "positionChange":
            if d["isOpen"]:
                # 新規ポジション or ポジション数量変化
                assert d["currentQty"] != 0
                d["side"] = "BUY" if d["currentQty"] > 0 else "SELL"
                self._update([d])
            else:
                # ポジション解消
                assert d["currentQty"] == 0
                self._delete([d])
        elif reason == "markPriceChange":
            # mark priceの変化によるポジション情報の部分更新
            # 性質上prev_itemは必ず存在するはず（ポジションが解消された後にマークプライス変化に
            # よるポジション情報の更新メッセージは来ないはず）
            if prev_item := self.get(d):
                updated_item = {**prev_item, **d}
                self._update([updated_item])
