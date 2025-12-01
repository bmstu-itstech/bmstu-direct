import logging
from typing import Any

from aiogram.utils.exceptions import MessageNotModified, TelegramAPIError

from common.repository import dp

logger = logging.getLogger(__name__)


def _exception_text(err: BaseException) -> str:
    text = getattr(err, "text", None)
    if text:
        return str(text)
    description = getattr(err, "description", None)
    if description:
        return str(description)
    return str(err)


@dp.errors_handler()
async def aiogram_errors_handler(update: Any, error: Exception) -> bool:
    if isinstance(error, MessageNotModified):
        logger.info("Message update skipped: %s", _exception_text(error))
        return True

    if isinstance(error, TelegramAPIError):
        logger.exception("Telegram API error: %s", _exception_text(error))
        return True

    logger.exception("Unhandled exception during update processing", exc_info=error)
    return True
