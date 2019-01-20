# LinkBot
LinkBot is a general-purpose [Discord](http://discordapp.com) bot. He is written in Python, using
[discord.py-rewrite](https://github.com/Rapptz/discord.py) API wrapper
([documentation](https://discordpy.readthedocs.io/en/rewrite/api.html)).

## Some Main Features
- Per-server :crown: Admins to restrict sensitive commands.
- Per-server :birthday: Birthday tracking. LinkBot will remind a channel of your birthday when it comes around.
- Per-server :speech_balloon: Quote tracking to store all of your friends' embarassing, disappointing, out-of-context quotes.
- Per-server :eye_speech_bubble: Topic system that enables users to subscribe to topics they like.
You can ping topics with a command when you want to post relevant information.
- A :calendar: reminder system that will DM you when the time comes.
- Youtube :movie_camera: video and Google :framed_picture: image first-result search embedding.
- Automatic :family: role-setting for new users in your server.
- And more!

## Getting Started
1. pip requirements  
Download the dependencies using pip: `pip install -r requirements.txt`  
As an exception: If you do not have Visual C++ and don't want to get it, you can `pip install fuzzywuzzy` without the `[speedup]`.
2. Discord API Application and Bot Account  
You can get both of these at the Discord Developer portal [here](https://discordapp.com/developers/applications/).
3. Neo4j Database  
You will need the community server version of Neo4j for the database. You can find it [here](https://neo4j.com/download-center/#panel2-2)
4. Configuration file  
If you run the program once, a config file will automatically be generated for you. From here, you can read through
the file and fill in the required information. It has lots of comments :smile:

Optionally, you will also need:
- a Google API key (for image and YouTube searches)
- a Google Custom Search (also required for image search)
- a Riot Games API key (for League of Legends game lookup)

If these are not included, the functionality will be automatically disabled.

## Commands
LinkBot works like most other discord bots: by reacting to user commands. The prefix for commands is stored in the
config file, and when LinkBot receives a command in a server that has the prefix attached, or through a direct message 
with/without the prefix, the associated command function for that command will be run.

### Adding Commands
- Create a script for your command at `./linkbot/commands/<yourcommand>.py`.
- Import the helper file: `from linkbot.utils.cmd_utils import *`.
- Create a function for your command: `async def <yourcommand>():`.
- Decorate your function with `@command()` and fill out the required parameters.
- Write your script, using any of the helper functions and decorators that are included from the helper file.
- Possibly add functionality to the main bot files `./linkbot/*` that is required for your command.
- That's it!
  - From here, your command should be callable by addressing the bot using the prefix specified in your config.
  - Your command should also be available via the `help` command.
