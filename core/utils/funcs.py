import regex
from config import load_config
from core.models.enums import TicketType
from services.db.services.repository import Repo
from core.utils.variables import channel_ids


config = load_config()


async def check_is_rus_word(word):
    """
    Берет name и возвращает:
    True - все символы - русские или тире
    False - иначе
    """

    rus_a, rus_ya = 1072, 1103
    for symbol in word:
        if (ord(symbol.lower()) > rus_ya or ord(symbol.lower()) < rus_a) and symbol != '-':
            return False
    return True


async def validate_name(name: str) -> bool:
    """
    Берет name и возвращает:
    True - имя прошло проверку
    False - имя не прошло проверку
    """
    name_split = name.strip().split()
    if len(name_split) >= 2:
        print(name, all([check_is_rus_word(word) for word in name_split]))
        return all([check_is_rus_word(word) for word in name_split])
    return False


async def validate_group(group_name: str) -> bool:
    """
    Берет group и возвращает:
    True - группа прошла проверку
    False - группа не прошла проверку
    """
    correct_faculties = [
            'АК', 'БМТ', 'ИБМ', 'ИСОТ', 'ИУ', "Л", 'МТ', 'ОЭ', 'ПС', 'СГН', 'СМ',
            'ТБД', 'ФН', 'РК', 'РКТ' ,'РЛ' ,'РТ' ,'Э', 'ЮР', 'ИУК', 'ИК', 'ПОДК',
            'К', 'ЛТ', 'ТБД', 'ТД', 'ТИП', 'ТМО', 'ТМП', 'ТМР', 'ТР' ,'ТСА', 'ТСР',
            'ТСС', 'ТУ', 'ТУС', 'ТЭ']

    for faculty in correct_faculties:
        if group_name.startswith(faculty):
            matched = regex.match(r'[1-9][0-4]?И?\-1?[1-9][1-9](?:Б|А|М)?', group_name[len(faculty):])
            if matched and len(group_name[len(faculty):]) > 3 and matched.group() == group_name[len(faculty):]:
                return True
            return False
    return False


async def message_link(channel_id: int, mes_id: int):
    link = f"https://t.me/c/{abs(channel_id)}/{mes_id}"
    return link


async def choose_id_by_data(data):
    if data["type"] == TicketType.Problem:
        return config


async def add_ticket(data, msg_link, repo: Repo):

    tg_user_id = data["tg_user_id"]
    ticket_text = data["text"]
    ticket_type = data["type"]
    is_anonim = data["is_anonim"]

    if is_anonim:
        return repo.add_ticket(
            tg_user_id, msg_link, ticket_text, ticket_type, is_anonim
        )
    name = data["name"]
    group = data["group"]

    await repo.update_user(tg_user_id, name, group)

    return repo.add_ticket(
        tg_user_id, msg_link, ticket_text, ticket_type, is_anonim, name=name, group=group
    )


async def choose_ch_id(data: dict):
    if data["type"] == TicketType.Problem:
        return channel_ids.problem_channel
    if data["type"] == TicketType.QUESTION:
        return channel_ids.question_channel
    if data["type"] == TicketType.SUGGEST:
        return channel_ids.suggest_channel
