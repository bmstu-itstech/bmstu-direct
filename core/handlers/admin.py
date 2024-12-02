import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from core.models.enums import UserRole
from core.utils import keyboards


logger = logging.getLogger(__name__)


async def admin_menu(message: Message, state: FSMContext):
    await message.answer("Админ-панель", reply_markup=await keyboards.admin_kb())
    await state.finish()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_menu, commands="admin", state="*", role=UserRole.ADMIN)
