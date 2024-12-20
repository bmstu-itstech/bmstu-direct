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

input_full_name = \
    "Введи своё ФИО полностью, чтобы мы знали, с кем в случае чего можно было связаться."

input_study_group = \
    "Введи свою учебную группу в формате ИУ13-13Б."

input_text = \
    "Расскажи, в чём суть твоего обращения."

choice_approve = \
    "Подтверждаешь введённые данные?"


def ticket_sent(ticket_id: int) -> str:
    return f"Твоё обращение отправлено! Ему присвоили номер #{ticket_id}"


ticket_channel_template = compiler.compile("""
Обращение #{{ticket.id}}
=================================
Статус: {{as_tag ticket.status}}
Тип заявления: {{as_tag ticket.issue}}
Категория: {{as_tag ticket.category}}
Заявитель: {{#if ticket.owner}}{{ticket.owner}}{{else}}анонимно{{/if}}
=================================
{{ticket.text}}
""")


def ticket_channel(ticket: TicketRecord) -> str:
    return ticket_channel_template(
        {
            "ticket": ticket,
        },
        helpers={"as_tag": as_tag}
    )


def as_tag(this, s) -> str:
    return "#" + s.lower().replace(" ", "")

