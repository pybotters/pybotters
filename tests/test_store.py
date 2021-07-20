import asyncio
import uuid

import pytest
import pytest_mock

import pybotters.store


def test_interface():
    store = pybotters.store.DataStoreInterface()
    store.create('example')
    assert isinstance(store._stores, dict)
    assert isinstance(store._events, list)
    assert isinstance(store._iscorofunc, bool)
    assert 'example' in store
    assert isinstance(store['example'], pybotters.store.DataStore)


@pytest.mark.asyncio
async def test_interface_onmessage(mocker: pytest_mock.MockerFixture):
    store = pybotters.store.DataStoreInterface()
    assert not store._iscorofunc
    store._events.append(asyncio.Event())
    store.onmessage({'foo': 'bar'}, mocker.MagicMock())
    assert not len(store._events)


def test_ds():
    ds1 = pybotters.store.DataStore()
    assert len(ds1._data) == 0
    assert len(ds1._index) == 0
    assert len(ds1._keys) == 0

    ds2 = pybotters.store.DataStore(keys=['foo', 'bar'])
    assert len(ds2._data) == 0
    assert len(ds2._index) == 0
    assert len(ds2._keys) == 2

    ds3 = pybotters.store.DataStore(
        data=[{'foo': 'value1', 'bar': 'value1'}, {'foo': 'value2', 'bar': 'value2'}]
    )
    assert len(ds3._data) == 2
    assert len(ds3._index) == 0
    assert len(ds3._keys) == 0

    ds4 = pybotters.store.DataStore(
        keys=['foo', 'bar'],
        data=[{'foo': 'value1', 'bar': 'value1'}, {'foo': 'value2', 'bar': 'value2'}],
    )
    assert len(ds4._data) == 2
    assert len(ds4._index) == 2
    assert len(ds4._keys) == 2

    class DataStoreWithKeys(pybotters.store.DataStore):
        _KEYS = ['foo', 'bar']

    ds5 = DataStoreWithKeys()
    assert len(ds5._data) == 0
    assert len(ds5._index) == 0
    assert len(ds5._keys) == 2


def test_hash():
    hashed = pybotters.store.DataStore._hash({'foo': 'bar'})
    assert isinstance(hashed, int)


def test_sweep_with_key():
    data = [{'foo': f'bar{i}'} for i in range(1000)]
    ds = pybotters.store.DataStore(keys=['foo'], data=data)
    ds._MAXLEN = len(data) - 100
    ds._sweep_with_key()
    assert len(ds._data) == 900
    assert len(ds._index) == 900


def test_sweep_without_key():
    data = [{'foo': f'bar{i}'} for i in range(1000)]
    ds = pybotters.store.DataStore(data=data)
    ds._MAXLEN = len(data) - 100
    ds._sweep_without_key()
    assert len(ds._data) == 900
    assert len(ds._index) == 0


def test_insert():
    data = [{'foo': f'bar{i}'} for i in range(1000)]

    ds1 = pybotters.store.DataStore(keys=['foo'])
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

    ds3 = pybotters.store.DataStore(keys=['invalid'])
    ds3._insert(data)
    assert len(ds3._data) == 0
    assert len(ds3._index) == 0


def test_update():
    data = [{'foo': f'bar{i}'} for i in range(1000)]
    newdata = [{'foo': f'bar{i}'} for i in range(1000, 2000)]

    ds1 = pybotters.store.DataStore(keys=['foo'], data=data)
    ds1._update(data)
    assert len(ds1._data) == 1000
    assert len(ds1._index) == 1000

    ds2 = pybotters.store.DataStore(keys=['foo'], data=data)
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

    ds4 = pybotters.store.DataStore(keys=['invalid'])
    ds4._update(data)
    assert len(ds4._data) == 0
    assert len(ds4._index) == 0


def test_delete():
    data = [{'foo': f'bar{i}'} for i in range(1000)]
    nodata = [{'foo': f'bar{i}'} for i in range(1000, 2000)]
    invalid = [{'invalid': f'data{i}'} for i in range(1000, 2000)]

    ds1 = pybotters.store.DataStore(keys=['foo'], data=data)
    ds1.delete(data)
    assert len(ds1._data) == 0
    assert len(ds1._index) == 0

    ds2 = pybotters.store.DataStore(keys=['foo'], data=data)
    ds2.delete(nodata)
    assert len(ds2._data) == 1000
    assert len(ds2._index) == 1000

    ds3 = pybotters.store.DataStore(keys=['foo'], data=data)
    ds3.delete(invalid)
    assert len(ds3._data) == 1000
    assert len(ds3._index) == 1000


def test_findel():
    data = [{'foo': f'bar{i}', 'iseven': (i % 2) == 0} for i in range(1000)]

    ds1 = pybotters.store.DataStore(keys=['foo'], data=data)
    ds1.findel({'iseven': True})
    assert len(ds1._data) == 500
    assert all(map(lambda record: not record['iseven'], ds1._data.values()))
    assert len(ds1._index) == 500

    ds2 = pybotters.store.DataStore(keys=['foo'], data=data)
    ds2.findel({'iseven': False})
    assert len(ds2._data) == 500
    assert all(map(lambda record: record['iseven'], ds2._data.values()))
    assert len(ds2._index) == 500


def test_clear():
    data = [{'foo': f'bar{i}'} for i in range(1000)]
    ds = pybotters.store.DataStore(keys=['foo'], data=data)
    ds._clear()
    assert len(ds._data) == 0
    assert len(ds._index) == 0


def test_get():
    data = [{'foo': f'bar{i}'} for i in range(1000)]

    ds1 = pybotters.store.DataStore(keys=['foo'], data=data)
    assert ds1.get({'foo': 'bar500'}) == {'foo': 'bar500'}
    assert ds1.get({'foo': 'bar9999'}) is None

    ds2 = pybotters.store.DataStore(data=data)
    assert ds2.get({'foo': 'bar500'}) is None


def test_find():
    data = [{'foo': f'bar{i}', 'mod': i % 2} for i in range(1000)]
    query = {'mod': 1}
    invalid = {'mod': -1}
    ds = pybotters.store.DataStore(keys=['foo'], data=data)
    assert isinstance(ds.find(), list)
    assert len(ds.find()) == 1000
    assert len(ds.find(query)) == 500
    assert len(ds.find(invalid)) == 0


def test__len__():
    data = [{'foo': f'bar{i}'} for i in range(1000)]
    ds = pybotters.store.DataStore(keys=['foo'], data=data)
    assert len(ds) == 1000


def test__iter__():
    data = [{'foo': f'bar{i}'} for i in range(5)]
    ds = pybotters.store.DataStore(keys=['foo'], data=data)
    data_iter = iter(ds)
    assert next(data_iter) == {'foo': 'bar0'}
    assert next(data_iter) == {'foo': 'bar1'}
    assert next(data_iter) == {'foo': 'bar2'}
    assert next(data_iter) == {'foo': 'bar3'}
    assert next(data_iter) == {'foo': 'bar4'}
    with pytest.raises(StopIteration):
        next(data_iter)


def test_set():
    ds = pybotters.store.DataStore()
    events = [asyncio.Event(), asyncio.Event(), asyncio.Event()]
    ds._events.extend(events)
    ds._set()
    assert all(e.is_set() for e in events)
    assert not len(ds._events)


@pytest.mark.asyncio
async def test_wait():
    class DataStoreHasDummySet(pybotters.store.DataStore):
        async def _set(self) -> None:
            return super()._set()

    ds = DataStoreHasDummySet()
    t_wait = asyncio.create_task(ds.wait())
    t_set = asyncio.create_task(ds._set())
    await asyncio.wait_for(t_wait, timeout=5.0)
    assert t_set.done()
