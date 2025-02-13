import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data
from aiogram.types.base import TelegramObject

from core.domain import Role


class RoleFilter(BoundFilter):
    key = "role"

    def __init__(self, role: typing.Union[None, Role, typing.Collection[Role]] = None):
        if role is None:
            self.roles = None
        elif isinstance(role, Role):
            self.roles = {role}
        else:
            self.roles = set(role)

    async def check(self, obj: TelegramObject):
        if self.roles is None:
            return True

        data = ctx_data.get()
        return data.get("role") in self.roles


class AdminFilter(RoleFilter):
    def __init__(self):
        super().__init__(Role.ADMIN)
