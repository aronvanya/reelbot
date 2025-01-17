import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, InlineKeyboardMarkup, InlineKeyboardButton

# Настройки бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7648873218:AAHgzpTF8jMosAsT2BFJPyfg9aU_sfaBD9Q")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://reelbot.onrender.com")  # Ваш Render Web Service URL

# Инициализация Flask
app = Flask(__name__)

# Telegram Bot Application
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Хранилище языковых настроек пользователей
user_languages = {}

# Функция для команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
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
            "Я — ваш помощник для загрузки рилсов из Instagram прямо в Telegram. 📲\n\n"
            "💡 Как я работаю:\n"
            "1️⃣ Скопируйте ссылку на рилс из Instagram.\n"
            "2️⃣ Отправьте ссылку в этот чат или в группу.\n"
            "3️⃣ Я загружу видео и пришлю его вам или в группу. 🎉"
        )
    elif lang == "en":
        user_languages[user_id] = "en"
        instruction = (
            "👋 Welcome!\n\n"
            "I am your assistant for downloading Instagram reels directly to Telegram. 📲\n\n"
            "💡 How I work:\n"
            "1️⃣ Copy the link to a reel from Instagram.\n"
            "2️⃣ Send the link to this chat or group.\n"
            "3️⃣ I will download the video and send it to you or the group. 🎉"
        )
    elif lang == "vi":
        user_languages[user_id] = "vi"
        instruction = (
            "👋 Chào mừng bạn!\n\n"
            "Tôi là trợ lý của bạn để tải video Reels từ Instagram trực tiếp vào Telegram. 📲\n\n"
            "💡 Tôi làm việc thế nào:\n"
            "1️⃣ Sao chép liên kết tới video Reels từ Instagram.\n"
            "2️⃣ Gửi liên kết vào cuộc trò chuyện này hoặc nhóm.\n"
            "3️⃣ Tôi sẽ tải video và gửi nó cho bạn hoặc nhóm. 🎉"
        )
    await query.edit_message_text(instruction)

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    await update.message.reply_text(f"Вы отправили: {text}")

# Обработка Webhook запросов от Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "OK", 200

# Основная функция запуска
def main():
    # Добавление обработчиков команд и сообщений
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang_.*"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Установка Webhook
    application.run_webhook(
        listen="0.0.0.0",  # Слушаем все подключения
        port=int(os.getenv("PORT", 8080)),  # Порт для Render Web Service
        webhook_url=f"{WEBHOOK_URL}/webhook"  # URL для Telegram Webhook
    )

if __name__ == "__main__":
    main()
