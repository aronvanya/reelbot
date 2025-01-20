import os
import instaloader
import cv2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Telegram настройки
TELEGRAM_TOKEN = "7648873218:AAHgzpTF8jMosAsT2BFJPyfg9aU_sfaBD9Q"

# Инициализация Instaloader
loader = instaloader.Instaloader()

# Глобальный словарь для хранения языка пользователя
user_languages = {}

# Функция для загрузки рилсов
def download_reel(url):
    try:
        post = instaloader.Post.from_shortcode(loader.context, url.split("/")[-2])
        loader.download_post(post, target="reels")
        for file in os.listdir("reels"):
            if file.endswith(".mp4"):
                return os.path.join("reels", file)
    except Exception as e:
        print(f"Ошибка загрузки рилса: {e}")
        return None

# Обработка сообщений с ссылками
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_type = update.effective_chat.type
    user_id = update.effective_user.id
    language = user_languages.get(user_id, "ru")  # По умолчанию русский

    loading_message_text = {
        "ru": "Загружаю рилс, подождите...",
        "en": "Downloading reel, please wait...",
        "vi": "Đang tải video, vui lòng đợi..."
    }.get(language, "Загружаю рилс, подождите...")

    error_message_text = {
        "ru": "Не удалось загрузить видео. Проверьте ссылку.",
        "en": "Failed to download the video. Please check the link.",
        "vi": "Không thể tải video. Vui lòng kiểm tra liên kết."
    }.get(language, "Не удалось загрузить видео. Проверьте ссылку.")

    user_sent_text = {
        "ru": "Видео отправлено пользователем: {user_name}",
        "en": "Video sent by user: {user_name}",
        "vi": "Video được gửi bởi người dùng: {user_name}"
    }.get(language, "Видео отправлено пользователем: {user_name}")

    url = update.message.text.strip()
    user_name = update.effective_user.first_name

    if "instagram.com/reel/" in url or "instagram.com/p/" in url:
        loading_message = await update.message.reply_text(loading_message_text)
        video_path = download_reel(url)
    else:
        return

    if video_path:
        try:
            cap = cv2.VideoCapture(video_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()

            caption_text = user_sent_text.format(user_name=user_name)
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=open(video_path, 'rb'),
                width=width,
                height=height,
                supports_streaming=True,
                caption=caption_text
            )
            await loading_message.delete()
            os.remove(video_path)
        except Exception as e:
            print(f"Ошибка отправки видео: {e}")
            if loading_message:
                await loading_message.edit_text(error_message_text)
    else:
        if loading_message:
            await loading_message.edit_text(error_message_text)

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Добро пожаловать! Отправьте ссылку на рилс из Instagram."
    )

# Основная функция
def main():
    if not os.path.exists("reels"):
        os.makedirs("reels")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.GROUPS | filters.ChatType.PRIVATE), handle_message))

    # Запуск вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        webhook_url=f"https://<ваш_домен>.railway.app/webhook"
    )

if __name__ == "__main__":
    main()
