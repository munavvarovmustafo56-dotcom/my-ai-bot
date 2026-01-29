import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from groq import Groq

# ==========================================
# 1. SOZLAMALAR (YANGILANGAN)
# ==========================================
# Yangi tokeningiz va ID-raqamingiz o'rnatildi
TELEGRAM_TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
GROQ_API_KEY = "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"
ADMIN_ID = 8508142416  # Sizning ID raqamingiz

WEB_APP_URL = "https://munavvarovmustafo56-dotcom.github.io/mini.app/"

# Logging - xatoliklarni kuzatish uchun
logging.basicConfig(level=logging.INFO)

# Ma'lumotlar bazasi
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
    # Web App orqali AI Chat
    builder.row(types.KeyboardButton(text="🚀 AI Chat (Oynada)", web_app=types.WebAppInfo(url=WEB_APP_URL)))
    builder.row(types.KeyboardButton(text="🏢 Kompaniya haqida"), types.KeyboardButton(text="🛠 Xizmatlarimiz"))
    builder.row(types.KeyboardButton(text="📱 Bizning kanallar"), types.KeyboardButton(text="📞 Bog'lanish"))
    
    # Faqat siz ko'radigan tugmalar
    if user_id == ADMIN_ID:
        builder.row(types.KeyboardButton(text="📊 Statistika"), types.KeyboardButton(text="📢 Reklama"))
        
    return builder.as_markup(resize_keyboard=True)

# ==========================================
# 3. HANDLERS (TUGMALAR)
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    db.commit()
    await message.answer(
        f"Salom, {message.from_user.first_name}! 🚀\n<b>Gelectronics</b> botiga xush kelibsiz.\nSavollaringizni AI Chat oynasida yozishingiz mumkin!", 
        reply_markup=main_menu(message.from_user.id), 
        parse_mode="HTML"
    )

@dp.message(F.text == "🏢 Kompaniya haqida")
async def about(message: types.Message):
    text = (
        "<b>🏢 Gelectronics kompaniyasi</b>\n\n"
        "2020-yilda tashkil etilgan. Kompaniya texnologik jarayonlarni dasturlash, "
        "avtomatlashtirish va murakkab elektronika ta'miri bilan shug'ullanadi.\n\n"
        "🌍 2022-yildan xalqaro loyihalarni amalga oshirib kelmoqda."
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "🛠 Xizmatlarimiz")
async def services(message: types.Message):
    text = (
        "<b>🛠 Bizning xizmatlar:</b>\n"
        "• Inverterlar va stanoklar ta'miri\n"
        "• Muhandis-dasturchi xizmati\n"
        "• Avtomatlashtirish xizmatlari"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "📞 Bog'lanish")
async def contact(message: types.Message):
    await message.answer("☎️ Telefon: 71 200 04 05\n👨‍💻 Telegram: @gelectronicsuz")

@dp.message(F.text == "📊 Statistika")
async def stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        await message.answer(f"📊 Jami foydalanuvchilar: {count} ta")

# ==========================================
# 4. WEB APP VA AI MANTIQI
# ==========================================
@dp.message(F.web_app_data)
async def web_app_handler(message: types.Message):
    user_query = message.web_app_data.data
    sent = await message.answer("AI o'ylamoqda... ⚡️")
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_query}]
        )
        await bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=sent.message_id, 
            text=f"🗨 <b>Savol:</b> {user_query}\n\n🤖 <b>Javob:</b>\n{completion.choices[0].message.content}",
            parse_mode="HTML"
        )
    except:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text="AI band.")

# ==========================================
# 5. TOZALOVCHI VA ISHGA TUSHIRISH
# ==========================================
async def main():
    # ENG MUHIM QISMI: Conflict xatosini yo'qotadi
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("--- BOT TOZALANDI VA ISHGA TUSHMOQDA ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
