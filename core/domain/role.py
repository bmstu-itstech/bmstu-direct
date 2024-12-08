from enum import Enum


class Role(str, Enum):
    STUDENT   = "student"
    MODERATOR = "moderator"
