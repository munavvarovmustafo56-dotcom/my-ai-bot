import asyncio
import logging
import sys
import os
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
from groq import Groq

# --- SOZLAMALAR ---
TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
ADMIN_ID = 8508142416 
GROQ_KEY = "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"
PORT = int(os.environ.get("PORT", 8080))
WEB_APP_URL = "https://my-ai-bot-iu2e.onrender.com" # O'zingizni linkni tekshiring!

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_KEY)

# ==========================================
# 1. WEB SERVER & API (AI UCHUN)
# ==========================================

# 1. index.html ni ochib beruvchi funksiya
async def handle_home(request):
    if os.path.exists("./index.html"):
        return web.FileResponse('./index.html')
    return web.Response(text="Web App yuklanmoqda...", status=200)

# 2. HAQIQIY AI API (Web App shu yerga murojaat qiladi)
async def handle_chat_api(request):
    try:
        data = await request.json() # Web Appdan kelgan xabarni o'qiymiz
        user_text = data.get('text', '')

        if not user_text:
            return web.json_response({'reply': 'Iltimos, biror narsa yozing.'})

        # Groqqa yuboramiz
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Sen Gelectronics kompaniyasining aqlli yordamchisisan. O'zbek tilida qisqa va lo'nda javob ber."},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.3-70b-versatile",
        )
        ai_reply = chat_completion.choices[0].message.content
        
        # Javobni Web Appga qaytaramiz
        return web.json_response({'reply': ai_reply})

    except Exception as e:
        logging.error(f"AI Xatosi: {e}")
        return web.json_response({'reply': 'Uzr, serverda xatolik yuz berdi.'})

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_home)          # Saytni ochish
    app.router.add_post('/api/chat', handle_chat_api) # AI bilan gaplashish yo'li
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"✅ SERVER VA API {PORT}-PORTDA ISHLAMOQDA")

# ==========================================
# 2. BOT TUGMALARI
# ==========================================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 GELECTRONICS APP (AI Chat)", web_app=WebAppInfo(url=WEB_APP_URL))],
            [KeyboardButton(text="📞 Bog'lanish"), KeyboardButton(text="📱 Ijtimoiy tarmoqlar")]
        ],
        resize_keyboard=True
    )

# ==========================================
# 3. BOT LOGIKASI
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        f"👋 <b>Assalomu alaykum!</b>\n\n"
        f"🤖 <b>AI Yordamchi</b> bilan gaplashish uchun tepadagi <b>'GELECTRONICS APP'</b> tugmasini bosing.\n"
        f"U yerda sun'iy intellekt sizga javob beradi.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@dp.message(F.text == "📞 Bog'lanish")
async def contact(message: types.Message):
    await message.answer("📞 <b>Admin:</b> @Mustafo_Admin\n📍 Farg'ona shahri", parse_mode="HTML")

@dp.message(F.text == "📱 Ijtimoiy tarmoqlar")
async def channels(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Telegram", url="https://t.me/Gelectronics_uz")],
        [InlineKeyboardButton(text="YouTube", url="https://youtube.com/@AOStudio")]
    ])
    await message.answer("Bizning tarmoqlar:", reply_markup=kb)

# ==========================================
# 4. ISHGA TUSHIRISH
# ==========================================
async def main():
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
