# from aiogram import types, Router
# from database.repository import save_document
# from utils.check_admin import check_admin
#
# router = Router()
#
# @router.message(commands=["add_document"])
# async def add_document_handler(message: types.Message):
#     """Инструкция для загрузки документа."""
#     if not await check_admin(message):
#         return
#     await message.answer("📎 Отправьте документ (PDF, DOCX) с его названием в сообщении.")
#
# @router.message(lambda message: message.document is not None)
# async def save_document_handler(message: types.Message):
#     """Сохраняем документ, если админ отправил файл."""
#     if not await check_admin(message):
#         return
#
#     document = message.document
#     file_name = document.file_name
#     file_path = f"documents/{file_name}"
#
#     await message.bot.download(document, file_path)
#
#     # Сохраняем в БД
#     save_document(file_name, file_path)
#
#     await message.answer(f"✅ Документ `{file_name}` загружен и сохранён.")
