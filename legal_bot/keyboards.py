# legal_bot/keyboards.py
from sqlalchemy.orm import Session
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from database.models import Lawyer, ScheduleConsultation
from database.repository import get_available_lawyers, get_free_time_slots
from database.base import SessionLocal
from logs.logger import setup_logger
from config.config import EMOJI_NUMBERS

logger = setup_logger(__name__)

def default_keyboard():
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Записаться на консультацию")]],
        resize_keyboard=True
    )

def phone_keyboard():
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Отправить номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def generate_date_keyboard(db: Session, lawyer: Lawyer):
    """
    Генерирует клавиатуру с ближайшими 10 датами, где есть свободные слоты.
    Формат даты: "dd-mm-YYYY"
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    available_dates = (
        db.query(ScheduleConsultation.consultation_date)
        .filter(ScheduleConsultation.lawyer_id == lawyer.id)
        .filter(ScheduleConsultation.is_free == True)
        .distinct()
        .order_by(ScheduleConsultation.consultation_date)
        .limit(10)
        .all()
    )
    for date_tuple in available_dates:
        date = date_tuple[0]
        day_name = date.strftime("%A")
        formatted_date = date.strftime("%d-%m-%Y")
        button = InlineKeyboardButton(
            text=f"{formatted_date} ({day_name})",
            callback_data=f"date_{formatted_date}"
        )
        keyboard.inline_keyboard.append([button])
    return keyboard if keyboard.inline_keyboard else None

def generate_time_keyboard(date_str: str, lawyer: Lawyer):
    db = SessionLocal()
    try:
        free_slots = get_free_time_slots(db, date_str, lawyer)
        buttons = []
        if free_slots:
            for slot in free_slots:
                buttons.append([InlineKeyboardButton(text=slot, callback_data=f"time_{slot}")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    finally:
        db.close()

def choose_lawyer_keyboard():
    db = SessionLocal()
    try:
        lawyers = get_available_lawyers(db)
        if not lawyers:
            return None
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for lawyer in lawyers:
            keyboard.inline_keyboard.append([InlineKeyboardButton(
                text=f"{lawyer.full_name()} ({lawyer.experience} лет опыта)",
                callback_data=f"lawyer_{lawyer.id}"
            )])
        return keyboard
    finally:
        db.close()

def generate_faq_keyboard(faq_entries):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    row = []
    for i, entry in enumerate(faq_entries, start=1):
        emoji_number = EMOJI_NUMBERS.get(i, f"{i//10}️⃣{i%10}️⃣")
        button = InlineKeyboardButton(text=emoji_number, callback_data=f"faq_{entry.id}")
        row.append(button)
        if len(row) == 5:
            keyboard.inline_keyboard.append(row)
            row = []
    if row:
        keyboard.inline_keyboard.append(row)
    return keyboard
