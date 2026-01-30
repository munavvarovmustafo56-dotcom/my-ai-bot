import asyncio
import logging
import sqlite3
import os
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiohttp import web

# --- SOZLAMALAR ---
TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40" # Tokeningiz
ADMIN_ID = 8508142416 
PORT = int(os.environ.get("PORT", 8080))

# Web App manzili (Renderdagi saytingiz linki)
# DIQQAT: Bu yerga o'z Render URLingizni to'g'ri yozishingiz kerak!
WEB_APP_URL = "https://my-ai-bot-iu2e.onrender.com" 

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==========================================
# 1. RENDER UCHUN SERVER (WEB APP + KEEP ALIVE)
# ==========================================
async def handle_webapp(request):
    # Bu funksiya boyagi index.html faylini ochib beradi
    return web.FileResponse('./index.html')

async def start_web_server():
    app = web.Application()
    # Asosiy sahifada index.html ochiladi
    app.router.add_get('/', handle_webapp)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"🚀 SERVER {PORT} PORTIDA ISHLAMOQDA. WEB APP TAYYOR!")

# ==========================================
# 2. DATABASE (BAZA)
# ==========================================
db = sqlite3.connect("gelectronics_webapp.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, fullname TEXT, username TEXT)")
db.commit()

# ==========================================
# 3. TUGMALAR (WEB APP TUGMASI BILAN)
# ==========================================
def main_menu():
    # Maxsus Web App tugmasi
    web_app_btn = KeyboardButton(text="🚀 Ilovani ochish (Web App)", web_app=WebAppInfo(url=WEB_APP_URL))
    
    # Oddiy tugmalar
    stats_btn = KeyboardButton(text="📊 Statistika")
    
    # Tugmalarni joylash
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [web_app_btn], # Katta tugma
            [stats_btn]    # Pastki tugma
        ],
        resize_keyboard=True
    )
    return keyboard

# ==========================================
# 4. BOT LOGIKASI
# ==========================================

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Bazaga yozish
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, fullname, username) VALUES (?, ?, ?)", 
                       (message.from_user.id, message.from_user.full_name, message.from_user.username))
        db.commit()
    except:
        pass

    text = (
        f"👋 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
        f"💎 <b>Gelectronics AI</b> ilovasiga xush kelibsiz.\n"
        f"Barcha xizmatlar va AI yordamchi endi bitta ilovada!\n\n"
        f"👇 <b>Pastdagi tugmani bosib ilovaga kiring:</b>"
    )

    # GIF animatsiya (Agar xohlasangiz)
    await message.answer_animation(
        animation="https://i.pinimg.com/originals/e8/50/74/e850742a78601c4fb8b79b6999a0d816.gif",
        caption=text,
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@dp.message(F.text == "📊 Statistika")
async def stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        await message.answer(f"📈 <b>Foydalanuvchilar soni:</b> {count} ta", parse_mode="HTML")
    else:
        await message.answer("Ilovani ochish uchun tepadagi tugmani bosing 👆")

# ==========================================
# 5. ISHGA TUSHIRISH
# ==========================================
async def main():
    # 1. Web serverni (index.html ni) yoqamiz
    asyncio.create_task(start_web_server())
    
    # 2. Botni yoqamiz
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")
