from services.ai_assistant import get_ai_response

def fake_openai_response(_):
    return "Ответ от OpenAI"

def test_get_ai_response(monkeypatch):
    # Подмена функции get_ai_response в модуле services.ai_assistant
    monkeypatch.setattr("services.ai_assistant.get_ai_response", fake_openai_response)
    response = get_ai_response("Тестовый вопрос")
    assert response == "Ответ от OpenAI"
