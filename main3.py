import asyncio, logging, sys, os, json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
from groq import Groq

# KONFIGURATSIYA
TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
GROQ_KEY = "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"
ADMIN_ID = 8508142416 
PORT = int(os.environ.get("PORT", 8080))
WEB_APP_URL = "https://my-ai-bot-iu2e.onrender.com" # Render'dagi link

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_KEY)

# --- WEB SERVER & API ---
async def handle_home(request):
    return web.FileResponse('./index.html') if os.path.exists("./index.html") else web.Response(text="index.html not found")

async def handle_chat_api(request):
    try:
        data = await request.json()
        user_text = data.get('text', '')
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "Sen Gelectronics yordamchisisan. O'zbekcha qisqa javob ber."}, {"role": "user", "content": user_text}],
            model="llama-3.3-70b-versatile",
        )
        return web.json_response({'reply': chat_completion.choices[0].message.content})
    except Exception:
        return web.json_response({'reply': 'Xatolik yuz berdi.'})

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_home)
    app.router.add_post('/api/chat', handle_chat_api)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()

# --- BOT HANDLERS ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🚀 GELECTRONICS APP", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton(text="📞 Bog'lanish"), KeyboardButton(text="📱 Ijtimoiy tarmoqlar")]
    ], resize_keyboard=True)
    await message.answer("🛠 <b>Gelectronics Premium</b> tizimiga xush kelibsiz!", reply_markup=kb, parse_mode="HTML")

@dp.message(F.text == "📞 Bog'lanish")
async def contact(message: types.Message):
    await message.answer("👤 <b>Admin:</b> @Mustafo_Admin\n☎️ <b>Tel:</b> +998 90 123 45 67", parse_mode="HTML")

@dp.message(F.text == "📱 Ijtimoiy tarmoqlar")
async def channels(message: types.Message):
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Telegram", url="https://t.me/Gelectronics_uz"), 
         InlineKeyboardButton(text="YouTube", url="https://youtube.com/@AOStudio")]
    ])
    await message.answer("Bizning tarmoqlar:", reply_markup=ikb)

async def main():
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
