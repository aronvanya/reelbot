import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройки Telegram Bot
TELEGRAM_TOKEN = "7648873218:AAHgzpTF8jMosAsT2BFJPyfg9aU_sfaBD9Q"
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Инициализация Flask
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Корневой маршрут для проверки сервера
@app.route("/", methods=["GET"])
def home():
    logging.info("Запрос на корневой маршрут")
    return "Бот работает!", 200

# Маршрут для обработки Webhook запросов
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        application.process_update(update)
        logging.info("Webhook успешно обработан")
        return "OK", 200
    except Exception as e:
        logging.error(f"Ошибка обработки Webhook: {e}")
        return "Ошибка", 500

# Функция для команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("👋 Добро пожаловать! Бот работает.")

# Функция для обработки текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Вы написали: {update.message.text}")

# Добавление обработчиков
application.add_handler(CommandHandler("start", start_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Основная функция запуска
if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        webhook_url="https://reelbot.onrender.com/webhook",
    )
