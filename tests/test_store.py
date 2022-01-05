import asyncio
import sys
import uuid

import pytest
import pytest_mock

import pybotters.store


def test_interface():
    store = pybotters.store.DataStoreManager()
    store.create('example')
    assert isinstance(store._stores, dict)
    assert isinstance(store._events, list)
    assert isinstance(store._iscorofunc, bool)
    assert 'example' in store
    assert isinstance(store['example'], pybotters.store.DataStore)

    store = pybotters.store.DataStoreManager(auto_cast=True)
    assert store._auto_cast is True
    store.create('example')
    store['example']._auto_cast is True


@pytest.mark.asyncio
async def test_interface_onmessage(mocker: pytest_mock.MockerFixture):
    store = pybotters.store.DataStoreManager()
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


def test_cast_item():
    actual = {
        'num_int': 123,
        'num_float': 1.23,
        'str_int': "123",
        'str_float': "1.23",
        'str_orig': "foo",
        'bool': True,
        'null': None,
    }
    expected = {
        'num_int': 123,
        'num_float': 1.23,
        'str_int': 123,
        'str_float': 1.23,
        'str_orig': "foo",
        'bool': True,
        'null': None,
    }
    pybotters.store.DataStore._cast_item(actual)
    assert expected == actual


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
    ds1._delete(data)
    assert len(ds1._data) == 0
    assert len(ds1._index) == 0

    ds2 = pybotters.store.DataStore(keys=['foo'], data=data)
    ds2._delete(nodata)
    assert len(ds2._data) == 1000
    assert len(ds2._index) == 1000

    ds3 = pybotters.store.DataStore(keys=['foo'], data=data)
    ds3._delete(invalid)
    assert len(ds3._data) == 1000
    assert len(ds3._index) == 1000


def test_pop():
    data = [{'foo': f'bar{i}'} for i in range(1000)]

    ds1 = pybotters.store.DataStore(keys=['foo'], data=data)
    assert ds1._pop({'foo': 'bar500'}) == {'foo': 'bar500'}
    assert ds1.get({'foo': 'bar500'}) is None
    assert ds1._pop({'foo': 'bar9999'}) is None

    ds2 = pybotters.store.DataStore(data=data)
    assert ds2._pop({'foo': 'bar500'}) is None


def test_find_and_delete():
    data = [{'foo': f'bar{i}', 'mod': i % 2} for i in range(1000)]
    query = {'mod': 1}
    invalid = {'mod': -1}

    ds1 = pybotters.store.DataStore(keys=['foo'], data=data)
    ret1 = ds1._find_and_delete()
    # return value
    assert isinstance(ret1, list)
    assert len(ret1) == 1000
    # data store
    assert len(ds1._data) == 0
    assert len(ds1._index) == 0

    ds2 = pybotters.store.DataStore(keys=['foo'], data=data)
    ret2 = ds2._find_and_delete(query)
    # return value
    assert isinstance(ret2, list)
    assert len(ret2) == 500
    assert all(map(lambda record: 1 == record['mod'], ret2))
    # data store
    assert len(ds2._data) == 500
    assert all(map(lambda record: 0 == record['mod'], ds2._data.values()))
    assert len(ds2._index) == 500

    ds3 = pybotters.store.DataStore(keys=['foo'], data=data)
    ret3 = ds3._find_and_delete(invalid)
    # return value
    assert isinstance(ret3, list)
    assert len(ret3) == 0
    # data store
    assert len(ds3._data) == 1000
    assert len(ds3._index) == 1000


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


def test__reversed__():
    data = [{'foo': f'bar{i}'} for i in range(5)]
    ds = pybotters.store.DataStore(keys=['foo'], data=data)
    if sys.version_info.major == 3 and sys.version_info.minor >= 8:
        data_iter = reversed(ds)
        assert next(data_iter) == {'foo': 'bar4'}
        assert next(data_iter) == {'foo': 'bar3'}
        assert next(data_iter) == {'foo': 'bar2'}
        assert next(data_iter) == {'foo': 'bar1'}
        assert next(data_iter) == {'foo': 'bar0'}
        with pytest.raises(StopIteration):
            next(data_iter)
    else:
        with pytest.raises(TypeError):
            data_iter = reversed(ds)


def test_set():
    ds = pybotters.store.DataStore()
    event = asyncio.Event()
    ds._events[event] = []
    data = [{'dummy1': 'data1'}, {'dummy2': 'data2'}, {'dummy3': 'data3'}]
    ds._set(data)
    assert all(e.is_set() for e in ds._events)
    assert ds._events[event] == data


@pytest.mark.asyncio
async def test_wait_set():
    data = [{'dummy': 'data'}]
    ret = {}

    class DataStoreHasDummySet(pybotters.store.DataStore):
        async def _set(self, data) -> None:
            return super()._set(data)

    async def wait_func(ds):
        ret['val'] = await ds.wait()

    ds0 = DataStoreHasDummySet()
    t_wait0 = asyncio.create_task(wait_func(ds0))
    t_set0 = asyncio.create_task(ds0._set(data))
    await asyncio.wait_for(t_wait0, timeout=5.0)
    assert t_set0.done()
    assert data == ret['val']


@pytest.mark.asyncio
async def test_wait_insert():
    data = [{'dummy': 'data'}]
    ret = {}

    class DataStoreHasDummyInsert(pybotters.store.DataStore):
        async def _insert(self, data) -> None:
            return super()._insert(data)

    async def wait_func(ds):
        ret['val'] = await ds.wait()

    ds1 = DataStoreHasDummyInsert()
    t_wait1 = asyncio.create_task(wait_func(ds1))
    t_set1 = asyncio.create_task(ds1._insert(data))
    await asyncio.wait_for(t_wait1, timeout=5.0)
    assert t_set1.done()
    assert data == ret['val']


@pytest.mark.asyncio
async def test_wait_update():
    data = [{'dummy': 'data'}]
    ret = {}

    class DataStoreHasDummyUpdate(pybotters.store.DataStore):
        async def _update(self, data) -> None:
            return super()._update(data)

    async def wait_func(ds):
        ret['val'] = await ds.wait()

    ds2 = DataStoreHasDummyUpdate()
    t_wait2 = asyncio.create_task(wait_func(ds2))
    t_set2 = asyncio.create_task(ds2._update(data))
    await asyncio.wait_for(t_wait2, timeout=5.0)
    assert t_set2.done()
    assert data == ret['val']


@pytest.mark.asyncio
async def test_wait_delete():
    data = [{'dummy': 'data'}]
    ret = {}

    class DataStoreHasDummyDelete(pybotters.store.DataStore):
        async def _delete(self, data) -> None:
            return super()._delete(data)

    async def wait_func(ds):
        ret['val'] = await ds.wait()

    ds3 = DataStoreHasDummyDelete()
    t_wait3 = asyncio.create_task(wait_func(ds3))
    t_set3 = asyncio.create_task(ds3._delete(data))
    await asyncio.wait_for(t_wait3, timeout=5.0)
    assert t_set3.done()
    assert data == ret['val']
