# 📜 Юридический Telegram-бот

## 📌 Описание проекта
Данный Telegram-бот предоставляет юридические консультации в автоматическом режиме. Он анализирует вопросы пользователей, обращается к базе знаний или к нейросетевому ассистенту (OpenAI) и выдаёт развернутые ответы с юридическими ссылками.

## ⚙️ Функционал
- 📩 Поддержка команд:
  - `/start` — начало работы с ботом
  - `/help` — справка по использованию
  - `/ask` — задать юридический вопрос
  - `/book` — запись на консультацию
  - `/faq` — часто задаваемы вопросы
- 📚 Поиск ответов в базе знаний ( PostgreSQL, SQLAlchemy,Alembic, Google Sheets)
- 🤖 Ответы на юридические вопросы с использованием базы знаний и OpenAI Assistants API.
- 📝 Запись на консультацию
- 📊 Логирование и анализ обращений пользователей

## 🛠 Технологии
- `Python 3.12`
- `aiogram` — асинхронный фреймворк для Telegram
- `requests`, `httpx` — работа с API
- `openai` — обработка естественного языка
- `gspread` — интеграция с Google Sheets
- `pytest` — тестирование

## 🚀 Установка и запуск
### 1. Клонирование репозитория
```bash
git clone https://github.com/lelik26/legal-telegram-bot.git
cd legal-telegram-legal_bot
```
### 2. Установка зависимостей
```bash
python -m venv .venv
source .venv/bin/activate  # для Linux/Mac
.venv\Scripts\activate    # для Windows
pip install -r requirements.txt
```
### 3. Настройка переменных окружения
Создайте `.env` файл и добавьте:
```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_database_url
OPENAI_ASSISTANT_ID=your_OPENAI_ASSISTANT_ID
GOOGLE_CREDENTIALS_PATH=your_GOOGLE_CREDENTIALS_PATH.json

```
### 4. Запуск бота
```bash
python legal_bot/legal_bot.py
```

## 📦 Развёртывание (Railway + Docker)
1. Создайте аккаунт на [Railway](https://railway.app/)
2. Подключите репозиторий
3. Railway автоматически найдёт `Dockerfile` и развернёт бота

## 🛠 Тестирование
```bash
pytest tests/
```
## Структура проекта

- `database/`: Управление базой данных, импорт данных и репозитории
- `hadlers/`: Основные обработчики команд
- `legal_bot/`: Основная логика работы бота
- `migrations/`: Миграции базы данных Alembic
- `services/`: Функции работы бота
- `config/`: Настройки окружения
- `README.md`: Это руководство

![Снимок экрана 2025-03-09 в 19.54.07.png](../../../../var/folders/kt/2sxlvzfd2xndcbn2ymyx8lym0000gp/T/TemporaryItems/NSIRD_screencaptureui_skaxNr/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-03-09%20%D0%B2%2019.54.07.png)


## 📌 TODO / Будущие улучшения

✅ Подключение админ-панели для управления базой знаний.

✅ Поддержка голосовых запросов.

🔜 Интеграция с CRM для юристов.

## 📞 Контакты и поддержка

Если у вас есть вопросы или предложения, создайте issue в репозитории или напишите на email: support@yourdomain.com.

## 📄 Лицензия
Проект распространяется под лицензией MIT.

