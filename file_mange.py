import aiofiles
import json
from telegram.ext import Application

async def load_notified_episodes():
    global tracked_shows
    try:
        async with aiofiles.open("notified_episodes.json", "r") as file:
            content = await file.read()
            return json.loads(content)
    except FileNotFoundError:
        return {show: None for show in tracked_shows}

async def save_notified_episodes(notified_episodes):
    async with aiofiles.open("notified_episodes.json", "w") as file:
        await file.write(json.dumps(notified_episodes, indent=4))

async def read_tracked_shows():
    try:
        async with aiofiles.open("tracked_shows.json", "r") as file:
            content = await file.read()
            return json.loads(content)
    except FileNotFoundError:
        return []

async def save_tracked_shows(application: Application, chat_id: int, new_show: str):
    try:
        # Open the tracked shows file and load the content
        async with aiofiles.open("tracked_shows.json", "r") as file:
            content = await file.read()
            tracked_shows = json.loads(content)
    except FileNotFoundError:
        # If file doesn't exist, start with an empty list
        tracked_shows = []

    if new_show not in tracked_shows:
        # Add the new show to the tracked list
        tracked_shows.append(new_show)

        # Save the updated list back to the file
        async with aiofiles.open("tracked_shows.json", "w") as file:
            await file.write(json.dumps(tracked_shows, indent=4))

        # Send a confirmation message to the user
        message = f"'{new_show}' has been added to the tracked shows."
        await application.bot.send_message(chat_id=chat_id, text=message)
    else:
        # If show is already tracked, notify the user
        await application.bot.send_message(chat_id=chat_id, text=f"'{new_show}' is already being tracked.")
