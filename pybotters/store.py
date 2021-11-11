from __future__ import annotations

import asyncio
import uuid
from typing import Any, Hashable, Iterator, Optional, Type, TypeVar, cast

from .typedefs import Item
from .ws import ClientWebSocketResponse


class DataStore:
    _KEYS = []
    _MAXLEN = 9999

    def __init__(
        self,
        keys: Optional[list[str]] = None,
        data: Optional[list[Item]] = None,
        *,
        auto_cast: bool = False,
    ) -> None:
        self._data: dict[uuid.UUID, Item] = {}
        self._index: dict[int, uuid.UUID] = {}
        self._keys: tuple[str, ...] = tuple(keys if keys else self._KEYS)
        self._events: dict[asyncio.Event, list[Item]] = {}
        self._auto_cast = auto_cast
        if data is None:
            data = []
        self._insert(data)
        if hasattr(self, '_init'):
            getattr(self, '_init')()

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Item]:
        return iter(self._data.values())

    @staticmethod
    def _hash(item: dict[str, Hashable]) -> int:
        return hash(tuple(item.items()))

    @staticmethod
    def _cast_item(item: dict[str, Hashable]) -> None:
        for k in item:
            if isinstance(item[k], str):
                try:
                    item[k] = int(item[k])
                except ValueError:
                    try:
                        item[k] = float(item[k])
                    except ValueError:
                        pass

    def _insert(self, data: list[Item]) -> None:
        if self._keys:
            for item in data:
                if self._auto_cast:
                    self._cast_item(item)
                try:
                    keyitem = {k: item[k] for k in self._keys}
                except KeyError:
                    pass
                else:
                    keyhash = self._hash(keyitem)
                    if keyhash not in self._index:
                        _id = uuid.uuid4()
                        self._data[_id] = item
                        self._index[keyhash] = _id
                    else:
                        self._data[self._index[keyhash]] = item
            self._sweep_with_key()
        else:
            for item in data:
                if self._auto_cast:
                    self._cast_item(item)
                _id = uuid.uuid4()
                self._data[_id] = item
            self._sweep_without_key()
        # !TODO! This behaviour might be undesirable.
        self._set(data)

    def _update(self, data: list[Item]) -> None:
        if self._keys:
            for item in data:
                if self._auto_cast:
                    self._cast_item(item)
                try:
                    keyitem = {k: item[k] for k in self._keys}
                except KeyError:
                    pass
                else:
                    keyhash = self._hash(keyitem)
                    if keyhash in self._index:
                        self._data[self._index[keyhash]].update(item)
                    else:
                        _id = uuid.uuid4()
                        self._data[_id] = item
                        self._index[keyhash] = _id
            self._sweep_with_key()
        else:
            for item in data:
                if self._auto_cast:
                    self._cast_item(item)
                _id = uuid.uuid4()
                self._data[_id] = item
            self._sweep_without_key()
        # !TODO! This behaviour might be undesirable.
        self._set(data)

    def _delete(self, data: list[Item]) -> None:
        if self._keys:
            for item in data:
                if self._auto_cast:
                    self._cast_item(item)
                try:
                    keyitem = {k: item[k] for k in self._keys}
                except KeyError:
                    pass
                else:
                    keyhash = self._hash(keyitem)
                    if keyhash in self._index:
                        del self._data[self._index[keyhash]]
                        del self._index[keyhash]
        # !TODO! This behaviour might be undesirable.
        self._set(data)

    def _remove(self, uuids: list[uuid.UUID]) -> None:
        if self._keys:
            for _id in uuids:
                if _id in self._data:
                    item = self._data[_id]
                    keyhash = self._hash({k: item[k] for k in self._keys})
                    del self._data[_id]
                    del self._index[keyhash]
        else:
            for _id in uuids:
                if _id in self._data:
                    del self._data[_id]
        # !TODO! This behaviour might be undesirable.
        self._set([])

    def _clear(self) -> None:
        self._data.clear()
        self._index.clear()
        self._set([])

    def _sweep_with_key(self) -> None:
        if len(self._data) > self._MAXLEN:
            over = len(self._data) - self._MAXLEN
            _iter = iter(self._index)
            keys = [next(_iter) for _ in range(over)]
            for k in keys:
                del self._data[self._index[k]]
                del self._index[k]

    def _sweep_without_key(self) -> None:
        if len(self._data) > self._MAXLEN:
            over = len(self._data) - self._MAXLEN
            _iter = iter(self._data)
            keys = [next(_iter) for _ in range(over)]
            for k in keys:
                del self._data[k]

    def get(self, item: Item) -> Optional[Item]:
        if self._keys:
            try:
                keyitem = {k: item[k] for k in self._keys}
            except KeyError:
                pass
            else:
                keyhash = self._hash(keyitem)
                if keyhash in self._index:
                    return self._data[self._index[keyhash]]

    def _pop(self, item: Item) -> Optional[Item]:
        if self._keys:
            try:
                keyitem = {k: item[k] for k in self._keys}
            except KeyError:
                pass
            else:
                keyhash = self._hash(keyitem)
                if keyhash in self._index:
                    ret = self._data[self._index[keyhash]]
                    del self._data[self._index[keyhash]]
                    del self._index[keyhash]
                    return ret

    def find(self, query: Optional[Item] = None) -> list[Item]:
        if query:
            return [
                item
                for item in self
                if all(k in item and query[k] == item[k] for k in query)
            ]
        else:
            return list(self)

    def _find_with_uuid(self, query: Optional[Item] = None) -> dict[uuid.UUID, Item]:
        if query is None:
            query = {}
        if query:
            return {
                _id: item
                for _id, item in self._data.items()
                if all(k in item and query[k] == item[k] for k in query)
            }
        else:
            return self._data

    def _find_and_delete(self, query: Optional[Item] = None) -> list[Item]:
        if query is None:
            query = {}
        if query:
            ret = [
                item
                for item in self
                if all(k in item and query[k] == item[k] for k in query)
            ]
            self._delete(ret)
            return ret
        else:
            ret = list(self)
            self._clear()
            return ret

    def _set(self, data: Optional[list[Item]] = None) -> None:
        if data is None:
            data = []
        for event in self._events:
            event.set()
            self._events[event].extend(data)

    async def wait(self) -> list[Item]:
        event = asyncio.Event()
        ret = []
        self._events[event] = ret
        await event.wait()
        del self._events[event]
        return ret


TDataStore = TypeVar('TDataStore', bound=DataStore)


class DataStoreManager:
    """
    データストアマネージャーの抽象クラスです。 データストアの作成・参照・ハンドリングなどの役割を持ちます。 それぞれの取引所のクラスが継承します。
    """

    def __init__(self, auto_cast: bool = False) -> None:
        self._stores: dict[str, DataStore] = {}
        self._events: list[asyncio.Event] = []
        self._iscorofunc = asyncio.iscoroutinefunction(self._onmessage)
        self._auto_cast = auto_cast
        if hasattr(self, '_init'):
            getattr(self, '_init')()

    def __getitem__(self, name: str) -> Optional['DataStore']:
        return self._stores[name]

    def __contains__(self, name: str) -> bool:
        return name in self._stores

    def create(
        self,
        name: str,
        *,
        keys: Optional[list[str]] = None,
        data: Optional[list[Item]] = None,
        datastore_class: Type[DataStore] = DataStore,
    ) -> None:
        if keys is None:
            keys = []
        if data is None:
            data = []
        self._stores[name] = datastore_class(keys, data, auto_cast=self._auto_cast)

    def get(self, name: str, type: Type[TDataStore]) -> TDataStore:
        return cast(type, self._stores.get(name))

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        print(msg)

    def onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        """
        Clientクラスws_connectメソッドの引数send_jsonに渡すハンドラです。
        """
        self._onmessage(msg, ws)
        self._set()

    def _set(self) -> None:
        for event in self._events:
            event.set()
        self._events.clear()

    async def wait(self) -> None:
        """
        非同期メソッド。onmessageのイベントがあるまで待機します。
        """
        event = asyncio.Event()
        self._events.append(event)
        await event.wait()
