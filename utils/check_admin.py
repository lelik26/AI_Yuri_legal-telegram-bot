from aiogram import types
from config.config import ADMIN_IDS

def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором."""
    return user_id in ADMIN_IDS

async def check_admin(message: types.Message):
    """Отправляет сообщение, если пользователь не админ."""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет прав для выполнения этой команды.")
        return False
    return True
