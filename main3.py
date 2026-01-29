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

logging.basicConfig(level=logging.INFO)

# Ma'lumotlar bazasi (Foydalanuvchilar va statistika uchun)
db = sqlite3.connect("users.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
db.commit()

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 2. PREMIUM KLAVIATURA
# ==========================================
def main_menu(user_id):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🤖 AI Professional Yordamchi"))
    builder.row(types.KeyboardButton(text="🏢 Kompaniya Haqida"), types.KeyboardButton(text="🛠 Xizmat Ko'rsatish"))
    builder.row(types.KeyboardButton(text="📱 Bizning Kanallar"), types.KeyboardButton(text="📞 Bog'lanish"))
    
    if user_id == ADMIN_ID:
        builder.row(types.KeyboardButton(text="📊 Statistika"), types.KeyboardButton(text="📢 Reklama Tarqatish"))
        
    return builder.as_markup(resize_keyboard=True)

# ==========================================
# 3. KOMPANIYA MA'LUMOTLARI (PREMIUM KONTENT)
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    db.commit()
    welcome_text = (
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>! 🚀\n\n"
        f"<b>Gelectronics</b> — sanoat elektronikasi va yuqori texnologiyalar olamiga xush kelibsiz.\n"
        f"Menga savolingizni yuboring yoki quyidagi menyudan foydalaning."
    )
    await message.answer(welcome_text, reply_markup=main_menu(message.from_user.id), parse_mode="HTML")

@dp.message(F.text == "🏢 Kompaniya Haqida")
async def about_handler(message: types.Message):
    about_text = (
        "<b>🏢 Gelectronics Kompaniyasi haqida ma'lumot:</b>\n\n"
        "Kompaniyamiz 2020-yilda o'z faoliyatini boshlagan bo'lib, hozirda ikki asosiy yo'nalishda peshqadamlik qilmoqda:\n\n"
        "1️⃣ <b>G-R-A-N-D Electronics</b> — Texnologik jarayonlarni avtomatlashtirish, muhandislik yechimlari va servis xizmati.\n"
        "2️⃣ <b>Gelectronics Magazin</b> — Sifatli sanoat elektronikasi ehtiyot qismlari savdosi.\n\n"
        "🌟 2022-yildan beri xalqaro darajadagi loyihalarda ishtirok etib, sanoat korxonalariga innovatsion yechimlar taqdim etib kelmoqdamiz."
    )
    await message.answer(about_text, parse_mode="HTML")

@dp.message(F.text == "🛠 Xizmat Ko'rsatish")
async def services_handler(message: types.Message):
    services_text = (
        "<b>🛠 Bizning Premium Xizmatlar:</b>\n\n"
        "✅ <b>Muhandis-elektronik:</b> Murakkab platalar, inverterlar va stanoklar ta'miri.\n"
        "✅ <b>Muhandis-dasturchi:</b> Sanoat kontrollerlarini (PLC) dasturlash va boshqaruv tizimlarini yaratish.\n"
        "✅ <b>Avtomatlashtirish:</b> Ishlab chiqarish jarayonlarini to'liq avtomatlashtirish.\n"
        "✅ <b>Konsultatsiya:</b> Korxonalar uchun texnik ekspertiza va yechimlar."
    )
    await message.answer(services_text, parse_mode="HTML")

@dp.message(F.text == "📞 Bog'lanish")
async def contact_handler(message: types.Message):
    contact_text = (
        "<b>📞 Aloqa Ma'lumotlari:</b>\n\n"
        "☎️ Markaziy telefon: <b>71 200 04 05</b>\n"
        "👨‍💻 Administrator: @gelectronicsuz\n"
        "📍 Manzil: Bizning servis markazimiz yirik korxonalar va xususiy mijozlar uchun xizmat ko'rsatadi."
    )
    await message.answer(contact_text, parse_mode="HTML")

@dp.message(F.text == "📱 Bizning Kanallar")
async def channels_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🎬 YouTube (Smart Faktlar)", url="https://youtube.com/@smartfaktlar"))
    builder.row(types.InlineKeyboardButton(text="🔵 Telegram Kanal", url="https://t.me/gelectronicsuz"))
    await message.answer("Bizning ijtimoiy tarmoqlardagi faoliyatimizni kuzatib boring:", reply_markup=builder.as_markup())

# ==========================================
# 4. PROFESSIONAL AI CHAT VA ADMIN
# ==========================================
@dp.message(F.text == "📊 Statistika")
async def stats_handler(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        await message.answer(f"📊 <b>Botdan foydalanuvchilar soni:</b> {count} ta", parse_mode="HTML")

@dp.message(F.text)
async def ai_message_handler(message: types.Message):
    # Agar foydalanuvchi menyudagi tugmalardan birini bosgan bo'lsa, AI ishga tushmaydi
    if message.text in ["🤖 AI Professional Yordamchi", "🏢 Kompaniya Haqida", "🛠 Xizmat Ko'rsatish", "📱 Bizning Kanallar", "📞 Bog'lanish", "📊 Statistika", "📢 Reklama Tarqatish"]:
        if message.text == "🤖 AI Professional Yordamchi":
            await message.answer("Savolingizni yozing, Gelectronics AI sizga texnik yordam berishga tayyor! 👇")
        return

    # AI javob berish jarayoni
    sent = await message.answer("🔍 <i>Gelectronics AI tahlil qilmoqda...</i>", parse_mode="HTML")
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Sen Gelectronics kompaniyasining aqlli yordamchisisan. Sanoat elektronikasi, inverterlar va stanoklar haqida chuqur bilimga egasan."},
                {"role": "user", "content": message.text}
            ]
        )
        await bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=sent.message_id, 
            text=completion.choices[0].message.content,
            parse_mode="Markdown"
        )
    except Exception as e:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text="Hozirda tizim band. Iltimos, birozdan so'ng urinib ko'ring.")

# ==========================================
# 5. ISHGA TUSHIRISH (MAX KAFOLAT)
# ==========================================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
