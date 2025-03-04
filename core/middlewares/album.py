import logging
import asyncio
from typing import Any, Dict, List

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types
from cachetools import TTLCache

logger = logging.getLogger(__name__)

class AlbumMiddleware(BaseMiddleware):
    def __init__(self, wait_time_seconds: float):
        super().__init__()
        self.wait_time_seconds = wait_time_seconds
        self.albums_cache = TTLCache(
            ttl=self.wait_time_seconds + 0.2,
            maxsize=1000
        )
        self.lock = asyncio.Lock()

    async def on_process_message(
        self,
        message: types.Message,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(message, types.Message):
            logger.debug(f"{self.__class__.__name__} используется не для Message, а для {type(message)}")
            return

        if message.media_group_id is None:
            return

        album_id: str = message.media_group_id

        async with self.lock:
            if album_id not in self.albums_cache:
                self.albums_cache[album_id] = {
                    "messages": [],
                    "processed": False
                }
            self.albums_cache[album_id]["messages"].append(message)

        await asyncio.sleep(self.wait_time_seconds)

        async with self.lock:
            if album_id in self.albums_cache:
                if self.albums_cache[album_id]["processed"]:
                    raise CancelHandler()

                messages: List[types.Message] = self.albums_cache[album_id]["messages"]
                smallest_message_id = min(msg.message_id for msg in messages)

                if message.message_id != smallest_message_id:
                    raise CancelHandler()
                else:
                    data["album"] = messages
                    self.albums_cache[album_id]["processed"] = True
                    # Не удаляем альбом из кэша, только ставим флаг processed = True
                    return
            else:
                return