# from aiogram import types, Router
# from database.repository import update_law_link
# from utils.check_admin import check_admin
#
# router = Router()
#
# @router.message(commands=["update_law"])
# async def update_law_handler(message: types.Message):
#     """Инструкция по обновлению ссылки."""
#     if not await check_admin(message):
#         return
#     await message.answer("🔗 Введите `название документа` и `новую ссылку на закон` через запятую.")
#
# @router.message(lambda message: "," in message.text)
# async def process_law_update(message: types.Message):
#     """Обновляет ссылку на закон в БД."""
#     if not await check_admin(message):
#         return
#
#     try:
#         doc_name, new_link = map(str.strip, message.text.split(",", 1))
#         update_law_link(doc_name, new_link)
#         await message.answer(f"✅ Ссылка для `{doc_name}` обновлена: {new_link}")
#     except Exception as e:
#         await message.answer(f"⚠️ Ошибка при обновлении: {str(e)}")
