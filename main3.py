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
ADMIN_ID = 8508142416 

WEB_APP_URL = "https://munavvarovmustafo56-dotcom.github.io/mini.app/"

db = sqlite3.connect("users.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
db.commit()

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 2. MENU
# ==========================================
def main_menu(user_id):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🚀 AI Chat (Oynada)", web_app=types.WebAppInfo(url=WEB_APP_URL)))
    builder.row(types.KeyboardButton(text="🏢 Kompaniya haqida"), types.KeyboardButton(text="🛠 Xizmatlarimiz"))
    builder.row(types.KeyboardButton(text="📱 Bizning kanallar"), types.KeyboardButton(text="📞 Bog'lanish"))
    
    if user_id == ADMIN_ID:
        builder.row(types.KeyboardButton(text="📊 Statistika"))
    return builder.as_markup(resize_keyboard=True)

# ==========================================
# 3. HANDLERS (TUGMALAR)
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    db.commit()
    await message.answer(f"<b>Gelectronics</b> botiga xush kelibsiz, {message.from_user.first_name}! 🚀\nQuyidagi tugmalardan foydalaning:", 
                         reply_markup=main_menu(message.from_user.id), parse_mode="HTML")

@dp.message(F.text == "🏢 Kompaniya haqida")
async def about_handler(message: types.Message):
    text = (
        "<b>🏢 Gelectronics kompaniyasi haqida:</b>\n\n"
        "2020-yilda tashkil etilgan kompaniyamiz hozirda ikki bo'linmadan iborat:\n"
        "1️⃣ <b>G-R-A-N-D Electronics</b> — Servis va avtomatlashtirish.\n"
        "2️⃣ <b>Gelectronics Magazin</b> — Ehtiyot qismlar yetkazib berish.\n\n"
        "🌍 2022-yildan xalqaro loyihalarda ishtirok etib kelmoqdamiz."
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "🛠 Xizmatlarimiz")
async def services_handler(message: types.Message):
    text = (
        "<b>🛠 Bizning xizmatlar:</b>\n\n"
        "✅ Muhandis-elektronik xizmati\n"
        "✅ Muhandis-dasturchi xizmati\n"
        "✅ Texnik jarayonlarni avtomatlashtirish\n"
        "✅ Inverter va murakkab platalar ta'miri\n"
        "✅ Mutaxassislar konsultatsiyasi"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "📞 Bog'lanish")
async def contact_handler(message: types.Message):
    text = (
        "<b>📞 Biz bilan bog'lanish:</b>\n\n"
        "☎️ Telefon: <b>71 200 04 05</b>\n"
        "👨‍💻 Telegram: @gelectronicsuz\n\n"
        "Savollaringiz bo'lsa, AI Chat oynasidan yozishingiz mumkin!"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "📱 Bizning kanallar")
async def channels_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🎬 YouTube", url="https://youtube.com/@smartfaktlar"))
    builder.row(types.InlineKeyboardButton(text="🔵 Telegram", url="https://t.me/gelectronicsuz"))
    await message.answer("Rasmiy kanallarimizga obuna bo'ling:", reply_markup=builder.as_markup())

# ==========================================
# 4. WEB APP VA AI MANTIQI
# ==========================================
@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    user_query = message.web_app_data.data
    sent = await message.answer("AI o'ylamoqda... ⚡️")
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_query}]
        )
        await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, 
                                    text=f"🗨 <b>Savolingiz:</b> {user_query}\n\n🤖 <b>Javob:</b>\n{completion.choices[0].message.content}", 
                                    parse_mode="HTML")
    except:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text="Xatolik yuz berdi.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
