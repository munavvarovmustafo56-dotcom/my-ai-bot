import asyncio
import logging
import sqlite3
import os
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from groq import Groq
from aiohttp import web

# ==========================================
# 1. SOZLAMALAR (ENG MUHIM QISM)
# ==========================================
TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
GROQ_KEY = "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"
ADMIN_ID = 8508142416 
PORT = int(os.environ.get("PORT", 8080))

# Loglarni chiroyli chiqarish
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
client = Groq(api_key=GROQ_KEY)

# ==========================================
# 2. RENDER UCHUN "O'LMAS" SERVER
# ==========================================
async def handle(request):
    return web.Response(text="🔥 Gelectronics Premium Bot is Running! 🔥")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"🚀 WEB SERVER {PORT} PORTIDA ISHGA TUSHDI")

# ==========================================
# 3. DATABASE (FOYDALANUVCHILAR BAZASI)
# ==========================================
db = sqlite3.connect("gelectronics_pro.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, fullname TEXT, username TEXT, joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
db.commit()

# ==========================================
# 4. HOLATLAR (STATES)
# ==========================================
class BotStates(StatesGroup):
    ai_chat = State() # Faqat AI bilan gaplashish rejimi

# ==========================================
# 5. KLAVIATURALAR (MENYULAR)
# ==========================================
def main_menu_kb():
    kb = ReplyKeyboardBuilder()
    # 1-qator
    kb.row(types.KeyboardButton(text="🤖 AI Yordamchi (Savol-Javob)"))
    # 2-qator
    kb.row(types.KeyboardButton(text="🛠 Xizmatlarimiz"), types.KeyboardButton(text="🏢 Kompaniya haqida"))
    # 3-qator
    kb.row(types.KeyboardButton(text="📱 Bizning Kanallar"), types.KeyboardButton(text="📞 Kontaktlar"))
    # Admin uchun
    kb.row(types.KeyboardButton(text="📊 Statistika"))
    return kb.as_markup(resize_keyboard=True)

def back_kb():
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="⬅️ Bosh menyuga qaytish"))
    return kb.as_markup(resize_keyboard=True)

# ==========================================
# 6. HANDLERS (BOTNING MIYASI)
# ==========================================

# --- START BOSILGANDA ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    # Bazaga yozish
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, fullname, username) VALUES (?, ?, ?)", 
                       (message.from_user.id, message.from_user.full_name, message.from_user.username))
        db.commit()
    except Exception as e:
        logging.error(f"DB Error: {e}")

    await state.clear() # Har qanday eski holatni o'chiramiz
    welcome_text = (
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!\n\n"
        f"🚀 <b>Gelectronics</b> rasmiy botiga xush kelibsiz.\n"
        f"Biz sanoat elektronikasi va IT yechimlar bo'yicha sizga yordam beramiz.\n\n"
        f"👇 <i>Kerakli bo'limni tanlang:</i>"
    )
    await message.answer(welcome_text, reply_markup=main_menu_kb(), parse_mode="HTML")

# --- ASOSIY TUGMALAR (HAR DOIM ISHLAYDI) ---

@dp.message(F.text.contains("🛠 Xizmatlarimiz"))
async def services(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "<b>🛠 GELECTRONICS XIZMATLARI:</b>\n\n"
        "⚡️ <b>Inverterlar ta'mirlash:</b> Har qanday turdagi chastota o'zgartirgichlar.\n"
        "🏭 <b>Sanoat Avtomatika:</b> Stanoklar va liniyalarni sozlash.\n"
        "💻 <b>Dasturlash:</b> Web saytlar, Telegram botlar va CRM tizimlar.\n"
        "📹 <b>Kuzatuv tizimlari:</b> Kamera va xavfsizlik tizimlarini o'rnatish.\n\n"
        "<i>Batafsil ma'lumot uchun admin bilan bog'laning.</i>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text.contains("🏢 Kompaniya haqida"))
async def about(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "🏢 <b>Gelectronics haqida</b>\n\n"
        "Bizning kompaniya zamonaviy texnologiyalar va elektronika sohasida yetakchi hisoblanadi. "
        "Bizning maqsadimiz — ishlab chiqarish jarayonlarini avtomatlashtirish va biznesingizni yangi bosqichga olib chiqishdir.\n\n"
        "📍 <b>Manzil:</b> Farg'ona shahri (yoki manzilingizni kiriting)\n"
        "📅 <b>Ish vaqti:</b> 09:00 - 18:00"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text.contains("📱 Bizning Kanallar"))
async def channels(message: types.Message, state: FSMContext):
    await state.clear()
    # Inline tugmalar (Linklar uchun)
    links = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📢 Telegram Kanal", url="https://t.me/Gelectronics_uz")],
        [types.InlineKeyboardButton(text="📸 Instagram", url="https://instagram.com/gelectronics_uz")],
        [types.InlineKeyboardButton(text="📹 YouTube", url="https://youtube.com/@AOStudio")]
    ])
    await message.answer("📱 <b>Bizning ijtimoiy tarmoqlarimizga obuna bo'ling:</b>", reply_markup=links, parse_mode="HTML")

@dp.message(F.text.contains("📞 Kontaktlar"))
async def contact(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "📞 <b>BOG'LANISH MARKAZI</b>\n\n"
        "👨‍💻 <b>Admin:</b> @Mustafo_Admin (o'z useringizni qo'ying)\n"
        "📞 <b>Tel:</b> +998 90 123 45 67\n"
        "📧 <b>Email:</b> info@gelectronics.uz\n\n"
        "<i>Savollaringiz bo'lsa, bemalol yozishingiz mumkin.</i>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text.contains("📊 Statistika"))
async def stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        await message.answer(f"📊 <b>Bot foydalanuvchilari soni:</b> {count} nafar", parse_mode="HTML")
    else:
        await message.answer("Bu bo'lim faqat admin uchun!")

# --- AI REJIMIGA KIRISH ---
@dp.message(F.text == "🤖 AI Yordamchi (Savol-Javob)")
async def enter_ai(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.ai_chat)
    text = (
        "🤖 <b>AI Rejimi Faollashdi!</b>\n\n"
        "Men Sun'iy Intellektman. Menga istalgan texnik savolingizni bering (kod yozish, elektronika, maslahatlar).\n\n"
        "<i>Chiqish uchun pastdagi 'Bosh menyuga qaytish' tugmasini bosing.</i>"
    )
    await message.answer(text, reply_markup=back_kb(), parse_mode="HTML")

# --- AI REJIMIDAN CHIQISH ---
@dp.message(F.text == "⬅️ Bosh menyuga qaytish")
async def exit_ai(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ <b>AI rejimi o'chirildi.</b> Asosiy menyudasiz.", reply_markup=main_menu_kb(), parse_mode="HTML")

# --- FAQAT AI SAVOLLARIGA JAVOB BERISH ---
@dp.message(BotStates.ai_chat)
async def ai_response(message: types.Message):
    wait_msg = await message.answer("⏳ <i>AI o'ylamoqda...</i>", parse_mode="HTML")
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Sen Gelectronics kompaniyasining aqlli yordamchisisan. O'zbek tilida qisqa, lo'nda va professional javob ber."},
                {"role": "user", "content": message.text}
            ],
            model="llama-3.3-70b-versatile",
        )
        response = chat_completion.choices[0].message.content
        await bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=response, parse_mode="Markdown")
    except Exception as e:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=f"⚠️ Xatolik: {str(e)}")

# ==========================================
# 7. ISHGA TUSHIRISH
# ==========================================
async def main():
    # 1. Web serverni orqa fonda yoqamiz (Render uchun)
    asyncio.create_task(start_web_server())
    
    # 2. Botni tozalab ishga tushiramiz
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")
