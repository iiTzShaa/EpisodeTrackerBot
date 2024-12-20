import asyncio
import os
from dotenv import load_dotenv
from telegram.error import TimedOut
from telegram.ext import Application, CommandHandler
from file_mange import read_tracked_shows, save_tracked_shows
from Scapper import check_for_new_episode

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

tracked_shows_path = "tracked_shows.json"
tracked_shows = []


class TelegramBot:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.application = Application.builder().token(BOT_TOKEN).build()
            cls._instance.setup_handlers()
        return cls._instance

    def setup_handlers(self):
        """ Set up the command handlers for the bot. """
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("track", self.track))
        self.application.add_handler(CommandHandler("getid", self.getid))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("get_tracked_shows", self.get_tracked_shows))

    async def start(self, update, context):
        """ Handle the /start command. """
        await update.message.reply_text("Hello! Use /track <show_name> to start tracking a show.")

    async def track(self, update, context):
        """ Handle the /track command. """
        if len(context.args) > 0:
            show_name = ' '.join(context.args)
            if show_name not in tracked_shows:
                tracked_shows.append(show_name)
                await update.message.reply_text(f"Tracking new episodes for '{show_name}'.")
                await save_tracked_shows(self.application, update.message.chat_id, show_name)
            else:
                await update.message.reply_text(f"'{show_name}' is already being tracked.")
        else:
            await update.message.reply_text("Please provide the show name after /track.")

    async def help(self, update, context):
        """ Handle the /help command. """
        help_text = (
            "Here are the commands you can use:\n\n"
            "/start - Start the bot and see a welcome message.\n"
            "/track <show_name> - Start tracking a specific TV show. "
            "Replace <show_name> with the title of the show you want to track.\n"
            "/get_tracked_shows - See a list of shows currently being tracked.\n"
            "/help - Show this help message.\n\n"
            "Once you add a show to track, the bot will check for new episodes once and notify you."
        )
        await update.message.reply_text(help_text)

    async def get_tracked_shows(self, update, context):
        """ Handle the /get_tracked_shows command. """
        global tracked_shows
        if not tracked_shows:
            await self.initialize_tracked_shows()

        if tracked_shows:
            message = "Currently tracked shows:\n" + "\n".join(tracked_shows)
        else:
            message = "No shows are currently being tracked."

        await update.message.reply_text(message)

    async def send_notification(self, chat_id, message):
        """Send a notification to the specified chat ID with the given message."""
        bot = self.application.bot
        for _ in range(3):  # Retry up to 3 times
            try:
                await bot.send_message(chat_id=chat_id, text=message)
                break  # Exit the loop if the message is sent successfully
            except TimedOut:
                await asyncio.sleep(2)  # Wait before retrying
        else:
            print(f"Failed to send message after 3 attempts: {message}")

    async def getid(self, update, context):
        """ Handle the /getid command. """
        chat_id = update.message.chat_id
        await update.message.reply_text(f"Your chat ID is: {chat_id}")

    async def initialize_tracked_shows(self):
        """ Initialize tracked shows list. """
        global tracked_shows
        tracked_shows = await read_tracked_shows() or []
        print("Tracked shows initialized:", tracked_shows)

    async def check_for_new_episodes(self):
        """Check for new episodes once and notify if found."""
        print("Checking for new episodes.")
        notified_episodes = {}  # In-memory dictionary for tracking notifications

        # Loop through tracked shows and check for new episodes
        for show_name in tracked_shows:
            new_episode_url = check_for_new_episode(show_name)
            if new_episode_url and new_episode_url != notified_episodes.get(show_name):
                message = f"New episode of '{show_name}' is out! Watch here: {new_episode_url}"
                await self.send_notification(CHAT_ID, message)
                notified_episodes[show_name] = new_episode_url

        print("Check completed. Notifications sent for new episodes.")

    async def run(self):
        """ Start the bot and check for new episodes once. """
        print("Starting bot...")
        global tracked_shows
        tracked_shows = await read_tracked_shows()

        print("Tracked shows:", tracked_shows)
        await self.check_for_new_episodes()
        await self.application.run_polling()


if __name__ == "__main__":
    bot = TelegramBot()
    asyncio.run(bot.run())
