import logging

from ..store import DataStore, DataStoreCollection
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BitMEXDataStore(DataStoreCollection):
    """BitMEX の DataStoreCollection クラス"""

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if "error" in msg:
            logger.warning(msg)
        if "table" in msg:
            table = msg["table"]
            if table == "orderBookL2_25":
                table = "orderBookL2"
            action = msg["action"]
            data = msg["data"]
            if action == "partial":
                self._create(
                    table, keys=msg["keys"] if "keys" in msg else [], data=data
                )
                if table == "trade":
                    self.trade._MAXLEN = 99999
            elif action == "insert":
                if target_store := self[table]:
                    target_store._insert(data)
            elif action == "update":
                if target_store := self[table]:
                    target_store._update(data)
            elif action == "delete":
                if target_store := self[table]:
                    target_store._delete(data)
            if table == "order":
                if "order" in self:
                    self.order._delete(
                        [
                            order
                            for order in self.order.find()
                            if order["ordStatus"] in ("Filled", "Canceled")
                        ]
                    )

    @property
    def funding(self) -> DataStore:
        """funding topic."""
        return self._get("funding", DataStore)

    @property
    def instrument(self) -> DataStore:
        """instrument topic."""
        return self._get("instrument", DataStore)

    @property
    def insurance(self) -> DataStore:
        """insurance topic."""
        return self._get("insurance", DataStore)

    @property
    def liquidation(self) -> DataStore:
        """liquidation topic."""
        return self._get("liquidation", DataStore)

    @property
    def orderbook(self) -> DataStore:
        """orderbook topic."""
        return self._get("orderBookL2", DataStore)

    @property
    def quote(self) -> DataStore:
        """quote topic."""
        return self._get("quote", DataStore)

    @property
    def quotebin1m(self) -> DataStore:
        """quotebin1m topic."""
        return self._get("quoteBin1m", DataStore)

    @property
    def quotebin5m(self) -> DataStore:
        """quotebin5m topic."""
        return self._get("quoteBin5m", DataStore)

    @property
    def quotebin1h(self) -> DataStore:
        """quotebin1h topic."""
        return self._get("quoteBin1h", DataStore)

    @property
    def quotebin1d(self) -> DataStore:
        """quotebin1d topic."""
        return self._get("quoteBin1d", DataStore)

    @property
    def trade(self) -> DataStore:
        """trade topic."""
        return self._get("trade", DataStore)

    @property
    def tradebin1m(self) -> DataStore:
        """tradebin1m topic."""
        return self._get("tradeBin1m", DataStore)

    @property
    def tradebin5m(self) -> DataStore:
        """tradebin5m topic."""
        return self._get("tradeBin5m", DataStore)

    @property
    def tradebin1h(self) -> DataStore:
        """tradebin1h topic."""
        return self._get("tradeBin1h", DataStore)

    @property
    def tradebin1d(self) -> DataStore:
        """tradebin1d topic."""
        return self._get("tradeBin1d", DataStore)

    @property
    def execution(self) -> DataStore:
        """execution topic."""
        return self._get("execution", DataStore)

    @property
    def order(self) -> DataStore:
        """order topic.

        アクティブオーダーのみデータが格納されます。 キャンセル、約定済みなどは削除されます。
        """
        return self._get("order", DataStore)

    @property
    def margin(self) -> DataStore:
        """margin topic."""
        return self._get("margin", DataStore)

    @property
    def position(self) -> DataStore:
        """position topic."""
        return self._get("position", DataStore)

    @property
    def wallet(self) -> DataStore:
        """wallet topic."""
        return self._get("wallet", DataStore)
