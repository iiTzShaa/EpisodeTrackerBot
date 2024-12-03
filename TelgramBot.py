import asyncio
import json
import os
import time
from dotenv import load_dotenv
import aiofiles
from telegram.ext import Application, CommandHandler
from file_mange import save_notified_episodes, read_tracked_shows, save_tracked_shows, load_notified_episodes
from Scapper import check_for_new_episode

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

tracked_shows_path = "tracked_shows.json"
last_reset_time = time.time()
last_modified_time = None
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


    # Handle time for automation reset
    async def load_last_reset_time(self):
        try:
            async with aiofiles.open("last_reset_time.json", "r") as file:
                content = await file.read()
                if content.strip():  # Check if content is not empty
                    return float(content)
                else:
                    return time.time()  # Return current time if content is empty
        except FileNotFoundError:
            return time.time()  # If file doesn't exist, return current time
        except ValueError:
            return time.time()

    # Method to save the last reset time to a file
    async def save_last_reset_time(self):
        async with aiofiles.open("last_reset_time.json", "w") as file:
            await file.write(str(self.last_reset_time))

    # Initialize last_reset_time
    async def initialize_reset_time(self):
        self.last_reset_time = await self.load_last_reset_time()

    #Handlers
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
            "Once you add a show to track, the bot will check for new episodes at specific times and notify you."
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
        """ Send a notification to the specified chat ID with the given message. """
        bot = self.application.bot
        await bot.send_message(chat_id=chat_id, text=message)

    async def getid(self, update, context):
        """ Handle the /getid command. """
        chat_id = update.message.chat_id
        await update.message.reply_text(f"Your chat ID is: {chat_id}")

    #Read Tracked Shows
    async def initialize_tracked_shows(self):
        """ Initialize tracked shows list. """
        global tracked_shows
        tracked_shows = await read_tracked_shows() or []
        print("Tracked shows initialized:", tracked_shows)

    #Load Tracked Shows after update
    async def load_tracked_shows_if_updated(self):
        """ Load tracked shows if they have been updated. """
        global last_modified_time
        current_modified_time = os.path.getmtime(tracked_shows_path)

        if last_modified_time is None or current_modified_time > last_modified_time:
            print("Checking for updated shows...")
            last_modified_time = current_modified_time
            async with aiofiles.open(tracked_shows_path, "r") as file:
                content = await file.read()
                tracked_shows = json.loads(content)
                print("Updated tracked shows list:", tracked_shows)
                return tracked_shows
        return None
    #Periodic Check for new episodes
    async def periodic_check(self):
        print("Checking for new episodes.")
        notified_episodes = await load_notified_episodes()
        if not hasattr(self, 'last_reset_time'):
            await self.initialize_reset_time()

        print(self.last_reset_time)
        # Check if 24 hours have passed and reset the notified_episodes
        current_time = time.time()
        print(current_time)
        if current_time - self.last_reset_time >= 86400:  # 86400 seconds = 24 hours
            print("Resetting notified episodes for a new day.")
            notified_episodes = {show: None for show in tracked_shows}
            await save_notified_episodes(notified_episodes)
            self.last_reset_time = current_time  # Update the reset time
            await self.save_last_reset_time()  # Persist the updated reset time

        # Loop through tracked shows and check for new episodes
        for show_name in tracked_shows:
            new_episode_url = check_for_new_episode(show_name)
            if new_episode_url and new_episode_url != notified_episodes.get(show_name):
                message = f"New episode of '{show_name}' is out! Watch here: {new_episode_url}"
                await self.send_notification(self.application, CHAT_ID, message)
                notified_episodes[show_name] = new_episode_url
                await save_notified_episodes(notified_episodes)

        print("Period check completed.")

    async def run(self):
        """ Start the bot and run the polling loop. """
        print("Start Bot")
        global tracked_shows
        tracked_shows = await read_tracked_shows()

        print(tracked_shows)
        asyncio.create_task(self.periodic_check())
        await self.initialize_reset_time()
        await self.application.run_polling()
