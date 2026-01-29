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
TELEGRAM_TOKEN = "8572454769:AAFkZ4vYlT_WZXv-0VYHhsxSQYUEDQC-GK8"
GROQ_API_KEY = "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"

# !!! DIQQAT: BU YERGA O'ZINGIZNING TELEGRAM ID RAQAMINGIZNI YOZING !!!
# ID raqamingizni bilish uchun Telegramda @userinfobot ga /start deb yozing
ADMIN_ID = 8508142416  # <--- Shu sonni o'zgartiring

# Ma'lumotlar bazasi
db = sqlite3.connect("users.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
db.commit()

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 2. MENU VA TUGMALAR (Admin uchun maxsus)
# ==========================================
def main_menu(user_id):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🤖 AI bilan gaplashish"))
    builder.row(types.KeyboardButton(text="🛠 Servis xizmati"), types.KeyboardButton(text="📱 Bizning kanallar"))
    builder.row(types.KeyboardButton(text="👨‍🎓 Magistratura ishi"))
    
    # FAQAT ADMIN UCHUN TUGMALAR
    if user_id == ADMIN_ID:
        builder.row(types.KeyboardButton(text="📊 Statistika"), types.KeyboardButton(text="📢 Reklama yuborish"))
        
    return builder.as_markup(resize_keyboard=True)

def channel_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🎬 AI Studio (YouTube)", url="https://youtube.com/@smartfaktlar?si=2H3GVICVDs6Qitsi")) 
    builder.row(types.InlineKeyboardButton(text="🔵 G-Electronics (Telegram)", url="https://t.me/gelectronicsuz"))
    return builder.as_markup()

# ==========================================
# 3. BUYRUQLAR
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    db.commit()
    
    await message.answer(
        f"Salom {message.from_user.first_name}! 🚀\nAI Studio yordamchi botiga xush kelibsiz!",
        reply_markup=main_menu(message.from_user.id)
    )

@dp.message(F.text == "📊 Statistika")
async def show_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return # Oddiy foydalanuvchiga javob bermaydi

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    await message.answer(f"📊 Botdan foydalanuvchilar jami soni: {count} ta")

@dp.message(F.text == "📢 Reklama yuborish")
async def start_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Reklama xabarini yuboring. Men uni hamma foydalanuvchilarga tarqataman.")

@dp.message(F.text == "📱 Bizning kanallar")
async def social_channels(message: types.Message):
    await message.answer("Bizning rasmiy kanallarimiz:", reply_markup=channel_menu())

@dp.message()
async def handle_all(message: types.Message):
    # Oddiy AI suhbati
    if message.text and not message.text.startswith("/"):
        sent = await message.answer("O'ylayapman... ⚡️")
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": message.text}]
            )
            await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=completion.choices[0].message.content)
        except:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text="Xatolik...")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
