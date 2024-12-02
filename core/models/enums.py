from enum import Enum


class UserRole(str, Enum):
    BLOCKED = "BLOCKED"
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class TicketType(str, Enum):
    QUESTION = "QUESTION"
    PROBLEM = "PROBLEM"
    SUGGEST = "SUGGEST"
