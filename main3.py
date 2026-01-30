import asyncio
import logging
import sqlite3
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from groq import Groq
from aiohttp import web

# 1. SOZLAMALAR
TELEGRAM_TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
GROQ_API_KEY = "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"
ADMIN_ID = 8508142416 
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

# Ma'lumotlar bazasi
db = sqlite3.connect("users.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
db.commit()

# --- RENDERNI ALDASH UCHUN KICHIK SERVER ---
async def handle(request):
    return web.Response(text="Gelectronics Bot is Active!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"--- RENDER UCHUN WEB SERVER {PORT} PORTIDA YONDI ---")

# --- BOT TUGLAMALARI ---
def main_menu(user_id):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🚀 AI Chat (Oynada)"))
    builder.row(types.KeyboardButton(text="🏢 Kompaniya haqida"), types.KeyboardButton(text="🛠 Xizmatlarimiz"))
    builder.row(types.KeyboardButton(text="📱 Bizning kanallar"), types.KeyboardButton(text="📞 Bog'lanish"))
    if user_id == ADMIN_ID:
        builder.row(types.KeyboardButton(text="📊 Statistika"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    db.commit()
    await message.answer(f"Assalomu alaykum <b>{message.from_user.first_name}</b>!\nGelectronics AI xizmatiga xush kelibsiz!", 
                         reply_markup=main_menu(message.from_user.id), parse_mode="HTML")

@dp.message(F.text == "📊 Statistika")
async def stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        await message.answer(f"📊 Botdan foydalanuvchilar soni: {count} ta")

@dp.message(F.text)
async def ai_handler(message: types.Message):
    if message.text in ["🚀 AI Chat (Oynada)", "🏢 Kompaniya haqida", "🛠 Xizmatlarimiz", "📱 Bizning kanallar", "📞 Bog'lanish", "📊 Statistika"]:
        # Agar bu tugmalar bo'lsa, AI ga yubormaymiz
        if message.text == "🏢 Kompaniya haqida":
            await message.answer("Gelectronics — Sanoat elektronikasi va avtomatlashtirish markazi.")
        return

    # Har qanday boshqa matnni AI tahlil qiladi
    msg = await message.answer("🔍 <i>AI o'ylamoqda...</i>", parse_mode="HTML")
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": message.text}],
            model="llama-3.3-70b-versatile",
        )
        await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, 
                                    text=chat_completion.choices[0].message.content)
    except:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="Xato yuz berdi. Qaytadan urinib ko'ring.")

# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    # Bir vaqtning o'zida ham botni, ham veb-serverni yoqamiz
    asyncio.create_task(start_web_server())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
