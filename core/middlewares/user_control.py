import logging
from typing import TypeVar

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram import types
from aiogram.types.base import TelegramObject

from config import config

from core import domain
from services.db.storage import Storage, ModelNotFoundException


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
        data["role"] = await map_user_role(store, this_user)

        try:
            await store.user(this_user.id)
        except ModelNotFoundException:
            await store.save_user(domain.User(chat_id=this_user.id, role=data["role"]))

        if data["role"] is domain.Role.BANNED:
            raise CancelHandler()


async def map_user_role(store: Storage, user: types.User) -> domain.Role:
    if user.is_bot:
        return domain.Role.BOT
    if user.id in config.admin_ids:
        return domain.Role.ADMIN

    moderators = await store.users_where(role=domain.Role.MODERATOR)
    banned_users = await store.users_where(role=domain.Role.BANNED)

    moderator_ids = {moderator.chat_id for moderator in moderators}
    banned_ids = {banned.chat_id for banned in banned_users}

    if user.id in moderator_ids:
        return domain.Role.MODERATOR
    if user.id in banned_ids:
        return domain.Role.BANNED

    return domain.Role.STUDENT
