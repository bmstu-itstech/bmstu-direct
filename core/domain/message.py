from dataclasses import dataclass
from typing import NamedTuple


class MessageID(NamedTuple):
    # Уникальный ID чата в Telegram.
    chat_id: int

    # Уникальный ID сообщения в рамках чата Telegram.
    message_id: int


@dataclass
class MessagePair:
    source_id: MessageID
    copy_id: MessageID
    ticket_id: int
