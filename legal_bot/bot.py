# /legal_bot/bot.py
import asyncio


from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from legal_bot.dispatcher import setup_dispatcher
from logs.logger import setup_logger

logger = setup_logger(__name__)




async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начало работы"),
        BotCommand(command="ask", description="Задать юридический вопрос"),
        BotCommand(command="book", description="Записаться на консультацию"),
        BotCommand(command="faq", description="Часто задаваемые вопросы"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="cancel", description="Отменить операцию")
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=BOT_TOKEN)
    logger.info("память до")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    logger.info("память после")

    setup_dispatcher(dp)
    await set_default_commands(bot)

    logger.info("Бот запущен")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())