# /tests/test_services.py
import pytest
from services.query_processor import process_query

def fake_get_legal_info(query):
    if "договор" in query.lower():
        return "Информация о договоре"
    return ""

def fake_get_ai_response(query):
    return "Ответ от OpenAI"

@pytest.fixture(autouse=True)
def patch_services(monkeypatch):
    monkeypatch.setattr("legal_bot.services.knowledge_base.get_legal_info", fake_get_legal_info)
    monkeypatch.setattr("legal_bot.services.ai_assistant.get_ai_response", fake_get_ai_response)

def test_process_query_from_knowledge_base():
    answer = process_query("Что такое договор?")
    assert "Информация о договоре" in answer

def test_process_query_from_ai():
    answer = process_query("Как зарегистрировать бизнес?")
    assert "Ответ от OpenAI" in answer
