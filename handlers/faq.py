# handler/faq.py

from aiogram import types, Router
from aiogram.fsm.state import State, StatesGroup
from database.repository import fetch_frequent_questions, get_knowledge_by_id
from database.base import SessionLocal
from legal_bot.keyboards import generate_faq_keyboard

from services.send_response import send_response, format_response
from services.generation_text import generate_faq_text

from logs.logger import setup_logger

logger = setup_logger(__name__)
router = Router()


# Состояние для FAQ
class FAQState(StatesGroup):
    waiting_for_faq = State()


async def faq_handler(message: types.Message):
    """
    Обрабатывает команду /faq.
    Показывает список вопросов текстом + кнопки с номерами.
    """
    with SessionLocal() as db:
        faq_entries = fetch_frequent_questions(db, limit=10)

    if not faq_entries:
        await message.answer("❓ В базе нет часто задаваемых вопросов.")
        return

    # Отправляем список вопросов + клавиатуру
    await message.answer(generate_faq_text(faq_entries), parse_mode="HTML")
    await message.answer("📌 <b>Выберите номер вопроса:</b>", parse_mode="HTML", reply_markup=generate_faq_keyboard(faq_entries))



# Функция отрабатывает нажатие кнопки с вопросом
async def faq_callback_handler(callback: types.CallbackQuery):
    """
    Обрабатывает нажатие на кнопку FAQ.
    """
    data = callback.data  # ожидаемый формат "faq_{id}"

    if not data.startswith("faq_"):
        return

    try:
        faq_id = int(data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный идентификатор вопроса.", show_alert=True)
        return

    with SessionLocal() as db:
        result = get_knowledge_by_id(db, faq_id)

    if not result:
        await callback.answer("Вопрос не найден.", show_alert=True)
        return

    # Отправляем ответ через `send_response()`, указывая, что это FAQ
    await send_response(callback.message, format_response(result), is_faq=True)


