class Error:
    err_in_db = "Произошла ошибка при работе с базой данных, попробуйте повторить действие или вернитесь к нему позднее."
    blocked = "Вы заблокированы системой, по важным вопросам обращайтесь @unrelcy"
    ticket_closed = "Это обращение уже закрыто"
    undefined_behaviour = "Не понимаю, что вы хотите сделать"
    no_permission = "У нас нет доступа к этому функционалу"
    no_func = "Функционал находится в разработке"


class Ticket:
    hello_message = "Здравствуйте, это бот для обратнйо связи студентов МГТУ им. Н.Э. Баумана "
    ask_is_new = "Вы хотите дополнить уже созданное обращение или создать новое?"
    ask_type = "Пожалуйста выберите тип обращения."
    ask_category = "Пожалуйста выберите категорию обращения."
    ask_anonim = "Вы хотите отправить анонимное обращение?"
    ask_name = "Пожалуйста введите ваше имя и фамилию."
    retry_ask_name = "Напишите имя и фамилию через пробел, не используя лишние символы."
    ask_group = "Пожалуйста введите вашу группу."
    retry_ask_group = "Группа не соответствует образцу, введите полное название группы\n Например ИУ7-14Б."
    ask_text = "Пожалуйста введите текст обращения."
    successful_sent = "Обращение успешно отправлено, ожидайте.\nТакже вы можете создать новое оп кнопкам на клавиатуре."
    answer_received = "Ответ получен.\nОн вас устраивает? нажмите соответствующую кнопку в меню."
    ask_contact = "Пожалуйста оставьте ваш контакт (номер телефона / почта / ссылка на соцсеть)."


class Btn:
    back = 'Назад.'
    make_ticket = 'Создать обращение'
    help = r'Помощь'
    my_tickets = 'Мои обращения'
    yes = 'Да'
    no = 'Нет'
    question = 'Вопрос'
    problem = 'Проблема'
    suggest = 'Предложение'

    # admin_buttons
    edit_types = "edit_types"
    edit_categories = "edit_categories"
    block_user = "block user"
    unblock_user = "unblock user"
    close_ticket = 'close_ticket'
    open_ticket = 'open_ticket'
    make_moderator = "make_moderator"
    make_admin = "make_admin"


cats = [
    'Учёба',
    'Общежитие',
    'Питание',
    'Медицина',
    'Военная кафедра',
    'Поступление',
    'Документы',
    'Стипендия и выплаты',
    'Внеучебная деятельность',
    'Другое'
]


def make_ticket_text(data: dict) -> str:
    text = f'''
    Отрытое заявление
    тип: {data["type"]}
    категория: {data["category"]}'''

    if data["is_anonim"]:
        text += '\n Анонимное.\n\n'
    else:
        text += f'\n от {data["name"]} \nиз группы {data["group"]}\n\n'

    text += data["text"]

    return text
