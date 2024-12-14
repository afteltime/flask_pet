from http.client import responses
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
import os
import redis
from app.worker import redis_url


redis_conn = redis.from_url(redis_url)
load_dotenv(dotenv_path='tgapi.env')
API_TOKEN = os.getenv('API_TOKEN_FOR_TG')
FLASK_API_URL = 'http://localhost:5000/api/feed'
FLASK_API_TOKEN_URL = 'http://localhost:5000/api/token'

ASK_NAME, POST_TEXT = range(2)

def load_posts_to_redis():
    response = requests.get(FLASK_API_URL)
    posts = response.json()

    for post in posts:
        post_key = f"post:{post['id']}"
        if not redis_conn.exists(post_key):
            redis_conn.hmset(post_key, {
                'author': post['author'],
                'timestamp': post['timestamp'],
                'content': post['content'],
                'rating': post['rating']
            })

load_posts_to_redis()



def get_posts_from_redis():
    posts = []
    keys = redis_conn.keys('post:*')
    for key in keys:
        post_data = redis_conn.hgetall(key)
        posts.append({
            'author': post_data[b'author'].decode('utf-8'),
            'timestamp': post_data[b'timestamp'].decode('utf-8'),
            'content': post_data[b'content'].decode('utf-8'),
            'rating': int(post_data[b'rating'])
        })
    posts.sort(key=lambda post: post['timestamp'], reverse=True)
    return posts


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [KeyboardButton("Проверить статус сервера"), KeyboardButton("Получить последние посты")],
        [KeyboardButton("Создать новый пост")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Привет! Выберите действие:', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "Проверить статус сервера":
        await send_status(update, context)
    elif text == "Получить последние посты":
        await send_feed(update, context)
    elif text == "Создать новый пост":
        await update.message.reply_text('Введите ваше имя для публикации поста:')
        return ASK_NAME
    else:
        await update.message.reply_text("Неизвестная команда. Пожалуйста, выберите действие с помощью кнопок.")

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['post_name'] = update.message.text
    await update.message.reply_text('Введите текст поста:')
    return POST_TEXT

async def send_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = context.user_data.get('post_name')
    content = update.message.text
    post_content = f"{user_name} say: {content}"

    payload = {
        'content': post_content
    }

    try:
        session = requests.Session()
        token_response = session.get(FLASK_API_TOKEN_URL)
        csrf_token = token_response.cookies['csrf_token']
        headers = {
            'X-CSRFToken': csrf_token
        }

        response = session.post(FLASK_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            await update.message.reply_text("Ваш пост успешно опубликован!")
        else:
            await update.message.reply_text(f"Не удалось создать пост. Статус: {response.status_code}. Ответ: {response.text}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Ошибка при создании поста: {str(e)}")

    return ConversationHandler.END, load_posts_to_redis()

async def send_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        response = requests.get(FLASK_API_URL)

        if response.status_code == 200:
            await update.message.reply_text("✅ Сервер работает корректно.")
        elif response.status_code == 400:
            await update.message.reply_text("⚠️ Неверный запрос к серверу (400 Bad Request).")
        elif response.status_code == 401:
            await update.message.reply_text("🔒 Требуется авторизация (401 Unauthorized).")
        elif response.status_code == 403:
            await update.message.reply_text("⛔ Доступ запрещен (403 Forbidden).")
        elif response.status_code == 404:
            await update.message.reply_text("🔍 Ресурс не найден (404 Not Found).")
        elif response.status_code == 500:
            await update.message.reply_text("💥 Внутренняя ошибка сервера (500 Internal Server Error).")
        elif response.status_code == 502:
            await update.message.reply_text("🛠️ Ошибка шлюза (502 Bad Gateway).")
        elif response.status_code == 503:
            await update.message.reply_text("🚧 Сервис недоступен (503 Service Unavailable).")
        elif response.status_code == 504:
            await update.message.reply_text("⏱️ Превышено время ожидания шлюза (504 Gateway Timeout).")
        else:
            await update.message.reply_text(f"❓ Неизвестный статус сервера: {response.status_code}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"🚨 Ошибка при подключении к серверу: {str(e)}")

async def send_feed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        posts = get_posts_from_redis()

        if not posts:
            await update.message.reply_text("Нет доступных постов.")
            return

        for post in posts[:5]:  # Ограничение на 5 постов
            await update.message.reply_text(
                f"📢 *{post['author']}*\n"
                f"🕒 {post['timestamp']}\n\n"
                f"{post['content']}\n"
                f"⭐{post['rating']}",
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        await update.message.reply_text(f"Ошибка при запросе постов: {str(e)}")

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex('^Создать новый пост$'), handle_message)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            POST_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_post)]
        },
        fallbacks=[]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling(stop_signals=None)

if __name__ == '__main__':
    main()
