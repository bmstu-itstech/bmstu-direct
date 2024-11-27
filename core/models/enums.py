from enum import IntEnum


class UserRole(IntEnum):
    Blocked = -1
    User = 0
    Moderator = 1
    Admin = 2


class TicketType(IntEnum):
    Question = 0
    Problem = 1
    Suggest = 2