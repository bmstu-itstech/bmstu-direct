import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from services.db.models import User
from core.models.role import UserRole
from core.utils.keyboards import *
from services.db.services.repository import Repo


logger = logging.getLogger(__name__)


async def admin_menu(message: Message, state: FSMContext):
    await message.answer("Админ-панель", reply_markup=get_admin_keyboard())
    await state.finish()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_menu, commands="admin", state="*", role=UserRole.OWNER)
