from flask import Flask, request, jsonify
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

BOT_TOKEN = "8439897161:AAEkWaO7MZS-pSP1wbLnGN7kqKQ_UTa65Zc"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

PROXY_HOST = "37.18.73.60"
PROXY_PORT = 5566
PROXY_URL = f"socks5://{PROXY_HOST}:{PROXY_PORT}"

proxies = {
    'http': PROXY_URL,
    'https': PROXY_URL
}

@app.route('/')
def index():
    return "✅ Сервер работает!", 200

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'photo' not in request.files:
            return jsonify({'success': False, 'error': 'Нет файла'}), 400
        
        file = request.files['photo']
        chat_id = request.form.get('chat_id')
        
        if not chat_id:
            return jsonify({'success': False, 'error': 'Нет chat_id'}), 400
        
        files = {'photo': (file.filename, file.read(), file.content_type)}
        data = {'chat_id': chat_id, 'caption': '📸 Фото с сайта!'}
        
        response = requests.post(
            f"{TELEGRAM_API}/sendPhoto",
            files=files,
            data=data,
            proxies=proxies
        )
        
        if response.status_code == 200:
            logging.info(f"✅ Фото отправлено в чат {chat_id}")
            return jsonify({'success': True})
        else:
            logging.error(f"❌ Ошибка Telegram: {response.text}")
            return jsonify({'success': False, 'error': response.text}), 500
        
    except Exception as e:
        logging.error(f"❌ Ошибка: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
