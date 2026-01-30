import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiohttp import web

# --- CHALQASHMASLIK UCHUN IMPORTLARNI TEKSHIRAMIZ ---
try:
    from messages import START_ANIMATION, WELCOME_TEXT
except ImportError:
    # Agar messages.py topilmasa, standart matn ishlatamiz (xavfsizlik uchun)
    START_ANIMATION = "https://i.pinimg.com/originals/e8/50/74/e850742a78601c4fb8b79b6999a0d816.gif"
    WELCOME_TEXT = "Assalomu alaykum! Ilovaga xush kelibsiz."

# --- SOZLAMALAR ---
TOKEN = "8572454769:AAEDOYLIADXSjH8QO2ucKvU3A2AgqUFRk40"
ADMIN_ID = 8508142416 
PORT = int(os.environ.get("PORT", 8080))
# Renderdagi manzilingiz (O'ZINGIZNIKINI TEKSHIRING!)
WEB_APP_URL = "https://my-ai-bot-iu2e.onrender.com"

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==========================================
# 1. SERVER (WEB APP + HEALTH CHECK)
# ==========================================
async def handle_home(request):
    # index.html faylini qidiramiz
    if os.path.exists("./index.html"):
        return web.FileResponse('./index.html')
    else:
        return web.Response(text="⚠️ Xatolik: index.html fayli topilmadi! Iltimos GitHubga yuklang.")

async def handle_health(request):
    # Render uchun maxsus "Tirikman" signali
    return web.Response(text="OK", status=200)

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_home)       # Asosiy sayt
    app.router.add_get('/healthz', handle_health) # Tekshiruv uchun
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"✅ WEB SERVER {PORT} PORTIDA MUVAFFAQIYATLI ISHGA TUSHDI")

# ==========================================
# 2. TUGMALAR
# ==========================================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Ilovani ochish", web_app=WebAppInfo(url=WEB_APP_URL))],
            [KeyboardButton(text="🔄 Botni yangilash")] # Agar qotib qolsa bosish uchun
        ],
        resize_keyboard=True
    )

# ==========================================
# 3. BOT LOGIKASI
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Ismni formatlash
    text = WELCOME_TEXT
    if "{name}" in text:
        text = text.format(name=message.from_user.first_name)
    
    await message.answer_animation(
        animation=START_ANIMATION,
        caption=text,
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@dp.message(F.text == "🔄 Botni yangilash")
async def restart_msg(message: types.Message):
    await message.answer("✅ Bot ishlab turibdi! Ilovani ochishingiz mumkin.", reply_markup=main_menu())

# ==========================================
# 4. ISHGA TUSHIRISH (TARTIB BILAN)
# ==========================================
async def main():
    # 1. Avval Web Serverni yoqamiz (Render ko'rishi uchun)
    await start_web_server()
    
    # 2. Biroz kutamiz (Server o'rnashib olishi uchun)
    await asyncio.sleep(2)
    
    # 3. Keyin Botni yoqamiz
    logging.info("🤖 BOT ISHGA TUSHMOQDA...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")
