import asyncio
from typing import Any, Awaitable, Dict, List, Optional, Union

import aiohttp

from ..auth import Auth
from ..store import DataStore, DataStoreInterface
from ..typedefs import Item
from ..ws import ClientWebSocketResponse


class BinanceDataStore(DataStoreInterface):
    def _init(self) -> None:
        self.create('trade', datastore_class=Trade)
        self.create('markprice', datastore_class=MarkPrice)
        self.create('kline', datastore_class=Kline)
        self.create('continuouskline', datastore_class=ContinuousKline)
        self.create('ticker', datastore_class=Ticker)
        self.create('bookticker', datastore_class=BookTicker)
        self.create('liquidation', datastore_class=Liquidation)
        self.create('orderbook', datastore_class=OrderBook)
        self.create('balance', datastore_class=Balance)
        self.create('position', datastore_class=Position)
        self.create('order', datastore_class=Order)
        self.listenkey: Optional[str] = None

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if resp.url.path in (
                '/fapi/v1/depth',
            ):
                self.orderbook._onresponse(resp.url.query['symbol'], data)
            elif resp.url.path in (
                '/fapi/v2/balance',
            ):
                self.balance._onresponse(data)
            elif resp.url.path in (
                '/fapi/v2/positionRisk',
            ):
                self.position._onresponse(data)
            elif resp.url.path in (
                '/fapi/v1/openOrders',
            ):
                self.order._onresponse(data)
            elif resp.url.path in (
                '/fapi/v1/listenKey',
            ):
                self.listenkey = data['listenKey']
                asyncio.create_task(self._listenkey(resp.__dict__['_raw_session']))

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if 'stream' in msg:
            data = msg['data']
        else:
            data = msg
        event: str = data['e'] if not isinstance(data, list) else data[0]['e']
        if event in ('trade', 'aggTrade'):
            self.trade._onmessage(data)
        elif event == 'markPriceUpdate':
            self.markprice._onmessage(data)
        elif event == 'bookTicker':
            self.bookticker._onmessage(data)
        elif event == 'kline':
            self.kline._onmessage(data)
        elif event == 'continuous_kline':
            self.continuouskline._onmessage(data)
        elif event in ('24hrMiniTicker', '24hrTicker'):
            self.ticker._onmessage(data)
        elif event == 'bookTicker':
            self.bookticker._onmessage(data)
        elif event == 'forceOrder':
            self.liquidation._onmessage(data)
        elif event == 'depthUpdate':
            self.orderbook._onmessage(data)
        elif event == 'ACCOUNT_UPDATE':
            self.balance._onmessage(data)
            self.position._onmessage(data)
        elif event == 'ORDER_TRADE_UPDATE':
            self.order._onmessage(data)

    @staticmethod
    async def _listenkey(session: aiohttp.ClientSession):
        while not session.closed:
            await session.put('https://fapi.binance.com/fapi/v1/listenKey', auth=Auth)
            await asyncio.sleep(1800.0) # 30 minutes

    @property
    def trade(self) -> 'Trade':
        return self.get('trade', Trade)

    @property
    def markprice(self) -> 'MarkPrice':
        return self.get('markprice', MarkPrice)

    @property
    def kline(self) -> 'Kline':
        return self.get('kline', Kline)

    @property
    def continuouskline(self) -> 'ContinuousKline':
        return self.get('continuouskline', ContinuousKline)

    @property
    def ticker(self) -> 'Ticker':
        return self.get('ticker', Ticker)

    @property
    def bookticker(self) -> 'BookTicker':
        return self.get('bookticker', BookTicker)

    @property
    def liquidation(self) -> 'Liquidation':
        return self.get('liquidation', Liquidation)

    @property
    def orderbook(self) -> 'OrderBook':
        return self.get('orderbook', OrderBook)

    @property
    def balance(self) -> 'Balance':
        return self.get('balance', Balance)

    @property
    def position(self) -> 'Position':
        return self.get('position', Position)

    @property
    def order(self) -> 'Order':
        return self.get('order', Order)


class Trade(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, item: Item) -> None:
        self._insert([item])


class MarkPrice(DataStore):
    _KEYS = ['s']

    def _onmessage(self, data: Union[Item, List[Item]]) -> None:
        if isinstance(data, list):
            self._update(data)
        else:
            self._update([data])


class Kline(DataStore):
    _KEYS = ['t', 's', 'i']

    def _onmessage(self, item: Item) -> None:
        self._update([item['k']])


class ContinuousKline(DataStore):
    _KEYS = ['ps', 'ct', 't', 'i']

    def _onmessage(self, item: Item) -> None:
        self._update([{'ps': item['ps'], 'ct': item['ct'], **item['k']}])


class Ticker(DataStore):
    _KEYS = ['s']

    def _onmessage(self, data: Union[Item, List[Item]]) -> None:
        if isinstance(data, list):
            self._update(data)
        else:
            self._update([data])


class BookTicker(DataStore):
    _KEYS = ['s']

    def _onmessage(self, item: Item) -> None:
        self._update([item])


class Liquidation(DataStore):
    def _onmessage(self, item: Item) -> None:
        self._insert([item['o']])


class OrderBook(DataStore):
    _KEYS = ['s', 'S', 'p']
    _MAPSIDE = {'BUY': 'b', 'SELL': 'a'}

    def sorted(self, query: Item={}) -> Dict[str, List[float]]:
        result = {self._MAPSIDE[k]: [] for k in self._MAPSIDE}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[self._MAPSIDE[item['S']]].append([item['p'], item['q']])
        result['b'].sort(key=lambda x: float(x[0]), reverse=True)
        result['a'].sort(key=lambda x: float(x[0]))
        return result

    def _onmessage(self, item: Item) -> None:
        for s, bs in self._MAPSIDE.items():
            for row in item[bs]:
                if float(row[1]) != 0.0:
                    self._update([{'s': item['s'], 'S': s, 'p': row[0], 'q': row[1]}])
                else:
                    self._delete([{'s': item['s'], 'S': s, 'p': row[0]}])

    def _onresponse(self, symbol: str, item: Item) -> None:
        for s, bs in (('BUY', 'bids'), ('SELL', 'asks')):
            for row in item[bs]:
                self._update([{'s': symbol, 'S': s, 'p': row[0], 'q': row[1]}])


class Balance(DataStore):
    _KEYS = ['a']

    def _onmessage(self, item: Item) -> None:
        self._update(item['a']['B'])

    def _onresponse(self, data: List[Item]) -> None:
        data_short = []
        for item in data:
            data_short.append({
                'a': item['asset'],
                'wb': item['balance'],
                'cw': item['crossWalletBalance'],
            })
        self._update(data_short)


class Position(DataStore):
    _KEYS = ['s', 'ps']

    def _onmessage(self, item: Item) -> None:
        self._update(item['a']['P'])

    def _onresponse(self, data: List[Item]) -> None:
        for item in data:
            self._update([{
                's': item['symbol'],
                'pa': item['positionAmt'],
                'ep': item['entryPrice'],
                'mt': item['marginType'],
                'iw': item['isolatedWallet'],
                'ps': item['positionSide'],
            }])


class Order(DataStore):
    _KEYS = ['s', 'i']

    def _onmessage(self, item: Item) -> None:
        if item['o']['X'] not in ('FILLED', 'CANCELED', 'EXPIRED'):
            self._update([item['o']])
        else:
            self._delete([item['o']])

    def _onresponse(self, data: List[Item]) -> None:
        data_short = []
        for item in data:
            data_short.append({
                's': item['symbol'],
                'c': item['clientOrderId'],
                'S': item['side'],
                'o': item['type'],
                'f': item['timeInForce'],
                'q': item['origQty'],
                'p': item['price'],
                'ap': item['avgPrice'],
                'sp': item['stopPrice'],
                'X': item['status'],
                'i': item['orderId'],
                'z': item['executedQty'],
                'T': item['updateTime'],
                'R': item['reduceOnly'],
                'wt': item['workingType'],
                'ot': item['origType'],
                'ps': item['positionSide'],
                'cp': item['closePosition'],
                'pP': item['priceProtect'],
            })
        self._update(data_short)
