# # database/models.py

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, func, Time, ARRAY, Boolean, ForeignKey, event, text
from sqlalchemy.orm import declarative_base
from database.base import Base

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    document = Column(Text, nullable=True)
    list_steps = Column(Text, nullable=True)
    references = Column(Text, nullable=True)
    templates = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    keyword = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())
    search_vector = Column(Text, nullable=True)
    search_vector_keyword = Column(Text, nullable=True)
    is_frequent = Column(Boolean, default=False, nullable=False)


# Функция для вычисления текстового вектора
def update_search_vectors(connection, target):
    # Объединяем нужные поля для поиска. Обычно используют вопрос и ответ.
    combined_text = f"{target.question.lower()}" # {targer.answer}
    target.search_vector = connection.execute(
        text("SELECT to_tsvector('russian', :text)"),
        {'text': combined_text}
    ).scalar()

    # Аналогично для ключевых слов – если нужно
    target.search_vector_keyword = connection.execute(
        text("SELECT to_tsvector('russian', :text)"),
        {'text': target.keyword.lower() if target.keyword else ''}
    ).scalar()


# При вставке нового объекта – вычисляем вектор
@event.listens_for(KnowledgeBase, "before_insert")
def compute_search_vectors_before_insert(mapper, connection, target):
    update_search_vectors(connection, target)

# При обновлении объекта – тоже вычисляем вектор
@event.listens_for(KnowledgeBase, "before_update")
def compute_search_vectors_before_update(mapper, connection, target):
    update_search_vectors(connection, target)

class UserRequest(Base):
    __tablename__ = "user_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    username = Column(Text, nullable=False)
    question = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    username = Column(Text, nullable=False)
    phone_number = Column(Text, nullable=False)
    name_client = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    consultation_date = Column(Date, nullable=True)
    consultation_time = Column(Text, nullable=True)
    name_lawyer = Column(Text, nullable=True)
    lawyer_id = Column(Integer, nullable=True)
    topic_consultation = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class Lawyer(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    description = Column(String)
    experience = Column(Integer, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    start_work = Column(Time, nullable=False)
    end_work = Column(Time, nullable=False)
    appointment_duration = Column(Integer, nullable=False)  # в минутах
    weekends = Column(ARRAY(String), nullable=False)  # например, ["Saturday", "Sunday"]

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class ScheduleConsultation(Base):
    __tablename__ = "schedule_consultations"

    id = Column(Integer, primary_key=True, index=True)
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"), nullable=False)
    consultation_date = Column(Date, nullable=False)
    consultation_time = Column(Time, nullable=False)
    is_free = Column(Boolean, default=True)
    name_client = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    topic_consultation = Column(String, nullable=True)
