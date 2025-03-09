import sys
import os

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

from database.base import Base
from database.models import *  # Импорт всех моделей

def include_object(object, name, type_, reflected, compare_to):
    # Игнорируем search_vector при создании миграций
    if type_ == "column" and object.table.name == "knowledge_base" and name == "search_vector":
        return False
    return True

# Конфиг Alembic
config = context.config

# Настраиваем логирование из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Устанавливаем target_metadata для автогенерации миграций
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запускаем миграции в offline-режиме (без подключения к БД)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object  # <-- Добавляем фильтр здесь тоже!
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Запускаем миграции в online-режиме (с подключением к БД)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object  # <-- Добавляем фильтр
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
