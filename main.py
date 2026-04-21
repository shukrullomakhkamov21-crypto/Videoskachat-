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
    opts = {
        'format': 'bestaudio/best' if mode == 'audio' else 'best',
        'outtmpl': f'{output_name}.%(ext)s',
        # YouTube "Бот эмаслигингни тасдиқла" демаслиги учун Android клиентларини ишлатамиз
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['dash', 'hls']
            }
        },
        'quiet': True,
        'no_warnings': True,
    }
    
    if mode == 'audio':
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    return opts

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Salom! 🎬\nYouTube, Instagram yoki TikTok ssilkasini yuboring yoki qo'shiq nomini yozing:")

@dp.message(F.text.startswith("http"))
async def link_handler(message: types.Message):
    link_id = str(uuid.uuid4())[:8]
    url_storage[link_id] = message.text
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 MP3 (Audio)", callback_data=f"dl_audio_{link_id}"),
         InlineKeyboardButton(text="🎬 MP4 (Video)", callback_data=f"dl_video_{link_id}")]
    ])
    await message.answer("Yuklab olish turini tanlang:", reply_markup=kb)

@dp.callback_query(F.data.startswith("dl_"))
async def download_callback(call: CallbackQuery):
    _, mode, link_id = call.data.split("_")
    url = url_storage.get(link_id)
    if not url:
        await call.answer("Xatolik: Ma'lumot topilmadi!")
        return
    
    await call.message.edit_text("Yuklanmoqda... ⏳\n(Bu biroz vaqt olishi mumkin)")
    
    file_name = f"file_{call.from_user.id}_{link_id}"
    opts = get_ydl_opts(mode, file_name)
    
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = 'mp3' if mode == 'audio' else info['ext']
            final_file = f"{file_name}.{ext}"
            
            if mode == 'audio':
                await call.message.answer_audio(types.FSInputFile(final_file), caption="Tayyor! 🎵")
            else:
                await call.message.answer_video(types.FSInputFile(final_file), caption="Tayyor! 🎬")
            
            # Faylni yuborgandan keyin serverdan o'chirish
            if os.path.exists(final_file):
                os.remove(final_file)
                
    except Exception as e:
        await call.message.answer(f"Xatolik yuz berdi: {str(e)[:100]}...")
    finally:
        await call.answer()

@dp.message(F.text)
async def search_handler(message: types.Message):
    if message.text.startswith("/"): return
    msg = await message.answer("Qidirilmoqda... 🔎")
    try:
        with YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
            results = ydl.extract_info(f"ytsearch5:{message.text}", download=False)['entries']
        
        buttons = []
        for r in results:
            l_id = str(uuid.uuid4())[:8]
            url_storage[l_id] = r['webpage_url']
            buttons.append([InlineKeyboardButton(text=r['title'][:40], callback_data=f"dl_audio_{l_id}")])
        
        await msg.edit_text("Natijalar (MP3 yuklash uchun bosing):", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    except:
        await msg.edit_text("Hech narsa topilmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
