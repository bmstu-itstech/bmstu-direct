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
        logger.error(f'Отсутствует переменная: {key}, проверь файл .env и сверься с файлом .env-example!')
        sys.exit(1)
    return value



BOT_TOKEN = get_env_variable("BOT_TOKEN")
ADMINS_IDS = list(map(int, get_env_variable('BOT_ADMINS_ID').split(',')))
DB_NAME = get_env_variable("DB_NAME")
DB_PASSWORD = get_env_variable("DB_PASSWORD")
DB_ADDRESS = get_env_variable("DB_ADDRESS")
DB_USER = get_env_variable("DB_USER")
QUESTIONS_CHAT = get_env_variable("QUESTION_CHAT_ID")
QUESTIONS_COMMENT = get_env_variable('QUESTION_COMMENT_ID')
PROBLEMS_CHAT = get_env_variable("PROBLEMS_CHAT_ID")
PROBLEMS_COMMENT = get_env_variable('PROBLEMS_COMMENT_ID')
SUGGESTIONS_CHAT = get_env_variable("SUGGESTIONS_CHAT_ID")
SUGGESTIONS_COMMENT = get_env_variable('SUGGESTIONS_COMMENT_ID')



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

