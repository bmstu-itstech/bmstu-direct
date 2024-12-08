import enum


class Category(str, enum.Enum):
    STUDY       = "Учёба"
    DORMITORY   = "Общежитие"
    FOOD        = "Питание"
    MEDICINE    = "Медицина"
    MILITARY    = "Военно-учебный центр"
    ADMISSION   = "Поступление"
    DOCUMENTS   = "Документы"
    SCHOLARSHIP = "Стипендия и выплаты"
    ELECTIVES   = "Внеучебная деятельность"
    OTHER       = "Другое"
