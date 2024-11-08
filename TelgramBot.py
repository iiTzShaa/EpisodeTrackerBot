import aiofiles
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from file_mange import save_tracked_shows, read_tracked_shows


tracked_shows = []

async def initialize_tracked_shows():
    global tracked_shows
    tracked_shows = await read_tracked_shows() or []
    print("Tracked shows initialized:", tracked_shows)  # Debugging

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Here are the commands you can use:\n\n"
        "/start - Start the bot and see a welcome message.\n"
        "/track <show_name> - Start tracking a specific TV show. "
        "Replace <show_name> with the title of the show you want to track.\n"
        "/get_tracked_shows - See a list of shows currently being tracked.\n"
        "/help - Show this help message.\n\n"
        "Once you add a show to track, the bot will check for new episodes at specific times and notify you."
    )
    await update.message.reply_text(help_text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! Use /track <show_name> to start tracking a show.")

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) > 0:
        show_name = ' '.join(context.args)
        if show_name not in tracked_shows:
            tracked_shows.append(show_name)
            await update.message.reply_text(f"Tracking new episodes for '{show_name}'.")
            await save_tracked_shows(tracked_shows)  # Save the updated list
        else:
            await update.message.reply_text(f"'{show_name}' is already being tracked.")
    else:
        await update.message.reply_text("Please provide the show name after /track.")

async def get_tracked_shows(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global tracked_shows
    if not tracked_shows:
        await initialize_tracked_shows()

    if tracked_shows:
        message = "Currently tracked shows:\n" + "\n".join(tracked_shows)
    else:
        message = "No shows are currently being tracked."

    await update.message.reply_text(message)

async def send_notification(application, chat_id, message):
    bot = application.bot  # Access the bot instance directly from the application
    await bot.send_message(chat_id=chat_id, text=message)

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    await update.message.reply_text(f"Your chat ID is: {chat_id}")
