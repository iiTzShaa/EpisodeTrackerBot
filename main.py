# main.py
from TelgramBot import TelegramBot
import asyncio
import nest_asyncio

if __name__ == "__main__":
    nest_asyncio.apply()  # Patch the current event loop to allow nested loops

    bot = TelegramBot()

    # Check if the event loop is already running
    try:
        # Run the bot using the existing event loop
        asyncio.get_event_loop().run_until_complete(bot.run())
    except RuntimeError:  # Event loop is already running
        # Use create_task if the event loop is already running
        asyncio.create_task(bot.run())