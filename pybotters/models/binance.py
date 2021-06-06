from typing import Any, List

from ..store import DataStore, DataStoreInterface
from ..typedefs import Item
from ..ws import ClientWebSocketResponse


class BinanceDataStore(DataStoreInterface):
    def _init(self) -> None:
        self.create('trade', datastore_class=Trade)
        self.create('indexprice', datastore_class=IndexPrice)
        self.create('markprice', datastore_class=MarkPrice)
        self.create('kline', datastore_class=Kline)
        self.create('continuouskline', datastore_class=ContinuousKline)
        self.create('indexpricekline', datastore_class=IndexPriceKline)
        self.create('markpricekline', datastore_class=MarkPriceKline)
        self.create('ticker', datastore_class=Ticker)
        self.create('bookticker', datastore_class=BookTicker)
        self.create('liquidation', datastore_class=Liquidation)
        self.create('orderbook', datastore_class=OrderBook)
        self.create('balance', datastore_class=Balance)
        self.create('position', datastore_class=Position)
        self.create('order', datastore_class=Order)

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if 'e' in msg:
            event: str = msg['e']
            if event in ('trade', 'aggTrade'):
                self.bookticker._onmessage(msg)
            elif event == 'bookTicker':
                self.bookticker._onmessage(msg)
            elif event == 'ACCOUNT_UPDATE':
                self.balance._onmessage(msg['a']['B'])
                self.position._onmessage(msg['a']['P'])
            elif event == 'ORDER_TRADE_UPDATE':
                self.order._onmessage(msg['o'])

    @property
    def trade(self) -> 'Trade':
        return self._stores.get('trade')

    @property
    def bookticker(self) -> 'BookTicker':
        return self._stores.get('bookticker')

    @property
    def balance(self) -> 'Balance':
        return self._stores.get('balance')

    @property
    def position(self) -> 'Position':
        return self._stores.get('position')

    @property
    def order(self) -> 'Order':
        return self._stores.get('order')


class Trade(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, item: Item) -> None:
        self._insert([item])


class IndexPrice(DataStore):
    pass


class MarkPrice(DataStore):
    pass


class Kline(DataStore):
    pass


class ContinuousKline(DataStore):
    pass


class IndexPriceKline(DataStore):
    pass


class MarkPriceKline(DataStore):
    pass


class Ticker(DataStore):
    pass


class BookTicker(DataStore):
    _KEYS = ['s']

    def _onmessage(self, item: Item) -> None:
        self._update([item])


class Liquidation(DataStore):
    pass


class OrderBook(DataStore):
    pass


class Balance(DataStore):
    _KEYS = ['a']

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)


class Position(DataStore):
    _KEYS = ['s', 'ps']

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)


class Order(DataStore):
    _KEYS = ['s', 'i']

    def _onmessage(self, item: Item) -> None:
        if item['X'] not in ('FILLED', 'CANCELED', 'EXPIRED'):
            self._update([item])
        else:
            self._delete([item])
