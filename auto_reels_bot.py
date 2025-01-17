import os
import instaloader
import cv2  # Для чтения размеров видео
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from server import keep_alive  # Импортируем веб-сервер

# Telegram настройки
TELEGRAM_TOKEN = "7648873218:AAHgzpTF8jMosAsT2BFJPyfg9aU_sfaBD9Q"
GROUP_CHAT_ID = -1002055756304  # ID вашей группы

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

    print(f"Получено обновление: {update}")

    if not update.message:
        print("Нет сообщения для обработки")
        return

    url = update.message.text.strip()
    user_name = update.effective_user.first_name

    if "instagram.com/reel/" in url or "instagram.com/p/" in url:
        loading_message = await update.message.reply_text(loading_message_text)
        print("Проверяем ссылку...")
        video_path = download_reel(url)
    else:
        print("Неподдерживаемая ссылка")
        return

    if video_path:
        try:
            cap = cv2.VideoCapture(video_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()

            print("Отправляем видео в чат...")
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
            if update.message:
                await update.message.delete()
        except Exception as e:
            print(f"Ошибка отправки видео: {e}")
            if loading_message:
                await loading_message.edit_text(error_message_text)
    else:
        if loading_message:
            await loading_message.edit_text(error_message_text)

# Функция для обработки команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Выберите язык / Choose your language / Chọn ngôn ngữ:",
        reply_markup=language_keyboard(update.effective_user.id)
    )

# Функция для создания клавиатуры языка
def language_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Русский", callback_data=f"lang_ru_{user_id}")],
        [InlineKeyboardButton("English", callback_data=f"lang_en_{user_id}")],
        [InlineKeyboardButton("Tiếng Việt", callback_data=f"lang_vi_{user_id}")]
    ])
    # Функция для обработки выбора языка
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query or not query.id:
        print("Неверный или отсутствующий callback query")
        return

    try:
        await query.answer()
    except Exception as e:
        print(f"Ошибка callback query: {e}")
        return

    data = query.data.split("_")
    lang = data[1]
    user_id = int(data[2])

    if lang == "ru":
        user_languages[user_id] = "ru"
        instruction = (
            "👋 Добро пожаловать!\\n\\n"
            "Я — ваш помощник для загрузки рилсов из Instagram прямо в Telegram. 📲\\n\\n"
            "💡 **Как я работаю?**\\n"
            "1️⃣ Скопируйте ссылку на рилс из Instagram.\\n"
            "2️⃣ Отправьте ссылку в этот чат или в группу/канал, где я добавлен.\\n"
            "3️⃣ Я загружу видео и пришлю его в вашу группу или канал.\\n\\n"
            "🛠 **Как добавить меня в группу или канал?**\\n"
            "1️⃣ Добавьте меня в группу/канал.\\n"
            "2️⃣ Назначьте меня администратором.\\n"
            "3️⃣ Наслаждайтесь автоматической загрузкой рилсов! 🎉\\n\\n"
            "Если у вас возникли вопросы или предложения, пишите разработчику: [vanyaaronov@gmail.com](mailto:vanyaaronov@gmail.com). Спасибо, что выбрали меня! 😊"
        )
    elif lang == "en":
        user_languages[user_id] = "en"
        instruction = (
            "👋 Welcome!\\n\\n"
            "I am your assistant for downloading Instagram reels directly to Telegram. 📲\\n\\n"
            "💡 **How do I work?**\\n"
            "1️⃣ Copy the link to a reel from Instagram.\\n"
            "2️⃣ Send the link to this chat or a group/channel where I am added.\\n"
            "3️⃣ I will download the video and send it to your group or channel.\\n\\n"
            "🛠 **How to add me to a group or channel?**\\n"
            "1️⃣ Add me to the group/channel.\\n"
            "2️⃣ Make me an admin.\\n"
            "3️⃣ Enjoy automatic reel downloads! 🎉\\n\\n"
            "If you have any questions or suggestions, contact the developer: [vanyaaronov@gmail.com](mailto:vanyaaronov@gmail.com). Thank you for choosing me! 😊"
        )
    elif lang == "vi":
        user_languages[user_id] = "vi"
        instruction = (
            "👋 Chào mừng bạn!\\n\\n"
            "Tôi là trợ lý của bạn để tải video Reels từ Instagram trực tiếp vào Telegram. 📲\\n\\n"
            "💡 **Tôi hoạt động như thế nào?**\\n"
            "1️⃣ Sao chép liên kết tới video Reels từ Instagram.\\n"
            "2️⃣ Gửi liên kết vào cuộc trò chuyện này hoặc nhóm/kênh mà tôi đã được thêm vào.\\n"
            "3️⃣ Tôi sẽ tải video và gửi nó đến nhóm hoặc kênh của bạn.\\n\\n"
            "🛠 **Làm thế nào để thêm tôi vào nhóm hoặc kênh?**\\n"
            "1️⃣ Thêm tôi vào nhóm/kênh.\\n"
            "2️⃣ Đặt tôi làm quản trị viên.\\n"
            "3️⃣ Tận hưởng việc tải video Reels tự động! 🎉\\n\\n"
            "Nếu bạn có bất kỳ câu hỏi hoặc đề xuất nào, hãy liên hệ với nhà phát triển: [vanyaaronov@gmail.com](mailto:vanyaaronov@gmail.com). Cảm ơn bạn đã chọn tôi! 😊"
        )

    if query.message.text != instruction:
        await query.edit_message_text(instruction, parse_mode="Markdown", reply_markup=language_keyboard(user_id))

# Функция для обработки ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Исключение поймано: {context.error}")
    if update and isinstance(update, Update):
        try:
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        except Exception as e:
            print(f"Ошибка при отправке сообщения об ошибке: {e}")

# Основная функция
def main():
    if not os.path.exists("reels"):
        os.makedirs("reels")

    keep_alive()  # Для поддержки активности на Render

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang_.*"))
    application.add_handler(MessageHandler(filters.TEXT & (filters.Chat(GROUP_CHAT_ID) | filters.ChatType.PRIVATE), handle_message))

    application.add_error_handler(error_handler)

    print("Бот запущен. Нажмите Ctrl+C для завершения.")
    application.run_polling()  # Переключаемся на polling
