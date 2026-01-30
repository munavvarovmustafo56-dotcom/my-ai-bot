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

# ==========================================
# 1. KONFIGURATSIYA (Siz bergan ma'lumotlar)
# ==========================================
TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
GROQ_KEY = "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"
ADMIN_ID = 8508142416 
ADMIN_USERNAME = "@kaliusercybersecurity"
PORT = int(os.environ.get("PORT", 8080))
# Renderdagi manzilingiz (O'zgartirish esdan chiqmasin!)
WEB_APP_URL = "https://my-ai-bot-iu2e.onrender.com" 

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_KEY)

# ==========================================
# 2. WEB SERVER & API
# ==========================================

# Asosiy sahifa (index.html)
async def handle_home(request):
    if os.path.exists("./index.html"):
        return web.FileResponse('./index.html')
    return web.Response(text="⚠️ index.html topilmadi! GitHubga yuklang.", status=404)

# Logo rasmni ochish (logo.jpg)
async def handle_logo(request):
    if os.path.exists("./logo.jpg"):
        return web.FileResponse('./logo.jpg')
    return web.Response(status=404) # Agar rasm yo'q bo'lsa

# AI API (Web App uchun miya)
async def handle_chat_api(request):
    try:
        data = await request.json()
        user_text = data.get('text', '')
        
        # Groq (Llama 3) ga so'rov
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Sen Gelectronics kompaniyasining aqlli yordamchisisan. Javoblaring aniq, professional va o'zbek tilida bo'lsin. Kompaniya 2020-yilda ochilgan, Grand Electronics va Gelectronics Magazin bo'limlari bor."},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.3-70b-versatile",
        )
        ai_reply = chat_completion.choices[0].message.content
        return web.json_response({'reply': ai_reply})
    except Exception as e:
        logging.error(f"AI Error: {e}")
        return web.json_response({'reply': 'Uzr, serverda vaqtinchalik xatolik.'})

# Serverni ishga tushirish
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_home)          # Sayt
    app.router.add_get('/logo.jpg', handle_logo)  # Logo rasm
    app.router.add_post('/api/chat', handle_chat_api) # AI
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"✅ PREMIUM SERVER {PORT}-PORTDA ISHLAMOQDA")

# ==========================================
# 3. BOT LOGIKASI
# ==========================================

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Asosiy menyu
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🚀 GELECTRONICS APP (AI & Xizmatlar)", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton(text="📞 Bog'lanish"), KeyboardButton(text="📱 Ijtimoiy tarmoqlar")],
        [KeyboardButton(text="🏢 Kompaniya haqida")]
    ], resize_keyboard=True)
    
    await message.answer(
        f"👋 <b>Assalomu alaykum!</b>\n\n"
        f"🏢 <b>GELECTRONICS</b> rasmiy botiga xush kelibsiz.\n"
        f"Biz texnologik jarayonlarni avtomatlashtirish va elektronika bo'yicha yetakchimiz.\n\n"
        f"👇 <i>Kerakli bo'limni tanlang:</i>",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.message(F.text == "📞 Bog'lanish")
async def contact(message: types.Message):
    text = (
        f"📞 <b>ALOQA MARKAZI</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"👤 <b>Admin:</b> {ADMIN_USERNAME}\n"
        f"📍 <b>Manzil:</b> Toshkent, Mirzo Ulug`bek 56A\n"
        f"☎️ <b>Tel:</b> 71 200 04 05\n\n"
        f"🕒 <i>Murojaatingizni kutamiz!</i>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "📱 Ijtimoiy tarmoqlar")
async def socials(message: types.Message):
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Telegram Kanal", url="https://t.me/gelectronicsuz")],
        [InlineKeyboardButton(text="🔴 YouTube (Smart Faktlar)", url="https://youtube.com/@smartfaktlar?si=q8vWQQNj8GzbBh9s")]
    ])
    await message.answer("🌐 <b>Bizning rasmiy sahifalarimiz:</b>", reply_markup=ikb, parse_mode="HTML")

@dp.message(F.text == "🏢 Kompaniya haqida")
async def about_company(message: types.Message):
    text = (
        "🏢 <b>GELECTRONICS TARIXI</b>\n\n"
        "Kompaniya 2020-yilda tashkil etilgan. Hozirda 2 ta asosiy bo'lim mavjud:\n"
        "1️⃣ <b>G-R-A-N-D Electronics (Servis):</b> Dasturlash va avtomatlashtirish.\n"
        "2️⃣ <b>Gelectronics Magazin:</b> Ehtiyot qismlar savdosi.\n\n"
        "🌍 2022-yildan xalqaro bozorga chiqdik (Xitoy, Turkiya, Tojikiston).\n"
        "🤝 500+ korxona bizning mijozimiz."
    )
    await message.answer(text, parse_mode="HTML")

# Admin statistikasi
@dp.message(Command("stat"))
async def stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📊 Statistika tizimi tez orada ulanadi.")

# ==========================================
# 4. ISHGA TUSHIRISH
# ==========================================
async def main():
    asyncio.create_task(start_web_server())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
