import enum


class Issue(str, enum.Enum):
    QUESTION   = "Вопрос"
    PROBLEM    = "Проблема"
    SUGGESTION = "Предложение"
