from telegram.ext import Application, CommandHandler
import logging

# Настройка Telegram Bot
TELEGRAM_TOKEN = "7648873218:AAHgzpTF8jMosAsT2BFJPyfg9aU_sfaBD9Q"

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация Telegram Bot
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Команда /start
async def start_command(update, context):
    await update.message.reply_text("👋 Добро пожаловать! Бот работает через polling.")

# Добавление команды
application.add_handler(CommandHandler("start", start_command))

# Запуск polling
if __name__ == "__main__":
    application.run_polling()
