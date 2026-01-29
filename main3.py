import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from groq import Groq

# ==========================================
# 1. SOZLAMALAR
# ==========================================
TELEGRAM_TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
GROQ_API_KEY = "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"
ADMIN_ID = 8508142416  # @userinfobot orqali olingan ID raqamingiz

# GitHub Pages'dagi Web App manzili
WEB_APP_URL = "https://munavvarovmustafo56-dotcom.github.io/mini.app/"

# Ma'lumotlar bazasi
db = sqlite3.connect("users.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
db.commit()

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 2. MENU (Web App bilan)
# ==========================================
def main_menu(user_id):
    builder = ReplyKeyboardBuilder()
    
    # 🤖 AI Chat endi Web App oynasida ochiladi
    builder.row(types.KeyboardButton(
        text="🚀 AI Chat (Oynada)", 
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    ))
    
    builder.row(types.KeyboardButton(text="🏢 Kompaniya haqida"), types.KeyboardButton(text="🛠 Xizmatlarimiz"))
    builder.row(types.KeyboardButton(text="📱 Bizning kanallar"), types.KeyboardButton(text="📞 Bog'lanish"))
    
    if user_id == ADMIN_ID:
        builder.row(types.KeyboardButton(text="📊 Statistika"))
        
    return builder.as_markup(resize_keyboard=True)

# ==========================================
# 3. HANDLERS
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    db.commit()
    
    welcome_text = (
        f"Salom, {message.from_user.first_name}! 🚀\n"
        f"<b>Gelectronics</b> rasmiy botiga xush kelibsiz.\n\n"
        f"Biz bilan texnologiyalar olami yanada yaqin!"
    )
    await message.answer(welcome_text, reply_markup=main_menu(message.from_user.id), parse_mode="HTML")

# WEB APP'DAN KELGAN XABARNI QABUL QILISH
@dp.message(F.web_app_data)
async def web_app_handler(message: types.Message):
    user_query = message.web_app_data.data
    sent = await message.answer("AI o'ylamoqda... ⚡️")
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_query}]
        )
        ai_res = completion.choices[0].message.content
        await bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=sent.message_id, 
            text=f"🗨 <b>Savolingiz:</b> {user_query}\n\n🤖 <b>Javob:</b>\n{ai_res}",
            parse_mode="HTML"
        )
    except:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text="AI hozirda band, birozdan so'ng urinib ko'ring.")

@dp.message(F.text == "🏢 Kompaniya haqida")
async def about_handler(message: types.Message):
    about_text = (
        "<b>🏢 Gelectronics kompaniyasi haqida:</b>\n\n"
        "2020-yilda tashkil etilgan kompaniyamiz hozirda ikki bo'linmadan iborat:\n"
        "1️⃣ <b>G-R-A-N-D Electronics</b> — Texnologik jarayonlarni avtomatlashtirish va servis.\n"
        "2️⃣ <b>Gelectronics Magazin</b> — Sifatli ehtiyot qismlar yetkazib berish.\n\n"
        "✅ 2022-yildan xalqaro loyihalarda ishtirok etib kelmoqdamiz."
    )
    await message.answer(about_text, parse_mode="HTML")

@dp.message(F.text == "🛠 Xizmatlarimiz")
async def services_handler(message: types.Message):
    services_text = (
        "<b>🛠 Bizning xizmatlar:</b>\n\n"
        "• Muhandis-elektronik xizmati\n"
        "• Muhandis-dasturchi xizmati\n"
        "• Texnik jarayonlarni avtomatlashtirish\n"
        "• Mutaxassislar konsultatsiyasi\n\n"
        "📞 Tel: 71 200 04 05"
    )
    await message.answer(services_text, parse_mode="HTML")

@dp.message(F.text == "📱 Bizning kanallar")
async def channels_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🎬 YouTube (Smart Faktlar)", url="https://youtube.com/@smartfaktlar"))
    builder.row(types.InlineKeyboardButton(text="🔵 Telegram (Gelectronics)", url="https://t.me/gelectronicsuz"))
    await message.answer("Bizning rasmiy kanallarimiz:", reply_markup=builder.as_markup())

@dp.message(F.text == "📊 Statistika")
async def stats_handler(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        await message.answer(f"📊 Botdan foydalanuvchilar soni: {count} ta")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

