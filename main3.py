import asyncio
import logging
import sqlite3
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from groq import Groq
from aiohttp import web

# --- KONFIGURATSIYA ---
TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
GROQ_KEY = "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"
ADMIN_ID = 8508142416 
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
client = Groq(api_key=GROQ_KEY)

# --- DATABASE ---
db = sqlite3.connect("gelectronics.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")
db.commit()

# --- STATES (BOTNING HOLATLARI) ---
class BotStates(StatesGroup):
    main_menu = State()
    ai_mode = State()

# --- RENDER WEB SERVER ---
async def handle(request):
    return web.Response(text="Gelectronics System: ACTIVE")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

# --- KEYBOARDS ---
def get_main_kb():
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="🏢 Kompaniya"), types.KeyboardButton(text="🛠 Xizmatlar"))
    kb.row(types.KeyboardButton(text="🤖 AI Professional Yordamchi"))
    kb.row(types.KeyboardButton(text="📞 Kontakt"), types.KeyboardButton(text="📊 Statistika"))
    return kb.as_markup(resize_keyboard=True)

def get_back_kb():
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="⬅️ Orqaga (Asosiy menyu)"))
    return kb.as_markup(resize_keyboard=True)

# --- HANDLERS ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (message.from_user.id, message.from_user.username))
    db.commit()
    await state.set_state(BotStates.main_menu)
    await message.answer("🛠 <b>Gelectronics Professional Tizimiga xush kelibsiz!</b>", 
                         reply_markup=get_main_kb(), parse_mode="HTML")

# AI REJIMIGA O'TISH
@dp.message(F.text == "🤖 AI Professional Yordamchi")
async def enter_ai_mode(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.ai_mode)
    await message.answer("🤖 <b>AI Rejimi yoqildi.</b>\nEndi menga texnik savollaringizni yozishingiz mumkin. \n\n<i>Chiqish uchun 'Orqaga' tugmasini bosing.</i>", 
                         reply_markup=get_back_kb(), parse_mode="HTML")

# ORQAGA QAYTISH
@dp.message(F.text == "⬅️ Orqaga (Asosiy menyu)")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.main_menu)
    await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=get_main_kb())

# KOMPANIYA VA XIZMATLAR (FAQAT MAIN MENUDA ISHLAYDI)
@dp.message(BotStates.main_menu, F.text == "🏢 Kompaniya")
async def about_comp(message: types.Message):
    await message.answer("<b>Gelectronics</b> — Sanoat elektronikasi bo'yicha №1 markaz.", parse_mode="HTML")

@dp.message(BotStates.main_menu, F.text == "📊 Statistika")
async def show_stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        res = cursor.fetchone()[0]
        await message.answer(f"📊 Foydalanuvchilar: {res}")

# FAQAT AI REJIMIDA SAVOLLARGA JAVOB BERISH
@dp.message(BotStates.ai_mode)
async def ai_chatting(message: types.Message):
    if message.text == "⬅️ Orqaga (Asosiy menyu)": return # Keyinchalik xato bermasligi uchun

    msg = await message.answer("🔍 <i>Tahlil qilinmoqda...</i>", parse_mode="HTML")
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": message.text}],
            model="llama-3.3-70b-versatile",
        )
        await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, 
                                    text=chat.choices[0].message.content)
    except:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="Xato!")

# --- ISHGA TUSHIRISH ---
async def main():
    asyncio.create_task(start_web_server())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
