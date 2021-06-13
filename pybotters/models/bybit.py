import asyncio
import logging
from typing import Any, Awaitable, Dict, List, Optional, Union

import aiohttp

from ..store import DataStore, DataStoreInterface
from ..typedefs import Item
from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


class BybitDataStore(DataStoreInterface):
    def _init(self) -> None:
        self.create('orderbook', datastore_class=OrderBook)
        self.create('trade', datastore_class=Trade)
        self.create('insurance', datastore_class=Insurance)
        self.create('instrument', datastore_class=Instrument)
        self.create('kline', datastore_class=Kline)
        self.create('position_inverse', datastore_class=PositionInverse)
        self.create('position_usdt', datastore_class=PositionUSDT)
        self.create('execution', datastore_class=Execution)
        self.create('order', datastore_class=Order)
        self.create('stoporder', datastore_class=StopOrder)
        self.create('wallet', datastore_class=Wallet)
        self.timestamp_e6: Optional[int] = None

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        for f in asyncio.as_completed(aws):
            resp = await f
            data = await resp.json()
            if resp.url.path in (
                '/v2/private/order',
                '/private/linear/order/search',
                '/futures/private/order',
            ):
                self.order._onresponse(data['result'])
            elif resp.url.path in (
                '/v2/private/stop-order',
                '/private/linear/stop-order/search',
                '/futures/private/stop-order'
            ):
                self.stoporder._onresponse(data['result'])
            elif resp.url.path in (
                '/v2/private/position/list',
                '/futures/private/position/list',
            ):
                self.position_inverse._onresponse(data['result'])
            elif resp.url.path in (
                '/private/linear/position/list',
            ):
                self.position_usdt._onresponse(data['result'])
            elif resp.url.path in (
                '/v2/private/wallet/balance',
            ):
                self.wallet._onresponse(data['result'])

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if 'topic' in msg:
            topic: str = msg['topic']
            data: Any = msg['data']
            if any([
                topic.startswith('orderBookL2_25'),
                topic.startswith('orderBook_200'),
            ]):
                self.orderbook._onmessage(topic, msg['type'], data)
            elif topic.startswith('trade'):
                self.trade._onmessage(data)
            elif topic.startswith('insurance'):
                self.insurance._onmessage(data)
            elif topic.startswith('instrument_info'):
                self.instrument._onmessage(topic, msg['type'], data)
            if any([
                topic.startswith('klineV2'),
                topic.startswith('candle'),
            ]):
                self.kline._onmessage(topic, data)
            elif topic == 'position':
                if ws._response.url.path == '/realtime':
                    self.position_inverse._onmessage(data)
                    self.wallet._onposition(data)
                elif ws._response.url.path == '/realtime_private':
                    self.position_usdt._onmessage(data)
            elif topic == 'execution':
                self.execution._onmessage(data)
            elif topic == 'order':
                self.order._onmessage(data)
            elif topic == 'stop_order':
                self.stoporder._onmessage(data)
            elif topic == 'wallet':
                self.wallet._onmessage(data)
        if 'timestamp_e6' in msg:
            self.timestamp_e6 = int(msg['timestamp_e6'])

    @property
    def orderbook(self) -> 'OrderBook':
        return self.get('orderbook', OrderBook)

    @property
    def trade(self) -> 'Trade':
        return self.get('trade', Trade)

    @property
    def insurance(self) -> 'Insurance':
        return self.get('insurance', Insurance)

    @property
    def instrument(self) -> 'Instrument':
        return self.get('instrument', Instrument)

    @property
    def kline(self) -> 'Kline':
        return self.get('kline', Kline)

    @property
    def position_inverse(self) -> 'PositionInverse':
        return self.get('position_inverse', PositionInverse)

    @property
    def position_usdt(self) -> 'PositionUSDT':
        return self.get('position_usdt', PositionUSDT)

    @property
    def execution(self) -> 'Execution':
        return self.get('execution', Execution)

    @property
    def order(self) -> 'Order':
        return self.get('order', Order)

    @property
    def stoporder(self) -> 'StopOrder':
        return self.get('stoporder', StopOrder)

    @property
    def wallet(self) -> 'Wallet':
        return self.get('wallet', Wallet)


class OrderBook(DataStore):
    _KEYS = ['symbol', 'id', 'side']

    def sorted(self, query: Item={}) -> Dict[str, List[Item]]:
        result = {'Sell': [], 'Buy': []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item['side']].append(item)
        result['Sell'].sort(key=lambda x: x['id'])
        result['Buy'].sort(key=lambda x: x['id'], reverse=True)
        return result

    def _onmessage(self, topic: str, type_: str, data: Union[List[Item], Item]) -> None:
        if type_ == 'snapshot':
            symbol = topic.split('.')[-1] # ex: 'orderBookL2_25.BTCUSD'
            result = self.find({'symbol': symbol})
            self._delete(result)
            if isinstance(data, dict):
                data = data['order_book']
            self._insert(data)
        elif type_ == 'delta':
            self._delete(data['delete'])
            self._update(data['update'])
            self._insert(data['insert'])

class Trade(DataStore):
    _KEYS = ['trade_id']
    _MAXLEN = 99999

    def _onmessage(self, data: List[Item]) -> None:
        self._insert(data)

class Insurance(DataStore):
    _KEYS = ['currency']

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)

class Instrument(DataStore):
    _KEYS = ['symbol']

    def _onmessage(self, topic: str, type_: str, data: Item) -> None:
        if type_ == 'snapshot':
            symbol = topic.split('.')[-1] # ex: 'instrument_info.100ms.BTCUSD'
            result = self.find({'symbol': symbol})
            self._delete(result)
            self._insert([data])
        elif type_ == 'delta':
            self._update(data['update'])

class Kline(DataStore):
    _KEYS = ['symbol', 'start']

    def _onmessage(self, topic: str, data: List[Item]) -> None:
        symbol = topic.split('.')[2] # ex:'klineV2.1.BTCUSD'
        for item in data:
            item['symbol'] = symbol
        self._update(data)

class PositionInverse(DataStore):
    _KEYS = ['symbol', 'position_idx']
    
    def getone(self, symbol: str) -> Optional[Item]:
        return self.get({'symbol': symbol, 'position_idx': 0})

    def getboth(self, symbol: str) -> Dict[str, Optional[Item]]:
        return {
            'Sell': self.get({'symbol': symbol, 'position_idx': 2}),
            'Buy': self.get({'symbol': symbol, 'position_idx': 1}),
        }

    def _onresponse(self, data: Union[Item, List[Item]]) -> None:
        if isinstance(data, dict):
            self._update([data])
        elif isinstance(data, list):
            if len(data):
                if 'data' in data[0]:
                    self._update([item['data'] for item in data])
                else:
                    self._update(data)

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)

class PositionUSDT(DataStore):
    _KEYS = ['symbol', 'side']

    def getboth(self, symbol: str) -> Dict[str, Optional[Item]]:
        return {
            'Sell': self.get({'symbol': symbol, 'side': 'Sell'}),
            'Buy': self.get({'symbol': symbol, 'side': 'Buy'}),
        }

    def _onresponse(self, data: List[Item]) -> None:
        if len(data):
            if 'data' in data[0]:
                self._update([item['data'] for item in data])
            else:
                self._update(data)

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)

class Execution(DataStore):
    _KEYS = ['exec_id']

    def _onmessage(self, data: List[Item]) -> None:
        self._update(data)

class Order(DataStore):
    _KEYS = ['order_id']

    def _onresponse(self, data: List[Item]) -> None:
        if isinstance(data, list):
            self._update(data)
        elif isinstance(data, dict):
            self._update([data])

    def _onmessage(self, data: List[Item]) -> None:
        for item in data:
            if item['order_status'] in ('Created', 'New', 'PartiallyFilled'):
                self._update([item])
            else:
                self._delete([item])

class StopOrder(DataStore):
    _KEYS = ['stop_order_id']

    def _onresponse(self, data: List[Item]) -> None:
        if isinstance(data, list):
            self._clear()
            self._update(data)
        elif isinstance(data, dict):
            self._update([data])

    def _onresponse(self, data: List[Item]) -> None:
        self._clear()
        self._update(data)

    def _onmessage(self, data: List[Item]) -> None:
        for item in data:
            if 'order_id' in item:
                item['stop_order_id'] = item.pop('order_id')
            if 'order_status' in item:
                item['stop_order_status'] = item.pop('order_status')
            if item['stop_order_status'] in ('Active', 'Untriggered'):
                self._update([item])
            else:
                self._delete([item])

class Wallet(DataStore):
    _KEYS = ['coin']

    def _onresponse(self, data: Dict[str, Item]) -> None:
        for coin, item in data.items():
            self._update([{
                'coin': coin,
                'wallet_balance': item['wallet_balance'],
                'available_balance': item['available_balance'],
            }])

    def _onposition(self, data: List[Item]) -> None:
        for item in data:
            symbol: str = item['symbol']
            if symbol.endswith('USD'):
                coin = symbol[:-3] # ex: BTCUSD
            else:
                coin = symbol[:-6] # ex: BTCUSDU21
            self._update([{
                'coin': coin,
                'wallet_balance': item['wallet_balance'],
                'available_balance': item['available_balance'],
            }])

    def _onmessage(self, data: List[Item]) -> None:
        for item in data:
            self._update([{
                'coin': 'USDT',
                'wallet_balance': item['wallet_balance'],
                'available_balance': item['available_balance'],
            }])
