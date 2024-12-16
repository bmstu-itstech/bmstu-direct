from enum import Enum


class Role(str, Enum):
    BOT       = "bot"
    STUDENT   = "student"
    MODERATOR = "moderator"
