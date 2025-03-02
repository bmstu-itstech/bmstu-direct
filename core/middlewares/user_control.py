import logging
from typing import TypeVar

import asyncio
from typing import Any, Dict

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware, BaseMiddleware
from aiogram import types
from aiogram.types.base import TelegramObject
from cachetools import TTLCache
from config import config

from core import domain
from services.db.storage import Storage

logger = logging.getLogger(__name__)
TelegramObjectType = TypeVar('TelegramObjectType', bound=TelegramObject)


class UserControlMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self):
        super().__init__()

    async def pre_process(self, obj: TelegramObjectType, data, *args):
        if obj.from_user is None:
            return

        store: Storage = data["store"]
        this_user: types.User = obj.from_user

        role = domain.Role.STUDENT
        if this_user.is_bot:
            role = domain.Role.BOT
        elif obj.chat.id == config.comment_chat_id:
            role = domain.Role.MODERATOR
        elif this_user.id in config.admin_ids:
            role = domain.Role.ADMIN
        elif await store.is_user_banned(this_user.id):
            logger.info(f"User with id={this_user.id} is banned. Handling skipped")
            raise CancelHandler()

        data["role"] = role
        logger.info(f"Update (type={type(obj).__name__}) from user with id={this_user.id}. User role={role}")



class AlbumsMiddleware(BaseMiddleware):
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
                self.albums_cache[album_id] = []
            self.albums_cache[album_id].append(message)

        await asyncio.sleep(self.wait_time_seconds)

        my_message_id = message.message_id
        smallest_message_id = my_message_id

        if album_id in self.albums_cache:
            for item in self.albums_cache[album_id]:
                smallest_message_id = min(smallest_message_id, item.message_id)

            if my_message_id != smallest_message_id:
                raise CancelHandler()
            else:
                data["album"] = self.albums_cache[album_id]
                del self.albums_cache[album_id]
                return
        else:
            return
