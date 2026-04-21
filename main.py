import asyncio
import requests
import uuid
import re
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# TOKENLAR
API_TOKEN = '8617193944:AAHKTyrVweAd2uyYK78aZj-wzAll6plkIu8'
GEMINI_KEY = 'AIzaSyBGUDN27GVP-VZ-lHJSszIc0TLVDzftVE4' # Sening kalitingni joyladim

# AI ni sozlash
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # Tezkor va aqlli model

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

url_storage = {}

# Cobalt API orqali yuklash funksiyasi
def get_cobalt_link(url, is_audio=True):
    api_url = "https://cobalt.tools/api/json"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    data = {"url": url, "downloadMode": "audio" if is_audio else "video", "videoQuality": "720"}
    try:
        response = requests.post(api_url, json=data, headers=headers, timeout=15)
        return response.json().get("url")
    except:
        return None

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Salom! 🤖 Men AI botman.\n\nSizga qanday yordam bera olaman?\n- Savol bering (AI javob beradi)\n- YouTube link yuboring (Yuklab beraman)\n- Qo'shiq nomini yozing (Qidiraman)")

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    link_id = str(uuid.uuid4())[:8]
    url_storage[link_id] = message.text
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 MP3", callback_data=f"cb_aud_{link_id}"),
         InlineKeyboardButton(text="🎬 MP4", callback_data=f"cb_vid_{link_id}")]
    ])
    await message.answer("Yuklash turini tanlang:", reply_markup=kb)

@dp.callback_query(F.data.startswith("cb_"))
async def download_callback(call: CallbackQuery):
    _, mode, link_id = call.data.split("_")
    url = url_storage.get(link_id)
    if not url:
        await call.answer("Xatolik!")
        return
    await call.message.edit_text("Yuklanmoqda... ⏳")
    final_url = get_cobalt_link(url, mode == "aud")
    if final_url:
        if mode == "aud":
            await call.message.answer_audio(final_url)
        else:
            await call.message.answer_video(final_url)
        await call.message.delete()
    else:
        await call.message.edit_text("Blokirovka tufayli yuklab bo'lmadi.")

@dp.message(F.text)
async def ai_and_search_handler(message: types.Message):
    if message.text.startswith("/"): return
    
    # Agar matn qisqa bo'lsa va qo'shiqqa o'xshasa (ixtiyoriy, lekin AI ga yuboramiz)
    # AI javob berishi uchun:
    msg = await message.answer("O'ylayapman... 🧠")
    try:
        response = model.generate_content(message.text)
        await msg.edit_text(response.text)
    except:
        await msg.edit_text("Hozircha javob bera olmayman.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
