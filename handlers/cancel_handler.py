from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from logs.logger import setup_logger
from legal_bot.keyboards import default_keyboard

logger = setup_logger(__name__)


# Универсальный обработчик отмены
async def cancel_handler(message: types.Message, state: FSMContext, action: str, command: str):
    """
    Универсальная функция отмены состояния (вопроса, записи на консультацию, FAQ).

    :param message: Сообщение от пользователя
    :param state: Состояние FSMContext
    :param action: Название действия (вопрос, запись, FAQ)
    :param command: Команда для повторного запуска (ask, book, faq)
    """
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    current_state = await state.get_state()

    if current_state is not None:
        await state.clear()
        logger.info(f"Пользователь {username} (ID: {user_id}) отменил {action}")
        await message.answer(
            f"🚫 <b>{action.capitalize()} отменен.</b>\n"
            f"Вы можете начать заново с команды /{command}.",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove() if command == "book" else default_keyboard()
        )
    else:
        await message.answer(f"❌ <b>Нет активных {action.lower()} для отмены.</b>", parse_mode="HTML")


# Обработчики отмены с передачей аргументов в `cancel_handler`
async def cancel_question(message: types.Message, state: FSMContext):
    await cancel_handler(message, state, "режим вопроса", "ask")


async def cancel_book(message: types.Message, state: FSMContext):
    await cancel_handler(message, state, "запись", "book")


async def cancel_faq(message: types.Message, state: FSMContext):
    await cancel_handler(message, state, "режим FAQ", "faq")
