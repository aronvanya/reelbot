import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application

# Настройки Telegram Bot
TELEGRAM_TOKEN = "7648873218:AAHgzpTF8jMosAsT2BFJPyfg9aU_sfaBD9Q"
WEBHOOK_URL = "https://reelbot.onrender.com"

# Инициализация Flask
app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Application
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Маршрут для проверки работы сервера
@app.route("/", methods=["GET"])
def home():
    return "Сервер Flask работает с Telegram Webhook!", 200

# Маршрут для Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        application.process_update(update)
        logger.info("Webhook успешно обработан.")
        return "OK", 200
    except Exception as e:
        logger.error(f"Ошибка обработки Webhook: {e}")
        return "Ошибка", 500

# Запуск Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
