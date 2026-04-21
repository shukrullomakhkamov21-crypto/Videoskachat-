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
GEMINI_KEY = 'AIzaSyBGUDN27GVP-VZ-lHJSszIc0TLVDzftVE4'

# AI ni sozlash - Xatolarni oldini olish uchun try-except ichida
try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"AI sozlashda xato: {e}")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

url_storage = {}

def get_cobalt_link(url, is_audio=True):
    api_url = "https://cobalt.tools/api/json"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    data = {"url": url, "downloadMode": "audio" if is_audio else "video", "videoQuality": "720"}
    try:
        response = requests.post(api_url, json=data, headers=headers, timeout=20)
        if response.status_code == 200:
            return response.json().get("url")
    except:
        return None
    return None

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Salom Shukrullo! 🤖 Men sening AI yordamchingman.\n\nSavol bering (AI javob beradi) yoki YouTube link yuboring.")

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    link_id = str(uuid.uuid4())[:8]
    url_storage[link_id] = message.text
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 MP3 Yuklash", callback_data=f"cb_aud_{link_id}"),
         InlineKeyboardButton(text="🎬 MP4 Yuklash", callback_data=f"cb_vid_{link_id}")]
    ])
    await message.answer("Nima yuklaymiz?", reply_markup=kb)

@dp.callback_query(F.data.startswith("cb_"))
async def download_callback(call: CallbackQuery):
    _, mode, link_id = call.data.split("_")
    url = url_storage.get(link_id)
    if not url:
        await call.answer("Ma'lumot topilmadi!")
        return
    
    await call.message.edit_text("Yuklash boshlandi... ⏳")
    final_url = get_cobalt_link(url, mode == "aud")
    
    if final_url:
        try:
            if mode == "aud":
                await call.message.answer_audio(final_url, caption="Tayyor! 🎵")
            else:
                await call.message.answer_video(final_url, caption="Tayyor! 🎬")
            await call.message.delete()
        except:
            await call.message.edit_text(f"Telegram orqali yuborib bo'lmadi. Mana link: {final_url}")
    else:
        await call.message.edit_text("YouTube blokirovkasi! Boshqa link sinab ko'ring.")

@dp.message(F.text)
async def ai_handler(message: types.Message):
    if message.text.startswith("/"): return
    
    # AI javob berishini kutish vaqtida foydalanuvchiga signal berish
    sent_msg = await message.answer("O'ylayapman... 🧠")
    
    try:
        # AI dan javob olish
        response = model.generate_content(message.text)
        # Javobni qismlarga bo'lish (agar juda uzun bo'lsa)
        if response.text:
            await sent_msg.edit_text(response.text[:4000])
        else:
            await sent_msg.edit_text("AI hozircha tushunmadi, savolni aniqroq yozing.")
    except Exception as e:
        print(f"Xato: {e}")
        await sent_msg.edit_text("AI bilan bog'lanishda muammo bo'ldi. API kalitini tekshiring.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
