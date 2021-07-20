import asyncio
import logging
from typing import Any, Awaitable, Dict, List

import aiohttp

from ..auth import Auth
from ..store import DataStore, DataStoreInterface
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class FTXDataStore(DataStoreInterface):
    def _init(self) -> None:
        self.create('ticker', datastore_class=Ticker)
        self.create('markets', datastore_class=Markets)
        self.create('trades', datastore_class=Trades)
        self.create('orderbook', datastore_class=OrderBook)
        self.create('fills', datastore_class=Fills)
        self.create('orders', datastore_class=Orders)
        self.create('positions', datastore_class=Positions)

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if resp.url.path in (
                '/api/orders',
                '/api/conditional_orders',
            ):
                self.orders._onresponse(data['result'])
            elif resp.url.path in ('/api/positions',):
                self.positions._onresponse(data['result'])
                self.positions._fetch = True

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if 'type' in msg:
            if msg['type'] == 'error':
                logger.warning(msg)
        if 'data' in msg:
            channel: str = msg['channel']
            market: str = msg['market'] if 'market' in msg else ''
            data: Any = msg['data']
            if channel == 'ticker':
                self.ticker._onmessage(market, data)
            elif channel == 'markets':
                self.markets._onmessage(data)
            elif channel == 'trades':
                self.trades._onmessage(market, data)
            elif channel == 'orderbook':
                self.orderbook._onmessage(market, data)
            elif channel == 'orderbookGrouped':
                data['action'] = msg['type']
                self.orderbook._onmessage(market, data)
            elif channel == 'fills':
                self.fills._onmessage(data)
                if self.positions._fetch:
                    asyncio.create_task(self.positions._onfills(ws._response._session))
            elif channel == 'orders':
                self.orders._onmessage(data)

    @property
    def ticker(self) -> 'Ticker':
        return self.get('ticker', Ticker)

    @property
    def markets(self) -> 'Markets':
        return self.get('markets', Markets)

    @property
    def trades(self) -> 'Trades':
        return self.get('trades', Trades)

    @property
    def orderbook(self) -> 'OrderBook':
        return self.get('orderbook', OrderBook)

    @property
    def fills(self) -> 'Fills':
        return self.get('fills', Fills)

    @property
    def orders(self) -> 'Orders':
        return self.get('orders', Orders)

    @property
    def positions(self) -> 'Positions':
        return self.get('positions', Positions)


class Ticker(DataStore):
    _KEYS = ['market']

    def _onmessage(self, market: str, item: Item) -> None:
        self._update([{'market': market, **item}])


class Markets(DataStore):
    _KEYS = ['name']

    def _onmessage(self, item: Item) -> None:
        if item['action'] == 'partial':
            self._clear()
        self._update([item['data'][k] for k in item['data']])


class Trades(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, market: str, data: List[Item]) -> None:
        for item in data:
            self._insert([{'market': market, **item}])


class OrderBook(DataStore):
    _KEYS = ['market', 'side', 'price']
    _BDSIDE = {'sell': 'asks', 'buy': 'bids'}

    def sorted(self, query: Item = {}) -> Dict[str, List[float]]:
        result = {'asks': [], 'bids': []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[self._BDSIDE[item['side']]].append([item['price'], item['size']])
        result['asks'].sort(key=lambda x: x[0])
        result['bids'].sort(key=lambda x: x[0], reverse=True)
        return result

    def _onmessage(self, market: str, data: List[Item]) -> None:
        if data['action'] == 'partial':
            result = self.find({'market': market})
            self._delete(result)
        for boardside, side in (('bids', 'buy'), ('asks', 'sell')):
            for item in data[boardside]:
                if item[1]:
                    self._update(
                        [
                            {
                                'market': market,
                                'side': side,
                                'price': item[0],
                                'size': item[1],
                            }
                        ]
                    )
                else:
                    self._delete([{'market': market, 'side': side, 'price': item[0]}])


class Fills(DataStore):
    def _onmessage(self, item: Item) -> None:
        self._insert([item])


class Orders(DataStore):
    _KEYS = ['id']

    def _onresponse(self, data: List[Item]) -> None:
        if data:
            results = self.find({'market': data[0]['market']})
            self._delete(results)
            self._update(data)

    def _onmessage(self, item: Item) -> None:
        if item['status'] != 'closed':
            self._update([item])
        else:
            self._delete([item])


class Positions(DataStore):
    _KEYS = ['future']

    def _init(self) -> None:
        self._fetch = False

    def _onresponse(self, data: List[Item]) -> None:
        self._update(data)

    async def _onfills(self, session: aiohttp.ClientSession) -> None:
        async with session.get(
            'https://ftx.com/api/positions?showAvgPrice=true', auth=Auth
        ) as resp:
            data = await resp.json()
        self._onresponse(data['result'])
