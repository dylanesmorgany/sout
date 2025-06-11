import logging
import os
from pathlib import Path
from uuid import uuid4

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

import yt_dlp

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

LOG_FILE = Path("logs.json")

def log_request(user: str, query: str, file_path: str | None):
    """Append request info to JSON log file."""
    import json
    entry = {
        "user": user,
        "query": query,
        "file": file_path,
        "id": str(uuid4()),
    }
    if LOG_FILE.exists():
        data = json.loads(LOG_FILE.read_text())
    else:
        data = []
    data.append(entry)
    LOG_FILE.write_text(json.dumps(data, indent=2))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me the name of a song and I'll return the audio!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    user = update.effective_user.username or str(update.effective_user.id)
    logger.info("Received query from %s: %s", user, query)
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "outtmpl": "%(title)s.%(ext)s",
            "audioformat": "mp3",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
            ydl.download([info["webpage_url"]])
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        await update.message.reply_audio(audio=open(filename, "rb"))
        log_request(user, query, filename)
        os.remove(filename)
    except Exception as e:
        logger.exception("Error processing request")
        await update.message.reply_text("Sorry, I couldn't find that song.")
        log_request(user, query, None)

async def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Please set TELEGRAM_BOT_TOKEN environment variable")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
