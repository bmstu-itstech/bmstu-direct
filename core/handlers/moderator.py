import logging
import re

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from core import texts
from core import states
from core import domain

from core.handlers import keyboards
from common.repository import dp, config
from services.db.storage import Storage


logger = logging.getLogger(__name__)
