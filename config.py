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
    problem_channel: int
    question_channel: int
    suggest_channel: int
    problem_chat: int
    question_chat: int
    suggest_chat: int


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig


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

            problem_channel=int(os.getenv("problem_channel_id")),
            question_channel=int(os.getenv("question_channel_id")),
            suggest_channel=int(os.getenv("suggest_channel_id")),

            problem_chat=int(os.getenv("problem_chat_id")),
            question_chat=int(os.getenv("question_chat_id")),
            suggest_chat=int(os.getenv("suggest_chat_id"))

    ),
        db=DbConfig(
            name=os.getenv("db_name"),
            password=os.getenv("db_password"),
            address=os.getenv("db_address"),
            user=os.getenv("db_user"),
        ),
    )


config = load_config()
