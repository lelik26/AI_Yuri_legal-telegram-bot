# handler/ask

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from legal_bot.keyboards import default_keyboard
from logs.logger import setup_logger
from services.query_processor import process_query

from services.send_response import send_response

from templates.templates_text_answer import WELCOME_TEXT

logger = setup_logger(__name__)


# Create state for question waiting
class QuestionState(StatesGroup):
    waiting_for_question = State()

async def ask_handler(message: types.Message, state: FSMContext):
    """
    Обрабатывает команду /ask.
    Если сообщение содержит только команду, просит ввести вопрос.
    Если сообщение содержит текст после команды, обрабатывает его как вопрос.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"

    logger.info(f"Пользователь {username} (ID: {user_id}) использовал команду /ask")

    # Если сообщение содержит только команду /ask
    if message.text.strip() == "/ask":
        await message.answer(
            f"{WELCOME_TEXT}",
            parse_mode="HTML",
            reply_markup=default_keyboard()
        )
        await state.set_state(QuestionState.waiting_for_question)
        logger.info(f"Пользователь {username} (ID: {user_id}) ожидает вопрос")
        return

    # Если команда с текстом — сразу обрабатываем
    query = message.text[5:].strip() if message.text.startswith("/ask ") else message.text.strip()
    await process_user_query(message, state, user_id, username, query)


async def process_question(message: types.Message, state: FSMContext):
    """
    Обрабатывает вопрос пользователя, когда он находится в состоянии ожидания вопроса.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"

    query = message.text.strip()  # Удаляем лишние пробелы
    if not query:
        await message.answer("❌ Вопрос не может быть пустым. Пожалуйста, введите ваш вопрос.")
        return

    logger.info(f"Получен вопрос от {username} (ID: {user_id}): {query[:50]}...")
    await process_user_query(message, state, user_id, username, query)

async def process_user_query(message: types.Message, state: FSMContext, user_id: int, username: str, query: str):
    """
    Общая функция для обработки запроса и отправки ответа пользователю.
    """
    logger.info("🔍 Обрабатываю вопрос от %s (ID: %s)", username, user_id)
    await message.answer(
        f"📝 <b>Получен вопрос:</b> <i>{query[:50]}{'...' if len(query) > 50 else ''}</i>\n\n"
        "⏳ Обрабатываю ваш запрос...",
        parse_mode="HTML"
    )

    try:
        response = process_query(user_id, username, query)
        logger.info(f"Вопрос от {username} (ID: {user_id}) успешно обработан")

        # Используем универсальную функцию отправки
        await send_response(message, response, is_faq=False)

    except Exception as e:
        logger.error(f"Ошибка при обработке вопроса: {str(e)}")
        await message.answer(
            "❌ <b>Произошла ошибка при обработке вашего вопроса.</b>\n"
            "Попробуйте переформулировать вопрос или повторите попытку позже.",
            parse_mode="HTML",
            reply_markup=default_keyboard()
        )






