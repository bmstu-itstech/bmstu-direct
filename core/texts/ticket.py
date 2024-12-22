from datetime import datetime

import pybars
from core.domain import TicketRecord
from common.repository import compiler


greet = "\n".join((
    "👋 Привет, Бауманец!",
    "Рады видеть тебя в нашем боте! Здесь ты можешь:",
    "🔹 Задать любые вопросы, которые тебя волнуют.",
    "🔹 Сообщить о возникшей проблеме.",
    "🔹 Предложить свою идею.",
))

create_ticket = \
    "Чтобы создать обращение, просто нажми кнопку ниже."

choice_issue = "\n".join((
    "Выбери тип обращения:",
    "🔧 Проблема – расскажи, что требует решения.",
    "❓ Вопрос – задай интересующий тебя вопрос.",
    "💡 Предложение – поделись своими идеями и инициативами!",
))

choice_category = \
    "Выбери направление, с которым связано твоё обращение."

choice_privacy = "\n".join((
    "🤫 Хотите отправить обращение анонимно?",
    "Конфиденциальность – наш лучший друг после вас!"
))

input_full_name = "\n".join((
    "✍️ Напиши своё полное ФИО",
    "Пожалуйста, укажи имя и фамилию, и если есть — добавь отчество.",
    "Пример: Иванов Иван Инванович"
))


input_study_group = \
    "🎓 Напиши номер своей учебной группы. Формат ввода: ИУ13-13Б."

input_text = \
    "📩 Опиши ниже свой вопрос или проблему:"

choice_approve = \
    "👀 Проверь, всё ли введено правильно. Подтверждаешь данные?"


def ticket_sent(ticket_id: int) -> str:
    return f"Твоё обращение отправлено! Ему присвоили номер #{ticket_id}"


ticket_channel_template = compiler.compile("""
Обращение #{{ticket.id}}
=================================
📌 Тип: {{as_tag ticket.issue}}
📂 Категория: {{as_tag ticket.category}}
👤 Отправитель: {{#if ticket.owner}}{{ticket.owner}}{{else}}анонимно{{/if}}
🕒 Дата отправки: {{as_date ticket.opened_at}}
=================================
📩 Текст обращения:
{{ticket.text}}
""")


def ticket_channel(ticket: TicketRecord) -> str:
    return ticket_channel_template(
        {
            "ticket": ticket,
        },
        helpers={
            "as_tag": as_tag,
            "as_date": as_date,
        }
    )


def as_tag(this, s) -> str:
    return "#" + s.lower().replace(" ", "")


def as_date(this, dt: datetime, date_format: str = None) -> str:
    return datetime.strftime(dt, date_format or "%d.%m.%Y %H:%M:%S")
