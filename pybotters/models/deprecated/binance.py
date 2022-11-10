from __future__ import annotations

import asyncio
import logging
from collections import deque
from typing import Any, Awaitable, Optional, Union

import aiohttp

from ...auth import Auth
from ...store import DataStore, DataStoreManager
from ...typedefs import Item
from ...ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BinanceDataStore(DataStoreManager):
    """
    非推奨: Binanceのデータストアマネージャー(※v0.4.0: Binance Futures USDⓈ-Mのみ)
    """

    def __new__(cls, *args, **kwargs) -> BinanceDataStore:
        logger.warning(
            "DEPRECATION WARNING: BinanceDataStore will be changed to "
            "BinanceUSDSMDataStore"
        )
        return super().__new__(cls)

    def _init(self) -> None:
        self.create("trade", datastore_class=Trade)
        self.create("markprice", datastore_class=MarkPrice)
        self.create("kline", datastore_class=Kline)
        self.create("continuouskline", datastore_class=ContinuousKline)
        self.create("ticker", datastore_class=Ticker)
        self.create("bookticker", datastore_class=BookTicker)
        self.create("liquidation", datastore_class=Liquidation)
        self.create("orderbook", datastore_class=OrderBook)
        self.create("balance", datastore_class=Balance)
        self.create("position", datastore_class=Position)
        self.create("order", datastore_class=Order)
        self.listenkey: Optional[str] = None

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """
        対応エンドポイント
        - GET /fapi/v1/depth (DataStore: orderbook)
            - Binance APIドキュメントに従ってWebSocket接続後にinitializeすること。
            - orderbook データストアの initialized がTrueになる。
        - GET /fapi/v2/balance (DataStore: balance)
        - GET /fapi/v2/positionRisk (DataStore: position)
        - GET /fapi/v1/openOrders (DataStore: order)
        - POST /fapi/v1/listenKey (Property: listenkey)
            - プロパティ listenkey にlistenKeyが格納され30分ごとに PUT /fapi/v1/listenKey
              のリクエストがスケジュールされる。
        - GET /fapi/v1/klines (DataStore: kline)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if resp.url.path in ("/fapi/v1/depth",):
                if "symbol" in resp.url.query:
                    self.orderbook._onresponse(resp.url.query["symbol"], data)
            elif resp.url.path in ("/fapi/v2/balance",):
                self.balance._onresponse(data)
            elif resp.url.path in ("/fapi/v2/positionRisk",):
                self.position._onresponse(data)
            elif resp.url.path in ("/fapi/v1/openOrders",):
                symbol = (
                    resp.url.query["symbol"] if "symbol" in resp.url.query else None
                )
                self.order._onresponse(symbol, data)
            elif resp.url.path in ("/fapi/v1/listenKey",):
                self.listenkey = data["listenKey"]
                asyncio.create_task(
                    self._listenkey(resp.url, resp.__dict__["_raw_session"])
                )
            elif resp.url.path in ("/fapi/v1/klines",):
                self.kline._onresponse(
                    resp.url.query["symbol"], resp.url.query["interval"], data
                )

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if "error" in msg:
            logger.warning(msg)
        if "result" not in msg:
            data = msg["data"] if "data" in msg else msg
            event = data["e"] if isinstance(data, dict) else data[0]["e"]
            if event in ("trade", "aggTrade"):
                self.trade._onmessage(data)
            elif event == "markPriceUpdate":
                self.markprice._onmessage(data)
            elif event == "kline":
                self.kline._onmessage(data)
            elif event == "continuous_kline":
                self.continuouskline._onmessage(data)
            elif event in ("24hrMiniTicker", "24hrTicker"):
                self.ticker._onmessage(data)
            elif event == "bookTicker":
                self.bookticker._onmessage(data)
            elif event == "forceOrder":
                self.liquidation._onmessage(data)
            elif event == "depthUpdate":
                self.orderbook._onmessage(data)
            elif event == "ACCOUNT_UPDATE":
                self.balance._onmessage(data)
                self.position._onmessage(data)
            elif event == "ORDER_TRADE_UPDATE":
                self.order._onmessage(data)

    @staticmethod
    async def _listenkey(url, session: aiohttp.ClientSession):
        while not session.closed:
            await session.put(url, auth=Auth)
            await asyncio.sleep(1800.0)  # 30 minutes

    @property
    def trade(self) -> "Trade":
        return self.get("trade", Trade)

    @property
    def markprice(self) -> "MarkPrice":
        return self.get("markprice", MarkPrice)

    @property
    def kline(self) -> "Kline":
        return self.get("kline", Kline)

    @property
    def continuouskline(self) -> "ContinuousKline":
        return self.get("continuouskline", ContinuousKline)

    @property
    def ticker(self) -> "Ticker":
        return self.get("ticker", Ticker)

    @property
    def bookticker(self) -> "BookTicker":
        return self.get("bookticker", BookTicker)

    @property
    def liquidation(self) -> "Liquidation":
        return self.get("liquidation", Liquidation)

    @property
    def orderbook(self) -> "OrderBook":
        return self.get("orderbook", OrderBook)

    @property
    def balance(self) -> "Balance":
        return self.get("balance", Balance)

    @property
    def position(self) -> "Position":
        return self.get("position", Position)

    @property
    def order(self) -> "Order":
        """
        アクティブオーダーのみ(約定・キャンセル済みは削除される)
        """
        return self.get("order", Order)


class Trade(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, item: Item) -> None:
        self._insert([item])


class MarkPrice(DataStore):
    _KEYS = ["s"]

    def _onmessage(self, data: Union[Item, list[Item]]) -> None:
        if isinstance(data, list):
            self._update(data)
        else:
            self._update([data])


class Kline(DataStore):
    _KEYS = ["t", "s", "i"]

    def _onmessage(self, item: Item) -> None:
        self._update([item["k"]])

    def _onresponse(self, symbol: str, interval: str, data: list[list[Any]]) -> None:
        ws_compatible_data: list[Item] = [
            {
                "t": kline_data[0],  # Open time
                "T": kline_data[6],  # Close time
                "s": symbol,
                "i": interval,
                "o": kline_data[1],  # Open
                "c": kline_data[4],  # Close
                "h": kline_data[2],  # High
                "l": kline_data[3],  # Low
                "v": kline_data[5],  # Base asset volume
                "n": kline_data[8],  # Number of trades
                "x": True,  # Is this kline closed?
                "q": kline_data[7],  # Quote asset volume
                "V": kline_data[9],  # Taker buy base asset volume
                "Q": kline_data[10],  # Taker buy quote asset volume
                "B": kline_data[11],  # Ignore
            }
            for kline_data in data
        ]
        self._update(ws_compatible_data)


class ContinuousKline(DataStore):
    _KEYS = ["ps", "ct", "t", "i"]

    def _onmessage(self, item: Item) -> None:
        self._update([{"ps": item["ps"], "ct": item["ct"], **item["k"]}])


class Ticker(DataStore):
    _KEYS = ["s"]

    def _onmessage(self, data: Union[Item, list[Item]]) -> None:
        if isinstance(data, list):
            self._update(data)
        else:
            self._update([data])


class BookTicker(DataStore):
    _KEYS = ["s"]

    def _onmessage(self, item: Item) -> None:
        self._update([item])


class Liquidation(DataStore):
    def _onmessage(self, item: Item) -> None:
        self._insert([item["o"]])


class OrderBook(DataStore):
    _KEYS = ["s", "S", "p"]
    _MAPSIDE = {"BUY": "b", "SELL": "a"}

    def _init(self) -> None:
        self.initialized = False
        self._buff = deque(maxlen=200)

    def sorted(self, query: Optional[Item] = None) -> dict[str, list[float]]:
        if query is None:
            query = {}
        result = {self._MAPSIDE[k]: [] for k in self._MAPSIDE}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[self._MAPSIDE[item["S"]]].append([item["p"], item["q"]])
        result["b"].sort(key=lambda x: float(x[0]), reverse=True)
        result["a"].sort(key=lambda x: float(x[0]))
        return result

    def _onmessage(self, item: Item) -> None:
        if not self.initialized:
            self._buff.append(item)
        for s, bs in self._MAPSIDE.items():
            for row in item[bs]:
                if float(row[1]) != 0.0:
                    self._update([{"s": item["s"], "S": s, "p": row[0], "q": row[1]}])
                else:
                    self._delete([{"s": item["s"], "S": s, "p": row[0]}])

    def _onresponse(self, symbol: str, item: Item) -> None:
        self.initialized = True
        self._delete(self.find({"s": symbol}))
        for s, bs in (("BUY", "bids"), ("SELL", "asks")):
            for row in item[bs]:
                self._insert([{"s": symbol, "S": s, "p": row[0], "q": row[1]}])
        for msg in self._buff:
            if msg["U"] <= item["lastUpdateId"] and msg["u"] >= item["lastUpdateId"]:
                self._onmessage(msg)
        self._buff.clear()


class Balance(DataStore):
    _KEYS = ["a"]

    def _onmessage(self, item: Item) -> None:
        self._update(item["a"]["B"])

    def _onresponse(self, data: list[Item]) -> None:
        for item in data:
            self._update(
                [
                    {
                        "a": item["asset"],
                        "wb": item["balance"],
                        "cw": item["crossWalletBalance"],
                    }
                ]
            )


class Position(DataStore):
    _KEYS = ["s", "ps"]

    def _onmessage(self, item: Item) -> None:
        self._update(item["a"]["P"])

    def _onresponse(self, data: list[Item]) -> None:
        for item in data:
            self._update(
                [
                    {
                        "s": item["symbol"],
                        "pa": item["positionAmt"],
                        "ep": item["entryPrice"],
                        "up": item["unRealizedProfit"],
                        "mt": item["marginType"],
                        "iw": item["isolatedWallet"],
                        "ps": item["positionSide"],
                    }
                ]
            )


class Order(DataStore):
    _KEYS = ["s", "i"]

    def _onmessage(self, item: Item) -> None:
        if item["o"]["X"] not in ("FILLED", "CANCELED", "EXPIRED"):
            self._update([item["o"]])
        else:
            self._delete([item["o"]])

    def _onresponse(self, symbol: Optional[str], data: list[Item]) -> None:
        if symbol is not None:
            self._delete(self.find({"s": symbol}))
        else:
            self._clear()
        for item in data:
            self._insert(
                [
                    {
                        "s": item["symbol"],
                        "c": item["clientOrderId"],
                        "S": item["side"],
                        "o": item["type"],
                        "f": item["timeInForce"],
                        "q": item["origQty"],
                        "p": item["price"],
                        "ap": item["avgPrice"],
                        "sp": item["stopPrice"],
                        "X": item["status"],
                        "i": item["orderId"],
                        "z": item["executedQty"],
                        "T": item["updateTime"],
                        "R": item["reduceOnly"],
                        "wt": item["workingType"],
                        "ot": item["origType"],
                        "ps": item["positionSide"],
                        "cp": item["closePosition"],
                        "pP": item["priceProtect"],
                    }
                ]
            )
