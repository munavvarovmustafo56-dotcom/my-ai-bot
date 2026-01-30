import asyncio, logging, sys, os, json, sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
from groq import Groq

# --- SOZLAMALAR ---
TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
GROQ_KEY = "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"
ADMIN_ID = 8508142416 
PORT = int(os.environ.get("PORT", 8080))
WEB_APP_URL = "https://mini-app-mustafo.onrender.com" # O'zingizni linkni tekshiring

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_KEY)

# --- BAZA BILAN ISHLASH (Admin uchun) ---
conn = sqlite3.connect("gelectronics.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
conn.commit()

def add_user(user_id):
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    except: pass

# --- WEB SERVER & API ---
async def handle_home(request):
    if os.path.exists("./index.html"): return web.FileResponse('./index.html')
    return web.Response(text="index.html topilmadi", status=404)

async def handle_logo(request):
    if os.path.exists("./logo.jpg"): return web.FileResponse('./logo.jpg')
    return web.Response(status=404)

# 1. AI CHAT (Xotira bilan)
async def handle_chat_api(request):
    try:
        data = await request.json()
        messages = data.get('messages', []) # Butun suhbat tarixini olamiz
        
        # Tizim xabarini qo'shamiz (System Prompt)
        system_msg = {"role": "system", "content": "Sen Gelectronics kompaniyasining aqlli menejerisan. Mijoz bilan xushmuomala bo'l. Kompaniya 2020-yilda ochilgan. Xizmatlar: Inverterlar remonti, Dasturlash, Avtomatika."}
        full_history = [system_msg] + messages

        chat_completion = client.chat.completions.create(
            messages=full_history,
            model="llama-3.3-70b-versatile",
        )
        return web.json_response({'reply': chat_completion.choices[0].message.content})
    except Exception as e:
        return web.json_response({'reply': f'Xatolik: {str(e)}'})

# 2. BUYURTMA QABUL QILISH (Order)
async def handle_order(request):
    try:
        data = await request.json()
        ism = data.get('name')
        tel = data.get('phone')
        xizmat = data.get('service')
        
        # Adminga xabar yuboramiz
        msg_text = (
            f"🔔 <b>YANGI BUYURTMA!</b>\n\n"
            f"👤 <b>Mijoz:</b> {ism}\n"
            f"📞 <b>Tel:</b> {tel}\n"
            f"🛠 <b>Xizmat:</b> {xizmat}\n"
            f"🕒 <i>Web App orqali keldi</i>"
        )
        await bot.send_message(ADMIN_ID, msg_text, parse_mode="HTML")
        return web.json_response({'status': 'success'})
    except:
        return web.json_response({'status': 'error'})

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_home)
    app.router.add_get('/logo.jpg', handle_logo)
    app.router.add_post('/api/chat', handle_chat_api)
    app.router.add_post('/api/order', handle_order) # Yangi yo'l
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()

# --- BOT QISMI ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    add_user(message.from_user.id) # Bazaga qo'shish
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🚀 GELECTRONICS APP", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton(text="📞 Bog'lanish"), KeyboardButton(text="📱 Tarmoqlar")]
    ], resize_keyboard=True)
    await message.answer("Assalomu alaykum! Gelectronics Super Tizimiga xush kelibsiz.", reply_markup=kb)

# ADMIN UCHUN REKLAMA YUBORISH (/send xabar)
@dp.message(Command("send"))
async def send_broadcast(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        text = message.text.replace("/send", "").strip()
        if not text:
            await message.answer("Xabar matnini yozing. Masalan: /send Yangi aksiya!")
            return
        
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        count = 0
        for user in users:
            try:
                await bot.send_message(user[0], f"📢 <b>YANGILIK:</b>\n\n{text}", parse_mode="HTML")
                count += 1
            except: pass
        await message.answer(f"✅ Xabar {count} ta odamga yuborildi.")

@dp.message(F.text == "📞 Bog'lanish")
async def contact(message: types.Message):
    await message.answer("👤 Admin: @kaliusercybersecurity\n📍 Toshkent, Mirzo Ulug`bek 56A\n☎️ 71 200 04 05")

@dp.message(F.text == "📱 Tarmoqlar")
async def socials(message: types.Message):
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Telegram", url="https://t.me/gelectronicsuz"),
         InlineKeyboardButton(text="YouTube", url="https://youtube.com/@smartfaktlar?si=q8vWQQNj8GzbBh9s")]
    ])
    await message.answer("Bizning tarmoqlar:", reply_markup=ikb)

async def main():
    asyncio.create_task(start_web_server())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
