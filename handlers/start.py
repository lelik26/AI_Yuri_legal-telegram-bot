# /handlers/start.py
from aiogram import types
from legal_bot.keyboards import default_keyboard
from templates.templates_text_answer import START_TEXT


async def start_handler(message: types.Message):
    user_name = message.from_user.first_name

    await message.answer(

        f"👋Привет, 🤝{user_name}!\n"
        f"{START_TEXT}",
        parse_mode="HTML",
        reply_markup=default_keyboard()
    )


