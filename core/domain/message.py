from dataclasses import dataclass


@dataclass
class Message:
    # ID группы в Telegram.
    chat_id: int | None

    # ID сообщения в группе в Telegram.
    message_id: int | None

    # ID сообщения в ЛС с пользователем
    # ID чата с пользователем можно получить из соответсвующего тикета
    owner_message_id: int

    # ID сообщения в ЛС пользователя, на которое сообщение является ответом.
    reply_to_message_id: int | None

    # ID тикета
    ticket_id: int


@dataclass
class MessageRecord(Message):
    _id: int
