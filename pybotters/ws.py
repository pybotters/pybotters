import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp
from aiohttp.http_websocket import json
from aiohttp.typedefs import StrOrURL


logger = logging.getLogger(__name__)


async def ws_run_forever(
    url: StrOrURL,
    session: aiohttp.ClientSession,
    event: asyncio.Event,
    *,
    send_str: Optional[str]=None,
    send_json: Optional[Any]=None,
    hdlr_str=None,
    hdlr_json=None,
    **kwargs: Any,
) -> None:
    iscorofunc_str = asyncio.iscoroutinefunction(hdlr_str)
    iscorofunc_json = asyncio.iscoroutinefunction(hdlr_json)
    while not session.closed:
        separator = asyncio.create_task(asyncio.sleep(60.0))
        try:
            async with session.ws_connect(url, **kwargs) as ws:
                event.set()
                if send_str is not None:
                    await ws.send_str(send_str)
                if send_json is not None:
                    await ws.send_json(send_json)
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        if hdlr_str is not None:
                            try:
                                if iscorofunc_str:
                                    await hdlr_str(msg.data, ws)
                                else:
                                    hdlr_str(msg.data, ws)
                            except Exception as e:
                                logger.error(repr(e))
                        if hdlr_json is not None:
                            try:
                                data = msg.json()
                            except json.decoder.JSONDecodeError:
                                pass
                            else:
                                try:
                                    if iscorofunc_json:
                                        await hdlr_json(data, ws)
                                    else:
                                        hdlr_json(data, ws)
                                except Exception as e:
                                    logger.error(repr(e))
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
        except aiohttp.WSServerHandshakeError as e:
            logger.warning(repr(e))
        await separator
