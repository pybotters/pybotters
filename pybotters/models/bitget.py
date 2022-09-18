from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Optional

import aiohttp

from ..store import DataStore, DataStoreManager
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BitgetDataStore(DataStoreManager):
    """
    Bitgetのデータストアマネージャー
    https://bitgetlimited.github.io/apidoc/en/mix/#websocketapi
    """

    def _init(self) -> None:
        self.create("trade", datastore_class=Trade)
        self.create("orderbook", datastore_class=OrderBook)
        self.create("ticker", datastore_class=Ticker)
        self.create("candlesticks", datastore_class=CandleSticks)
        self.create("account", datastore_class=Account)
        self.create("orders", datastore_class=Orders)
        self.create("positions", datastore_class=Positions)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """
        対応エンドポイント

        - GET /api/mix/v1/order/current (DataStore: orders)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if resp.url.path in ("/api/mix/v1/order/current",):
                if int(data.get("code", "0")) == 0:
                    self.orders._onresponse(data["data"])
                else:
                    raise ValueError(
                        "Response error at DataStore initialization\n"
                        f"URL: {resp.url}\n"
                        f"Data: {data}"
                    )

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if "arg" in msg and "data" in msg:
            channel = msg["arg"].get("channel")
            if channel == "trade":
                self.trade._onmessage(msg)
            elif channel == "ticker":
                self.ticker._onmessage(msg)
            elif channel == "candle1m":
                self.candlesticks._onmessage(msg)
            elif channel == "books":
                self.orderbook._onmessage(msg)
            elif channel == "account":
                self.account._onmessage(msg.get("data", []))
            elif channel == "positions":
                self.positions._onmessage(msg.get("data", []))
            elif channel == "orders":
                self.orders._onmessage(msg.get("data", []))

        if msg.get("event", "") == "error":
            logger.warning(msg)

    @property
    def trade(self) -> "Trade":
        return self.get("trade", Trade)

    @property
    def orderbook(self) -> "OrderBook":
        return self.get("orderbook", OrderBook)

    @property
    def ticker(self):
        return self.get("ticker", Ticker)

    @property
    def candlesticks(self) -> "CandleSticks":
        return self.get("candlesticks", CandleSticks)

    @property
    def account(self) -> "Account":
        return self.get("account", Account)

    @property
    def orders(self) -> "Orders":
        return self.get("orders", Orders)

    @property
    def positions(self) -> "Positions":
        return self.get("positions", Positions)


class Trade(DataStore):
    _KEYS = ["instId", "ts"]
    _MAXLEN = 99999

    def _onmessage(self, message: Item) -> None:
        instId = message["arg"]["instId"]
        self._insert(
            [
                {
                    "instId": instId,
                    "ts": int(item[0]),
                    "price": float(item[1]),
                    "size": float(item[2]),
                    "side": item[3],
                }
                for item in message.get("data", [])
            ]
        )


class OrderBook(DataStore):
    _KEYS = ["instId", "side", "price"]

    def _init(self) -> None:
        self.timestamp: Optional[int] = None

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

    def _onmessage(self, message: Item) -> None:
        instId = message["arg"]["instId"]
        books = message["data"]
        for key, side in (("bids", "BUY"), ("asks", "SELL")):
            for book in books:
                for item in book[key]:
                    if item[1] != "0":
                        self._insert(
                            [
                                {
                                    "instId": instId,
                                    "side": side,
                                    "price": float(item[0]),
                                    "size": float(item[1]),
                                }
                            ]
                        )
                    else:
                        self._delete(
                            [
                                {
                                    "instId": instId,
                                    "side": side,
                                    "price": float(item[0]),
                                    "size": float(item[1]),
                                }
                            ]
                        )


class Ticker(DataStore):
    _KEYS = ["instId"]

    def _onmessage(self, message):
        self._update(message.get("data"))


class CandleSticks(DataStore):
    _KEYS = ["instId", "interval", "ts"]

    def _onmessage(self, message: Item) -> None:
        instId = message["arg"]["instId"]
        channel = message["arg"]["channel"]
        self._insert(
            [
                {
                    "instId": instId,
                    "interval": channel[-2:],
                    "ts": item[0],
                    "o": float(item[1]),
                    "h": float(item[2]),
                    "l": float(item[3]),
                    "c": float(item[4]),
                    "baseVol": float(item[5]),
                }
                for item in message.get("data", [])
            ]
        )


class Account(DataStore):
    _KEYS = ["marginCoin"]

    def _onmessage(self, data: list[Item]) -> None:
        self._update(data)


class Orders(DataStore):
    _KEYS = ["instId", "clOrdId"]

    def _onmessage(self, data: list[Item]) -> None:
        for item in data:
            if item["status"] == "new":
                self._insert([item])
            elif item["status"] == "cancelled":
                self._delete([item])
            elif item["status"] == "partial-fill":
                self._update([item])
            elif item["status"] == "full-fill":
                self._delete([item])

    def _onresponse(self, data: list[Item]) -> None:
        # wsから配信される情報とAPIレスポンスで得られる情報の辞書キーが違うのでwsから配信される情報に合わせて格納
        self._insert(
            [
                {
                    "accFillSz": str(item["filledQty"]),
                    "cTime": int(item["cTime"]),
                    "clOrdId": item["clientOid"],
                    "force": item["timeInForce"],
                    "instId": item["symbol"],
                    "ordId": item["orderId"],
                    "ordType": item["orderType"],
                    "posSide": item["posSide"],
                    "px": str(item["price"]),
                    "side": "buy"
                    if item["side"] in ("close_short", "open_long")
                    else "sell",
                    "status": item["state"],
                    "sz": str(item["size"]),
                    "tgtCcy": item["marginCoin"],
                    "uTime": int(item["uTime"]),
                }
                for item in data
            ]
        )


class Positions(DataStore):
    _KEYS = ["posId", "instId"]

    def _onmessage(self, data: list[Item]) -> None:
        for item in data:
            if item["total"] == 0:
                self._delete([item])
            else:
                self._insert([item])
