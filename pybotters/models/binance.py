from __future__ import annotations

import asyncio
import logging
from collections import deque
from typing import Any, Awaitable, Optional, Union

import aiohttp

from ..auth import Auth
from ..store import DataStore, DataStoreManager
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BinanceDataStoreBase(DataStoreManager):
    _ORDERBOOK_INIT_ENDPOINT = None
    _ORDER_INIT_ENDPOINT = None
    _LISTENKEY_INIT_ENDPOINT = None
    _KLINE_INIT_ENDPOINT = None

    def _init(self) -> None:
        self.create("trade", datastore_class=Trade)
        self.create("kline", datastore_class=Kline)
        self.create("ticker", datastore_class=Ticker)
        self.create("bookticker", datastore_class=BookTicker)
        self.create("orderbook", datastore_class=OrderBook)
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
            endpoint = resp.url.path
            if self._is_target_endpoint(self._ORDERBOOK_INIT_ENDPOINT, endpoint):
                self._initialize_orderbook(resp, data)
            elif self._is_target_endpoint(self._ORDER_INIT_ENDPOINT, endpoint):
                self._initialize_order(resp, data)
            elif self._is_target_endpoint(self._LISTENKEY_INIT_ENDPOINT, endpoint):
                self._initialize_listenkey(resp, data)
            elif self._is_target_endpoint(self._KLINE_INIT_ENDPOINT, endpoint):
                self._initialize_kline(resp, data)

            self._initialize_hook(resp, data, endpoint)

    def _initialize_hook(self, resp: aiohttp.ClientResponse, data: Any, endpoint: str):
        """ 子クラス用initialize hook

        """
        ...

    def _is_target_endpoint(self, target: Union[str, tuple[str], None], endpoint: str):
        if target:
            if isinstance(target, str):
                return endpoint == target
            elif isinstance(target, tuple):
                return endpoint in target
            else:
                raise RuntimeError(f"Invalid target endpoint: {target}")
        else:
            return False

    def _initialize_orderbook(self, resp: aiohttp.ClientResponse, data: Any):
        if "symbol" in resp.url.query:
            self.orderbook._onresponse(resp.url.query["symbol"], data)

    def _initialize_order(self, resp: aiohttp.ClientResponse, data: Any):
        symbol = (
            resp.url.query["symbol"] if "symbol" in resp.url.query else None
        )
        self.order._onresponse(symbol, data)

    def _initialize_listenkey(self, resp: aiohttp.ClientResponse, data: Any):
        self.listenkey = data["listenKey"]
        asyncio.create_task(
            self._listenkey(resp.url, resp.__dict__["_raw_session"])
        )

    def _initialize_kline(self, resp: aiohttp.ClientResponse, data: Any):
        self.kline._onresponse(
            resp.url.query["symbol"], resp.url.query["interval"], data
        )

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if "error" in msg:
            logger.warning(msg)
        if "result" not in msg:
            data = self._get_data_from_msg(msg)
            event = self._get_event_from_msg(msg)
            if self._is_trade_msg(msg, event):
                self.trade._onmessage(data)
            elif self._is_kline_msg(msg, event):
                self.kline._onmessage(data)
            elif self._is_ticker_msg(msg, event):
                assert data["e"] in ("24hrMiniTicker", "24hrTicker")
                self.ticker._onmessage(data)
            elif self._is_bookticker_msg(msg, event):
                self.bookticker._onmessage(data)
            elif self._is_orderbook_msg(msg, event):
                self.orderbook._onmessage(data)
            elif self._is_order_msg(msg, event):
                self.order._onmessage(data)

            self._onmessage_hook(msg, event, data)

    def _get_data_from_msg(self, msg):
        return msg["data"] if "data" in msg else msg

    def _get_event_from_msg(self, msg):
        _data = msg["data"] if "data" in msg else msg
        _data = _data if isinstance(_data, dict) else _data[0]
        if "e" in _data:
            return _data["e"]
        else:
            return None

    def _onmessage_hook(self, msg: Any, event: str, data: Any):
        """ 子クラス用メッセージハンドラーhook

        """
        ...

    def _is_trade_msg(self, msg: Any, event: str):
        return event in ("trade", "aggTrade")

    def _is_kline_msg(self, msg: Any, event: str):
        return event == "kline"

    def _is_ticker_msg(self, msg: Any, event: str):
        return event in ("24hrMiniTicker", "24hrTicker")

    def _is_bookticker_msg(self, msg: Any, event: str):
        if event is None:
            return msg.get("stream", "").endswith("bookTicker")
        else:
            return event == "bookTicker"

    def _is_orderbook_msg(self, msg: Any, event: str):
        return event == "depthUpdate"

    def _is_order_msg(self, msg: Any, event: str):
        return event == "ORDER_TRADE_UPDATE"


    @staticmethod
    async def _listenkey(url, session: aiohttp.ClientSession):
        while not session.closed:
            await session.put(url, auth=Auth)
            await asyncio.sleep(1800.0)  # 30 minutes

    @property
    def trade(self) -> "Trade":
        return self.get("trade", Trade)

    @property
    def kline(self) -> "Kline":
        return self.get("kline", Kline)

    @property
    def ticker(self) -> "Ticker":
        return self.get("ticker", Ticker)

    @property
    def bookticker(self) -> "BookTicker":
        return self.get("bookticker", BookTicker)

    @property
    def orderbook(self) -> "OrderBook":
        return self.get("orderbook", OrderBook)

    @property
    def order(self) -> "Order":
        """
        アクティブオーダーのみ(約定・キャンセル済みは削除される)
        """
        return self.get("order", Order)


class BinanceFuturesDataStoreBase(BinanceDataStoreBase):
    _BALANCE_INIT_ENDPOINT = None
    _POSITION_INIT_ENDPOINT = None

    def _init(self) -> None:
        super()._init()
        self.create("markprice", datastore_class=MarkPrice)
        self.create("continuouskline", datastore_class=ContinuousKline)
        self.create("liquidation", datastore_class=Liquidation)
        self.create("balance", datastore_class=Balance)
        self.create("position", datastore_class=Position)


    def _initialize_hook(self, resp: aiohttp.ClientResponse, data: Any, endpoint: str):
        if self._is_target_endpoint(self._BALANCE_INIT_ENDPOINT, endpoint):
            self._initialize_balance(resp, data)
        elif self._is_target_endpoint(self._POSITION_INIT_ENDPOINT, endpoint):
            self._initialize_position(resp, data)


    def _onmessage_hook(self, msg: Any, event: str, data: Any):
        if self._is_position_msg(msg, event):
            self.position._onmessage(data)

        elif self._is_markprice_msg(msg, event):
            self.markprice._onmessage(data)

        elif self._is_continouskline_msg(msg, event):
            self.continuouskline._onmessage(data)

        elif self._is_liquidation_msg(msg, event):
            self.liquidation._onmessage(data)

        elif self._is_balance_msg(msg, event):
            self.balance._onmessage(data)

        elif self._is_position_msg(msg, event):
            self.position._onmessage(data)


    def _initialize_position(self, resp: aiohttp.ClientResponse, data: Any):
        self.position._onresponse(data)

    def _initialize_balance(self, resp: aiohttp.ClientResponse, data: Any):
        self.balance._onresponse(data)

    def _is_markprice_msg(self, msg: Any, event: str):
        return event == "markPriceUpdate"

    def _is_continouskline_msg(self, msg: Any, event: str):
        return event == "continuous_kline"

    def _is_liquidation_msg(self, msg: Any, event: str):
        return event == "forceOrder"

    def _is_balance_msg(self, msg: Any, event: str):
        return event == "ACCOUNT_UPDATE"

    def _is_position_msg(self, msg: Any, event: str):
        return event == "ACCOUNT_UPDATE"

    @property
    def markprice(self) -> "MarkPrice":
        return self.get("markprice", MarkPrice)

    @property
    def continuouskline(self) -> "ContinuousKline":
        return self.get("continuouskline", ContinuousKline)

    @property
    def liquidation(self) -> "Liquidation":
        return self.get("liquidation", Liquidation)

    @property
    def balance(self) -> "Balance":
        return self.get("balance", Balance)

    @property
    def position(self) -> "Position":
        return self.get("position", Position)




class BinanceSpotDataStore(BinanceDataStoreBase):
    _ORDERBOOK_INIT_ENDPOINT = "/api/v3/depth"
    _ORDER_INIT_ENDPOINT = "/api/v3/openOrders"
    _LISTENKEY_INIT_ENDPOINT = "/api/v3/userDataStream"
    _KLINE_INIT_ENDPOINT = "/api/v3/klines"
    _ACCOUNT_INIT_ENDPOINT = "/api/v3/account"

    def _init(self):
        super()._init()
        self.create("account", datastore_class=Account)

    def _initialize_hook(self, resp: aiohttp.ClientResponse, data: Any, endpoint: str):
        if self._is_target_endpoint(self._ACCOUNT_INIT_ENDPOINT, endpoint):
            self.account._onresponse(data)

    def _onmessage_hook(self, msg: Any, event: str, data: Any):
        if self._is_account_msg(msg, event):
            self.account._onmessage(data)

        elif self._is_order_msg(msg, event):
            self.order._onmessage(data)

    def _is_account_msg(self, msg: Any, event: str):
        return event == "outboundAccountPosition"

    def _is_order_msg(self, msg: Any, event: str):
        return event == "executionReport"

    @property
    def account(self):
        return self.get("account", Account)


class BinanceUSDSMDataStore(BinanceFuturesDataStoreBase):
    _ORDERBOOK_INIT_ENDPOINT = "/fapi/v1/depth"
    _BALANCE_INIT_ENDPOINT = "/fapi/v2/balance"
    _ORDER_INIT_ENDPOINT = "/fapi/v1/openOrders"
    _LISTENKEY_INIT_ENDPOINT = "/fapi/v1/listenKey"
    _KLINE_INIT_ENDPOINT = "/fapi/v1/klines"
    _POSITION_INIT_ENDPOINT = "/fapi/v2/positionRisk"


class BinanceCOINMDataStore(BinanceFuturesDataStoreBase):
    _ORDERBOOK_INIT_ENDPOINT = "/dapi/v1/depth"
    _BALANCE_INIT_ENDPOINT = "/dapi/v1/balance"
    _ORDER_INIT_ENDPOINT = "/dapi/v1/openOrders"
    _LISTENKEY_INIT_ENDPOINT = "/dapi/v1/listenKey"
    _KLINE_INIT_ENDPOINT = "/dapi/v1/klines"
    _POSITION_INIT_ENDPOINT = "/dapi/v1/positionRisk"



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


class Account(DataStore):
    _KEYS = ["a"]

    def _onmessage(self, item: Item) -> None:
        self._update(item["B"])

    def _onresponse(self, data: list[Item]):
        for item in data["balances"]:
            self._update(
                [
                    {
                        "a": item["asset"],
                        "f": item["free"],
                        "l": item["locked"],
                    }
                ]
            )


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
        if item["e"] == "ORDER_TRADE_UPDATE":
            # futures
            event = item["o"]["X"]
            items = [item["o"]]
        else:
            # spot
            event = item["X"]
            items = [item]

        if event not in ("FILLED", "CANCELED", "EXPIRED", "REJECTED"):
            self._update(items)
        else:
            self._delete(items)

    def _onresponse(self, symbol: Optional[str], data: list[Item]) -> None:
        if symbol is not None:
            self._delete(self.find({"s": symbol}))
        else:
            self._clear()
        for item in data:

            if "positionSide" in item:
                # futures
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
            else:
                # spot
                self._insert(
                    [
                        {
                            "s": item["symbol"],
                            "i": item["orderId"],
                            "c": item["clientOrderId"],
                            "p": item["price"],
                            "q": item["origQty"],
                            "z": item["executedQty"],
                            "Z": item["cummulativeQuoteQty"],
                            "f": item["timeInForce"],
                            "o": item["type"],
                            "S": item["side"],
                            "P": item["stopPrice"],
                            "F": item["icebergQty"],
                            "E": item["time"],
                            "T": item["updateTime"],
                            "w": item["isWorking"],
                            "Q": item['origQuoteOrderQty']
                        }
                    ]
                )


# 古いデータストアへのalias
BinanceDataStore = BinanceUSDSMDataStore
