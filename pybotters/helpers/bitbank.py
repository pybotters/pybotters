"""Helper functions for bitbank Private Stream API and PubNub.

.. autofunction:: subscribe_with_callback

.. autofunction:: subscribe

.. autofunction:: fetch_channel_and_token

.. autofunction:: fetch_subscribe
"""

from __future__ import annotations

__all__ = [
    "BaseResponse",
    "ChannelAndToken",
    "SubscribeResponse",
    "TimeToken",
    "SubscribeMessage",
    "subscribe_with_callback",
    "subscribe",
    "fetch_channel_and_token",
    "fetch_subscribe",
]

from typing import TYPE_CHECKING, Any, TypedDict, TypeVar, cast

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable
    from typing import Final

    import pybotters

_T = TypeVar("_T")


class BaseResponse(TypedDict):
    """bitbank base response.

    https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#general-api-information
    """

    success: int
    data: ChannelAndToken


class ChannelAndToken(TypedDict):
    """bitbank response for /v1/user/subscribe.

    https://github.com/bitbankinc/bitbank-api-docs/blob/master/private-stream.md
    """

    pubnub_channel: str
    pubnub_token: str


class SubscribeResponse(TypedDict):
    """PubNub Subscribe response.

    https://www.pubnub.com/docs/sdks/rest-api/subscribe-v-2#body-for-normal-messages
    """

    t: TimeToken
    m: list[SubscribeMessage]


class TimeToken(TypedDict):
    """The "t" field for SubscribeResponse."""

    t: str
    r: int


class SubscribeMessage(TypedDict):
    """The "m" field in SubscribeResponse."""

    a: str
    f: int
    p: TimeToken
    k: str
    c: str
    d: Any


DEFAULT_BITBANK_SERVER: Final[str] = "https://api.bitbank.cc"
DEFAULT_PUBNUB_SERVER: Final[str] = "https://ps.pndsn.com"
DEFAULT_SUBSCRIBE_KEY: Final[str] = "sub-c-ecebae8e-dd60-11e6-b6b1-02ee2ddab7fe"


async def subscribe_with_callback(
    client: pybotters.Client,
    callback: Callable[[Any], object],
    /,
    channel: str | None = None,
    token: str | None = None,
    tt: str | None = None,
    tr: str | None = None,
    *,
    bitbank_server: str = DEFAULT_BITBANK_SERVER,
    pubnub_server: str = DEFAULT_PUBNUB_SERVER,
    subscribe_key: str = DEFAULT_SUBSCRIBE_KEY,
) -> None:
    """Subscribe to bitbank Private Stream API and handle a callback.

    Example
    -------
    .. code-block::

        import asyncio
        import os
        from contextlib import suppress

        import pybotters
        from pybotters.helpers.bitbank import subscribe_with_callback

        BITBANK_API_KEY = os.environ["BITBANK_API_KEY"]
        BITBANK_API_SECRET = os.environ["BITBANK_API_SECRET"]

        apis = {"bitbank": [BITBANK_API_KEY, BITBANK_API_SECRET]}


        async def main():
            async with pybotters.Client(apis=apis) as client:
                store = pybotters.bitbankPrivateDataStore()
                task = asyncio.create_task(subscribe_with_callback(client, store.onmessage))
                try:
                    # Example: Watch active orders ...
                    with store.spot_order.watch() as stream:
                        async for _ in stream:
                            print(store.spot_order.find())
                finally:
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)


        if __name__ == "__main__":
            with suppress(KeyboardInterrupt):
                asyncio.run(main())
    """

    async for message in subscribe(
        client,
        channel=channel,
        token=token,
        tt=tt,
        tr=tr,
        bitbank_server=bitbank_server,
        pubnub_server=pubnub_server,
        subscribe_key=subscribe_key,
    ):
        for msg in message["m"]:
            callback(msg["d"])


async def subscribe(
    client: pybotters.Client,
    /,
    channel: str | None = None,
    token: str | None = None,
    tt: str | None = None,
    tr: str | None = None,
    *,
    bitbank_server: str = DEFAULT_BITBANK_SERVER,
    pubnub_server: str = DEFAULT_PUBNUB_SERVER,
    subscribe_key: str = DEFAULT_SUBSCRIBE_KEY,
) -> AsyncGenerator[SubscribeResponse]:
    """Subscribe to bitbank Private Stream API.

    This function yields SubscribeResponse.

    It automatically fetches PubNub credentials (channel and token) from bitbank if not
    provided. It also refetches the token if it expires.

    Example
    -------
    .. code-block::

        import asyncio
        import os
        from contextlib import suppress

        import pybotters
        from pybotters.helpers.bitbank import subscribe

        BITBANK_API_KEY = os.environ["BITBANK_API_KEY"]
        BITBANK_API_SECRET = os.environ["BITBANK_API_SECRET"]

        apis = {"bitbank": [BITBANK_API_KEY, BITBANK_API_SECRET]}

        async def main():
            async with pybotters.Client(apis=apis) as client:
                async for message in subscribe(client):
                    print(message)

        if __name__ == "__main__":
            with suppress(KeyboardInterrupt):
                asyncio.run(main())
    """

    if (channel is None) or (token is None):
        response = await fetch_channel_and_token(client, bitbank_server=bitbank_server)
        channel_and_token = response["data"]
    else:
        channel_and_token = ChannelAndToken(
            pubnub_channel=channel,
            pubnub_token=token,
        )

    while True:
        try:
            subscribe = await fetch_subscribe(
                client,
                channel=channel_and_token["pubnub_channel"],
                token=channel_and_token["pubnub_token"],
                tt=tt,
                tr=tr,
                pubnub_server=pubnub_server,
                subscribe_key=subscribe_key,
            )
            tt = subscribe["t"]["t"]
            tr = str(subscribe["t"]["r"])
        except ValueError as e:
            if (
                len(e.args)
                and isinstance(e.args[0], dict)
                and e.args[0].get("message") == "Token is expired."
            ):
                response = await fetch_channel_and_token(
                    client, bitbank_server=bitbank_server
                )
                channel_and_token = response["data"]
                continue

            raise

        yield subscribe


async def fetch_channel_and_token(
    client: pybotters.Client,
    /,
    *,
    bitbank_server: str = DEFAULT_BITBANK_SERVER,
) -> BaseResponse:
    """Fetch channel and token from bitbank.

    ``GET /user/subscribe``

    https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api.md#private-stream
    """

    url = f"{bitbank_server}/v1/user/subscribe"
    async with client.get(url) as resp:
        data = await resp.json()

    if (not isinstance(data, dict)) or (data.get("success") != 1):
        raise ValueError(data)

    return cast("BaseResponse", data)


async def fetch_subscribe(
    clinet: pybotters.Client,
    /,
    channel: str,
    token: str | None = None,
    tt: str | None = None,
    tr: str | None = None,
    *,
    pubnub_server: str = DEFAULT_PUBNUB_SERVER,
    subscribe_key: str = DEFAULT_SUBSCRIBE_KEY,
) -> SubscribeResponse:
    """Fetch bitbank subscription messages from PubNub.

    ``GET /v2/subscribe/:sub_key/:channel/:callback``

    https://www.pubnub.com/docs/sdks/rest-api/subscribe-v-2
    """

    url = f"{pubnub_server}/v2/subscribe/{subscribe_key}/{channel}/0"
    params: dict[str, str] = {"uuid": channel}
    if tt is not None:
        params["tt"] = tt
    if tr is not None:
        params["tr"] = tr
    if token is not None:
        params["auth"] = token

    async with clinet.get(url, params=params) as resp:
        data = await resp.json(content_type=None)

    if (not isinstance(data, dict)) or ("t" not in data):
        raise ValueError(data)

    return cast("SubscribeResponse", data)
