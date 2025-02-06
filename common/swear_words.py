import string
from config import config




with open(config.swear_words_file, "r", encoding="utf-8") as file:
    swear_words = { line.strip() for line in file }


def escape_swear_words(text: str) -> str:
    out = ""
    i = 0
    n = len(text)
    word = ""
    while i <= n:
        if i == n or text[i] in (string.punctuation + string.whitespace):
            len_w = len(word)
            if word.lower() in swear_words:
                out += "*" * len_w
            else:
                out += text[i - len_w : i]
            word = ""
            if i < n:
                out += text[i]
        else:
            word += text[i]
        i += 1
    return out

