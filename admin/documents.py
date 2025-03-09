# import os
# from aiogram import types, Router
# from aiogram.types import FSInputFile
# from database.repository import save_document, fetch_document_path, delete_entry, list_entries
# from utils.check_admin import check_admin
#
# router = Router()
#
# @router.message(commands=["list_entries"])
# async def list_entries_handler(message: types.Message):
#     """Вывод списка загруженных документов."""
#     if not await check_admin(message):
#         return
#
#     entries = list_entries()
#     if not entries:
#         await message.answer("📂 В базе пока нет документов.")
#     else:
#         text = "📜 **Список документов:**\n" + "\n".join([f"🔹 {e[0]} – {e[1]}" for e in entries])
#         await message.answer(text, parse_mode="Markdown")
#
# # 📎 Добавление документа
# @router.message(commands=["add_document"])
# async def add_document_handler(message: types.Message):
#     """Инструкция для загрузки документа."""
#     if not await check_admin(message):
#         return
#     await message.answer("📎 Отправьте документ (PDF, DOCX) с его названием в сообщении.")
#
# @router.message(lambda message: message.document is not None)
# async def save_document_handler(message: types.Message):
#     """Сохраняем документ в папке и записываем путь в БД."""
#     if not await check_admin(message):
#         return
#
#     document = message.document
#     file_name = document.file_name
#     file_path = f"documents/{file_name}"
#
#     # Загружаем документ в папку
#     os.makedirs("documents", exist_ok=True)  # Создаём папку, если её нет
#     await message.bot.download(document, file_path)
#
#     # Записываем путь в БД
#     save_document(file_name, file_path)
#
#     await message.answer(f"✅ Документ `{file_name}` загружен и сохранён в базе данных.")
#
# # 📜 Отправка документа пользователю
# @router.message(commands=["get_document"])
# async def get_document_handler(message: types.Message):
#     """Отправляет документ пользователю из папки."""
#     file_name = message.text.split(maxsplit=1)[-1]
#     file_path = fetch_document_path(file_name)
#
#     if file_path and os.path.exists(file_path):
#         await message.answer_document(document=FSInputFile(file_path))
#     else:
#         await message.answer("❌ Документ не найден.")
#
#
# # ❌ Удаление  документа
# @router.message(commands=["delete_entry"])
# async def delete_entry_handler(message: types.Message):
#     """Удаление записи."""
#     if not await check_admin(message):
#         return
#     await message.answer("✏️Введите название документа для удаления.")
#
# @router.message()
# async def process_delete_entry(message: types.Message):
#     """Обрабатывает удаление записи."""
#     if not await check_admin(message):
#         return
#
#     file_name = message.text.strip()
#     delete_entry(file_name)
#     await message.answer(f"✅ Запись `{file_name}` удалена.")
#
#
