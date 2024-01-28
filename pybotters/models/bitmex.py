import logging

from ..store import DataStore, DataStoreManager
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BitMEXDataStore(DataStoreManager):
    """
    BitMEXのデータストアマネージャー
    """

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
                self.create(table, keys=msg["keys"] if "keys" in msg else [], data=data)
                if table == "trade":
                    self["trade"]._MAXLEN = 99999
            elif action == "insert":
                if table in self:
                    self[table]._insert(data)
            elif action == "update":
                if table in self:
                    self[table]._update(data)
            elif action == "delete":
                if table in self:
                    self[table]._delete(data)
            if table == "order":
                if "order" in self:
                    self["order"]._delete(
                        [
                            order
                            for order in self["order"].find()
                            if order["ordStatus"] in ("Filled", "Canceled")
                        ]
                    )

    @property
    def funding(self) -> DataStore:
        return self.get("funding", DataStore)

    @property
    def instrument(self) -> DataStore:
        return self.get("instrument", DataStore)

    @property
    def insurance(self) -> DataStore:
        return self.get("insurance", DataStore)

    @property
    def liquidation(self) -> DataStore:
        return self.get("liquidation", DataStore)

    @property
    def orderbook(self) -> DataStore:
        return self.get("orderBookL2", DataStore)

    @property
    def quote(self) -> DataStore:
        return self.get("quote", DataStore)

    @property
    def quotebin1m(self) -> DataStore:
        return self.get("quoteBin1m", DataStore)

    @property
    def quotebin5m(self) -> DataStore:
        return self.get("quoteBin5m", DataStore)

    @property
    def quotebin1h(self) -> DataStore:
        return self.get("quoteBin1h", DataStore)

    @property
    def quotebin1d(self) -> DataStore:
        return self.get("quoteBin1d", DataStore)

    @property
    def trade(self) -> DataStore:
        return self.get("trade", DataStore)

    @property
    def tradebin1m(self) -> DataStore:
        return self.get("tradeBin1m", DataStore)

    @property
    def tradebin5m(self) -> DataStore:
        return self.get("tradeBin5m", DataStore)

    @property
    def tradebin1h(self) -> DataStore:
        return self.get("tradeBin1h", DataStore)

    @property
    def tradebin1d(self) -> DataStore:
        return self.get("tradeBin1d", DataStore)

    @property
    def execution(self) -> DataStore:
        return self.get("execution", DataStore)

    @property
    def order(self) -> DataStore:
        """
        アクティブオーダーのみ(約定・キャンセル済みは削除される)
        """
        return self.get("order", DataStore)

    @property
    def margin(self) -> DataStore:
        return self.get("margin", DataStore)

    @property
    def position(self) -> DataStore:
        return self.get("position", DataStore)

    @property
    def wallet(self) -> DataStore:
        return self.get("wallet", DataStore)
