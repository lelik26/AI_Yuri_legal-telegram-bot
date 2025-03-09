# database/google_to_postgres.py
import os
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import func, text

from database.base import SessionLocal
from database.models import KnowledgeBase

# Загружаем .env из config/
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
load_dotenv(dotenv_path)

# Получаем путь к ключу
base_dir = os.path.dirname(os.path.dirname(__file__))  # AI_Yuri_legal-telegram-bot
creds_path = os.path.join(base_dir, os.getenv("GOOGLE_CREDENTIALS_PATH"))

# Настройка Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

spreadsheet = client.open("knowledgeDataBaseLegalRealEstate")
worksheet = spreadsheet.worksheet("knowledge_base")
rows = worksheet.get_all_records()

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def transfer_data_to_postgres():
    with SessionLocal() as db:
        counter = 0
        batch_size = 20  # Коммитим каждые 20 строк

        for row in rows:
            question = row.get("question", "").strip()
            if not question:
                continue

            entry_data = {
                "question": question,
                "answer": row.get("answer", ""),
                "document": row.get("document", ""),
                "list_steps": row.get("list_steps", ""),
                "references": row.get("references", ""),
                "templates": row.get("templates", ""),
                "recommendations": row.get("recommendations", ""),
                "is_frequent": row.get("is_frequent", "").strip().lower() == "true",
                "keyword": row.get("keyword", "")
            }

            existing_entry = db.query(KnowledgeBase).filter_by(question=question).first()

            if existing_entry:
                for field, value in entry_data.items():
                    setattr(existing_entry, field, value)
            else:
                new_entry = KnowledgeBase(**entry_data)
                db.add(new_entry)

                # Update search vectors using PostgreSQL functions
                filled_entry_data_str = f"question: {new_entry.question} answer: {new_entry.answer}"
                new_entry.search_vector = db.execute(func.to_tsvector('russian', filled_entry_data_str))
                new_entry.search_vector_keyword = db.execute(func.to_tsvector('russian', new_entry.keyword))

            counter += 1
            if counter % batch_size == 0:
                db.commit()

            print(f"✔️ Обработана запись: {question}")

        db.commit()  # Финальный коммит

if __name__ == "__main__":
    transfer_data_to_postgres()
    print("✅ Данные успешно перенесены из Google Sheets в PostgreSQL")
