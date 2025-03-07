import os
import random
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import yt_dlp as youtube_dl

from app.data import (
    TEMP_DIR,
    RAPID_API_KEY,
    RAPID_API_HOST
)

# ==============================================================================================
# СКАЧИВАНИЕ ВИДОСОВ ИЗ ТИК ТОКА
# ==============================================================================================

async def tiktok_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Чтоб скачать видос с тик тока, просто кинь ссылку')

# Отсылание видоса из тик тока в формате файла юзеру
async def handle_tik_tok(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text

    if "tiktok.com" in message_text:
        url = message_text.split()[0] # [0] нужен для случая, если в сообщении 
                                    # от юзера после тик ток ссылки через пробел идут еще слова
        try:
            video_url = await get_tiktok_video_url(url)
            if video_url:
                video_path = await download_video(video_url)
                if video_path:
                    with open(video_path, 'rb') as video_file:
                        await update.message.reply_video(video_file, caption="На держи, тик ток кид ебучий")
                    os.remove(video_path)
            else:
                await update.message.reply_text("Че за хуйню ты скинул, это не ссылка на тики ток")
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}")

# функция для получения юрлки тики тока
async def get_tiktok_video_url(url):
    api_url = "https://tiktok-download-without-watermark.p.rapidapi.com/analysis"
    
    querystring = {"url": url}
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers=headers, params=querystring) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('code') == 0:
                    return data['data']['play']
            return None

# скачивание тики ток видоса
async def download_video(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                video_path = os.path.join(TEMP_DIR, f'tiktok_video_{random.randint(1000, 9999)}.mp4')
                with open(video_path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                return video_path
            else:
                print(f"Failed to download video. Status code: {response.status}")
                return None
            
# ==============================================================================================
# СКАЧИВАНИЕ ЗВУКОВ ИЗ ЮТУБА + КОНВЕРТ В МП3 ФАЙЛ
# ==============================================================================================

async def mp3_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mp3_link = update.message.text
    parts = mp3_link.split(' ', 1)

    if len(parts) != 2:
        await update.message.reply_text('Пожалуйста, используйте команду в формате: /mp3 <ссылка на ютуб>')
    elif not (parts[1][:23] == "https://www.youtube.com" or parts[1][:16] == "https://youtu.be"):
        await update.message.reply_text('ЭТО НЕ ССЫЛКА НА ЮТУБ, БРО')
        return ConversationHandler.END
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': 'C:/Users/m1rrx/Downloads/ffmpeg-2024-10-10-git-0f5592cfc7-full_build/ffmpeg-2024-10-10-git-0f5592cfc7-full_build/bin',
            'outtmpl': '%(title)s.%(ext)s',  
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(parts[1], download=True) 
            filename = ydl.prepare_filename(info_dict).rsplit('.', 1)[0] + '.mp3'

        with open(filename, 'rb') as file:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=file)

        os.remove(filename)