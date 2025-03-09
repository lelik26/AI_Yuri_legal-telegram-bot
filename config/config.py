import os

from dotenv import load_dotenv

load_dotenv()

# Список ключей
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# Доступ к базе данных
DATABASE_URL = os.getenv("DATABASE_URL")
MY_SECRET_KEY = os.getenv("MY_SECRET_KEY")
DATA_BASE = os.getenv("DATA_BASE")

# Доступ к таблице
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Максимальное количество символов в телеграмм
MAX_LENGTH_TEXT_TELEGRAM = 4096
MAX_LENGTH_LINE_BUTTON_TELEGRAM = 64

EMOJI_NUMBERS = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
}

DURATION_WORKING_HOUR = 60

# Список администраторов
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
LAWYER_IDS = list(map(int, os.getenv("LAWYER_IDS", "").split(",")))


# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "bot.log"

if not BOT_TOKEN or not OPENAI_API_KEY or not OPENAI_ASSISTANT_ID:
    raise EnvironmentError("Не все обязательные переменные окружения установлены!")
