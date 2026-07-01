from flask import Flask, request, jsonify
from aiogram import Bot, types
from aiogram.client.session.aiohttp import AiohttpSession
import asyncio
import os
import logging
import base64
from io import BytesIO

logging.basicConfig(level=logging.INFO)

# === НАСТРОЙКИ ===
BOT_TOKEN = "8439897161:AAEkWaO7MZS-pSP1wbLnGN7kqKQ_UTa65Zc"
PROXY_URL = "socks5://37.18.73.60:5566"

app = Flask(__name__)

# === КОРНЕВОЙ МАРШРУТ (ДЛЯ ПРОВЕРКИ) ===
@app.route('/')
def index():
    return "✅ Сервер работает!", 200

# === ПРИЁМ ФОТО ===
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'photo' not in request.files:
            return jsonify({'success': False, 'error': 'Нет файла'}), 400
        
        file = request.files['photo']
        chat_id = request.form.get('chat_id')
        
        if not chat_id:
            return jsonify({'success': False, 'error': 'Нет chat_id'}), 400
        
        # Читаем файл
        photo_data = file.read()
        
        # Отправляем боту (в отдельном потоке)
        asyncio.run(send_photo_to_bot(chat_id, photo_data))
        
        return jsonify({'success': True})
        
    except Exception as e:
        logging.error(f"❌ Ошибка: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

async def send_photo_to_bot(chat_id, photo_data):
    try:
        # Создаём сессию с прокси (если нужно)
        session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None
        bot = Bot(token=BOT_TOKEN, session=session) if session else Bot(token=BOT_TOKEN)
        
        # Отправляем фото
        photo_io = BytesIO(photo_data)
        photo_io.name = 'photo.jpg'
        
        await bot.send_photo(
            chat_id=int(chat_id),
            photo=types.InputFile(photo_io),
            caption="📸 Фото с сайта!"
        )
        
        logging.info(f"✅ Фото отправлено в чат {chat_id}")
        
        await bot.session.close()
        
    except Exception as e:
        logging.error(f"❌ Ошибка отправки фото: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
