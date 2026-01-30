import asyncio, logging, sys, os, json, sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
from groq import Groq

# --- SOZLAMALAR ---
TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
GROQ_KEY = "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"

# ⚠️ DIQQAT: XABAR BORADIGAN ODAMLAR RO'YXATI
# Bu yerga o'z ID raqamingiz va sherigingizning ID raqamini vergul bilan yozing.
# Masalan: [8508142416, 123456789]
RECIPIENTS = [73759699, 168840286] 

PORT = int(os.environ.get("PORT", 8080))
WEB_APP_URL = "https://my-ai-bot-iu2e.onrender.com" 

# --- FAYL YO'LLARI (GPS) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')
LOGO_PATH = os.path.join(BASE_DIR, 'logo.jpg')

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_KEY)

# --- BAZA ---
conn = sqlite3.connect("gelectronics.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
conn.commit()

def add_user(user_id):
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    except: pass

# --- WEB SERVER ---
async def handle_home(request):
    if os.path.exists(INDEX_PATH): return web.FileResponse(INDEX_PATH)
    return web.Response(text="index.html topilmadi!", status=404)

async def handle_logo(request):
    if os.path.exists(LOGO_PATH): return web.FileResponse(LOGO_PATH)
    return web.Response(status=404)

async def handle_chat_api(request):
    try:
        data = await request.json()
        messages = data.get('messages', [])
        
        system_msg = {
            "role": "system", 
            "content": (
                "Sen 'Gelectronics' kompaniyasining jiddiy AI xodimi. "
                "Manzilimiz: Toshkent, Sayram 7-tor ko'chasi, 52-uy. "
                "Faqat quyidagi mavzularda gapir: "
                "1. Inverterlar va elektron platalar ta'miri (G-R-A-N-D Service). "
                "2. Dasturlash va Avtomatika. "
                "Agar mijoz boshqa narsa so'rasa: 'Uzr, men faqat Gelectronics texnik masalalari bo'yicha javob bera olaman.' deb ayt."
            )
        }
        
        full_history = [system_msg] + messages
        chat_completion = client.chat.completions.create(
            messages=full_history,
            model="llama-3.3-70b-versatile",
            temperature=0.3 
        )
        return web.json_response({'reply': chat_completion.choices[0].message.content})
    except Exception as e:
        return web.json_response({'reply': f'Xatolik: {str(e)}'})

# --- BUYURTMANI 2 KISHIGA YUBORISH ---
async def handle_order(request):
    try:
        data = await request.json()
        
        text = (
            f"🆘 <b>YANGI TEXNIK BUYURTMA!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Mijoz:</b> {data.get('name')}\n"
            f"🏢 <b>Tashkilot:</b> {data.get('org')}\n"
            f"📞 <b>Tel:</b> {data.get('phone')}\n"
            f"📍 <b>Manzil:</b> {data.get('loc')}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚙️ <b>Model:</b> {data.get('model')}\n"
            f"🛠 <b>Muammo:</b> {data.get('problem')}\n"
            f"📅 <b>Vaqt:</b> {data.get('date')}\n"
        )
        
        # Sikl: Ro'yxatdagi har bir odamga jo'natamiz
        for user_id in RECIPIENTS:
            try:
                await bot.send_message(user_id, text, parse_mode="HTML")
            except Exception as e:
                logging.error(f"Xabar yuborishda xato ({user_id}): {e}")

        return web.json_response({'status': 'success'})
    except Exception as e:
        return web.json_response({'status': 'error'})

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_home)
    app.router.add_get('/logo.jpg', handle_logo)
    app.router.add_post('/api/chat', handle_chat_api)
    app.router.add_post('/api/order', handle_order)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()

# --- BOT ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    add_user(message.from_user.id)
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🚀 GELECTRONICS APP", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton(text="📍 Manzil"), KeyboardButton(text="📞 Kontaktlar")]
    ], resize_keyboard=True)
    await message.answer("Assalomu alaykum! App orqali buyurtma bering.", reply_markup=kb)

@dp.message(F.text == "📍 Manzil")
async def location(message: types.Message):
    await message.answer("📍 <b>Bizning manzil:</b>\nToshkent sh, Sayram 7-tor ko'chasi, 52-uy.", parse_mode="HTML")

@dp.message(F.text == "📞 Kontaktlar")
async def contact(message: types.Message):
    await message.answer("📞 <b>Aloqa:</b>\n+998 71 200 04 05", parse_mode="HTML")

async def main():
    asyncio.create_task(start_web_server())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
