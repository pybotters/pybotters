from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Awaitable

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    import aiohttp

    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BitgetDataStore(DataStoreCollection):
    """DataStoreCollection for Bitget V1 API"""

    def _init(self) -> None:
        self._create("trade", datastore_class=Trade)
        self._create("orderbook", datastore_class=OrderBook)
        self._create("ticker", datastore_class=Ticker)
        self._create("candlesticks", datastore_class=CandleSticks)
        self._create("account", datastore_class=Account)
        self._create("orders", datastore_class=Orders)
        self._create("positions", datastore_class=Positions)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data.

        対応エンドポイント

        - GET /api/mix/v1/order/current (:attr:`.BitgetDataStore.orders`)
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
        """trade channel.

        * https://bitgetlimited.github.io/apidoc/en/spot/#trades-channel
        * https://bitgetlimited.github.io/apidoc/en/mix/#trades-channel
        """
        return self._get("trade", Trade)

    @property
    def orderbook(self) -> "OrderBook":
        """books channel.

        * https://bitgetlimited.github.io/apidoc/en/spot/#depth-channel
        * https://bitgetlimited.github.io/apidoc/en/mix/#order-book-channel
        """
        return self._get("orderbook", OrderBook)

    @property
    def ticker(self):
        """ticker channel.

        * https://bitgetlimited.github.io/apidoc/en/spot/#tickers-channel
        * https://bitgetlimited.github.io/apidoc/en/mix/#tickers-channel
        """
        return self._get("ticker", Ticker)

    @property
    def candlesticks(self) -> "CandleSticks":
        """candle1m channel.

        * https://bitgetlimited.github.io/apidoc/en/spot/#candlesticks-channel
        * https://bitgetlimited.github.io/apidoc/en/mix/#candlesticks-channel
        """
        return self._get("candlesticks", CandleSticks)

    @property
    def account(self) -> "Account":
        """account channel.

        * https://bitgetlimited.github.io/apidoc/en/mix/#account-channel
        * https://bitgetlimited.github.io/apidoc/en/spot/#account-channel
        """
        return self._get("account", Account)

    @property
    def orders(self) -> "Orders":
        """orders channel.

        アクティブオーダーのみデータが格納されます。 キャンセル、約定済みなどは削除されます。

        * https://bitgetlimited.github.io/apidoc/en/spot/#order-channel
        * https://bitgetlimited.github.io/apidoc/en/mix/#order-channel
        """
        return self._get("orders", Orders)

    @property
    def positions(self) -> "Positions":
        """positions channel.

        * https://bitgetlimited.github.io/apidoc/en/mix/#positions-channel
        """
        return self._get("positions", Positions)


class Trade(DataStore):
    _KEYS = ["instId", "ts"]
    _MAXLEN = 99999

    def _onmessage(self, message: Item) -> None:
        instId = message["arg"]["instId"]
        self._insert(
            [
                {
                    "instId": instId,
                    "ts": item[0],
                    "px": item[1],
                    "sz": item[2],
                    "side": item[3],
                }
                for item in message.get("data", [])
            ]
        )


class OrderBook(DataStore):
    _KEYS = ["instId", "side", "px"]

    def _init(self) -> None:
        self.timestamp: int | None = None

    def sorted(
        self, query: Item | None = None, limit: int | None = None
    ) -> dict[str, list[Item]]:
        return self._sorted(
            item_key="side",
            item_asc_key="asks",
            item_desc_key="bids",
            sort_key="px",
            query=query,
            limit=limit,
        )

    def _onmessage(self, message: Item) -> None:
        instId = message["arg"]["instId"]
        books = message["data"]
        for side in ("asks", "bids"):
            for book in books:
                for item in book[side]:
                    if item[1] != "0":
                        self._insert(
                            [
                                {
                                    "instId": instId,
                                    "side": side,
                                    "px": item[0],
                                    "sz": item[1],
                                }
                            ]
                        )
                    else:
                        self._delete(
                            [
                                {
                                    "instId": instId,
                                    "side": side,
                                    "px": item[0],
                                    "sz": item[1],
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
                    "o": item[1],
                    "h": item[2],
                    "l": item[3],
                    "c": item[4],
                    "baseVol": item[5],
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
