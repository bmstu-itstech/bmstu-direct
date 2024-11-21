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
    chat_id1: str
    chat_id2: str
    chat_id3: str

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
            chat_id1=os.getenv("chat1_id"),
            chat_id2=os.getenv("chat2_id"),
            chat_id3=os.getenv("chat3_id")
        )
    )


config = load_config()
