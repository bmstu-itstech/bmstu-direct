from dataclasses import dataclass

from core.domain.role import Role


@dataclass
class User:
    chat_id: int
    role: Role
