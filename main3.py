import asyncio, logging, sys, os, json, sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
from groq import Groq

# --- SOZLAMALAR ---
TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
GROQ_KEY = "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"
ADMIN_USERNAME = "@kaliusercybersecurity"
ADMIN_ID = 8508142416
PORT = int(os.environ.get("PORT", 8080))
# Render URLingizni tekshiring!
WEB_APP_URL = "https://my-ai-bot-iu2e.onrender.com" 

# --- MUHIM: FAYLLAR MANZILINI ANIQLASH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')
LOGO_PATH = os.path.join(BASE_DIR, 'logo.jpg')

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_KEY)

# --- WEB SERVER ---
async def handle_home(request):
    # Fayl borligini jiddiy tekshiramiz
    if os.path.exists(INDEX_PATH):
        return web.FileResponse(INDEX_PATH)
    return web.Response(text=f"XATOLIK: index.html topilmadi! Qidirilgan joy: {INDEX_PATH}", status=404)

async def handle_logo(request):
    if os.path.exists(LOGO_PATH):
        return web.FileResponse(LOGO_PATH)
    return web.Response(status=404)

async def handle_chat_api(request):
    try:
        data = await request.json()
        messages = data.get('messages', [])
        # Tizim xabari (System Prompt)
        system_msg = {"role": "system", "content": "Sen Gelectronics kompaniyasining aqlli menejerisan. Kompaniya 2020-yilda ochilgan. Xizmatlar: Servis va Magazin. Javoblaring qisqa va o'zbek tilida bo'lsin."}
        
        # Agar messages bo'sh bo'lsa yoki noto'g'ri bo'lsa, faqat user textni olamiz
        user_text = data.get('text')
        if user_text:
            full_history = [system_msg, {"role": "user", "content": user_text}]
        else:
            full_history = [system_msg] + messages

        chat_completion = client.chat.completions.create(
            messages=full_history,
            model="llama-3.3-70b-versatile",
        )
        return web.json_response({'reply': chat_completion.choices[0].message.content})
    except Exception as e:
        return web.json_response({'reply': f'Xatolik: {str(e)}'})

async def handle_order(request):
    return web.json_response({'status': 'ok'}) # Hozircha oddiy javob

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_home)
    app.router.add_get('/logo.jpg', handle_logo)
    app.router.add_post('/api/chat', handle_chat_api)
    app.router.add_post('/api/order', handle_order)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()
    logging.info(f"SERVER {PORT} DA ISHLAMOQDA. HTML MANZILI: {INDEX_PATH}")

# --- BOT ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🚀 GELECTRONICS APP", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton(text="📞 Bog'lanish"), KeyboardButton(text="📱 Tarmoqlar")]
    ], resize_keyboard=True)
    await message.answer("Assalomu alaykum! Tizim ishga tushdi.", reply_markup=kb)

@dp.message(F.text == "📞 Bog'lanish")
async def contact(message: types.Message):
    await message.answer(f"👤 Admin: {ADMIN_USERNAME}\n📍 Toshkent\n☎️ 71 200 04 05")

@dp.message(F.text == "📱 Tarmoqlar")
async def socials(message: types.Message):
    await message.answer("Tarmoqlarimiz: @gelectronicsuz")

async def main():
    asyncio.create_task(start_web_server())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
