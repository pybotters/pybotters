import asyncio
import uuid
from typing import Any, Dict, Generator, Hashable, Iterator, List, Optional, Tuple

from .ws import ClientWebSocketResponse


class DataStoreInterface:
    def __init__(self) -> None:
        self._stores: Dict[str, DataStore] = {}
        self._events: List[asyncio.Event] = []
        self._iscorofunc = asyncio.iscoroutinefunction(self._on_message)

    def __getitem__(self, name: str) -> Optional['DataStore']:
        return self._stores[name]

    def __contains__(self, name: str) -> bool:
        return name in self._stores

    def create(self, name: str, *, keys: List[str]=[], data: List[Dict[str, Any]]=[]) -> None:
        self._stores[name] = DataStore(keys, data)

    def _on_message(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        print(msg)
        self._set()

    async def on_message(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if self._iscorofunc:
            await self._on_message(msg, ws)
        else:
            self._on_message(msg, ws)
        self._set()

    def _set(self) -> None:
        for event in self._events:
            event.set()
        self._events.clear()

    async def wait(self) -> None:
        event = asyncio.Event()
        self._events.append(event)
        await event.wait()


class DataStore:
    _MAXLEN = 9999

    def __init__(self, keys: List[str]=[], data: List[Dict[str, Any]]=[]) -> None:
        self._data: Dict[uuid.UUID, Dict[str, Any]] = {}
        self._index: Dict[int, uuid.UUID] = {}
        self._keys: Tuple[str, ...] = tuple(keys)
        self._events: List[asyncio.Event] = []
        self.insert(data)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return iter(self._data.values())

    @staticmethod
    def _hash(item: Dict[str, Hashable]) -> int:
        return hash(tuple(item.items()))

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
                del self._index[k]

    def insert(self, data: List[Dict[str, Any]]) -> None:
        if self._keys:
            for item in data:
                try:
                    keyitem = {k: item[k] for k in self._keys}
                except KeyError:
                    pass
                else:
                    keyhash = self._hash(keyitem)
                    _id = uuid.uuid4()
                    self._data[_id] = item
                    self._index[keyhash] = _id
            self._sweep_with_key()
        else:
            for item in data:
                _id = uuid.uuid4()
                self._data[_id] = item
            self._sweep_without_key()

    def update(self, data: List[Dict[str, Any]]) -> None:
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

    def delete(self, data: List[Dict[str, Any]]) -> None:
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

    def clear(self) -> None:
        self._data.clear()
        self._index.clear()

    def get(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self._keys:
            try:
                keyitem = {k: item[k] for k in self._keys}
            except KeyError:
                pass
            else:
                keyhash = self._hash(keyitem)
                if keyhash in self._index:
                    return self._data[self._index[keyhash]]

    def find(self, query: Dict[str, Any]={}) -> Generator[Dict[str, Any], None, None]:
        if query:
            return (item for item in self._data.values() if all(k in item and query[k] == item[k] for k in query))
        else:
            return (item for item in self._data.values())

    def _set(self) -> None:
        for event in self._events:
            event.set()
        self._events.clear()

    async def wait(self) -> None:
        event = asyncio.Event()
        self._events.append(event)
        await event.wait()
