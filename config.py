import os
import logging
import sys

from dotenv import load_dotenv
from dataclasses import dataclass

logger = logging.getLogger(__name__)
load_dotenv()

# функция получения переменной из .env с обработкой ошибок
def get_env_variable(key, default=None):
    value = os.getenv(key, default)
    if value is None:
        logger.error(f'Отсутсвует переменная: {key}, проверь файл .env и сверься с файлом .env-example!')
        sys.exit(1)
    return value


try:
    BOT_TOKEN = get_env_variable("Bot_token")
    ADMINS_IDS = list(map(int, get_env_variable('Bot_admin_ids').split(',')))
    DB_NAME = get_env_variable("Db_name")
    DB_PASSWORD = get_env_variable("Db_password")
    DB_ADDRESS = get_env_variable("Db_address")
    DB_USER = get_env_variable("Db_user")
    QUESTIONS_CHAT = get_env_variable("Questions_chat_id")
    QUESTIONS_COMMENT = get_env_variable('Questions_comment_id')
    PROBLEMS_CHAT = get_env_variable("Problems_chat_id")
    PROBLEMS_COMMENT = get_env_variable('Problems_comment_id')
    SUGGESTIONS_CHAT = get_env_variable("Suggestions_chat_id")
    SUGGESTIONS_COMMENT = get_env_variable('Suggestions_comment_id')

except Exception as e:
    logger.exception('Произошла ошибка при запуске')
    sys.exit(1)


@dataclass
class DbConfig:
    user: str
    password: str
    address: str
    name: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]

@dataclass
class ModChannel:
    questions_chat_id: str
    questions_comment_id: str

    problems_chat_id: str
    problems_comment_id: str

    suggestions_chat_id: str
    suggestions_comment_id: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    channel: ModChannel

def cast_bool(value: str) -> bool:
    if not value:
        return False
    return value.lower() in ("true", "t", "1", "yes", "y")


def load_config():
    return Config(
        tg_bot = TgBot(
            token = BOT_TOKEN,
            admin_ids = ADMINS_IDS,
        ),
        db = DbConfig(
            name =DB_NAME,
            password = DB_PASSWORD,
            address = DB_ADDRESS,
            user = DB_USER,
        ),
        channel = ModChannel(
            questions_chat_id = QUESTIONS_CHAT,
            questions_comment_id = QUESTIONS_COMMENT,

            problems_chat_id = PROBLEMS_CHAT,
            problems_comment_id = PROBLEMS_COMMENT,

            suggestions_chat_id = SUGGESTIONS_CHAT,
            suggestions_comment_id = SUGGESTIONS_COMMENT
        )
    )


config = load_config()

