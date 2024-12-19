import enum


class Status(str, enum.Enum):
    OPENED      = "Открыт"
    IN_PROGRESS = "В работе"
    CLOSED      = "Закрыт"
