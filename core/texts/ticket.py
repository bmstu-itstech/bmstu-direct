from core.domain import TicketRecord

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


def ticket_channel(ticket: TicketRecord) -> str:
    return "\n".join((
        f"Обращение #{ticket.id}",
         "=================================",
        f"Статус: {as_tag(ticket.status)}",
        f"Тип заявления: {as_tag(ticket.issue)}",
        f"Категория: {as_tag(ticket.category)}",
        f"Заявитель: {ticket.owner if ticket.owner is not None else 'анонимно'}",
         "=================================",
        ticket.text,
    ))


def as_tag(s: str) -> str:
    return "#" + s.lower().replace(" ", "")
