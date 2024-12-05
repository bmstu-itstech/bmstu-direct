import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from services.db.models import User, Ticket
from core.models.role import UserRole
from core.utils.keyboards import *
from core.text import text

from services.db.services.repository import Repo


logger = logging.getLogger(__name__)


async def admin_menu(message: Message, state: FSMContext):
    await message.answer(text.Btn.admin_panel, reply_markup=get_admin_keyboard())
    await state.finish()

def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_menu, commands=text.Commands.admin_menu, state="*", role=UserRole.OWNER)