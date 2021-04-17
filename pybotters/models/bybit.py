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

    async def initialize(self, aws: List[Awaitable[aiohttp.ClientResponse]]):
        for f in asyncio.as_completed(aws):
            resp = await f
            if resp.status != 200:
                logger.warning(f'status code != 200 ({resp.url.scheme}://{resp.url.host}{resp.url.path})')
                continue
            data = await resp.json()
            if data['ret_code'] != 0:
                logger.warning(f'ret_code != 0 ({resp.url.scheme}://{resp.url.host}{resp.url.path}) {data}')
                continue
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
                self.orderbook._onmessage(msg['type'], data)
            elif topic.startswith('trade'):
                self.trade._onmessage(data)
            elif topic.startswith('insurance'):
                self.insurance._onmessage(data)
            elif topic.startswith('instrument_info'):
                self.instrument._onmessage(msg['type'], data)
            if any([
                topic.startswith('klineV2'),
                topic.startswith('candle'),
            ]):
                self.kline._onmessage(topic, data)
            elif topic == 'position':
                if ws._response.url.path.startswith('/realtime'):
                    self.position_inverse._onmessage(data)
                    self.wallet._onposition(data)
                elif ws._response.url.path.startswith('/realtime_private'):
                    self.position_usdt._onmessage(data)
            elif topic == 'execution':
                self.execution._onmessage(data)
            elif topic == 'order':
                self.order._onmessage(data)
            elif topic == 'stop_order':
                self.stoporder._onmessage(data)
            elif topic == 'wallet':
                self.wallet._onmessage(data)

    @property
    def orderbook(self) -> 'OrderBook':
        return self._stores.get('orderbook')

    @property
    def trade(self) -> 'Trade':
        return self._stores.get('trade')

    @property
    def insurance(self) -> 'Insurance':
        return self._stores.get('insurance')

    @property
    def instrument(self) -> 'Instrument':
        return self._stores.get('instrument')

    @property
    def kline(self) -> 'Kline':
        return self._stores.get('kline')

    @property
    def position_inverse(self) -> 'PositionInverse':
        return self._stores.get('position_inverse')

    @property
    def position_usdt(self) -> 'PositionUSDT':
        return self._stores.get('position_usdt')

    @property
    def execution(self) -> 'Execution':
        return self._stores.get('execution')

    @property
    def order(self) -> 'Order':
        return self._stores.get('order')

    @property
    def stoporder(self) -> 'StopOrder':
        return self._stores.get('stoporder')

    @property
    def wallet(self) -> 'Wallet':
        return self._stores.get('wallet')


class OrderBook(DataStore):
    _KEYS = ['symbol', 'id', 'side']

    def getbest(self, symbol: str) -> Dict[str, Optional[Item]]:
        result = {'Sell': {}, 'Buy': {}}
        for item in self._data.values():
            if item['symbol'] == symbol:
                result[item['side']][float(item['price'])] = item
        return {
            'Sell': result['Sell'][min(result['Sell'])] if result['Sell'] else None,
            'Buy': result['Buy'][max(result['Buy'])] if result['Buy'] else None
        }

    def getsorted(self, symbol: str) -> Dict[str, List[Item]]:
        result = {'Sell': [], 'Buy': []}
        for item in self._data.values():
            if item['symbol'] == symbol:
                result[item['side']].append(item)
        return {
            'Sell': sorted(result['Sell'], key=lambda x: float(x['price'])),
            'Buy': sorted(result['Buy'], key=lambda x: float(x['price']), reverse=True)
        }

    def _onmessage(self, type_: str, data: Union[List[Item], Item]) -> None:
        if type_ == 'snapshot':
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

    def _onmessage(self, type_: str, data: Item) -> None:
        if type_ == 'snapshot':
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
            _item = {}
            _item['coin'] = coin
            _item['wallet_balance'] = item['wallet_balance']
            _item['available_balance'] = item['available_balance']
            self._update([_item])

    def _onposition(self, data: List[Item]) -> None:
        for item in data:
            _item = {}
            symbol: str = item['symbol']
            if symbol.endswith('USD'):
                _item['coin'] = symbol[:-3] # ex:'BTCUSD'
            else:
                _item['coin'] = symbol[:-6] # ex:'BTCUSDM21'
            _item['wallet_balance'] = item['wallet_balance']
            _item['available_balance'] = item['available_balance']
            self._update([_item])

    def _onmessage(self, data: List[Item]) -> None:
        for item in data:
            _item = {'coin': 'USDT'}
            _item['wallet_balance'] = item['wallet_balance']
            _item['available_balance'] = item['available_balance']
            self._update([_item])
