from config import config


with open(config.swear_words_file, "r", encoding="utf-8") as file:
    swear_words = { line.strip() for line in file }


def escape_swear_words(text: str) -> str:
    for word in swear_words:
        text = text.replace(word, '*' * len(word))
    return text
