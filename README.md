# EpisodeTrackerBot

EpisodeTrackerBot is a Telegram bot that keeps you updated on new episodes of your favorite anime series. The bot checks daily for new episodes and sends a notification when a new episode is released. You can also manage your anime watchlist by adding or listing tracked anime shows through simple commands.

Features
Track multiple anime series and get notified when new episodes are released.
Receive daily notifications at 20:00 if there’s a new episode for any anime on your watchlist.
Use easy-to-remember commands to add anime series to your tracked list, view tracked anime, and retrieve your chat ID.
Getting Started
Prerequisites
Python 3.8+
Telegram Bot API Token from BotFather
Optional: PythonAnywhere account (Hacker Plan or above) for 24/7 hosting
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/iiTzShaa/AnimeTrackerBot.git
cd AnimeTrackerBot
Create a virtual environment (recommended):

bash
Copy code
python3 -m venv myenv
source myenv/bin/activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Set up environment variables:

Create a .env file in the project root directory:
makefile
Copy code
BOT_TOKEN=your_bot_token
CHAT_ID=your_chat_id
Replace your_bot_token with the token you received from BotFather and your_chat_id with the chat ID where notifications should be sent.
Usage
Run the bot:

bash
Copy code
python main.py
Commands:

/start: Start the bot and see a welcome message.
/track <anime_name>: Start tracking a specific anime series (replace <anime_name> with the title of the anime).
/get_tracked_shows: View the list of anime series you are currently tracking.
/help: Display a list of available commands and their descriptions.
/getid: Get your Telegram chat ID for setup purposes.
Daily Notifications:

The bot checks for new episodes daily at 20:00 and will notify you if a new episode is available for any anime on your tracked list.
Deployment
PythonAnywhere
Upgrade to the Hacker Plan to enable always-on tasks for 24/7 availability.
Upload the code or clone the repository to PythonAnywhere.
Set up environment variables in the Account > Environment Variables section.
Add an Always-On Task in the Tasks section:
bash
Copy code
/home/Arui43/myenv/bin/python3 /home/Arui43/AnimeTrackerBot/main.py
Contributing
If you’d like to add new features or improve the bot, feel free to fork the repository, make changes, and submit a pull request. Contributions are welcome!

License
This project is open-source and available under the MIT License.
