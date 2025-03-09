# database/repository.py

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, not_
from database.models import KnowledgeBase, UserRequest, Consultation, Lawyer, ScheduleConsultation

# ------------------- Функции для работы с таблицей KnowledgeBase -------------------

def fetch_knowledge_base(db: Session, question: str, multiple: bool = True):
    # Поиск по вопросу с использованием ilike (поиск по подстроке без учёта регистра)
    query_filter = KnowledgeBase.question.ilike(f"%{question.lower().strip()}%")
    if multiple:
        return db.query(KnowledgeBase).filter(query_filter).all()
    return db.query(KnowledgeBase).filter(query_filter).first()


def fetch_frequent_questions(db: Session, limit: int = 10):
    return db.query(KnowledgeBase).filter(KnowledgeBase.is_frequent == True).limit(limit).all()

def get_knowledge_by_id(db: Session, answer_id: int):
    return db.query(KnowledgeBase).filter(KnowledgeBase.id == answer_id).first()


def add_knowledge_entry(db: Session, entry: dict):
    db_entry = KnowledgeBase(**entry)
    db.add(db_entry)
    db.commit()

# Новая функция поиска с использованием полнотекстового поиска
def search_knowledge_base(db, search_text):
    # Очистите строку: заменяем дефисы и лишние пробелы, приводим к нижнему регистру
    clean_text = search_text.replace('-', ' ').strip().lower()
    # Используем websearch_to_tsquery вместо plainto_tsquery
    ts_query = func.websearch_to_tsquery('russian', clean_text)
    results = db.query(KnowledgeBase)\
                .filter(KnowledgeBase.search_vector.op('@@')(ts_query))\
                .all()
    return results

# ------------------- Функции для работы с запросами пользователей -------------------

def log_user_request(db: Session, user_id: int, username: str, question: str):
    user_request = UserRequest(user_id=user_id, username=username, question=question)
    db.add(user_request)
    db.commit()
    db.refresh(user_request)
    return user_request

# ------------------- Функции бронирования и консультаций -------------------

def book_slot(db: Session, lawyer_id: int,date_str: str, time_str: str, client_data: dict):
    target_date = datetime.strptime(date_str, "%d-%m-%Y").date()
    target_time = datetime.strptime(time_str, "%H:%M").time()
    slot = db.query(ScheduleConsultation).filter_by(
        lawyer_id=lawyer_id,
        consultation_date=target_date,
        consultation_time=target_time
    ).first()
    if slot and slot.is_free:
        slot.is_free = False
        slot.name_client = client_data.get("name_client")
        slot.phone_number = client_data.get("phone_number")
        slot.email = client_data.get("email")
        slot.topic_consultation = client_data.get("topic_consultation")
        db.commit()
        return True
    return False

def save_consultation(db: Session, user_id: int, username: str, phone_number: str,
                      name_client: str, email: str, date: str, time: str,
                      lawyer_id: int, name_lawyer: str ,topic_consultation: str = None):
    """
    Сохраняет консультацию и обновляет график (ScheduleConsultation) через book_slot.
    Используются форматы: дата - "dd-mm-YYYY", время - "HH:MM".
    """
    client_data = {
        "name_client": name_client,
        "phone_number": phone_number,
        "email": email,
        "topic_consultation": topic_consultation
    }
    # Если слот уже занят, бронирование не производится.
    if not book_slot(db, lawyer_id, date, time, client_data):
        return False

    consultation = Consultation(
        user_id=user_id,
        username=username,
        phone_number=phone_number,
        name_client=name_client,
        email=email,
        consultation_date=datetime.strptime(date, "%d-%m-%Y").date(),
        consultation_time=time,
        name_lawyer=name_lawyer,
        lawyer_id=lawyer_id,  # Предполагается, что поле lawyer_id добавлено в модель Consultation
        topic_consultation=topic_consultation,
        created_at=datetime.utcnow()
    )
    db.add(consultation)
    db.commit()
    return True

# ------------------- Функции для работы с юристами и расписанием -------------------

def get_all_lawyers(db: Session):
    return db.query(Lawyer).all()


def get_lawyer_by_id(db: Session, lawyer_id: int):
    return db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()


def get_available_lawyers(db: Session):
    # Здесь %А может быть ошибкой, если вы ожидаете английское название дня, замените на "%A"
    today = datetime.today().strftime("%A")
    return db.query(Lawyer).filter(not_(Lawyer.weekends.op('@>')([today]))).all()

def generate_schedule(db: Session, lawyer):
    """
    Генерирует и обновляет расписание юриста на ближайшие 5 рабочих дней (с понедельника по пятницу).
    """
    today = datetime.today().date()
    start_date = today + timedelta(days=(14 - today.weekday()))  # ближайший понедельник
    end_date = start_date + timedelta(days=4) # Пятница
    for day in range((end_date - start_date).days + 1):
        target_date = start_date + timedelta(days=day)
        if target_date.strftime("%A") in lawyer.weekends:
            continue
        start_work = datetime.combine(target_date, lawyer.start_work)
        end_work = datetime.combine(target_date, lawyer.end_work)
        lunch_start = datetime.combine(target_date, datetime.strptime("12:00", "%H:%M").time())
        lunch_end = datetime.combine(target_date, datetime.strptime("13:00", "%H:%M").time())
        appointment_duration = timedelta(minutes=lawyer.appointment_duration)
        current_time = start_work
        while current_time + appointment_duration <= end_work:
            if lunch_start <= current_time < lunch_end:
                current_time = lunch_end  # Пропускаем обеденный перерыв
            exists = db.query(ScheduleConsultation).filter_by(
                lawyer_id=lawyer.id,
                consultation_date=target_date,
                consultation_time=current_time.time()
            ).first()
            if not exists:
                db.add(ScheduleConsultation(
                    lawyer_id=lawyer.id,
                    consultation_date=target_date,
                    consultation_time=current_time.time(),
                    is_free=True
                ))
            current_time += appointment_duration
        db.commit()

def get_free_time_slots(db: Session, date_str: str, lawyer):
    target_date = datetime.strptime(date_str, "%d-%m-%Y").date()
    free_slots = db.query(ScheduleConsultation).filter(
        ScheduleConsultation.lawyer_id == lawyer.id,
        ScheduleConsultation.consultation_date == target_date,
        ScheduleConsultation.is_free == True
    ).all()
    return [slot.consultation_time.strftime("%H:%M") for slot in free_slots]

