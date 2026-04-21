import asyncio
import requests
import uuid
import re
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# YANGI TOKEN VA GEMINI KEY
API_TOKEN = '8617193944:AAHO4q341-7WY34DjI6PV5B8JUNrS-xNsv8'
GEMINI_KEY = 'AIzaSyBGUDN27GVP-VZ-lHJSszIc0TLVDzftVE4'

# AI sozlamalari
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

url_storage = {}

def get_cobalt_link(url, is_audio=True):
    api_url = "https://cobalt.tools/api/json"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    data = {"url": url, "downloadMode": "audio" if is_audio else "video", "videoQuality": "720"}
    try:
        response = requests.post(api_url, json=data, headers=headers, timeout=20)
        return response.json().get("url")
    except:
        return None

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Salom Shukrullo! 🤖 Men endi AI yordamchingman.\n\nSavol bering yoki YouTube link yuboring.")

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    link_id = str(uuid.uuid4())[:8]
    url_storage[link_id] = message.text
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 MP3", callback_data=f"cb_aud_{link_id}"),
         InlineKeyboardButton(text="🎬 MP4", callback_data=f"cb_vid_{link_id}")]
    ])
    await message.answer("Nima yuklaymiz?", reply_markup=kb)

@dp.callback_query(F.data.startswith("cb_"))
async def download_callback(call: CallbackQuery):
    _, mode, link_id = call.data.split("_")
    url = url_storage.get(link_id)
    if not url:
        await call.answer("Ma'lumot topilmadi!")
        return
    await call.message.edit_text("Yuklanmoqda... ⏳")
    final_url = get_cobalt_link(url, mode == "aud")
    if final_url:
        try:
            if mode == "aud":
                await call.message.answer_audio(final_url)
            else:
                await call.message.answer_video(final_url)
            await call.message.delete()
        except:
            await call.message.edit_text(f"Tayyor: {final_url}")
    else:
        await call.message.edit_text("Blokirovka tufayli yuklab bo'lmadi.")

@dp.message(F.text)
async def ai_handler(message: types.Message):
    if message.text.startswith("/"): return
    msg = await message.answer("O'ylayapman... 🧠")
    try:
        response = model.generate_content(message.text)
        await msg.edit_text(response.text)
    except Exception as e:
        await msg.edit_text("Hozircha javob bera olmayman. Savolni qaytadan yozing.")

async def main():
    # Eski xabarlarni o'chirib yuborish (Conflict oldini olish uchun)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
