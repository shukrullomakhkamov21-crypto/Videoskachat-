import asyncio
import os
import uuid
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL

# BU YERGA O'Z TOKENINGNI YOZ
API_TOKEN = '8617193944:AAHKTyrVweAd2uyYK78aZj-wzAll6plkIu8'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

url_storage = {}

def get_ydl_opts(mode, output_name):
    if mode == 'audio':
        return {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_name}.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        }
    else:
        return {'format': 'best', 'outtmpl': f'{output_name}.%(ext)s'}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Salom! 🎬\nLink yuboring (YT, Insta, TikTok) yoki qo'shiq nomini yozing:")

@dp.message(F.text.startswith("http"))
async def link_handler(message: types.Message):
    link_id = str(uuid.uuid4())[:8]
    url_storage[link_id] = message.text
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 MP3", callback_data=f"dl_audio_{link_id}"),
         InlineKeyboardButton(text="🎬 MP4", callback_data=f"dl_video_{link_id}")]
    ])
    await message.answer("Tanlang:", reply_markup=kb)

@dp.callback_query(F.data.startswith("dl_"))
async def download_callback(call: CallbackQuery):
    _, mode, link_id = call.data.split("_")
    url = url_storage.get(link_id)
    if not url:
        await call.answer("Xato!")
        return
    await call.message.edit_text("Yuklanmoqda... ⏳")
    file_name = f"file_{call.from_user.id}"
    opts = get_ydl_opts(mode, file_name)
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = 'mp3' if mode == 'audio' else info['ext']
            final_file = f"{file_name}.{ext}"
            await (call.message.answer_audio(types.FSInputFile(final_file)) if mode == 'audio' 
                   else call.message.answer_video(types.FSInputFile(final_file)))
            if os.path.exists(final_file): os.remove(final_file)
    except Exception as e:
        await call.message.answer(f"Xatolik: {e}")

@dp.message(F.text)
async def search_handler(message: types.Message):
    if message.text.startswith("/"): return
    msg = await message.answer("🔎")
    with YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
        results = ydl.extract_info(f"ytsearch5:{message.text}", download=False)['entries']
    buttons = []
    for r in results:
        l_id = str(uuid.uuid4())[:8]
        url_storage[l_id] = r['webpage_url']
        buttons.append([InlineKeyboardButton(text=r['title'][:30], callback_data=f"dl_audio_{l_id}")])
    await msg.edit_text("Natijalar:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
