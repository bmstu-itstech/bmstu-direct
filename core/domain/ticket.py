from datetime import datetime

from attr import dataclass

from core.domain.category import Category
from core.domain.issue import Issue
from core.domain.status import Status
from core.domain.student import Student


@dataclass
class Ticket:
    # ID чата с пользователем, откуда поступило заявление.
    owner_chat_id: int

    # Тип заявление пользователя: например, вопрос или проблема.
    issue: Issue

    # Категория (направление) заявления: например, учёба или общежитие.
    category: Category

    # Непосредственно сам текст заявления от студента.
    text: str

    # Информация о студенте-заявителе.
    # Так, если студент указал, что хочет остаться анонимным, данное поле
    # будет равно None.
    owner: Student | None

    # Статус заявления: открыто или закрыто.
    status: Status


@dataclass
class TicketRecord(Ticket):
    # Уникальный ID тикета.
    id: int

    # Время открытия тикета
    opened_at: datetime | None

    # ID сообщения тикета в канале.
    channel_message_id: int | None

    # ID сообщения тикета в группе.
    group_message_id: int | None
