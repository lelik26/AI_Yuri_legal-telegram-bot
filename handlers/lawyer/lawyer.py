# from aiogram import types, Router, F
# from datetime import datetime, timedelta
# from aiogram.filters import Command
# from database.repository import get_consultations_by_date
# from legal_bot.keyboards import generate_lawyer_date_keyboard
# from logs.logger import setup_logger
# from database.base import SessionLocal
#
# logger = setup_logger(__name__)
# router = Router()
#
# @router.message(Command("booking_schedule"))
# async def booking_schedule_handler(message: types.Message):
#     """
#     Отправляет юристу inline-клавиатуру с датами ближайших 7 рабочих дней (без выходных).
#     """
#     keyboard = generate_lawyer_date_keyboard()
#     await message.answer("Выберите дату для просмотра расписания консультаций:", reply_markup=keyboard, parse_mode="HTML")
#
# @router.callback_query(lambda c: c.data.startswith("lawyer_date_"))
# async def lawyer_date_callback(callback: types.CallbackQuery):
#     """
#     Обрабатывает выбор даты юристом и показывает список консультаций на эту дату.
#     """
#     selected_date = callback.data.split("_")[-1]  # формат YYYY-MM-DD
#     db = SessionLocal()
#     try:
#         consultations = get_consultations_by_date(db, selected_date)
#         if consultations:
#             response_text = f"📅 <b>Расписание на {selected_date}:</b>\n\n"
#             for cons in consultations:
#                 # Форматируем строку для каждой консультации
#                 response_text += (f"🕒 Время записи: {cons.consultation_time} - Клиент: {cons.name_client}\n"
#                                   f"📞 телефон для связи: {cons.phone_number}\n"
#                                   f"Тема: {cons.question if cons.question else 'не указана'}\n\n")
#         else:
#             response_text = f"На {selected_date} консультации не запланированы."
#     except Exception as e:
#         logger.error("Ошибка получения расписания: %s", str(e))
#         response_text = "Ошибка получения расписания."
#     finally:
#         db.close()
#     await callback.message.edit_text(response_text, parse_mode="HTML")
#     await callback.answer()
