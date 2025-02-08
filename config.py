import os
from attr import dataclass
from dotenv import load_dotenv


load_dotenv()


class EnvIsNotDefined(Exception):
    def __init__(self, key: str):
        super().__init__(f"environment variable {key} is not defined")


def env_required(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvIsNotDefined(key)
    return value


def env_with_default(key: str, default: str = "") -> str:
    return os.getenv(key, default)


@dataclass
class DBConfig:
    host: str
    port: str
    user: str
    name: str
    password: str


@dataclass
class Config:
    telegram_bot_token: str
    channel_chat_id: int
    comment_chat_id: int
    swear_words_file: str
    db: DBConfig


config = Config(
    telegram_bot_token=env_required("TELEGRAM_BOT_TOKEN"),
    channel_chat_id=int(env_required("CHANNEL_CHAT_ID")),
    comment_chat_id=int(env_required("COMMENT_CHAT_ID")),
    swear_words_file=env_with_default("SWEAR_WORDS", "assets/swear_words.txt"),
    db=DBConfig(
        host=env_with_default("DB_HOST", "localhost"),
        port=env_with_default("DB_PORT", 5432),
        user=env_with_default("DB_USER", "postgres"),
        name=env_with_default("DB_NAME", "postgres"),
        password=env_with_default("DB_PASSWORD", "postgres"),
    )
)
