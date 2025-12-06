import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

TOKEN = os.getenv("BOT_TOKEN")       # токен из Render
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # твой Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

last_user_by_admin = {}

# Меню помощи
@dp.message(Command("helpme"))
async def help_menu(message: types.Message):
    kb = InlineKeyboardBuilder()
    buttons = [
        "По внешности", "По росту", "По качалке",
        "По пептидам", "По БАД-ам", "Другое…"
    ]
    for b in buttons:
        kb.button(text=b, callback_data=f"type:{b}")
    kb.adjust(2)
    await message.answer("Выберите тип вопроса:", reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith("type:"))
async def handle_type(callback: types.CallbackQuery):
    await callback.message.answer("Хорошо, ожидайте ответа.")
    await callback.answer()
    user_id = callback.from_user.id
    selected = callback.data.split(":", 1)[1]
    await bot.send_message(ADMIN_ID, f"Пользователь {user_id} выбрал категорию: {selected}")

# Пересылка сообщений пользователю
@dp.message(lambda msg: msg.from_user.id != ADMIN_ID)
async def user_msg(message: types.Message):
    user_id = message.from_user.id
    kb = InlineKeyboardBuilder()
    kb.button(text="Ответить", callback_data=f"reply:{user_id}")
    kb.button(text="Игнор", callback_data="ignore")
    kb.adjust(2)

    if message.photo:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id,
                             caption=f"Сообщение от {user_id}", reply_markup=kb.as_markup())
    else:
        await bot.send_message(ADMIN_ID, f"Сообщение от {user_id}:\n{message.text}",
                               reply_markup=kb.as_markup())
    await message.answer("Ваше сообщение отправлено. Ожидайте ответа.")

# Ответ админа
@dp.callback_query(lambda c: c.data.startswith("reply:"))
async def choose_reply(callback: types.CallbackQuery):
    user_id = int(callback.data.split(":", 1)[1])
    last_user_by_admin[callback.from_user.id] = user_id
    await callback.message.answer("Напишите ваш ответ пользователю 👇")
    await callback.answer()

@dp.message(lambda msg: msg.from_user.id == ADMIN_ID)
async def admin_reply(message: types.Message):
    admin_id = message.from_user.id
    if admin_id not in last_user_by_admin:
        await message.answer("Сначала нажмите кнопку «Ответить».")
        return
    target_user = last_user_by_admin[admin_id]
    if message.text:
        await bot.send_message(target_user, message.text)
    await message.answer("Отправлено ✔️")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
