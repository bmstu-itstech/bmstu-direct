import os

from dotenv import load_dotenv
from dataclasses import dataclass


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
    problems_chat_id: str
    suggestions_chat_id: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    channel: ModChannel

def cast_bool(value: str) -> bool:
    if not value:
        return False
    return value.lower() in ("true", "t", "1", "yes", "y")


load_dotenv()


def load_config():
    return Config(
        tg_bot=TgBot(
            token=os.getenv("bot_token"),
            admin_ids=list(map(int, os.getenv("bot_admin_ids").split(", "))),
        ),
        db=DbConfig(
            name=os.getenv("db_name"),
            password=os.getenv("db_password"),
            address=os.getenv("db_address"),
            user=os.getenv("db_user"),
        ),
        channel=ModChannel(
            questions_chat_id=os.getenv("questions_chat_id"),
            problems_chat_id=os.getenv("problems_chat_id"),
            suggestions_chat_id=os.getenv("suggestions_chat_id")
        )
    )


config = load_config()
