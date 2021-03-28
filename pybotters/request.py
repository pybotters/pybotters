import aiohttp
from multidict import MultiDict
from yarl import URL

from .auth import Hosts


class ClientRequest(aiohttp.ClientRequest):
    def __init__(self, *args, **kwargs) -> None:
        method: str = args[0]
        url: URL = args[1]

        if kwargs['params']:
            q = MultiDict(url.query)
            url2 = url.with_query(kwargs['params'])
            q.extend(url2.query)
            url = url.with_query(q)
            args = (method, url, )
            kwargs['params'] = None

        if url.host in Hosts.items:
            if Hosts.items[url.host].name in kwargs['session'].__dict__['_apis']:
                args = Hosts.items[url.host].func(args, kwargs)

        super().__init__(*args, **kwargs)
