# services/ai_assistant.py
import re
import logging
import openai
import traceback
from typing import Optional
import  config.config
import config.system_prompt


logger = logging.getLogger(__name__)



def clear_ai_response(text: str) -> str:
    """
        Очищает текст ответа от лишних аннотаций.
        """
    return re.sub(r"【[^】]+】", "", text).strip()

def get_ai_response(user_message: str) -> Optional[str]:
    try:
        if not user_message or len(user_message) > 4000:
            raise ValueError("Некорректный запрос: пустое сообщение или превышена длина 4000 символов")

        # Инициализация клиента OpenAI
        client = openai.OpenAI(api_key=config.config.OPENAI_API_KEY)

        # Используем уже существующий Assistant.
        assistant_id = config.config.OPENAI_ASSISTANT_ID
        instructions = config.system_prompt.SYSTEM_PROMPT
        # Предполагается, что в настройках ассистента уже прописаны:
        # 1. Системная инструкция (указана в Playground)
        # 2. База знаний с ID "vs_67c13a7425548191ba20b82812e9b89f"
        # Поэтому здесь дополнительных настроек не требуется.


        # 1. Создаем новый поток (thread) для OpenAI
        thread = client.beta.threads.create()

        # 2. Добавляем сообщение пользователя в Thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        # 3. Запускаем Run для обработки запроса ассистентом.
        # Параметр instructions можно использовать для дополнительного уточнения, если требуется
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=instructions
        )

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]

            if assistant_messages:
                last_message = assistant_messages[-1]
                if last_message.content and last_message.content[0].text:
                    return clear_ai_response(last_message.content[0].text.value)
                else:
                    logger.warning("Ответ ассистента пустой или не содержит текст.")
                    return "Ответ не найден"
        return f"Статус обработки: {run.status}"

    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {str(e)}\n{traceback.format_exc()}")
        return "Произошла внутренняя ошибка. Попробуйте снова."
