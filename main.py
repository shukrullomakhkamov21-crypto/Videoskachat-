import asyncio
import requests
import uuid
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# ДИҚҚАТ: Токенингни мана шу ерга қўштирноқ ичига ёз
API_TOKEN = '8617193944:AAHKTyrVweAd2uyYK78aZj-wzAll6plkIu8'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

url_storage = {}

def get_cobalt_link(url, is_audio=True):
    api_url = "https://cobalt.tools/api/json"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    data = {
        "url": url,
        "downloadMode": "audio" if is_audio else "video",
        "videoQuality": "720"
    }
    try:
        response = requests.post(api_url, json=data, headers=headers, timeout=15)
        return response.json().get("url")
    except:
        return None

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Салом! 🎬\nЮтуб линкини юборинг ёки қўшиқ номини ёзинг:")

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    link_id = str(uuid.uuid4())[:8]
    url_storage[link_id] = message.text
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 MP3 (Аудио)", callback_data=f"cb_aud_{link_id}"),
         InlineKeyboardButton(text="🎬 MP4 (Видео)", callback_data=f"cb_vid_{link_id}")]
    ])
    await message.answer("Танланг:", reply_markup=kb)

@dp.message(F.text)
async def search_handler(message: types.Message):
    if message.text.startswith("/"): return
    msg = await message.answer("Қидирилмоқда... 🔎")
    query = message.text.replace(" ", "+")
    try:
        search_url = f"https://www.youtube.com/results?search_query={query}"
        response = requests.get(search_url, timeout=10)
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)[:5]
        if not video_ids:
            await msg.edit_text("Ҳеч нарса топилмади.")
            return
        buttons = []
        for i, v_id in enumerate(list(set(video_ids))):
            link_id = str(uuid.uuid4())[:8]
            url_storage[link_id] = f"https://www.youtube.com/watch?v={v_id}"
            buttons.append([InlineKeyboardButton(text=f"🎵 Натижа {i+1} (MP3)", callback_data=f"cb_aud_{link_id}")])
        await msg.edit_text(f"'{message.text}' бўйича топдик:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    except:
        await msg.edit_text("Қидирувда хатолик бўлди.")

@dp.callback_query(F.data.startswith("cb_"))
async def download_callback(call: CallbackQuery):
    _, mode, link_id = call.data.split("_")
    url = url_storage.get(link_id)
    if not url:
        await call.answer("Маълумот эскирган.")
        return
    await call.message.edit_text("Юкланмоқда... ⏳")
    is_audio = (mode == "aud")
    final_url = get_cobalt_link(url, is_audio)
    if final_url:
        try:
            if is_audio:
                await call.message.answer_audio(final_url, caption="Тайёр! 🎵")
            else:
                await call.message.answer_video(final_url, caption="Тайёр! 🎬")
            await call.message.delete()
        except:
            await call.message.edit_text(f"Юклаш линки: {final_url}")
    else:
        await call.message.edit_text("Хатолик: Ютуб блокировкаси ёки сервер банд.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
