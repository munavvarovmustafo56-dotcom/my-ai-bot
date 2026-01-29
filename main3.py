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
ADMIN_ID = 8508142416  # O'zingizning ID raqamingizni yozing!

CHANNELS = ["@gelectronicsuz"] # Majburiy obuna kanali

db = sqlite3.connect("users.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
db.commit()

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 2. MENU VA TEKSHIRUVLAR
# ==========================================
async def check_sub(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            continue
    return True

def sub_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔵 Telegram kanalga a'zo bo'lish", url="https://t.me/gelectronicsuz"))
    builder.row(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription"))
    return builder.as_markup()

def main_menu(user_id):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🤖 AI bilan gaplashish"))
    builder.row(types.KeyboardButton(text="🏢 Kompaniya haqida"), types.KeyboardButton(text="🛠 Xizmatlarimiz"))
    builder.row(types.KeyboardButton(text="📱 Bizning kanallar"), types.KeyboardButton(text="📞 Bog'lanish"))
    if user_id == ADMIN_ID:
        builder.row(types.KeyboardButton(text="📊 Statistika"))
    return builder.as_markup(resize_keyboard=True)

# ==========================================
# 3. KREATIV MATNLAR VA HANDLERS
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    db.commit()
    if await check_sub(message.from_user.id):
        await message.answer(f"Salom, {message.from_user.first_name}! 🚀\n<b>Gelectronics</b> kompaniyasining rasmiy botiga xush kelibsiz!", reply_markup=main_menu(message.from_user.id), parse_mode="HTML")
    else:
        await message.answer("Botdan foydalanish uchun rasmiy kanalimizga a'zo bo'ling:", reply_markup=sub_menu())

@dp.message(F.text == "🏢 Kompaniya haqida")
async def about_company(message: types.Message):
    text = (
        "<b>🏢 'Gelectronics' kompaniyasi</b>\n\n"
        "Kompaniyamiz 2020-yilda tashkil etilgan bo‘lib, bugungi kunda ikki asosiy bo‘linmadan iborat:\n\n"
        "🔹 <b>G-R-A-N-D Electronics</b> — Servis korxonasi. Texnik qurilmalarni dasturlash, ma’lumotlarni uzoq masofaga uzatish va jarayonlarni avtomatlashtirish bilan shug'ullanadi.\n"
        "🔹 <b>Gelectronics Magazin</b> — Ishlab chiqarish-sotuv korxonasi. Yuqori sifatli ehtiyot qismlarni yetkazib berish xizmati.\n\n"
        "🌍 2022-yildan boshlab kompaniyamiz xalqaro miqyosda texnologik avtomatlashtirish loyihalarini muvaffaqiyatli amalga oshirib kelmoqda."
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "🛠 Xizmatlarimiz")
async def services_info(message: types.Message):
    text = (
        "<b>🛠 Bizning professional xizmatlarimiz:</b>\n\n"
        "✅ Muhandis-elektronik xizmati\n"
        "✅ Muhandis-dasturchi xizmati\n"
        "✅ Texnik jarayonlarni avtomatlashtirish\n"
        "✅ Mutaxassislar konsultatsiyasi\n"
        "✅ Texnik qurilmalarni ishlab chiqish va yaratish\n\n"
        "💡 <b>Ko‘p yillik tajribaga ega</b> jamoamiz har qanday murakkablikdagi vazifani sifatli hal etadi!"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "📞 Bog'lanish")
async def contact_info(message: types.Message):
    text = (
        "<b>📞 Biz bilan bog'lanish:</b>\n\n"
        "☎️ Telefon: <b>71 200 04 05</b>\n"
        "👨‍💻 Admin: @gelectronicsuz\n\n"
        "Savollaringiz bo'lsa, AI bilan gaplashish bo'limidan ham foydalanishingiz mumkin!"
    )
    await message.answer(text, parse_mode="HTML")

@dp.callback_query(F.data == "check_subscription")
async def check_callback(call: types.CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.delete()
        await call.message.answer("Obuna tasdiqlandi! Botdan foydalanishingiz mumkin.", reply_markup=main_menu(call.from_user.id))
    else:
        await call.answer("Siz hali kanalimizga a'zo bo'lmadingiz! ❌", show_alert=True)

@dp.message()
async def ai_logic(message: types.Message):
    if not await check_sub(message.from_user.id):
        return await message.answer("Avval kanalimizga a'zo bo'ling!", reply_markup=sub_menu())
    
    if message.text == "📱 Bizning kanallar":
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="🎬 YouTube (Smart Faktlar)", url="https://youtube.com/@smartfaktlar"))
        builder.row(types.InlineKeyboardButton(text="🔵 Telegram (Gelectronics)", url="https://t.me/gelectronicsuz"))
        return await message.answer("Bizning ijtimoiy tarmoqlarimiz:", reply_markup=builder.as_markup())

    if message.text == "📊 Statistika" and message.from_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        return await message.answer(f"📊 Jami foydalanuvchilar: {count} ta")

    if message.text and not message.text.startswith("/"):
        sent = await message.answer("O'ylayapman... ⚡️")
        try:
            completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": message.text}])
            await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text=completion.choices[0].message.content)
        except:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=sent.message_id, text="Xatolik yuz berdi.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
