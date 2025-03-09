# services/query_processor.py

from sqlalchemy import func
from database.models import KnowledgeBase
from database.base import SessionLocal
from services.ai_assistant import get_ai_response
from services.send_response import format_response
from logs.logger import setup_logger

logger = setup_logger(__name__)

def process_query(user_id: int, username: str, query: str) -> dict:
    """
    Обрабатывает запрос пользователя пошагово:
      1. Ищем по question с помощью full-text search (tsvector).
      2. Если ничего не найдено — ищем по keyword с использованием ts_rank_cd() и возвращаем ТОП-3.
      3. Если и это не дало результатов — обращаемся к AI.

    Логирует каждый этап.

    Returns:
        dict: Словарь с полями:
              -text: текст ответа или описание вариантов,
              -options (опционально): список ID вариантов для выбора,
              -дополнительные поля (list_steps, references, templates, recommendations),
              -source: источник ответа.
    """
    logger.info("Начинаю обработку запроса от %s (ID: %s): %s", username, user_id, query[:50])

    with SessionLocal() as db:
        # Этап 1: Поиск по полю question с использованием full-text search
        try:
            logger.info("Этап 1: Поиск по вопросу (tsvector на question)")
            result = db.query(KnowledgeBase).filter(
                func.to_tsvector('russian', KnowledgeBase.question)
                .match(query, postgresql_regconfig='russian')
            ).first()
            if result:
                logger.info("✅ Найден ответ по question: %s", result.answer[:50])
                return format_response(result)
        except Exception as e:
            logger.error("Ошибка на этапе 1 (question): %s", str(e))

        # Этап 2: Если ничего не найдено, ищем по keyword с использованием ts_rank_cd
        try:
            logger.info("Этап 2: Поиск по ключевым словам (keyword)")
            results = db.query(KnowledgeBase).filter(
                func.to_tsvector('russian', KnowledgeBase.keyword)
                .match(query, postgresql_regconfig='russian')
            ).order_by(
                func.ts_rank_cd(
                    func.to_tsvector('russian', KnowledgeBase.keyword),
                    func.plainto_tsquery('russian', query)
                ).desc()
            ).limit(1).all()
            if results and len(results) > 0:
                logger.info("Найдено %d вариантов по keyword", len(results))
                return format_response(results)
        except Exception as e:
            logger.error("Ошибка на этапе 2 (keyword): %s", str(e))

        # Этап 3: Если и это не дало результатов, обращаемся к AI
        try:
            logger.info("Этап 3: Обращаюсь к AI")
            ai_response = get_ai_response(query)
            logger.info("Получен ответ от AI")
            return {
                "text": ai_response,
                "law_links": None,
                "document": None,
                "list_steps": None,
                "references": None,
                "templates": None,
                "recommendations": None,
                "source": "ai_assistant"
            }
        except Exception as e:
            logger.error("Ошибка на этапе 3 (AI): %s", str(e))
            return {
                "text": "Извините, произошла ошибка при обработке вашего запроса.",
                "source": "error"
            }
