import os

from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


config_from_env = {
    'BOT_TOKEN': str(os.getenv("bot_token")),
    'ADMINS_IDS': map(int, os.getenv('bot_admin_ids').split(',')) if os.getenv('bot_admin_ids') else [],
    'DB_NAME': os.getenv("db_name"),
    'DB_PASSWORD': os.getenv("db_password"),
    'DB_ADDRESS': os.getenv("db_address"),
    'DB_USER': os.getenv("db_user"),
    'QUESTIONS_CHAT': os.getenv("questions_chat_id"),
    'QUESTIONS_COMMENT': os.getenv('questions_comment_id'),
    'PROBLEMS_CHAT': os.getenv("problems_chat_id"),
    'PROBLEMS_COMMENT': os.getenv('problems_comment_id'),
    'SUGGESTIONS_CHAT': os.getenv("suggestions_chat_id"),
    'SUGGESTIONS_COMMENT': os.getenv('suggestions_comment_id')

}
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
        tg_bot=TgBot(
            token=config_from_env['BOT_TOKEN'],
            admin_ids=config_from_env['ADMINS_IDS'],
        ),
        db=DbConfig(
            name=config_from_env['DB_NAME'],
            password=config_from_env['DB_PASSWORD'],
            address=config_from_env['DB_ADDRESS'],
            user=config_from_env['DB_USER'],
        ),
        channel=ModChannel(
            questions_chat_id = config_from_env['QUESTIONS_CHAT'],
            questions_comment_id = config_from_env['QUESTIONS_COMMENT'],

            problems_chat_id = config_from_env['PROBLEMS_CHAT'],
            problems_comment_id = config_from_env['PROBLEMS_COMMENT'],

            suggestions_chat_id = config_from_env['SUGGESTIONS_CHAT'],
            suggestions_comment_id = config_from_env['SUGGESTIONS_COMMENT']
        )
    )


config = load_config()
