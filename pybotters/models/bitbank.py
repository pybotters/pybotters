import json
from typing import Dict, List

from ..store import DataStore, DataStoreInterface
from ..typedefs import Item
from ..ws import ClientWebSocketResponse


class bitbankDataStore(DataStoreInterface):
    def _init(self) -> None:
        self.create('transactions', datastore_class=Transactions)
        self.create('depth', datastore_class=Depth)
        self.create('ticker', datastore_class=Ticker)

    def _onmessage(self, msg: str, ws: ClientWebSocketResponse) -> None:
        if msg.startswith('42'):
            data_json = json.loads(msg[2:])
            room_name = data_json[1]['room_name']
            data = data_json[1]['message']['data']
            if 'transactions' in room_name:
                self.transactions._onmessage(room_name, data)
            elif 'depth' in room_name:
                self.depth._onmessage(room_name, data)
            elif 'ticker' in room_name:
                self.ticker._onmessage(room_name, data)

    @property
    def transactions(self) -> 'Transactions':
        return self.get('transactions', Transactions)

    @property
    def depth(self) -> 'Depth':
        return self.get('depth', Depth)

    @property
    def ticker(self) -> 'Ticker':
        return self.get('ticker', Ticker)


class Transactions(DataStore):
    _MAXLEN = 99999

    def _onmessage(self, room_name: str, data: List[Item]) -> None:
        data = data['transactions']
        for item in data:
            pair = room_name.replace('transactions_', '')
            self._insert([{'pair': pair, **item}])


class Depth(DataStore):
    _KEYS = ['pair', 'side', 'price']
    _BDSIDE = {'sell': 'asks', 'buy': 'bids'}

    def sorted(self, query: Item = {}) -> Dict[str, List[float]]:
        result = {'asks': [], 'bids': []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[self._BDSIDE[item['side']]].append([item['price'], item['size']])
        result['asks'].sort(key=lambda x: x[0])
        result['bids'].sort(key=lambda x: x[0], reverse=True)
        return result

    def _onmessage(self, room_name: str, data: List[Item]) -> None:
        if 'whole' in room_name:
            pair = room_name.replace('depth_whole_', '')
            result = self.find({'pair': pair})
            self._delete(result)
            tuples = (('bids', 'buy'), ('asks', 'sell'))
        else:
            pair = room_name.replace('depth_diff_', '')
            tuples = (('b', 'buy'), ('a', 'sell'))

        for boardside, side in tuples:
            for item in data[boardside]:
                if item[1] != '0':
                    self._update(
                        [
                            {
                                'pair': pair,
                                'side': side,
                                'price': item[0],
                                'size': item[1],
                            }
                        ]
                    )
                else:
                    self._delete([{'pair': pair, 'side': side, 'price': item[0]}])


class Ticker(DataStore):
    _KEYS = ['pair']

    def _onmessage(self, room_name: str, item: Item) -> None:
        pair = room_name.replace('ticker_', '')
        self._insert([{'pair': pair, **item}])
