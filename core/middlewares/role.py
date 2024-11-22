from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from core.models.role import UserRole


class RoleMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, owner_ids: list[int]):
        super().__init__()
        self.owner_ids = owner_ids

    async def pre_process(self, obj, data, *args):
        if not getattr(obj, "from_user", None):
            data["role"] = None
            return

        data["role"] = UserRole.User

        if obj.from_user.id in self.owner_ids:
            data["role"] = UserRole.Admin

    async def post_process(self, obj, data, *args):
        del data["role"]
