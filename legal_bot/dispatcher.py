# legal_bot/dispatcher.py

from aiogram import Dispatcher, Router, F
from aiogram.filters import Command, StateFilter
from handlers import start, ask, help, book, faq, cancel_handler
from handlers.book import ConsultationState
from handlers.ask import QuestionState
from handlers.lawyer import lawyer
from logs.logger import setup_logger

logger = setup_logger(__name__)
router = Router()


def setup_dispatcher(dp: Dispatcher):
    # Регистрация общих команд
    router.message.register(start.start_handler, Command("start"))
    router.message.register(ask.ask_handler, Command("ask"))
    router.message.register(faq.faq_handler, Command("faq"))
    router.message.register(help.help_handler, Command("help"))

    # Регистрируем обработчики отмены для разных состояний
    # Регистрируем отмену вопроса
    router.message.register(
        cancel_handler.cancel_question,
        Command("cancel_question"),
        StateFilter(QuestionState.waiting_for_question)
        )

    # Регистрируем отмену записи
    router.message.register(
        cancel_handler.cancel_book,
        Command("cancel_book"))

    # Регистрируем отмену FAQ
    router.message.register(
        cancel_handler.cancel_faq,
        Command("отмена_FAQ"))

    # Обработчики FAQ
    router.callback_query.register(
        faq.faq_callback_handler,
        F.data.startswith("faq_"))

    # Обработчики question
    router.message.register(
        ask.process_question,
        StateFilter(QuestionState.waiting_for_question)
    )
    logger.info("ask.process_question")

    # Обработчики записи на консультацию
    router.message.register(book.consultation_handler, Command("book"))
    router.message.register(book.consultation_handler, F.text == "Записаться на консультацию")
    router.message.register(book.phone_handler, StateFilter(ConsultationState.waiting_for_phone))
    router.message.register(book.name_handler, StateFilter(ConsultationState.waiting_for_name))
    router.message.register(book.email_handler, StateFilter(ConsultationState.waiting_for_email))
    router.message.register(book.topic_book_handler, StateFilter(ConsultationState.waiting_for_topic_client))
    router.message.register(book.lawyer_selected_handler, StateFilter(ConsultationState.waiting_for_lawyer))
    router.callback_query.register(book.lawyer_selected_handler, F.data.startswith("lawyer_"),
                                   StateFilter(ConsultationState.waiting_for_lawyer))
    router.callback_query.register(book.date_handler, F.data.startswith("date_"),
                                   StateFilter(ConsultationState.waiting_for_date))
    router.callback_query.register(book.time_handler, F.data.startswith("time_"),
                                   StateFilter(ConsultationState.waiting_for_time))


    # Если есть модуль для юристов, включаем его:
    # router.include_router(lawyer.router)

    logger.info("Все обработчики бота успешно зарегистрированы")
    dp.include_router(router)
