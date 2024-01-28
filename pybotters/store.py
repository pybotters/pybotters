from __future__ import annotations

import asyncio
import copy
import uuid
from dataclasses import dataclass
from typing import Any, Hashable, Iterator, Type, TypeVar, cast

from .typedefs import Item
from .ws import ClientWebSocketResponse


class DataStore:
    _KEYS = []
    _MAXLEN = 9999

    def __init__(
        self,
        name: str | None = None,
        keys: list[str] | None = None,
        data: list[Item] | None = None,
    ) -> None:
        self.name: str = name
        self._data: dict[uuid.UUID, Item] = {}
        self._index: dict[int, uuid.UUID] = {}
        self._keys: tuple[str, ...] = tuple(keys if keys else self._KEYS)
        self._events: list[asyncio.Event] = []
        self._queues: list[asyncio.Queue] = []
        if data is None:
            data = []
        self._insert(data)
        if hasattr(self, "_init"):
            getattr(self, "_init")()

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Item]:
        return iter(self._data.values())

    def __reversed__(self) -> Iterator[Item]:
        return reversed(self._data.values())

    @staticmethod
    def _hash(item: dict[str, Hashable]) -> int:
        return hash(tuple(item.items()))

    def _insert(self, data: list[Item]) -> None:
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
                        self._put("insert", None, item)
                    else:
                        self._data[self._index[keyhash]] = item
                        self._put("insert", None, item)
            self._sweep_with_key()
        else:
            for item in data:
                _id = uuid.uuid4()
                self._data[_id] = item
                self._put("insert", None, item)
            self._sweep_without_key()
        self._set()

    def _update(self, data: list[Item]) -> None:
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
                        self._put("update", item, self._data[self._index[keyhash]])
                    else:
                        _id = uuid.uuid4()
                        self._data[_id] = item
                        self._index[keyhash] = _id
                        self._put("update", None, item)
            self._sweep_with_key()
        else:
            for item in data:
                _id = uuid.uuid4()
                self._data[_id] = item
                self._put("update", None, item)
            self._sweep_without_key()
        self._set()

    def _delete(self, data: list[Item]) -> None:
        if self._keys:
            for item in data:
                try:
                    keyitem = {k: item[k] for k in self._keys}
                except KeyError:
                    pass
                else:
                    keyhash = self._hash(keyitem)
                    if keyhash in self._index:
                        self._put("delete", item, self._data[self._index[keyhash]])
                        del self._data[self._index[keyhash]]
                        del self._index[keyhash]
        self._set()

    def _remove(self, uuids: list[uuid.UUID]) -> None:
        if self._keys:
            for _id in uuids:
                if _id in self._data:
                    item = self._data[_id]
                    keyhash = self._hash({k: item[k] for k in self._keys})
                    self._put("delete", None, self._data[_id])
                    del self._data[_id]
                    del self._index[keyhash]
        else:
            for _id in uuids:
                if _id in self._data:
                    self._put("delete", None, self._data[_id])
                    del self._data[_id]
        self._set()

    def _clear(self) -> None:
        for item in self:
            self._put("delete", None, item)
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

    def get(self, item: Item) -> Item | None:
        if self._keys:
            try:
                keyitem = {k: item[k] for k in self._keys}
            except KeyError:
                pass
            else:
                keyhash = self._hash(keyitem)
                if keyhash in self._index:
                    return self._data[self._index[keyhash]]

    def _pop(self, item: Item) -> Item | None:
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

    def find(self, query: Item | None = None) -> list[Item]:
        if query:
            return [
                item
                for item in self
                if all(k in item and query[k] == item[k] for k in query)
            ]
        else:
            return list(self)

    def _find_with_uuid(self, query: Item | None = None) -> dict[uuid.UUID, Item]:
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

    def _find_and_delete(self, query: Item | None = None) -> list[Item]:
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

    def _sorted(
        self,
        item_key: str,
        item_asc_key: str,
        item_desc_key: str,
        sort_key: str,
        query: Item | None = None,
        limit: int | None = None,
    ) -> dict[str, list[float]]:
        if query is None:
            query = {}

        result = {item_asc_key: [], item_desc_key: []}

        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item[item_key]].append(item)

        result[item_asc_key].sort(key=lambda x: float(x[sort_key]))
        result[item_desc_key].sort(key=lambda x: float(x[sort_key]), reverse=True)

        if limit:
            result[item_asc_key] = result[item_asc_key][:limit]
            result[item_desc_key] = result[item_desc_key][:limit]

        return result

    def _set(self) -> None:
        for event in self._events:
            event.set()
        self._events.clear()

    async def wait(self) -> None:
        event = asyncio.Event()
        self._events.append(event)
        await event.wait()

    def _put(self, operation: str, source: Item | None, item: Item) -> None:
        for queue in self._queues:
            queue.put_nowait(
                StoreChange(self, operation, copy.deepcopy(source), copy.deepcopy(item))
            )

    def watch(self) -> "StoreStream":
        return StoreStream(self)


TDataStore = TypeVar("TDataStore", bound=DataStore)


@dataclass
class StoreChange:
    store: DataStore
    operation: str
    source: Item | None
    data: Item


class StoreStream:
    def __init__(self, store: "DataStore") -> None:
        self._queue = asyncio.Queue()
        store._queues.append(self._queue)
        self._store = store

    async def get(self) -> StoreChange:
        return await self._queue.get()

    def close(self):
        self._store._queues.remove(self._queue)

    def __enter__(self) -> "StoreStream":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __aiter__(self) -> "StoreStream":
        return self

    async def __anext__(self) -> StoreChange:
        return await self.get()


class DataStoreManager:
    """
    データストアマネージャーの抽象クラスです。 データストアの作成・参照・ハンドリングなどの役割を持ちます。 それぞれの取引所のクラスが継承します。
    """

    def __init__(self) -> None:
        self._stores: dict[str, DataStore] = {}
        self._events: list[asyncio.Event] = []
        self._iscorofunc = asyncio.iscoroutinefunction(self._onmessage)
        if hasattr(self, "_init"):
            getattr(self, "_init")()

    def __getitem__(self, name: str) -> DataStore | None:
        return self._stores[name]

    def __contains__(self, name: str) -> bool:
        return name in self._stores

    def create(
        self,
        name: str,
        *,
        keys: list[str] | None = None,
        data: list[Item] | None = None,
        datastore_class: Type[DataStore] = DataStore,
    ) -> None:
        if keys is None:
            keys = []
        if data is None:
            data = []
        self._stores[name] = datastore_class(name, keys, data)

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
