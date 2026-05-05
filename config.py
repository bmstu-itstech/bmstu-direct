import os
from typing import Optional

from attr import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    telegram_bot_token: str
    admin_ids: list[int]
    channel_chat_id: int
    comment_chat_id: int
    swear_words_file: str
    logs_dir: str
    db_uri: str
    proxy_url: Optional[str] = None


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


config = Config(
    telegram_bot_token=env_required("TELEGRAM_BOT_TOKEN"),
    admin_ids=list(map(int, env_required("ADMIN_IDS").split(";"))),
    channel_chat_id=int(env_required("CHANNEL_CHAT_ID")),
    comment_chat_id=int(env_required("COMMENT_CHAT_ID")),
    swear_words_file=env_with_default("SWEAR_WORDS", "assets/swear_words.txt"),
    logs_dir=env_with_default("LOGS_DIR", "./logs"),
    db_uri=env_required("DATABASE_URI"),
    proxy_url=env_with_default("PROXY_URL") or None,
)
