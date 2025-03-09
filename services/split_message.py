# services/split_message

from config import MAX_LENGTH_TEXT_TELEGRAM, MAX_LENGTH_LINE_BUTTON_TELEGRAM

def split_message(text ):

    """Разбивает длинный текст на части, чтобы избежать ошибки Telegram."""
    return [text[i:i + MAX_LENGTH_TEXT_TELEGRAM] for i in range(0, len(text), MAX_LENGTH_TEXT_TELEGRAM)]

def split_text(text):
    """Разбивает текст на строки не длиннее max_length, оставляя целые слова."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 > MAX_LENGTH_LINE_BUTTON_TELEGRAM:
            lines.append(current_line)
            current_line = word
        else:
            current_line += " " + word if current_line else word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)