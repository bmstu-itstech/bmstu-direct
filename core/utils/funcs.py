import regex


def check_is_rus_word(word):
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


def validate_name(name: str) -> bool:
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

def validate_group(group_name: str) -> bool:
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


def message_link(channel_id: int, mes_id: int):
    link = f"https://t.me/c/{abs(channel_id)}/{mes_id}"
    return link