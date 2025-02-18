import logging
from typing import TypeVar

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram import types
from aiogram.types.base import TelegramObject

from config import config

from core import domain
from services.db.storage import Storage, UserNotFoundException

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

        try:
            await store.user(this_user.id)
            role = await store.user_role(this_user.id)
        except UserNotFoundException:
            if this_user.is_bot:
                role = domain.Role.BOT
            elif this_user.id in config.admin_ids:
                role = domain.Role.ADMIN
            else:
                role = domain.Role.STUDENT
            await store.save_user(domain.User(chat_id=this_user.id, role=role))
        if obj.chat.id == config.comment_chat_id:
            role = domain.Role.MODERATOR

        data["role"] = role

        if data["role"] is domain.Role.BANNED:
            raise CancelHandler()
