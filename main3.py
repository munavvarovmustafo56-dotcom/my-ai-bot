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
ADMIN_ID = 562143567  # O'zingizning Telegram ID'ingizni bilsangiz shu yerga yozing

# Ma'lumotlar bazasini sozlash
db = sqlite3.connect("users.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
db.commit()

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 2. MENU VA TUGMALAR
# ==========================================
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🤖 AI bilan gaplashish"))
    builder.row(types.KeyboardButton(text="🛠 Servis xizmati"), types.KeyboardButton(text="📱 YouTube Kanallar"))
    builder.row(types.KeyboardButton(text="👨‍🎓 Magistratura ishi"), types.KeyboardButton(text="📊 Statistika"))
    return builder.as_markup(resize_keyboard=True)

def youtube_menu():
    builder = InlineKeyboardBuilder()
    # Sizning asosiy kanalingiz
    builder.row(types.InlineKeyboardButton(text="🎬 AI Studio (Asosiy)", url="https://www.youtube.com/@AIStudio")) 
    # Botni ishlatish uchun kanal (namuna)
    builder.row(types.InlineKeyboardButton(text="🤖 Bot Yangiliklari", url="https://t.me/your_channel"))
    return builder.as_markup()

# ==========================================
# 3. BUYRUQLAR
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Foydalanuvchini bazaga qo'shish
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    db.commit()
    
    await message.answer(
        f"Salom {message.from_user.first_name}! 🚀\nAI Studio yordamchi botiga xush kelibsiz!",
        reply_markup=main_menu()
    )

@dp.message(F.text == "📱 YouTube Kanallar")
async def yt_channels(message: types.Message):
    await message.answer("Bizning ijtimoiy tarmoqdagi kanallarimiz:", reply_markup=youtube_menu())

@dp.message(F.text == "📊 Statistika")
async def show_stats(message: types.Message):
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    await message.answer(f"📊 Botdan foydalanuvchilar jami soni: {count} ta")

@dp.message(F.text == "👨‍🎓 Magistratura ishi")
async def master_work(message: types.Message):
    text = "Mavzu: 'Technological processes for increasing energy efficiency and developing an intelligent control system'."
    await message.answer(text)

@dp.message(F.text == "🛠 Servis xizmati")
async def service_info(message: types.Message):
    await message.answer("Biz har xil inverterlar va elektronika qurilmalarini tuzatamiz.")

@dp.message()
async def ai_chat(message: types.Message):
    if message.text and not message.text.startswith("/"):
        sent = await message.answer("O'ylayapman... ⚡️")
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": message.text}]
            )
            await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=completion.choices[0].message.content)
        except:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text="Xatolik bo'ldi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
