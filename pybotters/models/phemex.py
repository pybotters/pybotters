from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Optional
import urllib.parse

import aiohttp

from ..store import DataStore, DataStoreManager
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class PhemexDataStore(DataStoreManager):
    """
    Phemexのデータストアマネージャー
    https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md
    """

    def _init(self) -> None:
        self.create('trade', datastore_class=Trade)
        self.create('orderbook', datastore_class=OrderBook)
        self.create('ticker', datastore_class=Ticker)
        self.create('market24h', datastore_class=Market24h)
        self.create('kline', datastore_class=Kline)
        self.create('accounts', datastore_class=Accounts)
        self.create('orders', datastore_class=Orders)
        self.create('positions', datastore_class=Positions)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """
        対応エンドポイント

        - GET /exchange/public/md/kline (DataStore: kline)
        """
        for f in asyncio.as_completed(aws):
            resp = await f
            symbol = urllib.parse.parse_qs(urllib.parse.urlparse(str(resp.url)).query)[
                'symbol'
            ][0]
            data = await resp.json()
            if resp.url.path in ('/exchange/public/md/kline',):
                self.kline._onmessage({'symbol': symbol, 'kline': data['data']['rows']})

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if not msg.get('id'):
            if 'trades' in msg:
                self.trade._onmessage(msg)
            elif 'book' in msg:
                self.orderbook._onmessage(msg)
            elif 'tick' in msg:
                self.ticker._onmessage(msg)
            elif 'market24h' in msg:
                self.market24h._onmessage(msg['market24h'])
            elif 'kline' in msg:
                self.kline._onmessage(msg)

            if 'accounts' in msg:
                self.accounts._onmessage(msg.get('accounts'))
            if 'orders' in msg:
                self.orders._onmessage(msg.get('orders'))
            if 'positions' in msg:
                self.positions._onmessage(msg.get('positions'))

    @property
    def trade(self) -> 'Trade':
        return self.get('trade', Trade)

    @property
    def orderbook(self) -> 'OrderBook':
        return self.get('orderbook', OrderBook)

    @property
    def ticker(self):
        return self.get('ticker', Ticker)

    @property
    def market24h(self) -> 'Market24h':
        return self.get('market24h', Market24h)

    @property
    def kline(self) -> 'Kline':
        return self.get('kline', Kline)

    @property
    def accounts(self) -> 'Accounts':
        return self.get('accounts', Accounts)

    @property
    def orders(self) -> 'Orders':
        return self.get('orders', Orders)

    @property
    def positions(self) -> 'Positions':
        return self.get('positions', Positions)


class Trade(DataStore):
    _KEYS = ['symbol', 'timestamp']
    _MAXLEN = 99999

    def _onmessage(self, message: Item) -> None:
        symbol = message.get('symbol')
        self._insert(
            [
                {
                    'symbol': symbol,
                    'timestamp': item[0],
                    'side': item[1],
                    'price': item[2] / 10000,
                    'size': item[3],
                }
                for item in message.get('trades', [])
            ]
        )


class OrderBook(DataStore):
    _KEYS = ['symbol', 'side', 'price']

    def _init(self) -> None:
        self.timestamp: Optional[int] = None

    def sorted(self, query: Item = None) -> dict[str, list[Item]]:
        if query is None:
            query = {}
        result = {'SELL': [], 'BUY': []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item['side']].append(item)
        result['SELL'].sort(key=lambda x: x['price'])
        result['BUY'].sort(key=lambda x: x['price'], reverse=True)
        return result

    def _onmessage(self, message: Item) -> None:
        symbol = message['symbol']
        book = message['book']
        for key, side in (('bids', 'BUY'), ('asks', 'SELL')):
            for item in book[key]:
                if item[1] != 0:
                    self._insert(
                        [
                            {
                                'symbol': symbol,
                                'side': side,
                                'price': item[0],
                                'size': item[1],
                            }
                        ]
                    )
                else:
                    self._delete(
                        [
                            {
                                'symbol': symbol,
                                'side': side,
                                'price': item[0],
                                'size': item[1],
                            }
                        ]
                    )

        self.timestamp = message["timestamp"]


class Ticker(DataStore):
    _KEYS = ['symbol']

    def _onmessage(self, message):
        self._update([message.get('tick')])


class Market24h(DataStore):
    _KEYS = ['symbol']

    def _onmessage(self, item: Item) -> None:
        self._update([item])


class Kline(DataStore):
    _KEYS = ['symbol', 'interval', 'timestamp']

    def _onmessage(self, message: Item) -> None:
        symbol = message.get('symbol')
        self._insert(
            [
                {
                    'symbol': symbol,
                    'interval': item[1],
                    'timestamp': item[0],
                    'open': item[3] / 10000,
                    'high': item[4] / 10000,
                    'low': item[5] / 10000,
                    'close': item[6] / 10000,
                    'volume': item[7],
                    'turnover': item[8] / 10000,
                }
                for item in message.get('kline', [])
            ]
        )


class Accounts(DataStore):
    _KEYS = ['accountID', 'currency']

    def _onmessage(self, data: list[Item]) -> None:
        self._update(data)


class Orders(DataStore):
    _KEYS = ['orderID']

    def _onmessage(self, data: list[Item]) -> None:
        for item in data:
            if item['ordStatus'] == 'New':
                self._insert([item])
            elif item['ordStatus'] == 'PartiallyFilled':
                self._update([item])
            elif item['ordStatus'] == 'Filled':
                self._delete([item])
            elif item['ordStatus'] == 'Canceled' and item['action'] != 'Replace':
                self._delete([item])


class Positions(DataStore):
    _KEYS = ['accountID', 'symbol']

    def _onmessage(self, data: list[Item]) -> None:
        for item in data:
            if item['size'] == 0:
                self._delete([item])
            else:
                self._insert([item])
