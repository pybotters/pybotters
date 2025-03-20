from __future__ import annotations

import asyncio
import uuid
from typing import TYPE_CHECKING

import aiohttp
import pytest
import pytest_asyncio
from aiohttp import web

import pybotters.store

if TYPE_CHECKING:
    from aiohttp.test_utils import TestClient
    from pytest_aiohttp.plugin import AiohttpClient  # type: ignore

    from pybotters.ws import ClientWebSocketResponse


def test_dsm_construct():
    dsm = pybotters.store.DataStoreCollection()
    dsm._create("example")
    assert isinstance(dsm._stores, dict)
    assert isinstance(dsm._events, list)
    assert isinstance(dsm._iscorofunc, bool)
    assert "example" in dsm
    assert isinstance(dsm["example"], pybotters.store.DataStore)
    assert isinstance(
        dsm._get("example", pybotters.store.DataStore), pybotters.store.DataStore
    )


def test_dsm_subcls_construct():
    called = False

    class SubDataStoreCollection(pybotters.store.DataStoreCollection):
        def _init(self):
            nonlocal called
            called = True

    SubDataStoreCollection()

    assert called


@pytest_asyncio.fixture
async def echo_client(aiohttp_client: AiohttpClient) -> TestClient:
    routes = web.RouteTableDef()

    @routes.get("/ws")
    async def echo(request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for msg in ws:
            await ws.send_json(msg.json())
        return ws

    app = web.Application()
    app.add_routes(routes)

    client = await aiohttp_client(app)
    return client


@pytest.mark.asyncio
async def test_dsc_onmessage(echo_client: TestClient) -> None:
    class DSC(pybotters.store.DataStoreCollection):
        task: asyncio.Task[None]

        def _onmessage(
            self, message: object, ws: ClientWebSocketResponse | None = None
        ) -> None:
            assert ws is not None
            self.task = asyncio.create_task(ws.send_json(message))

    messages: list[object] = []
    async with echo_client.ws_connect(
        "/ws", timeout=aiohttp.ClientWSTimeout(ws_receive=5.0)
    ) as ws:
        dsc = DSC()
        dsc.onmessage({"foo": "bar"}, ws)  # type: ignore

        await dsc.task
        async for msg in ws:
            messages.append(msg.json())
            break

    assert messages == [{"foo": "bar"}]


def test_dsc_onmessage_without_ws(capsys: pytest.CaptureFixture) -> None:
    dsc = pybotters.store.DataStoreCollection()
    dsc.onmessage('{"foo":"bar"}')

    captured = capsys.readouterr()
    assert captured.out == '{"foo":"bar"}\n'


@pytest.mark.asyncio
async def test_dsc_wait() -> None:
    dsc = pybotters.store.DataStoreCollection()
    loop = asyncio.get_running_loop()

    wait_task = loop.create_task(dsc.wait())
    loop.call_soon(dsc.onmessage, {"foo": "bar"})

    await asyncio.wait_for(wait_task, timeout=5.0)


def test_ds_construct():
    ds1 = pybotters.store.DataStore()
    assert len(ds1._data) == 0
    assert len(ds1._index) == 0
    assert len(ds1._keys) == 0

    ds2 = pybotters.store.DataStore(keys=["foo", "bar"])
    assert len(ds2._data) == 0
    assert len(ds2._index) == 0
    assert len(ds2._keys) == 2

    ds3 = pybotters.store.DataStore(
        data=[{"foo": "value1", "bar": "value1"}, {"foo": "value2", "bar": "value2"}]
    )
    assert len(ds3._data) == 2
    assert len(ds3._index) == 0
    assert len(ds3._keys) == 0

    ds4 = pybotters.store.DataStore(
        keys=["foo", "bar"],
        data=[{"foo": "value1", "bar": "value1"}, {"foo": "value2", "bar": "value2"}],
    )
    assert len(ds4._data) == 2
    assert len(ds4._index) == 2
    assert len(ds4._keys) == 2

    class DataStoreWithKeys(pybotters.store.DataStore):
        _KEYS = ["foo", "bar"]

    ds5 = DataStoreWithKeys()
    assert len(ds5._data) == 0
    assert len(ds5._index) == 0
    assert len(ds5._keys) == 2


def test_ds_subcls_construct():
    called = False

    class SubDataStore(pybotters.store.DataStore):
        def _init(self):
            nonlocal called
            called = True

    SubDataStore()

    assert called


def test_ds_hash():
    hashed = pybotters.store.DataStore._hash({"foo": "bar"})
    assert isinstance(hashed, int)


def test_ds_sweep_with_key():
    data = [{"foo": f"bar{i}"} for i in range(1000)]
    ds = pybotters.store.DataStore(keys=["foo"], data=data)
    ds._MAXLEN = len(data) - 100
    ds._sweep_with_key()
    assert len(ds._data) == 900
    assert len(ds._index) == 900


def test_ds_sweep_without_key():
    data = [{"foo": f"bar{i}"} for i in range(1000)]
    ds = pybotters.store.DataStore(data=data)
    ds._MAXLEN = len(data) - 100
    ds._sweep_without_key()
    assert len(ds._data) == 900
    assert len(ds._index) == 0


def test_ds_insert():
    data = [{"foo": f"bar{i}"} for i in range(1000)]

    ds1 = pybotters.store.DataStore(keys=["foo"])
    ds1._insert(data)
    assert len(ds1._data) == 1000
    assert len(ds1._index) == 1000
    assert isinstance(next(iter(ds1._data.keys())), uuid.UUID)
    assert isinstance(next(iter(ds1._data.values())), dict)
    assert isinstance(next(iter(ds1._index.keys())), int)
    assert isinstance(next(iter(ds1._index.values())), uuid.UUID)

    ds2 = pybotters.store.DataStore()
    ds2._insert(data)
    assert len(ds2._data) == 1000
    assert len(ds2._index) == 0
    assert isinstance(next(iter(ds2._data.keys())), uuid.UUID)
    assert isinstance(next(iter(ds2._data.values())), dict)

    ds3 = pybotters.store.DataStore(keys=["invalid"])
    ds3._insert(data)
    assert len(ds3._data) == 0
    assert len(ds3._index) == 0

    ds4 = pybotters.store.DataStore(keys=["foo"], data=[{"foo": "bar1", "old": "baz"}])
    ds4._insert([{"foo": "bar1", "new": "foobar"}])
    assert ds4.get({"foo": "bar1"}) == {"foo": "bar1", "new": "foobar"}


def test_ds_update():
    data = [{"foo": f"bar{i}"} for i in range(1000)]
    newdata = [{"foo": f"bar{i}"} for i in range(1000, 2000)]

    ds1 = pybotters.store.DataStore(keys=["foo"], data=data)
    ds1._update(data)
    assert len(ds1._data) == 1000
    assert len(ds1._index) == 1000

    ds2 = pybotters.store.DataStore(keys=["foo"], data=data)
    ds2._update(newdata)
    assert len(ds2._data) == 2000
    assert len(ds2._index) == 2000
    assert isinstance(list(ds2._data.keys())[-1], uuid.UUID)
    assert isinstance(list(ds2._data.values())[-1], dict)
    assert isinstance(list(ds2._index.keys())[-1], int)
    assert isinstance(list(ds2._index.values())[-1], uuid.UUID)

    ds3 = pybotters.store.DataStore()
    ds3._update(data)
    assert len(ds3._data) == 1000
    assert len(ds3._index) == 0
    assert isinstance(next(iter(ds3._data.keys())), uuid.UUID)
    assert isinstance(next(iter(ds3._data.values())), dict)

    ds4 = pybotters.store.DataStore(keys=["invalid"])
    ds4._update(data)
    assert len(ds4._data) == 0
    assert len(ds4._index) == 0


def test_ds_delete():
    data = [{"foo": f"bar{i}"} for i in range(1000)]
    nodata = [{"foo": f"bar{i}"} for i in range(1000, 2000)]
    invalid = [{"invalid": f"data{i}"} for i in range(1000, 2000)]

    ds1 = pybotters.store.DataStore(keys=["foo"], data=data)
    ds1._delete(data)
    assert len(ds1._data) == 0
    assert len(ds1._index) == 0

    ds2 = pybotters.store.DataStore(keys=["foo"], data=data)
    ds2._delete(nodata)
    assert len(ds2._data) == 1000
    assert len(ds2._index) == 1000

    ds3 = pybotters.store.DataStore(keys=["foo"], data=data)
    ds3._delete(invalid)
    assert len(ds3._data) == 1000
    assert len(ds3._index) == 1000


def test_ds_remove():
    data = [{"id": i} for i in range(1000)]

    ds1 = pybotters.store.DataStore(keys=["id"], data=data)
    assert len(ds1._data) == 1000
    assert len(ds1._index) == 1000
    ds1._remove(list(ds1._find_with_uuid({"id": 1})))
    assert len(ds1._data) == 999
    assert len(ds1._index) == 999

    ds2 = pybotters.store.DataStore(data=data)
    assert len(ds2._data) == 1000
    assert len(ds2._index) == 0
    ds2._remove(list(ds2._find_with_uuid({"id": 1})))
    assert len(ds2._data) == 999
    assert len(ds2._index) == 0


def test_ds_pop():
    data = [{"foo": f"bar{i}"} for i in range(1000)]

    ds1 = pybotters.store.DataStore(keys=["foo"], data=data)
    assert ds1._pop({"foo": "bar500"}) == {"foo": "bar500"}
    assert ds1.get({"foo": "bar500"}) is None
    assert ds1._pop({"foo": "bar9999"}) is None

    ds2 = pybotters.store.DataStore(data=data)
    assert ds2._pop({"foo": "bar500"}) is None

    ds3 = pybotters.store.DataStore(keys=["foobar"], data=data)
    assert ds3._pop({"foo": "bar500"}) is None


def test_ds_find_and_delete():
    data = [{"foo": f"bar{i}", "mod": i % 2} for i in range(1000)]
    query = {"mod": 1}
    invalid = {"mod": -1}

    ds1 = pybotters.store.DataStore(keys=["foo"], data=data)
    ret1 = ds1._find_and_delete()
    # return value
    assert isinstance(ret1, list)
    assert len(ret1) == 1000
    # data store
    assert len(ds1._data) == 0
    assert len(ds1._index) == 0

    ds2 = pybotters.store.DataStore(keys=["foo"], data=data)
    ret2 = ds2._find_and_delete(query)
    # return value
    assert isinstance(ret2, list)
    assert len(ret2) == 500
    assert all(map(lambda record: 1 == record["mod"], ret2))
    # data store
    assert len(ds2._data) == 500
    assert all(map(lambda record: 0 == record["mod"], ds2._data.values()))
    assert len(ds2._index) == 500

    ds3 = pybotters.store.DataStore(keys=["foo"], data=data)
    ret3 = ds3._find_and_delete(invalid)
    # return value
    assert isinstance(ret3, list)
    assert len(ret3) == 0
    # data store
    assert len(ds3._data) == 1000
    assert len(ds3._index) == 1000


def test_ds_clear():
    data = [{"foo": f"bar{i}"} for i in range(1000)]
    ds = pybotters.store.DataStore(keys=["foo"], data=data)
    ds._clear()
    assert len(ds._data) == 0
    assert len(ds._index) == 0


def test_ds_get():
    data = [{"foo": f"bar{i}"} for i in range(1000)]

    ds1 = pybotters.store.DataStore(keys=["foo"], data=data)
    assert ds1.get({"foo": "bar500"}) == {"foo": "bar500"}
    assert ds1.get({"foo": "bar9999"}) is None

    ds2 = pybotters.store.DataStore(data=data)
    assert ds2.get({"foo": "bar500"}) is None

    ds3 = pybotters.store.DataStore(keys=["foobar"], data=data)
    assert ds3.get({"foo": "bar500"}) is None


def test_ds_find():
    data = [{"foo": f"bar{i}", "mod": i % 2} for i in range(1000)]
    query = {"mod": 1}
    invalid = {"mod": -1}
    ds = pybotters.store.DataStore(keys=["foo"], data=data)
    assert isinstance(ds.find(), list)
    assert len(ds.find()) == 1000
    assert len(ds.find(query)) == 500
    assert len(ds.find(invalid)) == 0


def test_ds_find_with_uuid():
    ds = pybotters.store.DataStore(data=[{"id": 1}, {"id": 2}])

    result = ds._find_with_uuid()
    assert len(result.keys()) == 2
    assert all(isinstance(x, uuid.UUID) for x in result.keys())
    assert list(result.values()) == [{"id": 1}, {"id": 2}]

    result = ds._find_with_uuid({"id": 1})
    assert len(result.keys()) == 1
    assert all(isinstance(x, uuid.UUID) for x in result.keys())
    assert list(result.values()) == [{"id": 1}]


@pytest.mark.parametrize(
    "test_input,query,limit,expected",
    [
        (
            [
                {"name": "foo", "id": "2", "sort_type": "desc"},
                {"name": "foo", "id": "5", "sort_type": "asc"},
                {"name": "foo", "id": "6", "sort_type": "asc"},
                {"name": "foo", "id": "1", "sort_type": "desc"},
                {"name": "foo", "id": "4", "sort_type": "asc"},
                {"name": "foo", "id": "3", "sort_type": "desc"},
            ],
            None,
            None,
            {
                "asc": [
                    {"name": "foo", "id": "4", "sort_type": "asc"},
                    {"name": "foo", "id": "5", "sort_type": "asc"},
                    {"name": "foo", "id": "6", "sort_type": "asc"},
                ],
                "desc": [
                    {"name": "foo", "id": "3", "sort_type": "desc"},
                    {"name": "foo", "id": "2", "sort_type": "desc"},
                    {"name": "foo", "id": "1", "sort_type": "desc"},
                ],
            },
        ),
        (
            [
                {"name": "foo", "id": "2", "sort_type": "desc"},
                {"name": "foo", "id": "5", "sort_type": "asc"},
                {"name": "bar", "id": "6", "sort_type": "asc"},
                {"name": "bar", "id": "1", "sort_type": "desc"},
                {"name": "foo", "id": "4", "sort_type": "asc"},
                {"name": "foo", "id": "3", "sort_type": "desc"},
            ],
            {"name": "foo"},
            None,
            {
                "asc": [
                    {"name": "foo", "id": "4", "sort_type": "asc"},
                    {"name": "foo", "id": "5", "sort_type": "asc"},
                ],
                "desc": [
                    {"name": "foo", "id": "3", "sort_type": "desc"},
                    {"name": "foo", "id": "2", "sort_type": "desc"},
                ],
            },
        ),
        (
            [
                {"name": "foo", "id": "2", "sort_type": "desc"},
                {"name": "foo", "id": "5", "sort_type": "asc"},
                {"name": "foo", "id": "6", "sort_type": "asc"},
                {"name": "foo", "id": "1", "sort_type": "desc"},
                {"name": "foo", "id": "4", "sort_type": "asc"},
                {"name": "foo", "id": "3", "sort_type": "desc"},
            ],
            None,
            1,
            {
                "asc": [
                    {"name": "foo", "id": "4", "sort_type": "asc"},
                ],
                "desc": [
                    {"name": "foo", "id": "3", "sort_type": "desc"},
                ],
            },
        ),
    ],
)
def test_ds_sorted(test_input, query, limit, expected):
    ds = pybotters.store.DataStore(keys=["name", "id", "sort_type"], data=test_input)
    actual = ds._sorted(
        item_key="sort_type",
        item_asc_key="asc",
        item_desc_key="desc",
        sort_key="id",
        query=query,
        limit=limit,
    )

    assert actual == expected


def test_ds__len__():
    data = [{"foo": f"bar{i}"} for i in range(1000)]
    ds = pybotters.store.DataStore(keys=["foo"], data=data)
    assert len(ds) == 1000


def test_ds__iter__():
    data = [{"foo": f"bar{i}"} for i in range(5)]
    ds = pybotters.store.DataStore(keys=["foo"], data=data)
    data_iter = iter(ds)
    assert next(data_iter) == {"foo": "bar0"}
    assert next(data_iter) == {"foo": "bar1"}
    assert next(data_iter) == {"foo": "bar2"}
    assert next(data_iter) == {"foo": "bar3"}
    assert next(data_iter) == {"foo": "bar4"}
    with pytest.raises(StopIteration):
        next(data_iter)


def test_ds__reversed__():
    data = [{"foo": f"bar{i}"} for i in range(5)]
    ds = pybotters.store.DataStore(keys=["foo"], data=data)
    data_iter = reversed(ds)
    assert next(data_iter) == {"foo": "bar4"}
    assert next(data_iter) == {"foo": "bar3"}
    assert next(data_iter) == {"foo": "bar2"}
    assert next(data_iter) == {"foo": "bar1"}
    assert next(data_iter) == {"foo": "bar0"}
    with pytest.raises(StopIteration):
        next(data_iter)


def test_ds_set():
    ds = pybotters.store.DataStore()
    events = [asyncio.Event(), asyncio.Event(), asyncio.Event()]
    ds._events.extend(events)
    ds._set()
    assert all(e.is_set() for e in events)
    assert not len(ds._events)


@pytest.mark.asyncio
async def test_ds_wait():
    ds = pybotters.store.DataStore()
    loop = asyncio.get_running_loop()

    wait_task = loop.create_task(ds.wait())
    loop.call_soon(ds._set)
    await asyncio.wait_for(wait_task, timeout=5.0)


@pytest.mark.asyncio
async def test_ds_wait_functional():
    ds = pybotters.store.DataStore(keys=["id"])
    loop = asyncio.get_running_loop()

    wait_task = loop.create_task(ds.wait())
    loop.call_soon(
        ds._insert, [{"id": 1, "val": 1}, {"id": 2, "val": 2}, {"id": 3, "val": 3}]
    )
    await asyncio.wait_for(wait_task, timeout=5.0)

    wait_task = loop.create_task(ds.wait())
    loop.call_soon(ds._update, [{"id": 1, "val": None}])
    await asyncio.wait_for(wait_task, timeout=5.0)

    wait_task = loop.create_task(ds.wait())
    loop.call_soon(ds._delete, [{"id": 1}])
    await asyncio.wait_for(wait_task, timeout=5.0)

    wait_task = loop.create_task(ds.wait())
    loop.call_soon(ds._remove, list(ds._find_with_uuid({"id": 2})))
    await asyncio.wait_for(wait_task, timeout=5.0)

    wait_task = loop.create_task(ds.wait())
    loop.call_soon(ds._clear)
    await asyncio.wait_for(wait_task, timeout=5.0)


def test_ds_put():
    ds = pybotters.store.DataStore()
    queue = asyncio.Queue()
    ds._queues.append(queue)

    operation = "update"
    source = {"id": 123, "data": "updata"}
    item = {"id": 123, "data": "updata", "extra": "extra"}

    ds._put(operation, source, item)
    result = queue.get_nowait()

    assert result == pybotters.store.StoreChange(ds, operation, source, item)


def test_ds_watch():
    ds = pybotters.store.DataStore()

    assert isinstance(ds.watch(), pybotters.store.StoreStream)


@pytest.mark.asyncio
async def test_store_stream():
    ds = pybotters.store.DataStore(
        keys=["id"], data=[{"id": 1, "data": "foo", "extra": "extra"}]
    )

    with ds.watch() as stream:
        assert isinstance(stream, pybotters.store.StoreStream)
        ds._update([{"id": 1, "data": "bar"}])

        async def _inner():
            async for change in stream:
                assert change.operation == "update"
                assert change.source == {"id": 1, "data": "bar"}
                assert change.data == {"id": 1, "data": "bar", "extra": "extra"}
                assert isinstance(change.store, pybotters.store.DataStore)

                break

        await asyncio.wait_for(_inner(), timeout=5.0)
