import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from groq import Groq

# ==========================================
# 1. XAVFSIZ SOZLAMALAR (Render orqali ulanadi)
# ==========================================
TELEGRAM_TOKEN = os.getenv("8572454769:AAFkZ4vYlT_WZXv-0VYHhsxSQYUEDQC-GK8")
GROQ_API_KEY = os.getenv("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")

# Ishlaydigan modellar
MODELS = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]

# ==========================================
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🤖 AI bilan gaplashish"))
    builder.row(types.KeyboardButton(text="🛠 Servis xizmati"), types.KeyboardButton(text="📱 YouTube: AO Studio"))
    builder.row(types.KeyboardButton(text="👨‍🎓 Magistratura ishi"), types.KeyboardButton(text="📞 Bog'lanish"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        f"Salom {message.from_user.first_name}! 🚀\nMen sizning shaxsiy yordamchingizman. Qanday yordam bera olaman?",
        reply_markup=main_menu()
    )

@dp.message()
async def handle_messages(message: types.Message):
    # Tugmalar uchun maxsus javoblar
    if message.text == "🛠 Servis xizmati":
        text = ("Biz har xil inverterlarni, stanoklarni va elektronikani tuzatamiz. "
                "Katta korxonalarga borib xizmat ko'rsatishimiz ham mumkin.")
        return await message.answer(text)

    if message.text == "📱 YouTube: AO Studio":
        return await message.answer("AO Studio kanalimizda qiziqarli Shorts videolarini tomosha qiling!")

    if message.text == "👨‍🎓 Magistratura ishi":
        return await message.answer("Sizning ilmiy ishingiz: 'Energiya samaradorligini oshirishning texnologik jarayonlari va intellektual boshqaruv tizimini ishlab chiqish'.")

    if message.text == "📞 Bog'lanish":
        return await message.answer("Men bilan bog'lanish: @mustafo_admin")

    # AI bilan suhbat
    if message.text:
        sent_message = await message.answer("O'ylayapman... ⚡️")
        
        success = False
        for model_name in MODELS:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "Sen aqlli va yordam beruvchi AI muhandissan. Isming Mustafoning yordamchisi."},
                        {"role": "user", "content": message.text}
                    ]
                )
                ai_response = completion.choices[0].message.content
                await bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=ai_response)
                success = True
                break
            except Exception:
                continue
        
        if not success:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text="Xatolik yuz berdi. Birozdan so'ng urinib ko'ring.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
