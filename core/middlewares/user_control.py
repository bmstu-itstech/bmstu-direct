import logging
from typing import TypeVar

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram import types
from aiogram.types.base import TelegramObject

from config import config

from core import domain
from services.db.storage import Storage, BannedUserNotFoundException

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
            raise CancelHandler()

        data["role"] = role
