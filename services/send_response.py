# services/send_response
from aiogram import types
from legal_bot.keyboards import default_keyboard
from services.split_message import split_message
from templates.templates_text_answer import FINISH_ASK_TEXT, NEXT_FAQ_TEXT


def format_response(result):
    """Форматирует найденный ответ в словарь."""

    return {
        "text": f"✅ <b>Найден ответ на ваш вопрос:</b>\n {result.answer} \n\n",
        "list_steps": f"📌 <b>📝 Возможные пути решения проблемы:</b>\n{result.list_steps}\n\n",
        "templates": f"<b> 📌 📜Список необходимых документов: </b>\n{result.templates}\n\n",
        "references": f"📌 <b>🔗 Ссылки на соответствующие ⚖️ законодательные нормы:</b>\n{result.references}\n\n",
        "recommendations": f"📌 <b>💡 Рекомендации:</b>\n{result.recommendations}\n\n",
        "source": "knowledge_base"
    }

async def send_response(message: types.Message, response: dict, is_faq: bool = False):
    """
    Отправляет пользователю основной ответ и дополнительные данные (если есть).

    :param message: объект сообщения Telegram
    :param response: словарь с данными ответа
    :param is_faq: флаг, указывающий, что это ответ на FAQ
    """

    # Отправляем основной текст, если он есть
    for part in split_message(response.get("text") or ""):
        await message.answer(part, parse_mode="HTML", reply_markup=default_keyboard())

    # Отправляем дополнительные блоки (если они не пустые)
    for key in ["list_steps", "templates", "references", "recommendations"]:
        if response.get(key):
            await message.answer(response[key], parse_mode="HTML", reply_markup=default_keyboard())

    # Отправляем финальное сообщение
    final_text = NEXT_FAQ_TEXT if is_faq else FINISH_ASK_TEXT
    await message.answer(final_text, parse_mode="HTML", reply_markup=default_keyboard())
