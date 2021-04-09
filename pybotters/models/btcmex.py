from typing import Any, Dict, List, Optional, Union

from ..store import DataStore, DataStoreInterface
from ..typedefs import Item
from ..ws import ClientWebSocketResponse


class BTCMEXDataStore(DataStoreInterface):
    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        if 'table' in msg:
            table = msg['table']
            if table == 'orderBookL2_25':
                table = 'orderBookL2'
            action = msg['action']
            data = msg['data']
            if action == 'partial':
                self.create(table, keys=msg['keys'], data=data)
                if table == 'trade':
                    self['trade']._MAXLEN = 99999
            elif action == 'insert':
                if table in self:
                    self[table]._insert(data)
            elif action == 'update':
                if table in self:
                    self[table]._update(data)
            elif action == 'delete':
                if table in self:
                    self[table]._delete(data)
            if table == 'order':
                if 'order' in self:
                    self['order']._delete([order for order in self['order'].find() if order['ordStatus'] in ('Filled', 'Canceled')])

    @property
    def orderbook(self) -> DataStore:
        return self._stores.get('orderBookL2')  

    @property
    def trade(self) -> DataStore:
        return self._stores.get('trade')

    @property
    def instrument(self) -> DataStore:
        return self._stores.get('instrument')

    @property
    def liquidation(self) -> DataStore:
        return self._stores.get('liquidation')

    @property
    def quote(self) -> DataStore:
        return self._stores.get('quote')

    @property
    def order(self) -> DataStore:
        return self._stores.get('order')

    @property
    def execution(self) -> DataStore:
        return self._stores.get('execution')

    @property
    def position(self) -> DataStore:
        return self._stores.get('position')

    @property
    def margin(self) -> DataStore:
        return self._stores.get('margin')

    @property
    def positionparam(self) -> DataStore:
        return self._stores.get('positionParam')

    @property
    def clientrisklimit(self) -> DataStore:
        return self._stores.get('clientRiskLimit')

    @property
    def fundsandbonus(self) -> DataStore:
        return self._stores.get('fundsAndBonus')

    @property
    def positionautocloseinfo(self) -> DataStore:
        return self._stores.get('positionAutoCloseInfo')
