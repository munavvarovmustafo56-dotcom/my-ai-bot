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

db = sqlite3.connect("users.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
db.commit()

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 2. MENU (WEB APP-SIZ)
# ==========================================
def main_menu(user_id):
    builder = ReplyKeyboardBuilder()
    # Endi AI Chat tugmasi shunchaki matn, oyna ochilmaydi
    builder.row(types.KeyboardButton(text="🤖 AI bilan suhbat"))
    builder.row(types.KeyboardButton(text="🏢 Kompaniya haqida"), types.KeyboardButton(text="🛠 Xizmatlarimiz"))
    builder.row(types.KeyboardButton(text="📱 Bizning kanallar"), types.KeyboardButton(text="📞 Bog'lanish"))
    
    if user_id == ADMIN_ID:
        builder.row(types.KeyboardButton(text="📊 Statistika"), types.KeyboardButton(text="📢 Reklama"))
        
    return builder.as_markup(resize_keyboard=True)

# ==========================================
# 3. HANDLERS
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    db.commit()
    await message.answer(
        f"Salom, {message.from_user.first_name}! 🚀\n<b>Gelectronics</b> botiga xush kelibsiz.\n"
        f"Menga savolingizni yuboring, men AI yordamida javob beraman!", 
        reply_markup=main_menu(message.from_user.id), 
        parse_mode="HTML"
    )

# AI BILAN MULOQOT (CHATNI O'ZIDA)
@dp.message(F.text & ~F.text.startswith("/"))
async def ai_chat_handler(message: types.Message):
    # Menyudagi tugmalarni AI filtrlashi kerak
    if message.text in ["🤖 AI bilan suhbat", "🏢 Kompaniya haqida", "🛠 Xizmatlarimiz", "📱 Bizning kanallar", "📞 Bog'lanish", "📊 Statistika", "📢 Reklama"]:
        if message.text == "🤖 AI bilan suhbat":
            await message.answer("Savolingizni yozing, men javob berishga tayyorman! 👇")
        elif message.text == "🏢 Kompaniya haqida":
            await message.answer("<b>Gelectronics</b> — 2020-yildan beri sanoat elektronikasi ta'miri bilan shug'ullanadi.", parse_mode="HTML")
        elif message.text == "🛠 Xizmatlarimiz":
            await message.answer("🛠 Inverterlar, stanoklar va murakkab platalar ta'miri.")
        elif message.text == "📞 Bog'lanish":
            await message.answer("☎️ Tel: 71 200 04 05\n👨‍💻 Telegram: @gelectronicsuz")
        elif message.text == "📱 Bizning kanallar":
            builder = InlineKeyboardBuilder()
            builder.row(types.InlineKeyboardButton(text="🎬 YouTube", url="https://youtube.com/@smartfaktlar"))
            await message.answer("Bizni kuzatib boring:", reply_markup=builder.as_markup())
        return

    # Har qanday boshqa matn uchun AI javob beradi
    sent = await message.answer("AI o'ylamoqda... ⚡️")
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": message.text}]
        )
        await bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=sent.message_id, 
            text=completion.choices[0].message.content
        )
    except:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text="Xatolik yuz berdi.")

# ==========================================
# 4. ISHGA TUSHIRISH
# ==========================================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
