# services/generation_text.py
from config.config import EMOJI_NUMBERS

def generate_faq_text(faq_entries):
    """
    Формирует текстовое сообщение со списком часто задаваемых вопросов.
    Каждый вопрос пронумерован красивым эмодзи.
    """
    text = "💡 <b>Часто задаваемые вопросы:</b>\n\n"
    for i, entry in enumerate(faq_entries, start=1):
        emoji = EMOJI_NUMBERS.get(i, f"{i}")
        text += f"{emoji} {entry.question}\n"
    return text