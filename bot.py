import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

# === Логування ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# === Фунція для очистки імені файлу ===
def clean_filename(filename: str) -> str:
    """Видалення заборонених символів"""
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', filename)  # Видалення заборонених символів


# === Функція завантаження відео ===
def download_video(url: str) -> str:
    """Скачує відео за посиланням та повертає шлях до файлу """
    try:
        os.makedirs('downloads', exist_ok=True)  # створюємо папку для завантаження відео
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # шлях для збереження файлу
            'quiet': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            raw_video_path = ydl.prepare_filename(info_dict)  # шлях до відео
            cleaned_path = 'downloads/' + clean_filename(os.path.basename(raw_video_path))  # Очистка имени файла
            os.rename(raw_video_path, cleaned_path)  # Змінюємо файл
            return cleaned_path
    except Exception as e:
        logging.error(f"Помилка під час завантажування  відео: {e}")
        return f"Помилка під час завантажування  відео: {e}"


# === обробник /START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Відправлення привітального смс"""
    await update.message.reply_text(
        "👋 Привіт відправ посилання на відео з Tik-Tok чи YouTube і я скачаю його для тебе )"
    )

# === обробник смс із посиланням ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Оброблює посилання і відправляє відео"""
    url = update.message.text.strip()

    if 'youtube.com' in url or 'youtu.be' in url or 'tiktok.com' in url:
        await update.message.reply_text("⏳ Зачекай трохи качаю відео , ці фіксики задрали так повільно все робити ...")

        video_path = download_video(url)

        if "Ошибка" in video_path:
            await update.message.reply_text(f"❌ {video_path}")
        else:
            try:
                await update.message.reply_video(video=open(video_path, 'rb'))  # Відправляємо відео
                os.remove(video_path)  # Видалення відео після відправлення
            except Exception as e:
                logging.error(f"Помилка відправлення відео: {e}")
                await update.message.reply_text("❌ Виникла помилка при відправлені відео ")
    else:
        await update.message.reply_text("🚫 ***Відправте коректне посилання на YouTube  або  TikTok відео.")


# === ОСНОВНОЙ ЗАПУСК БОТА ===
def main():
    """Запуск Telegram-бота."""
    TOKEN = '7082564547:AAG9XMs-60ddGL7kmOKukEbt2J73-GTqRts'

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Бот готовий до роботи ...")
    app.run_polling()


if __name__ == '__main__':
    main()
