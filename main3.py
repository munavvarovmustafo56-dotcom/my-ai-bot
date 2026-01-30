import asyncio, logging, sys, os, sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiohttp import web
from groq import Groq

# --- SOZLAMALAR ---
TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
GROQ_KEY = "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"
ADMIN_ID = 8508142416  # <-- O'Z ID RAQAMINGIZNI YOZING

PORT = int(os.environ.get("PORT", 8080))
WEB_APP_URL = "https://my-ai-bot-iu2e.onrender.com" 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')
LOGO_PATH = os.path.join(BASE_DIR, 'logo.jpg')

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_KEY)
admin_states = {} 

conn = sqlite3.connect("gelectronics.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
conn.commit()

def add_user(user_id):
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    except: pass

async def handle_home(request):
    if os.path.exists(INDEX_PATH): return web.FileResponse(INDEX_PATH)
    return web.Response(text="index.html topilmadi!", status=404)

async def handle_logo(request):
    if os.path.exists(LOGO_PATH): return web.FileResponse(LOGO_PATH)
    return web.Response(status=404)

# --- AI MIYYASI VA FILTR ---
async def handle_chat_api(request):
    try:
        data = await request.json()
        messages = data.get('messages', [])
        
        # 1. FOYDALANUVCHI SAVOLINI TEKSHIRAMIZ
        last_user_msg = ""
        for m in reversed(messages):
            if m['role'] == 'user':
                last_user_msg = m['content'].lower()
                break
        
        # 2. AGAR "KIM YARATGAN" DEYILSA -> MAJBURIY JAVOB QAYTARAMIZ
        # AI ga so'rov yuborilmaydi, to'g'ridan-to'g'ri javob beradi.
        triggers = ["kim yaratgan", "kim tuzgan", "kim yasagan", "muallif", "kim qildi", "dasturchi kim"]
        if any(t in last_user_msg for t in triggers):
            forced_reply = "Meni 14 yoshli dasturchi Munavvarov Mustafo yaratgan."
            return web.json_response({'reply': forced_reply})

        # 3. AGAR SAVOL BOSHQA BO'LSA -> AI ISHLAYDI
        system_msg = {
            "role": "system", 
            "content": (
                "Sen Gelectronics kompaniyasining texnik xodimisan. "
                "Manzil: Toshkent, Sayram 7-tor ko'chasi, 52-uy. "
                "Vazifang: Inverterlar, PLATA (sxema) va Dasturlash bo'yicha qisqa javob berish. "
                "SO'ZLARNI BUZMA! Har doim to'g'ri yoz."
            )
        }
        full_history = [system_msg] + messages
        
        chat_completion = client.chat.completions.create(
            messages=full_history,
            model="llama-3.3-70b-versatile",
            temperature=0.1 # Juda jiddiy rejim
        )
        
        raw_reply = chat_completion.choices[0].message.content
        
        # 4. JAVOBNI TEKSHIRISH VA TUZATISH (POST-PROCESS)
        # Agar AI "plita" deb yuborsa, biz uni "PLATA" ga almashtiramiz
        clean_reply = raw_reply.replace("plita", "PLATA").replace("Plita", "PLATA").replace("gaz plitasi", "elektron plata")
        
        return web.json_response({'reply': clean_reply})

    except Exception as e:
        return web.json_response({'reply': f'Xatolik: {str(e)}'})

async def handle_order(request):
    try:
        data = await request.json()
        text = f"🆘 <b>YANGI BUYURTMA!</b>\n\n👤 {data.get('name')}\n📞 {data.get('phone')}\n🛠 {data.get('problem')}\n📍 {data.get('loc')}"
        await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
        return web.json_response({'status': 'success'})
    except:
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

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    add_user(user_id)
    buttons = [[KeyboardButton(text="🚀 GELECTRONICS APP", web_app=WebAppInfo(url=WEB_APP_URL))]]
    if user_id == ADMIN_ID: buttons.append([KeyboardButton(text="📢 REKLAMA YUBORISH")])
    await message.answer("Assalomu alaykum!", reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True))

@dp.message(F.text == "📢 REKLAMA YUBORISH")
async def ask_ad(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        admin_states[ADMIN_ID] = "waiting_for_ad"
        await message.answer("Nima tashlasangiz (Rasm, Video, Text) hammaga tarqataman.")

@dp.message()
async def broadcast_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID and admin_states.get(ADMIN_ID) == "waiting_for_ad":
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        count = 0
        for user in users:
            try:
                await bot.copy_message(chat_id=user[0], from_chat_id=user_id, message_id=message.message_id)
                count += 1
                await asyncio.sleep(0.05)
            except: pass
        admin_states[ADMIN_ID] = None
        await message.answer(f"✅ {count} kishiga yuborildi!")

async def main():
    asyncio.create_task(start_web_server())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
