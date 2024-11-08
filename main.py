import asyncio
import json
import os
import time
from dotenv import load_dotenv
import aiofiles
import nest_asyncio
from telegram.ext import Application , CommandHandler
from file_mange import save_notified_episodes , read_tracked_shows , save_tracked_shows , load_notified_episodes
from TelgramBot import start , track , help , getid , send_notification , get_tracked_shows , tracked_shows ,save_tracked_shows
from Scapper import check_for_new_episode

nest_asyncio.apply()
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

tracked_shows_path = "tracked_shows.json"
last_reset_time = time.time()
last_modified_time = None
tracked_shows = []


async def load_tracked_shows_if_updated() :
    global last_modified_time
    current_modified_time = os.path.getmtime(tracked_shows_path)

    if last_modified_time is None or current_modified_time > last_modified_time :
        print("Cheking ...")
        last_modified_time = current_modified_time
        async with aiofiles.open(tracked_shows_path , "r") as file :
            content = await file.read()
            tracked_shows = json.loads(content)
            print("Updated tracked shows list:" , tracked_shows)
            return tracked_shows
    return None


async def periodic_check(application) :
    notified_episodes = await load_notified_episodes()
    last_reset_time = time.time()

    while True :
        updated_shows = await load_tracked_shows_if_updated()
        if updated_shows is not None :
            tracked_shows = updated_shows
        if time.time() - last_reset_time >= 86400 :
            notified_episodes = {show : None for show in tracked_shows}
            await save_notified_episodes(notified_episodes)
            last_reset_time = time.time()
            print("Resetting notified episodes for a new day.")

        for show_name in tracked_shows :
            new_episode_url = check_for_new_episode(show_name)
            if new_episode_url and new_episode_url != notified_episodes.get(show_name) :
                message = f"New episode of '{show_name}' is out! Watch here: {new_episode_url}"
                await send_notification(application , CHAT_ID , message)
                notified_episodes[show_name] = new_episode_url
                await save_notified_episodes(notified_episodes)
        await asyncio.sleep(10)


async def run_bot() :
    print("Start Bot")
    global tracked_shows
    tracked_shows = await read_tracked_shows()

    print(tracked_shows)
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start" , start))
    application.add_handler(CommandHandler("track" , track))
    application.add_handler(CommandHandler("getid" , getid))
    application.add_handler(CommandHandler("help" , help))
    application.add_handler(CommandHandler("get_tracked_shows" , get_tracked_shows))

    asyncio.create_task(periodic_check(application))

    print("POLLING")
    await application.run_polling()


if __name__ == "__main__" :
    asyncio.run(run_bot())
