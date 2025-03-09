import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Фикстура для общей подготовки окружения перед тестами (если нужно)."""
    print("\n[SETUP] Запуск всех тестов")
    yield
    print("\n[TEARDOWN] Завершение всех тестов")
