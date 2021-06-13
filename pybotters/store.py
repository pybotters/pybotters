import asyncio
import uuid
from typing import Any, cast, Dict, Hashable, Iterator, List, Optional, Tuple, Type, TypeVar

from .typedefs import Item
from .ws import ClientWebSocketResponse


class DataStore:
    _KEYS = []
    _MAXLEN = 9999

    def __init__(self, keys: List[str]=[], data: List[Item]=[]) -> None:
        self._data: Dict[uuid.UUID, Item] = {}
        self._index: Dict[int, uuid.UUID] = {}
        self._keys: Tuple[str, ...] = tuple(keys if keys else self._KEYS)
        self._events: List[asyncio.Event] = []
        self._insert(data)
        if hasattr(self, '_init'):
            getattr(self, '_init')()

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Item]:
        return iter(self._data.values())

    @staticmethod
    def _hash(item: Dict[str, Hashable]) -> int:
        return hash(tuple(item.items()))

    def _insert(self, data: List[Item]) -> None:
        if self._keys:
            for item in data:
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
                _id = uuid.uuid4()
                self._data[_id] = item
            self._sweep_without_key()
        self._set()

    def _update(self, data: List[Item]) -> None:
        if self._keys:
            for item in data:
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
                _id = uuid.uuid4()
                self._data[_id] = item
            self._sweep_without_key()
        self._set()

    def _delete(self, data: List[Item]) -> None:
        if self._keys:
            for item in data:
                try:
                    keyitem = {k: item[k] for k in self._keys}
                except KeyError:
                    pass
                else:
                    keyhash = self._hash(keyitem)
                    if keyhash in self._index:
                        del self._data[self._index[keyhash]]
                        del self._index[keyhash]
        self._set()

    def _clear(self) -> None:
        self._data.clear()
        self._index.clear()
        self._set()

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

    def find(self, query: Item={}) -> List[Item]:
        if query:
            return [item for item in self if all(k in item and query[k] == item[k] for k in query)]
        else:
            return list(self)

    def _set(self) -> None:
        for event in self._events:
            event.set()
        self._events.clear()

    async def wait(self) -> None:
        event = asyncio.Event()
        self._events.append(event)
        await event.wait()

TDataStore = TypeVar('TDataStore', bound=DataStore)

class DataStoreInterface:
    def __init__(self) -> None:
        self._stores: Dict[str, DataStore] = {}
        self._events: List[asyncio.Event] = []
        self._iscorofunc = asyncio.iscoroutinefunction(self._onmessage)
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
        keys: List[str]=[],
        data: List[Item]=[],
        datastore_class: Type[DataStore]=DataStore,
    ) -> None:
        self._stores[name] = datastore_class(keys, data)

    def get(self, name: str, type: Type[TDataStore]) -> TDataStore:
        return cast(type, self._stores.get(name))

    def _onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        print(msg)

    def onmessage(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        self._onmessage(msg, ws)
        self._set()

    def _set(self) -> None:
        for event in self._events:
            event.set()
        self._events.clear()

    async def wait(self) -> None:
        event = asyncio.Event()
        self._events.append(event)
        await event.wait()
