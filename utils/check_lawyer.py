from aiogram import types
from config import LAWYER_IDS

def is_lawyer(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором."""
    return user_id in LAWYER_IDS

async def check_lawyer(message: types.Message):
    """Отправляет сообщение, если пользователь не админ."""
    if message.from_user.id not in LAWYER_IDS:
        await message.answer("⛔ У вас нет прав для выполнения этой команды.")
        return False
    return True
