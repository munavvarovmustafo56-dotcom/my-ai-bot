import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from groq import Groq

# ==========================================
# 1. SOZLAMALAR (FAQAT SHU YERGA YOZING)
# ==========================================
TELEGRAM_TOKEN = "8572454769:AAFkZ4vYlT_WZXv-0VYHhsxSQYUEDQC-GK8"
GROQ_API_KEY = "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"

# Ishlaydigan modellar ro'yxati (navbati bilan tekshiriladi)
MODELS = ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"]
# ==========================================

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🤖 AI Suhbat"), types.KeyboardButton(text="🛠 Xizmatlar"))
    builder.row(types.KeyboardButton(text="📞 Bog'lanish"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        f"Salom {message.from_user.first_name}! 🚀\nMen tayyorman. Savolingizni yuboring!",
        reply_markup=main_menu()
    )

@dp.message()
async def chat_with_ai(message: types.Message):
    # Menyudagi tugmalar uchun oddiy javoblar
    if message.text == "🛠 Xizmatlar":
        return await message.answer("Bizning xizmatlar: Sayt yaratish va Elektronika ta'miri.")
    if message.text == "📞 Bog'lanish":
        return await message.answer("Admin: @musta")

    # Agar foydalanuvchi biror gap yozsa
    if message.text:
        sent_message = await message.answer("O'ylayapman... ⚡️")
        
        success = False
        # Har bir modelni birma-bir sinab ko'radi
        for model_name in MODELS:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": message.text}]
                )
                ai_response = completion.choices[0].message.content
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_message.message_id,
                    text=ai_response
                )
                success = True
                break # Agar ishlasa, sikldan chiqadi
            except Exception as e:
                print(f"{model_name} ishlamadi, keyingisiga o'taman...")
                continue
        
        if not success:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=sent_message.message_id,
                text="Kechirasiz, barcha modellar band yoki API kalitda muammo bor. 😔"
            )

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot muvaffaqiyatli ishga tushdi! Endi kodga qaytib kirish shart emas.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())