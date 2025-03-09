# /tests/test_bot.py
import pytest
from aiogram import types
from handlers import start

@pytest.mark.asyncio
async def test_start_handler():
    # Создаём фиктивное сообщение для команды /start
    message = types.Message(
        message_id=1,
        date=None,
        chat=types.Chat(id=123, type='private'),
        from_user=types.User(id=1, is_bot=False, first_name="TestUser", username="testuser"),
        text="/start"
    )
    # Тестовый запуск обработчика; в реальных тестах следует замокать метод answer
    await start.start_handler(message)
