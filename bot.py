import os
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Настройки бота
TELEGRAM_TOKEN = "7648873218:AAHgzpTF8jMosAsT2BFJPyfg9aU_sfaBD9Q"
WEBHOOK_URL = "https://reelbot.onrender.com"

# Инициализация Flask
app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Application
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Хранилище языковых настроек пользователей
user_languages = {}

# Функция для команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Добро пожаловать!\n\n"
        "Я — ваш помощник для загрузки рилсов из Instagram прямо в Telegram. 📲\n\n"
        "Выберите язык / Choose your language / Chọn ngôn ngữ:",
        reply_markup=language_keyboard(update.effective_user.id)
    )

# Клавиатура для выбора языка
def language_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Русский", callback_data=f"lang_ru_{user_id}")],
        [InlineKeyboardButton("English", callback_data=f"lang_en_{user_id}")],
        [InlineKeyboardButton("Tiếng Việt", callback_data=f"lang_vi_{user_id}")]
    ])

# Обработка выбора языка
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.id:
        return

    await query.answer()

    data = query.data.split("_")
    lang = data[1]
    user_id = int(data[2])

    if lang == "ru":
        user_languages[user_id] = "ru"
        instruction = (
            "👋 Добро пожаловать!\n\n"
            "💡 **Как я работаю:**\n"
            "1️⃣ Скопируйте ссылку на рилс из Instagram.\n"
            "2️⃣ Отправьте ссылку в этот чат или в группу, где я добавлен.\n"
            "3️⃣ Я загружу видео и пришлю его вам или в группу. 🎉"
        )
    elif lang == "en":
        user_languages[user_id] = "en"
        instruction = (
            "👋 Welcome!\n\n"
            "💡 **How I work:**\n"
            "1️⃣ Copy the link to a reel from Instagram.\n"
            "2️⃣ Send the link to this chat or group where I am added.\n"
            "3️⃣ I will download the video and send it to you or the group. 🎉"
        )
    elif lang == "vi":
        user_languages[user_id] = "vi"
        instruction = (
            "👋 Chào mừng bạn!\n\n"
            "💡 **Tôi hoạt động như thế nào:**\n"
            "1️⃣ Sao chép liên kết tới video Reels từ Instagram.\n"
            "2️⃣ Gửi liên kết vào cuộc trò chuyện này hoặc nhóm.\n"
            "3️⃣ Tôi sẽ tải video và gửi nó cho bạn hoặc nhóm. 🎉"
        )
    await query.edit_message_text(instruction, parse_mode="Markdown")

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    language = user_languages.get(user_id, "ru")
    response = {
        "ru": "Вы отправили: {text}",
        "en": "You sent: {text}",
        "vi": "Bạn đã gửi: {text}",
    }.get(language, "Вы отправили: {text}")

    await update.message.reply_text(response.format(text=update.message.text))

# Обработка Webhook запросов от Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        logger.info(f"Получен Webhook: {data}")
        update = Update.de_json(data, application.bot)
        application.process_update(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Ошибка обработки Webhook: {e}")
        return "Ошибка", 500

# Тестовый маршрут для проверки работы сервера
@app.route("/", methods=["GET"])
def home():
    return "Бот работает!", 200

# Основная функция запуска
def main():
    # Добавление обработчиков команд и сообщений
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang_.*"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Установка Webhook
    application.run_webhook(
        listen="0.0.0.0",  # Принимаем все подключения
        port=int(os.getenv("PORT", 8080)),  # Порт для Render Web Service
        webhook_url=f"{WEBHOOK_URL}/webhook",  # URL для Telegram Webhook
    )

if __name__ == "__main__":
    main()
