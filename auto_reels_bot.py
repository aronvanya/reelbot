import os
import instaloader
import cv2  # Для работы с видеофайлами
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Telegram настройки
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7648873218:AAHgzpTF8jMosAsT2BFJPyfg9aU_sfaBD9Q")

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

# Обработка команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Выберите язык / Choose your language / Chọn ngôn ngữ:",
        reply_markup=language_keyboard(update.effective_user.id)
    )

# Создание клавиатуры выбора языка
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

# Обработка сообщений с ссылками
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_type = update.effective_chat.type
    user_id = update.effective_user.id
    language = user_languages.get(user_id, "ru")

    loading_message = {
        "ru": "Загружаю рилс, подождите...",
        "en": "Downloading reel, please wait...",
        "vi": "Đang tải video, vui lòng đợi..."
    }.get(language, "Загружаю рилс, подождите...")

    error_message = {
        "ru": "Не удалось загрузить видео. Проверьте ссылку.",
        "en": "Failed to download the video. Please check the link.",
        "vi": "Không thể tải video. Vui lòng kiểm tra liên kết."
    }.get(language, "Не удалось загрузить видео. Проверьте ссылку.")

    url = update.message.text.strip()
    if "instagram.com/reel/" in url or "instagram.com/p/" in url:
        message = await update.message.reply_text(loading_message)
        video_path = download_reel(url)
        if video_path:
            try:
                cap = cv2.VideoCapture(video_path)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()

                caption = f"🎥 Видео предоставлено: {update.effective_user.first_name}"
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=open(video_path, 'rb'),
                    width=width,
                    height=height,
                    supports_streaming=True,
                    caption=caption
                )
                await message.delete()
                os.remove(video_path)
            except Exception as e:
                print(f"Ошибка отправки видео: {e}")
                await message.edit_text(error_message)
        else:
            await message.edit_text(error_message)

# Основная функция запуска
def main():
    if not os.path.exists("reels"):
        os.makedirs("reels")

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang_.*"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен. Нажмите Ctrl+C для завершения.")
    application.run_polling()

if __name__ == "__main__":
    main()
