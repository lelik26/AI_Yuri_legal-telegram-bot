# handlers/book.py
from datetime import datetime, timedelta

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from database.base import SessionLocal
from database.repository import save_consultation, get_lawyer_by_id, get_free_time_slots, generate_schedule
from handlers.lawyer import lawyer
from legal_bot.keyboards import (
    phone_keyboard,
    generate_date_keyboard,
    choose_lawyer_keyboard,
    generate_time_keyboard
)
from config.config import DURATION_WORKING_HOUR
from logs.logger import setup_logger

logger = setup_logger(__name__)
router = Router()

class ConsultationState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_name = State()
    waiting_for_email = State()
    waiting_for_topic_client = State()
    waiting_for_lawyer = State()
    waiting_for_date = State()
    waiting_for_time = State()

async def consultation_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    logger.info(f"Пользователь {username} (ID: {user_id}) начал запись на консультацию")
    await message.answer(
        "📞 <b>Шаг 1 из 7</b> - Номер телефона\n\nОтправьте номер (используйте кнопку ниже).\n\n"
        "<i>Для отмены записи используйте /cancel_book </i>",
        parse_mode="HTML",
        reply_markup=phone_keyboard()
    )
    await state.set_state(ConsultationState.waiting_for_phone)

async def phone_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    phone_number = message.contact.phone_number if message.contact else message.text.strip()
    logger.info(f"Пользователь {username} (ID: {user_id}) номер: {phone_number}")
    await state.update_data(phone=phone_number)
    await message.answer(
        "📧 <b>Шаг 2 из 7</b> - Введите ваше ИМЯ:\n\n"
        "<i>Для отмены записи используйте /cancel_book </i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ConsultationState.waiting_for_name)

async def name_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    name_client = message.text.strip()
    logger.info(f"Пользователь {username} (ID: {user_id}) имя: {name_client}")
    await state.update_data(name_client=name_client)
    await message.answer(
        "📧 <b>Шаг 3 из 7</b> - Введите ваш email (или 'нет'):\n\n"
        "<i>Для отмены записи используйте /cancel_book </i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ConsultationState.waiting_for_email)

async def email_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    email = message.text.strip()
    if email.lower() == "нет":
        email = None
        logger.info(f"Пользователь {username} не указал email")
    else:
        logger.info(f"Пользователь {username} указал email: {email}")
    await state.update_data(email=email)
    await message.answer(
        "📧 <b>Шаг 4 из 7</b> - Введите описание проблемы или темы записи (или напишите 'лично'):\n\n"
        "<i>Для отмены записи используйте /cancel_book </i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ConsultationState.waiting_for_topic_client)

async def topic_book_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    topic_client = message.text.strip()
    if topic_client.lower() == "лично" or topic_client == "":
        topic_client = None
        logger.info(f"Пользователь {username} не указал тему консультации")
    else:
        logger.info(f"Пользователь {username} указал тему консультации: {topic_client}")
    await state.update_data(topic_client=topic_client)

    keyboard = choose_lawyer_keyboard()
    if keyboard is None:
        await message.answer("❌ Нет доступных юристов.", parse_mode="HTML")
        return
    await message.answer(
        "⚖️ <b>Шаг 5 из 7</b> - Выберите юриста:\n\n"
        "<i>Для отмены записи используйте /cancel_book </i>",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await state.set_state(ConsultationState.waiting_for_lawyer)

async def lawyer_selected_handler(callback: types.CallbackQuery, state: FSMContext):
    # Из callback_data получаем lawyer_id
    lawyer_id = int(callback.data.split("_")[1])
    db = SessionLocal()
    try:

        lawyer = get_lawyer_by_id(db, lawyer_id)
        if not lawyer:
            await callback.answer("Ошибка! Юрист не найден.", show_alert=True)
            return

        # Сохраняем идентификатор и полное имя юриста в состоянии
        await state.update_data(lawyer_id=lawyer_id, lawyer_full_name=lawyer.full_name())
        generate_schedule(db, lawyer)
        date_keyboard = generate_date_keyboard(db, lawyer)
        await callback.message.answer(
            f"⚖️ <b>Вы выбрали:</b> {lawyer.full_name()}\n"
            f"График работы: {lawyer.start_work.strftime('%H:%M')} - {lawyer.end_work.strftime('%H:%M')}\n"
            f"Обед: 12:00-13:00\n"
            f"Выходные: {', '.join(lawyer.weekends)}\n\n"
            "<b>Шаг 6 из 7 - Выберите дату консультации:</b>",
            parse_mode="HTML",
            reply_markup=date_keyboard
        )
        await state.set_state(ConsultationState.waiting_for_date)
    finally:
        db.close()
    await callback.answer()

async def date_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор даты, проверяет, что это не выходной у юриста,
    и генерирует клавиатуру со свободными временными слотами.
    Формат даты: "dd-mm-YYYY".
    """
    selected_date_str = callback.data.split("_")[1]
    try:
        selected_date = datetime.strptime(selected_date_str, "%d-%m-%Y").date()

    except ValueError:
        await callback.message.answer("Неверный формат даты.", parse_mode="HTML")
        return

    logger.info(f"Выбрана дата: {selected_date_str}")

    data = await state.get_data()
    lawyer_id = data.get("lawyer_id")

    if not lawyer_id:
        await callback.message.answer("❌ Ошибка: не выбран юрист.")
        return

    db = SessionLocal()
    try:
        lawyer = get_lawyer_by_id(db, lawyer_id)
        if not lawyer:
            await callback.message.answer("❌ Ошибка! Юрист не найден.")
            return

        # Проверяем, не является ли выбранная дата выходным для юриста.

        weekday_mapping = {
            "Monday": "Понедельник",
            "Tuesday": "Вторник",
            "Wednesday": "Среда",
            "Thursday": "Четверг",
            "Friday": "Пятница",
            "Saturday": "Суббота",
            "Sunday": "Воскресенье"
        }
        weekday_russian = weekday_mapping.get(selected_date.strftime("%A"))
        if lawyer.weekends and weekday_russian in lawyer.weekends:
            await callback.message.answer(f"⛔ {weekday_russian} - выходной у юриста. Выберите другую дату.",
                                          parse_mode="HTML")
            return

        free_slots = get_free_time_slots(db, selected_date_str, lawyer)
        if not free_slots:
            await callback.message.answer("🔴 На эту дату нет доступного времени. Выберите другую дату.",
                                          parse_mode="HTML")
            return

        time_keyboard = generate_time_keyboard(selected_date_str, lawyer)
        await callback.message.answer(
            "🕒 <b>Шаг 7 из 7</b> - Выберите свободное время:\n\n"
            "<i>Для отмены записи используйте /cancel_book</i>",
            parse_mode="HTML",
            reply_markup=time_keyboard
        )
        await state.update_data(date=selected_date_str)
        await state.set_state(ConsultationState.waiting_for_time)
    finally:
        db.close()
    await callback.answer()

async def time_handler(callback: types.CallbackQuery, state: FSMContext):
    selected_time = callback.data.split("_")[1]  # Формат "HH:MM"
    logger.info(f"Выбрано время: {selected_time}")
    data = await state.get_data()
    phone_number = data.get("phone")
    name_client = data.get("name_client")
    email = data.get("email")
    topic_client = data.get("topic_client")
    selected_date = data.get("date")
    lawyer_id = data.get("lawyer_id")
    lawyer_full_name = data.get("lawyer_full_name")
    user_id = callback.from_user.id
    username = callback.from_user.username or "Без имени"
    await state.update_data(time=selected_time)
    db = SessionLocal()
    try:
        success = save_consultation(
            db,
            user_id=user_id,
            username=username,
            phone_number=phone_number,
            name_client=name_client,
            email=email,
            date=selected_date,
            time=selected_time,
            lawyer_id=lawyer_id,
            name_lawyer=lawyer_full_name,
            topic_consultation=topic_client
        )
        if success:
            # Рассчитываем время окончания приёма, добавляя длительность приёма
            end_time_obj = (datetime.strptime(selected_time, "%H:%M") +
                            timedelta(minutes=DURATION_WORKING_HOUR)).time()
            confirmation = (
                f"✅ <b>Уважаемый(ая) {name_client}!</b> Ваша консультация запланирована.\n\n"
                f"📅 <b>Дата:</b> {selected_date}\n"
                f"🕒 <b>Время:</b> {selected_time} - {end_time_obj.strftime('%H:%M')}\n"
                f"📞 <b>Телефон:</b> {phone_number}\n"
                f"📧 <b>Email:</b> {email if email else 'не указан'}\n"
                f"📝 <b>Тема консультации:</b> {topic_client if topic_client else 'не указана'}\n"
                f"👨‍⚖️ <b>Ваш юрист:</b> {lawyer_full_name}\n\n"
                "Наш специалист свяжется с вами для подтверждения записи."
            )
            await callback.message.answer(confirmation, parse_mode="HTML")
        else:
            await callback.message.answer(
                "❌ <b>Ошибка при записи на консультацию.</b>\nПопробуйте ещё раз или свяжитесь с нами.",
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Ошибка при сохранении: {str(e)}")
        await callback.message.answer(
            "❌ <b>Ошибка при записи на консультацию.</b>\nПопробуйте ещё раз или свяжитесь с нами.",
            parse_mode="HTML"
        )
    finally:
        db.close()
    await state.clear()
    await callback.answer()
    logger.info(f"Процесс записи для {username} завершён")
